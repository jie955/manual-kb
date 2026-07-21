#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_vlm_parser.py

整页 VLM 版面解析：渲页 PNG + page_manifest 元数据 → manual chunk JSON（parent + children）。

环境变量（与 caption_images.py 一致）：
  CAPTION_API_KEY / OPENAI_API_KEY
  CAPTION_BASE_URL   默认 https://api.openai.com/v1
  CAPTION_MODEL      如 gpt-4o、gemini-2.5-flash

硬规则（docs/排期.md）：
  - 示意图与内嵌表拆为两条 images、分别打 role
  - 端子/规格表按功能组聚合 structured.rows
  - spec_table 页必须有 table_data 或 structured.rows

无 API key 时：仅从 pilot_chunks.json 复用 manifest 中 pilot 页（默认 p9+p18），其余跳过。

用法:
  python pdf_vlm_parser.py --manifest _scratch/vlm_batch/page_manifest.json \\
      --pages-dir _scratch/vlm_batch/pages \\
      --out _scratch/vlm_batch/manual_chunks.json

  python pdf_vlm_parser.py ... --pilot-chunks _scratch/vlm_pilot/pilot_chunks.json
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from env_utils import load_dotenv
from page_identity import normalize_page_chunks

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CACHE_PATH = REPO_ROOT / ".vlm_cache.json"
DEFAULT_PILOT_CHUNKS = REPO_ROOT / "_scratch" / "vlm_pilot" / "pilot_chunks.json"

EXT_TO_MEDIA_TYPE = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

DEFAULT_MAX_TOKENS = 4096
RETRY_MAX_TOKENS = 8192
VLM_CACHE_VERSION = "vlm1"
API_MAX_ATTEMPTS = 3

BASE_SYSTEM = (
    "你是工业门机安装说明书版面解析助手。用户会提供一页说明书渲染图及页元数据。\n"
    "输出必须是**单个合法 JSON 数组**（不要 markdown 代码块），每个元素为 manual chunk 对象。\n"
    "通用字段：chunk_id, doc_type=installation_manual, source_pdf, page_range=[N,N], "
    "section{chapter_title,step_number,step_title}, content_zh, content_en, images[], "
    "models, parent_id, is_retrievable, embedding_text（仅可检索子块）。\n"
    "images[] 元素：image_id, file, caption, role（见下表）。\n"
    "role 取值：primary_step_illustration, spec_table, reference_diagram, packing_list, warning_icon。\n"
    "硬规则：\n"
    "1. 每页先产一个页级 parent（is_retrievable=false, parent_id=null）；chunk_id **必须**以用户消息中的「chunk_id 前缀建议」为准（前置页 a3s-manual-idxN，印刷页 a3s-manual-pN）。\n"
    "2. 每个 STEP 或独立表/警示块产一个可检索 child（is_retrievable=true, parent_id 指向页 parent）。\n"
    "3. 同一视觉区若含示意图+内嵌表，须拆为两条 images、分别打 role。\n"
    "4. 端子功能表等多编号同一功能行，按功能组聚合到 structured.rows，禁止按印刷行号机械拆句。\n"
    "5. role=spec_table 的块或 spec_table 页必须含 structured.rows 或 table_data。\n"
    "6. embedding_text 用章节+STEP+端子代号/关键词，不含 vlm_notes。\n"
    "7. models 固定 [\"A3S\",\"A5S\",\"A8S\"]。\n"
    "8. images[].file 使用占位路径 images/pNN-描述.png（后续可裁切替换）。\n"
)


def manifest_doc_prefix(manifest: dict) -> str:
    return str(manifest.get("doc_prefix") or "a3s-manual")


def manifest_models(manifest: dict) -> list[str]:
    raw = manifest.get("models")
    if isinstance(raw, list) and raw:
        return [str(m) for m in raw]
    return ["A3S", "A5S", "A8S"]


def build_system_prompt(page_type: str, manifest: dict) -> str:
    doc_prefix = manifest_doc_prefix(manifest)
    models = manifest_models(manifest)
    models_json = json.dumps(models, ensure_ascii=False)
    prefix_rule = (
        f"1. 每页先产一个页级 parent（is_retrievable=false, parent_id=null）；"
        f"chunk_id **必须**以用户消息中的「chunk_id 前缀（强制）」为准"
        f"（前置页 {doc_prefix}-idxN，印刷页 {doc_prefix}-pN）。\n"
    )
    models_rule = f"7. models 固定 {models_json}。\n"
    base = BASE_SYSTEM.replace(
        "1. 每页先产一个页级 parent（is_retrievable=false, parent_id=null）；chunk_id **必须**以用户消息中的「chunk_id 前缀建议」为准（前置页 a3s-manual-idxN，印刷页 a3s-manual-pN）。\n",
        prefix_rule,
    ).replace('7. models 固定 ["A3S","A5S","A8S"]。\n', models_rule)
    variant = PROMPT_VARIANTS.get(page_type, PROMPT_VARIANTS["other"])
    return base + "\n" + variant


PROMPT_VARIANTS: dict[str, str] = {
    "step_mixed": (
        "页类型 step_mixed：识别黑条章节名与各 STEP 边界。\n"
        "每个 STEP 产一 child；step_number/step_title 必填。\n"
        "示意图 role=primary_step_illustration；内嵌角度/规格表 role=spec_table 并附 table_data。\n"
        "页脚 NOTE/CAUTION 写入对应 STEP 的 content 或单独 child。"
    ),
    "spec_table": (
        "页类型 spec_table：整页以表格/对照数据为主。\n"
        "产一 child（chunk_id 含表意后缀如 -terminal-table 或 -specs）。\n"
        "必须 structured.rows 或 table_data；端子表按功能组聚合 terminals/labels。\n"
        "控制板示意图 role=reference_diagram 或 spec_table。"
    ),
    "warning": (
        "页类型 warning：提取安全警示原文（中英文）。\n"
        "可按主题拆多个 child，或单 child 汇总；警示图标 role=warning_icon。\n"
        "is_retrievable=true；embedding_text 含 WARNING/安全/安装 等关键词。"
    ),
    "packing": (
        "页类型 packing：提取装箱清单条目（组件名、数量、规格）。\n"
        "产 parent + 一 child；配图 role=packing_list。\n"
        "若有硬件数量表，用 structured.rows 或 table_data。"
    ),
    "other": (
        "页类型 other：按段落或主题拆 child；无 STEP 时 step_number/step_title 为 null。\n"
        "清单/工具列表可用 structured.rows。"
    ),
}


def _load_cache(cache_path: Path) -> dict:
    if cache_path.is_file():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _file_hash(filepath: Path) -> str:
    return hashlib.sha256(filepath.read_bytes()).hexdigest()


def _guess_media_type(filepath: Path) -> str:
    return EXT_TO_MEDIA_TYPE.get(filepath.suffix.lower(), "image/png")


def _get_config() -> tuple[str | None, str, str]:
    api_key = (
        os.environ.get("CAPTION_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    base_url = (
        os.environ.get("CAPTION_BASE_URL")
        or os.environ.get("TRANSLATE_BASE_URL")
        or "https://api.openai.com/v1"
    ).rstrip("/")
    model = os.environ.get("CAPTION_MODEL") or os.environ.get(
        "TRANSLATE_MODEL", "gpt-4o-mini"
    )
    return api_key, base_url, model


def _image_b64_data_uri(image_path: Path) -> str:
    media = _guess_media_type(image_path)
    b64 = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{media};base64,{b64}"


def _extract_message_content(message: dict) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text") or ""))
                elif "text" in block:
                    parts.append(str(block["text"]))
        return "".join(parts).strip()
    return ""


def _call_openai_vision(
    image_path: Path,
    user_text: str,
    system_text: str,
    api_key: str,
    base_url: str,
    model: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    url = (
        base_url
        if base_url.endswith("/chat/completions")
        else f"{base_url}/chat/completions"
    )
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_text},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_b64_data_uri(image_path)},
                    },
                ],
            },
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        body = resp.read().decode("utf-8")
    if not body.strip():
        raise ValueError("empty HTTP response body from vision API")
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError(f"vision API returned non-JSON body: {body[:200]!r}") from e
    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"no choices in response: {data}")
    content = _extract_message_content(choices[0].get("message") or {})
    if not content:
        raise ValueError(f"empty VLM content: {data}")
    if choices[0].get("finish_reason") == "length" and max_tokens < RETRY_MAX_TOKENS:
        return _call_openai_vision(
            image_path,
            user_text,
            system_text,
            api_key,
            base_url,
            model,
            max_tokens=RETRY_MAX_TOKENS,
        )
    return content


def _parse_json_array(text: str) -> list[dict]:
    text = (text or "").strip()
    if not text:
        raise ValueError("VLM returned empty text")

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("["), text.rfind("]")
        if start < 0 or end <= start:
            raise ValueError(f"VLM output is not valid JSON: {text[:200]!r}")
        data = json.loads(text[start : end + 1])

    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    if isinstance(data, list):
        return data
    raise ValueError("VLM output is not a JSON array")


def _parse_page_via_api(
    image_path: Path,
    user_text: str,
    system_text: str,
    api_key: str,
    base_url: str,
    model: str,
) -> str:
    """Call vision API with retries on empty/transient failures."""
    last_err: Exception | None = None
    for attempt in range(API_MAX_ATTEMPTS):
        try:
            return _call_openai_vision(
                image_path,
                user_text,
                system_text,
                api_key,
                base_url,
                model,
            )
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            ValueError,
            TimeoutError,
            json.JSONDecodeError,
        ) as e:
            last_err = e
            if attempt < API_MAX_ATTEMPTS - 1:
                wait = 2**attempt
                print(
                    f"[vlm] retry {attempt + 2}/{API_MAX_ATTEMPTS} after {e!s}",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            raise
    raise last_err or RuntimeError("vision API failed")


def page_image_path(entry: dict, pages_dir: Path) -> Path:
    if entry.get("image_name"):
        return pages_dir / str(entry["image_name"])
    printed = entry.get("printed_page")
    if printed is not None:
        return pages_dir / f"p{int(printed):02d}.png"
    pdf_index = entry.get("pdf_index")
    if pdf_index is not None:
        return pages_dir / f"idx{int(pdf_index):02d}.png"
    raise ValueError("manifest entry needs image_name, printed_page, or pdf_index")


def page_label(entry: dict) -> str:
    if entry.get("printed_page") is not None:
        return f"p{int(entry['printed_page']):02d}"
    if entry.get("pdf_index") is not None:
        return f"idx{int(entry['pdf_index']):02d}"
    return "page?"


def build_user_prompt(entry: dict, manifest: dict) -> str:
    printed = entry.get("printed_page")
    pdf_index = entry.get("pdf_index")
    page_type = entry.get("page_type", "other")
    chapter = entry.get("chapter_hint", "")
    source_pdf = manifest.get("source_pdf", "")
    doc_prefix = manifest_doc_prefix(manifest)
    if printed is not None:
        printed = int(printed)
        id_hint = f"{doc_prefix}-p{printed}"
        page_line = f"印刷页码：{printed}\npage_range：[{printed},{printed}]\n"
    else:
        id_hint = f"{doc_prefix}-idx{pdf_index}"
        page_line = f"PDF index (0-based)：{pdf_index}\n"
    return (
        f"源 PDF：{source_pdf}\n"
        f"{page_line}"
        f"page_type：{page_type}\n"
        f"chapter_hint：{chapter}\n"
        f"chunk_id 前缀（强制）：{id_hint}\n"
        "请解析本页并输出 JSON 数组。"
    )


def chunk_page_range(chunk: dict) -> int | None:
    pr = chunk.get("page_range")
    if isinstance(pr, list) and pr:
        return int(pr[0])
    return None


def load_pilot_chunks_for_pages(
    pilot_path: Path,
    printed_pages: set[int],
) -> list[dict]:
    data = json.loads(pilot_path.read_text(encoding="utf-8"))
    chunks = data if isinstance(data, list) else data.get("chunks", [])
    out: list[dict] = []
    for c in chunks:
        pg = chunk_page_range(c)
        if pg in printed_pages:
            out.append(c)
    return out


def needs_structured_review(chunk: dict) -> bool:
    """spec_table 无 structured/table_data 时 flag。"""
    images = chunk.get("images") or []
    has_spec_role = any(
        isinstance(img, dict) and img.get("role") == "spec_table" for img in images
    )
    if chunk.get("doc_type") == "installation_manual" and (
        chunk.get("structured") or chunk.get("table_data")
    ):
        return False
    if has_spec_role and not (chunk.get("structured") or chunk.get("table_data")):
        return True
    section = chunk.get("section") or {}
    if isinstance(section, dict):
        pass
    return False


def flag_chunks(chunks: list[dict]) -> list[dict]:
    flags: list[dict] = []
    for c in chunks:
        if not c.get("is_retrievable", True):
            continue
        pg = chunk_page_range(c)
        issues: list[str] = []
        if needs_structured_review(c):
            issues.append("missing_structured_rows")
        imgs = c.get("images") or []
        for img in imgs:
            if isinstance(img, dict) and img.get("role") == "spec_table":
                if not (c.get("structured") or c.get("table_data")):
                    issues.append("spec_table_without_data")
        if issues:
            flags.append(
                {
                    "printed_page": pg,
                    "chunk_id": c.get("chunk_id"),
                    "issues": sorted(set(issues)),
                }
            )
    return flags


def parse_pages(
    manifest_path: Path,
    pages_dir: Path,
    cache_path: Path,
    pilot_chunks_path: Path,
    *,
    force_api: bool = False,
    only_pages: set[int] | None = None,
) -> tuple[list[dict], dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    doc_prefix = manifest_doc_prefix(manifest)
    pages = manifest.get("pages") or []
    if only_pages is not None:
        pages = [
            p
            for p in pages
            if p.get("printed_page") is not None
            and int(p["printed_page"]) in only_pages
        ]
    api_key, base_url, model = _get_config()
    cache = _load_cache(cache_path)
    cache_dirty = False

    all_chunks: list[dict] = []
    stats = {
        "api_key_present": bool(api_key),
        "parsed_via_api": 0,
        "parsed_via_pilot": 0,
        "skipped_no_api": 0,
        "cached": 0,
        "failed": 0,
        "pages_total": len(pages),
    }

    pilot_pages = {
        int(p["printed_page"])
        for p in pages
        if p.get("printed_page") is not None
        and (p.get("pilot") or int(p["printed_page"]) in set(manifest.get("pilot_reuse") or []))
    }

    if not api_key and not force_api:
        pilot_chunks = load_pilot_chunks_for_pages(pilot_chunks_path, pilot_pages)
        all_chunks.extend(pilot_chunks)
        stats["parsed_via_pilot"] = len(pilot_pages)
        stats["skipped_no_api"] = len(pages) - len(pilot_pages)
        stats["correction_flags"] = flag_chunks(all_chunks)
        return all_chunks, stats

    for entry in pages:
        label = page_label(entry)
        printed = entry.get("printed_page")
        printed_int = int(printed) if printed is not None else None
        page_type = entry.get("page_type", "other")
        image_path = page_image_path(entry, pages_dir)

        if printed_int is not None and entry.get("pilot") and pilot_chunks_path.is_file():
            pilot_for_page = load_pilot_chunks_for_pages(
                pilot_chunks_path, {printed_int}
            )
            if pilot_for_page:
                pilot_for_page = normalize_page_chunks(
                    pilot_for_page, entry, doc_prefix=doc_prefix
                )
                all_chunks.extend(pilot_for_page)
                stats["parsed_via_pilot"] += 1
                print(f"[vlm] {label}: reuse pilot ({len(pilot_for_page)} chunks)", file=sys.stderr)
                continue

        if not image_path.is_file():
            print(f"[vlm] {label}: image missing {image_path}", file=sys.stderr)
            stats["failed"] += 1
            continue

        system_text = build_system_prompt(page_type, manifest)
        user_text = build_user_prompt(entry, manifest)
        cache_key = (
            _file_hash(image_path)
            + "|"
            + page_type
            + "|"
            + hashlib.sha256(user_text.encode()).hexdigest()[:16]
            + "|"
            + model
            + "|"
            + VLM_CACHE_VERSION
        )

        if cache_key in cache:
            page_chunks = _parse_json_array(cache[cache_key])
            stats["cached"] += 1
            status = "cached"
        else:
            try:
                raw = _parse_page_via_api(
                    image_path,
                    user_text,
                    system_text,
                    api_key,
                    base_url,
                    model,
                )
                page_chunks = _parse_json_array(raw)
                cache[cache_key] = raw
                cache_dirty = True
                stats["parsed_via_api"] += 1
                status = "api"
            except (
                urllib.error.URLError,
                urllib.error.HTTPError,
                ValueError,
                TimeoutError,
                json.JSONDecodeError,
            ) as e:
                print(f"[vlm] {label}: failed — {e}", file=sys.stderr)
                stats["failed"] += 1
                continue

        page_chunks = normalize_page_chunks(page_chunks, entry, doc_prefix=doc_prefix)
        all_chunks.extend(page_chunks)
        print(
            f"[vlm] {label} ({page_type}): {len(page_chunks)} chunks [{status}]",
            file=sys.stderr,
        )

    if cache_dirty:
        _save_cache(cache_path, cache)

    stats["correction_flags"] = flag_chunks(all_chunks)
    return all_chunks, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="VLM 整页解析 → manual chunk JSON")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pages-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--pilot-chunks", type=Path, default=DEFAULT_PILOT_CHUNKS)
    parser.add_argument(
        "--force-api",
        action="store_true",
        help="即使无 key 也尝试调用（调试用）",
    )
    parser.add_argument(
        "--stats-out",
        type=Path,
        default=None,
        help="写入解析统计 JSON",
    )
    parser.add_argument(
        "--only-pages",
        type=str,
        default="",
        help="仅解析指定印刷页，逗号分隔，如 2,4",
    )
    args = parser.parse_args()

    load_dotenv()

    only_pages: set[int] | None = None
    if args.only_pages.strip():
        only_pages = {int(x.strip()) for x in args.only_pages.split(",") if x.strip()}

    chunks, stats = parse_pages(
        args.manifest,
        args.pages_dir,
        args.cache_path,
        args.pilot_chunks,
        force_api=args.force_api,
        only_pages=only_pages,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    stats_path = args.stats_out or (args.out.parent / "parse_stats.json")
    stats_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    retrievable = sum(1 for c in chunks if c.get("is_retrievable", True))
    print(
        f"输出 {len(chunks)} chunks（可检索 {retrievable}）-> {args.out}",
        file=sys.stderr,
    )
    print(f"统计: {json.dumps(stats, ensure_ascii=False)}", file=sys.stderr)


if __name__ == "__main__":
    main()
