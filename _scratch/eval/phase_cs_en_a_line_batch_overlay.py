#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A-line batch overlay: Step 0 remaining 8 groups + qa_001 verbatim probe variants."""

from __future__ import annotations

import json
import re
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
STAMP = "20260708-cs-en-a-line-batch"

A3S_PROD = ROOT / "_scratch/run-006"
A3S_CHROMA = ROOT / "_scratch/run-007/chroma_captioned"
AD5S_PROD = ROOT / "_scratch/run-ad5s"
AD5S_CHROMA = AD5S_PROD / "chroma_captioned"

MAP_PATH = ROOT / "_scratch/eval/cs_email_query_map.json"

# --- shared verbatim sources ---
CS_0002_VERBATIM = (
    "I tested for power at the control board going to the motor and I get zero power. "
    "Fuse is good. Both AC and control board have power. Lock for gate unlocks when commanded "
    "but no power to motor it would seem."
)

CS_0012_VERBATIM = (
    "My contractor installed the opener and although the gate opens, it does not stop at the "
    "desired location, it moves too far and into the grass. Adjusting the screw (B) and sliding "
    "it to adjust does nothing - the gate still swings to the same spot too far over. It also "
    "does not close all the way, we notice it is VERY slow and then comes to a stop halfway. "
    "What is the solution? The contractor thinks that perhaps the screw (B) is faulty?"
)

CS_0016_VERBATIM = (
    "I installed, everything worked, now a red lightis flashlight and it won't work."
)

CS_0017_VERBATIM = (
    "Our gate arm has messed up again. We have done all the previous troubleshooting and it does "
    "the exact thing as the last one sent. The gate opener doesn't work at all. "
    "Can you let me know if we still have warranty. We purchased it in June of 2025."
)

CS_0018_VERBATIM = "I have batteries and AC adapter installed. I'm not getting anything to work."

CS_0019_VERBATIM = (
    "Gate is opening at first open hard turned down force to almost nothing . Open to far gets "
    "binded. Sometimes doesn't close seems to have a mind of its own . Tryed programing through "
    "control box and remote not picking up remote many time as well."
)

CS_0021_VERBATIM = (
    "The motherboard has power receives signal from fob , lights blink , a click noise , "
    "but the arms won't open or close. Checked with voltage meter board has power but will not "
    "send power to the arm terminals."
)

CS_0026_VERBATIM = (
    "We have troubleshoot the system, have replace the board with a new board. "
    "We have directly put + & - to the actuator and it does open and close but doesn't work "
    "when put back into to proper terminals. The fuse is good, there is a clicking sound when "
    "the remote is pressed but the actuator doesn't response."
)

# T4 probe · short variant to beat qa_033 battery overlap
CS_0026_VARIANT_SHORT = (
    "Board replaced. Actuator runs when directly connected to battery but does not respond "
    "when wired back to the control board."
)

CS_0026_VARIANT_CLICK = (
    "Fuse is good, clicking sound when remote pressed, actuator doesn't respond when wired "
    "to proper terminals but direct battery power works."
)

CS_0015_VERBATIM = (
    "We have one (hopefully) last issue. The gate opens and closes at the right spots and there "
    "is no sign of binding. That said, about half the time when the gate starts to close after "
    "the delay, it reverses. It waits through an entire additional delay cycle and tries again "
    "to close. With rare exception, it closes on the second try. But about half the time it "
    "closes normally. We are wondering if this may be an interaction between our soft stop and "
    "open/close delay settings."
)

QA_040_JOYCE_ANSWER_EN = (
    "1 Please double check all the brackets and hardware of the arm(including the screw of the "
    "limit switch) are secured since the looseness of the brackets or limit switch may also "
    "cause this issue.\n"
    "2 Power off the system, turn the FORCE potentiometer clockwise to increase the stall force "
    "to max. Then turn on the power and operate the gate opener to run for a complete opening & "
    "closing cycle. See whether the gate will open and close normally in the next opening and "
    "closing cycle.\n"
    "3 If the issue is still unresolved, please use the release key to disengage the clutches of "
    "both arms, and check whether the gate itself can be manually opened & closed freely 3.3 feet "
    "(one meter) away from the gate hinge. If not, please let me know the weight and length of "
    "your gate and double check the gate to make sure the gate can run freely by hand.\n"
    "4 If the above step is fine, please take down the arm from the gate and hold its front mount "
    "with a hand. Then press the remote to see if the arm can extend and retract properly each time."
)

QA_033_HEIDI_ANSWER_EN = (
    "Could you please confirm if the arm refers to the one we sent you in July, 2025? Please be "
    "noted that the warranty for replacement parts does not extend upon replacement; it remains "
    "effective from the original receipt date of the goods.\n"
    "1 Please ensure all the wire connection is correct and not loose.\n"
    "2 Please check the power LED light condition. If the POWER LED is OFF, please check if the "
    "fuse has blown, and replace the fuse if necessary. There is a backup fuse packed within the "
    "user manual pack.\n"
    "3 If the fuse is fine, please disconnect all wired accessories from the control board (just "
    "leave the power source and the arm). Disable the photocell function by turning the DIP "
    "switch #3 OFF. And try to press the remote to see whether the opener can work. If this step "
    "cannot help, please do step 4.\n"
    "4 Please refer to the user manual to erase all the codes from the control board and "
    "reprogram them. If reprogramming is not helpful, please further use a jumper wire to "
    "instantaneously short the push button terminals (4#, 5#) on the control board to see how "
    "it works.\n"
    "5 Use a multimeter to measure the output voltage of the +BAT- terminal on the control board "
    "(#11, #12), and then press the M12 remote control to operate the gate opener. It should be "
    "above 22VDC. Observe if there is a voltage drop after pressing the remote control.\n"
    "If above steps do not help, check the motor: connect the black & red wire of the arm "
    "directly to the UPS01 LOAD terminal. The arm should move. Reverse the polarity, the arm "
    "should move in the opposite direction.\n"
    "Check the limit switch: remove BLUE&GREEN&YELLOW wires, short DLMT&COM&ULMT terminals, then "
    "try again. The limit switch is faulty if the arm could run normally in both directions."
)

QA_016_BELLA_ANSWER_EN = (
    "May we kindly ask whether you adjusted the stall force after powering off the system first? "
    "After adjusting it, did you power the system back on and allow the opener to complete one "
    "full operating cycle?\n"
    "For Pull-to-Open Installation Mode, the open position is determined by the gate bracket. "
    "Please check if the moving rod is properly retracted when your gate is at the desired open "
    "position. Adjust the gate bracket inward a little if necessary.\n"
    "For Push-to-Open Installation Mode, the open position is adjusted by Limit Switch B. Adjust "
    "Limit Switch B inward on the arm, then press the remote to open the gate and see if the open "
    "position changes.\n"
    "Regarding the remote issue, please kindly clear all remote codes first, then try "
    "reprogramming the remotes again. Are all the remotes the original M12 remotes included with "
    "our system?"
)

VARIANTS_BLOCK_RE = re.compile(
    r"\n\n\[Customer reported variants\]\n.*", re.DOTALL
)


def run(cmd: list[str | Path]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def load_scenarios() -> dict[str, dict]:
    data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["scenarios"]}


def merge_email_examples(
    existing: list[dict] | None, additions: list[dict]
) -> list[dict]:
    by_key: dict[str, dict] = {}
    for ex in existing or []:
        key = ex.get("scenario_id") or ex.get("source") or json.dumps(ex, sort_keys=True)
        by_key[key] = ex
    for ex in additions:
        key = ex.get("scenario_id") or ex.get("source") or json.dumps(ex, sort_keys=True)
        by_key[key] = ex
    return list(by_key.values())


def ensure_chroma_dir(chroma_dir: Path) -> None:
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
            if "email_examples" in fields:
                fields["email_examples"] = merge_email_examples(
                    g.get("email_examples"), fields["email_examples"]
                )
            g.update(fields)
            return True
    return False


def ex(
    scenario_id: str,
    verbatim: str,
    *,
    mail_num: int | None = None,
    test_id: str | None = None,
    source: str = "",
    tags: list[str] | None = None,
) -> dict:
    row: dict = {
        "scenario_id": scenario_id,
        "verbatim": verbatim,
        "source": source or "samples/customer-service-emails/",
    }
    if mail_num is not None:
        row["mail_num"] = mail_num
    if test_id:
        row["test_id"] = test_id
    if tags:
        row["symptom_tags"] = tags
    return row


# Batch overlay spec: library -> group_id -> patch fields
A3S_BATCH: dict[str, dict] = {
    "qa_001": {
        "email_examples": [
            ex("cs_0002", CS_0002_VERBATIM, mail_num=2,
               source="samples/customer-service-emails/0002-a8132-et24-motor-no-power.md",
               tags=["zero_power_motor", "fuse_good", "lock_unlocks"]),
            ex("cs_0018", CS_0018_VERBATIM, mail_num=18,
               source="samples/customer-service-emails/0018-a5-a8-nothing-works-battery-ac.md",
               tags=["batteries_ac", "nothing_works"]),
            ex("cs_0021", CS_0021_VERBATIM, mail_num=21,
               source="samples/customer-service-emails/0021-a8132-board-power-arms-wont-move.md",
               tags=["board_power", "click", "arms_wont_move"]),
            ex("cs_0026", CS_0026_VERBATIM, test_id="T4", mail_num=None,
               source="samples/customer-service-emails/0026-a3a5a8-board-replaced-actuator-no-response.md",
               tags=["board_replaced", "actuator_ok"]),
            ex("cs_0026v1", CS_0026_VARIANT_SHORT, tags=["probe_variant", "actuator_ok"]),
            ex("cs_0026v2", CS_0026_VARIANT_CLICK, tags=["probe_variant", "click_no_response"]),
        ],
        "embed_prefix": (
            "zero power to motor fuse good lock unlocks · batteries and AC adapter nothing works · "
            "board has power won't send power to arm terminals lights blink click · "
            "actuator direct battery works wired back to board no response · board replaced"
        ),
    },
    "qa_019": {
        "email_examples": [
            ex("cs_0012", CS_0012_VERBATIM, mail_num=12,
               source="samples/customer-service-emails/0012-at12131-limit-overswing-stops-halfway.md",
               tags=["opens_too_far", "limit_b_open"]),
        ],
        "embed_prefix": (
            "opens too far into grass adjusting screw B does nothing overswings · "
            "gate does not stop at desired location AT12131"
        ),
    },
    "qa_020": {
        "email_examples": [
            ex("cs_0012", CS_0012_VERBATIM, mail_num=12,
               source="samples/customer-service-emails/0012-at12131-limit-overswing-stops-halfway.md",
               tags=["closes_halfway", "limit_b_close"]),
        ],
        "embed_prefix": (
            "does not close all the way very slow stops halfway screw B faulty · "
            "AT12131 close limit"
        ),
    },
    "qa_021": {
        "email_examples": [
            ex("cs_0012", CS_0012_VERBATIM, mail_num=12,
               source="samples/customer-service-emails/0012-at12131-limit-overswing-stops-halfway.md",
               tags=["close_limit", "push_open"]),
        ],
        "embed_prefix": (
            "does not close all the way very slow stops halfway · push open close limit"
        ),
    },
    "qa_033": {
        "answer_en": QA_033_HEIDI_ANSWER_EN,
        "email_examples": [
            ex("cs_0017", CS_0017_VERBATIM, mail_num=17,
               source="samples/customer-service-emails/0017-a5131-arm-failed-again-warranty.md",
               tags=["warranty", "arm_replacement", "won't_work"]),
        ],
        "embed_prefix": (
            "gate arm messed up again warranty arm replacement won't work at all A5131"
        ),
    },
}

AD5S_BATCH: dict[str, dict] = {
    "qa_001": {
        "email_examples": [
            ex("cs_0016", CS_0016_VERBATIM, mail_num=16,
               source="samples/customer-service-emails/0016-pw802-red-light-flashing-wont-work.md",
               tags=["red_light_flashing", "pw802"]),
        ],
        "embed_prefix": "red light flashing won't work after installation PW802 dual swing",
    },
    "qa_040": {
        "answer_en": QA_040_JOYCE_ANSWER_EN,
        "email_examples": [
            ex(
                "cs_0015",
                CS_0015_VERBATIM,
                mail_num=15,
                source="samples/customer-service-emails/0015-ad8s-auto-close-reverses-second-try.md",
                tags=["auto_close", "delay_reversal", "second_try", "soft_stop"],
            ),
        ],
        "embed_prefix": (
            "auto close delay gate reverses when starting to close · additional delay cycle "
            "closes on second try · soft stop open close delay interaction AD8S"
        ),
    },
    "qa_016": {
        "answer_en": QA_016_BELLA_ANSWER_EN,
        "email_examples": [
            ex("cs_0019", CS_0019_VERBATIM, mail_num=19,
               source="samples/customer-service-emails/0019-ad5s-opens-too-far-remote-not-recognized.md",
               tags=["opens_too_far", "remote_learn", "pull_open"]),
        ],
        "embed_prefix": (
            "opens too far gets binded pull to open remote not picking up · "
            "sometimes doesn't close AD5S dual solar"
        ),
    },
}


def apply_batch_to_qa_groups(prod: Path, batch: dict[str, dict], lib: str) -> list[str]:
    path = prod / "qa_groups.json"
    groups = load_groups(path)
    touched: list[str] = []
    for gid, fields in batch.items():
        payload = {k: v for k, v in fields.items() if k != "embed_prefix"}
        if not patch_group(groups, gid, **payload):
            raise SystemExit(f"{gid} not found in {lib} qa_groups")
        touched.append(gid)
    save_groups(path, groups)
    print(f"patched {lib} qa_groups: {', '.join(touched)}")
    return touched


def primary_retrievable_chunk(chunks: list[dict], group_id: str) -> dict | None:
    hits = [c for c in chunks if c.get("group_id") == group_id and c.get("is_retrievable")]
    if not hits:
        return None
    for c in hits:
        if str(c.get("chunk_id", "")).endswith("_c001"):
            return c
    return hits[0]


def strip_variants_block(text: str) -> str:
    return VARIANTS_BLOCK_RE.sub("", text or "").rstrip()


def prepend_keywords(base: str, prefix: str) -> str:
    prefix = (prefix or "").strip()
    if not prefix:
        return base
    if prefix in base:
        return base
    return f"{prefix}\n{base}" if base else prefix


def patch_manifest_batch(
    chunks: list[dict],
    batch: dict[str, dict],
) -> int:
    n = 0
    for gid, spec in batch.items():
        target = primary_retrievable_chunk(chunks, gid)
        if not target:
            print(f"  WARN no retrievable chunk for {gid}", flush=True)
            continue
        if "answer_en" in spec:
            for c in chunks:
                if c.get("group_id") == gid and (
                    c.get("parent_id") is None or str(c.get("chunk_id", "")).endswith("_parent")
                ):
                    c["content_en"] = spec["answer_en"]
            if not target.get("content_en"):
                target["content_en"] = spec["answer_en"]
        examples = spec.get("email_examples")
        if examples is not None:
            target["email_examples"] = merge_email_examples(
                target.get("email_examples"), examples
            )
        base = strip_variants_block(target.get("embedding_text") or "")
        base = prepend_keywords(base, spec.get("embed_prefix", ""))
        merged_examples = target.get("email_examples") or []
        target["embedding_text"] = append_email_verbatim_to_embedding(base, merged_examples)
        n += 1
    return n


def reembed_chroma(chroma_dir: Path, chunks: list[dict], tmp_name: str) -> None:
    tmp = chroma_dir.parent / tmp_name
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
    if not (chroma_dir / "manifest.json").is_file():
        raise SystemExit(f"re-embed failed: missing manifest in {chroma_dir}")


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


def scenario_verbatim(scenarios: dict[str, dict], sid: str) -> str:
    sc = scenarios[sid]
    vb = sc.get("verbatim_customer") or []
    if vb:
        return vb[0] if len(vb) == 1 else "\n\n".join(vb[:2])
    return sc.get("primary_query") or ""


def spot_check(scenarios: dict[str, dict]) -> dict:
    from library_router import load_unified_libraries, unified_search

    model_rel = str(MODEL.relative_to(ROOT)).replace("\\", "/")
    libs = load_unified_libraries(model_rel, k=3)
    probes = [
        ("cs_0002", "a3s", {"qa_001", "qa_033"}),
        ("cs_0012", "a3s", {"qa_019", "qa_020", "qa_021"}),
        ("cs_0015", "ad5s", {"qa_040", "qa_015", "qa_016"}),
        ("cs_0016", "ad5s", {"qa_001"}),
        ("cs_0017", "a3s", {"qa_033"}),
        ("cs_0018", "a3s", {"qa_001", "qa_002"}),
        ("cs_0019", "ad5s", {"qa_016", "qa_020", "qa_005"}),
        ("cs_0021", "a3s", {"qa_001"}),
        ("cs_0026", "a3s", {"qa_001", "qa_033"}),
        ("cs_0026v", "a3s", {"qa_001", "qa_033"}),
    ]
    checks = []
    for label, exp_lib, acceptable in probes:
        if label == "cs_0026v":
            query = CS_0026_VARIANT_SHORT
        else:
            query = scenario_verbatim(scenarios, label)
        routing, hits = unified_search(query, libs)
        top1 = hits[0].group_id if hits else None
        row = {
            "label": label,
            "query_preview": query[:100],
            "matched_library": routing.matched_library,
            "library_ok": routing.matched_library == exp_lib,
            "top1_group": top1,
            "top1_ok": top1 in acceptable if acceptable else None,
            "acceptable_groups": sorted(acceptable),
            "top3_groups": [h.group_id for h in hits[:3]],
            "top1_score": round(hits[0].score, 4) if hits else None,
        }
        checks.append(row)
        ok = top1 in acceptable if top1 else False
        print(f"  {label}: lib={routing.matched_library} top1={top1} [{'OK' if ok else 'MISS'}]")
    return {"stamp": STAMP, "checks": checks}


def main() -> int:
    backup_paths()
    scenarios = load_scenarios()

    apply_batch_to_qa_groups(A3S_PROD, A3S_BATCH, "a3s")
    apply_batch_to_qa_groups(AD5S_PROD, AD5S_BATCH, "ad5s")

    a3s_tmp = A3S_CHROMA.parent / "a_line_batch_chunks_a3s.json"
    ad5s_tmp = AD5S_CHROMA.parent / "a_line_batch_chunks_ad5s.json"

    if a3s_tmp.is_file():
        chunks_a3s = json.loads(a3s_tmp.read_text(encoding="utf-8"))
    else:
        ensure_chroma_dir(A3S_CHROMA)
        chunks_a3s = deepcopy(
            json.loads((A3S_CHROMA / "manifest.json").read_text(encoding="utf-8"))["chunks"]
        )
        patch_manifest_batch(chunks_a3s, A3S_BATCH)
    print("re-embed a3s chroma (batch overlay)", flush=True)
    reembed_chroma(A3S_CHROMA, chunks_a3s, "a_line_batch_chunks_a3s.json")

    if ad5s_tmp.is_file():
        chunks_ad5s = json.loads(ad5s_tmp.read_text(encoding="utf-8"))
    else:
        ensure_chroma_dir(AD5S_CHROMA)
        chunks_ad5s = deepcopy(
            json.loads((AD5S_CHROMA / "manifest.json").read_text(encoding="utf-8"))["chunks"]
        )
        patch_manifest_batch(chunks_ad5s, AD5S_BATCH)
    print("re-embed ad5s chroma (batch overlay)", flush=True)
    reembed_chroma(AD5S_CHROMA, chunks_ad5s, "a_line_batch_chunks_ad5s.json")

    rebuild_en_indexes()

    print("\n=== batch spot check ===")
    result = spot_check(scenarios)
    out_path = ROOT / "_scratch/eval/a_line_batch_overlay_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
