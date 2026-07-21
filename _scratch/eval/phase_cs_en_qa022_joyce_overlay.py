#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extend qa_022 answer_en to Joyce #13 four-step ladder (11#/12#, FORCE/SOFT STOP, push load, arm off gate)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

QA_GROUPS = ROOT / "_scratch/run-006/qa_groups.json"
CHUNKS_CAP = ROOT / "_scratch/run-006/chunks_captioned.json"
ZH_MANIFEST = ROOT / "_scratch/run-007/chroma_captioned/manifest.json"

QA_022_ANSWER_EN = (
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
)


def patch_qa_groups() -> None:
    groups = json.loads(QA_GROUPS.read_text(encoding="utf-8"))
    for g in groups:
        if g.get("group_id") == "qa_022":
            g["answer_en"] = QA_022_ANSWER_EN
            print("patched qa_groups qa_022 answer_en")
            break
    QA_GROUPS.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def _sync_content_en(chunks: list[dict]) -> int:
    n = 0
    for c in chunks:
        if c.get("group_id") != "qa_022":
            continue
        if c.get("parent_id") is None or c.get("chunk_id", "").endswith("_parent"):
            c["content_en"] = QA_022_ANSWER_EN
            n += 1
    return n


def patch_chunks_captioned() -> None:
    chunks = json.loads(CHUNKS_CAP.read_text(encoding="utf-8"))
    n = _sync_content_en(chunks)
    CHUNKS_CAP.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"patched chunks_captioned qa_022 parent blocks: {n}")


def patch_zh_manifest() -> None:
    manifest = json.loads(ZH_MANIFEST.read_text(encoding="utf-8"))
    n = _sync_content_en(manifest["chunks"])
    ZH_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"patched ZH chroma manifest qa_022 parent blocks: {n}")


def rebuild_a3s_en_index() -> None:
    cmd = [
        sys.executable,
        str(ROOT / "_scratch/eval/phase_1a_pilot_en_index.py"),
        "--libs",
        "a3s",
    ]
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    patch_qa_groups()
    patch_chunks_captioned()
    patch_zh_manifest()
    rebuild_a3s_en_index()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
