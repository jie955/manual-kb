#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_doc_extractor.py

用途：
    针对"问答型"技术文档（如故障排查手册），按 Word 原生标题层级（Heading 1/2/3）
    识别问答（Q-A）分组边界，而不是依赖正文中的数字编号或固定长度切分。
    组内自动按中英文拆分正文，并将图片按其在文档中的位置关联到所属分组。

核心思路（对应诊断报告中的解决方案）：
    1. 解析阶段：直接读取 docx 的段落样式（Heading 1/2/3），不经过"转纯文本"这一步，
       避免标题层级信息丢失。
    2. 分组阶段：以 Heading 1 作为大类边界，Heading 2/3 作为具体问题（Q）边界，
       两个标题之间的所有内容（含图片、表格）归为同一个问答组。
    3. 组内细分：按字符的中/英文占比判断语言归属，不依赖正文数字编号，
       从根本上规避"中文手动编号 vs 英文 Word 列表域"不一致导致的错位问题。
    4. 图片处理：图片就地关联到所属问答组，不单独抽取成孤立切片，段落图片和
       表格单元格内的图片均支持提取。
    5. 表格处理：按文档真实流顺序遍历（不用 document.paragraphs，该 API 会
       完全跳过表格），表格按行提取，单元格间用 " | " 拼接以保留行列关系，
       避免表格被打散成互不相关的散句。

用法：
    python qa_doc_extractor.py <输入docx路径> <输出目录>

输出：
    <输出目录>/qa_groups.json   —— 结构化问答组数据
    <输出目录>/images/          —— 提取出的图片文件
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from branch_utils import attach_qa_023_structure, attach_qa_024_structure
from link_utils import apply_simple_tier_links, apply_video_tier_links
from ladder_utils import attach_troubleshooting_ladder
from link_utils import (
    find_urls,
    infer_link_type,
    is_url_only,
    pick_link_label,
    strip_urls_from_text,
)
from negotiation_utils import negotiation_offers_from_text

# ---------- 语言判定 ----------

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")


def classify_language(text: str, cjk_ratio_threshold: float = 0.15) -> str:
    """
    按中文字符占比判断段落语言归属。
    不依赖数字编号，避免中英文编号体系不一致导致的误判。
    """
    stripped = text.strip()
    if not stripped:
        return "empty"
    cjk_count = len(CJK_PATTERN.findall(stripped))
    total_count = len(re.sub(r"\s", "", stripped))
    if total_count == 0:
        return "empty"
    ratio = cjk_count / total_count
    return "zh" if ratio >= cjk_ratio_threshold else "en"


# ---------- 标题层级判定 ----------


def get_heading_level(paragraph) -> int:
    """
    返回段落的标题层级（1/2/3/4...），非标题段落返回 0。
    兼容中文/英文 Word 样式命名（如 "Heading 2" / "标题 2" / 数字样式ID）。
    """
    style_name = (paragraph.style.name or "").strip()
    match = re.search(r"(?:heading|标题)\s*(\d)", style_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


# ---------- 图片提取 ----------


def extract_images_from_paragraph(paragraph, document, image_dir, image_counter):
    """
    检查段落内的所有 run，提取其中内嵌的图片，保存到 image_dir，
    返回本段落包含的图片文件名列表（保持文档内出现顺序）。
    """
    saved_images = []
    for run in paragraph.runs:
        blips = run._element.findall(".//" + qn("a:blip"))
        for blip in blips:
            r_id = blip.get(qn("r:embed"))
            if not r_id:
                continue
            try:
                image_part = document.part.related_parts[r_id]
            except KeyError:
                continue
            image_bytes = image_part.blob
            ext = image_part.content_type.split("/")[-1]
            ext = "jpg" if ext == "jpeg" else ext
            image_counter[0] += 1
            filename = f"image_{image_counter[0]:03d}.{ext}"
            filepath = os.path.join(image_dir, filename)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            saved_images.append(filename)
    return saved_images


# ---------- 文档流遍历 ----------


def iter_block_items(document):
    """
    按文档流的真实顺序，依次产出段落（Paragraph）和表格（Table）对象。
    直接使用 document.paragraphs 会完全跳过表格内容，这里改为遍历
    document.element.body 的原始子元素并按需包装，保证顺序和完整性。
    """
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            yield Paragraph(child, document)
        elif tag == "tbl":
            yield Table(child, document)


def _push_label_candidate(group: dict, line: str) -> None:
    cands = group.setdefault("_en_label_candidates", [])
    cands.append(line.strip())
    group["_en_label_candidates"] = cands[-3:]


def _register_link(group: dict, url: str, lang: str) -> None:
    url = url.strip().rstrip(".,);]")
    if not url:
        return
    link_type = infer_link_type(url)
    label = pick_link_label(group.get("_en_label_candidates", []), url, link_type)
    group.setdefault("links", []).append(
        {
            "url": url,
            "label": label,
            "lang": lang,
            "link_type": link_type,
        }
    )


def _append_answer_text(group: dict, text: str, lang: str) -> None:
    if lang == "zh":
        group["answer_zh"].append(text)
    elif lang == "en":
        group["answer_en"].append(text)
        _push_label_candidate(group, text)


def process_paragraph(paragraph, document, image_dir, image_counter, current_group):
    """处理单个段落：提取图片、外链，按语言归类文本，写入 current_group。"""
    text = paragraph.text.strip()

    images = extract_images_from_paragraph(
        paragraph, document, image_dir, image_counter
    )
    if images:
        current_group["images"].extend(images)

    if not text:
        return

    lang = classify_language(text)
    if lang == "empty":
        return

    if is_url_only(text):
        _register_link(current_group, text, lang)
        return

    urls = find_urls(text)
    if urls:
        for url in urls:
            _register_link(current_group, url, lang)
        text = strip_urls_from_text(text)
        if not text:
            return

    _append_answer_text(current_group, text, lang)


def process_table(table, document, image_dir, image_counter, current_group):
    """
    处理表格：按行遍历所有单元格，单元格内段落同样按语言归类、提取图片。
    为保留"这是表格内容"这一结构信息，每行结果以 " | " 拼接单元格文本，
    便于后续切片时保留原始的行列关系，而不是把表格打散成无关联的散句。
    """
    for row in table.rows:
        row_zh_cells = []
        row_en_cells = []
        for cell in row.cells:
            cell_zh_parts = []
            cell_en_parts = []
            for cell_paragraph in cell.paragraphs:
                cell_text = cell_paragraph.text.strip()

                images = extract_images_from_paragraph(
                    cell_paragraph, document, image_dir, image_counter
                )
                if images:
                    current_group["images"].extend(images)

                if not cell_text:
                    continue
                lang = classify_language(cell_text)
                if lang == "empty":
                    continue
                if is_url_only(cell_text):
                    _register_link(current_group, cell_text, lang)
                    continue
                urls = find_urls(cell_text)
                if urls:
                    for url in urls:
                        _register_link(current_group, url, lang)
                    cell_text = strip_urls_from_text(cell_text)
                    if not cell_text:
                        continue
                if lang == "zh":
                    cell_zh_parts.append(cell_text)
                elif lang == "en":
                    cell_en_parts.append(cell_text)
                    _push_label_candidate(current_group, cell_text)
            if cell_zh_parts:
                row_zh_cells.append(" ".join(cell_zh_parts))
            if cell_en_parts:
                row_en_cells.append(" ".join(cell_en_parts))
        if row_zh_cells:
            current_group["answer_zh"].append("| " + " | ".join(row_zh_cells) + " |")
        if row_en_cells:
            current_group["answer_en"].append("| " + " | ".join(row_en_cells) + " |")


# ---------- 主提取逻辑 ----------


def extract_qa_groups(docx_path: str, output_dir: str):
    document = Document(docx_path)
    image_dir = os.path.join(output_dir, "images")
    os.makedirs(image_dir, exist_ok=True)
    image_counter = [0]

    groups = []
    current_section = None
    current_group = None
    group_id_counter = [0]

    def start_new_group(question_text, level, section):
        group_id_counter[0] += 1
        return {
            "group_id": f"qa_{group_id_counter[0]:03d}",
            "section": section,
            "question": question_text.strip(),
            "heading_level": level,
            "answer_zh": [],
            "answer_en": [],
            "images": [],
            "links": [],
        }

    for block in iter_block_items(document):
        if isinstance(block, Table):
            if current_group is not None:
                process_table(block, document, image_dir, image_counter, current_group)
            continue

        paragraph = block
        text = paragraph.text.strip()
        level = get_heading_level(paragraph)

        if level == 1:
            if current_group is not None:
                groups.append(current_group)
                current_group = None
            current_section = text
            continue

        if level in (2, 3):
            if current_group is not None:
                groups.append(current_group)
            current_group = start_new_group(text, level, current_section)
            continue

        if current_group is None:
            continue

        process_paragraph(
            paragraph, document, image_dir, image_counter, current_group
        )

    if current_group is not None:
        groups.append(current_group)

    for g in groups:
        g["answer_zh"] = "\n".join(g["answer_zh"])
        g["answer_en"] = "\n".join(g["answer_en"])
        g.pop("_en_label_candidates", None)
        g.setdefault("negotiation_offers", [])
        g.setdefault("structure_warnings", [])
        for field, lang in (("answer_zh", "zh"), ("answer_en", "en")):
            cleaned, offers = negotiation_offers_from_text(g[field], lang)
            g[field] = cleaned
            g["negotiation_offers"].extend(offers)
        if g.get("group_id") == "qa_023":
            if not attach_qa_023_structure(g):
                if not g.get("structure_warnings"):
                    attach_troubleshooting_ladder(g)
        elif not attach_qa_024_structure(g):
            if not g.get("structure_warnings"):
                attach_troubleshooting_ladder(g)
        apply_simple_tier_links(g)
        apply_video_tier_links(g)

    return groups


def main() -> None:
    parser = argparse.ArgumentParser(description="问答型 docx 文档结构化提取工具")
    parser.add_argument("input_docx", help="输入的 .docx 文件路径")
    parser.add_argument("output_dir", help="输出目录（结构化 JSON + 图片）")
    args = parser.parse_args()

    if not os.path.isfile(args.input_docx):
        raise SystemExit(f"file not found: {args.input_docx}")
    if not args.input_docx.lower().endswith(".docx"):
        raise SystemExit("only .docx supported")

    os.makedirs(args.output_dir, exist_ok=True)
    groups = extract_qa_groups(args.input_docx, args.output_dir)

    output_json_path = os.path.join(args.output_dir, "qa_groups.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)

    total_images = sum(len(g["images"]) for g in groups)
    total_links = sum(len(g.get("links") or []) for g in groups)
    warn_groups = [g for g in groups if g.get("structure_warnings")]
    print(f"共提取问答组: {len(groups)} 个", file=sys.stderr)
    if warn_groups:
        print(
            f"structure_warnings: {len(warn_groups)} 组须人工复核",
            file=sys.stderr,
        )
        for g in warn_groups:
            for w in g["structure_warnings"]:
                print(f"  - {w['message']}", file=sys.stderr)
    print(f"共提取图片: {total_images} 张 -> {os.path.join(args.output_dir, 'images')}", file=sys.stderr)
    print(f"共提取外链: {total_links} 条", file=sys.stderr)
    print(f"结构化结果已保存: {output_json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
