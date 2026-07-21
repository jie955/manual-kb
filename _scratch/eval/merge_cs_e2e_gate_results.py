#!/usr/bin/env python3
"""Merge partial run_cs_e2e_gate results into full 9-case baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runners.gate_report import get_gate_scenario_ids, write_probe_markdown  # noqa: E402

GATE_SCENARIO_IDS = get_gate_scenario_ids("topens")

EVAL = Path(__file__).resolve().parent


def main() -> int:
    base_path = EVAL / "cs_e2e_gate_results.json"
    patch_paths = [Path(p) for p in sys.argv[1:]] if len(sys.argv) > 1 else []
    if not patch_paths:
        print("Usage: merge_cs_e2e_gate_results.py <base.json> [patch.json ...]", file=sys.stderr)
        return 1

    base = json.loads(patch_paths[0].read_text(encoding="utf-8"))
    by_id = {r["scenario_id"]: r for r in base.get("results") or []}
    for patch_path in patch_paths[1:]:
        patch = json.loads(patch_path.read_text(encoding="utf-8"))
        for row in patch.get("results") or []:
            by_id[row["scenario_id"]] = row

    merged = {**base, "results": [by_id[sid] for sid in GATE_SCENARIO_IDS if sid in by_id]}
    out = EVAL / "cs_e2e_gate_results.json"
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    write_probe_markdown(merged, EVAL / "phase0_gate_probe.md")

    ok = sum(1 for r in merged["results"] if r.get("reply_full"))
    print(f"Merged → {out} · generated {ok}/9")
    for r in merged["results"]:
        sid = r["scenario_id"]
        rl = r.get("reply_len") or 0
        flag = (
            "OK"
            if r.get("top1_hit")
            else ("n/a" if not r.get("expected_groups") else "MISS")
        )
        gen = "GEN" if rl else "FAIL"
        print(f"  {sid} top1={r.get('top1_group')} [{flag}] {gen} len={rl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
