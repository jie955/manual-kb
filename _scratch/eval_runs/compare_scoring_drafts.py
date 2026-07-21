#!/usr/bin/env python3
"""Compare scoring drafts: Round0 vs Round1 vs post-refactor."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "_scratch" / "eval"
RUNS = ROOT / "_scratch" / "eval_runs"

DRAFTS = {
    "round0": EVAL / "scoring_draft_round0.json",
    "round1": EVAL / "scoring_draft_round1.json",
    "post_refactor": EVAL / "scoring_draft_cs_22mail_post_refactor_2026-07-10.json",
}
OUT = RUNS / "scoring_draft_compare_2026-07-10.md"


def load_cases(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {c["scenario_id"]: c for c in data["cases"]}


def summarize(cases: list[dict]) -> dict:
    mvp = [c for c in cases if c.get("mvp19") == "是"]
    return {
        "mvp19": len(mvp),
        "d4_pass": sum(1 for c in mvp if c["dim4"] == "通过"),
        "d4_pending": sum(1 for c in mvp if c["dim4"] == "待人工"),
        "d2_direct": sum(1 for c in mvp if c["dim2"] == "直接可发"),
        "d2_minor": sum(1 for c in mvp if c["dim2"] == "小改可发"),
        "d2_rewrite": sum(1 for c in mvp if c["dim2"] == "需重写"),
        "d1_wrong": sum(1 for c in mvp if c["dim1"] == "错"),
    }


def main() -> int:
    loaded: dict[str, dict[str, dict]] = {}
    stats: dict[str, dict] = {}
    for name, path in DRAFTS.items():
        if not path.is_file():
            print(f"WARN missing {path}")
            continue
        loaded[name] = load_cases(path)
        stats[name] = summarize(list(loaded[name].values()))

    lines = [
        "# 22-Mail · Scoring Draft Compare",
        "",
        "**性质**：四维 **草稿** 对比 · 须人工确认 · **不可**作发链依据",
        "",
        "## MVP19 草稿汇总（④严格通过 · 目标 ≥16/19）",
        "",
        "| 轮次 | ④通过 | 待人工 | ②直接可发 | ②小改可发 | ②需重写 | ①错 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    labels = {
        "round0": "Round0 基线 (2026-07-08)",
        "round1": "Round1 复测 (2026-07-08)",
        "post_refactor": "Post-refactor (2026-07-10)",
    }
    for key in ("round0", "round1", "post_refactor"):
        if key not in stats:
            continue
        s = stats[key]
        lines.append(
            f"| {labels[key]} | {s['d4_pass']}/19 | {s['d4_pending']} | "
            f"{s['d2_direct']} | {s['d2_minor']} | {s['d2_rewrite']} | {s['d1_wrong']} |"
        )

    if "round0" in loaded and "post_refactor" in loaded:
        lines.extend(["", "## ④草稿变化（Round0 → Post-refactor）", ""])
        improved = []
        regressed = []
        for sid, cur in loaded["post_refactor"].items():
            if cur.get("mvp19") != "是":
                continue
            old = loaded["round0"].get(sid, {})
            if not old:
                continue
            if old.get("dim4") != "通过" and cur.get("dim4") == "通过":
                improved.append(sid)
            elif old.get("dim4") == "通过" and cur.get("dim4") != "通过":
                regressed.append(sid)
        lines.append(f"- **新增④通过**：{len(improved)} 封" + (f" — {', '.join(improved)}" if improved else ""))
        lines.append(f"- **④退步**：{len(regressed)} 封" + (f" — {', '.join(regressed)}" if regressed else ""))

        lines.extend(["", "## ②草稿变化（MVP19）", ""])
        lines.append("| cs_id | Round0 ② | Post-refactor ② | ④ |")
        lines.append("| --- | --- | --- | --- |")
        for sid in sorted(loaded["post_refactor"].keys()):
            cur = loaded["post_refactor"][sid]
            if cur.get("mvp19") != "是":
                continue
            old = loaded["round0"].get(sid, {})
            o2 = old.get("dim2", "—")
            n2 = cur.get("dim2", "—")
            d4 = cur.get("dim4", "—")
            mark = " **" if o2 != n2 else ""
            n2_cell = f"**{n2}**" if o2 != n2 else n2
            lines.append(f"| {sid} | {o2} | {n2_cell} | {d4} |")

    lines.extend(
        [
            "",
            "## 留档",
            "",
            f"- 草稿 MD：[`scoring_draft_cs_22mail_post_refactor_2026-07-10.md`](../../_scratch/eval/scoring_draft_cs_22mail_post_refactor_2026-07-10.md)",
            f"- 机械对比：[`cs_22mail_compare_2026-07-10.md`](./cs_22mail_compare_2026-07-10.md)",
            "",
            "## 人工下一步",
            "",
            "1. 对照 `generated_reply_en` 确认/修正 E–H（xlsx「复测评分」或新 sheet）",
            "2. 仅统计 MVP19（计入MVP19=是）→ **≥16/19** ④通过",
            "3. `cs_0008` truncated 须单独审 ②（TC148 不计入 MVP19）",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    for k, s in stats.items():
        print(k, s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
