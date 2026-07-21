#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BL-RET-01a · batch re-embed docx 三库 + manual 四库，写入 doc_type / models。"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from copy import deepcopy
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MODEL = ROOT / "_scratch/modelscope/BAAI/bge-m3"
STAMP = date.today().strftime("%Y%m%d") + "-bl-ret-01a"

TARGETS: list[dict] = [
    {
        "id": "a3s-ts",
        "chunks": ROOT / "_scratch/run-006/chunks_captioned.json",
        "chroma": ROOT / "_scratch/run-007/chroma_captioned",
        "doc_type": "troubleshooting",
        "models": ["A3S", "A5S", "A8S"],
    },
    {
        "id": "ad5s-ts",
        "chunks": ROOT / "_scratch/run-ad5s/chunks_captioned.json",
        "chroma": ROOT / "_scratch/run-ad5s/chroma_captioned",
        "doc_type": "troubleshooting",
        "models": ["AD5S", "AD8S"],
    },
    {
        "id": "tc148-ts",
        "chunks": ROOT / "_scratch/run-tc148/chunks_captioned.json",
        "chroma": ROOT / "_scratch/run-tc148/chroma_captioned",
        "doc_type": "troubleshooting",
        "models": ["TC148"],
    },
    {
        "id": "a3s-manual",
        "chunks": ROOT / "_scratch/vlm_a3s_full/chunks_enriched.json",
        "chroma": ROOT / "_scratch/vlm_a3s_full/chroma_enriched",
        "doc_type": "installation_manual",
        "models": ["A3S", "A5S", "A8S"],
    },
    {
        "id": "ad5s-manual",
        "chunks": ROOT / "_scratch/vlm_ad5s_full/chunks_enriched.json",
        "chroma": ROOT / "_scratch/vlm_ad5s_full/chroma_enriched",
        "doc_type": "installation_manual",
        "models": ["AD5S", "AD8S"],
    },
    {
        "id": "at6132s-manual",
        "chunks": ROOT / "_scratch/vlm_at6132s_full/chunks_enriched.json",
        "chroma": ROOT / "_scratch/vlm_at6132s_full/chroma_enriched",
        "doc_type": "installation_manual",
        "models": ["AT6132S"],
    },
    {
        "id": "tc148-manual",
        "chunks": ROOT / "_scratch/vlm_tc148_full/chunks_enriched.json",
        "chroma": ROOT / "_scratch/vlm_tc148_full/chroma_enriched",
        "doc_type": "installation_manual",
        "models": ["TC148"],
    },
]


def load_chunks(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "chunks" in data:
        return data["chunks"]
    if isinstance(data, list):
        return data
    raise SystemExit(f"unsupported chunks format: {path}")


def stamp_chunks(chunks: list[dict], doc_type: str, models: list[str]) -> list[dict]:
    out = deepcopy(chunks)
    for c in out:
        c["doc_type"] = doc_type
        c["models"] = list(models)
    return out


def backup_chroma(chroma: Path) -> None:
    if not chroma.is_dir():
        return
    bak = chroma.parent / f"{chroma.name}.bak-{STAMP}"
    if bak.exists():
        return
    shutil.copytree(chroma, bak)
    print(f"  backup -> {bak.relative_to(ROOT)}")


def embed(stamped: list[dict], chroma: Path, tag: str) -> int:
    tmp = chroma.parent / f".{tag}-stamped-{STAMP}.json"
    tmp.write_text(json.dumps(stamped, ensure_ascii=False, indent=2), encoding="utf-8")
    backup_chroma(chroma)
    cmd = [
        sys.executable,
        str(ROOT / "embed_ingest_local.py"),
        str(tmp),
        str(chroma),
        "--model",
        str(MODEL),
    ]
    print("+", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)
    ret = sum(1 for c in stamped if c.get("is_retrievable", True))
    return ret


def verify_manifest(chroma: Path) -> dict:
    manifest = json.loads((chroma / "manifest.json").read_text(encoding="utf-8"))
    ret = [c for c in manifest["chunks"] if c.get("is_retrievable", True)]
    dtypes = {c.get("doc_type") for c in ret}
    with_models = sum(1 for c in ret if c.get("models"))
    return {"retrievable": len(ret), "doc_types": sorted(dtypes), "with_models": with_models}


def main() -> int:
    report: list[dict] = []
    for t in TARGETS:
        cid = t["id"]
        chunks_path: Path = t["chunks"]
        chroma: Path = t["chroma"]
        if not chunks_path.is_file():
            print(f"SKIP {cid}: missing {chunks_path}", file=sys.stderr)
            continue
        print(f"\n=== {cid} ===")
        stamped = stamp_chunks(load_chunks(chunks_path), t["doc_type"], t["models"])
        n = embed(stamped, chroma, cid.replace("/", "-"))
        stats = verify_manifest(chroma)
        row = {"id": cid, "embedded": n, **stats, "chroma": str(chroma.relative_to(ROOT))}
        report.append(row)
        print(f"  OK retrievable={stats['retrievable']} doc_types={stats['doc_types']} models={stats['with_models']}/{stats['retrievable']}")

    out = ROOT / "_scratch/eval/bl_ret_01a_batch_report.json"
    out.write_text(json.dumps({"stamp": STAMP, "targets": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
