#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # _scratch
LIBS = [
    ("A3S", "vlm_a3s_full", 46),
    ("AD5S", "vlm_ad5s_full", 48),
    ("AT6132S", "vlm_at6132s_full", 47),
    ("TC148", "vlm_tc148_full", 2),
]

for label, dname, expected_pages in LIBS:
    p = ROOT / dname
    print(f"=== {label} ({dname}) ===")
    stats = p / "parse_stats.json"
    if stats.exists():
        s = json.loads(stats.read_text(encoding="utf-8"))
        failed = s.get("failed", "?")
        total = s.get("pages_total", expected_pages)
        print(f"  VLM parse_stats: {total - int(failed) if isinstance(failed, int) else '?'}/{total} ok, failed={failed}")
    retry = list(p.glob("parse_stats_*.json"))
    for rf in retry:
        rs = json.loads(rf.read_text(encoding="utf-8"))
        if rs.get("failed") == 0 and rs.get("pages_total", 0) <= 5:
            print(f"  retry {rf.name}: {rs.get('parsed_via_api')}/{rs.get('pages_total')} ok")
    for fname in ("chunks_enriched.json", "chunks.json"):
        f = p / fname
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            retr = sum(1 for c in data if c.get("is_retrievable", True))
            print(f"  {fname}: {len(data)} blocks, retrievable={retr}")
    chroma = p / "chroma_enriched" / "manifest.json"
    if chroma.exists():
        chunks = json.loads(chroma.read_text(encoding="utf-8")).get("chunks") or []
        retr = sum(1 for c in chunks if c.get("is_retrievable", True))
        print(f"  chroma_enriched: {retr} vectors (manifest)")
    else:
        print("  chroma_enriched: —")
    if label == "A3S":
        merged = ROOT / "unified" / "a3s" / "chroma_merged" / "manifest.json"
    elif label == "AD5S":
        merged = ROOT / "unified" / "ad5s" / "chroma_merged" / "manifest.json"
    elif label == "TC148":
        merged = ROOT / "unified" / "tc148" / "chroma_merged" / "manifest.json"
    else:
        merged = None
    if merged and Path(merged).exists():
        mc = json.loads(Path(merged).read_text(encoding="utf-8")).get("chunks") or []
        manual = sum(1 for c in mc if c.get("doc_type") == "installation_manual" and c.get("is_retrievable", True))
        print(f"  unified merge: {manual} manual retrievable chunks")
    print()

print("=== catalog PDF (samples/catalog/) ===")
print("  未 ingest · 一期不做")
