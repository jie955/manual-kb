#!/usr/bin/env python3
"""Compare Round 1e vs patch_off draft dim4 — focus on patched vs control cohorts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, load_json

PATCHED_GEN = {
    "cs_0001",
    "cs_0002",
    "cs_0003",
    "cs_0012",
    "cs_0014",
    "cs_0016",
    "cs_0018",
    "cs_0020",
    "cs_0021",
    "cs_0022",
}
CONTROL_NO_PATCH = {"cs_0013", "cs_0015", "cs_0017", "cs_0019"}
ROUND1E = ROOT / "_scratch/eval_runs/cs_22mail_round1e_2026-07-10.json"
PATCH_OFF = ROOT / "_scratch/eval_runs/cs_22mail_patch_off_2026-07-10.json"
OUT = ROOT / "_scratch/eval_runs/patch_off_compare_2026-07-10.md"


def load_cases(path: Path) -> dict[str, dict]:
    payload = load_json(path)
    scenarios = {s["id"]: s for s in load_json(ROOT / "_scratch/eval/cs_email_query_map.json")["scenarios"]}
    return {r["scenario_id"]: draft_case(r, scenarios[r["scenario_id"]]) for r in payload["results"]}


def cohort_summary(cases: dict[str, dict], ids: set[str], mvp_only: bool = True) -> dict:
    rows = [cases[i] for i in sorted(ids) if i in cases]
    if mvp_only:
        rows = [c for c in rows if c.get("mvp19") == "是"]
    pass_n = sum(1 for c in rows if c["dim4"] == "通过")
    return {"n": len(rows), "pass": pass_n, "rows": rows}


def main() -> int:
    r1 = load_cases(ROUND1E)
    po = load_cases(PATCH_OFF)

    lines = [
        "# patch_off vs Round 1e · ④草稿对比",
        "",
        "**注意**：同用 `draft_22mail_scoring.py` 机械规则，**不可**与人工 xlsx ④混比；",
        "patch_off 与 round1e 可比（同一把草稿尺），但与 holdout 横比仍须谨慎。",
        "",
        f"- Round 1e：`{ROUND1E.name}`",
        f"- patch_off（`--no-eval-pack`）：`{PATCH_OFF.name}`",
        "",
    ]

    mvp_r1 = [c for c in r1.values() if c.get("mvp19") == "是"]
    mvp_po = [c for c in po.values() if c.get("mvp19") == "是"]
    lines.append("## MVP19 汇总")
    lines.append("")
    lines.append(f"| 批次 | ④草稿通过 |")
    lines.append(f"| --- | --- |")
    lines.append(f"| Round 1e | **{sum(1 for c in mvp_r1 if c['dim4']=='通过')}/{len(mvp_r1)}** |")
    lines.append(f"| patch_off | **{sum(1 for c in mvp_po if c['dim4']=='通过')}/{len(mvp_po)}** |")
    lines.append("")

    for label, cohort in [
        ("10 个 generation/pinned 补丁 case", PATCHED_GEN),
        ("无补丁对照组", CONTROL_NO_PATCH),
    ]:
        s1 = cohort_summary(r1, cohort)
        s2 = cohort_summary(po, cohort)
        lines.extend(
            [
                f"## {label}",
                "",
                f"| 批次 | ④通过 |",
                f"| --- | --- |",
                f"| Round 1e | **{s1['pass']}/{s1['n']}** |",
                f"| patch_off | **{s2['pass']}/{s2['n']}** |",
                "",
                "| cs_id | Round1e ④ | patch_off ④ | Round1e ② | patch_off ② | Δ |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for sid in sorted(cohort):
            if sid not in r1 or sid not in po:
                continue
            c1, c2 = r1[sid], po[sid]
            delta = "—" if c1["dim4"] == c2["dim4"] else f"{c1['dim4']}→{c2['dim4']}"
            lines.append(
                f"| {sid} | {c1['dim4']} | {c2['dim4']} | {c1['dim2']} | {c2['dim2']} | {delta} |"
            )
        lines.append("")

    # Full delta table MVP19
    lines.extend(["## MVP19 全表 Δ", "", "| cs_id | R1e ④ | patch ④ | R1e ② | patch ② |", "| --- | --- | --- | --- | --- |"])
    for sid in sorted(r1.keys()):
        if r1[sid].get("mvp19") != "是":
            continue
        c1, c2 = r1[sid], po.get(sid, {})
        if not c2:
            continue
        lines.append(
            f"| {sid} | {c1['dim4']} | {c2['dim4']} | {c1['dim2']} | {c2['dim2']} |"
        )
    lines.append("")

    dropped = [
        sid
        for sid in PATCHED_GEN
        if sid in r1 and sid in po
        and r1[sid]["dim4"] == "通过"
        and po[sid]["dim4"] != "通过"
        and r1[sid].get("mvp19") == "是"
    ]
    control_moved = [
        sid
        for sid in CONTROL_NO_PATCH
        if sid in r1 and sid in po and r1[sid]["dim4"] != po[sid]["dim4"]
    ]

    lines.extend(
        [
            "## 解读要点",
            "",
            f"- **补丁 case 从通过→不通过**：{', '.join(dropped) or '（无）'}",
            f"- **对照组 ④变化**：{', '.join(f'{s}({r1[s]["dim4"]}→{po[s]["dim4"]})' for s in control_moved) or '（无 — 开关无副作用信号）'}",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.name}")
    print(f"MVP19: R1e {sum(1 for c in mvp_r1 if c['dim4']=='通过')}/{len(mvp_r1)} → patch_off {sum(1 for c in mvp_po if c['dim4']=='通过')}/{len(mvp_po)}")
    print(f"Patched cohort: {s1['pass'] if False else cohort_summary(r1, PATCHED_GEN)['pass']}/{cohort_summary(r1, PATCHED_GEN)['n']} → {cohort_summary(po, PATCHED_GEN)['pass']}/{cohort_summary(po, PATCHED_GEN)['n']}")
    s1c = cohort_summary(r1, CONTROL_NO_PATCH)
    s2c = cohort_summary(po, CONTROL_NO_PATCH)
    print(f"Control cohort: {s1c['pass']}/{s1c['n']} → {s2c['pass']}/{s2c['n']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
