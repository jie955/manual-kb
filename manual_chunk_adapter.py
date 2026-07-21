#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
manual_chunk_adapter.py

将 VLM 产出的 manual chunk JSON 转为 embed_ingest_local.py 可用的 chunks.json。

映射规则:
  - group_id = parent_id
  - question = step_title 或 chapter_title 合成
  - section = section 对象扁平化字符串
  - images = {file, caption} 列表（兼容 image_utils）
  - 保留 doc_type / structured / role 等 manual 元数据供 manifest 回表

用法:
  python manual_chunk_adapter.py pilot_chunks.json output/chunks.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from page_identity import canonical_parent_id, page_key


def _str_field(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def flatten_section(section: dict | None) -> str:
    if not section:
        return ""
    parts: list[str] = []
    chapter = _str_field(section.get("chapter_title"))
    step_num = _str_field(section.get("step_number"))
    step_title = _str_field(section.get("step_title"))
    if chapter:
        parts.append(chapter)
    if step_num and step_title:
        parts.append(f"{step_num} {step_title}")
    elif step_title:
        parts.append(step_title)
    elif step_num:
        parts.append(step_num)
    return " · ".join(parts)


def synthesize_question(section: dict | None) -> str:
    if not section:
        return ""
    step_title = _str_field(section.get("step_title"))
    if step_title:
        return step_title
    return _str_field(section.get("chapter_title"))


def normalize_manual_images(
    images: list | None,
    images_base: Path | None,
) -> list[dict]:
    out: list[dict] = []
    for img in images or []:
        if isinstance(img, str):
            out.append({"file": img, "caption": None, "caption_status": "not_captioned"})
            continue
        if not isinstance(img, dict):
            continue
        file_path = str(img.get("file") or img.get("image_id") or "")
        if images_base and file_path and not Path(file_path).is_absolute():
            file_path = str((images_base / file_path).as_posix())
        entry: dict = {
            "file": file_path,
            "caption": img.get("caption"),
            "caption_status": "captioned" if img.get("caption") else "not_captioned",
        }
        if img.get("role"):
            entry["role"] = img["role"]
        if img.get("image_id"):
            entry["image_id"] = img["image_id"]
        out.append(entry)
    return out


def is_parent_chunk(chunk: dict) -> bool:
    return chunk.get("is_retrievable") is False and not chunk.get("parent_id")


def _parent_score(chunk: dict, child_count: int = 0) -> tuple:
    zh = (chunk.get("content_zh") or "").strip()
    en = (chunk.get("content_en") or "").strip()
    has_key = 1 if chunk.get("page_key") else 0
    return (child_count, len(zh) + len(en), has_key)


def _resolve_duplicate_parents(
    parents_in: dict[str, dict],
    children_by_parent: dict[str, list[dict]],
) -> dict[str, dict]:
    by_id: dict[str, list[dict]] = defaultdict(list)
    for pid, chunk in parents_in.items():
        by_id[pid].append(chunk)

    resolved: dict[str, dict] = {}
    for pid, candidates in by_id.items():
        if len(candidates) == 1:
            resolved[pid] = candidates[0]
            continue
        kids = len(children_by_parent.get(pid, []))
        best = max(candidates, key=lambda c: _parent_score(c, kids))
        print(
            f"[adapter] WARN duplicate parent chunk_id={pid!r} "
            f"({len(candidates)} rows) -> keep richest",
            file=sys.stderr,
        )
        resolved[pid] = best
    return resolved


def _validate_page_keys(manual_chunks: list[dict], manifest: dict | None) -> None:
    if not manifest:
        return
    doc_prefix = str(manifest.get("doc_prefix") or "a3s-manual")
    allowed = {
        page_key(e): canonical_parent_id(e, doc_prefix=doc_prefix)
        for e in manifest.get("pages") or []
    }
    for c in manual_chunks:
        pk = c.get("page_key")
        if not pk or pk not in allowed:
            continue
        expected = allowed[pk]
        cid = c.get("chunk_id", "")
        if is_parent_chunk(c) and cid != expected:
            print(
                f"[adapter] WARN page_key={pk!r} parent {cid!r} != {expected!r}",
                file=sys.stderr,
            )
        pid = c.get("parent_id")
        if pid and pid != expected and not str(cid).startswith(expected):
            print(
                f"[adapter] WARN page_key={pk!r} child parent_id={pid!r} != {expected!r}",
                file=sys.stderr,
            )


def adapt_manual_chunk(
    chunk: dict,
    images_base: Path | None,
) -> dict:
    section_obj = chunk.get("section") or {}
    parent_id = chunk.get("parent_id")
    chunk_id = chunk["chunk_id"]
    is_retrievable = chunk.get("is_retrievable", True)
    is_child = bool(parent_id) and is_retrievable

    images = normalize_manual_images(chunk.get("images"), images_base)
    adapted: dict = {
        "chunk_id": chunk_id,
        "group_id": parent_id or chunk_id,
        "parent_id": parent_id if is_child else None,
        "is_child": is_child,
        "is_retrievable": is_retrievable,
        "section": flatten_section(section_obj),
        "question": synthesize_question(section_obj),
        "embedding_text": chunk.get("embedding_text") if is_retrievable else None,
        "content_zh": chunk.get("content_zh", ""),
        "content_en": chunk.get("content_en", ""),
        "images": images,
        "has_image": bool(images),
        "lang": chunk.get("lang", "zh"),
    }

    for key in (
        "doc_type",
        "source_pdf",
        "page_range",
        "section_obj",
        "structured",
        "table_data",
        "models",
        "vlm_notes",
        "page_key",
    ):
        if key in chunk:
            adapted[key] = chunk[key]

    if section_obj and "section_obj" not in adapted:
        adapted["section_obj"] = section_obj

    if chunk.get("table_data") and "table_data" not in adapted:
        adapted["table_data"] = chunk["table_data"]

    return adapted


def build_parent_from_children(
    parent_id: str,
    children: list[dict],
    images_base: Path | None,
) -> dict:
    first = children[0]
    section_obj = first.get("section_obj") or first.get("section") or {}
    if isinstance(section_obj, str):
        section_obj = {"chapter_title": section_obj}

    content_zh = "\n\n".join(
        c.get("content_zh", "").strip()
        for c in children
        if c.get("content_zh", "").strip()
    )
    content_en = "\n\n".join(
        c.get("content_en", "").strip()
        for c in children
        if c.get("content_en", "").strip()
    )

    seen_files: set[str] = set()
    images: list[dict] = []
    for child in children:
        for img in normalize_manual_images(child.get("images"), images_base):
            if img["file"] and img["file"] not in seen_files:
                seen_files.add(img["file"])
                images.append(img)

    page_range = first.get("page_range")
    return {
        "chunk_id": parent_id,
        "group_id": parent_id,
        "parent_id": None,
        "is_child": False,
        "is_retrievable": False,
        "section": flatten_section(section_obj if isinstance(section_obj, dict) else None),
        "question": synthesize_question(section_obj if isinstance(section_obj, dict) else None),
        "embedding_text": None,
        "content_zh": content_zh,
        "content_en": content_en,
        "images": images,
        "has_image": bool(images),
        "lang": first.get("lang", "zh"),
        "doc_type": first.get("doc_type", "installation_manual"),
        "source_pdf": first.get("source_pdf"),
        "page_range": page_range,
        "section_obj": section_obj if isinstance(section_obj, dict) else {},
        "models": first.get("models", []),
    }


def adapt_manual_chunks(
    manual_chunks: list[dict],
    images_base: Path | None = None,
    manifest: dict | None = None,
) -> list[dict]:
    _validate_page_keys(manual_chunks, manifest)

    parents_raw = {c["chunk_id"]: c for c in manual_chunks if is_parent_chunk(c)}
    children_by_parent: dict[str, list[dict]] = {}
    standalone: list[dict] = []
    adapted_parents: list[dict] = []

    for chunk in manual_chunks:
        if is_parent_chunk(chunk):
            continue
        adapted = adapt_manual_chunk(chunk, images_base)
        if adapted["parent_id"]:
            children_by_parent.setdefault(adapted["parent_id"], []).append(adapted)
        else:
            standalone.append(adapted)

    parents_in = _resolve_duplicate_parents(parents_raw, children_by_parent)

    all_parent_ids = set(parents_in) | set(children_by_parent)
    for parent_id in sorted(all_parent_ids):
        if parent_id in parents_in:
            adapted_parents.append(
                adapt_manual_chunk(parents_in[parent_id], images_base)
            )
        elif parent_id in children_by_parent:
            adapted_parents.append(
                build_parent_from_children(
                    parent_id,
                    children_by_parent[parent_id],
                    images_base,
                )
            )

    parent_order = {p["chunk_id"]: i for i, p in enumerate(adapted_parents)}
    result: list[dict] = []
    for parent in adapted_parents:
        result.append(parent)
        kids = sorted(
            children_by_parent.get(parent["chunk_id"], []),
            key=lambda c: c["chunk_id"],
        )
        result.extend(kids)
    result.extend(standalone)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="manual chunk JSON -> embed_ingest_local chunks.json"
    )
    parser.add_argument("input_json", help="manual chunks JSON（list 或 {chunks:[]}）")
    parser.add_argument("output_json", help="输出 chunks.json 路径")
    parser.add_argument(
        "--images-base",
        type=Path,
        default=None,
        help="相对图片路径的基准目录（默认输入文件所在目录）",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="page_manifest.json（可选，启用 page_key 一致性 warn）",
    )
    args = parser.parse_args()

    input_path = Path(args.input_json)
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "chunks" in data:
        manual_chunks = data["chunks"]
    elif isinstance(data, list):
        manual_chunks = data
    else:
        raise SystemExit("unsupported input format: expected list or {chunks:[]}")

    images_base = args.images_base or input_path.parent
    manifest = None
    if args.manifest and args.manifest.is_file():
        with open(args.manifest, "r", encoding="utf-8") as mf:
            manifest = json.load(mf)
    chunks = adapt_manual_chunks(manual_chunks, images_base, manifest=manifest)

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    retrievable = sum(1 for c in chunks if c.get("is_retrievable"))
    parents = sum(1 for c in chunks if not c.get("is_retrievable"))
    print(f"输入 manual 块: {len(manual_chunks)} 个", file=sys.stderr)
    print(f"输出 chunks: {len(chunks)} 个（可检索 {retrievable}，parent {parents}）", file=sys.stderr)
    print(f"已保存: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
