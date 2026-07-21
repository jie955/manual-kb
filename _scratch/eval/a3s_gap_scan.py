#!/usr/bin/env python3
"""A3S docx vs run-006 qa_groups / run-007 manifest — strict gap scan."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from qa_doc_extractor import get_heading_level, iter_block_items

DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
QA_GROUPS = ROOT / "_scratch/run-006/qa_groups.json"
MANIFEST = ROOT / "_scratch/run-007/chroma_captioned/manifest.json"
OUT_JSON = Path(__file__).with_name("a3s_gap_scan.json")
OUT_MD = Path(__file__).with_name("a3s_gap_scan.md")


def h1_num(section: str) -> str:
    m = re.match(r"^([一二三四五六七八九十]+)、", section or "")
    return m.group(1) if m else ""


def norm_section(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    s = re.sub(r"^[一二三四五六七八九十]+、", "", s)
    return s.lower()


def match_groups_to_h1(h1: str, groups: list[dict]) -> list[dict]:
    h1_n = norm_section(h1)
    matched: list[dict] = []
    for g in groups:
        sec = g["section"]
        sec_n = norm_section(sec)
        if sec == h1:
            matched.append(g)
        elif sec_n == h1_n:
            matched.append(g)
        elif len(h1_n) > 8 and (h1_n in sec_n or sec_n in h1_n):
            matched.append(g)
    return matched


def scan_docx() -> list[dict]:
    doc = Document(str(DOCX))
    rows: list[dict] = []
    current_h1: str | None = None
    current_h2: str | None = None
    h2_list: list[str] = []
    orphan_paras = 0

    def flush():
        nonlocal h2_list, orphan_paras
        if current_h1 is None:
            return
        rows.append(
            {
                "h1": current_h1,
                "h1_num": h1_num(current_h1),
                "h2_headings": list(h2_list),
                "h2_count": len(h2_list),
                "orphan_para_count": orphan_paras,
            }
        )
        h2_list.clear()
        orphan_paras = 0

    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        text = block.text.strip()
        if not text:
            continue
        level = get_heading_level(block)
        if level == 1:
            flush()
            current_h1 = text
            current_h2 = None
        elif level in (2, 3) and current_h1:
            current_h2 = text
            h2_list.append(text)
        elif current_h1 and current_h2 is None:
            orphan_paras += 1

    flush()
    return rows


def load_groups() -> list[dict]:
    return json.loads(QA_GROUPS.read_text(encoding="utf-8"))


def manifest_group_ids() -> set[str]:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    chunks = raw["chunks"] if isinstance(raw, dict) else raw
    return {
        c["group_id"]
        for c in chunks
        if c.get("is_retrievable", True) and not c.get("parent_id")
    }


def main() -> None:
    docx_rows = scan_docx()
    groups = load_groups()
    prod_ids = manifest_group_ids()

    lines = [
        "# A3S docx · 严格对照 gap scan",
        "",
        "**手测基准**：`samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx`（18 个 H1）",
        f"**prod**：`_scratch/run-007/chroma_captioned` · **{len(prod_ids)}** retrievable root groups",
        f"**extract**：`_scratch/run-006/qa_groups.json` · **{len(groups)}** groups",
        "",
        "## H1 覆盖总览",
        "",
        "| # | H1（docx） | H2 | orphan 段 | prod 组 | 状态 |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]

    out_sections: list[dict] = []
    missing_h1: list[str] = []
    partial_h1: list[str] = []
    covered_h1: list[str] = []

    for row in docx_rows:
        sec_groups = match_groups_to_h1(row["h1"], groups)
        h2c = row["h2_count"]
        orphan = row["orphan_para_count"]
        num = row["h1_num"] or "—"

        if not sec_groups:
            status = "❌ 未入库"
            missing_h1.append(row["h1"])
        elif orphan > 0 and h2c == 0 and not sec_groups:
            status = "❌ 未入库"
            missing_h1.append(row["h1"])
        elif orphan > 0:
            status = "✅ overlay" if h2c == 0 else "⚠️ 有组+orphan"
            covered_h1.append(row["h1"])
            if h2c > 0:
                partial_h1.append(row["h1"])
        else:
            status = "✅ 已入库"
            covered_h1.append(row["h1"])

        lines.append(
            f"| {num} | {row['h1'][:44]} | {h2c} | {orphan} | {len(sec_groups)} | {status} |"
        )

        gids = [g["group_id"] for g in sec_groups]
        out_sections.append(
            {
                **row,
                "prod_groups": gids,
                "prod_questions": [g["question"] for g in sec_groups],
                "status": status,
                "in_chroma": all(g in prod_ids for g in gids) if gids else False,
            }
        )

    overlay_h1 = [r["h1"] for r in out_sections if r["status"] == "✅ overlay"]
    lines.extend(
        [
            "",
            f"**汇总**：18 H1 · ✅ 全量 {len(covered_h1) - len(partial_h1) - len(overlay_h1)} · ✅ overlay {len(overlay_h1)} · ⚠️ partial {len(partial_h1)} · ❌ 未入库 {len(missing_h1)}",
            "",
            "## ❌ 未入库 H1（docx 有 · prod 无）",
            "",
        ]
    )
    for h in missing_h1:
        lines.append(f"- {h}")

    lines.extend(["", "## ⚠️ 已入库但 docx 仍有 orphan 段（H1 正文无 H2）", ""])
    for h in partial_h1:
        lines.append(f"- {h}")

    lines.extend(["", "## ✅ prod 组明细（按 docx H1）", ""])
    for sec in out_sections:
        if not sec["prod_groups"]:
            continue
        lines.append(f"### {sec['h1_num'] or '—'} · {sec['h1'][:55]}")
        for g, q in zip(sec["prod_groups"], sec["prod_questions"]):
            lines.append(f"- **{g}** · {q}")
        if sec["orphan_para_count"]:
            lines.append(f"- _（另有 {sec['orphan_para_count']} 段 H1 orphan 正文未入库）_")
        lines.append("")

    payload = {
        "docx": str(DOCX.relative_to(ROOT)).replace("\\", "/"),
        "h1_count": len(docx_rows),
        "prod_group_count": len(prod_ids),
        "extract_group_count": len(groups),
        "missing_h1": missing_h1,
        "partial_h1": partial_h1,
        "covered_h1": covered_h1,
        "sections": out_sections,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD)
    print(
        f"docx H1={len(docx_rows)} · missing={len(missing_h1)} · partial={len(partial_h1)} · prod={len(prod_ids)}"
    )


if __name__ == "__main__":
    main()
