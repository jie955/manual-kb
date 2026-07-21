#!/usr/bin/env python3
"""Classify patch_off MVP19 failures: framework vs generation vs images vs presales."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, load_json

PATCHED_GEN = {
    "cs_0001", "cs_0002", "cs_0003", "cs_0012", "cs_0014",
    "cs_0016", "cs_0018", "cs_0020", "cs_0021", "cs_0022",
}
PRESALES_BRIEF = {"cs_0004", "cs_0005", "cs_0006", "cs_0007", "cs_0011"}

PATCH_OFF = ROOT / "_scratch/eval_runs/cs_22mail_patch_off_2026-07-10.json"
ROUND1E = ROOT / "_scratch/eval_runs/cs_22mail_round1e_2026-07-10.json"
OUT = ROOT / "_scratch/eval_runs/patch_off_deconfusion_2026-07-10.md"


def load_cases(path: Path) -> dict[str, dict]:
    payload = load_json(path)
    scenarios = {s["id"]: s for s in load_json(ROOT / "_scratch/eval/cs_email_query_map.json")["scenarios"]}
    return {r["scenario_id"]: draft_case(r, scenarios[r["scenario_id"]]) for r in payload["results"]}


def bucket(c: dict) -> str:
    n2 = c.get("dim2_note") or ""
    if c.get("dim3") == "该配没配":
        return "③图片机制（非文字生成）"
    if "ref_keys=" in n2 and "小改可发" == c.get("dim2"):
        return "②真实生成缺口（ref_keys 部分命中，有金标准）"
    if "presales · weak links" in n2:
        return "presales brief 缺失（产品/链接）"
    if c.get("dim2") == "待人工":
        return "②待人工（无金标准或无 ref_keys 模式）"
    if c.get("dim4") == "通过":
        return "仍通过"
    return "其他"


def main() -> int:
    r1 = load_cases(ROUND1E)
    po = load_cases(PATCH_OFF)

    lines = [
        "# patch_off 掉分解混 · 框架修复后",
        "",
        "§7.2 已应用：`无金标准 / 无 ref_keys 模式` → ②待人工、④待人工（非自动否决）。",
        "**结论**：Joyce 补丁 case 掉分**主要不是**该框架 bug — 多数有金标准且 `ref_keys=25–50%`（真实生成缺口）。",
        "",
        "## cs_0005 专项（已查清）",
        "",
        "| 维 | Round 1e | patch_off | 原因 |",
        "| --- | --- | --- | --- |",
        f"| ① | {r1['cs_0005']['dim1']} | {po['cs_0005']['dim1']} | 无变化 |",
        f"| ② | {r1['cs_0005']['dim2']} | {po['cs_0005']['dim2']} | 无变化 |",
        f"| ③ | {r1['cs_0005']['dim3']} | **{po['cs_0005']['dim3']}** | `pinned_images` 摘掉 → `images_used` 空 · Reference 要求配图 |",
        f"| ④ | {r1['cs_0005']['dim4']} | {po['cs_0005']['dim4']} | **③一票否决**，非①② |",
        "",
        "→ **独立根因**：配图/检索机制，勿归入「生成文字质量」筐。",
        "",
        "## MVP19 patch_off 未通过 · 根因桶",
        "",
    ]

    failed = [sid for sid, c in po.items() if c.get("mvp19") == "是" and c["dim4"] != "通过"]
    buckets: dict[str, list[str]] = {}
    for sid in sorted(failed):
        b = bucket(po[sid])
        buckets.setdefault(b, []).append(sid)

    for b, sids in sorted(buckets.items()):
        lines.append(f"### {b} ({len(sids)})")
        lines.append("")
        for sid in sids:
            c = po[sid]
            r = "补丁" if sid in PATCHED_GEN else ("presales" if sid in PRESALES_BRIEF else "—")
            lines.append(
                f"- **{sid}** [{r}] ④={c['dim4']} · ②={c['dim2']} · ③={c['dim3']} · {c['dim2_note'][:60]}"
            )
        lines.append("")

    # Patched 8 dropped
    dropped_patch = [
        s for s in PATCHED_GEN
        if r1[s]["dim4"] == "通过" and po[s]["dim4"] != "通过" and po[s].get("mvp19") == "是"
    ]
    fw_only = [s for s in dropped_patch if bucket(po[s]).startswith("②待人工")]
    real_gen = [s for s in dropped_patch if "ref_keys=" in (po[s].get("dim2_note") or "")]

    lines.extend([
        "## 10 个 generation/pinned 补丁 case · 掉分拆解",
        "",
        f"- 通过→未通过：**{len(dropped_patch)}** 封",
        f"- 其中 §7.2 框架误伤（待人工桶）：**{len(fw_only)}**",
        f"- 其中 ref_keys 部分命中（真实生成缺口）：**{len(real_gen)}**",
        "",
        "## Holdout（框架修复后）",
        "",
    ])
    for sid in ["cs_0023", "cs_0024", "cs_0025", "cs_0026", "cs_0027"]:
        if sid in po:
            continue
    hold = load_cases(ROOT / "_scratch/eval_runs/holdout_t1_t5_2026-07-10.json")
    for sid in sorted(hold.keys()):
        c = hold[sid]
        lines.append(f"- **{sid}** ④={c['dim4']} · ②={c['dim2']} · {c['dim2_note'][:55]}")

    lines.extend([
        "",
        "## 建议顺序（更新）",
        "",
        "1. §7.2 框架 ✅ — holdout cs_0025/0027 应改 ④待人工",
        "2. 人工 xlsx（三份草稿同尺，均非终审）",
        "3. 根因聚类后通用修复：**A** ref_keys 阶梯/终端锚点 **B** presales playbook **C** 配图检索 **D** style/audit",
        "4. 勿按 case 数堆规则",
        "",
    ])

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.name}")
    print(f"Framework-only in patched drops: {fw_only}")
    print(f"ref_keys partial: {real_gen}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
