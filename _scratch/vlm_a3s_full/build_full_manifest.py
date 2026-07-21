#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_full_manifest.py — 生成 A3S 说明书 52 印刷页全量 page_manifest。

合并小批量 page_manifest.json 中已标注的 page_type；其余页按页码启发式默认。

用法:
  python _scratch/vlm_a3s_full/build_full_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parents[2]
FULL_DIR = Path(__file__).resolve().parent
BATCH_MANIFEST = REPO_ROOT / "_scratch" / "vlm_batch" / "page_manifest.json"
DEFAULT_PDF = REPO_ROOT / "samples" / "manuals" / "A3S,A5(S),A8(S)说明书.pdf"
PRINTED_MAX = 43
FRONT_PDF_INDICES = [0, 1, 2]
SKIP_PDF_INDICES = set(range(46, 52))

OTHER_PAGES = {1, 3, 5}
DEFAULT_STEP = "step_mixed"


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
    if printed >= 45:
        return "other"
    return DEFAULT_STEP


def main() -> None:
    batch = json.loads(BATCH_MANIFEST.read_text(encoding="utf-8"))
    known = {int(p["printed_page"]): p for p in batch.get("pages", [])}

    doc = fitz.open(DEFAULT_PDF)
    pages: list[dict] = []
    missing: list[int] = []

    for printed in range(1, PRINTED_MAX + 1):
        try:
            pdf_index = find_page_by_printed_number(doc, printed)
        except ValueError:
            missing.append(printed)
            continue

        if printed in known:
            entry = dict(known[printed])
            entry["printed_page"] = printed
            entry["pdf_index"] = pdf_index
        else:
            entry = {
                "printed_page": printed,
                "pdf_index": pdf_index,
                "page_type": default_page_type(printed),
                "chapter_hint": f"A3S manual printed page {printed}",
            }
        pages.append(entry)

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
        "source_pdf": batch.get("source_pdf", "A3S,A5(S),A8(S)说明书.pdf"),
        "source_path": batch.get("source_path", "samples/manuals/A3S,A5(S),A8(S)说明书.pdf"),
        "models": batch.get("models", ["A3S", "A5S", "A8S"]),
        "selection_notes": (
            f"PDF 52 pages total: {len(pages)} VLM targets "
            f"(printed 1–{PRINTED_MAX} + front idx {FRONT_PDF_INDICES}; "
            f"skip blank idx 46–51)."
        ),
        "pilot_reuse": batch.get("pilot_reuse", [9, 18]),
        "pages": pages,
    }

    out = FULL_DIR / "page_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"manifest: {len(pages)} pages -> {out}", file=sys.stderr)
    if missing:
        print(f"warn: missing printed pages: {missing}", file=sys.stderr)


if __name__ == "__main__":
    main()
