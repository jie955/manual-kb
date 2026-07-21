#!/usr/bin/env python3
"""理解A · 三库 prod 分库手测（API + 浏览器 · eval 口径探针）。"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOT = ROOT / "_scratch/eval/screenshots/v1_three_lib_handtest"
OUT_MD = ROOT / "_scratch/eval/v1_three_lib_handtest_log.md"
OUT_JSON = ROOT / "_scratch/eval/v1_three_lib_handtest_result.json"

PORTS = {"a3s": 8765, "ad5s": 8766, "tc148": 8767}

PORT_PROBE = {
    "a3s": ("适配器供电 power 灯不闪", "qa_001"),
    "ad5s": ("电机电流小 并接机臂排查", "qa_023"),
    "tc148": ("TC148 没反应 遥控器正常", "qa_002"),
}

# V1-05 Tier A · display probe 口径
TIER_A = [
    ("a01", "qa_001", "控制板灯不亮", ["10A", "250VAC"]),
    ("a03", "qa_002", "纯太阳能板供电 指示灯不亮", ["10A"]),
    ("a05", "qa_004", "一接太阳能板门机就不转了", ["30W"]),
    ("a06", "qa_005", "学遥控器 学习灯不亮", ["11#", "12#"]),
    ("a07", "qa_006", "学遥控器 学习灯一直亮 学不上", ["CR2025"]),
    ("a08", "qa_008", "遥控距离太短 站远点就不行", ["CR2025", "65"]),
    ("a09", "qa_010", "按遥控器完全没反应", ["#5", "DIP"]),
    ("a11", "qa_012", "一按遥控保险丝就烧", ["10A", "250VAC"]),
    ("b03", "qa_033", "自动关门功能没用 不会自己关", ["#2"]),
    ("b10", "qa_040", "门开关到一半就停住或弹回来", ["#3", "FORCE"]),
]

EXT01B = [
    ("b01", "qa_031", "门自己乱开乱关怎么回事", None),
    ("b02", "qa_032", "缓停止不对 没有缓停效果", None),
    ("b04", "qa_034", "风大能把门吹开一点怎么办", None),
    ("b05", "qa_035", "双机臂其中一个臂完全不工作", None),
    ("b06", "qa_036", "门开关特别慢 运行速度很慢", None),
    ("b07", "qa_037", "拉开门 开门不限位 限位A怎么调", ["限位A"]),
    ("b08", "qa_038", "机臂伸太过缩不回去 离合打开了", None),
    ("b09", "qa_039", "电机转但拉杆不动 机臂不伸缩", None),
    ("b11", "qa_041", "离合钥匙拧不开 门关到位很紧", None),
    ("b12", "qa_042", "脱门也打不开离合 伸太过推不进去", None),
    ("b13", "qa_043", "按遥控机臂有异响 离合打开还有声音", ["异响"]),
]

LIMIT = [
    ("LD16", "ad5s", "qa_016", "开到位后又弹回来 拉开门", ["反弹"]),
    ("LD37", "ad5s", "qa_037", "拉开门 开门不限位 限位A怎么调", ["限位A"]),
    ("LD20", "ad5s", "qa_020", "拉开门 关门不限位 限位B怎么调", ["限位B"]),
    ("LA19", "a3s", "qa_015", "门关到位又弹回来 拉开门", ["反弹"]),
    ("LA18", "a3s", "qa_018", "拉开门 开门位置不对 不限位", ["限位A"]),
]

SAMPLE = [
    ("S-A3S", "a3s", "qa_003", "太阳能充不进电池怎么办", None),
    ("S-AD5S", "ad5s", "qa_003", "太阳能充不进电池怎么办", ["42V"]),
    ("S-AD5S2", "ad5s", "qa_022", "门刚动一下就停 电机电流太小", ["50", "1152"]),
]


@dataclass
class Row:
    id: str
    lib: str
    query: str
    expect_gid: str
    ok: bool
    bucket: str
    notes: list[str] = field(default_factory=list)
    group_id: str = ""
    snippet: str = ""


def base(lib: str) -> str:
    return f"http://127.0.0.1:{PORTS[lib]}/"


def wait_health(lib: str, timeout: float = 120.0) -> bool:
    url = base(lib) + "api/health"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1.0)
    return False


def verify_ports() -> dict[str, str | None]:
    """Return lib -> error message if wrong chroma on port."""
    errs: dict[str, str | None] = {}
    for lib, (q, exp) in PORT_PROBE.items():
        if not wait_health(lib, timeout=30):
            errs[lib] = f":{PORTS[lib]} not responding"
            continue
        top = api_ask(lib, q)["hits"][0]
        if top.get("group_id") != exp:
            errs[lib] = f"port {PORTS[lib]} looks wrong (query={q!r} → {top.get('group_id')} not {exp})"
        else:
            errs[lib] = None
    return errs


def api_ask(lib: str, query: str, *, use_llm: bool = False) -> dict:
    body = json.dumps({"query": query, "use_llm": use_llm}).encode()
    req = urllib.request.Request(
        base(lib) + "api/ask",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def check_needles(text: str, needles: list[str] | None) -> list[str]:
    if not needles:
        return []
    return [n for n in needles if n not in text]


def run_api(port_errs: dict[str, str | None]) -> list[Row]:
    rows: list[Row] = []

    for qid, gid, query, needles in TIER_A:
        if port_errs.get("ad5s"):
            rows.append(Row(qid, "ad5s", query, gid, False, "tier_a", [port_errs["ad5s"]]))
            continue
        top = api_ask("ad5s", query)["hits"][0]
        zh = top.get("content_zh") or ""
        miss = check_needles(zh, needles)
        ok = top.get("group_id") == gid and not miss and len(zh) >= 40
        notes = []
        if top.get("group_id") != gid:
            notes.append(f"top1={top.get('group_id')}")
        if miss:
            notes.append(f"spec missing: {miss}")
        rows.append(Row(qid, "ad5s", query, gid, ok, "tier_a", notes, top.get("group_id", ""), zh[:100]))

    for qid, gid, query, hints in EXT01B:
        if port_errs.get("ad5s"):
            rows.append(Row(qid, "ad5s", query, gid, False, "ext01b", [port_errs["ad5s"]]))
            continue
        top = api_ask("ad5s", query)["hits"][0]
        zh = top.get("content_zh") or ""
        ok = top.get("group_id") == gid
        notes = []
        if not ok:
            notes.append(f"top1={top.get('group_id')}")
        if hints:
            miss = [h for h in hints if h not in zh and h not in (top.get("question") or "")]
            if miss:
                notes.append(f"hint missing: {miss}")
        if len(zh.strip()) < 30:
            notes.append("thin/empty zh")
        rows.append(Row(qid, "ad5s", query, gid, ok and "thin" not in str(notes), "ext01b", notes, top.get("group_id", ""), zh[:90]))

    for lid, lib, gid, query, hints in LIMIT:
        if port_errs.get(lib):
            rows.append(Row(lid, lib, query, gid, False, "limit", [port_errs[lib]]))
            continue
        top = api_ask(lib, query)["hits"][0]
        title = top.get("question") or ""
        zh = top.get("content_zh") or ""
        ok = top.get("group_id") == gid
        notes = []
        if not ok:
            notes.append(f"top1={top.get('group_id')}")
        for h in hints:
            if h not in title and h not in zh[:250]:
                notes.append(f"symptom tag missing: {h}")
        rows.append(Row(lid, lib, query, gid, ok and not any("missing" in n for n in notes), "limit", notes, top.get("group_id", ""), title[:70]))

    for sid, lib, gid, query, hints in SAMPLE:
        if port_errs.get(lib):
            rows.append(Row(sid, lib, query, gid, False, "sample", [port_errs[lib]]))
            continue
        top = api_ask(lib, query)["hits"][0]
        zh = top.get("content_zh") or ""
        ok = top.get("group_id") == gid
        notes = []
        if hints:
            miss = check_needles(zh, hints)
            if miss:
                notes.append(f"content missing: {miss}")
                ok = False
        rows.append(Row(sid, lib, query, gid, ok, "sample", notes, top.get("group_id", ""), zh[:80]))

    for tid, query, gid in [
        ("CRT1", "TC148 没反应 遥控器正常", "qa_002"),
        ("CRT2", "接上TC148墙壁开关 自己开关门", "qa_001"),
    ]:
        if port_errs.get("tc148"):
            rows.append(Row(tid, "tc148", query, gid, False, "tc148_crt", [port_errs["tc148"]]))
            continue
        top = api_ask("tc148", query)["hits"][0]
        tpls = top.get("customer_reply_templates") or []
        tpl = (tpls[0].get("text") if tpls else "") or ""
        zh = top.get("content_zh") or ""
        ok = (
            top.get("group_id") == gid
            and "Please help us confirm" in tpl
            and "Please help us confirm" not in zh
            and not (top.get("content_en") or "").strip()
        )
        notes = []
        if not tpls:
            notes.append("no customer_reply_templates — restart :8767 after re-embed?")
        rows.append(Row(tid, "tc148", query, gid, ok, "tc148_crt", notes, top.get("group_id", ""), f"tpl={len(tpl)}"))
    return rows


def run_browser(port_errs: dict[str, str | None]) -> list[dict]:
    from playwright.sync_api import sync_playwright

    out: list[dict] = []
    if port_errs.get("ad5s") and port_errs.get("tc148"):
        return [{"id": "SKIP", "ok": False, "notes": "ports not ready"}]

    SHOT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1100})

        if not port_errs.get("ad5s"):
            for case in [
                ("B-P23", "电机电流小 并接机臂排查", "qa_023"),
                ("B-P24", "走停加电阻 二极管怎么接", "qa_024"),
            ]:
                page.goto(f"http://127.0.0.1:{PORTS['ad5s']}/", wait_until="networkidle")
                page.locator("#query").fill(case[1])
                page.locator("#btn").click()
                page.wait_for_selector("#results.visible", timeout=120_000)
                time.sleep(0.5)
                meta = page.locator("#matchMeta").inner_text()
                ok = case[2] in meta
                if case[0] == "B-P24":
                    if page.locator("#ladderWrap:not(.hidden)").count():
                        if page.locator("#branchFilterWrap:not(.hidden)").count():
                            page.locator("#filterRegion").select_option("US")
                            time.sleep(0.2)
                    links = page.locator("#answerLinks a").count()
                    ok = ok and links >= 1
                if case[0] == "B-P23":
                    ok = ok and page.locator("#ladderWrap:not(.hidden)").count() > 0
                page.locator("#answerPanel").screenshot(path=str(SHOT / f"{case[0]}.png"))
                out.append({"id": case[0], "lib": "ad5s", "ok": ok, "gid": case[2]})

        if not port_errs.get("tc148"):
            page.goto(f"http://127.0.0.1:{PORTS['tc148']}/", wait_until="networkidle")
            page.locator("#query").fill("TC148 没反应 遥控器正常")
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            page.locator("#customerReplyFold").evaluate("el => { el.open = true; }")
            tpl_len = len(page.evaluate('() => document.getElementById("customerReplyBody").textContent || ""'))
            disc = page.locator(".customer-reply-disclaimer").inner_text()
            ok = "qa_002" in page.locator("#matchMeta").inner_text() and tpl_len > 500 and "政策承诺" in disc
            page.locator("#answerPanel").screenshot(path=str(SHOT / "B-CRT.png"))
            out.append({"id": "B-CRT", "lib": "tc148", "ok": ok, "tpl_len": tpl_len})

        browser.close()
    return out


def write_md(api_rows: list[Row], browser_rows: list[dict], port_errs: dict) -> None:
    lines = [
        "# 理解A · 三库 prod 分库手测留档",
        "",
        "**日期**：2026-07-05 · **模式**：三库各自 prod · eval 口径 API + 浏览器",
        "**端口**：A3S `:8765` · AD5S `:8766` · TC148 `:8767`",
        "**脚本**：[`v1_three_lib_prod_handtest.py`](./v1_three_lib_prod_handtest.py)",
        "",
        "## 端口探针",
        "",
    ]
    for lib, err in port_errs.items():
        flag = "✅" if err is None else f"❌ {err}"
        lines.append(f"- **{lib}** :{PORTS[lib]} — {flag}")
    lines.extend(["", "## 汇总", ""])
    ap = sum(1 for r in api_rows if r.ok)
    bp = sum(1 for r in browser_rows if r.get("ok"))
    lines.append(f"| API | {ap}/{len(api_rows)} | Browser | {bp}/{len(browser_rows)} |")
    lines.append("")

    for bucket in ("tier_a", "ext01b", "limit", "sample", "tc148_crt"):
        sub = [r for r in api_rows if r.bucket == bucket]
        if not sub:
            continue
        lines += [f"## {bucket}", "", "| id | expect | top1 | OK | 备注 |", "| --- | --- | --- | ---: | --- |"]
        for r in sub:
            lines.append(f"| {r.id} | {r.expect_gid} | {r.group_id} | {'✅' if r.ok else '❌'} | {'; '.join(r.notes) or '—'} |")
        lines.append("")

    if browser_rows:
        lines += ["## 浏览器", "", "| id | OK |", "| --- | ---: |"]
        for r in browser_rows:
            lines.append(f"| {r['id']} | {'✅' if r.get('ok') else '❌'} |")
        lines.append("")

    fails = [r for r in api_rows if not r.ok] + [r for r in browser_rows if not r.get("ok")]
    lines += ["## 待判断", ""]
    if not fails:
        lines.append("无 failing 项。")
    else:
        lines.append("下列项需区分 **新问题** vs **已知 backlog**（confusable Top3 / thin-ZH 规格仍在 EN 等）：")
        for r in fails:
            if isinstance(r, Row):
                lines.append(f"- **{r.id}** [{r.bucket}] expect `{r.expect_gid}` → `{r.group_id}` · {r.notes}")
            else:
                lines.append(f"- **{r['id']}** browser · {r}")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    port_errs = verify_ports()
    api_rows = run_api(port_errs)
    browser_rows = run_browser(port_errs)
    OUT_JSON.write_text(
        json.dumps({"port_errs": port_errs, "api": [r.__dict__ for r in api_rows], "browser": browser_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_md(api_rows, browser_rows, port_errs)
    ap = sum(1 for r in api_rows if r.ok)
    print(f"ports: {port_errs}")
    print(f"API {ap}/{len(api_rows)} · Browser {sum(1 for r in browser_rows if r.get('ok'))}/{len(browser_rows)}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
