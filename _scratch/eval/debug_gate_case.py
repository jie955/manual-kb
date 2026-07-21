#!/usr/bin/env python3
"""Debug single gate case generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runners._env import load_dotenv as _load_dotenv  # noqa: E402
from evals.runners.run_cs_e2e_gate import load_scenarios, run_case  # noqa: E402
from library_router import load_unified_libraries  # noqa: E402

MAP_PATH = ROOT / "_scratch" / "eval" / "cs_email_query_map.json"


def load_scenarios_legacy() -> dict:
    return load_scenarios(MAP_PATH)


_load_dotenv()


def main() -> int:
    sid = sys.argv[1] if len(sys.argv) > 1 else "cs_0024"
    sc = load_scenarios_legacy()[sid]
    libs = load_unified_libraries()
    key = _get_config()[0]
    row = run_case(sc, libs, generate=True, api_key=key)
    print(f"scenario={sid} reply_len={row.get('reply_len')} truncated={row.get('truncated')}")
    if row.get("reply_full"):
        print(row["reply_full"][:500])
    else:
        print("(no reply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
