#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-05 Tier A 第 12 组：qa_010 步 2 增补 DIP #5 → 12/12 closure。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "_scratch/eval"))

from ad5s_zh_en_gap_scan import en_only_specs  # noqa: E402

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-v1-05-qa010"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
GROUP = "qa_010"

STEP2_OLD = "2 排除配件影响\n"
STEP2_NEW = (
    "2 排除配件影响：断开控制板上所有有线配件（仅留电源和机臂）；"
    "将 DIP 开关 #5 拨 OFF 关闭红外功能；清除遥控编码后重学，"
    "仍不行则瞬时短接 push button 端口（#4、#5）测试\n"
)


def patch_qa010(groups: list[dict]) -> None:
    g = next(x for x in groups if x["group_id"] == GROUP)
    zh = g.get("answer_zh") or ""
    if STEP2_OLD not in zh and STEP2_NEW.split("：")[0] in zh:
        print("  qa_010 already patched")
        return
    if STEP2_OLD not in zh:
        raise SystemExit(f"qa_010 step 2 anchor not found")
    g["answer_zh"] = zh.replace(STEP2_OLD, STEP2_NEW, 1)
    print("  patched qa_010 dip #5 in step 2")


def verify(g: dict) -> None:
    miss = en_only_specs(g.get("answer_en") or "", g.get("answer_zh") or "")
    dip = [m for m in miss if m[0] == "dip_switch"]
    if dip:
        raise SystemExit(f"spec verify failed: {dip}")
    print("OK   qa_010 dip_switch covered in ZH")


def merge_chunks() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_gid = {c["group_id"]: c for c in old_cap if c.get("is_retrievable", True)}
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        if c["group_id"] == GROUP:
            merged = deepcopy(c)
            old = old_by_gid.get(GROUP)
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
    groups = json.loads((PROD / "qa_groups.json").read_text(encoding="utf-8"))
    patch_qa010(groups)
    g = next(x for x in groups if x["group_id"] == GROUP)
    verify(g)
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
        [sys.executable, str(ROOT / "_scratch/eval/bl_v1_05_display_probe.py")],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_05_qa010_eval.json"),
        ],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
