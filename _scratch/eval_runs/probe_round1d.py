#!/usr/bin/env python3
"""Round 1d stability probe for targeted cases."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from _scratch.eval.draft_22mail_scoring import draft_case, ref_key_hits, extract_reference_reply
from evals.runners.cs_22mail_batch_runner import run_case_with_images, load_scenarios
from generate_answer import _get_config
from library_router import load_unified_libraries

TARGETS = ["cs_0016", "cs_0005", "cs_0001", "cs_0014", "cs_0020", "cs_0022"]
RUNS = 2

libs = load_unified_libraries("_scratch/modelscope/BAAI/bge-m3", index="en")
scenarios = load_scenarios(ROOT / "_scratch/eval/cs_email_query_map.json")
api_key = _get_config()[0]

for sid in TARGETS:
    sc = scenarios[sid]
    md = (ROOT / sc["file"]).read_text(encoding="utf-8")
    ref = extract_reference_reply(md)
    ref_keys = ref_key_hits(ref) if ref else set()
    print(f"\n=== {sid} ref_keys={sorted(ref_keys)} ===")
    for i in range(RUNS):
        row = run_case_with_images(
            sc, libs, generate=True, api_key=api_key, domain_id="topens"
        )
        d = draft_case(row, sc)
        rk = ref_key_hits(row["generated_reply_en"] or "")
        imgs = len(row.get("images_used") or [])
        print(
            f"  run {i+1}: dim1={d['dim1']} dim2={d['dim2']} dim3={d['dim3']} "
            f"dim4={d['dim4']} steps={row['reply_audit']['step_count']} "
            f"imgs={imgs} miss={sorted(ref_keys - rk)}"
        )
