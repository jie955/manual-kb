#!/usr/bin/env python3
"""Compatibility launcher — canonical: evals/runners/cs_22mail_batch_runner.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

if __name__ == "__main__":
    from evals.runners.cs_22mail_batch_runner import main

    raise SystemExit(main())
