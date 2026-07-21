#!/usr/bin/env python3
"""Merge retry page chunks into manual_chunks.json by page_key."""
from __future__ import annotations

import json
import sys
from pathlib import Path

FULL_DIR = Path(__file__).resolve().parent


def page_sort_key(c: dict) -> tuple:
    pk = c.get("page_key") or ""
    if pk.startswith("printed:"):
        return (1, int(pk.split(":")[1]))
    if pk.startswith("idx:"):
        return (0, int(pk.split(":")[1]))
    pr = c.get("page_range") or [9999]
    return (2, pr[0])


def merge(full_path: Path, patch_path: Path, page_keys: set[str]) -> None:
    full = json.loads(full_path.read_text(encoding="utf-8"))
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    merged = [c for c in full if c.get("page_key") not in page_keys] + patch
    merged.sort(key=page_sort_key)
    full_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    ret = sum(1 for c in merged if c.get("is_retrievable"))
    print(
        f"merged: {len(merged)} chunks ({ret} retrievable), "
        f"patched {len(page_keys)} pages (+{len(patch)} blocks)",
        file=sys.stderr,
    )


def main() -> None:
    merge(
        FULL_DIR / "manual_chunks.json",
        FULL_DIR / "manual_chunks_retry.json",
        {"printed:6", "printed:29", "printed:46"},
    )


if __name__ == "__main__":
    main()
