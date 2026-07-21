#!/usr/bin/env python3
"""Formal Joyce 22-mail batch runner — reports under _scratch/eval_runs/."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from evals.runners._env import load_dotenv  # noqa: E402

load_dotenv()

import yaml  # noqa: E402
from agents.cs_email_workflow import run_cs_email_workflow  # noqa: E402
from domains.eval_pack import resolve_search_query, pinned_images  # noqa: E402
from generate_answer import _get_config  # noqa: E402
from library_router import load_unified_libraries  # noqa: E402

DEFAULT_MODEL = "_scratch/modelscope/BAAI/bge-m3"
DEFAULT_DOMAIN = "topens"
REPORT_DIR = ROOT / "_scratch" / "eval_runs"


def load_gate_pack(domain_id: str = DEFAULT_DOMAIN) -> dict:
    path = ROOT / "domains" / domain_id / "evals" / "gates.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_scenarios(map_path: Path) -> dict[str, dict]:
    data = json.loads(map_path.read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["scenarios"]}


def customer_email(scenario: dict) -> str:
    verbatim = scenario.get("verbatim_customer") or []
    if verbatim:
        return verbatim[0] if len(verbatim) == 1 else "\n\n".join(verbatim[:2])
    return scenario.get("primary_query") or ""


def acceptable_groups(scenario: dict) -> set[str]:
    groups = set(scenario.get("expected_group_ids") or [])
    groups.update(scenario.get("alternate_group_ids") or [])
    return {g for g in groups if g}


def is_tc148_case(expected_library: str | None, matched_library: str) -> bool:
    return expected_library == "tc148" or matched_library == "tc148"


def run_case_with_images(
    scenario: dict,
    libraries,
    *,
    generate: bool,
    api_key: str | None,
    domain_id: str,
) -> dict:
    sid = scenario["id"]
    email = customer_email(scenario)
    query = resolve_search_query(
        scenario, email, scenario_id=sid, domain_id=domain_id
    )
    ok = acceptable_groups(scenario)
    exp_lib = scenario.get("expected_library")
    mail_type = scenario.get("type") or "troubleshoot"

    wf = run_cs_email_workflow(
        email,
        libraries,
        search_query=query,
        domain_id=domain_id,
        generate=generate,
        api_key=api_key,
        scenario_id=sid,
        mail_type=mail_type,
        dedupe_hits=False,
    )

    top1_group = wf.top3_group_ids[0] if wf.top3_group_ids else None
    top1_hit = (top1_group in ok) if ok else None

    images_used: list = []
    links_used: list = []
    for h in wf.gen_hits:
        images_used.extend(h.get("images") or [])
        links_used.extend(h.get("links") or [])
    images_used.extend(pinned_images(sid, domain_id=domain_id))

    tc148 = is_tc148_case(exp_lib, wf.matched_library)
    reply_audit = wf.reply_audit or {}

    return {
        "scenario_id": sid,
        "mail_num": scenario.get("mail_num"),
        "raw_email": email,
        "expected_library": exp_lib,
        "matched_library": wf.matched_library,
        "routing_method": wf.routing_method,
        "is_tc148": tc148,
        "top1_group": top1_group,
        "top1_hit": top1_hit,
        "top3_groups": wf.top3_group_ids,
        "images_used": images_used,
        "links_used": links_used,
        "style": wf.style_meta(),
        "generated_reply_en": wf.generated_answer,
        "reply_truncated": wf.llm_truncated,
        "reply_incomplete_reason": wf.incomplete_reason,
        "reply_audit": reply_audit,
        "reply_len": len(wf.generated_answer or ""),
        "context_zh_leak": wf.context_zh_leak,
        "trace": wf.trace.to_dict(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Formal Joyce 22-mail batch runner")
    ap.add_argument("--domain", default=DEFAULT_DOMAIN)
    ap.add_argument("--round", required=True, help="round0 or round1 (stored in meta)")
    ap.add_argument("--index", default="en", choices=("zh", "en"))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--generate", action="store_true")
    ap.add_argument(
        "--no-eval-pack",
        action="store_true",
        help="Disable EvalPack YAML (generation/pinned/ref/boost) for patch-off validation",
    )
    args = ap.parse_args()

    if args.no_eval_pack:
        os.environ["EVAL_PACK_DISABLED"] = "1"

    gate_pack = load_gate_pack(args.domain)
    map_path = ROOT / (
        gate_pack.get("case_map_relpath") or "_scratch/eval/cs_email_query_map.json"
    )
    ids = list(gate_pack.get("joyce_22_ids") or [f"cs_{i:04d}" for i in range(1, 23)])

    api_key = _get_config()[0] if args.generate else None
    if args.generate and not api_key:
        print("ERROR: --generate requires QA_API_KEY", file=sys.stderr)
        return 1

    scenarios = load_scenarios(map_path)
    libraries = load_unified_libraries(model=DEFAULT_MODEL, index=args.index)

    results = []
    for sid in ids:
        sc = scenarios.get(sid)
        if not sc:
            print(f"WARN unknown scenario_id={sid}, skip", file=sys.stderr)
            continue
        row = run_case_with_images(
            sc,
            libraries,
            generate=args.generate,
            api_key=api_key,
            domain_id=args.domain,
        )
        mail_num = sc.get("mail_num") or (len(results) + 1)
        row["mail_id"] = f"MAIL-{int(mail_num):02d}"
        row["mvp19"] = "否" if row["is_tc148"] else "是"
        results.append(row)
        print(
            f"{row['mail_id']} ({sid}) · lib={row['matched_library']} "
            f"· mvp19={row['mvp19']} · images={len(row['images_used'])} · top1={row['top1_group']}"
        )

    out = args.out or (
        REPORT_DIR / f"cs_22mail_{args.round}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    payload = {
        "meta": {
            "round": args.round,
            "domain": args.domain,
            "index": args.index,
            "eval_pack_disabled": args.no_eval_pack,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total": len(results),
            "mvp19_count": sum(1 for r in results if r["mvp19"] == "是"),
            "note": "System output only. Human scoring stays external.",
        },
        "results": results,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} · {len(results)} cases · MVP19={payload['meta']['mvp19_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
