#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge troubleshooting + installation_manual chroma per model family (BL-RET-01a)."""

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
STAMP = date.today().strftime("%Y%m%d") + "-merge"

# Same model family · troubleshooting + manual → unified search index
FAMILIES: dict[str, dict] = {
    "a3s": {
        "models": ["A3S", "A5S", "A8S"],
        "sources": [
            ROOT / "_scratch/run-007/chroma_captioned",
            ROOT / "_scratch/vlm_a3s_full/chroma_enriched",
        ],
        "ts_stamped": ROOT / "_scratch/run-007/.a3s-ts-stamped-20260708-bl-ret-01a.json",
        "out": ROOT / "_scratch/unified/a3s/chroma_merged",
    },
    "ad5s": {
        "models": ["AD5S", "AD8S"],
        "sources": [
            ROOT / "_scratch/run-ad5s/chroma_captioned",
            ROOT / "_scratch/vlm_ad5s_full/chroma_enriched",
        ],
        "ts_stamped": ROOT / "_scratch/run-ad5s/.ad5s-ts-stamped-20260708-bl-ret-01a.json",
        "out": ROOT / "_scratch/unified/ad5s/chroma_merged",
    },
    "tc148": {
        "models": ["TC148"],
        "sources": [
            ROOT / "_scratch/run-tc148/chroma_captioned",
            ROOT / "_scratch/vlm_tc148_full/chroma_enriched",
        ],
        "ts_stamped": ROOT / "_scratch/run-tc148/.tc148-ts-stamped-20260708-bl-ret-01a.json",
        "out": ROOT / "_scratch/unified/tc148/chroma_merged",
    },
}


def load_ts_chunks(spec: dict) -> list[dict]:
    stamped: Path | None = spec.get("ts_stamped")
    ts_chroma: Path = spec["sources"][0]
    if stamped and stamped.is_file():
        data = json.loads(stamped.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else data["chunks"]
    return load_manifest_chunks(ts_chroma)


def load_manifest_chunks(chroma_dir: Path) -> list[dict]:
    chunks = json.loads((chroma_dir / "manifest.json").read_text(encoding="utf-8"))["chunks"]
    # Fallback: legacy manifests may lack doc_type on disk; infer from source dir name.
    for c in chunks:
        if c.get("doc_type"):
            continue
        if "chroma_enriched" in chroma_dir.as_posix() or "manual" in chroma_dir.name:
            c["doc_type"] = "installation_manual"
        else:
            c["doc_type"] = "troubleshooting"
    return chunks


def merge_family(family_id: str, spec: dict) -> dict:
    merged: list[dict] = []
    seen: set[str] = set()
    ts_chunks = load_ts_chunks(spec)
    manual_chunks = load_manifest_chunks(spec["sources"][1])
    for c in ts_chunks + manual_chunks:
        cid = c["chunk_id"]
        if cid in seen:
            tag = "manual" if c.get("doc_type") == "installation_manual" else "ts"
            cid = f"{family_id}::{tag}::{cid}"
            c = deepcopy(c)
            c["chunk_id"] = cid
        seen.add(cid)
        merged.append(deepcopy(c))

    out: Path = spec["out"]
    if out.exists():
        bak = out.parent / f"{out.name}.bak-{STAMP}"
        if not bak.exists():
            shutil.copytree(out, bak)
        shutil.rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / f".merged-{family_id}-{STAMP}.json"
    tmp.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    cmd = [
        sys.executable,
        str(ROOT / "embed_ingest_local.py"),
        str(tmp),
        str(out),
        "--model",
        str(MODEL),
    ]
    print(f"=== merge {family_id} ({len(merged)} chunks) ===")
    print("+", " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)
    ret = [c for c in merged if c.get("is_retrievable", True)]
    ts = sum(1 for c in ret if c.get("doc_type") == "troubleshooting")
    manual = sum(1 for c in ret if c.get("doc_type") == "installation_manual")
    return {
        "family": family_id,
        "out": str(out.relative_to(ROOT)),
        "total_chunks": len(merged),
        "retrievable": len(ret),
        "troubleshooting": ts,
        "installation_manual": manual,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Merge ts + manual chroma per family")
    parser.add_argument("--families", nargs="*", choices=sorted(FAMILIES), default=sorted(FAMILIES))
    args = parser.parse_args()

    report = [merge_family(fid, FAMILIES[fid]) for fid in args.families]
    out = ROOT / "_scratch/eval/merge_model_chroma_report.json"
    out.write_text(json.dumps({"stamp": STAMP, "families": report}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
