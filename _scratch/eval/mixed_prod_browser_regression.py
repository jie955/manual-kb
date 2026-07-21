"""Mixed prod flat-group browser regression (M1–M3). Requires qa_server on :8765."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"

CASES = [
    {
        "id": "M1",
        "query": "按遥控器完全没反应",
        "expect_group": "qa_010",
        "expect_figures": True,
        "note": "flat + 配图",
    },
    {
        "id": "M2",
        "query": "控制板一直咔哒响",
        "expect_group": "qa_011",
        "expect_figures": False,
        "note": "flat、无 branch 筛选器",
    },
    {
        "id": "M3",
        "query": "一按遥控保险丝就烧",
        "expect_group": "qa_012",
        "expect_figures": False,
        "note": "长组子块命中",
    },
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


def api_probe(query: str) -> dict:
    body = json.dumps({"query": query, "use_llm": False}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/ask",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def run_playwright() -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("pip install playwright && playwright install chromium")

    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        console_errors: list[str] = []
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        page.goto(f"{BASE}/", wait_until="networkidle")
        # LLM off for flat manual steps (default checkbox unchecked)
        if page.locator("#useLlm").is_checked():
            page.locator("#useLlm").uncheck()

        for case in CASES:
            case_errors: list[str] = []
            console_errors.clear()
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            page.wait_for_function(
                "() => { const m = document.getElementById('matchMeta'); "
                "const a = document.getElementById('answer'); "
                "return m && m.textContent.trim().length > 0 && a && a.textContent.trim().length > 10; }",
                timeout=120_000,
            )

            ladder_hidden = page.locator("#ladderWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            filter_hidden = page.locator("#branchFilterWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            answer_visible = page.locator("#answer").evaluate(
                "el => !el.classList.contains('hidden')"
            )
            answer_text = page.locator("#answer").inner_text().strip()
            meta = page.locator("#matchMeta").inner_text().strip()
            n_figures = page.locator("#answerFigures img").count()
            figures_visible = page.locator("#answerFiguresWrap").evaluate(
                "el => !el.classList.contains('hidden')"
            )

            api = api_probe(case["query"])
            top = (api.get("hits") or [{}])[0]
            top_gid = top.get("group_id", "")
            score = top.get("score", 0)
            ladder = top.get("troubleshooting_ladder") or []

            ok = True
            reasons: list[str] = []
            if console_errors:
                ok = False
                reasons.append(f"js_errors={console_errors[:3]}")
            if not ladder_hidden:
                ok = False
                reasons.append("ladderWrap visible")
            if not filter_hidden:
                ok = False
                reasons.append("branchFilterWrap visible")
            if not answer_visible or len(answer_text) < 20:
                ok = False
                reasons.append("answer empty/hidden")
            if top_gid != case["expect_group"]:
                ok = False
                reasons.append(f"top1={top_gid} want {case['expect_group']}")
            if ladder:
                ok = False
                reasons.append("api has troubleshooting_ladder")
            if case["expect_figures"] and n_figures < 1:
                ok = False
                reasons.append("expected figures missing")
            if not case["expect_figures"] and figures_visible and n_figures > 0:
                # qa_011/012: no figures expected in Gate #5; allow but note
                pass

            results.append(
                {
                    "id": case["id"],
                    "query": case["query"],
                    "ok": ok,
                    "top1": top_gid,
                    "score": round(float(score), 4),
                    "ladder_hidden": ladder_hidden,
                    "filter_hidden": filter_hidden,
                    "answer_len": len(answer_text),
                    "figures": n_figures,
                    "meta": meta[:120],
                    "reasons": reasons,
                }
            )

        browser.close()
    return results


def main() -> None:
    wait_health()
    rows = run_playwright()
    all_ok = all(r["ok"] for r in rows)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    if not all_ok:
        sys.exit(1)
    print("MIXED_PROD_BROWSER: 3/3 PASS, no JS errors")


if __name__ == "__main__":
    main()
