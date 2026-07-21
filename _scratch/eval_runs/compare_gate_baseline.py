#!/usr/bin/env python3
"""Compare latest gate run vs Phase 0 baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "_scratch/eval/cs_e2e_gate_results.json"
CURRENT = ROOT / "_scratch/eval_runs/cs_e2e_gate_2026-07-10.json"
OUT = ROOT / "_scratch/eval_runs/cs_e2e_gate_compare_2026-07-10.md"


def summarize(data: dict) -> dict:
    rows = data["results"]
    scorable = [r for r in rows if r.get("expected_groups")]
    top1_hits = sum(1 for r in scorable if r.get("top1_hit"))
    lib_hits = sum(1 for r in rows if r.get("library_hit"))
    leaks = sum(1 for r in rows if r.get("context_zh_leak"))
    gen = sum(1 for r in rows if r.get("reply_full"))
    trunc = sum(1 for r in rows if r.get("truncated"))
    return {
        "cases": len(rows),
        "top1_hit": f"{top1_hits}/{len(scorable)}",
        "library_hit": f"{lib_hits}/{len(rows)}",
        "zh_leak": f"{leaks}/{len(rows)}",
        "generated": f"{gen}/{len(rows)}",
        "truncated": trunc,
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
        "# Gate G/S · Post-Refactor Compare",
        "",
        f"**Baseline**: `{BASELINE.name}` ({baseline.get('generated')})",
        f"**Current**: `{current_path.name}` ({current.get('generated')})",
        "",
        "## Mechanical metrics (Gate G / K)",
        "",
        "| Metric | Baseline | Current |",
        "| --- | --- | --- |",
        f"| Top1 hit (scorable) | {b['top1_hit']} | {c['top1_hit']} |",
        f"| Library hit | {b['library_hit']} | {c['library_hit']} |",
        f"| context_zh_leak | {b['zh_leak']} | {c['zh_leak']} |",
        f"| Generated replies | {b['generated']} | {c['generated']} |",
        f"| Truncated | {b['truncated']} | {c['truncated']} |",
        "",
        "## Per-case",
        "",
        "| Case | Top1 | Lib | ZH leak | Style | Reply len | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for sid in sorted(base_by):
        o, n = base_by[sid], cur_by.get(sid, {})
        notes: list[str] = []
        if o.get("top1_hit") != n.get("top1_hit"):
            notes.append("top1_hit changed")
        if o.get("context_zh_leak") != n.get("context_zh_leak"):
            notes.append("zh_leak changed")
        o_style = (o.get("style") or {}).get("family_id", "—")
        n_style = (n.get("style") or {}).get("family_id", "—")
        if o_style != n_style:
            notes.append(f"style {o_style}→{n_style}")
        lines.append(
            f"| {sid} | `{o.get('top1_group')}`→`{n.get('top1_group')}` "
            f"[{o.get('top1_hit')}→{n.get('top1_hit')}] | "
            f"`{o.get('matched_library')}` | "
            f"{'❌' if n.get('context_zh_leak') else '✅'} | "
            f"`{n_style}` | {o.get('reply_len')}→{n.get('reply_len')} | "
            f"{'; '.join(notes) or '—'} |"
        )

    verdict_g = c["zh_leak"] == b["zh_leak"] and c["top1_hit"] == b["top1_hit"]
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- **Gate G (mechanical)**: {'✅ no regression' if verdict_g else '⚠️ see deltas'}",
            "- **Gate S**: manual G/S 1–5 unchanged in this script; compare `reply_full` in JSON / probe MD",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)
    print("baseline", b)
    print("current ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
