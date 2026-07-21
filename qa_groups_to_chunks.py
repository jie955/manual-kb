#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_groups_to_chunks.py

将 qa_doc_extractor 产出的 qa_groups.json 转为向量库可 ingest 的 chunks 列表。

策略（五步）：
  1. 短组整组成片；长组按 answer_zh 语义子结构二次切分，子块继承 section/question
  2. embedding_text 只用中文（无中文时 section+question+content_en，lang=en_only）
  3. 图片只挂在父块，不单独成片
  4. 每片带齐元数据：chunk_id / group_id / section / question / has_image / lang 等
  5. 长组父子块：子块检索，父块返回完整上下文

用法:
  python qa_groups_to_chunks.py qa_groups.json -o chunks.json
  python qa_groups_to_chunks.py qa_groups.json -o chunks.json --max-chunk-chars 400
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 步骤/子结构边界：手打数字、字母分项、表格行
STEP_START = re.compile(
    r"^("
    r"\d+\s"  # 1 检查...
    r"|[a-zA-Z][.)]\s"  # a. b)
    r"|\|"  # 表格行
    r")",
    re.MULTILINE,
)
LETTER_STEP = re.compile(r"^[a-zA-Z]\s+\S")


def detect_lang(answer_zh: str, answer_en: str) -> str:
    has_zh = bool(answer_zh.strip())
    has_en = bool(answer_en.strip())
    if has_zh and has_en:
        return "zh_en"
    if has_zh:
        return "zh"
    if has_en:
        return "en_only"
    return "empty"


def build_embedding_text(
    section: str | None,
    question: str,
    content_zh: str,
    content_en: str,
    lang: str,
) -> str:
    header_parts = [p for p in (section, question) if p and p.strip()]
    header = "\n".join(header_parts)
    body = content_zh.strip() if content_zh.strip() else ""
    if not body and lang == "en_only":
        body = content_en.strip()
    if header and body:
        return f"{header}\n{body}"
    return header or body


def is_step_boundary(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
    if line.startswith("|"):
        return True
    if STEP_START.match(line):
        return True
    if LETTER_STEP.match(line):
        return True
    return False


def split_zh_semantic(text: str, max_chars: int, min_merge: int) -> list[str]:
    """按段落与步骤边界切分中文正文，合并过短段。"""
    text = text.strip()
    if not text:
        return []

    raw_segments: list[str] = []
    current_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current_lines:
                raw_segments.append("\n".join(current_lines))
                current_lines = []
            continue
        if is_step_boundary(stripped) and current_lines:
            raw_segments.append("\n".join(current_lines))
            current_lines = [stripped]
        else:
            current_lines.append(stripped)

    if current_lines:
        raw_segments.append("\n".join(current_lines))

    if not raw_segments:
        raw_segments = [text]

    # 合并过短段到上一段
    merged: list[str] = []
    for seg in raw_segments:
        if merged and len(seg) < min_merge:
            merged[-1] = merged[-1] + "\n" + seg
        elif merged and len(merged[-1]) < min_merge:
            merged[-1] = merged[-1] + "\n" + seg
        else:
            merged.append(seg)

    # 超长单段再按字符窗切（兜底）
    final: list[str] = []
    for seg in merged:
        if len(seg) <= max_chars:
            final.append(seg)
            continue
        start = 0
        while start < len(seg):
            end = min(start + max_chars, len(seg))
            if end < len(seg):
                cut = seg.rfind("\n", start, end)
                if cut > start + max_chars // 2:
                    end = cut
            final.append(seg[start:end].strip())
            start = end
    return [s for s in final if s.strip()]


def group_to_chunks(
    group: dict,
    *,
    max_chunk_chars: int,
    min_merge_chars: int,
    source_doc: str,
) -> list[dict]:
    group_id = group["group_id"]
    section = group.get("section")
    question = group.get("question", "")
    answer_zh = group.get("answer_zh") or ""
    answer_en = group.get("answer_en") or ""
    images = list(group.get("images") or [])
    lang = detect_lang(answer_zh, answer_en)

    zh_len = len(answer_zh.strip())
    is_long = zh_len > max_chunk_chars

    base_meta = {
        "group_id": group_id,
        "section": section,
        "question": question,
        "lang": lang,
        "source_doc": source_doc,
        "content_en_full": answer_en,
        "image_captions": [],
    }

    if not is_long:
        chunk_id = f"{group_id}_c01"
        content_zh = answer_zh.strip()
        return [
            {
                **base_meta,
                "chunk_id": chunk_id,
                "parent_chunk_id": None,
                "chunk_role": "leaf",
                "retrievable": True,
                "content_zh": content_zh,
                "content_en": answer_en,
                "embedding_text": build_embedding_text(
                    section, question, content_zh, answer_en, lang
                ),
                "images": images,
                "has_image": bool(images),
            }
        ]

    # 长组：父块 + 子块
    parent_id = f"{group_id}_p"
    parent = {
        **base_meta,
        "chunk_id": parent_id,
        "parent_chunk_id": None,
        "chunk_role": "parent",
        "retrievable": False,
        "content_zh": answer_zh,
        "content_en": answer_en,
        "embedding_text": build_embedding_text(
            section, question, answer_zh, answer_en, lang
        ),
        "images": images,
        "has_image": bool(images),
    }

    zh_parts = split_zh_semantic(answer_zh, max_chunk_chars, min_merge_chars)
    if not zh_parts:
        zh_parts = [answer_zh] if answer_zh.strip() else [""]

    children: list[dict] = []
    for i, part in enumerate(zh_parts, start=1):
        child_id = f"{group_id}_c{i:02d}"
        children.append(
            {
                **base_meta,
                "chunk_id": child_id,
                "parent_chunk_id": parent_id,
                "chunk_role": "child",
                "retrievable": True,
                "content_zh": part,
                "content_en": "",  # 英文整段在父块
                "embedding_text": build_embedding_text(
                    section, question, part, "", lang
                ),
                "images": [],
                "has_image": bool(images),  # 组内有图，命中子块后回父块取图
            }
        )

    return [parent, *children]


def convert_groups_to_chunks(
    groups: list[dict],
    *,
    max_chunk_chars: int,
    min_merge_chars: int,
    source_doc: str,
) -> dict:
    all_chunks: list[dict] = []
    stats = {
        "groups": len(groups),
        "leaf_chunks": 0,
        "parent_chunks": 0,
        "child_chunks": 0,
        "retrievable_chunks": 0,
        "with_images_on_parent": 0,
    }

    for group in groups:
        chunks = group_to_chunks(
            group,
            max_chunk_chars=max_chunk_chars,
            min_merge_chars=min_merge_chars,
            source_doc=source_doc,
        )
        for c in chunks:
            role = c["chunk_role"]
            if role == "leaf":
                stats["leaf_chunks"] += 1
            elif role == "parent":
                stats["parent_chunks"] += 1
                if c["has_image"]:
                    stats["with_images_on_parent"] += 1
            elif role == "child":
                stats["child_chunks"] += 1
            if c.get("retrievable"):
                stats["retrievable_chunks"] += 1
        all_chunks.extend(chunks)

    return {
        "meta": {
            "source_doc": source_doc,
            "max_chunk_chars": max_chunk_chars,
            "min_merge_chars": min_merge_chars,
            "stats": stats,
        },
        "chunks": all_chunks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="qa_groups.json → 向量库 chunks（含父子块）"
    )
    parser.add_argument("qa_groups_json", type=Path, help="qa_groups.json 路径")
    parser.add_argument("-o", "--output", type=Path, required=True, help="输出 chunks.json")
    parser.add_argument(
        "--max-chunk-chars",
        type=int,
        default=400,
        help="超过此长度（answer_zh 字符数）触发长组子切分",
    )
    parser.add_argument(
        "--min-merge-chars",
        type=int,
        default=40,
        help="合并过短子段的最小阈值",
    )
    parser.add_argument(
        "--doc-name",
        default="",
        help="源文档名（写入 source_doc 元数据）",
    )
    args = parser.parse_args()

    if not args.qa_groups_json.is_file():
        raise SystemExit(f"file not found: {args.qa_groups_json}")

    groups = json.loads(args.qa_groups_json.read_text(encoding="utf-8"))
    source_doc = args.doc_name or args.qa_groups_json.parent.name

    result = convert_groups_to_chunks(
        groups,
        max_chunk_chars=args.max_chunk_chars,
        min_merge_chars=args.min_merge_chars,
        source_doc=source_doc,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    s = result["meta"]["stats"]
    print(f"groups: {s['groups']}", file=sys.stderr)
    print(
        f"chunks total: {len(result['chunks'])} "
        f"(leaf={s['leaf_chunks']} parent={s['parent_chunks']} child={s['child_chunks']})",
        file=sys.stderr,
    )
    print(f"retrievable (for embedding): {s['retrievable_chunks']}", file=sys.stderr)
    print(f"parents with images: {s['with_images_on_parent']}", file=sys.stderr)
    print(f"written: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
