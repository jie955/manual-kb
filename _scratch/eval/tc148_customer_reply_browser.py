#!/usr/bin/env python3
"""TC148 customer_reply_template · demo fold UI gate (playwright)."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "http://127.0.0.1:8766"
SHOT = ROOT / "_scratch/eval/screenshots/v1_handtest_llm_on"

CASES = [
    {"id": "CRT-T2", "query": "TC148 没反应 遥控器正常", "gid": "qa_002"},
    {"id": "CRT-T1", "query": "接上TC148墙壁开关 自己开关门", "gid": "qa_001"},
]


def wait_health(timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/api/health", timeout=3) as r:
                if r.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1.0)
    raise SystemExit(f"server not ready: {BASE}")


def main() -> None:
    from playwright.sync_api import sync_playwright

    wait_health()
    SHOT.mkdir(parents=True, exist_ok=True)
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1100})
        page.goto(f"{BASE}/", wait_until="networkidle")

        for case in CASES:
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=60_000)
            page.wait_for_selector("#customerReplyWrap:not(.hidden)", timeout=30_000)

            meta = page.locator("#matchMeta").inner_text()
            fold = page.locator("#customerReplyFold")
            fold.evaluate("el => { el.open = true; }")
            time.sleep(0.2)
            disclaimer = page.locator(".customer-reply-disclaimer").inner_text()
            body = page.evaluate(
                '() => document.getElementById("customerReplyBody").textContent || ""'
            )

            top_ok = case["gid"] in meta
            has_tpl = "Please help us confirm" in body
            has_disclaimer = "非自动生成的政策承诺" in disclaimer
            zh_main = page.locator("#answer").inner_text()
            zh_ok = len(zh_main) > 50 and "Please help us confirm" not in zh_main

            shot = SHOT / f"{case['id']}_crt_fold.png"
            page.locator("#answerPanel").screenshot(path=str(shot))

            ok = top_ok and has_tpl and has_disclaimer and zh_ok
            rows.append(
                {
                    "id": case["id"],
                    "gid": case["gid"],
                    "ok": ok,
                    "tpl_len": len(body),
                    "screenshot": str(shot.relative_to(ROOT)),
                }
            )

        browser.close()

    out = ROOT / "_scratch/eval/tc148_crt_browser_result.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(1 for r in rows if r["ok"])
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"TC148_CRT_UI: {passed}/{len(rows)} PASS")
    if passed < len(rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
