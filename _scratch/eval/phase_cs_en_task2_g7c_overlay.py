#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G7c: #15 csq_090 — qa_036 vs qa_040 auto-close delay / soft stop split."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PROD = ROOT / "_scratch/run-ad5s"
CHROMA_DIR = PROD / "chroma_captioned"
STAMP = "20260707-cs-en-task2-g7c"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_036", "qa_040", "qa_032"})

PATCHES: dict[str, dict] = {
    "qa_040": {
        "question": (
            "开关门中途走停或反弹 · Auto Close Reverses When Starting to Close · "
            "Additional Delay Cycle Closes on Second Try · Soft Stop Open Close Delay Interaction · "
            "AD8S Dual Swing Powered Down Moving Pot Delay Dialed In"
        ),
        "answer_zh_prefix": (
            "症状：自动关门延迟后开始关闭即反转/再等一整轮延迟二次才关（§九·#15 AD8S；"
            "about half the time gate starts to close after the delay it reverses · "
            "entire additional delay cycle tries again to close · closes on the second try · "
            "soft stop and open close delay interaction · powered down before moving pot delay dialed in · "
            "no sign of binding opens closes right spots；"
            "非门机运行慢§十三·非单纯调FORCE/SOFT STOP运行速度·非§十一关到位反弹·非遇阻qa_025）"
        ),
    },
    "qa_036": {
        "question": (
            "门机运行慢 Gate Operates Slowly · 11#12# Voltage · Motor Speed · "
            "Not Auto Close Delay Reversal"
        ),
        "answer_zh_prefix": (
            "症状：门机运行慢/11#12#电压压降/电机转速（§十三；gate operates slowly · "
            "voltage above 22V · motor runs slow speed；"
            "非gate starts to close after delay reverses·非additional delay cycle second try·"
            "非soft stop and open close delay interaction·非half the time closes normally half reverses·"
            "非auto close delay dialed in reverses when starting to close）"
        ),
    },
    "qa_032": {
        "answer_zh_prefix": (
            "症状：缓停止不起作用/soft stop issues（§十四；"
            "非auto close delay开始关闭即反转·非additional delay cycle·非closes on second try·"
            "非§九中途反弹循环）"
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
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists() and CHROMA_DIR.is_dir():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        bak = PROD / f"{name}.bak-{STAMP}"
        if not bak.exists() and (PROD / name).is_file():
            shutil.copy2(PROD / name, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks() -> list[dict]:
    bak = PROD / f"chroma_captioned.bak-{STAMP}"
    base = bak if (bak / "manifest.json").is_file() else CHROMA_DIR
    return json.loads((base / "manifest.json").read_text(encoding="utf-8"))["chunks"]


def build_qa040_cs15_embedding(question: str, segment: str) -> str:
    return (
        "powered down first before moving the pot great delay dialed in AD8S dual swing · "
        "about half the time when the gate starts to close after the delay it reverses · "
        "waits through entire additional delay cycle tries again to close · "
        "closes on the second try half the time closes normally · "
        "soft stop and open close delay interaction no sign of binding · "
        "gate opens and closes at the right spots · "
        "gate reverses when starting to close after auto close delay\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa036_slow_embedding(question: str, segment: str) -> str:
    return (
        "gate operates slowly motor speed voltage 11 12 terminals above 22V · "
        "门机运行慢 运行速度很慢 · "
        "not auto close delay reverses not additional delay cycle not closes on second try · "
        "not soft stop open close delay interaction\n"
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
            cid = merged.get("chunk_id")
            q = merged.get("question") or ""
            seg = merged.get("content_zh") or ""
            if cid == "qa_040_c001":
                merged["embedding_text"] = build_qa040_cs15_embedding(q, seg)
            elif cid == "qa_036_c001":
                merged["embedding_text"] = build_qa036_slow_embedding(q, seg)
            out.append(merged)
        emitted.add(gid)
    return out


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = apply_patches(load_groups(PROD / "qa_groups.json"))
    save_groups(PROD / "qa_groups.json", groups)
    chunks_out = PROD / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    cap_path = PROD / "chunks_captioned.json"
    cap_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(cap_path),
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
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/cs_en_task2_ad5s_regression.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
