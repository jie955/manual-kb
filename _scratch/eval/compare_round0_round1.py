#!/usr/bin/env python3
"""Compare Round 0 vs Round 1 batch eval metrics."""
from __future__ import annotations

import json
from pathlib import Path

EVAL = Path(__file__).resolve().parent


def scan(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for r in data["results"]:
        a = r.get("reply_audit") or {}
        rows.append(
            {
                "id": r["scenario_id"],
                "top1": r.get("top1_group"),
                "trunc": r.get("reply_truncated"),
                "inc": r.get("reply_incomplete_reason"),
                "proceed": a.get("proceed_ref"),
                "check": a.get("check_step_ref"),
                "glued": a.get("glued_steps"),
                "steps": a.get("step_count"),
                "style": (r.get("style") or {}).get("family_id"),
            }
        )
    return rows


def count(rows: list[dict], key: str) -> int:
    return sum(1 for x in rows if x[key])


def main() -> None:
    r0 = scan(EVAL / "cs_22mail_eval_round0.json")
    r1 = scan(EVAL / "cs_22mail_eval_round1.json")

    print("=== Round0 vs Round1 ===")
    for label, key in [
        ("truncated", "trunc"),
        ("proceed_ref", "proceed"),
        ("check_step_ref", "check"),
        ("glued_steps", "glued"),
    ]:
        print(f"{label}: {count(r0, key)}/22 -> {count(r1, key)}/22")

    inc0 = sum(1 for x in r0 if x["inc"])
    inc1 = sum(1 for x in r1 if x["inc"])
    print(f"incomplete_reason: {inc0}/22 -> {inc1}/22")

    print("\n=== Top1 changes (round0->round1) ===")
    by0 = {x["id"]: x for x in r0}
    for x in r1:
        o = by0[x["id"]]
        if o["top1"] != x["top1"]:
            print(f"{x['id']}: {o['top1']} -> {x['top1']}")

    print("\n=== Style family changes ===")
    for x in r1:
        o = by0[x["id"]]
        if o["style"] != x["style"]:
            print(f"{x['id']}: {o['style']} -> {x['style']}")

    print("\n=== Remaining format flags in round1 ===")
    any_bad = False
    for x in r1:
        flags = [k for k in ("proceed", "check", "glued") if x[k]]
        if flags or x["trunc"] or x["inc"]:
            any_bad = True
            print(x["id"], flags, f"trunc={x['trunc']}", x["inc"] or "")
    if not any_bad:
        print("(none)")


if __name__ == "__main__":
    main()
