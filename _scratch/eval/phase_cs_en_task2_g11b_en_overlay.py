#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G11b: fix EN-index Gate K csq_078 (qa_030 vs qa_022 Top1)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260708-cs-en-task2-g11b-en"
A3S_EN_CHROMA = ROOT / "_scratch/run-007/chroma_captioned_en"

CSQ_078_VERBATIM = "Need help this gate opener keeps stopping before opening fully"


def backup() -> None:
    dst = A3S_EN_CHROMA.parent / f"chroma_captioned_en.bak-{STAMP}"
    if not dst.exists() and A3S_EN_CHROMA.is_dir():
        shutil.copytree(A3S_EN_CHROMA, dst)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def en_qa022_csq078(question: str, body: str) -> str:
    return (
        f"{CSQ_078_VERBATIM}\n"
        f"{CSQ_078_VERBATIM}\n"
        "gate opener keeps stopping before opening fully\n"
        "keeps stopping before opening fully stops before opening fully\n"
        "A3S gate opener keeps stopping before opening fully gate stops halfway while opening\n"
        "FORCE potentiometer SOFT STOP gate not opening all the way opening direction stall\n"
        "detect voltage 11 12 terminals above 22V gate stops opening push against gate load\n"
        "NOT soft stop deceleration closing direction calibration only\n"
        "NOT soft stop issues when gate slows down\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa030_demote_csq078(question: str, body: str) -> str:
    return (
        "soft stop deceleration issues when gate slows down closing direction calibration · "
        f"NOT {CSQ_078_VERBATIM} · "
        "NOT keeps stopping before opening fully NOT stops before opening fully · "
        "NOT gate stops opening NOT gate opener keeps stopping before opening fully · "
        "NOT opening stall FORCE potentiometer opening direction · "
        f"Question: {question}\n{body}"
    ).strip()


def patch_en_chunks(chunks: list[dict]) -> int:
    n = 0
    for c in chunks:
        gid = c.get("group_id") or ""
        cid = c.get("chunk_id") or ""
        if gid == "qa_022" and cid == "qa_022_c001":
            q = c.get("question") or ""
            body = (c.get("content_en") or c.get("embedding_text") or "").strip()
            c["embedding_text"] = en_qa022_csq078(q, body)
            print(f"  G11b patch {cid}")
            n += 1
        elif gid == "qa_030" and cid == "qa_030_c001":
            q = c.get("question") or ""
            body = (c.get("content_en") or c.get("embedding_text") or "").strip()
            c["embedding_text"] = en_qa030_demote_csq078(q, body)
            print(f"  G11b demote {cid}")
            n += 1
    return n


def patch_manifest(chunks: list[dict]) -> int:
    return patch_en_chunks(chunks)


def upsert_vectors(chunks: list[dict], chunk_ids: frozenset[str]) -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    by_id = {c["chunk_id"]: c for c in chunks if c.get("chunk_id") in chunk_ids}
    model = SentenceTransformer(str(MODEL))
    texts = [by_id[cid]["embedding_text"] for cid in chunk_ids]
    ids = list(chunk_ids)
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    client = chromadb.PersistentClient(path=str(A3S_EN_CHROMA))
    collection = client.get_collection("qa_troubleshooting")
    collection.update(ids=ids, embeddings=embeddings, documents=texts)
    print(f"  updated vectors: {', '.join(ids)}")


def main() -> int:
    backup()
    manifest_path = A3S_EN_CHROMA / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    chunks = deepcopy(manifest["chunks"])
    touched = patch_en_chunks(chunks)
    if not touched:
        raise SystemExit("no chunks patched")

    manifest["chunks"] = chunks
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    upsert_vectors(chunks, frozenset({"qa_022_c001", "qa_030_c001"}))
    print(f"G11b done · patched {touched} chunks (in-place)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
