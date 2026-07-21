#!/usr/bin/env python3
"""Quick checks for cs_email context filtering and pilot EN enrichment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from context_builder import filter_hits_for_cs_email  # noqa: E402
from pilot_en_context import enrich_hits_for_cs_email  # noqa: E402


def test_filter_qa_022() -> None:
    hits = [
        {"group_id": "qa_022", "content_en": "push load"},
        {"group_id": "qa_020", "content_en": "close limit"},
        {"group_id": "qa_033", "content_en": "limit short"},
    ]
    out = filter_hits_for_cs_email(hits)
    assert [h["group_id"] for h in out] == ["qa_022"]


def test_enrich_tc148() -> None:
    hits = [{"group_id": "qa_002", "content_en": ""}]
    out = enrich_hits_for_cs_email(hits, "tc148")
    en = (out[0].get("content_en") or "").lower()
    assert "extension cable" in en
    assert "short cable" in en


if __name__ == "__main__":
    test_filter_qa_022()
    test_enrich_tc148()
    print("ok")
