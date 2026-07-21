#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-A3S-EXT-01 · orphan overlay 配图缺口扫描：docx inline 图 vs qa_groups images[]."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from qa_doc_extractor import extract_images_from_paragraph, get_heading_level, iter_block_items

DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
QA_GROUPS = ROOT / "_scratch/run-006/qa_groups.json"
OUT_MD = Path(__file__).with_name("a3s_ext01_image_gap_scan.md")
OUT_JSON = Path(__file__).with_name("a3s_ext01_image_gap_scan.json")

IMAGE_REF_RE = re.compile(r"screenshot|as shown|见图|如下图|\bsee .{0,20}below\b", re.I)
EXT_IDS = [f"qa_{i:03d}" for i in range(29, 44)]


def scan_docx_images(doc: Document) -> list[dict]:
    rows: list[dict] = []
    state: dict | None = None
    counter = [0]
    img_dir = Path(__file__).with_name("_tmp_img_scan")
    img_dir.mkdir(exist_ok=True)

    def flush() -> None:
        if state and state.get("h1"):
            rows.append(dict(state))

    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        level = get_heading_level(block)
        if level == 1:
            flush()
            state = {
                "h1": text,
                "in_h2": False,
                "orphan_imgs": 0,
                "h2_imgs": 0,
                "orphan_image_refs": [],
            }
            continue
        if state is None:
            continue
        if level in (2, 3):
            state["in_h2"] = True
            continue
        imgs = extract_images_from_paragraph(block, doc, str(img_dir), counter)
        if imgs:
            if state["in_h2"]:
                state["h2_imgs"] += len(imgs)
            else:
                state["orphan_imgs"] += len(imgs)
        if text and not state["in_h2"] and IMAGE_REF_RE.search(text):
            state["orphan_image_refs"].append(text[:120])
    flush()
    return rows


def main() -> None:
    doc = Document(str(DOCX))
    rows = scan_docx_images(doc)
    groups = json.loads(QA_GROUPS.read_text(encoding="utf-8"))
    by_id = {g["group_id"]: g for g in groups}

    ext_rows = []
    for gid in EXT_IDS:
        g = by_id.get(gid)
        if not g:
            continue
        en = g.get("answer_en") or ""
        zh = g.get("answer_zh") or ""
        ext_rows.append(
            {
                "group_id": gid,
                "section": g.get("section", "")[:60],
                "images_count": len(g.get("images") or []),
                "en_image_ref": bool(IMAGE_REF_RE.search(en)),
                "zh_image_ref": bool(IMAGE_REF_RE.search(zh)),
            }
        )

    orphan_h1_with_imgs = [r for r in rows if r["orphan_imgs"] > 0 or r["orphan_image_refs"]]
    baseline_with_imgs = [
        g for g in groups if g["group_id"] <= "qa_028" and g.get("images")
    ]

    report = {
        "docx_h1_orphan_image": orphan_h1_with_imgs,
        "ext_groups": ext_rows,
        "baseline_groups_with_images": len(baseline_with_imgs),
        "baseline_image_total": sum(len(g.get("images") or []) for g in baseline_with_imgs),
        "ext_groups_images_total": sum(r["images_count"] for r in ext_rows),
        "ext_en_ref_no_images": [
            r for r in ext_rows if (r["en_image_ref"] or r["zh_image_ref"]) and r["images_count"] == 0
        ],
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# A3S EXT-01 · orphan 配图缺口扫描",
        "",
        f"**docx**：`{DOCX.name}` · **prod**：`qa_029`–`qa_043`",
        "",
        "## 结论性质",
        "",
        "- **新发现**：BL-A3S-EXT-01 overlay 脚本只抽 **orphan 段落文字 + URL→links[]**，**未走** `qa_doc_extractor` 的 inline 图抽取。",
        "- **系统性**：凡 H1 orphan 段内嵌图 + 正文写 “see screenshot below” 的，prod `images[]` 均为空。",
        "- **非已知 backlog**：此前验收维是 links / eval / thin-ZH，**未列配图完整性 gate**。",
        "",
        "## docx · H1 orphan 区含图或文字指图",
        "",
        "| H1 | orphan 图 | H2 图 | 文字指图 |",
        "| --- | ---: | ---: | --- |",
    ]
    for r in orphan_h1_with_imgs:
        refs = "; ".join(r["orphan_image_refs"][:1])[:50] or "—"
        lines.append(
            f"| {r['h1'][:45]} | {r['orphan_imgs']} | {r['h2_imgs']} | {refs} |"
        )

    lines += [
        "",
        "## qa_029–043 · images[] vs 正文指图",
        "",
        "| group | images | EN指图 | ZH指图 | section |",
        "| --- | ---: | :---: | :---: | --- |",
    ]
    for r in ext_rows:
        lines.append(
            f"| {r['group_id']} | {r['images_count']} | {'✓' if r['en_image_ref'] else '·'} | "
            f"{'✓' if r['zh_image_ref'] else '·'} | {r['section'][:40]} |"
        )

    lines += [
        "",
        f"**baseline qa_001–028**：{len(baseline_with_imgs)} 组有图 · 共 {report['baseline_image_total']} 张",
        f"**EXT qa_029–043**：{report['ext_groups_images_total']} 张 · **指图无图** {len(report['ext_en_ref_no_images'])} 组",
        "",
        "## 指图但 images[] 为空（需修）",
        "",
    ]
    for r in report["ext_en_ref_no_images"]:
        lines.append(f"- **{r['group_id']}** · {r['section']}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)
    print(f"orphan H1 with imgs/refs: {len(orphan_h1_with_imgs)}")
    print(f"ext ref-no-image: {len(report['ext_en_ref_no_images'])}")


if __name__ == "__main__":
    main()
