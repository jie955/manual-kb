#!/usr/bin/env python3
"""One-off P1 + safety reverse audit for Round 1 scoring."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draft_22mail_scoring import (  # noqa: E402
    MAP_PATH,
    ROOT,
    draft_dim1,
    draft_dim2,
    extract_reference_reply,
    load_json,
    ref_key_hits,
)

SAFETY_KEYS = {
    "DIP#3",
    "DIP#5",
    "4#/5#",
    "instant_short",
    "limit_short",
    "limit_B",
    "FORCE",
    "SOFT_STOP",
    "11#/12#",
}


def safety_in_text(t: str) -> set[str]:
    low = t.lower()
    flags: set[str] = set()
    if re.search(r"power\s+off|disconnect.*power|power\s+down", low):
        flags.add("power_off")
    if re.search(r"\bshort\b|jumper", low):
        flags.add("short/jumper")
    if re.search(r"dip\s*switch", low):
        flags.add("DIP")
    if re.search(r"limit\s+switch", low):
        flags.add("limit_switch")
    if re.search(r"force\s+potentiometer|stall\s+force", low):
        flags.add("FORCE")
    if re.search(r"11#|12#", low):
        flags.add("11#/12#")
    return flags


def main() -> None:
    map_data = load_json(MAP_PATH)
    scenarios = {s["id"]: s for s in map_data["scenarios"]}
    batch = load_json(Path(__file__).parent / "cs_22mail_eval_round1.json")
    rows = {r["scenario_id"]: r for r in batch["results"]}

    print("=== P1: dim1 analysis ===")
    for sid in ["cs_0001", "cs_0020", "cs_0022"]:
        row = rows[sid]
        scen = scenarios[sid]
        ref = extract_reference_reply((ROOT / scen["file"]).read_text(encoding="utf-8"))
        d1, n1 = draft_dim1(row, scen)
        d2, n2 = draft_dim2(row, scen, ref)
        rk_ref = ref_key_hits(ref)
        rk_rep = ref_key_hits(row["generated_reply_en"])
        print(
            f"{sid} mail#{scen['mail_num']} expected={scen.get('expected_group_ids')} "
            f"top1={row['top1_group']} routing={row.get('routing_method')}"
        )
        print(f"  dim1: {d1} — {n1}")
        print(f"  dim2: {d2} — {n2}")
        print(f"  ref_keys missing: {sorted(rk_ref - rk_rep)}")
        print(f"  reply safety: {sorted(safety_in_text(row['generated_reply_en']))}")
        print(f"  ref safety: {sorted(safety_in_text(ref))}")
        print()

    print("=== SAFETY AUDIT: MVP19 draft 直接可发 (fault only) ===")
    cases = load_json(Path(__file__).parent / "scoring_draft_round1.json")["cases"]
    for c in cases:
        if c["mvp19"] != "是" or c["dim2"] != "直接可发":
            continue
        sid = c["scenario_id"]
        scen = scenarios[sid]
        if scen.get("type") == "presales":
            continue
        row = rows[sid]
        ref = extract_reference_reply((ROOT / scen["file"]).read_text(encoding="utf-8"))
        rk_ref = ref_key_hits(ref)
        rk_rep = ref_key_hits(row["generated_reply_en"])
        miss = sorted(rk_ref - rk_rep)
        miss_safety = [m for m in miss if m in SAFETY_KEYS]
        ref_only = sorted(safety_in_text(ref) - safety_in_text(row["generated_reply_en"]))
        flag = bool(miss_safety or ref_only)
        print(
            f"#{scen['mail_num']:02d} {sid} top1={c['top1']} note={c['dim2_note']} "
            f"{'>>> REVIEW' if flag else '>>> OK'}"
        )
        print(f"  ref_keys miss: {miss} | safety miss: {miss_safety}")
        if ref_only:
            print(f"  prose safety ref-only: {ref_only}")
        print()


if __name__ == "__main__":
    main()
