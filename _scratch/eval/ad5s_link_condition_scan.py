#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""扫 AD5S qa_groups：条件化链接 / 协商形态（只读，写 eval 留档）。

⚠️ 输出仅供人工参考，不是最终分类权威源。
启发式基于关键词/正则，存在误报（如 qa_004/027 曾误标 erm12_receiver）。
定稿分类见 troubleshooting_schema_v1.md 与人工 taxonomy 核对。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://\S+")

# 条件化表述（启发式 · 仅供人工参考，非 extract 输出）
CONDITION_PATTERNS = [
    ("region_us_uk", re.compile(r"\bUS\b|\bUK\b|amazon\.com|amazon\.co\.uk", re.I)),
    ("stall_direction", re.compile(r"拉开门|推开门|pull.to.open|push.to.open|opening abnormally|closing abnormally", re.I)),
    ("method_fallback", re.compile(r"if (?:step |the )?(?:1|2|3)|方法[一二三]|still (?:not|no)|仍无反应|若.*仍", re.I)),
    # 仅 ERM12 产品名或中文「加外接收器」排查步；不含 sizing 段落的 generic external receiver
    ("erm12_receiver", re.compile(r"ERM12|加外接收器|外置接收器", re.I)),
    ("disclaimer_no_sale", re.compile(r"do not have .{0,80} for sale|not for sale in our store|本店.*不卖|暂无.*售", re.I)),
    ("youtube_howto", re.compile(r"youtube\.com|youtu\.be", re.I)),
]

DISCLAIMER = """\
> **⚠️ 启发式扫描 · 仅供人工参考**
>
> 本表由 `ad5s_link_condition_scan.py` 关键词/正则自动生成，**不是** extract 或 schema 的权威分类。
> 已知误报类型：generic `external receiver` 出现在规格/选型段（已收紧 ERM12 规则）；`method_fallback` 与互斥 `branches` 混在同一 hint 列。
> 定稿语义见 [`troubleshooting_schema_v1.md`](./troubleshooting_schema_v1.md) 与下方「语义分类」人工核对节。
"""

MANUAL_TAIL_MARKER = "## schema 设计备忘"


def scan_group(g: dict) -> dict:
    gid = g["group_id"]
    zh = g.get("answer_zh") or ""
    en = g.get("answer_en") or ""
    both = zh + "\n" + en
    urls = URL_RE.findall(both)
    hits = [name for name, pat in CONDITION_PATTERNS if pat.search(both)]
    return {
        "group_id": gid,
        "question": (g.get("question") or "")[:50],
        "url_count": len(urls),
        "link_count": len(g.get("links") or []),
        "negotiation_count": len(g.get("negotiation_offers") or []),
        "condition_hints": hits,
        "zh_len": len(zh),
        "en_len": len(en),
    }


def build_scan_body(path: Path, groups: list) -> str:
    rows = [scan_group(g) for g in groups]
    lines = [
        "# AD5S 链接/条件形态扫描",
        "",
        DISCLAIMER,
        "",
        f"源：`{path.as_posix()}` · 组数 {len(groups)}",
        "",
        "## 含 links[] 的组",
        "",
        "| group | question | links | negotiation | condition_hints |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for r in rows:
        if not r["link_count"]:
            continue
        q = r["question"].replace("|", "/")
        hints = ", ".join(r["condition_hints"]) or "—"
        lines.append(
            f"| {r['group_id']} | {q} | {r['link_count']} | "
            f"{r['negotiation_count']} | {hints} |"
        )

    lines += [
        "",
        "## 无 URL 但有 condition 启发式的组",
        "",
        "| group | question | hints |",
        "| --- | --- | --- |",
    ]
    for r in rows:
        if r["condition_hints"] and not r["link_count"]:
            q = r["question"].replace("|", "/")
            lines.append(
                f"| {r['group_id']} | {q} | {', '.join(r['condition_hints'])} |"
            )

    lines += ["", "## negotiation_offers（BL-V1-06）", ""]
    neg = [r for r in rows if r["negotiation_count"]]
    if not neg:
        lines.append("（无）")
    else:
        for r in neg:
            g = next(x for x in groups if x["group_id"] == r["group_id"])
            lines.append(f"- **{r['group_id']}** ×{r['negotiation_count']}")
            for o in g.get("negotiation_offers", []):
                t = o["text"].replace("|", "/")
                lines.append(f"  - `{t}`")

    return "\n".join(lines) + "\n"


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "_scratch/run-ad5s-dry-v106/qa_groups.json")
    out_path = Path(
        sys.argv[2]
        if len(sys.argv) > 2
        else "_scratch/eval/ad5s_link_condition_scan.md"
    )
    groups = json.loads(path.read_text(encoding="utf-8"))
    body = build_scan_body(path, groups)

    manual_tail = ""
    if out_path.exists():
        old = out_path.read_text(encoding="utf-8")
        if MANUAL_TAIL_MARKER in old:
            manual_tail = old[old.index(MANUAL_TAIL_MARKER) - 1 :]  # keep leading newline

    out_path.write_text(body + manual_tail, encoding="utf-8")
    print(f"written: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
