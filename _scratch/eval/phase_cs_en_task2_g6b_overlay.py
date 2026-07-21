#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G6b: #12 oracle companion — limit open/close Chinese split + q23/q25 regression."""

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
STAMP = "20260707-cs-en-task2-g6b"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
TOUCH_IDS = frozenset({"qa_017", "qa_018", "qa_019", "qa_020", "qa_021", "qa_034"})

PATCHES: dict[str, dict] = {
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门开位停不下来/推开门开门不限位/开门过远进草地（限位B开位·推开门·screw B·"
            "adjusting limit switch B does nothing · opens too far into grass · overswings · AT12131；"
            "非推开门关不到位·非§十二走停·非stops before opening fully·非gate arm warranty·"
            "非push button does nothing）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：拉开门关门位不到位/关门不限位/关门慢中途停（限位B·关门位·"
            "doesn't close all the way · very slow stops halfway · screw B faulty · AT12131；"
            "非推开门开位停不下来·非推开门开位不限位·非开门过远进草地·"
            "非§十二走停·非gate arm messed up）"
        ),
    },
    "qa_021": {
        "answer_zh_prefix": (
            "症状：推开门关不到位/推开门关门位不限位（限位A·关门位·magnet；"
            "非推开门开位停不下来·非推开门开位不限位·非开门过远进草地·"
            "非screw B开位·非stops before opening fully）"
        ),
    },
    "qa_017": {
        "answer_zh_prefix": (
            "症状：推开门开到位后反弹（§十开反弹·推开门·限位B远端；"
            "非推开门开位停不下来·非推开门开位不限位·非开门过远进草地不限位）"
        ),
    },
    "qa_018": {
        "answer_zh_prefix": (
            "症状：拉开门开门位置不对/拉开门开位不限位（限位A·开位；"
            "非推开门关不到位·非推开门开位不限位·非关门限位B·"
            "非opens too far into grass screw B·非stops before opening fully）"
        ),
    },
    "qa_034": {
        "answer_zh_prefix": (
            "症状：运行慢/11#12#电压压降/调FORCE与SOFT STOP（gate operates slowly · voltage above 22V；"
            "非§十二走停推阻·非stops before opening fully·非opens too far into grass limit B·"
            "非推开门开位不限位·非motor won't function zero power ET24·非auto close reverses）"
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


def build_limit_open_embedding(question: str, segment: str) -> str:
    return (
        "推开门 开门停不下来 推开门开位不限位 · "
        "AT12131 gate opens too far into grass limit switch B does nothing adjusting screw B overswings · "
        "opens too far does not stop at desired location · push to open limit B open position\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_limit_close_embedding(question: str, segment: str) -> str:
    return (
        "拉开门 关门不限位 关门慢中途停 · "
        "gate closes very slow stops halfway doesn't close all the way AT12131 limit switch B close · "
        "screw B faulty contractor adjusting limit\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def custom_embeddings(new_chunks: list[dict], groups: list[dict]) -> dict[str, str]:
    custom: dict[str, str] = {}
    by_gid = {g["group_id"]: g for g in groups}
    for c in new_chunks:
        cid = c.get("chunk_id") or ""
        gid = c.get("group_id") or ""
        q = by_gid.get(gid, {}).get("question") or ""
        seg = c.get("content_zh") or ""
        if cid == "qa_019_c001":
            custom[cid] = build_limit_open_embedding(q, seg)
        elif cid == "qa_020_c001":
            custom[cid] = build_limit_close_embedding(q, seg)
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
        if gid not in TOUCH_IDS:
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
