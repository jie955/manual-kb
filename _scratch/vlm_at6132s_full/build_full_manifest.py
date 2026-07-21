#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_full_manifest.py — AT6132S / AT12132S 说明书全量 page_manifest。

用法:
  python _scratch/vlm_at6132s_full/build_full_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parents[2]
FULL_DIR = Path(__file__).resolve().parent
DEFAULT_PDF = REPO_ROOT / "samples" / "manuals" / "AT6132S,AT12132S说明书.pdf"
PRINTED_MAX = 45
FRONT_PDF_INDICES = [1, 2]
SKIP_PDF_INDICES = set(range(48, 56))

OTHER_PAGES = {1, 3, 5}
DEFAULT_STEP = "step_mixed"
SOURCE_PDF = "AT6132S,AT12132S说明书.pdf"


def find_page_by_printed_number(doc: fitz.Document, printed: int) -> int:
    target = str(printed)
    for idx in range(len(doc)):
        lines = [ln.strip() for ln in doc[idx].get_text("text").splitlines() if ln.strip()]
        if target in lines:
            return idx
    raise ValueError(f"printed page {printed} not found")


def default_page_type(printed: int) -> str:
    if printed in OTHER_PAGES:
        return "other"
    if printed == 2:
        return "warning"
    if printed == 4:
        return "packing"
    if printed == 6:
        return "spec_table"
    if printed == 18:
        return "spec_table"
    if printed >= 44:
        return "other"
    return DEFAULT_STEP


def main() -> None:
    doc = fitz.open(DEFAULT_PDF)
    pages: list[dict] = []
    missing: list[int] = []

    for printed in range(1, PRINTED_MAX + 1):
        try:
            pdf_index = find_page_by_printed_number(doc, printed)
        except ValueError:
            missing.append(printed)
            continue
        pages.append(
            {
                "printed_page": printed,
                "pdf_index": pdf_index,
                "page_type": default_page_type(printed),
                "chapter_hint": f"AT6132S manual printed page {printed}",
            }
        )

    for pdf_index in FRONT_PDF_INDICES:
        if pdf_index >= len(doc):
            continue
        pages.append(
            {
                "printed_page": None,
                "pdf_index": pdf_index,
                "page_type": "other",
                "chapter_hint": "Front matter (cover / TOC)",
                "image_name": f"idx{pdf_index:02d}.png",
            },
        )

    doc.close()
    pages.sort(key=lambda e: int(e["pdf_index"]))

    manifest = {
        "source_pdf": SOURCE_PDF,
        "source_path": f"samples/manuals/{SOURCE_PDF}",
        "doc_prefix": "at6132s-manual",
        "document_title": "Document:AT6132S AT12132S Installation Manual",
        "models": ["AT6132S", "AT12132S"],
        "selection_notes": (
            f"PDF 56 pages total: {len(pages)} VLM targets "
            f"(printed 1–{PRINTED_MAX} + front idx {FRONT_PDF_INDICES}; "
            f"skip empty idx 0 and blank idx 48–55)."
        ),
        "pilot_reuse": [],
        "pages": pages,
    }

    out = FULL_DIR / "page_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {len(pages)} pages -> {out}", file=sys.stderr)
    if missing:
        print(f"warn: missing printed pages: {missing}", file=sys.stderr)


if __name__ == "__main__":
    main()
