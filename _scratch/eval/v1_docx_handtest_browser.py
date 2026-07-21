#!/usr/bin/env python3
"""docx V1 line · AD5S demo hand-test (playwright · LLM off · :8765).

Coverage: EXT-01b sample · V1-05 Tier A · limit/bounce · qa_023/024 · YouTube links.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8765"
SHOT = Path(__file__).resolve().parent / "screenshots" / "v1_handtest"

CASES = [
    # V1-05 Tier A spot-fix sample
    {"id": "TA01", "query": "控制板灯不亮", "gid": "qa_001", "kind": "flat"},
    {"id": "TA10", "query": "按遥控器完全没有反应", "gid": "qa_010", "kind": "flat_links"},
    {"id": "TA33", "query": "自动关门功能没用 不会自己关", "gid": "qa_033", "kind": "flat"},
    {"id": "TA40", "query": "门开到一半就停住或弹回来", "gid": "qa_040", "kind": "flat"},
    # EXT-01b / §十十一 限位反弹
    {"id": "LB16", "query": "开到位后又弹回来 拉开门安装", "gid": "qa_016", "kind": "flat"},
    {"id": "LB37", "query": "拉开门 开门不限位 限位A怎么调", "gid": "qa_037", "kind": "flat"},
    # EXT-01b batch1 thin-ZH
    {"id": "B31", "query": "门自己乱开乱关怎么回事", "gid": "qa_031", "kind": "thin_en"},
    # §十九 + YouTube links (post-close)
    {"id": "YT29", "query": "拆机臂内部怎么润滑", "gid": "qa_029", "kind": "flat_links", "min_links": 3},
    {"id": "YT42", "query": "脱门也打不开离合 伸太过推不进去", "gid": "qa_042", "kind": "flat_links", "min_links": 4},
    # complex ladder
    {
        "id": "P23",
        "query": "电机电流小 并接机臂排查",
        "gid": "qa_023",
        "kind": "parallel_ladder",
    },
    {
        "id": "P24",
        "query": "走停加电阻 二极管怎么接",
        "gid": "qa_024",
        "kind": "install_ladder",
    },
    # sample other
    {"id": "S08", "query": "遥控距离太短 站远点就不行", "gid": "qa_008", "kind": "ladder"},
]


def wait_health(timeout: float = 180.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/api/health", timeout=3) as r:
                if r.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1.0)
    raise SystemExit(f"server not ready at {BASE}")


def api_ask(query: str) -> dict:
    body = json.dumps({"query": query, "use_llm": False}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/ask",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def run() -> list[dict]:
    from playwright.sync_api import sync_playwright

    SHOT.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 960})
        js_errors: list[str] = []
        page.on("pageerror", lambda e: js_errors.append(str(e)))

        page.goto(f"{BASE}/", wait_until="networkidle")
        if page.locator("#useLlm").is_checked():
            page.locator("#useLlm").uncheck()

        for case in CASES:
            js_errors.clear()
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            page.wait_for_function(
                "() => document.getElementById('matchMeta')?.textContent?.trim().length > 0",
                timeout=120_000,
            )
            time.sleep(0.3)

            meta = page.locator("#matchMeta").inner_text()
            gid = ""
            if " · qa_" in meta:
                gid = meta.split(" · qa_")[1].split()[0]
                gid = "qa_" + gid.replace("qa_", "")

            api = api_ask(case["query"])
            top = (api.get("hits") or [{}])[0]
            api_gid = top.get("group_id", "")

            ladder_vis = not page.locator("#ladderWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            filter_vis = not page.locator("#branchFilterWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            isr_hidden = page.locator("#filterInstallStallRegion").evaluate(
                "el => el.classList.contains('hidden')"
            )
            branch_tags = page.locator(".ladder-branch-tag").all_inner_texts()
            n_links = page.locator("#answerLinks a").count()
            n_figs = page.locator("#answerFigures img").count()
            filter_label = page.locator("#branchFilterLabel").inner_text()

            ok = True
            reasons: list[str] = []
            if js_errors:
                ok = False
                reasons.append(f"js: {js_errors[:2]}")
            if api_gid != case["gid"]:
                ok = False
                reasons.append(f"top1={api_gid} want {case['gid']}")

            kind = case["kind"]
            if kind == "flat":
                if ladder_vis:
                    ok = False
                    reasons.append("unexpected ladder")
            elif kind == "flat_links":
                if ladder_vis:
                    ok = False
                    reasons.append("unexpected ladder")
                min_l = case.get("min_links", 1)
                if n_links < min_l:
                    ok = False
                    reasons.append(f"links={n_links} want>={min_l}")
            elif kind == "thin_en":
                if page.locator("#answer .answer-en-supplement").count() < 1:
                    ok = False
                    reasons.append("missing EN supplement")
            elif kind == "ladder":
                if not ladder_vis:
                    ok = False
                    reasons.append("ladder hidden")
            elif kind == "parallel_ladder":
                if not ladder_vis:
                    ok = False
                    reasons.append("ladder hidden")
                if not isr_hidden:
                    ok = False
                    reasons.append("install/stall filters should be hidden")
                want = ["机臂2并到机臂1", "机臂1并到机臂2"]
                for w in want:
                    if not any(w in t for t in branch_tags):
                        ok = False
                        reasons.append(f"missing tag {w}")
            elif kind == "install_ladder":
                if not ladder_vis:
                    ok = False
                    reasons.append("ladder hidden")
                if not filter_vis:
                    ok = False
                    reasons.append("branchFilterWrap hidden")
                if isr_hidden:
                    ok = False
                    reasons.append("install/stall filters should be visible")
                # apply one filter combo
                page.locator("#filterInstall").select_option("push_open")
                page.locator("#filterSymptom").select_option("close_abnormal")
                page.locator("#filterRegion").select_option("US")
                time.sleep(0.2)
                tags_after = page.locator(".ladder-branch-tag").all_inner_texts()
                if not tags_after:
                    ok = False
                    reasons.append("no branch after filter")

            shot = SHOT / f"{case['id']}.png"
            page.locator("#answerPanel").screenshot(path=str(shot))

            out.append(
                {
                    "id": case["id"],
                    "query": case["query"],
                    "ok": ok,
                    "top1": api_gid,
                    "kind": kind,
                    "ladder": ladder_vis,
                    "filter_wrap": filter_vis,
                    "isr_hidden": isr_hidden,
                    "branch_tags": branch_tags[:4],
                    "filter_label": filter_label[:50],
                    "links": n_links,
                    "figures": n_figs,
                    "reasons": reasons,
                    "screenshot": str(shot.name),
                }
            )

        browser.close()
    return out


def main() -> None:
    wait_health()
    rows = run()
    passed = sum(1 for r in rows if r["ok"])
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"V1_HANDTEST: {passed}/{len(rows)} PASS")
    if passed < len(rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
