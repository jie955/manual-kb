#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_full_manifest.py — TC148 说明书 page_manifest（2 页接线图）。

用法:
  python _scratch/vlm_tc148_full/build_full_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FULL_DIR = Path(__file__).resolve().parent
SOURCE_PDF = "TC148说明书.pdf"

# PDF 仅 2 页，无可用文本层页码；按 pdf_index 顺序映射为印刷页 1–2。
PAGES = [
    {
        "printed_page": 1,
        "pdf_index": 0,
        "page_type": "other",
        "chapter_hint": "TC148 waterproof wall push button wiring diagram page 1",
    },
    {
        "printed_page": 2,
        "pdf_index": 1,
        "page_type": "other",
        "chapter_hint": "TC148 waterproof wall push button wiring diagram page 2",
    },
]


def main() -> None:
    manifest = {
        "source_pdf": SOURCE_PDF,
        "source_path": f"samples/manuals/{SOURCE_PDF}",
        "doc_prefix": "tc148-manual",
        "document_title": "Document:TC148 Waterproof Wall Push Button Installation Manual",
        "models": ["TC148"],
        "selection_notes": (
            "PDF 2 pages total: both are graphic wiring diagrams; "
            "no extractable printed page numbers in text layer."
        ),
        "pilot_reuse": [],
        "pages": PAGES,
    }

    out = FULL_DIR / "page_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {len(PAGES)} pages -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
