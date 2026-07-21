#!/usr/bin/env python3
"""Merge manual_chunks_p03.json into manual_chunks.json by page_key."""
from __future__ import annotations

import json
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


def main() -> None:
    full_path = FULL_DIR / "manual_chunks.json"
    p03_path = FULL_DIR / "manual_chunks_p03.json"
    full = json.loads(full_path.read_text(encoding="utf-8"))
    p03 = json.loads(p03_path.read_text(encoding="utf-8"))

    merged = [c for c in full if c.get("page_key") != "printed:3"] + p03
    merged.sort(key=page_sort_key)
    full_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    ret_before = sum(1 for c in full if c.get("is_retrievable"))
    ret_after = sum(1 for c in merged if c.get("is_retrievable"))
    print(
        f"merged: {len(merged)} chunks ({ret_after} retrievable, "
        f"+{len(merged) - len(full)} blocks, +{ret_after - ret_before} retrievable)"
    )


if __name__ == "__main__":
    main()
