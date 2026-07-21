#!/usr/bin/env python3
"""Phase 1a · Build pilot English Retrieval Index (subset re-embed)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from en_representation import build_embedding_text_en, extract_en_symptom_keywords  # noqa: E402

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"

# Pilot scope: Gate Tier A groups + #1 + TC148 (Plan §5)
PILOT_GROUPS: dict[str, frozenset[str]] = {
    "a3s": frozenset(
        {
            "qa_001",
            "qa_002",
            "qa_011",
            "qa_013",
            "qa_022",
            "qa_025",
            "qa_033",
            "qa_034",
        }
    ),
    "ad5s": frozenset(
        {
            "qa_001",
            "qa_010",
            "qa_015",
            "qa_016",
            "qa_020",
            "qa_040",
        }
    ),
    "tc148": frozenset({"qa_001", "qa_002"}),
}

LIBRARY_CHROMA = {
    "a3s": ROOT / "_scratch/run-007/chroma_captioned",
    "ad5s": ROOT / "_scratch/run-ad5s/chroma_captioned",
    "tc148": ROOT / "_scratch/run-tc148/chroma_captioned",
}

LIBRARY_OUT = {
    "a3s": ROOT / "_scratch/run-007/chroma_captioned_en",
    "ad5s": ROOT / "_scratch/run-ad5s/chroma_captioned_en",
    "tc148": ROOT / "_scratch/run-tc148/chroma_captioned_en",
}

# Gate pilot · authoritative EN troubleshooting (when parent content_en thin/missing)
A3S_ANSWER_EN_PATCH: dict[str, str] = {
    "qa_022": (
        "1 Please detect the voltage of the +BAT- terminals (11# and 12#) on the control board "
        "while pressing the remote to see whether the voltage stays at almost 24V (above 22V). "
        "If the voltage drops too much, the problem may be with the power source. "
        "If the voltage is fine, please proceed to the following tests.\n"
        "2 Please power off the system first (disconnect the power source from the +BAT- terminals). "
        "Turn the FORCE potentiometer all the way clockwise to increase the stall force, and turn "
        "the SOFT STOP potentiometer all the way counter-clockwise to decrease the soft stop period. "
        "Then turn on the power and operate the gate opener through a complete opening and closing cycle. "
        "See whether the gate opens and closes all the way on the next cycle.\n"
        "3 If the problem still persists, push against the gate (in the opposite direction of its movement) "
        "while the gate is opening. Continuously add some load and see whether the gate can open all the way properly.\n"
        "4 If the tests above do not help, please remove the arm from the gate and hold its front mount firmly, "
        "then press the remote to see whether the arm can extend and retract properly each time. "
        "If the arm runs normally in this test, the arm itself is fine — please let me know the weight and length "
        "of your gate, and whether the gate can be opened and closed freely about 3.3 feet (one meter) from the gate hinge."
    ),
}

# TC148 · minimal troubleshooting EN for Gate R (not full template text)
TC148_ANSWER_EN_PATCH: dict[str, str] = {
    "qa_001": (
        "1 Disconnect all wired accessories except the TC148 wall switch and test.\n"
        "2 If the issue disappears, check for other accessories on push-button terminals; use shielded wire.\n"
        "3 Check wiring distance and cable gauge (2C*22 AWG, max ~15 m); try without extension cable.\n"
        "4 Try grounding COM to earth; if still failing, test or replace the TC148 switch."
    ),
    "qa_002": (
        "1 Disconnect the extension cable connecting TC148 to the control board and "
        "replace it with a short cable to test whether the gate opener works. "
        "If yes, please confirm the distance between TC148 and the control board.\n"
        "2 Disconnect all wired accessories from the control board except the power "
        "supply and arm. Momentarily short (instant touch only — plug in then pull out) "
        "the push button terminals (4# and 5#, or O/S/C and COM) to see if the opener responds.\n"
        "3 Confirm the wall switch is a genuine TOPENS TC148 (third-party switches may be incompatible).\n"
        "4 Check wire distance and gauge: use well-shielded 2C×22 AWG (2×0.3 mm²) minimum; "
        "keep cable length under 15 m when possible."
    ),
}

GROUP_ANSWER_EN_PATCH: dict[str, str] = {**A3S_ANSWER_EN_PATCH, **TC148_ANSWER_EN_PATCH}


def patch_group_en_from_parent(chunk_by_id: dict, group_id: str) -> str | None:
    for c in chunk_by_id.values():
        if c.get("group_id") == group_id and not c.get("parent_id"):
            en = (c.get("content_en") or "").strip()
            if en:
                return en
    for c in chunk_by_id.values():
        if c.get("group_id") == group_id:
            en = (c.get("content_en") or "").strip()
            if en:
                return en
    return GROUP_ANSWER_EN_PATCH.get(group_id)


def build_pilot_manifest(src_dir: Path, pilot_groups: frozenset[str], lib_id: str) -> list[dict]:
    manifest = json.loads((src_dir / "manifest.json").read_text(encoding="utf-8"))
    chunks = deepcopy(manifest["chunks"])
    chunk_by_id = {c["chunk_id"]: c for c in chunks}

    for c in chunks:
        gid = c.get("group_id") or ""
        if gid not in pilot_groups:
            continue
        if not c.get("is_retrievable", True):
            continue
        question = c.get("question") or ""
        content_en = (c.get("content_en") or "").strip()
        if not content_en:
            content_en = patch_group_en_from_parent(chunk_by_id, gid) or ""
            if content_en and not c.get("content_en"):
                c["content_en"] = content_en
        kw = extract_en_symptom_keywords(question)
        en_embed = build_embedding_text_en(question, content_en, symptom_keywords=kw)
        if not en_embed.strip():
            print(f"WARN {lib_id} {gid} {c['chunk_id']}: empty EN embed", file=sys.stderr)
            continue
        c["embedding_text_en"] = en_embed
        c["embedding_text"] = en_embed

    return chunks


def write_chunks_json(chunks: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Phase 1a pilot EN index")
    parser.add_argument(
        "--libs",
        nargs="*",
        choices=sorted(PILOT_GROUPS.keys()),
        help="Rebuild only these libraries (default: all)",
    )
    args = parser.parse_args()
    lib_filter = set(args.libs) if args.libs else None

    summary: list[dict] = []
    for lib_id, pilot in PILOT_GROUPS.items():
        if lib_filter and lib_id not in lib_filter:
            continue
        src = LIBRARY_CHROMA[lib_id]
        if not (src / "manifest.json").is_file():
            print(f"SKIP missing {src}", file=sys.stderr)
            continue
        dst = LIBRARY_OUT[lib_id]
        chunks = build_pilot_manifest(src, pilot, lib_id)
        filtered = [c for c in chunks if c.get("group_id") in pilot]
        retrievable = [
            c for c in filtered if c.get("is_retrievable", True) and c.get("embedding_text")
        ]
        tmp = dst.parent / "pilot_chunks.json"
        write_chunks_json(filtered, tmp)

        if dst.exists():
            shutil.rmtree(dst)
        cmd = [
            sys.executable,
            str(ROOT / "embed_ingest_local.py"),
            str(tmp),
            str(dst),
            "--model",
            str(MODEL),
        ]
        print(f"=== {lib_id} pilot EN index ({len(retrievable)} retrievable in pilot groups) ===")
        subprocess.run(cmd, check=True, cwd=str(ROOT))
        summary.append(
            {
                "library": lib_id,
                "pilot_groups": sorted(pilot),
                "retrievable_pilot_chunks": len(retrievable),
                "chroma_dir": str(dst.relative_to(ROOT)).replace("\\", "/"),
            }
        )

    out = ROOT / "_scratch/eval/phase_1a_pilot_en_index.json"
    if lib_filter and out.is_file():
        existing = json.loads(out.read_text(encoding="utf-8"))
        by_lib = {row["library"]: row for row in existing}
        for row in summary:
            by_lib[row["library"]] = row
        summary = [by_lib[k] for k in sorted(by_lib)]
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
