#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-04 AD5S：简单档 links（qa_003/010/030）+ qa_023 parallel branch overlay → prod。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from branch_utils import attach_qa_023_structure
from link_utils import apply_simple_tier_links, find_urls, infer_link_type, strip_urls_from_text
from negotiation_utils import negotiation_offers_from_text

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-v1-04"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_003", "qa_010", "qa_023", "qa_030"})


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def transform_qa_023(g: dict) -> None:
    g.setdefault("negotiation_offers", [])
    g.setdefault("structure_warnings", [])
    g.setdefault("links", [])
    for field, lang in (("answer_zh", "zh"), ("answer_en", "en")):
        cleaned, offers = negotiation_offers_from_text(g[field], lang)
        g[field] = cleaned
        g["negotiation_offers"].extend(offers)
    for url in find_urls(g.get("answer_en") or ""):
        if infer_link_type(url) == "purchase_link":
            g["links"].append(
                {"url": url, "label": url, "lang": "en", "link_type": "purchase_link"}
            )
    g["answer_en"] = strip_urls_from_text(g.get("answer_en") or "")
    attach_qa_023_structure(g)
    print(f"  qa_023: ladder steps={len(g.get('troubleshooting_ladder') or [])}")


def transform_group(g: dict) -> dict:
    out = deepcopy(g)
    gid = out["group_id"]
    if gid == "qa_023":
        transform_qa_023(out)
    elif gid in TOUCH_IDS:
        out.setdefault("links", [])
        if apply_simple_tier_links(out):
            print(f"  {gid}: links={len(out.get('links') or [])}")
    return out


def apply_overlay(groups: list[dict]) -> list[dict]:
    return [transform_group(g) if g["group_id"] in TOUCH_IDS else g for g in groups]


def backup() -> None:
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(PROD / "chroma_captioned", chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        bak = PROD / f"{name}.bak-{STAMP}"
        if not bak.exists():
            shutil.copy2(PROD / name, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def merge_chunks_captioned() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_gid = {c["group_id"]: c for c in old_cap if c.get("is_retrievable", True)}
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        gid = c["group_id"]
        if gid in TOUCH_IDS:
            merged = deepcopy(c)
            old = old_by_gid.get(gid)
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


def pipeline() -> None:
    backup()
    groups = apply_overlay(load_groups(PROD / "qa_groups.json"))
    save_groups(PROD / "qa_groups.json", groups)
    run([sys.executable, str(ROOT / "_scratch/eval/verify_qa_023_acceptance.py")])
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")])
    merge_chunks_captioned()
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_04_ad5s_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
