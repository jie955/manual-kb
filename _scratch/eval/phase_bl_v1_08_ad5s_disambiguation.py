#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-08 Phase 1: AD5S §十二 qa_020/021/037 title + answer lead disambiguation."""

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
STAMP = "20260705-bl-v1-08"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_020", "qa_021", "qa_037"})

PATCHES: dict[str, dict] = {
    "qa_020": {
        "question": "关门限位不到位·限位B（推/拉开门）Gate Close Limit · Limit Switch B · Push/Pull",
        "answer_zh_prefix": "症状：关门不到位或关门不限位（限位B·关门位；非开门开位·非限位A）",
    },
    "qa_021": {
        "question": "关门限位不到位·限位A外移·磁环排查 Gate Close Limit · Limit A · Magnet/Short Test",
        "answer_zh_prefix": "症状：关不到位需限位A外移或磁环/控制板短接排查（限位A·关门位；非限位B·非开门开位）",
    },
    "qa_037": {
        "question": "开门不限位/过位（拉开门·限位A·开位）Gate Open Limit · Pull-to-Open · Limit A Open",
        "answer_zh_prefix": "症状：开门不限位/开门过位或开门不停（限位A·开位；非关门限位B）",
    },
}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in PATCHES:
            continue
        p = PATCHES[gid]
        g["question"] = p["question"]
        zh = (g.get("answer_zh") or "").strip()
        prefix = p["answer_zh_prefix"]
        if not zh.startswith(prefix):
            # strip old symptom prefixes
            for old in (
                "症状：开门不限位/开门过位或开门不停（限位A·开位；非关门限位B）",
                "症状：开门过位或开门不停（限位A·开位；非关门限位B）",
                "症状：关门不到位或关门不限位（限位B·关门位；非开门限位A开位）",
                "症状：关门不到位或关门不限位（限位B·关门位；非开门开位·非限位A）",
                "症状：关不到位需限位A外移或磁环/控制板短接排查（限位A·关门位；非限位B·非开门开位）",
            ):
                if zh.startswith(old):
                    zh = zh[len(old) :].lstrip("\n")
                    break
            g["answer_zh"] = prefix + ("\n" + zh if zh else "")
        print(f"  patched {gid}: q={g['question'][:50]}…")
    return out


def backup() -> None:
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if chroma_dst.exists():
        shutil.rmtree(chroma_dst)
    shutil.copytree(PROD / "chroma_captioned", chroma_dst)
    for name in ("qa_groups.json", "chunks_captioned.json"):
        shutil.copy2(PROD / name, PROD / f"{name}.bak-{STAMP}")
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def merge_chunks_captioned() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = [
        old_by_id[c["chunk_id"]] if c["chunk_id"] in old_by_id and c["group_id"] not in TOUCH_IDS else c
        for c in new_chunks
    ]
    (PROD / "chunks_captioned.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def pipeline() -> None:
    backup()
    groups = apply_patches(load_groups(PROD / "qa_groups.json"))
    save_groups(PROD / "qa_groups.json", groups)
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
            str(ROOT / "_scratch/eval/bl_v1_08_ad5s_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
