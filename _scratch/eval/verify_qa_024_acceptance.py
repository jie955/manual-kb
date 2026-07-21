#!/usr/bin/env python3
"""qa_024 四项验收（extract + 展示逻辑，不依赖浏览器）。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from branch_utils import (
    branch_matches,
    collect_ladder_branch_images,
    filter_branches,
)


def format_branch_tag(br: dict) -> str:
    install = {"pull_open": "拉开门", "push_open": "推开门"}
    symptom = {"open_abnormal": "开门不正常", "close_abnormal": "关门不正常"}
    region = {"US": "美国", "UK": "英国"}

    def fmt(aw: dict) -> str:
        parts = []
        if aw.get("install_mode"):
            parts.append(install[aw["install_mode"]])
        if aw.get("stall_symptom"):
            parts.append(symptom[aw["stall_symptom"]])
        if aw.get("region"):
            parts.append(region[aw["region"]])
        return " · ".join(parts)

    any_list = br.get("applies_when_any") or []
    reg = (br.get("applies_when") or {}).get("region")
    if len(any_list) >= 2:
        paths = [fmt(p) for p in any_list]
        region_part = region.get(reg, reg) if reg else ""
        return " ⇄ ".join(paths) + (f" · {region_part}" if region_part else "")
    return fmt(br.get("applies_when") or {})


def load_qa_024_ladder() -> list:
    import os

    rel = os.environ.get("AD5S_QA_GROUPS", "_scratch/run-ad5s-dry-ladder/qa_groups.json")
    path = ROOT / rel
    groups = json.loads(path.read_text(encoding="utf-8"))
    g = next(x for x in groups if x["group_id"] == "qa_024")
    return g["troubleshooting_ladder"]


def step3_branches(ladder: list) -> list:
    return ladder[2]["branches"]


def main() -> int:
    ladder = load_qa_024_ladder()
    branches = step3_branches(ladder)
    ok = True

    # 1. ctx={} → 2 张
    m0 = filter_branches(branches, {})
    print(f"[1] ctx={{}} → {len(m0)} branch cards (expect 2)")
    if len(m0) != 2:
        ok = False

    # 2. region=US → 1 张
    mus = filter_branches(branches, {"region": "US"})
    print(f"[2] region=US → {len(mus)} branch cards (expect 1)")
    if len(mus) != 1:
        ok = False
    elif len({b["content_zh"] for b in mus}) != 1:
        print("    FAIL: duplicate content_zh")
        ok = False

    # 3. 截图场景 push_open + close_abnormal + US
    ctx3 = {
        "install_mode": "push_open",
        "stall_symptom": "close_abnormal",
        "region": "US",
    }
    m3 = filter_branches(branches, ctx3)
    print(f"[3] push_open+close_abnormal+US → {len(m3)} card(s) (expect 1)")
    if len(m3) != 1:
        ok = False
    else:
        br = m3[0]
        tag = format_branch_tag(br)
        print(f"    tag: {tag}")
        print(f"    content_zh head: {br['content_zh'][:40]}…")
        print(f"    content_en has +Motor: {'+Motor' in br['content_en']}")
        if "推开门" not in tag or "关门不正常" not in tag:
            print("    FAIL: tag missing push_open/close_abnormal labels")
            ok = False
        if "⇄" not in tag:
            print("    FAIL: tag should show bidirectional ⇄")
            ok = False
        if "+Motor" not in br["content_en"]:
            ok = False
        if "推开门关门不正常" not in br["content_zh"]:
            print("    FAIL: content_zh should mention mirror 推开门关门不正常")
            ok = False

    # 4. region=US 配图不含 027
    imgs = collect_ladder_branch_images(ladder, {"region": "US"})
    print(f"[4] region=US images: {imgs}")
    if "image_027.png" in imgs:
        print("    FAIL: image_027 should not appear for US")
        ok = False
    if "image_026.png" not in imgs:
        print("    FAIL: image_026 expected for US")
        ok = False

    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
