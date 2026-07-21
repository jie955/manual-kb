#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-05 Wave1+2 gate probe: Top1 + thin-ZH + patched groups show spec in content_zh."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from display_content_utils import is_thin_zh, thin_zh_reason  # noqa: E402
from qa_server import _ask, _init_engine, _load_dotenv  # noqa: E402

# id, query, expect_gid, expect_thin, must_contain_in_zh (any)
QUERIES = [
    ("a01", "控制板灯不亮", "qa_001", False, ["10A", "250VAC"]),
    ("a03", "纯太阳能控制板指示灯不亮", "qa_002", False, ["10A"]),
    ("a05", "接上太阳能板门机就不转了", "qa_004", False, ["30W"]),
    ("a06", "学遥控器 学习灯不亮", "qa_005", True, ["11#", "12#"]),
    ("a07", "学遥控器 学习灯一直亮 学不上", "qa_006", True, ["CR2025"]),
    ("c01", "只有一个遥控器坏了", "qa_007", True, ["CR2025"]),
    ("a08", "遥控距离太短", "qa_008", True, ["CR2025", "65"]),
    ("a09", "按遥控器完全没有反应", "qa_010", False, ["#5", "DIP"]),
    ("a15", "no response when pressing remote AD5S", "qa_010", False, ["#5", "DIP"]),
    ("c02", "要多按几次遥控门机才动", "qa_009", False, ["CR2025"]),
    ("a11", "一按遥控器保险丝就烧", "qa_012", False, ["10A", "250VAC"]),
    ("b03", "自动关门功能没用 不会自己关", "qa_033", False, ["DIP", "#2"]),
    ("b10", "门开到一半就停住或弹回来", "qa_040", False, ["3.3", "1米"]),
    ("a14", "门刚动一下就停 电机电流", "qa_022", False, []),  # §十四 C · 无 merge
]


def main() -> None:
    _load_dotenv()
    _init_engine(
        REPO / "_scratch/run-ad5s/chroma_captioned",
        "_scratch/modelscope/BAAI/bge-m3",
    )
    print("id | top1 | expect | thin | spec_in_zh | gate")
    fails = 0
    for qid, q, exp_gid, exp_thin, needles in QUERIES:
        data = _ask(q, use_llm=False)
        top = (data.get("hits") or [None])[0]
        gid = top.get("group_id") if top else None
        zh = (top.get("content_zh") or top.get("answer_zh") or "") if top else ""
        en = (top.get("content_en") or top.get("answer_en") or "") if top else ""
        thin = is_thin_zh(zh, en)
        spec_ok = all(n in zh for n in needles) if needles else True
        ok = gid == exp_gid and thin == exp_thin and spec_ok
        if not ok:
            fails += 1
        reason = thin_zh_reason(zh, en) or "-"
        print(
            f"{qid} | {gid} | {exp_gid} | {thin} | {spec_ok} | "
            f"{'PASS' if ok else 'FAIL'} ({reason})"
        )
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
