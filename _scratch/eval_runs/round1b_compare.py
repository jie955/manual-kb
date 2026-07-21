#!/usr/bin/env python3
"""Compare Round1b vs post-refactor scoring drafts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "_scratch" / "eval"
RUNS = ROOT / "_scratch" / "eval_runs"
OUT = RUNS / "round1b_compare_2026-07-10.md"


def load_cases(path: Path) -> dict[str, dict]:
    return {c["scenario_id"]: c for c in json.loads(path.read_text(encoding="utf-8"))["cases"]}


def mvp_pass(cases: dict[str, dict]) -> list[str]:
    return sorted(
        sid
        for sid, c in cases.items()
        if c.get("mvp19") == "是" and c.get("dim4") == "通过"
    )


def main() -> int:
    before = load_cases(EVAL / "scoring_draft_cs_22mail_post_refactor_2026-07-10.json")
    after = load_cases(EVAL / "scoring_draft_cs_22mail_round1b_2026-07-10.json")
    b_pass = mvp_pass(before)
    a_pass = mvp_pass(after)
    gained = sorted(set(a_pass) - set(b_pass))
    lost = sorted(set(b_pass) - set(a_pass))

    lines = [
        "# Round 1b · Targeted Fix Compare",
        "",
        f"**Before**: post-refactor draft · **{len(b_pass)}/19** MVP19 ④通过",
        f"**After**: round1b draft · **{len(a_pass)}/19** MVP19 ④通过（目标 ≥16）",
        "",
        "## ④新增通过",
        "",
        ", ".join(gained) if gained else "(none)",
        "",
        "## ④退步",
        "",
        ", ".join(lost) if lost else "(none)",
        "",
        "## Target cases",
        "",
        "| cs_id | before ④ | after ④ | after top1 |",
        "| --- | --- | --- | --- |",
    ]
    for sid in ["cs_0002", "cs_0011", "cs_0012", "cs_0019", "cs_0006"]:
        b = before.get(sid, {})
        a = after.get(sid, {})
        lines.append(
            f"| {sid} | {b.get('dim4','—')} | {a.get('dim4','—')} | {a.get('top1','—')} |"
        )
    lines.extend(
        [
            "",
            "## 留档",
            "",
            "- JSON: `_scratch/eval_runs/cs_22mail_round1b_2026-07-10.json`",
            "- 草稿: `_scratch/eval/scoring_draft_cs_22mail_round1b_2026-07-10.md`",
            "",
        ]
    )
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print("gained", gained)
    print("lost", lost)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
