#!/usr/bin/env python3
"""Diagnose cs_0024 generation + cs_0013/cs_0026 retrieval."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runners.run_cs_e2e_gate import (  # noqa: E402
    DEFAULT_MODEL,
    customer_email,
    load_scenarios,
    run_case,
)
from evals.runners._env import load_dotenv as _load_dotenv  # noqa: E402
from generate_answer import (  # noqa: E402
    _chat_url,
    _get_config,
    build_cs_email_system_prompt,
)
from context_builder import build_context_for_hits  # noqa: E402
from library_router import hits_to_context, load_unified_libraries, unified_search  # noqa: E402
from generate_answer import CS_EMAIL_SYSTEM_PROMPT_EN  # noqa: E402

_load_dotenv()


def diag_retrieval(sid: str) -> None:
    sc = _scenarios()[sid]
    libs = load_unified_libraries(model=DEFAULT_MODEL)
    print(f"\n=== Retrieval · {sid} ===")
    print(f"expected: lib={sc.get('expected_library')} groups={sc.get('expected_group_ids')}")
    for label, q in [
        ("primary_query", sc.get("primary_query") or ""),
        ("customer_email", customer_email(sc)),
    ]:
        routing, hits = unified_search(q, libs)
        top3 = [(h.group_id, round(h.score, 4)) for h in hits[:3]]
        print(f"  [{label}] method={routing.routing_method} lib={routing.matched_library}")
        print(f"    top3: {top3}")


def diag_cs_0024_api() -> None:
    sid = "cs_0024"
    sc = _scenarios()[sid]
    libs = load_unified_libraries(model=DEFAULT_MODEL)
    email = customer_email(sc)
    routing, hits = unified_search(email, libs)
    lib = libs[routing.matched_library]
    ctx_rows = hits_to_context(hits[:3], lib.chunk_by_id)
    gen_hits = [
        {
            "section": r.get("section"),
            "question": r.get("question"),
            "content_zh": r.get("content_zh"),
            "content_en": r.get("content_en"),
            "images": r.get("images") or [],
            "links": r.get("links") or [],
            "customer_reply_templates": r.get("customer_reply_templates") or [],
            "group_id": r.get("group_id"),
        }
        for r in ctx_rows
    ]
    context_parts = build_context_for_hits(gen_hits, locale="en", response_mode="cs_email")
    system, sel = build_cs_email_system_prompt(
        section=str(gen_hits[0].get("section") or ""),
        question=str(gen_hits[0].get("question") or ""),
        customer_email=email,
        hits=gen_hits,
        scenario_id=sid,
        base_prompt=CS_EMAIL_SYSTEM_PROMPT_EN,
    )
    user_content = (
        f"Customer email (English):\n{email}\n\n"
        + "\n\n".join(context_parts)
        + "\n\nWrite the outbound reply email body."
    )
    print(f"\n=== cs_0024 API probe ===")
    print(f"style={sel.family_id if sel else None}")
    print(f"system_len={len(system)} user_len={len(user_content)} email_len={len(email)}")

    api_key, base_url, model = _get_config()
    payload = {
        "model": model,
        "max_tokens": 4096,
        "max_completion_tokens": 4096,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    }
    req = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    reasoning = (msg.get("reasoning_content") or "").strip()
    print(f"finish={choice.get('finish_reason')!r}")
    print(f"content_len={len(content)} reasoning_len={len(reasoning)}")
    print(f"usage={data.get('usage')}")
    if content:
        print("content_head:", content[:300])
    elif reasoning:
        print("reasoning_head:", reasoning[:300])
    else:
        print("EMPTY message keys:", list(msg.keys()))


def main() -> int:
    diag_retrieval("cs_0013")
    diag_retrieval("cs_0026")
    diag_cs_0024_api()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
