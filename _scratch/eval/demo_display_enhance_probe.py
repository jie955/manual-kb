#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo 展示增强探针：文档来源字段 + hits #2-#4 相关推荐素材 · 三库 API spot-check."""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LIBS = {
    "a3s": {
        "port": 8765,
        "label": "A3S / A5S / A8S",
        "doc_title": "A3S-A5S-A8S 常见问题排查",
        "probes": [
            ("日常保养喷WD40润滑", "qa_040", "保养域 · 相关推荐语义"),
            ("离合钥匙拧不开", "qa_038", "配图组 · 来源章节"),
            ("随意开关门乱开", "qa_029", "Top2 邻域相近（预期可接受）"),
        ],
    },
    "ad5s": {
        "port": 8766,
        "label": "AD5S / AD8S",
        "doc_title": "AD5S-AD8S 常见问题排查",
        "probes": [
            ("门自己乱开乱关怎么回事", "qa_031", "EXT 组来源"),
            ("电机电流小 并接机臂排查", "qa_023", "ladder 组"),
            ("日常保养润滑 WD40", "qa_028", "保养 · Top2 邻域"),
        ],
    },
    "tc148": {
        "port": 8767,
        "label": "TC148",
        "doc_title": "TC148 常见问题排查",
        "probes": [
            ("TC148 没反应 遥控器正常", "qa_002", "2 组库来源"),
            ("接上TC148墙壁开关 自己开关门", "qa_001", "confusable 邻域"),
        ],
    },
}


def human_section(section: str) -> str:
    s = (section or "").strip()
    if not s:
        return "—"
    m = re.match(r"^(.+?)\s+(?=[A-Za-z][A-Za-z\s\-'(),]{6,})", s)
    if m:
        return m.group(1).strip()
    return s[:56] + "…" if len(s) > 56 else s


def ask(port: int, query: str) -> dict:
    body = json.dumps({"query": query, "use_llm": False}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/ask",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def related_from_hits(hits: list[dict], top_gid: str) -> list[dict]:
    seen = {top_gid}
    out = []
    for h in hits[1:]:
        gid = h.get("group_id")
        if not gid or gid in seen:
            continue
        seen.add(gid)
        out.append(
            {
                "group_id": gid,
                "question": (h.get("question") or "")[:50],
                "section": human_section(h.get("section") or ""),
                "score": round(float(h.get("score") or 0), 3),
            }
        )
        if len(out) >= 3:
            break
    return out


def health(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=5) as r:
            return r.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def main() -> int:
    rows = []
    fails = 0
    for lib_id, cfg in LIBS.items():
        if not health(cfg["port"]):
            print(f"FAIL {lib_id} :{cfg['port']} not ready")
            fails += 1
            continue
        print(f"\n=== {lib_id} :{cfg['port']} ===")
        for query, exp_gid, note in cfg["probes"]:
            try:
                data = ask(cfg["port"], query)
            except Exception as exc:
                print(f"  ERR {query[:20]} -> {exc}")
                fails += 1
                continue
            hits = data.get("hits") or []
            top = hits[0] if hits else {}
            gid = top.get("group_id")
            ok_top = gid == exp_gid
            if not ok_top:
                fails += 1
            src = f"{cfg['label']} · {cfg['doc_title']} · {human_section(top.get('section') or '')}"
            related = related_from_hits(hits, gid or "")
            rel_note = "—"
            if related:
                rel_note = " | ".join(f"{r['group_id']}({r['score']}) {r['section'][:18]}" for r in related)
            gate = "PASS" if ok_top else "FAIL"
            print(f"  [{gate}] {query[:22]} -> {gid} exp={exp_gid}")
            print(f"       来源: {src}")
            print(f"       相关({len(related)}): {rel_note}")
            print(f"       备注: {note}")
            rows.append(
                {
                    "lib": lib_id,
                    "query": query,
                    "expect": exp_gid,
                    "top1": gid,
                    "source_line": src,
                    "related": related,
                    "note": note,
                    "pass": ok_top,
                }
            )
    out_json = Path(__file__).with_name("demo_display_enhance_probe.json")
    out_json.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nrows={len(rows)} fails={fails} -> {out_json.name}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
