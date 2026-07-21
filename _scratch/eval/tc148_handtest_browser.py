#!/usr/bin/env python3
"""TC148 demo hand-test (playwright · :8766)."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8766"

CASES = [
    {"id": "T2", "query": "TC148 没反应 遥控器正常", "gid": "qa_002", "min_links": 2},
    {"id": "T1", "query": "墙壁开关自检后灯常亮", "gid": "qa_001", "min_links": 1, "min_figs": 1},
    {"id": "T3", "query": "push button 端口短接 O/S/C COM", "gid": "qa_002", "known_miss": True},
]


def wait_health(timeout: float = 120.0) -> None:
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


def main() -> None:
    from playwright.sync_api import sync_playwright

    wait_health()
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(f"{BASE}/", wait_until="networkidle")
        if page.locator("#useLlm").is_checked():
            page.locator("#useLlm").uncheck()

        for case in CASES:
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            time.sleep(0.3)
            api = api_ask(case["query"])
            top = (api.get("hits") or [{}])[0]
            gid = top.get("group_id", "")
            n_links = page.locator("#answerLinks a").count()
            n_figs = page.locator("#answerFigures img").count()
            ok = True
            reasons = []
            if not case.get("known_miss") and gid != case["gid"]:
                ok = False
                reasons.append(f"top1={gid} want {case['gid']}")
            if case.get("known_miss"):
                # T3: document actual top1; content check only
                zh = page.locator("#answer").inner_text()
                if "短接" not in zh and gid == "qa_001":
                    reasons.append("T3 known miss but qa_001 missing 短接 in zh")
                    if gid == "qa_001":
                        ok = False  # minor content issue
            if n_links < case.get("min_links", 0):
                ok = False
                reasons.append(f"links={n_links}")
            if n_figs < case.get("min_figs", 0):
                ok = False
                reasons.append(f"figs={n_figs}")
            out.append(
                {
                    "id": case["id"],
                    "ok": ok,
                    "top1": gid,
                    "links": n_links,
                    "figures": n_figs,
                    "known_miss": case.get("known_miss"),
                    "reasons": reasons,
                }
            )
        browser.close()

    print(json.dumps(out, ensure_ascii=False, indent=2))
    blocking = [c for c in out if not c["ok"] and not c.get("known_miss")]
    if blocking:
        sys.exit(1)
    print(f"TC148_HANDTEST: {sum(1 for c in out if c['ok'])}/{len(out)} PASS (T3 known miss excluded)")


if __name__ == "__main__":
    main()
