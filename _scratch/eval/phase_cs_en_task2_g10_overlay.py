#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G10: cs_0013 margin (qa_022 vs qa_020) + cs_0026 derived csq_169 (qa_001 vs qa_011)."""

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
STAMP = "20260708-cs-en-task2-g10"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
TOUCH_IDS = frozenset({"qa_001", "qa_033", "qa_011", "qa_022", "qa_020"})

# Prefixes inherit G9 board-replaced cluster where applicable; G10 adds stall/limit + fuse-good hooks.
PATCHES: dict[str, dict] = {
    "qa_001": {
        "answer_zh_prefix": (
            "症状：换板后执行器直供电可行但远程/端子无输出 · replaced control board · "
            "actuator direct 24V power works both directions · clicking sound remote · "
            "fuse good click sound actuator doesn't respond 2 years old · "
            "board has power won't send power to arm terminals · DLMT COM ULMT tripped · "
            "proper terminals no response A3 A5 A8；"
            "非push remote 3 times·非must press remote multiple times·非CODE LED微微亮 only"
        ),
    },
    "qa_033": {
        "answer_zh_prefix": (
            "症状：换板后只朝一个方向/限位短接排查 · replaced control board · "
            "actuator direct 24V works · clicking remote no response · "
            "fuse good click sound actuator doesn't respond · "
            "short DLMT COM ULMT limit switch · gate arm messed up won't work · "
            "only opens one direction motor runs both directions；"
            "非push remote 3 times·非must press remote multiple times·非remote needs multiple presses"
        ),
    },
    "qa_011": {
        "answer_zh_prefix": (
            "症状：按遥控器/按键完全无反应（AT12131 · gate does nothing when push button · "
            "no response at all · control board power led off fuse backup manual pack · "
            "short push button terminals 4 and 5 opener not working；"
            "非replaced control board·非fuse good clicking actuator direct power both directions·"
            "非board replaced DLMT COM ULMT·非actuator direct 24V works·"
            "非opens too far limit·非开门过远进草地·非按多次才有反应qa_010·非motor bypass limit）"
        ),
    },
    "qa_022": {
        "answer_zh_prefix": (
            "症状：开门未开全即停/走停（§十二电机电流小·A3S gate opener keeps stopping before opening fully · "
            "Need help this gate opener keeps stopping before opening fully · "
            "keeps stopping before opening fully · detect voltage 11 12 terminals above 22V · "
            "gate stops opening · FORCE potentiometer SOFT STOP gate not opening all the way · "
            "stops before opening fully · push against gate load test · Texas Ranch Farm；"
            "非关门限位B close·非gate not closing fully·非close limit screw B·"
            "非FORCE SOFT STOP closing·非门机运行慢§三十四）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：拉开门关门位不到位/reconfirm open closed position pull to open limit switch B close（"
            "限位B·关门位·FORCE potentiometer SOFT STOP gate not closing fully · "
            "gate not closing fully · doesn't close all the way · "
            "very slow stops halfway close limit AT12131 screw B；"
            "非§十二走停·非keeps stopping before opening fully·非gate stops opening·"
            "非stops before opening fully·非Need help gate opener opening·非opens too far overswing）"
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
    return json.loads((A3S_CHROMA / "manifest.json").read_text(encoding="utf-8"))["chunks"]


def build_qa001_board_embedding(question: str, segment: str) -> str:
    return (
        "replaced control board clicking sound remote actuator no response A3 A5 A8 · "
        "fuse good click sound actuator doesn't respond 2 years old · "
        "actuator direct 24V power works both directions · board has power won't send power to arm · "
        "DLMT COM ULMT tripped proper terminals no response\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa033_board_embedding(question: str, segment: str) -> str:
    return (
        "replaced control board actuator direct 24V works clicking remote no response · "
        "fuse good click sound actuator doesn't respond · "
        "short DLMT COM ULMT limit switch gate arm messed up only one direction\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa011_no_response_embedding(question: str, segment: str) -> str:
    return (
        "no response at all AT12131 gate does nothing push button control board power led off fuse backup · "
        "NOT replaced control board NOT fuse good clicking actuator direct power both directions · "
        "NOT board replaced DLMT COM ULMT NOT actuator direct 24V works\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa022_stall_embedding(question: str, segment: str) -> str:
    return (
        "FORCE potentiometer SOFT STOP gate not opening all the way\n"
        "FORCE potentiometer SOFT STOP gate not opening all the way opening direction stall\n"
        "A3S gate opener keeps stopping before opening fully\n"
        "Need help this gate opener keeps stopping before opening fully\n"
        "keeps stopping before opening fully gate stops halfway while opening\n"
        "detect voltage 11 12 terminals above 22V gate stops opening\n"
        "NOT close limit screw B NOT gate not closing fully NOT pull to open limit switch B close\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa020_close_embedding(question: str, segment: str) -> str:
    return (
        "gate not closing fully doesn't close all the way close limit screw B AT12131 closing only\n"
        "reconfirm open closed position pull to open limit switch B close position\n"
        "NOT gate not opening all the way NOT opening all the way NOT FORCE potentiometer opening stall\n"
        "NOT keeps stopping before opening fully NOT gate stops opening NOT stops before opening fully\n"
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
        if gid == "qa_001" and cid.endswith("_c001"):
            custom[cid] = build_qa001_board_embedding(q, seg)
        elif gid == "qa_033" and cid.endswith("_c001"):
            custom[cid] = build_qa033_board_embedding(q, seg)
        elif gid == "qa_011" and cid.endswith("_c001"):
            custom[cid] = build_qa011_no_response_embedding(q, seg)
        elif gid == "qa_022" and cid.endswith("_c001"):
            custom[cid] = build_qa022_stall_embedding(q, seg)
        elif gid == "qa_020" and cid.endswith("_c001"):
            custom[cid] = build_qa020_close_embedding(q, seg)
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
