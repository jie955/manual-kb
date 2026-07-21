#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A3S post-handtest batch: LINK-A3S · IMG-EXT-02 · ZH-SKELETON qa_041 · RETR-DISAMB qa_040/041."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from docx import Document
from link_utils import apply_simple_tier_links
from image_utils import normalize_images
from qa_doc_extractor import extract_images_from_paragraph, get_heading_level, iter_block_items

GROUPS_DIR = ROOT / "_scratch/run-006"
CHROMA_DIR = ROOT / "_scratch/run-007/chroma_captioned"
IMAGE_DIR = GROUPS_DIR / "images"
DOCX = ROOT / "samples/troubleshooting/A3S-A5S-A8S常见问题排查.docx"
MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = "20260705-a3s-post-handtest"

# H1 section key → target group(s) for orphan inline images (type A)
ORPHAN_IMG_TARGETS: dict[str, list[str]] = {
    "八、开关门过程中走停或反弹": ["qa_035"],
    "十三、电机转机臂不伸缩": ["qa_037"],
    "十四、机臂声音异常": ["qa_039"],
    "十五、离合打不开": ["qa_038"],
}

# Type B: shared asset already in prod images/
TYPE_B_IMAGES: dict[str, list[str]] = {
    "qa_033": ["image_019.png"],
}

DISAMB_PATCHES: dict[str, dict] = {
    "qa_040": {
        "question": "WD40日常保养润滑（喷WD40/机油）Routine Maintenance",
        "answer_zh_prefix": "症状：WD40/机油日常保养·机臂外表/防冻（非拆机臂·非grease内腔·非深度润滑）",
        "answer_zh_body": (
            "日常保养润滑：\n"
            "寒冷地区1°C（30°F）以下，每4~6周在不锈钢拉杆上喷WD40防冻结。\n"
            "日常保养请在不锈钢拉杆上喷WD40或普通机油即可。"
        ),
    },
    "qa_041": {
        "question": "深度润滑（拆机臂·grease内腔）Deep Lubrication",
        "answer_zh_prefix": "症状：运行不顺畅·拆机臂润滑内腔/丝母/丝杆/grease（非单独WD40外表保养）",
        "answer_zh_body": (
            "如果运行不顺畅，可进一步拆机臂润滑不锈钢管内壁、丝母内外侧及丝杆。\n"
            "使用能耐当地最低温度的润滑脂。\n"
            "参考下方视频与维护指南链接。"
        ),
    },
}

TOUCH_IDS = frozenset(
    {
        "qa_003",
        "qa_033",
        "qa_035",
        "qa_038",
        "qa_039",
        "qa_040",
        "qa_041",
    }
)


def load_groups(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_groups(path: Path, groups: list[dict]) -> None:
    path.write_text(json.dumps(groups, ensure_ascii=False, indent=2), encoding="utf-8")


def next_image_index() -> int:
    nums = []
    for p in IMAGE_DIR.glob("image_*.*"):
        try:
            nums.append(int(p.stem.split("_")[1]))
        except (IndexError, ValueError):
            continue
    return max(nums) if nums else 0


def section_target(h1: str) -> list[str] | None:
    for key, gids in ORPHAN_IMG_TARGETS.items():
        if key in h1:
            return gids
    return None


def extract_orphan_images_by_section() -> dict[str, list[str]]:
    """Extract type-A orphan inline images from docx; return section_key → filenames in IMAGE_DIR."""
    doc = Document(str(DOCX))
    counter = [next_image_index()]
    section_files: dict[str, list[str]] = {}
    state: dict | None = None

    for block in iter_block_items(doc):
        if not hasattr(block, "text"):
            continue
        level = get_heading_level(block)
        if level == 1:
            state = {"h1": block.text.strip(), "in_h2": False}
            continue
        if state is None:
            continue
        if level in (2, 3):
            state["in_h2"] = True
            continue
        if state["in_h2"]:
            continue
        h1 = state["h1"]
        gids = section_target(h1)
        if not gids:
            continue
        imgs = extract_images_from_paragraph(block, doc, str(IMAGE_DIR), counter)
        if imgs:
            key = next(k for k in ORPHAN_IMG_TARGETS if k in h1)
            section_files.setdefault(key, []).extend(imgs)
    return section_files


def apply_link_a3s(groups: list[dict]) -> None:
    for g in groups:
        gid = g["group_id"]
        if gid == "qa_003":
            if apply_simple_tier_links(g):
                print(f"  LINK-A3S {gid}: links={len(g.get('links') or [])}")
        elif gid in ("qa_001", "qa_002"):
            urls_in_en = "topens.com" in (g.get("answer_en") or "")
            has_links = bool(g.get("links"))
            print(f"  LINK-A3S verify {gid}: topens_in_en={urls_in_en} links={has_links} -> no change")


def apply_img_ext02(groups: list[dict]) -> dict[str, list[str]]:
    by_id = {g["group_id"]: g for g in groups}
    applied: dict[str, list[str]] = {}

    section_files = extract_orphan_images_by_section()
    for section_key, gids in ORPHAN_IMG_TARGETS.items():
        files = section_files.get(section_key, [])
        if not files:
            print(f"  IMG-EXT type-A {section_key}: no new files")
            continue
        for gid in gids:
            g = by_id[gid]
            merged = list(dict.fromkeys((g.get("images") or []) + files))
            g["images"] = merged
            applied[gid] = merged
            print(f"  IMG-EXT type-A {gid}: +{files} -> {merged}")

    for gid, files in TYPE_B_IMAGES.items():
        g = by_id[gid]
        merged = list(dict.fromkeys((g.get("images") or []) + files))
        g["images"] = merged
        applied[gid] = merged
        print(f"  IMG-EXT type-B {gid}: shared {files} -> {merged}")

    # qa_040: docx §十七 grease paragraph has text ref but no inline image in source
    g40 = by_id["qa_040"]
    if not g40.get("images"):
        print("  IMG-EXT qa_040: docx has no inline grease image — skipped (text ref only)")

    return applied


def apply_disamb_and_zh_skeleton(groups: list[dict]) -> None:
    for g in groups:
        gid = g["group_id"]
        if gid not in DISAMB_PATCHES:
            continue
        p = DISAMB_PATCHES[gid]
        g["question"] = p["question"]
        g["answer_zh"] = p["answer_zh_prefix"] + "\n" + p["answer_zh_body"]
        print(f"  RETR-DISAMB+ZH {gid}: q={g['question'][:48]}… zh={len(g['answer_zh'])}")


def backup() -> None:
    chroma_dst = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
    if not chroma_dst.exists():
        shutil.copytree(CHROMA_DIR, chroma_dst)
    groups_path = GROUPS_DIR / "qa_groups.json"
    bak_groups = GROUPS_DIR / f"qa_groups.json.bak-{STAMP}"
    if not bak_groups.exists():
        shutil.copy2(groups_path, bak_groups)
    print(f"backup stamp {STAMP}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(x) for x in cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_manifest_chunks(use_backup: bool = True) -> list[dict]:
    base = CHROMA_DIR
    if use_backup:
        bak = CHROMA_DIR.parent / f"chroma_captioned.bak-{STAMP}"
        if (bak / "manifest.json").is_file():
            base = bak
    data = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    return data["chunks"]


def merge_image_captions(new_imgs: list, old_chunks: list[dict]) -> list[dict]:
    caption_by_file: dict[str, dict] = {}
    for c in old_chunks:
        for img in normalize_images(c.get("images")):
            if img.get("caption"):
                caption_by_file[img["file"]] = deepcopy(img)
    out: list[dict] = []
    for img in normalize_images(new_imgs):
        if img["file"] in caption_by_file:
            out.append(deepcopy(caption_by_file[img["file"]]))
        else:
            out.append(img)
    return out


def merge_captioned_chunks(new_chunks: list[dict], old_chunks: list[dict]) -> list[dict]:
    old_by_id = {c["chunk_id"]: c for c in old_chunks}
    out: list[dict] = []
    for c in new_chunks:
        gid = c["group_id"]
        if gid not in TOUCH_IDS and c["chunk_id"] in old_by_id:
            out.append(deepcopy(old_by_id[c["chunk_id"]]))
            continue
        merged = deepcopy(c)
        old = old_by_id.get(c["chunk_id"])
        if merged.get("images"):
            merged["images"] = merge_image_captions(merged["images"], old_chunks)
            merged["has_image"] = bool(merged["images"])
        elif old and old.get("images"):
            merged["images"] = deepcopy(old["images"])
            merged["has_image"] = bool(old.get("has_image") or old["images"])
        out.append(merged)
    return out


def probe_retrieval() -> None:
    from display_content_utils import is_thin_zh, thin_zh_reason
    from qa_server import _ask, _init_engine, _load_dotenv

    _load_dotenv()
    _init_engine(CHROMA_DIR, "_scratch/modelscope/BAAI/bge-m3")
    probes = [
        ("LINK", "太阳能不能给电池充电", "qa_003", None),
        ("IMG-B", "机臂只朝一个方向转", "qa_033", None),
        ("IMG-A", "开关门过程中走停反弹", "qa_035", None),
        ("IMG-A", "离合钥匙拧不开", "qa_038", None),
        ("DISAMB", "日常保养喷WD40润滑", "qa_040", True),
        ("DISAMB", "深度润滑拆机臂", "qa_041", True),
        ("DISAMB", "WD40", "qa_040", None),
    ]
    print("\n=== display probe ===")
    for tag, q, exp_gid, exp_thin in probes:
        data = _ask(q, use_llm=False)
        top = (data.get("hits") or [None])[0] or {}
        gid = top.get("group_id")
        score = top.get("score")
        zh = top.get("content_zh") or ""
        en = top.get("content_en") or ""
        thin = is_thin_zh(zh, en)
        reason = thin_zh_reason(zh, en) or "-"
        ok_gid = gid == exp_gid
        ok_thin = exp_thin is None or thin == exp_thin
        ok = ok_gid and ok_thin
        imgs = len(top.get("images") or [])
        print(
            f"{tag} | {q[:20]} | top1={gid}({score:.3f}) exp={exp_gid} "
            f"thin={thin} imgs={imgs} | {'PASS' if ok else 'FAIL'}"
        )
        if tag == "DISAMB" and q == "WD40":
            print(f"  WD40 note: top1={gid} (path-B target qa_040)")


def pipeline() -> None:
    backup()
    old_chunks = load_manifest_chunks()
    groups = load_groups(GROUPS_DIR / "qa_groups.json")
    print("--- LINK-A3S ---")
    apply_link_a3s(groups)
    print("--- IMG-EXT-02 ---")
    apply_img_ext02(groups)
    print("--- ZH-SKELETON + RETR-DISAMB ---")
    apply_disamb_and_zh_skeleton(groups)
    save_groups(GROUPS_DIR / "qa_groups.json", groups)

    chunks_out = GROUPS_DIR / "chunks_out"
    run([sys.executable, "chunk_builder.py", str(GROUPS_DIR / "qa_groups.json"), str(chunks_out)])
    new_chunks = json.loads((chunks_out / "chunks.json").read_text(encoding="utf-8"))
    merged = merge_captioned_chunks(new_chunks, old_chunks)
    chunks_captioned = GROUPS_DIR / "chunks_captioned.json"
    chunks_captioned.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    run(
        [
            sys.executable,
            "embed_ingest_local.py",
            str(chunks_captioned),
            str(CHROMA_DIR),
            "--model",
            str(MODEL),
        ]
    )
    eval_out = ROOT / "_scratch/eval/a3s_post_handtest_eval.json"
    run(
        [
            sys.executable,
            "eval_run.py",
            str(CHROMA_DIR),
            "--eval",
            "eval_queries.json",
            "--model",
            str(MODEL),
            "--json-out",
            str(eval_out),
        ]
    )
    probe_retrieval()


if __name__ == "__main__":
    pipeline()
