#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-07: scan all AD5S qa_groups for is_thin_zh boundaries."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from display_content_utils import count_zh_numbered_steps, is_thin_zh, supplement_en_text, thin_zh_reason
from context_builder import build_context_block

QA_GROUPS = ROOT / "_scratch/run-ad5s/qa_groups.json"
CHUNKS = ROOT / "_scratch/run-ad5s/chunks_captioned.json"
OUT_JSON = Path(__file__).with_name("thin_zh_scan_ad5s.json")
OUT_MD = Path(__file__).with_name("thin_zh_scan_ad5s.md")


def norm_text(v) -> str:
    if isinstance(v, list):
        return "\n".join(v)
    return (v or "").strip()


def main() -> None:
    groups = json.loads(QA_GROUPS.read_text(encoding="utf-8"))
    chunks_by_gid = {}
    for c in json.loads(CHUNKS.read_text(encoding="utf-8")):
        if c.get("is_retrievable", True):
            chunks_by_gid.setdefault(c["group_id"], c)

    rows = []
    for g in groups:
        gid = g["group_id"]
        zh = norm_text(g.get("answer_zh"))
        en = norm_text(g.get("answer_en"))
        zl, el = len(zh), len(en)
        ratio = round(zl / el, 4) if el else None
        thin = is_thin_zh(zh, en)
        reason = thin_zh_reason(zh, en)
        steps = count_zh_numbered_steps(zh)
        chunk = chunks_by_gid.get(gid, {})
        czh = (chunk.get("content_zh") or "").strip()
        cen = (chunk.get("content_en") or "").strip()
        thin_chunk = is_thin_zh(czh, cen) if chunk else None

        ctx = build_context_block(
            {
                "section": g.get("section"),
                "question": g.get("question"),
                "content_zh": czh or zh,
                "content_en": cen or en,
                "images": g.get("images") or [],
                "links": g.get("links") or [],
            }
        )
        has_en_sup = "英文操作步骤（中文过短，须参考）" in ctx
        en_in_ctx = len(ctx)

        rows.append(
            {
                "group_id": gid,
                "question": g.get("question", "")[:60],
                "section": (g.get("section") or "")[:50],
                "zh_len": zl,
                "en_len": el,
                "ratio": ratio,
                "thin_qa_groups": thin,
                "thin_reason": reason,
                "zh_steps": steps,
                "thin_chunk": thin_chunk,
                "zh_preview": zh[:80].replace("\n", " "),
                "context_has_en_supplement": has_en_sup,
                "context_len": en_in_ctx,
                "en_supplement_len": len(supplement_en_text(czh or zh, cen or en) or ""),
            }
        )

    thin_rows = [r for r in rows if r["thin_qa_groups"]]
    borderline = [
        r
        for r in rows
        if not r["thin_qa_groups"]
        and r["en_len"]
        and (
            (r["zh_len"] < 120 and r["ratio"] and r["ratio"] < 0.35)
            or (r["zh_len"] >= 70 and r["zh_len"] < 90 and r["en_len"] > 200)
        )
    ]

    out = {
        "group_count": len(rows),
        "thin_count": len(thin_rows),
        "borderline_not_thin": borderline,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# BL-V1-07 · AD5S thin-ZH 全库扫描",
        "",
        f"**组数** {len(rows)} · **thin** {len(thin_rows)} · **边界未触发** {len(borderline)}",
        "",
        "## 判定规则（v2 · 2026-07-05）",
        "",
        "1. zh 空 → thin",
        "2. zh < 80 且 en > 3×zh",
        "3. en ≥ 200 且 zh/en < 8%",
        "4. 编号步骤 < 3 且 en ≥ 400 且 zh < 250",
        "5. 编号步骤 ≥ 3 且 zh < 150 且 en ≥ 800 且 zh/en < 15%",
        "",
        "> v1 的 zh/en<25% 误触 **30/34**；v2 全库 **见 thin_reason 列**",
        "",
        "## thin 组",
        "",
        "| group | zh | en | ratio | steps | reason | question |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for r in sorted(thin_rows, key=lambda x: x["ratio"] or 0):
        lines.append(
            f"| {r['group_id']} | {r['zh_len']} | {r['en_len']} | {r['ratio']} | {r['zh_steps']} | {r['thin_reason']} | {r['question'][:40]} |"
        )

    lines.extend(
        [
            "",
            "## 非 thin（按 ratio 升序 · 边界观察）",
            "",
            "| group | zh | en | ratio | thin? |",
            "| --- | ---: | ---: | ---: | :---: |",
        ]
    )
    for r in sorted([x for x in rows if not x["thin_qa_groups"]], key=lambda x: x["ratio"] or 999):
        flag = "**←边界**" if r in borderline else ""
        lines.append(
            f"| {r['group_id']} | {r['zh_len']} | {r['en_len']} | {r['ratio']} | {flag} |"
        )

    lines.extend(["", "## 重点边界", ""])
    for gid in ("qa_022", "qa_001", "qa_008", "qa_025", "qa_028"):
        r = next(x for x in rows if x["group_id"] == gid)
        lines.append(
            f"- **{gid}**: zh={r['zh_len']} en={r['en_len']} ratio={r['ratio']} "
            f"thin={r['thin_qa_groups']} · preview: `{r['zh_preview'][:60]}…`"
        )

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON} and {OUT_MD}")
    print(f"thin={len(thin_rows)} / {len(rows)}")
    for r in thin_rows:
        print(f"  {r['group_id']} zh={r['zh_len']} en={r['en_len']} ratio={r['ratio']} reason={r['thin_reason']} steps={r['zh_steps']}")


if __name__ == "__main__":
    main()
