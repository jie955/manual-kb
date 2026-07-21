#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 3 · Strip duplicate URLs from answer_en when links[] already present."""

from __future__ import annotations

import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from link_utils import find_urls, strip_urls_from_text

PROD = ROOT / "_scratch/run-006"
CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
EN_CHROMA = ROOT / "_scratch/run-007/chroma_captioned_en"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260709-bl-wave3-a3s-prose-strip"


def main() -> int:
    groups_path = PROD / "qa_groups.json"
    bak = PROD / f"qa_groups.json.bak-{STAMP}"
    if not bak.exists():
        shutil.copy2(groups_path, bak)

    groups = json.loads(groups_path.read_text(encoding="utf-8"))
    touched: list[str] = []
    for g in groups:
        links = g.get("links") or []
        en = g.get("answer_en") or ""
        if not links or not find_urls(en):
            continue
        cleaned = strip_urls_from_text(en)
        if cleaned != en:
            g["answer_en"] = cleaned
            touched.append(g["group_id"])
            print(f"  strip {g['group_id']}")

    if not touched:
        print("no prose strip changes")
        return 0

    groups_path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")
    by_gid = {g["group_id"]: g for g in groups}
    touch_set = set(touched)

    for chroma_dir in (CHROMA, EN_CHROMA):
        manifest_path = chroma_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        chunks = manifest["chunks"]
        ids: set[str] = set()
        for c in chunks:
            gid = c.get("group_id") or ""
            if gid not in touch_set:
                continue
            g = by_gid[gid]
            if c.get("content_en"):
                c["content_en"] = g.get("answer_en") or c["content_en"]
            if c.get("is_retrievable", True):
                ids.add(c["chunk_id"])
        manifest["chunks"] = chunks
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        import chromadb
        from sentence_transformers import SentenceTransformer

        by_id = {c["chunk_id"]: c for c in chunks if c.get("chunk_id") in ids}
        ordered = sorted(by_id)
        texts = [by_id[i]["embedding_text"] for i in ordered]
        model = SentenceTransformer(str(MODEL))
        embeddings = model.encode(texts, normalize_embeddings=True).tolist()
        client = chromadb.PersistentClient(path=str(chroma_dir))
        collection = client.get_collection("qa_troubleshooting")
        collection.update(ids=ordered, embeddings=embeddings, documents=texts)
        print(f"  updated {chroma_dir.name}: {len(ordered)} vectors")

    print(f"prose strip done: {', '.join(touched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
