#!/usr/bin/env python3
"""Scan AT6132S manual PDF page structure."""
from __future__ import annotations

import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "samples/manuals/AT6132S,AT12132S说明书.pdf"
OUT = Path(__file__).resolve().parent / "_pdf_scan.json"


def main() -> None:
    doc = fitz.open(PDF)
    rows = []
    for idx in range(len(doc)):
        lines = [ln.strip() for ln in doc[idx].get_text("text").splitlines() if ln.strip()]
        nums = [l for l in lines if l.isdigit() and len(l) <= 2]
        rows.append(
            {
                "pdf_index": idx,
                "line_count": len(lines),
                "footer_nums": nums[:8],
                "empty": len(lines) == 0,
            }
        )
    doc.close()

    # detect printed pages via footer number match
    printed_map: dict[int, int] = {}
    for r in rows:
        if len(r["footer_nums"]) == 1 and r["footer_nums"][0].isdigit():
            printed_map[int(r["footer_nums"][0])] = r["pdf_index"]

    summary = {
        "pdf_pages": len(rows),
        "empty_indices": [r["pdf_index"] for r in rows if r["empty"]],
        "printed_map_size": len(printed_map),
        "printed_max": max(printed_map) if printed_map else 0,
        "printed_min": min(printed_map) if printed_map else 0,
        "rows": rows,
        "printed_map": {str(k): v for k, v in sorted(printed_map.items())},
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
