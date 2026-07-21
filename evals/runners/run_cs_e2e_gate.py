#!/usr/bin/env python3
"""Formal CS E2E gate runner — domain-pack gate ids + report under eval_runs/."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from evals.runners._env import load_dotenv  # noqa: E402

load_dotenv()

import yaml  # noqa: E402
from agents.cs_email_workflow import run_cs_email_workflow  # noqa: E402
from domains.eval_pack import resolve_search_query  # noqa: E402
from evals.runners.gate_report import get_gate_scenario_ids, write_probe_markdown  # noqa: E402
from library_router import load_unified_libraries  # noqa: E402

DEFAULT_MODEL = "_scratch/modelscope/BAAI/bge-m3"
DEFAULT_DOMAIN = "topens"
REPORT_DIR = ROOT / "_scratch" / "eval_runs"
SCRATCH_EVAL_DIR = ROOT / "_scratch" / "eval"

# Backward-compatible alias for merge_cs_e2e_gate_results.py
GATE_SCENARIO_IDS = get_gate_scenario_ids(DEFAULT_DOMAIN)


def load_gate_pack(domain_id: str = DEFAULT_DOMAIN) -> dict:
    path = ROOT / "domains" / domain_id / "evals" / "gates.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not data:
        raise SystemExit(f"empty gate pack: {path}")
    return data


def resolve_map_path(gate_pack: dict) -> Path:
    rel = gate_pack.get("case_map_relpath") or "_scratch/eval/cs_email_query_map.json"
    return ROOT / rel


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


def run_case(
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

    wf = run_cs_email_workflow(
        email,
        libraries,
        search_query=query,
        domain_id=domain_id,
        generate=generate,
        api_key=api_key,
        scenario_id=sid,
        dedupe_hits=False,
    )

    top1_group = wf.top3_group_ids[0] if wf.top3_group_ids else None
    top1_hit = top1_group in ok if ok else None
    lib_hit = exp_lib is None or wf.matched_library == exp_lib

    wf.trace.validation_result = {"top1_hit": top1_hit, "library_hit": lib_hit}

    return {
        "scenario_id": sid,
        "test_id": scenario.get("test_id"),
        "mail_num": scenario.get("mail_num"),
        "label": scenario.get("file", "").split("/")[-1].replace(".md", ""),
        "query": query,
        "expected_library": exp_lib,
        "expected_groups": sorted(ok),
        "matched_library": wf.matched_library,
        "routing_method": wf.routing_method,
        "library_hit": lib_hit,
        "top1_group": top1_group,
        "top1_hit": top1_hit,
        "top3_groups": wf.top3_group_ids,
        "context_zh_leak": wf.context_zh_leak,
        "truncated": wf.llm_truncated,
        "style": wf.style_meta(repo_root=ROOT),
        "reply_preview": (wf.generated_answer or "")[:800] if wf.generated_answer else None,
        "reply_full": wf.generated_answer,
        "reply_len": len(wf.generated_answer or ""),
        "trace": wf.trace.to_dict(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Formal E2E CS gate runner")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--index", choices=("zh", "en"), default="en")
    parser.add_argument("--ids", nargs="*", default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=REPORT_DIR,
        help="Report directory (default: _scratch/eval_runs)",
    )
    parser.add_argument(
        "--scratch-legacy-output",
        action="store_true",
        help="Also write _scratch/eval/cs_e2e_gate_results.json + phase0_gate_probe.md",
    )
    args = parser.parse_args()

    gate_pack = load_gate_pack(args.domain)
    map_path = resolve_map_path(gate_pack)
    ids = args.ids or list(gate_pack.get("gate_scenario_ids") or [])

    from generate_answer import _get_config

    api_key = _get_config()[0] if args.generate else None
    if args.generate and not api_key:
        print("ERROR: --generate requires QA_API_KEY", file=sys.stderr)
        return 1

    scenarios = load_scenarios(map_path)
    libraries = load_unified_libraries(model=args.model, index=args.index)

    results = []
    for sid in ids:
        sc = scenarios.get(sid)
        if not sc:
            print(f"WARN unknown scenario {sid}", file=sys.stderr)
            continue
        row = run_case(
            sc,
            libraries,
            generate=args.generate,
            api_key=api_key,
            domain_id=args.domain,
        )
        results.append(row)
        flag = "OK" if row.get("top1_hit") else ("n/a" if row["expected_groups"] == [] else "MISS")
        print(
            f"{sid} · lib={row['matched_library']} top1={row['top1_group']} [{flag}]"
            + (f" · style={row['style']['family_id']}" if row.get("style") else "")
            + (" · zh_leak" if row["context_zh_leak"] else "")
        )

    stamp = date.today().isoformat()
    payload = {
        "generated": stamp,
        "domain": args.domain,
        "model": args.model,
        "index": args.index,
        "generate": args.generate,
        "results": results,
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f"cs_e2e_gate_{stamp}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")

    if args.scratch_legacy_output:
        legacy_json = SCRATCH_EVAL_DIR / "cs_e2e_gate_results.json"
        legacy_md = SCRATCH_EVAL_DIR / "phase0_gate_probe.md"
        legacy_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        write_probe_markdown(payload, legacy_md)
        print(f"Wrote {legacy_json}")
        print(f"Wrote {legacy_md}")

    return 0


def main_scratch_compat() -> int:
    """Legacy CLI: same as --scratch-legacy-output to _scratch/eval/."""
    if "--scratch-legacy-output" not in sys.argv:
        sys.argv.append("--scratch-legacy-output")
    if "--out-dir" not in sys.argv:
        sys.argv.extend(["--out-dir", str(REPORT_DIR)])
    return main()


if __name__ == "__main__":
    raise SystemExit(main())
