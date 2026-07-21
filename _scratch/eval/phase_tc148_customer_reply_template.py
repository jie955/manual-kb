#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TC148 · customer_reply_template 字段 + answer_en 剥离 + re-chunk/embed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PROD = ROOT / "_scratch/run-tc148"
STAMP = "20260705-tc148-crt"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TARGETS = ("qa_001", "qa_002")


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_patch(groups: list[dict]) -> None:
    for g in groups:
        if g["group_id"] not in TARGETS:
            continue
        en = (g.get("answer_en") or "").strip()
        if not en:
            existing = g.get("customer_reply_templates") or []
            if existing:
                print(f"  {g['group_id']}: already patched")
            continue
        g["customer_reply_templates"] = [
            {
                "text": en,
                "lang": "en",
                "content_role": "customer_reply_template",
            }
        ]
        g["answer_en"] = ""
        print(f"  {g['group_id']}: moved {len(en)} chars -> customer_reply_templates")


def merge_chunks() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        if c["group_id"] in TARGETS:
            merged = deepcopy(c)
            old = old_by_id.get(c["chunk_id"])
            if old and old.get("images"):
                merged["images"] = deepcopy(old["images"])
                merged["has_image"] = bool(old.get("has_image") or old["images"])
            out.append(merged)
        elif c["chunk_id"] in old_by_id:
            out.append(old_by_id[c["chunk_id"]])
        else:
            out.append(c)
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    bak = PROD / f"qa_groups.json.bak-{STAMP}"
    if not bak.exists():
        shutil.copy2(PROD / "qa_groups.json", bak)

    groups = load_groups(PROD / "qa_groups.json")
    apply_patch(groups)
    (PROD / "qa_groups.json").write_text(
        json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    subprocess.run(
        [sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")],
        cwd=ROOT,
        check=True,
    )
    merge_chunks()
    subprocess.run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(MODEL),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_tc148.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/tc148_crt_post_eval.json"),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "_scratch/eval/verify_tc148_customer_reply_template.py")],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
