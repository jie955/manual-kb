#!/usr/bin/env python3
"""Compatibility launcher for Phase 0 gate probe.

Canonical implementation: evals/runners/run_cs_e2e_gate.py

Re-exports helpers for overlay scripts in this directory. CLI delegates to the
formal runner and writes legacy artifacts (cs_e2e_gate_results.json, phase0_gate_probe.md).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runners._env import load_dotenv as _load_dotenv  # noqa: E402
from evals.runners.gate_report import (  # noqa: E402
    get_gate_scenario_ids,
    write_probe_markdown,
)
from evals.runners.run_cs_e2e_gate import (  # noqa: E402
    DEFAULT_DOMAIN,
    DEFAULT_MODEL,
    customer_email,
    run_case,
)
from evals.runners.run_cs_e2e_gate import load_scenarios as _load_scenarios  # noqa: E402

_load_dotenv()

GATE_SCENARIO_IDS = get_gate_scenario_ids(DEFAULT_DOMAIN)
MAP_PATH = ROOT / "_scratch" / "eval" / "cs_email_query_map.json"


def load_scenarios() -> dict[str, dict]:
    """Load scenarios from scratch case map (historical no-arg API)."""
    return _load_scenarios(MAP_PATH)


if __name__ == "__main__":
    from evals.runners.run_cs_e2e_gate import main_scratch_compat

    raise SystemExit(main_scratch_compat())
