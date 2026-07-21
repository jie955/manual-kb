#!/usr/bin/env python3
"""Regenerate Phase 0 pilot replies with style exemplars + scenario_id."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

for path in (ROOT / ".env", ROOT.parent / ".env"):
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from generate_answer import _get_config  # noqa: E402
from library_router import load_unified_libraries  # noqa: E402
from run_cs_e2e_gate import customer_email, load_scenarios, run_case  # noqa: E402

PILOT = ["cs_0001", "cs_0008", "cs_0013"]


def main() -> int:
    if not _get_config()[0]:
        print("ERROR: QA_API_KEY required", file=sys.stderr)
        return 1
    scenarios = load_scenarios()
    libraries = load_unified_libraries(model="_scratch/modelscope/BAAI/bge-m3")
    out_dir = Path(__file__).resolve().parent / "phase0_pilot_replies"
    out_dir.mkdir(exist_ok=True)
    rows = []
    for sid in PILOT:
        row = run_case(scenarios[sid], libraries, generate=True, api_key=_get_config()[0])
        text = row.get("reply_full") or row.get("reply_preview") or ""
        (out_dir / f"{sid}.md").write_text(text, encoding="utf-8")
        rows.append(row)
        fam = (row.get("style") or {}).get("family_id", "?")
        print(f"{sid} · style={fam} · {row.get('reply_len')} chars · trunc={row.get('truncated')}")
    meta = Path(__file__).resolve().parent / "cs_e2e_gate_generated.json"
    meta.write_text(json.dumps({"results": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
