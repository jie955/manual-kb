#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 1 · English CS retrieval baseline over cs_email_query_map.json (176 queries)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from library_router import load_unified_libraries, pick_library, unified_search

DEFAULT_MODEL = "_scratch/modelscope/BAAI/bge-m3"
MAP_PATH = Path(__file__).resolve().parent / "cs_email_query_map.json"

def load_libraries(model: str, *, k: int, index: str):
    return load_unified_libraries(model, k=k, index=index)


def load_map(path: Path) -> tuple[list[dict], dict[str, dict]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    scenarios = {s["id"]: s for s in data["scenarios"]}
    return data["queries"], scenarios


def acceptable_groups(item: dict, scenario: dict | None) -> set[str]:
    groups = set(item.get("expected_group_ids") or [])
    if scenario:
        groups.update(scenario.get("expected_group_ids") or [])
        groups.update(scenario.get("alternate_group_ids") or [])
    return {g for g in groups if g}


def mrr_rank(hit_groups: list[str], ok: set[str]) -> float:
    for i, g in enumerate(hit_groups, start=1):
        if g in ok:
            return 1.0 / i
    return 0.0


def evaluate_query(
    item: dict,
    scenario: dict | None,
    libraries,
) -> dict:
    query = item["query"]
    routing, hits = unified_search(query, libraries)
    hit_groups = [h.group_id for h in hits]
    ok = acceptable_groups(item, scenario)
    exp_lib = item.get("expected_library") or (scenario or {}).get("expected_library")
    corpus = item.get("corpus_mapping") or (scenario or {}).get("corpus_mapping")

    top1_group = hit_groups[0] if hit_groups else None
    top1_hit = bool(ok and top1_group in ok)
    top3_hit = bool(ok and set(hit_groups[:3]) & ok)
    lib_hit = exp_lib is None or routing.matched_library == exp_lib

    top_hit = hits[0] if hits else None
    block = libraries[routing.matched_library].chunk_by_id.get(top_hit.chunk_id, {}) if top_hit else {}

    return {
        "id": item["id"],
        "scenario_id": item.get("scenario_id"),
        "tier": item.get("tier"),
        "corpus_mapping": corpus,
        "query": query,
        "expected_library": exp_lib,
        "expected_group_ids": sorted(ok),
        "matched_library": routing.matched_library,
        "routing_method": routing.routing_method,
        "library_scores": routing.library_scores,
        "keyword_hits": routing.keyword_hits,
        "library_hit": lib_hit,
        "top1_group": top1_group,
        "top1_question": block.get("question"),
        "top1_score": top_hit.score if top_hit else None,
        "top1_hit": top1_hit if ok else None,
        "top3_hit": top3_hit if ok else None,
        "top3_groups": hit_groups[:3],
        "mrr": mrr_rank(hit_groups, ok) if ok else None,
        "scorable": bool(ok),
    }


def summarize(rows: list[dict], label: str) -> dict:
    scored = [r for r in rows if r["scorable"]]
    n = len(scored)
    if not n:
        return {"label": label, "total": len(rows), "scorable": 0}
    top1 = sum(1 for r in scored if r["top1_hit"])
    top3 = sum(1 for r in scored if r["top3_hit"])
    mrr = sum(r["mrr"] or 0.0 for r in scored) / n
    lib_scored = [r for r in rows if r.get("expected_library")]
    lib_hits = sum(1 for r in lib_scored if r.get("library_hit"))
    return {
        "label": label,
        "total": len(rows),
        "scorable": n,
        "top1_hits": top1,
        "top3_hits": top3,
        "top1_acc": round(top1 / n, 4),
        "top3_acc": round(top3 / n, 4),
        "mrr": round(mrr, 4),
        "routing_labeled": len(lib_scored),
        "routing_hits": lib_hits,
        "routing_acc": round(lib_hits / len(lib_scored), 4) if lib_scored else None,
    }


def render_md(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# English CS Retrieval Baseline · Task 1",
        "",
        f"**Generated**: {payload['generated']}",
        f"**Model**: `{payload['model']}` · **Queries**: {payload['query_count']}",
        "",
        "## Summary",
        "",
        "| Slice | N | Scorable | Top1 | Top3 | MRR | Routing acc |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in (
        "all",
        "tier_a_verbatim",
        "corpus_direct",
        "corpus_logic",
        "corpus_out",
        "gate_direct_logic_tier_a",
    ):
        row = s[key]
        ra = row.get("routing_acc")
        ra_s = f"{ra:.1%}" if ra is not None else "—"
        lines.append(
            f"| {row['label']} | {row['total']} | {row.get('scorable', 0)} | "
            f"{row.get('top1_acc', '—')} | {row.get('top3_acc', '—')} | "
            f"{row.get('mrr', '—')} | {ra_s} |"
        )

    lines.extend(
        [
            "",
            "## Routing method (all queries)",
            "",
        ]
    )
    for method, count in payload["routing_methods"].items():
        lines.append(f"- **{method}**: {count}")

    misses = [r for r in payload["details"] if r["scorable"] and not r["top1_hit"]]
    lines.extend(["", f"## Top1 misses (scorable) · {len(misses)}", ""])
    for r in misses[:40]:
        q_disp = (r["query"][:72] + "…") if len(r["query"]) > 72 else r["query"]
        lines.append(
            f"- `{r['id']}` · {r['corpus_mapping']} · "
            f"exp `{r['expected_group_ids']}` → got `{r['top1_group']}` "
            f"({r['matched_library']}/{r['routing_method']}) · `{q_disp}`"
        )
    if len(misses) > 40:
        lines.append(f"- … and {len(misses) - 40} more (see JSON)")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="English CS retrieval baseline")
    parser.add_argument("--map", type=Path, default=MAP_PATH)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("-k", type=int, default=5)
    parser.add_argument("--index", choices=("zh", "en"), default="zh", help="zh=chroma_captioned · en=chroma_captioned_en")
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--md-out", type=Path, default=None)
    args = parser.parse_args()

    suffix = "" if args.index == "zh" else "_en"
    json_default = Path(__file__).parent / f"cs_en_retrieval_baseline{suffix}.json"
    md_default = Path(__file__).parent / f"cs_en_retrieval_baseline{suffix}.md"
    json_out = args.json_out or json_default
    md_out = args.md_out or md_default

    queries, scenarios = load_map(args.map)
    print(f"loading libraries ({args.index}) + {args.model} …", file=sys.stderr)
    libraries = load_libraries(args.model, k=args.k, index=args.index)

    details: list[dict] = []
    for i, item in enumerate(queries, 1):
        scen = scenarios.get(item.get("scenario_id") or "")
        details.append(evaluate_query(item, scen, libraries))
        if i % 20 == 0:
            print(f"  {i}/{len(queries)}", file=sys.stderr)

    slices: dict[str, list[dict]] = {
        "all": details,
        "tier_a_verbatim": [r for r in details if r["tier"] == "A_verbatim"],
        "corpus_direct": [r for r in details if r["corpus_mapping"] == "direct"],
        "corpus_logic": [r for r in details if r["corpus_mapping"] == "logic"],
        "corpus_out": [r for r in details if r["corpus_mapping"] == "out"],
        "gate_direct_logic_tier_a": [
            r
            for r in details
            if r["tier"] == "A_verbatim" and r["corpus_mapping"] in ("direct", "logic")
        ],
    }

    summary = {key: summarize(rows, key) for key, rows in slices.items()}
    routing_methods = dict(Counter(r["routing_method"] for r in details))

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": args.model,
        "index": args.index,
        "query_count": len(queries),
        "map_path": str(args.map.relative_to(ROOT)).replace("\\", "/"),
        "summary": summary,
        "routing_methods": routing_methods,
        "details": details,
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_md(payload), encoding="utf-8")

    print(json.dumps(summary["all"], ensure_ascii=False, indent=2), file=sys.stderr)
    print(json.dumps(summary["gate_direct_logic_tier_a"], ensure_ascii=False, indent=2), file=sys.stderr)
    print(f"wrote {json_out}", file=sys.stderr)
    print(f"wrote {md_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
