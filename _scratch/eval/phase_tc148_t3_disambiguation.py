#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TC148 T3 检索 disambiguation · 2 组症状化前缀（限位域同型）。"""

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
STAMP = "20260705-tc148-t3"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"

# 新症状行（替换各组首条 症状：…）
QA001_SYM_OLD = "症状：不接TC148，门机可以正常工作，一接上TC148，随机开关门"
QA001_SYM_NEW = (
    "症状：接上TC148后随机开关门/乱动（非遥控正常按TC148无反应·非push button端口瞬时短接O/S/C COM）"
)

QA002_SYM_OLD = "症状：其他设备（例如遥控器）可以操控门机，但是按下TC148后，门机没有反应。"
QA002_SYM_NEW = (
    "症状：遥控可用但按TC148无反应（push button端口瞬时短接 O/S/C COM 排查·非随机开关门/乱动）"
)

QA002_Q_OLD = "二、按TC148 PUSH BUTTON门机没有反应 （TC148不工作）"
QA002_Q_NEW = "按TC148无反应·push button短接排查 No Response · O/S/C COM Short Test"


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def apply_patch(groups: list[dict]) -> None:
    for g in groups:
        gid = g["group_id"]
        if gid == "qa_001":
            zh = g.get("answer_zh") or ""
            if QA001_SYM_OLD in zh:
                g["answer_zh"] = zh.replace(QA001_SYM_OLD, QA001_SYM_NEW, 1)
            elif QA001_SYM_NEW.split("（")[0] not in zh:
                raise SystemExit("qa_001 symptom anchor not found")
        elif gid == "qa_002":
            g["question"] = QA002_Q_NEW
            zh = g.get("answer_zh") or ""
            if QA002_SYM_OLD in zh:
                g["answer_zh"] = zh.replace(QA002_SYM_OLD, QA002_SYM_NEW, 1)
            elif QA002_SYM_NEW.split("（")[0] not in zh:
                raise SystemExit("qa_002 symptom anchor not found")
        else:
            continue
        print(f"  patched {gid}")


def merge_chunks() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        if c["group_id"] in ("qa_001", "qa_002"):
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
            str(ROOT / "_scratch/eval/tc148_t3_post_eval.json"),
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, str(ROOT / "_scratch/eval/verify_tc148_content.py")],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
