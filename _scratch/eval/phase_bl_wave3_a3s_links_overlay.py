#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wave 3 · A3S qa_023/qa_024 Amazon purchase links → links[] (in-place)."""

from __future__ import annotations

import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from link_utils import find_urls, infer_link_type, normalize_links, strip_urls_from_text

PROD = ROOT / "_scratch/run-006"
CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
EN_CHROMA = ROOT / "_scratch/run-007/chroma_captioned_en"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260708-bl-wave3-a3s-links"
TOUCH = frozenset({"qa_023", "qa_024"})


def apply_purchase_links(group: dict) -> bool:
    en = group.get("answer_en") or ""
    urls = find_urls(en)
    if not urls:
        return False
    links = normalize_links(group.get("links") or [])
    existing = {x["url"] for x in links}
    for url in urls:
        if url in existing:
            continue
        label = "Resistor" if "B08HYZV3DW" in url else "Diode" if "B01HMSR2T4" in url else url
        links.append(
            {"url": url, "label": label, "lang": "en", "link_type": infer_link_type(url)}
        )
        existing.add(url)
    cleaned = strip_urls_from_text(en)
    changed = cleaned != en or links != normalize_links(group.get("links") or [])
    group["links"] = links
    group["answer_en"] = cleaned
    return changed


def upsert_chroma(chroma_dir: Path, chunks: list[dict], chunk_ids: set[str]) -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    by_id = {c["chunk_id"]: c for c in chunks if c.get("chunk_id") in chunk_ids}
    ids = sorted(by_id)
    texts = [by_id[i]["embedding_text"] for i in ids]
    model = SentenceTransformer(str(MODEL))
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    client = chromadb.PersistentClient(path=str(chroma_dir))
    collection = client.get_collection("qa_troubleshooting")
    collection.update(ids=ids, embeddings=embeddings, documents=texts)


def main() -> int:
    groups_path = PROD / "qa_groups.json"
    bak = PROD / f"qa_groups.json.bak-{STAMP}"
    if not bak.exists():
        shutil.copy2(groups_path, bak)

    groups = json.loads(groups_path.read_text(encoding="utf-8"))
    touched: list[str] = []
    for g in groups:
        if g["group_id"] in TOUCH and apply_purchase_links(g):
            touched.append(g["group_id"])
            print(f"  links {g['group_id']}: {len(g.get('links') or [])}")

    if not touched:
        print("no link changes")
        return 0

    groups_path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")
    by_gid = {g["group_id"]: g for g in groups}

    for chroma_dir in (CHROMA, EN_CHROMA):
        manifest_path = chroma_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        chunks = manifest["chunks"]
        ids: set[str] = set()
        for c in chunks:
            gid = c.get("group_id") or ""
            if gid not in TOUCH:
                continue
            g = by_gid[gid]
            c["links"] = deepcopy(g.get("links") or [])
            if c.get("content_en"):
                c["content_en"] = g.get("answer_en") or c["content_en"]
            if c.get("is_retrievable", True):
                ids.add(c["chunk_id"])
        manifest["chunks"] = chunks
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        upsert_chroma(chroma_dir, chunks, ids)
        print(f"  updated {chroma_dir.name}: {len(ids)} vectors")

    print(f"wave3 links overlay done: {', '.join(touched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
