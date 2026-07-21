#!/usr/bin/env python3
"""qa_023 四项验收（parallel branch + 采购链 + 协商剥离，不依赖浏览器）。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from branch_utils import collect_ladder_branch_images, filter_branches
from link_utils import find_urls


def load_qa_023() -> dict:
    rel = os.environ.get("AD5S_QA_GROUPS", "_scratch/run-ad5s/qa_groups.json")
    path = ROOT / rel
    groups = json.loads(path.read_text(encoding="utf-8"))
    return next(x for x in groups if x["group_id"] == "qa_023")


def main() -> int:
    g = load_qa_023()
    ladder = g.get("troubleshooting_ladder") or []
    ok = True

    if len(ladder) != 3:
        print(f"[0] ladder steps={len(ladder)} (expect 3)")
        ok = False

    branches = ladder[0]["branches"] if ladder else []
    m0 = filter_branches(branches, {})
    print(f"[1] ctx={{}} → {len(m0)} branch cards (expect 2)")
    if len(m0) != 2:
        ok = False

    ctx = {"parallel_test": "arm2_on_arm1"}
    m1 = filter_branches(branches, ctx)
    imgs = collect_ladder_branch_images(ladder, ctx)
    print(f"[2] parallel_test=arm2_on_arm1 → {len(m1)} card, images={imgs}")
    if len(m1) != 1:
        ok = False
    if imgs != ["image_024.png"]:
        print("    FAIL: expected image_024.png only")
        ok = False

    step2_links = ladder[1].get("links") or [] if len(ladder) > 1 else []
    purchase = [lk for lk in step2_links if lk.get("link_type") == "purchase_link"]
    print(f"[3] step2 purchase_link count={len(purchase)} (expect 1)")
    if len(purchase) != 1:
        ok = False
    elif not purchase[0].get("disclaimer"):
        print("    FAIL: missing disclaimer on purchase_link")
        ok = False

    offers = g.get("negotiation_offers") or []
    en = g.get("answer_en") or ""
    root_links = g.get("links") or []
    print(f"[4] negotiation_offers={len(offers)}, bare URLs in answer_en={find_urls(en)}")
    if not offers or not any("M12" in o.get("text", "") for o in offers):
        ok = False
    if "M12 remotes" in en or find_urls(en):
        print("    FAIL: negotiation or bare URL still in answer_en")
        ok = False
    if root_links:
        print(f"    FAIL: root links should be empty, got {len(root_links)}")
        ok = False

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
