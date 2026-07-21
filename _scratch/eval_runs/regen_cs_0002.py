#!/usr/bin/env python3
"""Regenerate cs_0002 row for round1b comparison."""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
sc = scenarios["cs_0002"]
api_key = _get_config()[0]

row = run_case_with_images(sc, libs, generate=True, api_key=api_key, domain_id="topens")
row["mail_id"] = "MAIL-02"
row["mvp19"] = "是"
d = draft_case(row, sc)

out = ROOT / "_scratch/eval_runs/cs_0002_stable_2026-07-10.json"
payload = {
    "meta": {
        "scenario_id": "cs_0002",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "fix": "Reference 0 order + mandatory 6-step brief",
    },
    "row": row,
    "draft": d,
}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(d, ensure_ascii=False, indent=2))
print(f"wrote {out}")
