#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-07 gate probe: retrieval Top1 + is_thin_zh (same as demo renderFlatBody)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from display_content_utils import is_thin_zh, thin_zh_reason  # noqa: E402
from qa_server import _ask, _init_engine, _load_dotenv  # noqa: E402

QUERIES = [
    ("b01", "门自己乱开乱关怎么回事", "qa_031", True),
    ("b02", "缓停止不对 没有缓停效果", "qa_032", True),
    ("b03", "自动关门功能没用 不会自己关", "qa_033", True),
    ("b04", "风大能把门吹开一点怎么办", "qa_034", True),
    ("a01", "控制板灯不亮", "qa_001", False),
    ("a14", "门刚动一下就停 电机电流", "qa_022", False),
    ("N1", "日常保养润滑", "qa_028", True),
]


def main() -> None:
    _load_dotenv()
    _init_engine(
        REPO / "_scratch/run-ad5s/chroma_captioned",
        "_scratch/modelscope/BAAI/bge-m3",
    )
    print("id | top1 | expect | thin | reason | gate")
    fails = 0
    for qid, q, exp_gid, exp_thin in QUERIES:
        data = _ask(q, use_llm=False)
        top = (data.get("hits") or [None])[0]
        gid = top.get("group_id") if top else None
        zh = (top.get("content_zh") or "") if top else ""
        en = (top.get("content_en") or "") if top else ""
        thin = is_thin_zh(zh, en)
        reason = thin_zh_reason(zh, en) or "-"
        ok = gid == exp_gid and thin == exp_thin
        if not ok:
            fails += 1
        print(f"{qid} | {gid} | {exp_gid} | {thin} | {reason} | {'PASS' if ok else 'FAIL'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
