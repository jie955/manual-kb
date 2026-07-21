#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-V1-05 Wave1+2：Tier A spot-fix 9 组 answer_zh（+ qa_008 ladder）→ prod。"""

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
STAMP = "20260705-bl-v1-05-wave1"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
TOUCH_IDS = frozenset(
    {"qa_001", "qa_002", "qa_004", "qa_005", "qa_006", "qa_007", "qa_008", "qa_009", "qa_012"}
)

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

# 完整 answer_zh 替换（surgical · 仅增补规格句，不改步骤结构）
ANSWER_ZH: dict[str, str] = {
    "qa_001": (
        "1 检查接线，测量控制板+BAT-端子（11#、12#）电压是否高于22V\n"
        "2 如果电压正常，检查控制板power灯是否正常闪烁（约每秒闪2次），如果没亮，检查更换保险丝"
        "（规格∅5×20mm 10A 250VAC快断玻璃管；备用保险丝在说明书包装内）\n"
        "3 如果电压低于22VDC，检查适配器输出是否36VDC；断开电池和控制板之间的接线，测量电池电压是否正常，"
        "如果低，测TS24-U适配器的输出，如果输出正常，多充一会儿试试"
        "（电池规格需24V 12Ah，或2节12V电池串联成24V）\n"
        "4 如果电池电压还是不行，检查电池，更换电池试试"
    ),
    "qa_002": (
        "1 检查接线，测量控制板+BAT-端子（11#、12#）电压是否22V以上\n"
        "2 如果电压正常，检查更换保险丝（规格∅5×20mm 10A 250VAC快断玻璃管；备用保险丝在说明书包装内）\n"
        "3 如果电压低于正常值，把太阳能控制器和太阳板、控制板断开，用万用表测电池电压和控制器load端口的输出，\n"
        "a 如果电池电压正常，但是控制器输出不对，控制器坏，需要更换；\n"
        "b 如果电池电压低于22VDC，用额外的电池充电器把电池充满再试；\n"
        "c 如果电池充满的情况下，电池电压依然22VDC以下，电池坏，需要更换电池；"
    ),
    "qa_004": (
        "检查太阳能板（开路测试）\n"
        "断开太阳能板与TCS3之间的连接，断开各块太阳能板之间的连接，在无遮挡的正午阳光下，测量每一块太阳能板的开路电压\n"
        "正常值：>42VDC\n"
        "如果某块板明显低于42VDC → 该太阳能板损坏\n"
        "检查电池电压\n"
        "断开TCS3与电池之间的连接, 测量电池电压\n"
        "如果电压 <22VDC → 用外部充电器将电池充到24VDC以上，再重新接入系统\n"
        "测试TCS3是否正常（断开太阳能板）\n"
        "保持太阳能板断开, 仅连接电池到TCS3, 测量以下端口：\n"
        "端口正常值\t                   异常判断\n"
        "BAT端口\t= 电池电压; 若异常 → TCS3可能内部BAT通路故障\n"
        "LOAD端口>22VDC\t; 若低于22VDC或为0 → TCS3损坏\n"
        "如果BAT和LOAD均正常 → TCS3是好的，继续第4步\n"
        "接回太阳能板，整体验证\n"
        "接回太阳能板到TCS3, 测量以下端口，三者应大致等于电池电压\n"
        "SOL端口≈ 电池电压\n"
        "BAT端口\t≈ 电池电压\n"
        "LOAD端口≈ 电池电压\n"
        "如果端口电压异常→ 太阳能板损坏\n"
        "电池耗电异常 Abnormal Battery Drain\n"
        "确认电池规格、接线正确（一般需24V 12Ah或2×12V 12Ah串联），\n"
        "纯太阳能且无市电时：每增加一个持续耗电配件（如对射/有线键盘/外接收器等）建议太阳能板增加约30W；"
        "若有效阳光不足6小时/天或门机每天开关超过10次，也需加大太阳能板和电池容量。\n"
        "断开其他额外用电设备（如是否给其他外部用电器供电，如：备用灯、门禁读卡器等）。\n"
        "拔掉所有配件及机臂，看是否还异常耗电。\n"
        "还不行的话，换一组新的符合规格的电池试试。\n"
        "好了 → 电池问题。\n"
        "没好 → 继续下一步。\n"
        "断开TCS3与控制板的连接。（用TCS3）\n"
        "依然耗电 → TCS3问题。\n"
        "不耗电了 → 接回空控制板（不接配件）。\n"
        "又耗电 → 控制板问题。\n"
        "不耗电 → 机臂或某个配件问题（逐个接回排查）。"
    ),
    "qa_005": (
        "症状：学习灯不亮（按CODE SW后CODE LED不亮；非学习灯常亮）\n"
        "1 检查电源灯亮不亮；测量控制板+BAT-端子（11#、12#）电压是否高于22V，"
        "检查保险丝（备用保险丝在说明书包装内），如果都正常而学不上，控制板可能坏\n"
        "2 断开配件试试"
    ),
    "qa_006": (
        "症状：学习灯亮但学不上（按CODE SW后CODE LED能亮；非学习灯不亮）\n"
        "先测量控制板+BAT-端子（11#、12#）电压是否高于22V。\n"
        "断开配件，换电池（遥控器使用2粒CR2025）、换一个遥控器，试一试；"
        "清除所有密码重学，如果还不可以，瞬时短接push button端口（4#、5#）试试"
    ),
    "qa_007": (
        "症状：其他遥控器正常的，只是其中一个或者一些不能操控门机\n"
        "换电池试试（遥控器使用2粒CR2025电池）\n"
        "清除重学试试\n"
        "如果还是不行，且是我们自己的遥控器的话，遥控器坏了"
    ),
    "qa_008": (
        "1打开控制箱调整天线位置和方向（M12遥控器开外区参考距离约65英尺/20米）\n"
        "2 通过穿线孔尝试把天线拉出来点试试\n"
        "3 更换遥控器电池试试（每个遥控器需2粒3V CR2025锂电池）\n"
        "4 加ERM12外接收器"
    ),
    "qa_009": (
        "换遥控器电池（2粒CR2025），同时也清除遥控编码，重学试试\n"
        "离门机近一点试试，如果有用，把天线放不同位置，方向（水平、竖直）试试\n"
        "3. 瞬时短接push button，看看门机是不是每瞬时短接一次，都会有相应的动作\n"
        "4. 打开离合，确保门可以手动推拉顺畅，同时保持离合打开，按遥控器，观察是否每按一下，门机都有相应的动作\n"
        "5 观察周围环境是否有导致信号减弱或失效的干扰物，如是否紧邻紧高压线、大功率变压器，金属栅栏，电信基站、广播电台发射塔等"
    ),
    "qa_012": (
        "1 检查端口接的线与线之间是否有铜丝触碰到，确认保险丝规格正确（∅5×20mm 10A 250VAC快断玻璃管）；\n"
        "2 断开控制板端口上的有线配件，机臂线，只保留电源接线，然后按遥控器；\n"
        "如果保险丝烧，检查控制板的输入电压，正常电压24VDC左右；如果电压没问题，那就是控制板坏，可以看看控制板表面是否有元器件短路痕迹；\n"
        "(2) 如果保险丝不烧，把机臂从门上拿下来，机臂电机线接回控制板，打开离合，按遥控器看看烧不烧，此时如果烧，问题在电机电流大，如果不烧，合上离合再按遥控器，如果烧，问题在机臂内部卡顿，手动推拉机臂是否顺畅；\n"
        "3如果没问题，把机臂装门上再按遥控器试试，如果这个时候烧 说明负载过大，可能门本身较重或卡顿，"
        "需要检查门本身是否可以推拉顺畅（可在距门铰链约1米/3.3英尺处手动开合测试），并问问门宽门重；\n"
        "4如果以上都好的，依次把有线配件接回去，逐一排查哪个配件导致烧控制板的。"
    ),
}

QA_008_LADDER_ZH: dict[int, str] = {
    1: "打开控制箱调整天线位置和方向（M12遥控器开外区参考距离约65英尺/20米）",
    3: "更换遥控器电池试试（每个遥控器需2粒3V CR2025锂电池）",
    4: "加ERM12外接收器",
}


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_patches(groups: list[dict]) -> list[dict]:
    out = deepcopy(groups)
    for g in out:
        gid = g["group_id"]
        if gid not in TOUCH_IDS:
            continue
        g["answer_zh"] = ANSWER_ZH[gid]
        if gid == "qa_008":
            ladder = g.get("troubleshooting_ladder") or []
            for step in ladder:
                idx = step.get("step_index")
                if idx in QA_008_LADDER_ZH:
                    step["content_zh"] = QA_008_LADDER_ZH[idx]
        print(f"  patched {gid}")
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
    chroma_dst = PROD / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(PROD / "chroma_captioned", chroma_dst)
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
        raise SystemExit("spec verification failed — abort before embed")
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
            str(ROOT / "_scratch/eval/bl_v1_05_wave1_eval.json"),
        ]
    )


if __name__ == "__main__":
    pipeline()
