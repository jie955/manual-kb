#!/usr/bin/env python3
"""Phase 1b · Full English Retrieval Index (all retrievable groups per library)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from en_representation import build_embedding_text_en, extract_en_symptom_keywords  # noqa: E402

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"

LIBRARY_CHROMA = {
    "a3s": ROOT / "_scratch/run-007/chroma_captioned",
    "ad5s": ROOT / "_scratch/run-ad5s/chroma_captioned",
    "tc148": ROOT / "_scratch/run-tc148/chroma_captioned",
}

LIBRARY_OUT = {
    "a3s": ROOT / "_scratch/run-007/chroma_captioned_en",
    "ad5s": ROOT / "_scratch/run-ad5s/chroma_captioned_en",
    "tc148": ROOT / "_scratch/run-tc148/chroma_captioned_en",
}

# Reuse pilot patches from phase_1a
from phase_1a_pilot_en_index import GROUP_ANSWER_EN_PATCH, patch_group_en_from_parent  # noqa: E402


def build_full_manifest(src_dir: Path, lib_id: str) -> list[dict]:
    manifest = json.loads((src_dir / "manifest.json").read_text(encoding="utf-8"))
    chunks = deepcopy(manifest["chunks"])
    chunk_by_id = {c["chunk_id"]: c for c in chunks}

    for c in chunks:
        if not c.get("is_retrievable", True):
            continue
        gid = c.get("group_id") or ""
        question = c.get("question") or ""
        content_en = (c.get("content_en") or "").strip()
        if not content_en:
            content_en = patch_group_en_from_parent(chunk_by_id, gid) or ""
            if content_en:
                c["content_en"] = content_en
        kw = extract_en_symptom_keywords(question)
        en_embed = build_embedding_text_en(question, content_en, symptom_keywords=kw)
        if not en_embed.strip():
            print(f"WARN {lib_id} {gid} {c['chunk_id']}: empty EN embed", file=sys.stderr)
            continue
        c["embedding_text"] = en_embed

    return chunks


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Phase 1b full EN index")
    parser.add_argument("--libs", nargs="*", choices=sorted(LIBRARY_CHROMA), default=sorted(LIBRARY_CHROMA))
    args = parser.parse_args()

    summary: list[dict] = []
    for lib_id in args.libs:
        src = LIBRARY_CHROMA[lib_id]
        dst = LIBRARY_OUT[lib_id]
        if not (src / "manifest.json").is_file():
            print(f"SKIP missing {src}", file=sys.stderr)
            continue
        chunks = build_full_manifest(src, lib_id)
        retrievable = [c for c in chunks if c.get("is_retrievable", True) and c.get("embedding_text")]
        tmp = dst.parent / "full_en_chunks.json"
        tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        if dst.exists():
            shutil.rmtree(dst)
        cmd = [sys.executable, str(ROOT / "embed_ingest_local.py"), str(tmp), str(dst), "--model", str(MODEL)]
        print(f"=== {lib_id} full EN ({len(retrievable)} retrievable) ===")
        subprocess.run(cmd, check=True, cwd=str(ROOT))
        summary.append(
            {
                "library": lib_id,
                "retrievable_chunks": len(retrievable),
                "chroma_dir": str(dst.relative_to(ROOT)).replace("\\", "/"),
            }
        )

    out = ROOT / "_scratch/eval/phase_1b_full_en_index.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
