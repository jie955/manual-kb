#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate #5 清单批量探针：与 qa_server 同路径，输出 demo_qa_log 行。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

MODEL = "_scratch/modelscope/BAAI/bge-m3"

LIBS: dict[str, dict] = {
    "a3s": {
        "label": "A3S",
        "chroma": REPO / "_scratch/run-007/chroma_captioned",
        "images": REPO / "_scratch/run-006/images",
        "queries": [
            ("A1", "适配器供电 灯不亮", "电源"),
            ("A2", "太阳能充不进电池怎么办", "太阳能"),
            ("A3", "遥控距离太短 站远点就不行", "遥控"),
            ("A4", "学遥控器 学习灯不亮", "遥控编程"),
            ("A5", "门开到一半自己停了是咋回事", None),
            ("A6", "下雨天开门机跳闸", None),
            ("X3", "AD5S 机臂电流小 走 EN→ZH 翻译", "越界"),
            ("X4", "帮我写一首关于大门的诗", "无关"),
        ],
    },
    "ad5s": {
        "label": "AD5S",
        "chroma": REPO / "_scratch/run-ad5s/chroma_captioned",
        "images": REPO / "_scratch/run-ad5s/images",
        "queries": [
            ("D1", "按遥控器完全没反应", "qa_010"),
            ("D2", "门刚动一下就停 电机电流太小", "qa_022"),
            ("D3", "控制板一直咔哒响", "qa_011"),
            ("D4", "一按遥控保险丝就烧", "qa_012"),
            ("D5", "推拉门装反了怎么办", None),
            ("D6", "两个机臂只有一个在动", None),
            ("X2", "TC148 墙壁按键 随机开门", "越界"),
            ("X4", "帮我写一首关于大门的诗", "无关"),
        ],
    },
    "tc148": {
        "label": "TC148",
        "chroma": REPO / "_scratch/run-tc148/chroma_captioned",
        "images": REPO / "_scratch/run-tc148/images",
        "queries": [
            ("T1", "墙壁开关自检后灯常亮", "qa_001"),
            ("T2", "TC148 没反应 遥控器正常", "qa_002"),
            ("T3", "push button 端口短接 O/S/C COM", "qa_002"),
            ("T4", "太阳能板不充电", "越界"),
            ("T5", "机械臂伸不出去", "越界"),
            ("X1", "太阳能板 2 块怎么接", "越界"),
            ("X4", "帮我写一首关于大门的诗", "无关"),
        ],
    },
}

REFUSE_MARKERS = (
    "未找到",
    "不足以",
    "无法回答",
    "不在手册",
    "没有足够",
    "查不到",
    "无关",
    "不属于",
)


def _images_ok(hit: dict, images_dir: Path) -> str:
    files = []
    for img in hit.get("images") or []:
        f = img.get("file") if isinstance(img, dict) else str(img)
        if f:
            files.append(f)
    if not files:
        return "无"
    missing = [f for f in files if not (images_dir / f).is_file()]
    return "NG裂图" if missing else "OK"


def _oob_hint(tag: str | None, gen: str | None) -> str:
    if tag not in ("越界", "无关"):
        return "n/a"
    if not gen:
        return "?"
    g = gen.strip()
    if any(m in g for m in REFUSE_MARKERS):
        return "OK拒答"
    if tag == "无关" and ("诗" in g or "诗歌" in g):
        return "WARN写诗"
    return "NG硬答"


def run_lib(lib_key: str, *, use_llm: bool) -> list[dict]:
    from qa_server import _init_engine, _ask, _load_dotenv

    cfg = LIBS[lib_key]
    _load_dotenv()
    _init_engine(cfg["chroma"], MODEL)

    rows: list[dict] = []
    for qid, query, hint in cfg["queries"]:
        data = _ask(query, use_llm=use_llm)
        top = (data.get("hits") or [None])[0]
        gen = data.get("generated_answer") or ""
        row = {
            "id": qid,
            "lib": cfg["label"],
            "llm": "on" if use_llm else "off",
            "query": query,
            "hint": hint,
            "top1_group": top.get("group_id") if top else None,
            "top1_question": (top.get("question") or "")[:60] if top else None,
            "score": round(top["score"], 4) if top else None,
            "llm_status": data.get("llm_status"),
            "llm_truncated": data.get("llm_truncated"),
            "配图": _images_ok(top, cfg["images"]) if top else "无",
            "越界": _oob_hint(hint, gen if use_llm else None),
            "生成摘要": (gen[:180] + "…") if len(gen) > 180 else gen,
        }
        rows.append(row)
    return rows


def format_log_line(r: dict) -> str:
    return (
        f"[{r['id']}] lib={r['lib']} | LLM={r['llm']} | query=\"{r['query']}\" | "
        f"top1={r['top1_group']} score={r['score']} | "
        f"配图={r['配图']} | 越界={r['越界']} | llm={r['llm_status']} | "
        f"生成摘要={r['生成摘要']!r} | 人工忠实=待核"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo checklist batch probe")
    parser.add_argument("lib", choices=list(LIBS), help="a3s | ad5s | tc148")
    parser.add_argument("--no-llm", action="store_true", help="仅检索+原文路径")
    parser.add_argument("--json-out", type=Path, help="写 JSON 明细")
    parser.add_argument("--append-log", type=Path, help="追加 demo_qa_log 行")
    args = parser.parse_args()

    rows = run_lib(args.lib, use_llm=not args.no_llm)
    for r in rows:
        print(format_log_line(r))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\njson: {args.json_out}", file=sys.stderr)

    if args.append_log:
        args.append_log.parent.mkdir(parents=True, exist_ok=True)
        header = f"\n## {LIBS[args.lib]['label']} · probe {rows[0]['llm']}\n\n"
        if not args.append_log.exists():
            args.append_log.write_text(
                "# demo_qa_log · Gate #5\n\n", encoding="utf-8"
            )
        with args.append_log.open("a", encoding="utf-8") as f:
            f.write(header)
            for r in rows:
                f.write(format_log_line(r) + "\n")
        print(f"log: {args.append_log}", file=sys.stderr)


if __name__ == "__main__":
    main()
