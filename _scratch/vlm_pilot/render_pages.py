#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pages.py

PyMuPDF 渲页：将 A3S 说明书指定页渲染为 PNG（默认 2x 缩放）。
通过页脚印刷页码定位目标页，避免 PDF index 与印刷页码偏移。

用法:
  python render_pages.py
  python render_pages.py --pages 9 18 --scale 2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF = REPO_ROOT / "samples" / "manuals" / "A3S,A5(S),A8(S)说明书.pdf"
DEFAULT_OUT = Path(__file__).resolve().parent / "pages"


def find_page_by_printed_number(doc: fitz.Document, printed: int) -> int:
    """返回 0-based page index，其页脚含印刷页码 printed。"""
    target = str(printed)
    for idx in range(len(doc)):
        lines = [
            ln.strip()
            for ln in doc[idx].get_text("text").splitlines()
            if ln.strip()
        ]
        if target in lines:
            return idx
    raise ValueError(f"printed page {printed} not found in PDF footers")


def render_page(
    doc: fitz.Document,
    page_index: int,
    out_path: Path,
    scale: float,
) -> None:
    page = doc[page_index]
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out_path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Render A3S manual pages to PNG")
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF,
        help="源 PDF 路径",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT,
        help="输出目录",
    )
    parser.add_argument(
        "--pages",
        type=int,
        nargs="+",
        default=[9, 18],
        help="印刷页码（页脚数字），默认 9 18",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=2.0,
        help="渲染缩放倍数，默认 2x",
    )
    args = parser.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")

    doc = fitz.open(args.pdf)
    print(f"PDF: {args.pdf.name} ({len(doc)} pages)", file=sys.stderr)

    mapping: list[tuple[int, int, Path]] = []
    for printed in args.pages:
        idx = find_page_by_printed_number(doc, printed)
        out_name = f"p{printed:02d}.png"
        out_path = args.out_dir / out_name
        render_page(doc, idx, out_path, args.scale)
        mapping.append((printed, idx, out_path))
        print(
            f"  printed p{printed:02d} -> pdf_index={idx} -> {out_path}",
            file=sys.stderr,
        )

    doc.close()
    print(f"rendered {len(mapping)} page(s) to {args.out_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
