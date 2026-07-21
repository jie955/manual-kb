#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
caption_images.py

流水线第 2.5 步（在 chunk_builder 之后、embed 之前）：
为 chunks 关联图片生成有上下文的 VLM 说明，替代通用图像识别的无效描述。

思路来源：上下文 = 问题标题 + 中文步骤（与 translate.py 降级/缓存模式一致）。

环境变量（二选一后端）：
  OpenAI 兼容视觉（推荐，与 TRANSLATE 同网关）：
    CAPTION_API_KEY / OPENAI_API_KEY
    CAPTION_BASE_URL   默认 https://api.openai.com/v1
    CAPTION_MODEL      如 gpt-4o、gemini-2.5-flash（需网关支持 vision）
  Anthropic 原生：
    CAPTION_BACKEND=anthropic
    ANTHROPIC_API_KEY
    CAPTION_MODEL      如 claude-sonnet-4-20250514

用法:
  python caption_images.py chunks.json images/ output_dir/
  python caption_images.py chunks.json images/ output_dir/ --enrich-embedding
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from image_utils import caption_text_for_embedding, normalize_image_entry

DEFAULT_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".caption_cache.json"
)

CAPTION_SYSTEM_PROMPT = (
    "你是技术文档配图说明助手。用户会提供一段故障排查说明文字（该图片所在的上下文）"
    "和一张图片，图片就出现在这段说明文字描述的步骤附近。\n"
    "任务：结合上下文，用一句简体中文说明这张图片在该故障排查场景中展示的具体内容"
    "（例如：某个接线端口的位置、某个部件的外观、某个操作动作的示意）。\n"
    "要求：\n"
    "1. 必须结合上下文给出具体、有指向性的说明，不要只描述图片的颜色、形状、构图这类"
    "与故障排查任务无关的通用视觉信息；\n"
    "2. 如果图片内容确实与上下文无法建立明确关联，如实说明「图片与上下文关联不明确」，"
    "不要编造；\n"
    "3. 一到两句话，不要markdown标记，不要前缀。"
)

EXT_TO_MEDIA_TYPE = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MAX_TOKENS = 1024
RETRY_MAX_TOKENS = 2048
CAPTION_CACHE_VERSION = "cap2"


def load_chunks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    if isinstance(data, list):
        return data
    raise SystemExit("unsupported chunks.json format")


def _load_cache(cache_path: str) -> dict:
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_path: str, cache: dict) -> None:
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _file_hash(filepath: str) -> str:
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _guess_media_type(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    return EXT_TO_MEDIA_TYPE.get(ext, "image/png")


def _get_config() -> tuple[str | None, str, str, str]:
    backend = os.environ.get("CAPTION_BACKEND", "openai").lower()
    api_key = (
        os.environ.get("CAPTION_API_KEY")
        or os.environ.get("TRANSLATE_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    base_url = (
        os.environ.get("CAPTION_BASE_URL")
        or os.environ.get("TRANSLATE_BASE_URL")
        or "https://api.openai.com/v1"
    ).rstrip("/")
    if backend == "anthropic":
        model = os.environ.get("CAPTION_MODEL", "claude-sonnet-4-20250514")
    else:
        model = os.environ.get("CAPTION_MODEL") or os.environ.get(
            "TRANSLATE_MODEL", "gpt-4o-mini"
        )
    return api_key, base_url, model, backend


def _image_b64_data_uri(image_path: str) -> str:
    media = _guess_media_type(image_path)
    with open(image_path, "rb") as f:
        b64 = base64.standard_b64encode(f.read()).decode("utf-8")
    return f"data:{media};base64,{b64}"


def _extract_message_content(message: dict) -> str:
    """兼容 OpenAI 字符串 content 与多 part 数组。"""
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(str(block.get("text") or ""))
            elif "text" in block:
                parts.append(str(block["text"]))
        return "".join(parts).strip()
    return ""


def _looks_truncated(text: str) -> bool:
    """启发式：句中截断（无句末标点且偏短）。"""
    t = text.strip()
    if not t:
        return True
    if t[-1] in "。！？":
        return False
    # 完整长句偶尔省略句号；极短且无标点则视为截断
    return len(t) < 35


def _call_openai_vision(
    image_path: str,
    context_text: str,
    api_key: str,
    base_url: str,
    model: str,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    url = base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": CAPTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"上下文：\n{context_text}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": _image_b64_data_uri(image_path)},
                    },
                ],
            },
        ],
    }
    # 新 OpenAI / 部分网关用 max_completion_tokens
    payload["max_completion_tokens"] = max_tokens

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"no choices in response: {data}")

    choice = choices[0]
    content = _extract_message_content(choice.get("message") or {})
    if not content:
        raise ValueError(f"empty caption content: {data}")

    finish = choice.get("finish_reason") or ""
    usage = data.get("usage") or {}
    completion_tokens = usage.get("completion_tokens")
    reasoning_tokens = (
        usage.get("completion_tokens_details") or {}
    ).get("reasoning_tokens")

    truncated = finish == "length" or _looks_truncated(content)
    if truncated and max_tokens < RETRY_MAX_TOKENS:
        print(
            f"[caption] 输出疑似截断 finish={finish!r} "
            f"completion_tokens={completion_tokens} reasoning_tokens={reasoning_tokens} "
            f"len={len(content)} → 以 max_tokens={RETRY_MAX_TOKENS} 重试",
            file=sys.stderr,
        )
        return _call_openai_vision(
            image_path,
            context_text,
            api_key,
            base_url,
            model,
            max_tokens=RETRY_MAX_TOKENS,
        )

    if truncated:
        print(
            f"[caption] 警告：重试后仍疑似截断 finish={finish!r} text={content[:60]!r}",
            file=sys.stderr,
        )

    return content


def _call_anthropic_vision(
    image_path: str, context_text: str, api_key: str, model: str
) -> str:
    with open(image_path, "rb") as f:
        image_b64 = base64.standard_b64encode(f.read()).decode("utf-8")
    media_type = _guess_media_type(image_path)
    payload = {
        "model": model,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "system": CAPTION_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"上下文：\n{context_text}"},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_b64,
                        },
                    },
                ],
            }
        ],
    }
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    text_blocks = [
        b["text"] for b in data.get("content", []) if b.get("type") == "text"
    ]
    if not text_blocks:
        raise ValueError(f"no text in anthropic response: {data}")
    return "".join(text_blocks).strip()


def _call_vision_api(
    image_path: str,
    context_text: str,
    api_key: str,
    base_url: str,
    model: str,
    backend: str,
) -> str:
    if backend == "anthropic":
        return _call_anthropic_vision(image_path, context_text, api_key, model)
    return _call_openai_vision(image_path, context_text, api_key, base_url, model)


def build_context_text(chunk: dict) -> str:
    question = chunk.get("question", "")
    body = (
        chunk.get("content_zh")
        or chunk.get("answer_zh_translated")
        or chunk.get("content_en")
        or ""
    )
    body = str(body)[:800]
    return f"故障场景：{question}\n说明：{body}".strip()


def _image_file_from_entry(entry) -> str:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return str(entry.get("file") or "")
    return str(entry)


def caption_chunks(
    chunks: list[dict],
    images_dir: str,
    cache_path: str,
    *,
    enrich_embedding: bool = False,
) -> list[dict]:
    api_key, base_url, model, backend = _get_config()
    cache = _load_cache(cache_path)
    cache_dirty = False

    if not api_key:
        print(
            "[caption] 警告：未配置 CAPTION_API_KEY / ANTHROPIC_API_KEY / OPENAI_API_KEY，"
            "跳过说明生成（images 保持原样）。",
            file=sys.stderr,
        )

    for chunk in chunks:
        raw_images = chunk.get("images") or []
        if not raw_images:
            continue

        context_text = build_context_text(chunk)
        captioned_images = []

        for entry in raw_images:
            image_filename = _image_file_from_entry(entry)
            if not image_filename:
                continue

            image_path = os.path.join(images_dir, image_filename)
            if not os.path.exists(image_path):
                print(f"[caption] 图片不存在，跳过: {image_path}", file=sys.stderr)
                captioned_images.append(
                    normalize_image_entry(
                        {
                            "file": image_filename,
                            "caption": None,
                            "caption_status": "file_missing",
                        }
                    )
                )
                continue

            if not api_key:
                captioned_images.append(
                    normalize_image_entry(
                        {
                            "file": image_filename,
                            "caption": None,
                            "caption_status": "no_api_key",
                        }
                    )
                )
                continue

            cache_key = (
                _file_hash(image_path)
                + "|"
                + hashlib.sha256(context_text.encode("utf-8")).hexdigest()[:16]
                + "|"
                + model
                + "|"
                + CAPTION_CACHE_VERSION
            )

            if cache_key in cache:
                caption = cache[cache_key]
                status = "cached"
            else:
                try:
                    caption = _call_vision_api(
                        image_path, context_text, api_key, base_url, model, backend
                    )
                    cache[cache_key] = caption
                    cache_dirty = True
                    status = "generated"
                except (
                    urllib.error.URLError,
                    urllib.error.HTTPError,
                    ValueError,
                    TimeoutError,
                    json.JSONDecodeError,
                ) as e:
                    print(
                        f"[caption] 生成失败: {image_filename} — {e}",
                        file=sys.stderr,
                    )
                    caption = None
                    status = "failed"

            captioned_images.append(
                normalize_image_entry(
                    {
                        "file": image_filename,
                        "caption": caption,
                        "caption_zh": caption,
                        "caption_status": status,
                    }
                )
            )

        chunk["images"] = captioned_images

        if enrich_embedding and chunk.get("is_retrievable", True):
            extra = caption_text_for_embedding(captioned_images)
            base = chunk.get("embedding_text") or ""
            if extra and extra not in base:
                chunk["embedding_text"] = f"{base}\n{extra}".strip()

    if cache_dirty:
        _save_cache(cache_path, cache)

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="VLM 上下文 caption（可选增强 embedding）")
    parser.add_argument("chunks_json", type=Path)
    parser.add_argument("images_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--cache-path", default=DEFAULT_CACHE_PATH)
    parser.add_argument(
        "--enrich-embedding",
        action="store_true",
        help="将 caption 追加到可检索块的 embedding_text（默认仅写 images）",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="覆盖原 chunks.json（输出目录即 chunks 所在目录时使用）",
    )
    args = parser.parse_args()

    chunks = load_chunks(args.chunks_json)
    chunks = caption_chunks(
        chunks,
        str(args.images_dir),
        args.cache_path,
        enrich_embedding=args.enrich_embedding,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_name = "chunks.json" if args.in_place else "chunks_captioned.json"
    output_path = args.output_dir / out_name
    output_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total = sum(len(c.get("images") or []) for c in chunks)
    generated = sum(
        1
        for c in chunks
        for img in (c.get("images") or [])
        if isinstance(img, dict) and img.get("caption_status") == "generated"
    )
    cached = sum(
        1
        for c in chunks
        for img in (c.get("images") or [])
        if isinstance(img, dict) and img.get("caption_status") == "cached"
    )
    print(f"图片总数: {total}", file=sys.stderr)
    print(f"  新生成: {generated}  缓存: {cached}  其余: {total - generated - cached}", file=sys.stderr)
    print(f"输出: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
