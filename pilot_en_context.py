#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 1a pilot EN manifest → cs_email generation context (ADR-0003).

EN index paths come from the active domain pack (indices.yaml).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from domains.loader import get_default_domain
from image_utils import normalize_images

REPO_ROOT = Path(__file__).resolve().parent


def _en_dirs() -> dict[str, Path]:
    return {
        pid: REPO_ROOT / rel
        for pid, rel in get_default_domain().en_chroma_dirs().items()
    }


# Compatibility: tests / callers may still import PILOT_EN_DIRS.
PILOT_EN_DIRS: dict[str, Path] = _en_dirs()


@lru_cache(maxsize=8)
def _load_en_chunk_by_id(library_id: str) -> dict[str, dict[str, Any]]:
    chroma = _en_dirs().get(library_id)
    if not chroma or not (chroma / "manifest.json").is_file():
        return {}
    manifest = json.loads((chroma / "manifest.json").read_text(encoding="utf-8"))
    return {c["chunk_id"]: c for c in manifest.get("chunks") or []}


def _best_en_block(en_by_id: dict[str, dict], group_id: str) -> dict[str, Any] | None:
    parent: dict[str, Any] | None = None
    for c in en_by_id.values():
        if c.get("group_id") != group_id:
            continue
        en = (c.get("content_en") or "").strip()
        if not en:
            continue
        if not c.get("parent_id"):
            parent = c
        elif parent is None:
            parent = c
    return parent


def enrich_hits_for_cs_email(
    hits: list[dict],
    library_id: str,
) -> list[dict]:
    """Fill missing content_en / links from Phase 1a pilot EN index."""
    en_by_id = _load_en_chunk_by_id(library_id)
    if not en_by_id:
        return hits
    out: list[dict] = []
    for hit in hits:
        row = dict(hit)
        gid = str(row.get("group_id") or "")
        if not (row.get("content_en") or "").strip():
            en_block = _best_en_block(en_by_id, gid)
            if en_block:
                row["content_en"] = en_block.get("content_en")
                if en_block.get("links") and not row.get("links"):
                    row["links"] = en_block.get("links")
                if en_block.get("images") and not row.get("images"):
                    row["images"] = normalize_images(en_block.get("images"))
        out.append(row)
    return out
