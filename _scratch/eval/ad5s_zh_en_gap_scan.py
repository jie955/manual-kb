#!/usr/bin/env python3
"""One-off scan: AD5S qa_groups zh/en gap inventory for BL-V1-05."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROUPS_PATH = ROOT / "_scratch/run-ad5s/qa_groups.json"

SPEC_PATTERNS = [
    (r"∅\s*\d+[*×x]?\d*mm", "fuse_spec"),
    (r"\d+\s*A\s+250VAC", "fuse_rating"),
    (r"CR\d{4}", "remote_battery"),
    (r"24V\s*12Ah|12V\s*12Ah", "battery_spec"),
    (r"2C\*22\s*AWG|22\s*AWG", "wire_gauge"),
    (r"\d+\s*feet", "range_feet"),
    (r"blinks twice per second", "power_led_blink"),
    (r"backup fuse packed", "backup_fuse_location"),
    (r"11# and 12#", "bat_terminal_ids"),
    (r"dip switch #\d+", "dip_switch"),
    (r"0\.\d+\s*inches?", "rod_length"),
    (r"36VDC", "adapter_output"),
    (r"42\s*VDC|42V", "solar_ocv"),
    (r"30W more solar", "solar_watt_addon"),
    (r"ERM12|M12 remote", "product_model"),
    (r"https?://\S+", "url"),
]

ZH_EQUIV = {
    "fuse_spec": ["∅", "5*20", "5×20", "保险丝规格", "规格对"],
    "fuse_rating": ["10A", "250VAC", "250V"],
    "remote_battery": ["CR2025"],
    "battery_spec": ["12Ah", "24V", "12V"],
    "wire_gauge": ["AWG", "22"],
    "range_feet": ["65", "英尺", "feet"],
    "power_led_blink": ["闪烁", "blink", "两次"],
    "backup_fuse_location": ["备用", "说明书", "manual pack"],
    "bat_terminal_ids": ["11", "12#", "BAT"],
    "dip_switch": ["#5", "红外", "DIP", "跳线"],
    "rod_length": ["0.4", "英寸", "拉杆"],
    "adapter_output": ["36V"],
    "solar_ocv": ["42V", "42"],
    "solar_watt_addon": ["30W", "30瓦"],
    "product_model": ["ERM12", "M12", "外接收器"],
    "url": ["http", "链接", "amazon", "drive.google"],
}


def en_only_specs(en: str, zh: str) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pat, label in SPEC_PATTERNS:
        for m in re.finditer(pat, en, re.I):
            snippet = m.group(0)
            key = f"{label}:{snippet}"
            if key in seen:
                continue
            seen.add(key)
            equiv = ZH_EQUIV.get(label, [])
            if equiv and any(e.lower() in zh.lower() for e in equiv):
                continue
            missing.append((label, snippet))
    return missing


def classify_group(g: dict) -> str:
    en = g.get("answer_en", "") or ""
    zh = g.get("answer_zh", "") or ""
    if "Please help us confirm" in en:
        return "tc148_email"
    en_br = len(re.findall(r"\bIf (?:problem|the|it|so|not)\b", en, re.I))
    zh_if = len(re.findall(r"如果", zh))
    missing = en_only_specs(en, zh)
    has_url_only_en = any(l == "url" for l, _ in missing)
    has_spec = any(l != "url" for l, _ in missing)
    if en_br > zh_if + 2 and zh_if < 3:
        return "structural_branch"
    if has_spec:
        return "detail_spec"
    if has_url_only_en:
        return "detail_link"
    if len(en) > len(zh) * 1.8 and len(zh) > 50:
        return "detail_prose"
    return "aligned"


def main() -> None:
    groups = json.loads(GROUPS_PATH.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for g in groups:
        zh = g.get("answer_zh", "") or ""
        en = g.get("answer_en", "") or ""
        missing = en_only_specs(en, zh)
        kind = classify_group(g)
        if kind == "aligned" and not missing:
            continue
        rows.append(
            {
                "group_id": g["group_id"],
                "question": g["question"],
                "kind": kind,
                "images": g.get("images", []),
                "missing": missing,
                "zh_len": len(zh),
                "en_len": len(en),
            }
        )

    out = ROOT / "_scratch/eval/ad5s_zh_en_gap_inventory.md"
    lines = [
        "# AD5S · zh/en 信息量差异清单",
        "",
        f"**源**：`_scratch/run-ad5s/qa_groups.json` · **组数**：{len(groups)} · **有缺口**：{len(rows)} · **扫描**：BL-V1-05（2026-07-05）",
        "",
        "## 子模式分类",
        "",
        "| 子模式 | 含义 | 组数 |",
        "| --- | --- | ---: |",
    ]
    by_kind: dict[str, int] = {}
    kind_desc = {
        "detail_spec": "骨架对齐，EN 步骤内多规格/型号/数值（AD5S 型）",
        "detail_link": "EN 含 URL，ZH 无对应链",
        "detail_prose": "EN prose 明显更长，混合细节+话术",
        "structural_branch": "EN 条件分支明显多于 ZH",
        "tc148_email": "TC148 型客服邮件稿（AD5S 无）",
        "aligned": "基本对齐",
    }
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    for k in sorted(by_kind.keys()):
        lines.append(f"| **{k}** | {kind_desc.get(k, k)} | {by_kind[k]} |")
    lines.extend(["", "## 逐组清单", ""])
    for r in rows:
        imgs = ", ".join(r["images"]) or "—"
        lines.append(f"### {r['group_id']} · `{r['kind']}`")
        lines.append(f"- **问题**：{r['question']}")
        lines.append(f"- **配图**：{imgs}")
        lines.append(f"- **长度**：zh={r['zh_len']} / en={r['en_len']}")
        if r["missing"]:
            lines.append("- **EN 独有（抽样）**：")
            for label, snippet in r["missing"]:
                lines.append(f"  - `{label}`: {snippet}")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out} ({len(rows)} groups with gaps)")


if __name__ == "__main__":
    main()
