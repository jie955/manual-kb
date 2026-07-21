#!/usr/bin/env python3
# -*- coding: utf-8
"""BL Wave 3 · manual supplement smoke (BL-RET-01a + unified_search)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_router import load_unified_libraries, unified_search

MODEL = "_scratch/modelscope/BAAI/bge-m3"
QUERIES = [
    ("a3s-install", "DIP switch photocell wiring installation A3S control board", "installation_manual"),
    ("ad5s-install", "AD5S dual swing wiring diagram installation manual", "installation_manual"),
    ("a3s-ts", "AT12131S gate does nothing when I push the button", "troubleshooting"),
]


def main() -> int:
    libs = load_unified_libraries(
        MODEL,
        k=3,
        index="en",
        merged=True,
        allowed_libraries=["a3s", "ad5s"],
    )
    ok = 0
    for label, query, expect_dtype in QUERIES:
        _, hits = unified_search(query, libs, include_manual=True)
        manual_hits = [h for h in hits if h.metadata.get("doc_type") == "installation_manual"]
        top = hits[0].group_id if hits else None
        score = round(hits[0].score, 4) if hits else 0
        if expect_dtype == "installation_manual":
            hit_ok = bool(manual_hits)
            extra = f"manual={manual_hits[0].group_id}({round(manual_hits[0].score,4)})" if manual_hits else "no manual"
        else:
            hit_ok = top and top.startswith("qa_")
            extra = ""
        print(f"{label}: top={top} score={score} {extra} -> {'OK' if hit_ok else 'FAIL'}")
        ok += int(hit_ok)
    print(f"manual smoke: {ok}/{len(QUERIES)}")
    return 0 if ok == len(QUERIES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
