#!/usr/bin/env python3
"""Holdout eval: Gate T1–T5 (cs_0023–cs_0027) — NOT in Joyce 22 / NOT in Round 1b–1e EvalPack patches."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, render_md
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

HOLDOUT_IDS = ["cs_0023", "cs_0024", "cs_0025", "cs_0026", "cs_0027"]
OUT_JSON = ROOT / "_scratch/eval_runs/holdout_t1_t5_2026-07-10.json"
OUT_MD = ROOT / "_scratch/eval/scoring_draft_holdout_t1_t5_2026-07-10.md"


def main() -> int:
    api_key = _get_config()[0]
    if not api_key:
        print("ERROR: QA_API_KEY required", file=sys.stderr)
        return 1

    scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
    libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")

    results = []
    for sid in HOLDOUT_IDS:
        sc = scenarios[sid]
        row = run_case_with_images(
            sc, libs, generate=True, api_key=api_key, domain_id="topens"
        )
        row["mail_id"] = sc.get("test_id") or sid
        row["mvp19"] = "否" if row["is_tc148"] else "是"
        results.append(row)
        print(f"{sid} ({sc.get('test_id')}) · top1={row['top1_group']} · lib={row['matched_library']}")

    payload = {
        "meta": {
            "holdout": "gate_t1_t5",
            "scenario_ids": HOLDOUT_IDS,
            "note": "No EvalPack per-case patches in Round 1b–1e",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    cases = [draft_case(r, scenarios[r["scenario_id"]]) for r in results]
    pass_all = sum(1 for c in cases if c["dim4"] == "通过")
    pass_mvp = sum(1 for c in cases if c.get("mvp19") == "是" and c["dim4"] == "通过")
    mvp_n = sum(1 for c in cases if c.get("mvp19") == "是")

    meta = {
        "source_json": OUT_JSON.name,
        "generated_at": payload["meta"]["generated_at"],
        "round": "holdout_t1_t5",
    }
    OUT_MD.write_text(
        render_md(cases, meta, title="Holdout T1–T5 · 四维评分草稿"),
        encoding="utf-8",
    )

    print(f"\nWrote {OUT_JSON.name}")
    print(f"Wrote {OUT_MD.name}")
    print(f"Holdout dim4 pass: {pass_all}/{len(cases)} (MVP-like {pass_mvp}/{mvp_n})")
    for c in cases:
        print(f"  {c['scenario_id']}: dim4={c['dim4']} dim2={c['dim2']} · {c['dim2_note'][:50]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
