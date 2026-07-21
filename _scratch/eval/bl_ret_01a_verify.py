#!/usr/bin/env python3
# -*- coding: utf-8
"""BL-RET-01a verification · doc_type filter + merge smoke."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval_engine import RetrievalConfig, search

MODEL = "_scratch/modelscope/BAAI/bge-m3"
QUERY_TS = "AT12131S gate does nothing when I push the button"
QUERY_MANUAL = "DIP switch photocell wiring installation A3S control board"


def probe(label: str, chroma: Path, *, doc_type: str | None) -> str:
    cfg = RetrievalConfig(chroma_dir=chroma, model=MODEL, k=3, doc_type=doc_type)
    hits = search(cfg, QUERY_TS if "ts" in label else QUERY_MANUAL)
    top = [(h.group_id, round(h.score, 4), h.metadata.get("doc_type")) for h in hits[:3]]
    print(f"{label} doc_type={doc_type!r} -> {top}")
    return top[0][2] if top else ""


def main() -> int:
    merged = ROOT / "_scratch/unified/a3s/chroma_merged"
    if not merged.is_dir():
        print("SKIP merge smoke: no unified chroma", file=sys.stderr)
        return 1

    ts_only = probe("merged-ts", merged, doc_type="troubleshooting")
    manual_only = probe("merged-manual", merged, doc_type="installation_manual")
    ok_ts = ts_only == "troubleshooting"
    ok_manual = manual_only == "installation_manual"
    print(f"filter smoke: ts={ok_ts} manual={ok_manual}")
    return 0 if ok_ts and ok_manual else 1


if __name__ == "__main__":
    raise SystemExit(main())
