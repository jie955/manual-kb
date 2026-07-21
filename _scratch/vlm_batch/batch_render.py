#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_render.py

按 page_manifest.json 批量渲页（2x PNG）到 _scratch/vlm_batch/pages/。
复用 vlm_pilot/render_pages.py 的页脚印刷页码定位逻辑。

用法:
  python _scratch/vlm_batch/batch_render.py
  python _scratch/vlm_batch/batch_render.py --manifest page_manifest.json --scale 2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import fitz

REPO_ROOT = Path(__file__).resolve().parents[2]
BATCH_DIR = Path(__file__).resolve().parent
DEFAULT_MANIFEST = BATCH_DIR / "page_manifest.json"
DEFAULT_OUT = BATCH_DIR / "pages"


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


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch render manual pages from manifest")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=None,
        help="覆盖 manifest 中的 PDF 路径",
    )
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    pdf_rel = manifest.get("source_path", "samples/manuals/A3S,A5(S),A8(S)说明书.pdf")
    pdf_path = args.pdf or (REPO_ROOT / pdf_rel)
    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")

    pages = manifest.get("pages") or []
    if not pages:
        raise SystemExit("manifest has no pages")

    doc = fitz.open(pdf_path)
    print(f"PDF: {pdf_path.name} ({len(doc)} pages)", file=sys.stderr)
    print(f"Rendering {len(pages)} page(s) at {args.scale}x -> {args.out_dir}", file=sys.stderr)

    rendered = 0
    for entry in pages:
        printed = entry.get("printed_page")
        pdf_index = entry.get("pdf_index")
        if pdf_index is not None:
            idx = int(pdf_index)
            if printed is not None:
                printed = int(printed)
                try:
                    footer_idx = find_page_by_printed_number(doc, printed)
                    if footer_idx != idx:
                        print(
                            f"  warn: p{printed:02d} footer -> index {footer_idx}, "
                            f"manifest pdf_index={idx} (using manifest)",
                            file=sys.stderr,
                        )
                except ValueError:
                    print(
                        f"  warn: p{printed:02d} not in PDF footers; "
                        f"using manifest pdf_index={idx}",
                        file=sys.stderr,
                    )
                out_name = entry.get("image_name") or f"p{printed:02d}.png"
            else:
                out_name = entry.get("image_name") or f"idx{idx:02d}.png"
        elif printed is not None:
            printed = int(printed)
            idx = find_page_by_printed_number(doc, printed)
            out_name = entry.get("image_name") or f"p{printed:02d}.png"
        else:
            print(f"  skip: entry missing printed_page and pdf_index", file=sys.stderr)
            continue

        out_path = args.out_dir / out_name
        render_page(doc, idx, out_path, args.scale)
        rendered += 1
        label = f"p{printed:02d}" if printed is not None else f"idx{idx}"
        print(
            f"  {label} ({entry.get('page_type', '?')}) -> index={idx} -> {out_path.name}",
            file=sys.stderr,
        )

    doc.close()
    print(f"rendered {rendered} page(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
