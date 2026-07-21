#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-05 Wave3：qa_033 DIP · qa_040 门宽 spec → prod。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "_scratch/eval"))

from ad5s_zh_en_gap_scan import en_only_specs  # noqa: E402

PROD = ROOT / "_scratch/run-ad5s"
STAMP = "20260705-bl-v1-05-wave3"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset({"qa_033", "qa_040"})

CRITICAL = {
    "fuse_spec",
    "fuse_rating",
    "remote_battery",
    "battery_spec",
    "bat_terminal_ids",
    "dip_switch",
    "adapter_output",
    "solar_ocv",
    "solar_watt_addon",
    "range_feet",
    "backup_fuse_location",
}

ANSWER_ZH: dict[str, str] = {
    "qa_033": (
        "1 断开有线配件，按遥控器让门停半路，等一会看看门会不会自动关，如果可以，应该是配件影响导致门无法自动关门，"
        "可以一个一个接配件，测试看看是哪个导致\n"
        "2 如果断开配件后，自动关门还是没起作用，保持配件断开，然后把门机的电断开（断开控制板+BAT-电源），"
        "将 DIP 开关 #2 拨 ON 开启自动关门功能，调节 AUTO CLOSE 电位器设定自动关门时间；"
        "然后上电，按遥控器走一个完整的开关门循环，再按遥控器让门运行到半开位置停下，等一会\n"
        "若仍无效，检查 DIP 开关 #1 是否按推拉开门安装方式设置正确\n"
        "特殊案例：能自动开，不能自动关（每一次都是设定的时间，大概率是推拉开门逻辑反了）"
    ),
    "qa_040": (
        "症状：开关门中途/一半走停或反弹（§九；非开到位反弹·非关到位反弹·非§十二限位）\n"
        "1 排除红外遇阻影响（未使用红外时可将 DIP 开关 #3 拨 OFF 关闭红外功能）\n"
        "2 断电调遇阻力与缓停止（FORCE 电位器略顺时针增大遇阻力；SOFT STOP 电位器略逆时针减小缓停时间）\n"
        "3 还有问题的话，可以控制板上一次只接一个机臂，找出问题机臂，然后做下面的测试\n"
        "4 打开离合，用离合钥匙打开离合，在距门铰链约1米（3.3英尺）处手动开合门，检查是否推拉顺畅；"
        "不顺请告知门宽门重，并复核门能否用手顺畅运行\n"
        "5 机臂从门上拿下来试试按遥控器的时候机臂能否正常伸缩\n"
        "6 还不行发视频\n"
        "如果上面步骤还不行，可以考虑测电压，和转拉耳180°的排查\n"
        "如果机臂不带门也伸出一点就反弹，其他已排除，客人不能测电机电流：\n"
        "可以让客户把离合打开，按遥控器看看电机有没有问题，如果没问题，那么也很有可能机臂存在某个卡点。"
        "如果离合打开电机还有问题，可以做测电机，如果此时电机可以正常运行，那控制板可能有故障了。"
    ),
}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    for g in out:
        if g["group_id"] in TOUCH_IDS:
            g["answer_zh"] = ANSWER_ZH[g["group_id"]]
            print(f"  patched {g['group_id']}")
    return out


def verify_specs(groups: list[dict]) -> bool:
    ok = True
    by_id = {g["group_id"]: g for g in groups}
    for gid in sorted(TOUCH_IDS):
        g = by_id[gid]
        miss = en_only_specs(g.get("answer_en") or "", g.get("answer_zh") or "")
        crit = [(l, s) for l, s in miss if l in CRITICAL]
        if crit:
            print(f"FAIL {gid} still missing: {crit}")
            ok = False
        else:
            print(f"OK   {gid} critical specs covered in ZH")
    return ok


def backup() -> None:
    for name in ("qa_groups.json", "chunks_captioned.json"):
        bak = PROD / f"{name}.bak-{STAMP}"
        if not bak.exists():
            shutil.copy2(PROD / name, bak)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def merge_chunks_captioned() -> None:
    old_cap = json.loads((PROD / "chunks_captioned.json").read_text(encoding="utf-8"))
    new_chunks = json.loads((PROD / "chunks_out/chunks.json").read_text(encoding="utf-8"))
    old_by_gid = {c["group_id"]: c for c in old_cap if c.get("is_retrievable", True)}
    old_by_id = {c["chunk_id"]: c for c in old_cap}
    out = []
    for c in new_chunks:
        gid = c["group_id"]
        if gid in TOUCH_IDS:
            merged = deepcopy(c)
            old = old_by_gid.get(gid)
            if old and old.get("images"):
                merged["images"] = deepcopy(old["images"])
                merged["has_image"] = bool(old.get("has_image") or old["images"])
            out.append(merged)
        elif c["chunk_id"] in old_by_id:
            out.append(old_by_id[c["chunk_id"]])
        else:
            out.append(c)
    (PROD / "chunks_captioned.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def pipeline() -> None:
    backup()
    groups = apply_patches(load_groups(PROD / "qa_groups.json"))
    if not verify_specs(groups):
        raise SystemExit("spec verification failed")
    save_groups(PROD / "qa_groups.json", groups)
    run([sys.executable, "chunk_builder.py", str(PROD / "qa_groups.json"), str(PROD / "chunks_out")])
    merge_chunks_captioned()
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(PROD / "chunks_captioned.json"),
            str(PROD / "chroma_captioned"),
            "--model",
            str(MODEL),
        ]
    )
    run([sys.executable, str(ROOT / "_scratch/eval/bl_v1_05_display_probe.py")])
    run([sys.executable, str(ROOT / "_scratch/eval/verify_qa_023_acceptance.py")])
    run(
        [
            sys.executable,
            "eval_run.py",
            str(PROD / "chroma_captioned"),
            "--eval",
            "eval_queries_ad5s.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(ROOT / "_scratch/eval/bl_v1_05_wave3_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
