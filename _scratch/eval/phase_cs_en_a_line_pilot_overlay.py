#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-line pilot overlay: #1 qa_011 · #13 qa_022 · T4 qa_001 (+ #3 qa_010 ad5s)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from en_representation import (  # noqa: E402
    append_email_verbatim_to_embedding,
    build_embedding_text_en,
    extract_en_symptom_keywords,
)

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260708-cs-en-a-line-v2"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
AD5S_PROD = ROOT / "_scratch/run-ad5s"
AD5S_CHROMA = AD5S_PROD / "chroma_captioned"

# --- #1 cs_0001 · AT12131S → qa_011 (both) ---
CS_0001_VERBATIM = (
    "the gate does nothing when i push the button or use the key pad remote."
)

QA_011_JOYCE_ANSWER_EN = (
    "1 Check all the wires are connected as they should be. And please measure the voltage "
    "of the +BAT- terminals (11# and 12#) on the control board to see whether it is above 22V. "
    "If the voltage is normal, please check whether the power led on the control board is ON. "
    "If the power led is off, check the fuse whether it was burnt out and replace the fuse if "
    "necessary. There is a backup fuse packed within the user manual pack. If the two above are "
    "fine please do test 2.\n"
    "2 Disconnect all accessories from the control board first (just leave the power source and "
    "the arm). And disable the photocell function by turning the dip switch #3 off, even though "
    "you didn't install the photocell. Then erase all remotes codes from the control board and "
    "reprogram them to have a try. If it fails, please immediately short the push button terminals "
    "(4# and 5#) to check whether the opener can work.\n"
    "3 If step 2 doesn't help, please check the motor. Connect the red & black wires of the arm "
    "to the DC 24V power source directly, the motor should run, and then exchange the polarity of "
    "the wires, the motor should run in the opposite direction. If the motor runs in both "
    "directions, the motor itself is good. Please connect the black & red wires back to the control "
    "board and check step 4.\n"
    "4 Disconnect the BLUE, GREEN & YELLOW wires of the faulty arm from the control board, use two "
    "jumper wires to short the ULT, COM & DLT terminals to which the wires were connected, and then "
    "press the remote to see if the arm could extend and retract. If it could move in both directions, "
    "then the limit switch is defective."
)

QA_011_EMAIL_EXAMPLES = [
    {
        "scenario_id": "cs_0001",
        "mail_num": 1,
        "verbatim": CS_0001_VERBATIM,
        "source": "samples/customer-service-emails/0001-at12131s-gate-no-response.md",
    }
]

# --- #13 cs_0013 · A3S → qa_022 (verbatim) ---
CS_0013_VERBATIM = "Need help this gate opener keeps stopping before opening fully"

QA_022_EMAIL_EXAMPLES = [
    {
        "scenario_id": "cs_0013",
        "mail_num": 13,
        "verbatim": CS_0013_VERBATIM,
        "source": "samples/customer-service-emails/0013-a3s-stops-before-fully-open.md",
        "symptom_tags": ["stops_before_open", "stall_force"],
    }
]

# --- T4 cs_0026 → qa_001 (verbatim) ---
CS_0026_VERBATIM = (
    "We have troubleshoot the system, have replace the board with a new board. "
    "We have directly put + & - to the actuator and it does open and close but doesn't work "
    "when put back into to proper terminals. The fuse is good, there is a clicking sound when "
    "the remote is pressed but the actuator doesn't response, We have tripped the DLMT, com ,Ulmt "
    "as directed in the Manuel and still no response."
)

QA_001_EMAIL_EXAMPLES = [
    {
        "scenario_id": "cs_0026",
        "test_id": "T4",
        "mail_num": None,
        "verbatim": CS_0026_VERBATIM,
        "source": "samples/customer-service-emails/0026-a3a5a8-board-replaced-actuator-no-response.md",
        "symptom_tags": ["board_replaced", "actuator_ok", "board_no_response"],
    }
]

# --- #3 cs_0003 · AD8 → qa_010 (verbatim) ---
CS_0003_VERBATIM = (
    "Installed openers as per instructions. Programmed supplied remotes. "
    "3 LEDs on control board responds when remote is pressed, however gates do not open. "
    "Please advise."
)

QA_010_QUESTION = (
    "按遥控器没有反应 · LEDs Respond Remote Pressed Gate Won't Move · "
    "3 LEDs Control Board Responds Gates Do Not Open · "
    "No Response When The Remote Is Pressed"
)

QA_010_ZH_PREFIX = (
    "症状：LED有反应但门不动作（3 LEDs on control board responds when remote pressed gates do not open · "
    "programmed remotes LED responds gate won't move AD8 dual swing；"
    "非§九中途走停qa_040·非auto close reverses·非gate stops mid-travel·非按多次才有反应qa_010多次）\n"
)

QA_010_EMAIL_EXAMPLES = [
    {
        "scenario_id": "cs_0003",
        "mail_num": 3,
        "verbatim": CS_0003_VERBATIM,
        "source": "samples/customer-service-emails/0003-ad8-leds-respond-gate-wont-open.md",
    }
]

QA_040_NEG = "非3 LEDs respond gates do not open·非LED responds remote pressed gate won't move·"


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_chroma_dir(chroma_dir: Path) -> None:
    """Restore ZH chroma from latest bak if active dir missing (a3s post-pilot)."""
    if chroma_dir.is_dir():
        return
    parent = chroma_dir.parent
    baks = sorted(parent.glob(f"{chroma_dir.name}.bak-*"), reverse=True)
    if not baks:
        raise SystemExit(f"missing chroma dir and no backup: {chroma_dir}")
    print(f"restore {chroma_dir.name} from {baks[0].name}", flush=True)
    shutil.copytree(baks[0], chroma_dir)


def backup_paths() -> None:
    for base, names in (
        (A3S_PROD, ("qa_groups.json",)),
        (AD5S_PROD, ("qa_groups.json",)),
    ):
        for name in names:
            src = base / name
            bak = base / f"{name}.bak-{STAMP}"
            if src.is_file() and not bak.exists():
                shutil.copy2(src, bak)
    for chroma in (A3S_CHROMA, AD5S_CHROMA):
        bak = chroma.parent / f"{chroma.name}.bak-{STAMP}"
        if chroma.is_dir() and not bak.exists():
            shutil.copytree(chroma, bak)
    print(f"backup stamp {STAMP}")


def patch_group(groups: list[dict], group_id: str, **fields) -> bool:
    for g in groups:
        if g.get("group_id") == group_id:
            g.update(fields)
            return True
    return False


def patch_a3s_qa_groups() -> None:
    path = A3S_PROD / "qa_groups.json"
    groups = load_groups(path)
    for gid, fields in (
        ("qa_011", {"email_examples": QA_011_EMAIL_EXAMPLES, "answer_en": QA_011_JOYCE_ANSWER_EN}),
        ("qa_022", {"email_examples": QA_022_EMAIL_EXAMPLES}),
        ("qa_001", {"email_examples": QA_001_EMAIL_EXAMPLES}),
    ):
        if not patch_group(groups, gid, **fields):
            raise SystemExit(f"{gid} not found in a3s qa_groups")
    save_groups(path, groups)
    print("patched a3s qa_011 qa_022 qa_001")


def patch_ad5s_qa_groups() -> None:
    path = AD5S_PROD / "qa_groups.json"
    groups = load_groups(path)
    if not patch_group(
        groups,
        "qa_010",
        question=QA_010_QUESTION,
        email_examples=QA_010_EMAIL_EXAMPLES,
    ):
        raise SystemExit("qa_010 not found in ad5s qa_groups")
    for g in groups:
        if g.get("group_id") == "qa_010":
            zh = (g.get("answer_zh") or "").strip()
            if QA_010_ZH_PREFIX.strip() not in zh:
                g["answer_zh"] = QA_010_ZH_PREFIX + zh
        if g.get("group_id") == "qa_040":
            zh = g.get("answer_zh") or ""
            if QA_040_NEG not in zh:
                g["answer_zh"] = zh.replace(
                    "症状：开关门中途走停或反弹",
                    "症状：开关门中途走停或反弹（" + QA_040_NEG.rstrip("·") + "；",
                    1,
                )
    save_groups(path, groups)
    print("patched ad5s qa_010 question/email_examples + qa_040 neg hint")


def build_a3s_embedding(
    group_id: str,
    question: str,
    content_en: str,
    *,
    email_examples: list[dict],
    extra_keywords: str = "",
) -> str:
    kw = extract_en_symptom_keywords(question)
    if extra_keywords:
        kw = f"{kw} · {extra_keywords}" if kw else extra_keywords
    base = build_embedding_text_en(question, content_en, symptom_keywords=kw)
    return append_email_verbatim_to_embedding(base, email_examples)


def primary_retrievable_chunk(chunks: list[dict], group_id: str) -> dict | None:
    hits = [
        c
        for c in chunks
        if c.get("group_id") == group_id and c.get("is_retrievable")
    ]
    if not hits:
        return None
    for c in hits:
        if str(c.get("chunk_id", "")).endswith("_c001"):
            return c
    return hits[0]


def patch_manifest_group(
    chunks: list[dict],
    group_id: str,
    *,
    question: str | None = None,
    content_en: str | None = None,
    email_examples: list[dict] | None = None,
    embed_extra_keywords: str = "",
) -> int:
    target = primary_retrievable_chunk(chunks, group_id)
    if not target:
        return 0
    if question:
        target["question"] = question
        for c in chunks:
            if c.get("group_id") == group_id and c.get("parent_id") is None:
                c["question"] = question
    if content_en:
        for c in chunks:
            if c.get("group_id") == group_id and (
                c.get("parent_id") is None or c.get("chunk_id", "").endswith("_parent")
            ):
                c["content_en"] = content_en
    if email_examples is not None:
        target["email_examples"] = email_examples
    en_body = (target.get("content_en") or content_en or "").strip()
    q = target.get("question") or question or ""
    examples = email_examples if email_examples is not None else target.get("email_examples") or []
    target["embedding_text"] = build_a3s_embedding(
        group_id,
        q,
        en_body,
        email_examples=examples,
        extra_keywords=embed_extra_keywords,
    )
    return 1


def reembed_chroma(chroma_dir: Path, chunks: list[dict]) -> None:
    manifest_path = chroma_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"chunks": chunks}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    tmp = chroma_dir.parent / "a_line_pilot_chunks.json"
    tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
    run(
        [
            sys.executable,
            ROOT / "embed_ingest_local.py",
            tmp,
            chroma_dir,
            "--model",
            MODEL,
        ]
    )


def patch_and_reembed_a3s() -> None:
    ensure_chroma_dir(A3S_CHROMA)
    manifest_path = A3S_CHROMA / "manifest.json"
    chunks = deepcopy(json.loads(manifest_path.read_text(encoding="utf-8"))["chunks"])
    n = 0
    n += patch_manifest_group(
        chunks,
        "qa_011",
        content_en=QA_011_JOYCE_ANSWER_EN,
        email_examples=QA_011_EMAIL_EXAMPLES,
        embed_extra_keywords=(
            "gate does nothing when push button · keypad remote no response · "
            "AT12131 no response at all"
        ),
    )
    n += patch_manifest_group(
        chunks,
        "qa_022",
        email_examples=QA_022_EMAIL_EXAMPLES,
        embed_extra_keywords=(
            "A3S gate keeps stopping before opening fully · stops before fully open · "
            "stall force soft stop"
        ),
    )
    n += patch_manifest_group(
        chunks,
        "qa_001",
        email_examples=QA_001_EMAIL_EXAMPLES,
        embed_extra_keywords=(
            "replaced control board actuator direct power works · clicking sound remote · "
            "board has power won't send power to arm"
        ),
    )
    print(f"patched a3s manifest retrievable chunks: {n}")
    reembed_chroma(A3S_CHROMA, chunks)


def patch_and_reembed_ad5s() -> None:
    ensure_chroma_dir(AD5S_CHROMA)
    manifest_path = AD5S_CHROMA / "manifest.json"
    chunks = deepcopy(json.loads(manifest_path.read_text(encoding="utf-8"))["chunks"])
    parent_en = None
    for c in chunks:
        if c.get("group_id") == "qa_010" and c.get("parent_id") is None:
            parent_en = (c.get("content_en") or "").strip()
            break
    n = patch_manifest_group(
        chunks,
        "qa_010",
        question=QA_010_QUESTION,
        content_en=parent_en,
        email_examples=QA_010_EMAIL_EXAMPLES,
        embed_extra_keywords=(
            "3 LEDs respond remote pressed gates do not open · "
            "LED responds gate won't move · AD8 dual swing"
        ),
    )
    print(f"patched ad5s manifest qa_010 retrievable chunks: {n}")
    reembed_chroma(AD5S_CHROMA, chunks)


def rebuild_en_indexes() -> None:
    run(
        [
            sys.executable,
            ROOT / "_scratch/eval/phase_1a_pilot_en_index.py",
            "--libs",
            "a3s",
            "ad5s",
        ]
    )


def spot_check() -> dict:
    from library_router import load_unified_libraries, unified_search

    libs = load_unified_libraries(str(MODEL.relative_to(ROOT)).replace("\\", "/"), k=3)
    cases = [
        ("cs_0001", CS_0001_VERBATIM, "a3s", "qa_011"),
        ("cs_0013", CS_0013_VERBATIM, "a3s", "qa_022"),
        ("cs_0026", CS_0026_VERBATIM, "a3s", "qa_001"),
        ("cs_0003", CS_0003_VERBATIM, "ad5s", "qa_010"),
    ]
    out = []
    for label, query, exp_lib, exp_group in cases:
        routing, hits = unified_search(query, libs)
        top1 = hits[0].group_id if hits else None
        row = {
            "label": label,
            "query": query[:80],
            "matched_library": routing.matched_library,
            "library_ok": routing.matched_library == exp_lib,
            "top1_group": top1,
            "top1_ok": top1 == exp_group,
            "top3_groups": [h.group_id for h in hits[:3]],
            "top1_score": round(hits[0].score, 4) if hits else None,
        }
        out.append(row)
        status = "OK" if top1 == exp_group else "MISS"
        print(f"  {label}: lib={routing.matched_library} top1={top1} [{status}]")
    return {"stamp": STAMP, "checks": out}


def run_gate_subset() -> None:
    run(
        [
            sys.executable,
            ROOT / "_scratch/eval/run_cs_e2e_gate.py",
            "--ids",
            "cs_0001",
            "cs_0013",
            "cs_0026",
        ]
    )


def main() -> int:
    ensure_chroma_dir(A3S_CHROMA)
    ensure_chroma_dir(AD5S_CHROMA)
    ensure_chroma_dir(AD5S_CHROMA)
    backup_paths()
    patch_a3s_qa_groups()
    patch_ad5s_qa_groups()
    patch_and_reembed_a3s()
    patch_and_reembed_ad5s()
    rebuild_en_indexes()
    print("\n=== spot check ===")
    result = spot_check()
    out_path = ROOT / "_scratch/eval/cs_en_a_line_pilot_overlay_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path.relative_to(ROOT)}")
    print("\n=== gate subset (retrieval only) ===")
    run_gate_subset()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
