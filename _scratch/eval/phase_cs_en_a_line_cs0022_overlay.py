#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-line overlay · cs_0022 (#22 A5132 dual swing) → ad5s §九 qa_040 (in-place)."""

from __future__ import annotations

import json
import shutil
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from en_representation import append_email_verbatim_to_embedding

AD5S_PROD = ROOT / "_scratch/run-ad5s"
AD5S_CHROMA = AD5S_PROD / "chroma_captioned"
AD5S_EN_CHROMA = AD5S_PROD / "chroma_captioned_en"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260708-cs-en-a-line-cs0022"
GROUP_ID = "qa_040"

CS_0022_VERBATIM = (
    "Just recently my gate started acting differently. The left panel - furthest from the "
    "controller - seems to open and reaches full open then immediately starts closing about "
    "4 feet. there use to be a pause which it is not doing any more. This stops the right "
    "panel from closing as well. When I press the remote button it tries to open again and "
    "then after a pause only closes 4 feet. My gate is a pull to open."
)

EMBED_PREFIX = (
    "left panel furthest from controller opens fully then immediately starts closing about 4 feet · "
    "safety reverse no photocell obstruction when fully open · pull to open dual swing A5132 · "
    "left gate stopped before open position then closed itself · stops right panel from closing"
)


def merge_email_examples(existing: list | None, new_rows: list[dict]) -> list[dict]:
    out = list(existing or [])
    seen = {(r.get("scenario_id"), r.get("verbatim")) for r in out}
    for row in new_rows:
        key = (row.get("scenario_id"), row.get("verbatim"))
        if key not in seen:
            out.append(row)
            seen.add(key)
    return out


def ex(scenario_id: str, verbatim: str, **kw) -> dict:
    row = {"scenario_id": scenario_id, "verbatim": verbatim, "source": kw.get("source", "")}
    if kw.get("mail_num") is not None:
        row["mail_num"] = kw["mail_num"]
    if kw.get("tags"):
        row["symptom_tags"] = kw["tags"]
    return row


def new_example() -> dict:
    return ex(
        "cs_0022",
        CS_0022_VERBATIM,
        mail_num=22,
        source="samples/customer-service-emails/0022-a5132-opens-then-recloses-resolved.md",
        tags=["dual_swing", "safety_reverse", "pull_open", "left_panel"],
    )


def patch_target(target: dict) -> None:
    examples = merge_email_examples(target.get("email_examples"), [new_example()])
    target["email_examples"] = examples
    base = target.get("embedding_text") or ""
    if EMBED_PREFIX not in base:
        base = f"{EMBED_PREFIX}\n{base}".strip()
    target["embedding_text"] = append_email_verbatim_to_embedding(base, examples)


def upsert_chroma(chroma_dir: Path, chunk_id: str, embedding_text: str) -> None:
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(str(MODEL))
    emb = model.encode([embedding_text], normalize_embeddings=True).tolist()
    client = chromadb.PersistentClient(path=str(chroma_dir))
    collection = client.get_collection("qa_troubleshooting")
    collection.update(ids=[chunk_id], embeddings=emb, documents=[embedding_text])


def main() -> int:
    groups_path = AD5S_PROD / "qa_groups.json"
    bak = AD5S_PROD / f"qa_groups.json.bak-{STAMP}"
    if not bak.exists():
        shutil.copy2(groups_path, bak)

    groups = json.loads(groups_path.read_text(encoding="utf-8"))
    for g in groups:
        if g["group_id"] == GROUP_ID:
            g["email_examples"] = merge_email_examples(g.get("email_examples"), [new_example()])
            print(f"  qa_groups {GROUP_ID} examples={len(g.get('email_examples') or [])}")
            break
    else:
        raise SystemExit(f"{GROUP_ID} not found")
    groups_path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")

    chunk_id = None
    for chroma_dir in (AD5S_CHROMA, AD5S_EN_CHROMA):
        manifest_path = chroma_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        chunks = manifest["chunks"]
        target = None
        for c in chunks:
            if c.get("group_id") == GROUP_ID and c.get("is_retrievable"):
                if str(c.get("chunk_id", "")).endswith("_c001"):
                    target = c
                    break
                target = target or c
        if not target:
            raise SystemExit(f"no chunk for {GROUP_ID} in {chroma_dir}")
        patch_target(target)
        chunk_id = target["chunk_id"]
        manifest["chunks"] = chunks
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        upsert_chroma(chroma_dir, chunk_id, target["embedding_text"])
        print(f"  updated {chroma_dir.name} {chunk_id}")

    print("cs_0022 a-line overlay done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
