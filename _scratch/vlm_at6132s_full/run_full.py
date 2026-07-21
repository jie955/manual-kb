#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_full.py — AT6132S / AT12132S 说明书全量 VLM 流水线。

步骤：build_manifest → batch_render → pdf_vlm_parser → renormalize → adapter → enrich → embed

用法:
  python _scratch/vlm_at6132s_full/run_full.py
  python _scratch/vlm_at6132s_full/run_full.py --skip-manifest --skip-render --skip-parse
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FULL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
from env_utils import load_dotenv

DEFAULT_MODEL = REPO_ROOT / "_scratch/modelscope/BAAI/bge-m3"


def run(cmd: list[str]) -> None:
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="AT6132S full VLM pipeline")
    parser.add_argument("--skip-manifest", action="store_true")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--skip-parse", action="store_true")
    parser.add_argument("--skip-adapter", action="store_true")
    parser.add_argument("--skip-enrich", action="store_true")
    parser.add_argument("--skip-renormalize", action="store_true")
    parser.add_argument("--skip-embed", action="store_true")
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    args = parser.parse_args()

    load_dotenv()

    manifest = FULL_DIR / "page_manifest.json"
    pages_dir = FULL_DIR / "pages"
    manual_chunks = FULL_DIR / "manual_chunks.json"
    chunks_out = FULL_DIR / "chunks.json"
    chunks_enriched = FULL_DIR / "chunks_enriched.json"
    chroma_dir = FULL_DIR / "chroma_enriched"

    if not args.skip_manifest:
        run([sys.executable, str(FULL_DIR / "build_full_manifest.py")])

    if not args.skip_render:
        run(
            [
                sys.executable,
                str(REPO_ROOT / "_scratch/vlm_batch/batch_render.py"),
                "--manifest",
                str(manifest),
                "--out-dir",
                str(pages_dir),
            ]
        )

    if not args.skip_parse:
        run(
            [
                sys.executable,
                str(REPO_ROOT / "pdf_vlm_parser.py"),
                "--manifest",
                str(manifest),
                "--pages-dir",
                str(pages_dir),
                "--out",
                str(manual_chunks),
                "--stats-out",
                str(FULL_DIR / "parse_stats.json"),
            ]
        )

    if not args.skip_renormalize:
        run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts/renormalize_manual_chunks.py"),
                "--manifest",
                str(manifest),
                "--pages-dir",
                str(pages_dir),
                "--out",
                str(manual_chunks),
            ]
        )

    if not args.skip_adapter and manual_chunks.is_file():
        run(
            [
                sys.executable,
                str(REPO_ROOT / "manual_chunk_adapter.py"),
                str(manual_chunks),
                str(chunks_out),
                "--manifest",
                str(manifest),
                "--images-base",
                str(FULL_DIR),
            ]
        )

    embed_input = chunks_out
    if not args.skip_enrich and chunks_out.is_file():
        run(
            [
                sys.executable,
                str(REPO_ROOT / "manual_embed_enrich.py"),
                str(chunks_out),
                str(chunks_enriched),
                "--manifest",
                str(manifest),
            ]
        )
        embed_input = chunks_enriched

    if not args.skip_embed and embed_input.is_file():
        model_path = Path(args.model)
        if not model_path.is_file() and not model_path.is_dir():
            print(f"[full] skip embed: model not found at {model_path}", file=sys.stderr)
        else:
            data = json.loads(embed_input.read_text(encoding="utf-8"))
            retrievable = sum(1 for c in data if c.get("is_retrievable", True))
            if retrievable == 0:
                print("[full] skip embed: no retrievable chunks", file=sys.stderr)
            else:
                run(
                    [
                        sys.executable,
                        str(REPO_ROOT / "embed_ingest_local.py"),
                        str(embed_input),
                        str(chroma_dir),
                        "--model",
                        str(model_path),
                    ]
                )
                print(f"[full] ingested {retrievable} chunks -> {chroma_dir}", file=sys.stderr)

    print("[full] done", file=sys.stderr)


if __name__ == "__main__":
    main()
