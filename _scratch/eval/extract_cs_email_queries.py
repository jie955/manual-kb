#!/usr/bin/env python3
"""One-off extractor for customer-service-emails scenario files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CS_DIR = ROOT / "samples" / "customer-service-emails"

MAPPING = {
    "0001-at12131s-gate-no-response.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["power", "4#5#", "remote"],
    },
    "0002-a8132-et24-motor-no-power.md": {
        "corpus": "logic",
        "library": "a3s",
        "groups": ["qa_001", "qa_033"],
        "domains": ["motor", "11#12#", "ET24", "limit"],
    },
    "0003-ad8-leds-respond-gate-wont-open.md": {
        "corpus": "logic",
        "library": "ad5s",
        "groups": ["qa_010", "qa_001"],
        "domains": ["remote", "dual_arm", "DIP"],
        "mapping_note": "LED responds gate won't move · ad5s qa_010 primary · qa_040 is wrong Top1 (§九 mid-travel)",
    },
    "0004-pw302-two-separate-gates-recommendation.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales"],
    },
    "0005-at12132s-dual-swing-solar-jy9132-recommendation.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales", "solar"],
    },
    "0006-a8131-vs-at12131-comparison.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales"],
    },
    "0007-dual-swing-model-comparison-uk-remotes.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales", "remote"],
    },
    "0008-pw502-tc148-push-button-not-working.md": {
        "corpus": "direct",
        "library": "tc148",
        "groups": ["qa_001", "qa_002"],
        "domains": ["TC148", "4#5#", "instant_short"],
    },
    "0009-at6131-tc148-erratic-wired-button.md": {
        "corpus": "direct",
        "library": "tc148",
        "groups": ["qa_001", "qa_002"],
        "domains": ["TC148", "4#5#", "shield", "erratic"],
    },
    "0010-a8131-tc148-no-response.md": {
        "corpus": "direct",
        "library": "tc148",
        "groups": ["qa_001", "qa_002"],
        "domains": ["TC148", "4#5#"],
    },
    "0011-a8132-ad8-at1202-pw802-comparison.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales"],
    },
    "0012-at12131-limit-overswing-stops-halfway.md": {
        "corpus": "logic",
        "library": "a3s",
        "groups": ["qa_020", "qa_021"],
        "domains": ["limit", "pull_push", "FORCE"],
    },
    "0013-a3s-stops-before-fully-open.md": {
        "corpus": "direct",
        "library": "a3s",
        "groups": ["qa_022"],
        "domains": ["stall", "11#12#", "FORCE"],
    },
    "0014-at602-limit-overclose-magnetic-ring.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["limit", "magnetic_ring"],
    },
    "0015-ad8s-auto-close-reverses-second-try.md": {
        "corpus": "direct",
        "library": "ad5s",
        "groups": ["qa_040", "qa_015", "qa_016"],
        "domains": ["auto_close", "delay", "dual_arm"],
    },
    "0016-pw802-red-light-flashing-wont-work.md": {
        "corpus": "logic",
        "library": "ad5s",
        "groups": ["qa_001"],
        "domains": ["power", "dual_arm", "11#12#"],
    },
    "0017-a5131-arm-failed-again-warranty.md": {
        "corpus": "logic",
        "library": "a3s",
        "groups": ["qa_033"],
        "domains": ["motor", "limit", "warranty"],
    },
    "0018-a5-a8-nothing-works-battery-ac.md": {
        "corpus": "direct",
        "library": "a3s",
        "groups": ["qa_001", "qa_002"],
        "domains": ["power", "11#12#", "fuse"],
    },
    "0019-ad5s-opens-too-far-remote-not-recognized.md": {
        "corpus": "direct",
        "library": "ad5s",
        "groups": ["qa_016", "qa_020"],
        "domains": ["limit", "pull_open", "remote", "stall"],
    },
    "0020-at1202-wont-stay-closed-slave-arm.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["limit", "dual_arm", "auto_close"],
    },
    "0021-a8132-board-power-arms-wont-move.md": {
        "corpus": "logic",
        "library": "a3s",
        "groups": ["qa_001"],
        "domains": ["click", "dual_arm", "11#12#"],
    },
    "0022-a5132-opens-then-recloses-resolved.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["limit", "safety_reverse", "pull_push_fork", "dual_arm"],
        "limit_fork": True,
        "mapping_note": "A5132 dual swing · out-of-corpus · runtime ref ad5s/qa_016 n/a · a3s lacks open-bounce group",
    },
    "0023-ad5s-left-gate-auto-close-cycle-erratic.md": {
        "corpus": "direct",
        "library": "ad5s",
        "groups": ["qa_016", "qa_015", "qa_020"],
        "domains": ["auto_close", "dual_arm", "limit"],
        "limit_fork": True,
    },
    "0024-minnesota-solar-at6132s-vs-ad5s-presales.md": {
        "corpus": "out",
        "library": None,
        "groups": [],
        "domains": ["presales", "solar"],
    },
    "0025-tc148-stopped-warranty-replacement-composite.md": {
        "corpus": "direct",
        "library": "tc148",
        "groups": ["qa_001", "qa_002"],
        "domains": ["TC148", "warranty", "composite"],
    },
    "0026-a3a5a8-board-replaced-actuator-no-response.md": {
        "corpus": "direct",
        "library": "a3s",
        "groups": ["qa_001", "qa_033"],
        "domains": ["board", "motor", "limit", "partial_diag"],
    },
    "0027-remote-multiple-press-no-model-generic.md": {
        "corpus": "logic",
        "library": "a3s",
        "groups": ["qa_010"],
        "domains": ["remote", "click", "no_model"],
    },
}


def extract_bodies(text: str) -> list[str]:
    bodies: list[str] = []
    if "## 客户原文" not in text:
        return bodies
    part = text.split("## 客户原文", 1)[1]
    if "## 客服回复" in part:
        part = part.split("## 客服回复", 1)[0]
    for block in re.findall(r"```([\s\S]*?)```", part):
        block = block.strip()
        if "Body:" in block:
            bodies.append(block.split("Body:", 1)[1].strip())
        elif block.startswith(("From:", "Hi", "My Neighbor", "Good evening")):
            skip_prefixes = (
                "From:", "Send Time:", "To:", "Subject:", "On ", "---",
                "You received",
            )
            lines = []
            for ln in block.splitlines():
                s = ln.strip()
                if not s or any(s.startswith(p) for p in skip_prefixes):
                    continue
                if s.startswith(("Country Code:", "Name:", "Where Did You Buy?:",
                                 "Order Number:", "Product Model:", "Country / Region:",
                                 "How Do You Install", "Gate Application:", "Gate Type:",
                                 "Gate Weight", "Gate Length", "List The Accessories")):
                    continue
                lines.append(s)
            if lines:
                bodies.append("\n".join(lines))
    return bodies


def main() -> None:
    scenarios = []
    queries = []
    q_idx = 0
    for p in sorted(CS_DIR.glob("0*.md")):
        text = p.read_text(encoding="utf-8")
        num = p.name[:4]
        mail_num = int(num)
        tier = "test" if mail_num >= 23 else "real"
        meta = {}
        for m in re.finditer(r"\| \*\*([^*]+)\*\* \| ([^|]+) \|", text):
            k, v = m.group(1).strip(), m.group(2).strip()
            if k in ("产品线", "类型", "来源", "测试维度", "渠道"):
                meta[k] = v
        map_info = MAPPING.get(p.name, {})
        bodies = extract_bodies(text)
        file_queries = re.findall(r"^- `([^`]+)`", text, re.M)
        type_raw = meta.get("类型", "") + meta.get("测试维度", "")
        domains = map_info.get("domains", [])
        if "售前" in type_raw or "presales" in domains:
            stype = "presales"
        elif "复合" in type_raw or "composite" in domains:
            stype = "composite"
        else:
            stype = "fault"
        scenario = {
            "id": f"cs_{num}",
            "file": f"samples/customer-service-emails/{p.name}",
            "mail_num": mail_num if tier == "real" else None,
            "test_id": f"T{mail_num - 22}" if tier == "test" else None,
            "tier": tier,
            "type": stype,
            "product_line": meta.get("产品线", ""),
            "corpus_mapping": map_info.get("corpus", "out"),
            "expected_library": map_info.get("library"),
            "expected_group_ids": map_info.get("groups", []),
            "domains": map_info.get("domains", []),
            "limit_fork_case": map_info.get("limit_fork", False),
            "verbatim_customer": bodies,
            "primary_query": file_queries[0] if file_queries else (bodies[0][:200] if bodies else ""),
        }
        scenarios.append(scenario)
        for i, body in enumerate(bodies):
            q_idx += 1
            queries.append({
                "id": f"csq_{q_idx:03d}",
                "lang": "en",
                "tier": "A_verbatim" if tier == "real" else "C_test_prompt",
                "query": body.replace("\n", " ").strip()[:600],
                "scenario_id": scenario["id"],
                "source": "customer_body",
                "expected_library": map_info.get("library"),
                "expected_group_ids": map_info.get("groups", []),
                "corpus_mapping": map_info.get("corpus", "out"),
                "category": "verbatim",
            })
        for fq in file_queries:
            q_idx += 1
            queries.append({
                "id": f"csq_{q_idx:03d}",
                "lang": "en",
                "tier": "B_derived",
                "query": fq,
                "scenario_id": scenario["id"],
                "source": "derived_retrieval_query",
                "expected_library": map_info.get("library"),
                "expected_group_ids": map_info.get("groups", []),
                "corpus_mapping": map_info.get("corpus", "out"),
                "category": "colloquial_en",
            })
    limit_fork = [
        {
            "id": "csq_fork_001",
            "query": "My gate is a pull to open. Does that make a difference?",
            "scenario_id": "cs_0022",
            "note": "install_mode correction · form said Push",
            "needs_install_mode": True,
            "confusable_groups": ["qa_016", "qa_017", "qa_018", "qa_019"],
        },
        {
            "id": "csq_fork_002",
            "query": "left panel reaches full open then immediately starts closing about 4 feet no remote",
            "scenario_id": "cs_0022",
            "note": "safety reverse + limit composite",
            "needs_install_mode": True,
        },
        {
            "id": "csq_fork_003",
            "query": "gate opens too far limit switch B does nothing pull to open",
            "scenario_id": "cs_0012",
            "note": "trunk+fork in one CS email · AT12131",
            "needs_install_mode": True,
        },
        {
            "id": "csq_fork_004",
            "query": "AD5S left gate not opening fully auto close only 2 seconds",
            "scenario_id": "cs_0023",
            "note": "甲方T1 · dual arm + auto close",
            "needs_install_mode": "unknown",
        },
        {
            "id": "csq_fork_005",
            "query": "gate does not stay closed opens again slave arm AT1202 P9 00",
            "scenario_id": "cs_0020",
            "note": "limit + dual slave · no v1 docx",
            "needs_install_mode": True,
        },
    ]
    out = {
        "version": "1.0",
        "generated": "2026-07-07",
        "source_dir": "samples/customer-service-emails/",
        "note": "English eval candidates from 22 real + 5 test CS scenarios. corpus_mapping: direct|logic|out",
        "stats": {
            "scenarios": len(scenarios),
            "queries": len(queries),
            "limit_fork_probes": len(limit_fork),
            "direct_hit": sum(1 for s in scenarios if s["corpus_mapping"] == "direct"),
            "logic_hit": sum(1 for s in scenarios if s["corpus_mapping"] == "logic"),
            "out_of_corpus": sum(1 for s in scenarios if s["corpus_mapping"] == "out"),
        },
        "scenarios": scenarios,
        "queries": queries,
        "limit_fork_probes": limit_fork,
    }
    out_path = Path(__file__).parent / "cs_email_query_map.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({len(scenarios)} scenarios, {len(queries)} queries)")


if __name__ == "__main__":
    main()
