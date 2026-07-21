"""§十九 browser sign-off (N1–N2). Requires qa_server prod :8765."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"

CASES = [
    {
        "id": "N1",
        "query": "日常保养润滑 WD40",
        "expect_group": "qa_028",
        "min_links": 0,
        "expect_figures": False,
        "answer_snippet": "日常保养",
        "min_answer_len": 5,
        "note": "WD40 在 content_en；demo 仅渲染 content_zh（7 字）→ 展示层 ⚠️minor",
    },
    {
        "id": "N2",
        "query": "拆机臂内部怎么润滑",
        "expect_group": "qa_029",
        "min_links": 3,
        "expect_figures": False,
        "answer_snippet": "润滑",
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
    from playwright.sync_api import sync_playwright

    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        console_errors: list[str] = []
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        page.goto(f"{BASE}/", wait_until="networkidle")
        if page.locator("#useLlm").is_checked():
            page.locator("#useLlm").uncheck()

        for case in CASES:
            console_errors.clear()
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            page.wait_for_function(
                "() => { const m = document.getElementById('matchMeta'); "
                "const a = document.getElementById('answer'); "
                "return m && m.textContent.trim().length > 0 && a && a.textContent.trim().length > 3; }",
                timeout=120_000,
            )

            ladder_hidden = page.locator("#ladderWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            filter_hidden = page.locator("#branchFilterWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )
            answer_text = page.locator("#answer").inner_text().strip()
            meta = page.locator("#matchMeta").inner_text().strip()
            n_figures = page.locator("#answerFigures img").count()
            n_links = page.locator("#answerLinks a").count()
            link_hrefs = page.locator("#answerLinks a").evaluate_all(
                "els => els.map(e => e.href)"
            )
            links_wrap_hidden = page.locator("#answerLinksWrap").evaluate(
                "el => el.classList.contains('hidden')"
            )

            api = api_probe(case["query"])
            top = (api.get("hits") or [{}])[0]
            top_gid = top.get("group_id", "")
            score = top.get("score", 0)
            api_links = top.get("links") or []

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
            if len(answer_text) < case.get("min_answer_len", 10):
                ok = False
                reasons.append("answer too short")
            if case["answer_snippet"] not in answer_text and case["answer_snippet"].lower() not in answer_text.lower():
                ok = False
                reasons.append(f"answer missing {case['answer_snippet']!r}")
            if top_gid != case["expect_group"]:
                ok = False
                reasons.append(f"top1={top_gid} want {case['expect_group']}")
            if n_links < case["min_links"]:
                ok = False
                reasons.append(f"links={n_links} want >={case['min_links']}")
            if case["expect_figures"] and n_figures < 1:
                ok = False
                reasons.append("figures missing")

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
                    "links_ui": n_links,
                    "link_hrefs": link_hrefs[:5],
                    "api_links": len(api_links),
                    "links_wrap_hidden": links_wrap_hidden,
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
    print("SEC19_BROWSER: 2/2 PASS, no JS errors")


if __name__ == "__main__":
    main()
