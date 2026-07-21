#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G7b: #1 push-button derivatives + #2 motor tail (qa_011 vs qa_019 boundary)."""

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
STAMP = "20260707-cs-en-task2-g7b"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
TOUCH_IDS = frozenset({"qa_001", "qa_010", "qa_011", "qa_019", "qa_033", "qa_035"})

PATCHES: dict[str, dict] = {
    "qa_011": {
        "question": (
            "按遥控器/按键完全无反应 No Response At All · AT12131 Push Button Does Nothing · "
            "Gate Does Nothing When I Push the Button · Control Board Power LED Off Fuse Backup"
        ),
        "answer_zh_prefix": (
            "症状：按遥控器/按键完全无反应（AT12131 · gate does nothing when push button · "
            "no response at all · control board power led off fuse backup manual pack · "
            "short push button terminals 4 and 5 opener not working；"
            "非opens too far limit·非开门过远进草地·非按多次才有反应qa_010·非motor bypass limit）"
        ),
    },
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门开位停不下来/开门过远进草地（限位B开位·推开门·screw B·AT12131；"
            "非gate does nothing when push button·非no response at all·非power led off fuse·"
            "非motor won't function bypass limit·非§十二走停）"
        ),
    },
    "qa_010": {
        "answer_zh_prefix": (
            "症状：遥控要按多次才有反应（push remote button 3 times · intermittent click no movement · "
            "control board clicks but gate doesn't move intermittent；"
            "非完全不工作·非按一次完全无反应qa_011·非opens too far）"
        ),
    },
    "qa_035": {
        "answer_zh_prefix": (
            "症状：开关门中途走停或反弹（§八遇阻红外·"
            "非motor won't function · 非zero power to motor · 非lock still unlocks ET24 · "
            "非worked four days · 非opens too far into grass limit · "
            "非bypassed motor limit switch jumping wires）"
        ),
    },
    "qa_033": {
        "answer_zh_prefix": (
            "症状：机臂故障/限位短接/电机排查（bypassed motor limit switch jumping wires · "
            "short DLMT COM ULMT · gate arm messed up · only opens one direction；"
            "非gate does nothing push button·非opens too far limit B·非motor won't function lock unlocks only）"
        ),
    },
    "qa_001": {
        "answer_zh_prefix": (
            "症状：完全不工作/无反应/电机无输出（motor won't function · zero power to motor · "
            "lock still unlocks · worked four days ET24 · ET24 lock unlocks but gate won't move；"
            "非CODE LED微微亮·非push remote 3 times·非opens too far limit·"
            "非control board power led off fuse only）"
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


def build_qa011_embedding(question: str, segment: str) -> str:
    return (
        "AT12131 gate does nothing when I push the button · no response at all push button remote · "
        "control board power led off fuse backup manual pack · "
        "short push button terminals 4 and 5 opener not working keypad remote no response\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa001_motor_embedding(question: str, segment: str) -> str:
    return (
        "ET24 lock unlocks but gate opener won't move · bypassed motor limit switch jumping wires still nothing · "
        "motor won't function zero power worked four days\n"
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
        if cid == "qa_011_c001":
            custom[cid] = build_qa011_embedding(q, seg)
        elif cid == "qa_001_c001":
            custom[cid] = build_qa001_motor_embedding(q, seg)
        elif cid == "qa_010_c001":
            custom[cid] = (
                "control board clicks but gate doesn't move intermittent · "
                "Topens gate opener remote intermittent click no movement\n"
                f"[问题] {q}\n[子场景：症状]\n{seg}"
            )
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


if __name__ == "__main__":
    pipeline()
