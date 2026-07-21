#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_batch.py — A3S 小批量 VLM 流水线编排

步骤：batch_render → pdf_vlm_parser → manual_chunk_adapter → manual_embed_enrich → embed_ingest_local

用法:
  python _scratch/vlm_batch/run_batch.py
  python _scratch/vlm_batch/run_batch.py --skip-embed
  python _scratch/vlm_batch/run_batch.py --no-enrich   # 跳过 embedding_text 增强
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from env_utils import load_dotenv
BATCH_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = (
    r"D:\CodeBuddy\Self os\SelfOS\11_Workbench-Content\scripts"
    r"\qa-doc-extractor\_scratch\modelscope\BAAI\bge-m3"
)


def run(cmd: list[str], *, cwd: Path = REPO_ROOT) -> None:
    print(f"$ {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run A3S VLM small batch pipeline")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--skip-parse", action="store_true")
    parser.add_argument("--skip-adapter", action="store_true")
    parser.add_argument("--skip-embed", action="store_true")
    parser.add_argument("--no-enrich", action="store_true", help="跳过 manual_embed_enrich")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    load_dotenv()

    manifest = BATCH_DIR / "page_manifest.json"
    pages_dir = BATCH_DIR / "pages"
    manual_chunks = BATCH_DIR / "manual_chunks.json"
    chunks_out = BATCH_DIR / "chunks.json"
    chunks_enriched = BATCH_DIR / "chunks_enriched.json"
    chroma_dir = BATCH_DIR / "chroma_enriched" if not args.no_enrich else BATCH_DIR / "chroma"

    if not args.skip_render:
        run([sys.executable, str(BATCH_DIR / "batch_render.py"), "--manifest", str(manifest)])

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
            ]
        )

    if not args.skip_adapter and manual_chunks.is_file():
        run(
            [
                sys.executable,
                str(REPO_ROOT / "manual_chunk_adapter.py"),
                str(manual_chunks),
                str(chunks_out),
                "--images-base",
                str(BATCH_DIR),
            ]
        )

    embed_input = chunks_out
    if not args.no_enrich and chunks_out.is_file():
        run(
            [
                sys.executable,
                str(REPO_ROOT / "manual_embed_enrich.py"),
                str(chunks_out),
                str(chunks_enriched),
            ]
        )
        embed_input = chunks_enriched

    if not args.skip_embed and embed_input.is_file():
        model_path = Path(args.model)
        if not model_path.exists():
            print(f"[batch] skip embed: model not found at {model_path}", file=sys.stderr)
        else:
            retrievable = 0
            data = json.loads(embed_input.read_text(encoding="utf-8"))
            chunks = data if isinstance(data, list) else data.get("chunks", [])
            retrievable = sum(1 for c in chunks if c.get("is_retrievable", True))
            if retrievable == 0:
                print("[batch] skip embed: no retrievable chunks", file=sys.stderr)
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

    print("[batch] done", file=sys.stderr)


if __name__ == "__main__":
    main()
