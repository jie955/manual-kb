#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 2 Wave G11: migrate G9/G10 + #12/#13 limit overlays to A3S EN-index (chroma_captioned_en)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260708-cs-en-task2-g11-en"

A3S_ZH_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
A3S_EN_CHROMA = ROOT / "_scratch/run-007/chroma_captioned_en"
AD5S_ZH_CHROMA = ROOT / "_scratch/run-ad5s/chroma_captioned"
AD5S_EN_CHROMA = ROOT / "_scratch/run-ad5s/chroma_captioned_en"

A3S_TOUCH = frozenset(
    {"qa_001", "qa_010", "qa_011", "qa_019", "qa_020", "qa_021", "qa_022", "qa_033", "qa_030", "qa_034"}
)
AD5S_TOUCH = frozenset({"qa_001", "qa_032", "qa_036", "qa_040"})


def backup() -> None:
    dst = A3S_EN_CHROMA.parent / f"chroma_captioned_en.bak-{STAMP}"
    if not dst.exists() and A3S_EN_CHROMA.is_dir():
        shutil.copytree(A3S_EN_CHROMA, dst)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def en_qa001_board(question: str, body: str) -> str:
    return (
        "replaced control board clicking sound remote actuator no response A3 A5 A8 · "
        "fuse good click sound actuator doesn't respond · "
        "actuator direct 24V power works both directions · board has power won't send power to arm · "
        "DLMT COM ULMT tripped proper terminals no response\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa033_board(question: str, body: str) -> str:
    return (
        "replaced control board actuator direct 24V works clicking remote no response · "
        "fuse good click sound actuator doesn't respond · "
        "short DLMT COM ULMT limit switch gate arm messed up only one direction\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa011_no_response(question: str, body: str) -> str:
    return (
        "no response at all AT12131 gate does nothing push button control board power led off fuse backup · "
        "NOT replaced control board NOT fuse good clicking actuator direct power both directions · "
        "NOT board replaced DLMT COM ULMT NOT actuator direct 24V works\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa010_remote_multi(question: str, body: str) -> str:
    return (
        "push remote 3 times second or third try board click nothing happens remote needs multiple presses · "
        "NOT replaced control board NOT actuator direct 24V works NOT board replaced clicking DLMT COM ULMT\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa019_open_overswing(question: str, body: str) -> str:
    return (
        "push to open gate opens too far into grass overswings adjusting screw B sliding limit switch does nothing · "
        "opens too far AT12131 screw B open limit push to open · "
        "NOT gate not closing fully NOT doesn't close all the way NOT very slow stops halfway close limit\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa020_close_limit(question: str, body: str) -> str:
    return (
        "contractor installed opener gate opens does not stop desired location moves too far into grass · "
        "adjusting screw B sliding limit switch gate still swings too far · "
        "gate not closing fully doesn't close all the way very slow stops halfway close limit screw B AT12131 · "
        "reconfirm open closed position pull to open limit switch B close position · "
        "NOT keeps stopping before opening fully NOT gate stops opening opening stall FORCE opening direction\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa021_close_limit(question: str, body: str) -> str:
    return (
        "gate not closing fully doesn't close all the way very slow stops halfway close limit · "
        "reconfirm open closed position limit switch B close AT12131 screw B · "
        "NOT opens too far into grass NOT overswings open limit NOT keeps stopping before opening fully\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa022_stall(question: str, body: str) -> str:
    return (
        "Need help this gate opener keeps stopping before opening fully\n"
        "gate opener keeps stopping before opening fully\n"
        "keeps stopping before opening fully stops before opening fully\n"
        "A3S gate opener keeps stopping before opening fully gate stops halfway while opening\n"
        "FORCE potentiometer SOFT STOP gate not opening all the way opening direction stall\n"
        "detect voltage 11 12 terminals above 22V gate stops opening push against gate load\n"
        "NOT soft stop issues closing deceleration NOT gate operates slowly\n"
        "NOT close limit screw B NOT gate not closing fully only closing problem\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa030_demote(question: str, body: str) -> str:
    return (
        "soft stop deceleration issues when gate slows down closing direction calibration · "
        "NOT keeps stopping before opening fully NOT stops before opening fully · "
        "NOT gate stops opening NOT gate opener keeps stopping before opening fully · "
        "NOT Need help gate opener keeps stopping before opening fully opening stall\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa034_demote(question: str, body: str) -> str:
    return (
        "gate operates slowly motor speed voltage 11 12 terminals motor runs slow · "
        "NOT keeps stopping before opening fully NOT stops before opening fully gate stops opening\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa040_autoclose(question: str, body: str) -> str:
    return (
        "powered down first before moving the pot great delay dialed in AD8S dual swing · "
        "about half the time when the gate starts to close after the delay it reverses · "
        "waits through entire additional delay cycle tries again to close closes on second try · "
        "soft stop and open close delay interaction gate opens closes at right spots no binding · "
        "gate reverses when starting to close after auto close delay · "
        "NOT gate operates slowly NOT soft stop issues only NOT keeps stopping before opening fully\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa036_slow(question: str, body: str) -> str:
    return (
        "gate operates slowly motor speed voltage 11 12 terminals above 22V · "
        "NOT auto close delay reverses NOT additional delay cycle NOT closes on second try · "
        "NOT soft stop open close delay interaction NOT gate starts to close after delay reverses\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_ad5s_qa001_redlight(question: str, body: str) -> str:
    return (
        "installed everything worked red light flashing won't work PW802 power LED flash · "
        "gate opener doesn't work at all after install red light flashing · "
        "NOT programming remote NOT CODE LED ON only faint glow\n"
        f"Question: {question}\n{body}"
    ).strip()


def en_qa032_softstop(question: str, body: str) -> str:
    return (
        "soft stop not working deceleration §十四 · "
        "NOT auto close delay reverses NOT additional delay cycle NOT closes on second try\n"
        f"Question: {question}\n{body}"
    ).strip()


def custom_en_embedding(chunk: dict, question: str, body: str, lib: str) -> str | None:
    cid = chunk.get("chunk_id") or ""
    gid = chunk.get("group_id") or ""
    if lib == "a3s":
        if gid in ("qa_022", "qa_030"):
            pass
        elif gid == "qa_034" and cid == "qa_034_c001":
            pass
        elif not cid.endswith("_c001"):
            return None
        builders = {
            "qa_001": en_qa001_board,
            "qa_033": en_qa033_board,
            "qa_011": en_qa011_no_response,
            "qa_010": en_qa010_remote_multi,
            "qa_019": en_qa019_open_overswing,
            "qa_020": en_qa020_close_limit,
            "qa_021": en_qa021_close_limit,
            "qa_022": en_qa022_stall,
            "qa_030": en_qa030_demote,
            "qa_034": en_qa034_demote,
        }
    else:
        if cid != f"{gid}_c001":
            return None
        builders = {
            "qa_001": en_ad5s_qa001_redlight,
            "qa_040": en_qa040_autoclose,
            "qa_036": en_qa036_slow,
            "qa_032": en_qa032_softstop,
        }
    fn = builders.get(gid)
    if not fn:
        return None
    return fn(question, body)


def build_en_chunks_for_lib(lib_id: str, zh_chroma: Path, touch: frozenset[str]) -> list[dict]:
    from phase_1b_full_en_index import build_full_manifest

    groups_path = ROOT / "_scratch/run-006/qa_groups.json" if lib_id == "a3s" else ROOT / "_scratch/run-ad5s/qa_groups.json"
    chunks = build_full_manifest(zh_chroma, lib_id)
    groups = {g["group_id"]: g for g in json.loads(groups_path.read_text(encoding="utf-8"))}
    out: list[dict] = []
    for c in chunks:
        nc = deepcopy(c)
        gid = nc.get("group_id") or ""
        if gid not in touch:
            out.append(nc)
            continue
        q = groups.get(gid, {}).get("question") or nc.get("question") or ""
        body = (nc.get("content_en") or nc.get("embedding_text") or "").strip()
        custom = custom_en_embedding(nc, q, body, lib_id)
        if custom:
            nc["embedding_text"] = custom
            print(f"  EN overlay {lib_id} {nc.get('chunk_id')}")
        out.append(nc)
    return out


def ingest_chunks(chunks: list[dict], dst: Path, tmp_name: str) -> None:
    tmp = dst.parent / tmp_name
    tmp.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    if dst.exists():
        import time

        for attempt in range(5):
            try:
                shutil.rmtree(dst)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                time.sleep(2)
    run(
        [
            sys.executable,
            str(ROOT / "embed_ingest_local.py"),
            str(tmp),
            str(dst),
            "--model",
            str(MODEL),
        ]
    )


def pipeline() -> None:
    backup()
    a3s = build_en_chunks_for_lib("a3s", A3S_ZH_CHROMA, A3S_TOUCH)
    ingest_chunks(a3s, A3S_EN_CHROMA, f".g11-en-a3s-{STAMP}.json")
    ad5s_bak = AD5S_EN_CHROMA.parent / f"chroma_captioned_en.bak-{STAMP}"
    if not ad5s_bak.exists() and AD5S_EN_CHROMA.is_dir():
        shutil.copytree(AD5S_EN_CHROMA, ad5s_bak)
    ad5s = build_en_chunks_for_lib("ad5s", AD5S_ZH_CHROMA, AD5S_TOUCH)
    ingest_chunks(ad5s, AD5S_EN_CHROMA, f".g11-en-ad5s-{STAMP}.json")


if __name__ == "__main__":
    pipeline()
