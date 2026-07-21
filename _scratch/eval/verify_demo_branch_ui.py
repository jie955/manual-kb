#!/usr/bin/env python3
"""Demo branch UI gate: qa_023 parallel_test labels + qa_024 install/stall filters (blocking U6)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from branch_utils import filter_branches

DEMO = ROOT / "demo/index.html"
QA_GROUPS = ROOT / "_scratch/run-ad5s/qa_groups.json"

PARALLEL_LABELS = {
    "arm2_on_arm1": "机臂2并到机臂1",
    "arm1_on_arm2": "机臂1并到机臂2",
}


def format_applies_when(aw: dict) -> str:
    parts = []
    if aw.get("parallel_test"):
        parts.append(PARALLEL_LABELS.get(aw["parallel_test"], aw["parallel_test"]))
    return " · ".join(parts)


def ladder_uses_parallel_test(ladder: list) -> bool:
    return any(
        br.get("applies_when", {}).get("parallel_test")
        for step in ladder
        for br in step.get("branches") or []
    )


def ladder_has_install_stall(ladder: list) -> bool:
    for step in ladder:
        for br in step.get("branches") or []:
            aw = br.get("applies_when") or {}
            if aw.get("region") or br.get("applies_when_any"):
                return True
    return False


def main() -> int:
    html = DEMO.read_text(encoding="utf-8")
    ok = True
    for needle in (
        "PARALLEL_LABELS",
        "ladderUsesParallelTest",
        "filterInstallStallRegion",
        "机臂2并到机臂1",
    ):
        if needle not in html:
            print(f"FAIL demo missing: {needle}")
            ok = False

    groups = json.loads(QA_GROUPS.read_text(encoding="utf-8"))
    qa023 = next(g for g in groups if g["group_id"] == "qa_023")
    qa024 = next(g for g in groups if g["group_id"] == "qa_024")
    l23 = qa023.get("troubleshooting_ladder") or []
    l24 = qa024.get("troubleshooting_ladder") or []

    if not ladder_uses_parallel_test(l23):
        print("FAIL qa_023: no parallel_test branches")
        ok = False
    else:
        branches = l23[0]["branches"]
        tags = [format_applies_when(b["applies_when"]) for b in branches]
        print(f"[U1-U3] qa_023 parallel tags: {tags}")
        if tags != ["机臂2并到机臂1", "机臂1并到机臂2"]:
            print("FAIL qa_023 branch tag text")
            ok = False
        if len(filter_branches(branches, {})) != 2:
            print("FAIL qa_023 ctx={{}} should show 2 branches")
            ok = False

    if not ladder_has_install_stall(l24):
        print("FAIL qa_024: no install/stall/region branches (U6)")
        ok = False
    else:
        print("[U6] qa_024 has install/stall/region ladder — demo must show 3 dropdowns")

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
