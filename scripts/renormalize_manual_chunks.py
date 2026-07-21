#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 .vlm_cache.json 离线 renormalize manual_chunks（不调用 VLM API）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from env_utils import load_dotenv
from page_identity import (
    assert_printed_page_canonical_p2,
    assert_printed_page_identity_unchanged,
    chunk_ids_for_page,
    duplicate_chunk_id_report,
    load_chunks_from_cache,
    load_manifest,
    load_vlm_cache,
    normalize_page_chunks,
    renormalize_chunks_from_cache,
)


def _entry_by_printed(manifest: dict, printed: int) -> dict:
    for e in manifest.get("pages") or []:
        if e.get("printed_page") == printed:
            return e
    raise KeyError(f"printed_page {printed} not in manifest")


def _chunks_for_printed_from_cache(
    manifest: dict,
    cache: dict,
    pages_dir: Path,
    printed: int,
    model: str,
    *,
    doc_prefix: str,
) -> tuple[list[dict], list[dict]]:
    from pdf_vlm_parser import (
        VLM_CACHE_VERSION,
        _file_hash,
        _parse_json_array,
        build_user_prompt,
        load_pilot_chunks_for_pages,
        page_image_path,
        DEFAULT_PILOT_CHUNKS,
    )
    from page_identity import lookup_vlm_cache_raw

    entry = _entry_by_printed(manifest, printed)
    pilot_reuse = set(manifest.get("pilot_reuse") or [])
    if printed in pilot_reuse and DEFAULT_PILOT_CHUNKS.is_file():
        before = load_pilot_chunks_for_pages(DEFAULT_PILOT_CHUNKS, {printed})
        after = normalize_page_chunks(before, entry, doc_prefix=doc_prefix)
        return before, after

    image_path = page_image_path(entry, pages_dir)
    user_text = build_user_prompt(entry, manifest)
    raw = lookup_vlm_cache_raw(
        cache,
        image_path,
        user_text,
        entry.get("page_type", "other"),
        model,
        VLM_CACHE_VERSION,
        file_hash_fn=_file_hash,
    )
    if raw is None:
        raise KeyError(f"cache miss for printed:{printed}")
    before = _parse_json_array(raw)
    after = normalize_page_chunks(before, entry, doc_prefix=doc_prefix)
    return before, after


def main() -> None:
    parser = argparse.ArgumentParser(
        description="离线 renormalize：cache → manual_chunks（无网络）"
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pages-dir", type=Path, required=True)
    parser.add_argument("--cache-path", type=Path, default=REPO_ROOT / ".vlm_cache.json")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--regression-printed",
        type=str,
        default="2,9,18,20",
        help="normalize 前后 chunk_id 须不变的印刷页（逗号分隔；含 p2 反例确认）",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="与 parse 时一致的 CAPTION_MODEL（默认读环境变量）",
    )
    args = parser.parse_args()
    load_dotenv()

    import os

    from pdf_vlm_parser import VLM_CACHE_VERSION

    model = (
        args.model
        or os.environ.get("CAPTION_MODEL")
        or os.environ.get("TRANSLATE_MODEL")
        or "gemini-2.5-flash"
    )

    manifest = load_manifest(args.manifest)
    doc_prefix = str(manifest.get("doc_prefix") or "a3s-manual")
    cache = load_vlm_cache(args.cache_path)

    for printed_s in args.regression_printed.split(","):
        printed = int(printed_s.strip())
        before, after = _chunks_for_printed_from_cache(
            manifest, cache, args.pages_dir, printed, model, doc_prefix=doc_prefix
        )
        assert_printed_page_identity_unchanged(
            before, after, label=f"printed:{printed}"
        )
        if printed == 2:
            assert_printed_page_canonical_p2(after, printed=2)
            print(
                f"[regression] printed:2 OK — canonical p2, not front matter "
                f"({len(chunk_ids_for_page(after))} ids)",
                file=sys.stderr,
            )
        else:
            print(
                f"[regression] printed:{printed} OK ({len(chunk_ids_for_page(after))} ids)",
                file=sys.stderr,
            )

    chunks_before = load_chunks_from_cache(
        manifest,
        cache,
        args.pages_dir,
        normalize=False,
        model=model,
        cache_version=VLM_CACHE_VERSION,
        pilot_reuse=set(manifest.get("pilot_reuse") or []),
        doc_prefix=doc_prefix,
    )
    dup_before, dup_ids_before = duplicate_chunk_id_report(chunks_before)

    chunks = renormalize_chunks_from_cache(
        manifest, cache, args.pages_dir, model=model, doc_prefix=doc_prefix
    )
    dup_after, dup_ids_after = duplicate_chunk_id_report(chunks)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(chunks)} chunks -> {args.out}", file=sys.stderr)
    print(
        f"[duplicate] before={dup_before}"
        + (f" {dup_ids_before}" if dup_ids_before else "")
        + f" after={dup_after}"
        + (f" {dup_ids_after}" if dup_ids_after else ""),
        file=sys.stderr,
    )

    if dup_after != 0:
        print(
            "[duplicate] FAIL: expected after=0 (BL-PDF-04 gate)",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
