"""BL-V1-07 browser sign-off: thin-ZH EN supplement block styling & visibility.

Requires qa_server on :8765 (AD5S prod chroma).
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8765"
SHOT_DIR = Path(__file__).resolve().parent / "screenshots" / "bl_v1_07"

EN_LABEL = "英文操作步骤（中文正文过短"

CASES = [
    # batch1 + N1 — must show labeled EN supplement
    {"id": "b01", "query": "门自己乱开乱关怎么回事", "expect_group": "qa_031", "expect_en_block": True},
    {"id": "b02", "query": "缓停止不对 没有缓停效果", "expect_group": "qa_032", "expect_en_block": True},
    {"id": "b03", "query": "自动关门功能没用 不会自己关", "expect_group": "qa_033", "expect_en_block": True},
    {"id": "b04", "query": "风大能把门吹开一点怎么办", "expect_group": "qa_034", "expect_en_block": True},
    {"id": "N1", "query": "日常保养润滑", "expect_group": "qa_028", "expect_en_block": True},
    # install_mode extreme_ratio — intentional trigger (qa_016–019 family)
    {
        "id": "install_pull",
        "query": "拉开门安装",
        "expect_group": "qa_016",
        "expect_en_block": True,
        "note": "extreme_ratio · 步骤数≠内容详尽度 · install_mode 族",
    },
    # must NOT show EN supplement
    {"id": "a01", "query": "控制板灯不亮", "expect_group": "qa_001", "expect_en_block": False},
    {"id": "a14", "query": "门刚动一下就停 电机电流", "expect_group": "qa_022", "expect_en_block": False},
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

    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
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
                "return m && m.textContent.trim().length > 0 && a && a.innerHTML.trim().length > 3; }",
                timeout=120_000,
            )

            n_sup = page.locator("#answer .answer-en-supplement").count()
            label_text = ""
            if n_sup:
                label_text = page.locator("#answer .answer-en-label").first.inner_text().strip()
            zh_pre = page.locator("#answer pre.steps").count()
            answer_html = page.locator("#answer").inner_html()
            answer_text = page.locator("#answer").inner_text().strip()
            meta = page.locator("#matchMeta").inner_text().strip()

            # DOM order: zh pre before en supplement
            zh_before_en = True
            if n_sup and zh_pre:
                zh_before_en = page.locator("#answer").evaluate(
                    """el => {
                      const pre = el.querySelector('pre.steps');
                      const sup = el.querySelector('.answer-en-supplement');
                      if (!pre || !sup) return true;
                      return pre.compareDocumentPosition(sup) & Node.DOCUMENT_POSITION_FOLLOWING;
                    }"""
                )

            api = api_probe(case["query"])
            top = (api.get("hits") or [{}])[0]
            top_gid = top.get("group_id", "")

            ok = True
            reasons: list[str] = []
            if console_errors:
                ok = False
                reasons.append(f"js_errors={console_errors[:3]}")
            if top_gid != case["expect_group"]:
                ok = False
                reasons.append(f"top1={top_gid} want {case['expect_group']}")
            if case["expect_en_block"]:
                if n_sup < 1:
                    ok = False
                    reasons.append("missing .answer-en-supplement")
                if EN_LABEL not in label_text:
                    ok = False
                    reasons.append(f"bad label: {label_text!r}")
                if len(answer_text) < 200:
                    ok = False
                    reasons.append(f"answer too short for thin+en ({len(answer_text)})")
                if zh_pre < 1 and top_gid != "qa_028":
                    ok = False
                    reasons.append("missing pre.steps zh block")
                if not zh_before_en:
                    ok = False
                    reasons.append("EN block before ZH (wrong order)")
            else:
                if n_sup > 0:
                    ok = False
                    reasons.append("unexpected .answer-en-supplement")
                if EN_LABEL in answer_text:
                    ok = False
                    reasons.append("EN label leaked into non-thin answer")

            shot = SHOT_DIR / f"{case['id']}.png"
            page.locator("#results").screenshot(path=str(shot))

            results.append(
                {
                    "id": case["id"],
                    "query": case["query"],
                    "ok": ok,
                    "top1": top_gid,
                    "expect_en_block": case["expect_en_block"],
                    "n_supplement": n_sup,
                    "label": label_text[:60],
                    "zh_pre": zh_pre,
                    "answer_len": len(answer_text),
                    "zh_before_en": zh_before_en,
                    "meta": meta[:100],
                    "screenshot": str(shot.relative_to(SHOT_DIR.parent.parent)),
                    "reasons": reasons,
                    "note": case.get("note"),
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
    print(f"BL_V1_07_BROWSER: {len(rows)}/{len(rows)} PASS, screenshots in {SHOT_DIR}")


if __name__ == "__main__":
    main()
