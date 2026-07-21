#!/usr/bin/env python3
# -*- coding: utf-8
"""BL-A3S-EXT-01 · classify摸底: A3S docx 12 missing H1 + §十二 partial."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from qa_doc_extractor import classify_language, get_heading_level, iter_block_items

DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
QA_GROUPS = ROOT / "_scratch/run-006/qa_groups.json"
OUT_JSON = Path(__file__).with_name("a3s_ext01_classification.json")
OUT_MD = Path(__file__).with_name("a3s_ext01_classification.md")

# 12 missing + §十二 partial（与 a3s_gap_scan 一致）
SECTION_KEYS = [
    ("四、只朝一个方向", False),
    ("五、随意开关门", False),
    ("六、缓停止有问题", False),
    ("七、自动关门不生效", False),
    ("八、开关门过程中走停或反弹", False),
    ("门机运行慢", False),
    ("十三、电机转机臂不伸缩", False),
    ("十四、机臂声音异常", False),
    ("十五、离合打不开", False),
    ("风会把门吹开", False),
    ("十七、保养与润滑", False),
    ("十八、其他产品知识", False),
    ("十二、电机电流小", True),  # partial
]

URL_RE = re.compile(r"https?://[^\s\"<>)\]]+")
IF_THEN_RE = re.compile(r"(无异响|有异响|If (?:so|not)|做步骤\d|continue to step)", re.I)
NUMBERED = re.compile(r"^\s*\d+\s+[\.\、]", re.M)


def extract_orphan_paras(doc: Document) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {k: [] for k, _ in SECTION_KEYS}
    current_key: str | None = None
    in_h2 = False
    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        if not text:
            continue
        level = get_heading_level(block)
        if level == 1:
            current_key = next((k for k, _ in SECTION_KEYS if k in text), None)
            in_h2 = False
            continue
        if level in (2, 3):
            in_h2 = True
            continue
        if current_key and not in_h2:
            out[current_key].append(text)
    return out


def tag_section(key: str, paras: list[str], is_partial: bool) -> tuple[str, str, str]:
    full = "\n".join(paras)
    n = len(paras)
    if is_partial:
        return "P", "—", f"prod 已有 qa_022–028；orphan {n} 段勿错组"
    if not paras:
        return "—", "—", "无 orphan 段（可能已有 H2）"
    if key.startswith("十四") or IF_THEN_RE.search(full) and n > 15:
        return "DT", "B", f"{n} 段 · if/异响决策 · 优先 F prose"
    if key.startswith("十三") or key.startswith("十五"):
        return "L-scenario", "B", f"{n} 段 · 可能拆 2 H2"
    if URL_RE.search(full):
        return "F", "B", f"{n} 段 · 含 URL · links[]"
    return "F", "B" if classify_language(full) == "en" or len(full) > 800 else "—", f"{n} 段 · 顺序步骤"


def main() -> None:
    doc = Document(str(DOCX))
    paras = extract_orphan_paras(doc)
    groups = json.loads(QA_GROUPS.read_text(encoding="utf-8"))
    rows = []
    for key, is_partial in SECTION_KEYS:
        p = paras.get(key, [])
        proc, z, ev = tag_section(key, p, is_partial)
        rows.append(
            {
                "section_key": key,
                "partial": is_partial,
                "orphan_count": len(p),
                "process_tag": proc,
                "z_column": z,
                "evidence": ev,
            }
        )

    md = [
        "# BL-A3S-EXT-01 · 分类摸底",
        "",
        f"**源**：`{DOCX.relative_to(ROOT)}` · prod **{len(groups)}** 组",
        "",
        "| key | orphan | tag | Z | 证据 |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for r in rows:
        md.append(
            f"| {r['section_key']} | {r['orphan_count']} | **{r['process_tag']}** | {r['z_column']} | {r['evidence']} |"
        )

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(OUT_MD)


if __name__ == "__main__":
    main()
