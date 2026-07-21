#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G5: A3S #17 A5131 arm/warranty cluster + qa_001 embed scope fix."""

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
STAMP = "20260707-cs-en-task2-g5"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
A3S_TOUCH = frozenset({"qa_001", "qa_033"})

PATCHES: dict[str, dict] = {
    "qa_033": {
        "question": (
            "只朝一个方向 Only Opens/Closes One Direction · "
            "Gate Arm Messed Up Again · Won't Work At All · Arm Replacement Warranty"
        ),
        "answer_zh_prefix": (
            "症状：机臂故障/只朝一个方向/限位短接（gate arm messed up again · doesn't work at all · "
            "warranty arm replacement · A5131 · short DLMT COM ULMT limit switch · DIP switch 3 OFF · "
            "only opens one direction · motor runs both directions limit defective；"
            "非开门过远opens too far·非完全不亮CODE LED）"
        ),
    },
    "qa_001": {
        "question": (
            "控制板灯不亮（适配器）No Led On the Control Board · "
            "Batteries and AC Adapter Nothing Works · Board Has Power Arms Won't Move"
        ),
        "answer_zh_prefix": (
            "症状：完全不工作/无反应（batteries and AC adapter · not getting anything to work · "
            "nothing works · board has power won't send power to arm terminals · "
            "arms won't open or close · lights blink click；"
            "非CODE LED微微亮·非太阳能板单独故障·非gate arm warranty replacement）"
        ),
    },
}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_known_prefix(zh: str, prefixes: tuple[str, ...]) -> str:
    for old in prefixes:
        if zh.startswith(old):
            return zh[len(old) :].lstrip("\n")
    return zh


def apply_patches(groups: list[dict]) -> list[dict]:
    prefixes = tuple(p["answer_zh_prefix"] for p in PATCHES.values() if "answer_zh_prefix" in p)
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in PATCHES:
            continue
        p = PATCHES[gid]
        if "question" in p:
            g["question"] = p["question"]
        if "answer_zh_prefix" in p:
            zh = strip_known_prefix((g.get("answer_zh") or "").strip(), prefixes)
            prefix = p["answer_zh_prefix"]
            if not zh.startswith(prefix):
                g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}")
    return out


def backup() -> None:
    chroma_dst = A3S_PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists() and A3S_CHROMA.is_dir():
        shutil.copytree(A3S_CHROMA, chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        src = A3S_PROD / name
        bak = A3S_PROD / f"{name}.bak-{STAMP}"
        if src.is_file() and not bak.exists():
            shutil.copy2(src, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks() -> list[dict]:
    bak = A3S_PROD / f"chroma_captioned.bak-{STAMP}"
    base = bak if (bak / "manifest.json").is_file() else A3S_CHROMA
    return json.loads((base / "manifest.json").read_text(encoding="utf-8"))["chunks"]


def build_qa033_embedding(question: str, segment: str) -> str:
    return (
        "A5131 gate arm messed up again same as last replacement won't work at all warranty · "
        "gate opener doesn't work at all arm replacement limit switch DLMT COM ULMT short jumper · "
        "DIP switch 3 OFF disconnect accessories only opens one direction\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa001_symptom_embedding(question: str, segment: str) -> str:
    return (
        "batteries and AC adapter installed not getting anything to work nothing works · "
        "A5 A8 gate opener batteries AC adapter · "
        "motherboard has power arms won't open or close click noise · "
        "board has power will not send power to arm terminals\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def custom_embeddings(new_chunks: list[dict], groups: list[dict]) -> dict[str, str]:
    custom: dict[str, str] = {}
    g033 = next(g for g in groups if g["group_id"] == "qa_033")
    g001 = next(g for g in groups if g["group_id"] == "qa_001")
    for c in new_chunks:
        cid = c.get("chunk_id") or ""
        if cid == "qa_033_c001":
            custom[cid] = build_qa033_embedding(g033.get("question") or "", c.get("content_zh") or "")
        elif cid == "qa_001_c001":
            custom[cid] = build_qa001_symptom_embedding(g001.get("question") or "", c.get("content_zh") or "")
    return custom


def _merge_chunk_media(new_chunk: dict, old_by_id: dict[str, dict]) -> dict:
    merged = deepcopy(new_chunk)
    old = old_by_id.get(merged["chunk_id"])
    if not old:
        return merged
    if old.get("images"):
        merged["images"] = deepcopy(old["images"])
        merged["has_image"] = bool(old.get("has_image") or old["images"])
    if old.get("links") and not merged.get("links"):
        merged["links"] = deepcopy(old["links"])
        merged["has_links"] = bool(old.get("has_links") or old["links"])
    if old.get("content_en") and not merged.get("content_en"):
        merged["content_en"] = old["content_en"]
    return merged


def merge_captioned_chunks(
    new_chunks: list[dict],
    old_chunks: list[dict],
    custom_embedding: dict[str, str],
) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    old_by_gid: dict[str, list[dict]] = {}
    for old in old_chunks:
        old_by_gid.setdefault(old["group_id"], []).append(old)

    for c in new_chunks:
        gid = c["group_id"]
        if gid in emitted:
            continue
        if gid not in A3S_TOUCH:
            out.extend(deepcopy(old_by_gid.get(gid, [])))
            emitted.add(gid)
            continue
        old_by_id = {x["chunk_id"]: x for x in old_by_gid.get(gid, [])}
        for nc in new_chunks:
            if nc["group_id"] != gid:
                continue
            merged = _merge_chunk_media(nc, old_by_id)
            cid = merged.get("chunk_id") or ""
            if cid in custom_embedding:
                merged["embedding_text"] = custom_embedding[cid]
            out.append(merged)
        emitted.add(gid)
    return out


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = apply_patches(load_groups(A3S_PROD / "qa_groups.json"))
    save_groups(A3S_PROD / "qa_groups.json", groups)
    chunks_out = A3S_PROD / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(A3S_PROD / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks, custom_embeddings(new_chunks, groups))
    cap_path = A3S_PROD / "chunks_captioned.json"
    cap_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(cap_path),
            str(A3S_CHROMA),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(A3S_CHROMA),
            "--eval",
            "eval_queries.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/cs_en_task2_zh_regression.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
