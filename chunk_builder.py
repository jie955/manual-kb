#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chunk_builder.py

用途：
    在 qa_doc_extractor.py 输出的 qa_groups.json 基础上，按既定切片策略
    生成可直接喂给向量库的最终 chunks 列表（父子块结构 + 完整元数据）。

切片策略（对应诊断/策略讨论中的五点）：
    1. 单元大小分级：
       - 短组（中文正文长度 < SHORT_GROUP_THRESHOLD）：整组作为一个检索块，
         不再拆分，避免破坏语义完整性。
       - 长组（中文正文长度 >= SHORT_GROUP_THRESHOLD）：按自然段落做二次切分，
         每个子块都继承父组标题作为前缀，保证脱离上下文也能读懂。
    2. 检索语言：仅用 question + answer_zh 生成"用于检索的正文"（embedding_text）；
       answer_en 作为附属字段随块返回，不参与相似度匹配。
    3. 图片挂靠：图片不单独成块，作为所属块的 images 字段一起存储。
    4. 元数据：每个块补齐 chunk_id / group_id / section / question /
       has_image / lang / is_child 等字段，便于检索、过滤、追溯。
    5. 父子块结构：
       - 短组：parent 块本身即用于检索（无子块，parent_id 为空）。
       - 长组：拆出多个 child 块用于向量检索（embedding_text 更聚焦、更短），
         同时保留一个 parent 块（不参与检索，is_retrievable=False）存放
         该组的完整内容，供命中 child 后关联取出、返回给大模型的完整上下文。

用法：
    python chunk_builder.py <输入 qa_groups.json 路径> <输出目录>

输出：
    <输出目录>/chunks.json —— 最终 chunks 列表，可直接导入向量库
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from en_representation import append_email_verbatim_to_embedding
from translate import translate_batch

# 长组判定阈值：中文正文字符数达到此值，视为"长组"，需要二次切分
SHORT_GROUP_THRESHOLD = 300

# 子块目标长度区间（中文字符数），二次切分时尽量落在这个区间内
CHILD_MIN_LENGTH = 80
CHILD_MAX_LENGTH = 400

# 中文正文低于此长度，视为"实质为空"，需要走翻译兜底
EMPTY_ZH_THRESHOLD = 5


def split_into_semantic_segments(text: str) -> list[str]:
    """
    把长组的中文正文按自然段落拆分为若干"语义子段"。
    先按换行拆分成自然段落，再把过短的相邻段落合并，
    避免出现"半句话"这种粒度过细的子块。
    """
    raw_paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    if not raw_paragraphs:
        return []

    segments: list[str] = []
    buffer = ""
    for para in raw_paragraphs:
        if not buffer:
            buffer = para
        elif len(buffer) < CHILD_MIN_LENGTH:
            buffer = buffer + "\n" + para
        else:
            segments.append(buffer)
            buffer = para

        if len(buffer) >= CHILD_MAX_LENGTH:
            segments.append(buffer)
            buffer = ""

    if buffer:
        if segments and len(buffer) < CHILD_MIN_LENGTH:
            segments[-1] = segments[-1] + "\n" + buffer
        else:
            segments.append(buffer)

    return segments


def extract_segment_label(segment: str, max_len: int = 12) -> str:
    """
    从子段首句中提取一个简短标签，用于拼接进子块前缀，
    如"太阳能供电："这种小节标记。找不到明显标记时返回空字符串。
    """
    first_line = segment.split("\n")[0].strip()
    pattern = r"^([^\s：:，,。.]{2,%d})[：:]" % max_len
    match = re.match(pattern, first_line)
    if match:
        return match.group(1)
    return ""


def build_parent_chunk(group: dict) -> dict:
    """构建父块：完整问答组内容，不参与检索，仅供命中子块后关联取出。"""
    return {
        "chunk_id": f"{group['group_id']}_parent",
        "group_id": group["group_id"],
        "parent_id": None,
        "is_child": False,
        "is_retrievable": False,
        "section": group.get("section"),
        "question": group.get("question"),
        "embedding_text": None,
        "content_zh": group.get("answer_zh", ""),
        "content_en": group.get("answer_en", ""),
        "images": group.get("images", []),
        "has_image": bool(group.get("images")),
        "links": group.get("links", []),
        "has_links": bool(group.get("links")),
        "negotiation_offers": group.get("negotiation_offers", []),
        "customer_reply_templates": group.get("customer_reply_templates", []),
        "structure_warnings": group.get("structure_warnings", []),
        "troubleshooting_ladder": group.get("troubleshooting_ladder") or [],
        "email_examples": group.get("email_examples") or [],
        "lang": "zh",
    }


def _finalize_embedding_text(base: str, group: dict) -> str:
    return append_email_verbatim_to_embedding(base, group.get("email_examples"))


def build_single_chunk(group: dict, translated_zh: str | None = None) -> dict:
    """
    短组：整组直接作为一个可检索块（无父子拆分）。

    translated_zh: 当原文 answer_zh 为空/近空时，由 translate_batch 生成的中文摘要，
        仅用于 embedding_text，不替换 content_zh。
    """
    question = group.get("question", "")
    answer_zh = group.get("answer_zh", "")
    answer_en = group.get("answer_en", "")

    is_zh_empty = len(answer_zh.strip()) < EMPTY_ZH_THRESHOLD

    if not is_zh_empty:
        embedding_text = f"{question}\n{answer_zh}".strip()
        translation_status = "not_needed"
    elif translated_zh:
        embedding_text = f"{question}\n{translated_zh}".strip()
        translation_status = "translated"
    else:
        embedding_text = f"{question}\n{answer_en}".strip()
        translation_status = "fallback_to_english"

    embedding_text = _finalize_embedding_text(embedding_text, group)

    return {
        "chunk_id": f"{group['group_id']}_c001",
        "group_id": group["group_id"],
        "parent_id": None,
        "is_child": False,
        "is_retrievable": True,
        "section": group.get("section"),
        "question": question,
        "embedding_text": embedding_text,
        "content_zh": answer_zh,
        "content_en": answer_en,
        "answer_zh_translated": translated_zh if is_zh_empty else None,
        "translation_status": translation_status,
        "images": group.get("images", []),
        "has_image": bool(group.get("images")),
        "links": group.get("links", []),
        "has_links": bool(group.get("links")),
        "negotiation_offers": group.get("negotiation_offers", []),
        "customer_reply_templates": group.get("customer_reply_templates", []),
        "structure_warnings": group.get("structure_warnings", []),
        "troubleshooting_ladder": group.get("troubleshooting_ladder") or [],
        "email_examples": group.get("email_examples") or [],
        "lang": "zh",
    }


def build_child_chunks(group: dict) -> list[dict]:
    """长组：按语义子段拆分为多个子块，每块继承父组标题作为前缀。"""
    question = group.get("question", "")
    answer_zh = group.get("answer_zh", "")
    segments = split_into_semantic_segments(answer_zh)

    if not segments:
        return [build_single_chunk(group)]

    children: list[dict] = []
    for idx, segment in enumerate(segments, start=1):
        label = extract_segment_label(segment)
        prefix = f"[问题] {question}"
        if label:
            prefix += f"\n[子场景：{label}]"
        embedding_text = f"{prefix}\n{segment}".strip()
        if idx == 1:
            embedding_text = _finalize_embedding_text(embedding_text, group)

        children.append(
            {
                "chunk_id": f"{group['group_id']}_c{idx:03d}",
                "group_id": group["group_id"],
                "parent_id": f"{group['group_id']}_parent",
                "is_child": True,
                "is_retrievable": True,
                "section": group.get("section"),
                "question": question,
                "embedding_text": embedding_text,
                "content_zh": segment,
                "content_en": None,
                "images": [],
                "has_image": False,
                "links": [],
                "has_links": bool(group.get("links")),
                "negotiation_offers": [],
                "email_examples": group.get("email_examples") or [] if idx == 1 else [],
                "lang": "zh",
            }
        )

    return children


def build_chunks(groups: list[dict]) -> list[dict]:
    empty_zh_groups = [
        g
        for g in groups
        if len(g.get("answer_zh", "").strip()) < EMPTY_ZH_THRESHOLD
        and g.get("answer_en", "").strip()
    ]
    english_texts = [g["answer_en"] for g in empty_zh_groups]
    translation_map = translate_batch(english_texts) if english_texts else {}

    chunks: list[dict] = []
    for group in groups:
        answer_zh = group.get("answer_zh", "")
        is_zh_empty = len(answer_zh.strip()) < EMPTY_ZH_THRESHOLD
        is_long_group = len(answer_zh) >= SHORT_GROUP_THRESHOLD

        if is_zh_empty:
            translated_zh = translation_map.get(group.get("answer_en", ""))
            chunks.append(build_single_chunk(group, translated_zh=translated_zh))
        elif not is_long_group:
            chunks.append(build_single_chunk(group))
        else:
            parent_chunk = build_parent_chunk(group)
            child_chunks = build_child_chunks(group)
            chunks.append(parent_chunk)
            chunks.extend(child_chunks)

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="qa_groups.json -> 最终切片 chunks.json")
    parser.add_argument("input_json", help="qa_doc_extractor.py 输出的 qa_groups.json 路径")
    parser.add_argument("output_dir", help="输出目录")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        groups = json.load(f)

    chunks = build_chunks(groups)

    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, "chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    retrievable_count = sum(1 for c in chunks if c["is_retrievable"])
    parent_count = sum(1 for c in chunks if not c["is_retrievable"])
    child_count = sum(1 for c in chunks if c["is_child"])
    single_count = retrievable_count - child_count
    translated_count = sum(
        1 for c in chunks if c.get("translation_status") == "translated"
    )
    fallback_count = sum(
        1 for c in chunks if c.get("translation_status") == "fallback_to_english"
    )

    print(f"输入问答组: {len(groups)} 个", file=sys.stderr)
    print(f"输出总块数: {len(chunks)} 个", file=sys.stderr)
    print(
        f"  - 可检索块: {retrievable_count} 个（短组整块 {single_count} + 长组子块 {child_count}）",
        file=sys.stderr,
    )
    print(f"  - 父块（不参与检索，仅供关联返回）: {parent_count} 个", file=sys.stderr)
    if translated_count or fallback_count:
        print(
            f"  - 纯英文组翻译情况: 成功翻译 {translated_count} 个, "
            f"翻译失败/未配置API退回英文 {fallback_count} 个",
            file=sys.stderr,
        )
    print(f"结果已保存: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
