#!/usr/bin/env python3
"""Task 0 · Oracle side-by-side generation for cs_side_by_side_demo.md cases."""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _load_dotenv() -> None:
    for path in (ROOT / ".env", ROOT.parent / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


_load_dotenv()

from generate_answer import _get_config, generate_answer  # noqa: E402

CASES = [
    {
        "id": "A",
        "case_id": "cs_0013",
        "label": "#13 A3S",
        "chroma": ROOT / "_scratch/run-007/chroma_captioned",
        "oracle_groups": ["qa_034", "qa_022"],
        "customer_email": (
            "Dear TOPENS,\n\n"
            "Need help this gate opener keeps stopping before opening fully.\n\n"
            "Product Model: A3S\n"
            "Where Did You Buy?: AMAZON.COM\n"
            "Country / Region: Texas\n"
            "Gate Application: Ranch / Farm\n"
            "Gate Length: 12-14' (3.6-4.3m)\n"
            "Accessories: M12\n\n"
            "Thanks,\nEdward"
        ),
    },
    {
        "id": "B",
        "case_id": "cs_0008",
        "label": "#8 PW502+TC148",
        "chroma": ROOT / "_scratch/run-tc148/chroma_captioned",
        "oracle_groups": ["qa_002"],
        "customer_email": (
            "Dear TOPENS,\n\n"
            "Push button not working, therefore we jumpered out #4&5 at the main "
            "control panel and still nothing happened. Other than that everything works.\n\n"
            "Product Model: PW502\n"
            "Accessories: TC148 waterproof push button, M12 remote\n"
            "Country / Region: Canada\n\n"
            "Thanks,\nCindy Tan"
        ),
    },
    {
        "id": "C",
        "case_id": "cs_0022",
        "label": "#22 A5132 (approx oracle)",
        "chroma": ROOT / "_scratch/run-ad5s/chroma_captioned",
        "oracle_groups": ["qa_015"],
        "customer_email": (
            "Dear TOPENS,\n\n"
            "Just recently my gate started acting differently. The left panel - furthest "
            "from the controller - seems to open and reaches full open then immediately "
            "starts closing about 4 feet. (there use to be a pause which it is not doing "
            "any more.) This stops the right panel from closing as well. When I press the "
            "remote button it tries to open again and then after a pause (the correct pause) "
            "only closes 4 feet. I am wondering if I need to move the magnets on the left panel. "
            "Please advise.\n\n"
            "Product Model: A5132\n"
            "Gate Type: Dual Swing Gate\n"
            "How Does Your Gate Open?: Swing Gate - Push to Open\n\n"
            "Thanks,\nStuart"
        ),
    },
]


def load_group_hit(chroma_dir: Path, group_id: str) -> dict:
    manifest = json.loads((chroma_dir / "manifest.json").read_text(encoding="utf-8"))
    chunks = [c for c in manifest["chunks"] if c.get("group_id") == group_id]
    if not chunks:
        raise KeyError(f"{group_id} not in {chroma_dir}")
    for c in chunks:
        if str(c.get("chunk_id", "")).endswith("_parent"):
            return c
    return max(
        chunks,
        key=lambda c: len(c.get("content_zh") or "") + len(c.get("content_en") or ""),
    )


def hit_from_chunk(chunk: dict) -> dict:
    return {
        "section": chunk.get("section"),
        "question": chunk.get("question"),
        "content_zh": chunk.get("content_zh"),
        "content_en": chunk.get("content_en"),
        "images": chunk.get("images") or [],
        "links": chunk.get("links") or [],
        "customer_reply_templates": chunk.get("customer_reply_templates") or [],
        "group_id": chunk.get("group_id"),
    }


def main() -> int:
    api_key, _, model = _get_config()
    if not api_key:
        print("ERROR: set QA_API_KEY / OPENAI_API_KEY", file=sys.stderr)
        return 1

    out_dir = ROOT / "_scratch/eval"
    results: list[dict] = []

    for case in CASES:
        hits = []
        for gid in case["oracle_groups"]:
            chunk = load_group_hit(case["chroma"], gid)
            hits.append(hit_from_chunk(chunk))
        reply, truncated, _incomplete = generate_answer(
            case["customer_email"],
            hits,
            locale="en",
            response_mode="cs_email",
        )
        results.append(
            {
                "id": case["id"],
                "case_id": case["case_id"],
                "label": case["label"],
                "oracle_groups": case["oracle_groups"],
                "truncated": truncated,
                "reply": reply or "",
            }
        )
        print(f"\n{'=' * 60}\n{case['label']} · oracle {case['oracle_groups']}\n{'=' * 60}\n")
        print(reply or "(empty)")
        if truncated:
            print("\n(warn: possibly truncated)", file=sys.stderr)

    stamp = date.today().isoformat()
    json_path = out_dir / "cs_side_by_side_generated.json"
    json_path.write_text(
        json.dumps({"generated": stamp, "model": model, "results": results}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
