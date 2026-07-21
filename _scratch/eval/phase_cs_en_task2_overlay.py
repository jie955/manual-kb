#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G1: A3S qa_022/qa_034/qa_025 EN-retrieval symptom enrich + re-embed."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

GROUPS_DIR = ROOT / "_scratch/run-006"
CHROMA_DIR = ROOT / "_scratch/run-007/chroma_captioned"
STAMP = "20260707-cs-en-task2-g1"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_022", "qa_025", "qa_034", "qa_018", "qa_020"})

PATCHES: dict[str, dict] = {
    "qa_022": {
        "question": (
            "手动反推排查 · Stops Before Opening Fully · Gate Stops Halfway While Opening · "
            "Push Against Gate Load Test"
        ),
        "answer_zh_prefix": (
            "症状：开门未开全即停/走停（§十二电机电流小·推阻加负载排查；"
            "stops before opening fully · stopping before fully open；"
            "非开门限位A开位·非§八中途走停）"
        ),
    },
    "qa_034": {
        "question": (
            "门机运行慢 · 11#12# Voltage · FORCE · SOFT STOP · Gate Operates Slowly"
        ),
        "answer_zh_prefix": (
            "症状：运行慢/11#12#电压压降/调FORCE与SOFT STOP（"
            "gate operates slowly · voltage above 22V；"
            "非§十二走停推阻·非stops before opening fully·非限位A开门位·"
            "非auto close reverses when starting to close）"
        ),
    },
    "qa_025": {
        "answer_zh_prefix": (
            "症状：电机电流过小导致走停/遇阻（§十二；非开门未开全限位·非auto close反弹）"
        ),
    },
    "qa_018": {
        "answer_zh_prefix": (
            "症状：拉开门开门位置不对或开门不限位（限位A·开位；"
            "非关门限位B·非推开门开位·"
            "非开门未开全走停·非stops before opening fully·非gate stops halfway while opening）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：拉开门关门位置不对或关门不限位（限位B·关门位；"
            "非开门未开全走停·非stops before opening fully·非gate stops halfway while opening·"
            "非§十二推阻加负载）"
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
    chroma_dst = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    groups_path = GROUPS_DIR / "qa_groups.json"
    bak_groups = GROUPS_DIR / f"qa_groups.json.bak-{STAMP}"
    if not bak_groups.exists():
        shutil.copy2(groups_path, bak_groups)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks() -> list[dict]:
    bak = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
    base = bak if (bak / "manifest.json").is_file() else CHROMA_DIR
    data = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    return data["chunks"]


def build_qa022_symptom_embedding(question: str, segment: str) -> str:
    return (
        "keeps stopping before opening fully · gate opener stops before opening fully · "
        "gate stops halfway while opening · stopping before fully open · "
        "motor current too low stall push against gate load test\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


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


def merge_captioned_chunks(new_chunks: list[dict], old_chunks: list[dict]) -> list[dict]:
    out: list[dict] = []
    emitted: set[str] = set()
    old_by_gid: dict[str, list[dict]] = {}
    for old in old_chunks:
        old_by_gid.setdefault(old["group_id"], []).append(old)

    for c in new_chunks:
        gid = c["group_id"]
        if gid in emitted:
            continue
        if gid not in TOUCH_IDS:
            out.extend(deepcopy(old_by_gid.get(gid, [])))
            emitted.add(gid)
            continue
        old_by_id = {x["chunk_id"]: x for x in old_by_gid.get(gid, [])}
        for nc in new_chunks:
            if nc["group_id"] != gid:
                continue
            merged = _merge_chunk_media(nc, old_by_id)
            if merged.get("chunk_id") == "qa_022_c001":
                merged["embedding_text"] = build_qa022_symptom_embedding(
                    merged.get("question") or "",
                    merged.get("content_zh") or "",
                )
            out.append(merged)
        emitted.add(gid)
    return out


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = apply_patches(load_groups(GROUPS_DIR / "qa_groups.json"))
    save_groups(GROUPS_DIR / "qa_groups.json", groups)
    chunks_out = GROUPS_DIR / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(GROUPS_DIR / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    chunks_captioned = GROUPS_DIR / "chunks_captioned.json"
    chunks_captioned.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(chunks_captioned),
            str(CHROMA_DIR),
            "--model",
            str(MODEL),
        ]
    )
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA_DIR),
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
