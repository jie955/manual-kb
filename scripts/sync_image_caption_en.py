#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync English image captions from crosswalk into chunks_captioned + chroma manifests."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from image_utils import migrate_legacy_caption, normalize_image_entry, normalize_images

CROSSWALK_PATH = ROOT / "samples/troubleshooting/image_caption_crosswalk.json"

LIBRARIES: list[dict[str, Any]] = [
    {
        "id": "a3s",
        "chunks": ROOT / "_scratch/run-006/chunks_captioned.json",
        "chroma_zh": ROOT / "_scratch/run-007/chroma_captioned",
        "chroma_en": ROOT / "_scratch/run-007/chroma_captioned_en",
        "manual": ROOT / "_scratch/vlm_a3s_full/manual_chunks.json",
    },
    {
        "id": "ad5s",
        "chunks": ROOT / "_scratch/run-ad5s/chunks_captioned.json",
        "chroma_zh": ROOT / "_scratch/run-ad5s/chroma_captioned",
        "chroma_en": ROOT / "_scratch/run-ad5s/chroma_captioned_en",
        "manual": ROOT / "_scratch/vlm_ad5s_full/manual_chunks.json",
    },
    {
        "id": "tc148",
        "chunks": ROOT / "_scratch/run-tc148/chunks_captioned.json",
        "chroma_zh": ROOT / "_scratch/run-tc148/chroma_captioned",
        "chroma_en": ROOT / "_scratch/run-tc148/chroma_captioned_en",
        "manual": None,
    },
]


def load_crosswalk(path: Path = CROSSWALK_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data


def _basename(file_name: str) -> str:
    return Path(file_name).name


def build_alias_index(entries: dict[str, Any]) -> dict[str, str]:
    """Map alias basename -> canonical crosswalk key."""
    index: dict[str, str] = {}
    for key, entry in entries.items():
        index[_basename(key)] = key
        for alias in entry.get("aliases") or []:
            index[_basename(alias)] = key
    return index


def resolve_caption_en(
    library_id: str,
    file_name: str,
    entries: dict[str, Any],
    alias_index: dict[str, str],
) -> str | None:
    base = _basename(file_name)
    key = alias_index.get(base)
    if not key:
        return None
    entry = entries[key]
    libs = entry.get("libraries")
    if libs and library_id not in libs:
        return None
    overrides = entry.get("overrides") or {}
    if library_id in overrides:
        return str(overrides[library_id]).strip() or None
    cap = entry.get("caption_en")
    return str(cap).strip() if cap else None


def patch_image_dict(
    img: dict[str, Any],
    *,
    library_id: str,
    entries: dict[str, Any],
    alias_index: dict[str, str],
) -> tuple[dict[str, Any], bool]:
    row = migrate_legacy_caption(dict(img))
    cap_en = resolve_caption_en(library_id, row.get("file", ""), entries, alias_index)
    changed = False
    if cap_en and row.get("caption_en") != cap_en:
        row["caption_en"] = cap_en
        changed = True
    return row, changed


def patch_images_field(
    images: Any,
    *,
    library_id: str,
    entries: dict[str, Any],
    alias_index: dict[str, str],
    only_basenames: set[str] | None,
) -> tuple[list[Any], int]:
    if not images:
        return images if isinstance(images, list) else [], 0
    patched = 0
    out: list[Any] = []
    for raw in images if isinstance(images, list) else normalize_images(images):
        if isinstance(raw, str):
            base = _basename(raw)
            if only_basenames and base not in only_basenames:
                out.append(raw)
                continue
            cap_en = resolve_caption_en(library_id, base, entries, alias_index)
            if cap_en:
                out.append({"file": base, "caption_en": cap_en, "caption_status": "crosswalk"})
                patched += 1
            else:
                out.append(raw)
            continue
        row, changed = patch_image_dict(
            normalize_image_entry(raw),
            library_id=library_id,
            entries=entries,
            alias_index=alias_index,
        )
        base = _basename(row.get("file", ""))
        if only_basenames and base not in only_basenames:
            out.append(row)
            continue
        if changed:
            patched += 1
        out.append(row)
    return out, patched


def patch_chunks_file(
    chunks_path: Path,
    *,
    library_id: str,
    entries: dict[str, Any],
    alias_index: dict[str, str],
    only_basenames: set[str] | None,
    dry_run: bool,
) -> dict[str, Any]:
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    total_patched = 0
    touched_files: set[str] = set()
    missing: set[str] = set()

    for chunk in chunks:
        images = chunk.get("images")
        if not images:
            continue
        new_images, patched = patch_images_field(
            images,
            library_id=library_id,
            entries=entries,
            alias_index=alias_index,
            only_basenames=only_basenames,
        )
        if patched:
            chunk["images"] = new_images
            total_patched += patched
            for img in normalize_images(new_images):
                base = _basename(img.get("file", ""))
                if only_basenames is None or base in only_basenames:
                    touched_files.add(base)
                    if not img.get("caption_en"):
                        missing.add(base)

    if not dry_run and total_patched:
        tmp = chunks_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(chunks_path)

    return {
        "path": str(chunks_path),
        "patched": total_patched,
        "touched_files": sorted(touched_files),
        "missing_en": sorted(missing),
    }


def patch_manifest_file(
    manifest_path: Path,
    *,
    library_id: str,
    entries: dict[str, Any],
    alias_index: dict[str, str],
    only_basenames: set[str] | None,
    dry_run: bool,
) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {"path": str(manifest_path), "skipped": "not_found", "patched": 0}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = manifest.get("chunks")
    if chunks is None and "chunk_by_id" in manifest:
        chunks = list(manifest["chunk_by_id"].values())
    if not isinstance(chunks, list):
        return {"path": str(manifest_path), "skipped": "no_chunks", "patched": 0}

    total_patched = 0
    for chunk in chunks:
        images = chunk.get("images")
        if not images:
            continue
        new_images, patched = patch_images_field(
            images,
            library_id=library_id,
            entries=entries,
            alias_index=alias_index,
            only_basenames=only_basenames,
        )
        if patched:
            chunk["images"] = new_images
            total_patched += patched

    if not dry_run and total_patched:
        tmp = manifest_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(manifest_path)

    return {"path": str(manifest_path), "patched": total_patched}


def harvest_manual_captions(manual_path: Path) -> list[dict[str, str]]:
    if not manual_path or not manual_path.is_file():
        return []
    chunks = json.loads(manual_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for chunk in chunks:
        for img in chunk.get("images") or []:
            if not isinstance(img, dict):
                continue
            cap_en = (img.get("caption_en") or img.get("caption") or "").strip()
            if not cap_en:
                continue
            rows.append(
                {
                    "manual_file": str(img.get("file") or ""),
                    "caption_en": cap_en,
                    "chunk_id": str(chunk.get("chunk_id") or ""),
                }
            )
    return rows


def suggest_mappings(library_id: str, manual_path: Path | None) -> None:
    rows = harvest_manual_captions(manual_path) if manual_path else []
    print(f"\n=== suggest: {library_id} ({len(rows)} manual captions) ===", file=sys.stderr)
    for row in rows[:40]:
        print(json.dumps(row, ensure_ascii=False), file=sys.stderr)
    if len(rows) > 40:
        print(f"... and {len(rows) - 40} more", file=sys.stderr)


def run_sync(
    *,
    mvp_only: bool,
    all_images: bool,
    dry_run: bool,
    suggest: bool,
) -> dict[str, Any]:
    crosswalk = load_crosswalk()
    entries = crosswalk.get("entries") or {}
    alias_index = build_alias_index(entries)

    if mvp_only:
        only_basenames = {_basename(x) for x in crosswalk.get("mvp_basenames") or []}
        for key, entry in entries.items():
            only_basenames.add(_basename(key))
            for alias in entry.get("aliases") or []:
                only_basenames.add(_basename(alias))
    elif all_images:
        only_basenames = None
    else:
        raise SystemExit("Specify --mvp or --all")

    report: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "mvp" if mvp_only else "all",
        "dry_run": dry_run,
        "libraries": [],
    }

    if suggest:
        for lib in LIBRARIES:
            suggest_mappings(lib["id"], lib.get("manual"))
        return report

    for lib in LIBRARIES:
        lib_report: dict[str, Any] = {"id": lib["id"], "chunks": None, "manifests": []}
        chunks_path: Path = lib["chunks"]
        if not chunks_path.is_file():
            lib_report["chunks"] = {"skipped": "not_found"}
        else:
            lib_report["chunks"] = patch_chunks_file(
                chunks_path,
                library_id=lib["id"],
                entries=entries,
                alias_index=alias_index,
                only_basenames=only_basenames,
                dry_run=dry_run,
            )
        for label, chroma_key in (("zh", "chroma_zh"), ("en", "chroma_en")):
            manifest = Path(lib[chroma_key]) / "manifest.json"
            lib_report["manifests"].append(
                {
                    "index": label,
                    **patch_manifest_file(
                        manifest,
                        library_id=lib["id"],
                        entries=entries,
                        alias_index=alias_index,
                        only_basenames=only_basenames,
                        dry_run=dry_run,
                    ),
                }
            )
        report["libraries"].append(lib_report)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync caption_en from crosswalk into chunks + manifests")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--mvp", action="store_true", help="Patch MVP basename set only")
    scope.add_argument("--all", action="store_true", help="Patch all image references in crosswalk entries")
    scope.add_argument("--suggest", action="store_true", help="Print manual caption harvest (no writes)")
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not write files")
    args = parser.parse_args()

    report = run_sync(
        mvp_only=bool(args.mvp),
        all_images=bool(args.all),
        dry_run=bool(args.dry_run),
        suggest=bool(args.suggest),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
