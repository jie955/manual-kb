#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
experiment_suite.py

按既定顺序跑检索实验 A→D，输出对比表。
实验 E（云 embedding）需先 embed_ingest_cloud.py 再单独 eval。

用法:
  python experiment_suite.py _scratch/run-006/chunks.json _scratch/run-006/eval
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from retrieval_engine import DEFAULT_RERANKER

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CHUNKS = SCRIPT_DIR / "_scratch/run-006/chunks.json"
DEFAULT_OUT = SCRIPT_DIR / "_scratch/run-006/eval"


def run_cmd(cmd: list[str], cwd: Path) -> None:
    print(f"\n>>> {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, cwd=str(cwd), check=True)


def download_modelscope(repo: str, cache_dir: Path) -> Path:
    from modelscope import snapshot_download

    path = snapshot_download(repo, cache_dir=str(cache_dir))
    print(f"model ready: {path}", file=sys.stderr)
    return Path(path)


def ingest(chunks: Path, chroma_dir: Path, model: str, python: str) -> None:
    chroma_dir.mkdir(parents=True, exist_ok=True)
    run_cmd(
        [
            python,
            "embed_ingest_local.py",
            str(chunks),
            str(chroma_dir),
            "--model",
            model,
        ],
        SCRIPT_DIR,
    )


def eval_one(
    chroma_dir: Path,
    name: str,
    python: str,
    out_dir: Path,
    *,
    model: str,
    prefix: bool = False,
    hybrid: float | None = None,
    rerank: bool = False,
    reranker_model: str | None = None,
) -> dict:
    cmd = [
        python,
        "eval_run.py",
        str(chroma_dir),
        "--name",
        name,
        "--model",
        model,
        "--json-out",
        str(out_dir / f"{name}.json"),
    ]
    if prefix:
        cmd.append("--prefix")
    if hybrid is not None:
        cmd.extend(["--hybrid", str(hybrid)])
    if rerank:
        cmd.append("--rerank")
    if reranker_model:
        cmd.extend(["--reranker-model", reranker_model])

    proc = subprocess.run(
        cmd,
        cwd=str(SCRIPT_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        raise SystemExit(f"eval failed: {name}")

    json_path = out_dir / f"{name}.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    return payload["summary"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval experiments A→D")
    parser.add_argument("chunks_json", type=Path, nargs="?", default=DEFAULT_CHUNKS)
    parser.add_argument("out_dir", type=Path, nargs="?", default=DEFAULT_OUT)
    parser.add_argument(
        "--python",
        default=str(SCRIPT_DIR.parent / "docx-to-md/.venv/Scripts/python.exe"),
    )
    parser.add_argument("--skip-ingest", action="store_true", help="跳过 B 步重入库")
    args = parser.parse_args()

    python = args.python
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    model_cache = SCRIPT_DIR / "_scratch/modelscope"

    small_model = str(SCRIPT_DIR / "_scratch/modelscope/Xorbits/bge-small-zh-v1.5")
    small_chroma = out_dir / "chroma_bge-small"

    if not Path(small_model).is_dir():
        download_modelscope("Xorbits/bge-small-zh-v1.5", model_cache)

    if not (small_chroma / "manifest.json").is_file():
        ingest(args.chunks_json, small_chroma, small_model, python)

    results: list[dict] = []

    # ① baseline
    results.append(
        eval_one(
            small_chroma,
            "A0_baseline_small",
            python,
            out_dir,
            model=small_model,
        )
    )

    # ② A: BGE query prefix
    results.append(
        eval_one(
            small_chroma,
            "A1_bge_prefix",
            python,
            out_dir,
            model=small_model,
            prefix=True,
        )
    )

    # ③ B: bge-m3 re-ingest
    m3_path = model_cache / "bge-m3"
    m3_chroma = out_dir / "chroma_bge-m3"
    m3_local = None
    for repo in ("AI-ModelScope/bge-m3", "BAAI/bge-m3"):
        try:
            m3_local = download_modelscope(repo, model_cache)
            break
        except Exception as exc:
            print(f"modelscope {repo} failed: {exc}", file=sys.stderr)
    if m3_local and not args.skip_ingest:
        ingest(args.chunks_json, m3_chroma, str(m3_local), python)
        results.append(
            eval_one(
                m3_chroma,
                "B1_bge-m3",
                python,
                out_dir,
                model=str(m3_local),
            )
        )
        results.append(
            eval_one(
                m3_chroma,
                "B2_bge-m3_prefix",
                python,
                out_dir,
                model=str(m3_local),
                prefix=True,
            )
        )
        best_chroma = m3_chroma
        best_model = str(m3_local)
        best_label = "bge-m3"
    else:
        best_chroma = small_chroma
        best_model = small_model
        best_label = "bge-small"

    # ④ C: hybrid
    for alpha in (0.7, 0.5):
        results.append(
            eval_one(
                best_chroma,
                f"C_hybrid_{best_label}_a{int(alpha*10)}",
                python,
                out_dir,
                model=best_model,
                hybrid=alpha,
            )
        )

    # ⑤ D: reranker
    reranker_path = SCRIPT_DIR / DEFAULT_RERANKER
    if not reranker_path.is_dir():
        try:
            downloaded = download_modelscope("BAAI/bge-reranker-v2-m3", model_cache)
            reranker_path = Path(downloaded)
        except Exception as exc:
            print(f"reranker download skipped: {exc}", file=sys.stderr)

    if reranker_path.is_dir():
        reranker_model = str(reranker_path)
        results.append(
            eval_one(
                best_chroma,
                f"D1_rerank_{best_label}",
                python,
                out_dir,
                model=best_model,
                rerank=True,
                reranker_model=reranker_model,
            )
        )
        results.append(
            eval_one(
                best_chroma,
                f"D2_hybrid_rerank_{best_label}",
                python,
                out_dir,
                model=best_model,
                hybrid=0.6,
                rerank=True,
                reranker_model=reranker_model,
            )
        )

    report = {
        "experiments": results,
        "table": [
            {
                "name": r["name"],
                "top1": r["top1_acc"],
                "top3": r["top3_acc"],
                "top1_hits": f"{r['top1_hits']}/{r['total']}",
            }
            for r in results
        ],
    }
    report_path = out_dir / "experiment_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== Experiment Summary ===", file=sys.stderr)
    print(f"{'name':<32} {'Top1':>8} {'Top3':>8} {'hits':>8}", file=sys.stderr)
    for row in report["table"]:
        print(
            f"{row['name']:<32} {row['top1']:>8.2%} {row['top3']:>8.2%} {row['top1_hits']:>8}",
            file=sys.stderr,
        )
    print(f"\nfull report: {report_path}", file=sys.stderr)
    print(json.dumps(report["table"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
