#!/usr/bin/env python3
"""V1.1 #2 · demo LLM=on path screenshots + gate (playwright)."""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHOT = ROOT / "_scratch/eval/screenshots/v1_handtest_llm_on"

AD5S = "http://127.0.0.1:8765"
TC148 = "http://127.0.0.1:8766"

AD5S_CASES = [
    {"id": "L-P23", "query": "电机电流小 并接机臂排查", "gid": "qa_023"},
    {"id": "L-P24", "query": "走停加电阻 二极管怎么接", "gid": "qa_024"},
    {"id": "L-TA10", "query": "按遥控器完全没有反应", "gid": "qa_010"},
    {"id": "L-YT29", "query": "拆机臂内部怎么润滑", "gid": "qa_029"},
    {"id": "L-TA01", "query": "控制板灯不亮", "gid": "qa_001"},
]

TC148_CASES = [
    {"id": "L-T2", "query": "TC148 没反应 遥控器正常", "gid": "qa_002"},
    {"id": "L-T3", "query": "push button 端口短接 O/S/C COM", "gid": "qa_002"},
]


def wait_health(base: str, timeout: float = 180.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base}/api/health", timeout=3) as r:
                if r.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(1.0)
    raise SystemExit(f"server not ready: {base}")


def llm_configured(base: str) -> bool:
    with urllib.request.urlopen(f"{base}/api/config", timeout=10) as r:
        return bool(json.loads(r.read()).get("llm_configured"))


def run_suite(base: str, cases: list[dict], lib: str) -> list[dict]:
    from playwright.sync_api import sync_playwright

    wait_health(base)
    if not llm_configured(base):
        raise SystemExit(f"{lib}: LLM not configured (QA_API_KEY)")

    SHOT.mkdir(parents=True, exist_ok=True)
    out: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 1000})
        page.goto(f"{base}/", wait_until="networkidle")

        if not page.locator("#useLlm").is_checked():
            page.locator("#useLlm").check()

        for case in cases:
            page.locator("#query").fill(case["query"])
            page.locator("#btn").click()
            page.wait_for_selector("#results.visible", timeout=120_000)
            # Wait for LLM polish or failure message
            page.wait_for_function(
                """() => {
                  const w = document.getElementById('llmPolishWrap');
                  const t = document.getElementById('llmPolish');
                  return w && !w.classList.contains('hidden') && t && t.textContent.trim().length > 5;
                }""",
                timeout=120_000,
            )
            time.sleep(0.5)

            meta = page.locator("#matchMeta").inner_text()
            gid = case["gid"]
            top_ok = gid in meta
            llm_text = page.locator("#llmPolish").inner_text().strip()
            llm_ok = len(llm_text) > 20 and "未配置" not in llm_text and "调用失败" not in llm_text
            manual_visible = (
                not page.locator("#ladderWrap").evaluate("el => el.classList.contains('hidden')")
                or not page.locator("#answer").evaluate("el => el.classList.contains('hidden')")
            )
            n_links = page.locator("#answerLinks a").count()

            shot = SHOT / f"{case['id']}.png"
            page.locator("#answerPanel").screenshot(path=str(shot))

            ok = top_ok and llm_ok and manual_visible
            reasons = []
            if not top_ok:
                reasons.append(f"top1 mismatch in meta: {meta[:80]}")
            if not llm_ok:
                reasons.append(f"llm: {llm_text[:60]}")
            if not manual_visible:
                reasons.append("manual steps hidden")

            out.append(
                {
                    "lib": lib,
                    "id": case["id"],
                    "query": case["query"],
                    "expect_gid": gid,
                    "ok": ok,
                    "llm_len": len(llm_text),
                    "links": n_links,
                    "screenshot": str(shot.relative_to(ROOT)),
                    "reasons": reasons,
                }
            )

        browser.close()
    return out


def main() -> None:
    all_rows = run_suite(AD5S, AD5S_CASES, "AD5S") + run_suite(TC148, TC148_CASES, "TC148")
    passed = sum(1 for r in all_rows if r["ok"])
    out_path = ROOT / "_scratch/eval/v1_handtest_llm_on_result.json"
    out_path.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(all_rows, ensure_ascii=False, indent=2))
    print(f"V1_LLM_ON: {passed}/{len(all_rows)} PASS · shots in {SHOT}")
    if passed < len(all_rows):
        sys.exit(1)


if __name__ == "__main__":
    main()
