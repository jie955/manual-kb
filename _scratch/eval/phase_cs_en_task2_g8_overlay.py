#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G8: q23/q23b + #12/#13 derived tail (qa_017 vs qa_019, qa_034 vs qa_022)."""

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
STAMP = "20260707-cs-en-task2-g8"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
TOUCH_IDS = frozenset({"qa_015", "qa_017", "qa_019", "qa_020", "qa_021", "qa_022", "qa_034"})

PATCHES: dict[str, dict] = {
    "qa_017": {
        "question": (
            "推开门开到位后反弹 · §十 Gate Open Bounce Back · Push-to-Open · Limit B · "
            "Not Push-to-Open Open Limit Overswing"
        ),
        "answer_zh_prefix": (
            "症状：推开门开到位后反弹（§十开反弹·推开门·限位B远端；"
            "非推开门开位停不下来·非推开门开位不限位·非推开门开门停不下来·"
            "非开门过远进草地·非screw B overswing）"
        ),
    },
    "qa_019": {
        "answer_zh_prefix": (
            "症状：推开门 开门停不下来 · 推开门开位不限位 · "
            "推开门开位停不下来/开门过远进草地（限位B开位·推开门·screw B·AT12131 · "
            "adjusting screw B sliding limit switch gate still overswings · "
            "opens too far into grass · overswings；"
            "非§十开到位反弹·非§十二走停·非push button does nothing）"
        ),
    },
    "qa_015": {
        "answer_zh_prefix": (
            "症状：门关到位又弹回来（拉开门·§九反弹·限位B；"
            "非adjusting screw B overswings·非gate still overswings·非opens too far·"
            "非reconfirm open closed position limit switch B·非AT12131 limit·非关门慢中途停）"
        ),
    },
    "qa_020": {
        "answer_zh_prefix": (
            "症状：拉开门关门位不到位/reconfirm open closed position pull to open limit switch B（"
            "限位B·关门位·gate not closing fully · doesn't close all the way · "
            "FORCE potentiometer SOFT STOP limit context AT12131；"
            "非§九反弹·非门机运行慢§三十四·非§十二走停·非opens too far overswing）"
        ),
    },
    "qa_021": {
        "answer_zh_prefix": (
            "症状：推开门关不到位/关门位不限位（限位A·关门位；"
            "非gate not closing fully FORCE only·非§十二走停·非推开门开位不限位）"
        ),
    },
    "qa_022": {
        "answer_zh_prefix": (
            "症状：开门未开全即停/走停（§十二电机电流小·detect voltage 11 12 terminals above 22V · "
            "gate stops opening · FORCE potentiometer SOFT STOP gate not opening all the way · "
            "stops before opening fully · push against gate load test；"
            "非门机运行慢§三十四·非限位 screw B overswing·非§八中途反弹）"
        ),
    },
    "qa_034": {
        "answer_zh_prefix": (
            "症状：门机运行慢/11#12#电压压降/电机转速慢（gate operates slowly · motor speed slow；"
            "非§十二走停·非stops before opening fully·非gate stops opening·"
            "非detect voltage 11 12 gate stops opening·"
            "非gate not closing fully limit·非gate not opening all the way stall·"
            "非FORCE SOFT STOP limit switch·非opens too far limit B·非推开门开位不限位）"
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


def build_qa019_embedding(question: str, segment: str) -> str:
    return (
        "推开门 开门停不下来 推开门开位不限位 · "
        "adjusting screw B sliding limit switch gate still overswings AT12131 · "
        "opens too far into grass limit switch B does nothing\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa020_embedding(question: str, segment: str) -> str:
    return (
        "reconfirm open closed position pull to open limit switch B · "
        "gate not closing fully FORCE potentiometer SOFT STOP AT12131 limit close · "
        "doesn't close all the way very slow stops halfway screw B\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa022_stall_embedding(question: str, segment: str) -> str:
    return (
        "detect voltage 11 12 terminals above 22V gate stops opening · "
        "FORCE potentiometer SOFT STOP gate not opening all the way · "
        "stops before opening fully gate stops halfway while opening · "
        "A3S gate opener keeps stopping before opening fully\n"
        f"[问题] {question}\n[子场景：症状]\n{segment}"
    ).strip()


def build_qa034_slow_embedding(question: str, segment: str) -> str:
    return (
        "门机运行慢 门开关特别慢 运行速度很慢 gate operates slowly motor speed · "
        "voltage 11 12 terminals slow operation · "
        "not stops before opening fully not gate stops opening not stall\n"
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
            custom[cid] = build_qa019_embedding(q, seg)
        elif cid == "qa_020_c001":
            custom[cid] = build_qa020_embedding(q, seg)
        elif cid == "qa_022_c001":
            custom[cid] = build_qa022_stall_embedding(q, seg)
        elif cid == "qa_034_c001":
            custom[cid] = build_qa034_slow_embedding(q, seg)
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
