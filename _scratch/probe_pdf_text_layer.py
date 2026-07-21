"""Probe PDF native text layer vs vector-outlined content (PyMuPDF)."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import fitz

MANUALS_DIR = Path(__file__).resolve().parents[1] / "samples" / "manuals"


def line_kind(line: str) -> str:
    if re.fullmatch(r"[\d\s]+", line):
        return "page_num"
    if line in ("◆", "●", "■", "▪"):
        return "bullet_only"
    if re.fullmatch(r"[.\s·…\-_]+", line):
        return "dot_leader"
    if len(line) <= 3 and not re.search(r"[A-Za-z\u4e00-\u9fff]{2,}", line):
        return "symbol_short"
    if re.search(r"[A-Za-z\u4e00-\u9fff]{3,}", line):
        return "meaningful"
    return "other"


def analyze_pdf(path: Path) -> dict:
    doc = fitz.open(path)
    page_stats = []
    meaningful_lines: list[str] = []

    for i, page in enumerate(doc):
        text = page.get_text("text")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        kinds = Counter(line_kind(ln) for ln in lines)
        meaningful = [ln for ln in lines if line_kind(ln) == "meaningful"]

        text_spans = 0
        text_span_chars = 0
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text_spans += 1
                    text_span_chars += len(span.get("text", ""))

        drawings = page.get_drawings()
        path_ops = sum(len(d.get("items", [])) for d in drawings)

        page_stats.append(
            {
                "page": i + 1,
                "lines": len(lines),
                "meaningful": len(meaningful),
                "kinds": dict(kinds),
                "text_spans": text_spans,
                "text_span_chars": text_span_chars,
                "drawings": len(drawings),
                "path_ops": path_ops,
                "sample_meaningful": meaningful[:3],
                "sample_all": lines[:5],
            }
        )
        meaningful_lines.extend(meaningful)

    total_pages = len(doc)
    sample_idxs = [0, total_pages // 2, total_pages - 1] if total_pages > 1 else [0]
    samples = [page_stats[i] for i in sample_idxs]

    result = {
        "name": path.name,
        "pages": total_pages,
        "pages_with_meaningful": sum(1 for p in page_stats if p["meaningful"] > 0),
        "total_meaningful_lines": sum(p["meaningful"] for p in page_stats),
        "total_text_span_chars": sum(p["text_span_chars"] for p in page_stats),
        "total_text_spans": sum(p["text_spans"] for p in page_stats),
        "total_drawings": sum(p["drawings"] for p in page_stats),
        "sample_pages": samples,
        "unique_meaningful_preview": list(dict.fromkeys(meaningful_lines))[:15],
    }
    doc.close()
    return result


def main() -> None:
    files = sorted(MANUALS_DIR.glob("*.pdf"))
    if not files:
        print(f"No PDFs under {MANUALS_DIR}")
        return

    print("=" * 80)
    for path in files:
        r = analyze_pdf(path)
        usable = "NO" if r["total_meaningful_lines"] < 5 else "PARTIAL"
        print(f"\nFILE: {r['name']}")
        print(f"  Pages: {r['pages']}")
        print(f"  Native text layer usable: {usable}")
        print(
            f"  Pages with meaningful lines: {r['pages_with_meaningful']}/{r['pages']}"
        )
        print(f"  Total meaningful lines (3+ letter/word): {r['total_meaningful_lines']}")
        print(
            f"  Text spans / span chars: {r['total_text_spans']} / {r['total_text_span_chars']}"
        )
        print(f"  Drawing objects (vector paths): {r['total_drawings']}")
        print("  Sample pages:")
        for sp in r["sample_pages"]:
            print(
                f"    p{sp['page']}: lines={sp['lines']} meaningful={sp['meaningful']} "
                f"spans={sp['text_spans']} drawings={sp['drawings']}"
            )
            if sp["sample_all"]:
                print(f"      extracted lines: {sp['sample_all'][:4]}")
            if sp["sample_meaningful"]:
                print(f"      meaningful: {sp['sample_meaningful']}")
        preview = r["unique_meaningful_preview"]
        print(f"  Unique meaningful preview: {preview if preview else '(none)'}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
