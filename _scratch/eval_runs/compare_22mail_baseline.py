#!/usr/bin/env python3
"""Compare post-refactor 22-mail batch vs Round 0 baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "_scratch/eval/cs_22mail_eval_round0.json"
CURRENT = ROOT / "_scratch/eval_runs/cs_22mail_post_refactor_2026-07-10.json"
OUT = ROOT / "_scratch/eval_runs/cs_22mail_compare_2026-07-10.md"


def _audit_flags(row: dict) -> list[str]:
    a = row.get("reply_audit") or {}
    flags = []
    if row.get("reply_truncated"):
        flags.append("truncated")
    if row.get("reply_incomplete_reason"):
        flags.append(f"incomplete:{row['reply_incomplete_reason']}")
    if a.get("proceed_ref"):
        flags.append("proceed_ref")
    if a.get("check_step_ref"):
        flags.append("check_step_ref")
    if a.get("glued_steps"):
        flags.append("glued_steps")
    if row.get("context_zh_leak"):
        flags.append("zh_leak")
    return flags


def summarize(data: dict) -> dict:
    rows = data["results"]
    scorable = [r for r in rows if r.get("top1_hit") is not None]
    top1_hits = sum(1 for r in scorable if r.get("top1_hit"))
    mvp19 = [r for r in rows if r.get("mvp19") == "是"]
    mvp_top1 = sum(1 for r in mvp19 if r.get("top1_hit"))
    leaks = sum(1 for r in rows if r.get("context_zh_leak"))
    trunc = sum(1 for r in rows if r.get("reply_truncated"))
    gen = sum(1 for r in rows if r.get("generated_reply_en"))
    audit_bad = sum(1 for r in rows if _audit_flags(r))
    return {
        "cases": len(rows),
        "mvp19": len(mvp19),
        "top1_hit": f"{top1_hits}/{len(scorable)}",
        "mvp19_top1": f"{mvp_top1}/{len(mvp19)}",
        "zh_leak": f"{leaks}/{len(rows)}",
        "generated": f"{gen}/{len(rows)}",
        "truncated": trunc,
        "audit_flags": audit_bad,
    }


def main() -> int:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    current_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CURRENT
    current = json.loads(current_path.read_text(encoding="utf-8"))

    b = summarize(baseline)
    c = summarize(current)
    base_by = {r["scenario_id"]: r for r in baseline["results"]}
    cur_by = {r["scenario_id"]: r for r in current["results"]}

    lines = [
        "# 22-Mail Batch · Post-Refactor Compare",
        "",
        f"**Baseline**: `{BASELINE.name}` ({baseline['meta'].get('generated_at', '')[:10]})",
        f"**Current**: `{current_path.name}` ({current['meta'].get('generated_at', '')[:10]})",
        "",
        "## Mechanical metrics",
        "",
        "| Metric | Baseline | Current |",
        "| --- | --- | --- |",
        f"| Cases | {b['cases']} | {c['cases']} |",
        f"| MVP19 subset | {b['mvp19']} | {c['mvp19']} |",
        f"| Top1 hit (scorable) | {b['top1_hit']} | {c['top1_hit']} |",
        f"| MVP19 Top1 hit | {b['mvp19_top1']} | {c['mvp19_top1']} |",
        f"| context_zh_leak | {b['zh_leak']} | {c['zh_leak']} |",
        f"| Generated | {b['generated']} | {c['generated']} |",
        f"| Truncated | {b['truncated']} | {c['truncated']} |",
        f"| Audit/format flags | {b['audit_flags']} | {c['audit_flags']} |",
        "",
        "## Per-case deltas",
        "",
        "| Case | Top1 | Lib | Style | Reply len | Flags |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for sid in sorted(cur_by.keys()):
        o = base_by.get(sid, {})
        n = cur_by[sid]
        top1_delta = f"`{o.get('top1_group')}`→`{n.get('top1_group')}`"
        if o.get("top1_hit") != n.get("top1_hit"):
            top1_delta += f" [{o.get('top1_hit')}→{n.get('top1_hit')}]"
        lib_delta = f"`{o.get('matched_library')}`→`{n.get('matched_library')}`"
        style_o = (o.get("style") or {}).get("family_id", "—")
        style_n = (n.get("style") or {}).get("family_id", "—")
        style_delta = f"`{style_o}`" if style_o == style_n else f"`{style_o}`→`{style_n}`"
        len_delta = f"{o.get('reply_len', 0)}→{n.get('reply_len', 0)}"
        notes = []
        if o.get("top1_group") != n.get("top1_group"):
            notes.append("top1 changed")
        if style_o != style_n:
            notes.append("style changed")
        if o.get("reply_len", 0) != n.get("reply_len", 0):
            notes.append("len changed")
        flags = _audit_flags(n)
        if flags:
            notes.extend(flags)
        lines.append(
            f"| {sid} | {top1_delta} | {lib_delta} | {style_delta} | {len_delta} | "
            f"{', '.join(notes) if notes else '—'} |"
        )

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            "- **Mechanical (K/G)**: see table above",
            "- **Gate S / ④整体通过**: human ①②③④ in xlsx; compare `generated_reply_en` in JSON",
            "",
        ]
    )

    no_regression = (
        c["top1_hit"] == b["top1_hit"]
        and c["zh_leak"] == b["zh_leak"]
        and c["generated"] == b["generated"]
    )
    lines.append(
        f"- **Post-refactor mechanical**: {'✅ no regression' if no_regression else '⚠️ see deltas'}"
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print("baseline", b)
    print("current ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
