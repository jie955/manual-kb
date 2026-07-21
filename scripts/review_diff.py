#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review_diff.py

用 .env 配置的 LLM 审查 git diff，输出 Markdown 报告。
不依赖 Cursor BYOK；默认走 AGICTO OpenAI 兼容（gpt-5.1-codex-high）。

环境变量:
  REVIEW_BACKEND=openai | anthropic   默认 openai（AGICTO 等网关）
  REVIEW_API_KEY / QA_API_KEY / TRANSLATE_API_KEY / OPENAI_API_KEY
  REVIEW_BASE_URL                     默认 https://api.agicto.cn/v1
  REVIEW_MODEL                        默认 gpt-5.1-codex-high
  ANTHROPIC_BASE_URL                  anthropic 后端时用

用法:
  python scripts/review_diff.py
  python scripts/review_diff.py --uncommitted
  python scripts/review_diff.py --base main
  python scripts/review_diff.py --files generate_answer.py context_builder.py
  git diff main...HEAD | python scripts/review_diff.py --stdin
  python scripts/review_diff.py --output _scratch/eval/my_review.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from env_utils import load_dotenv  # noqa: E402

DEFAULT_ANTHROPIC_BASE = "https://api.anthropic.com"
DEFAULT_OPENAI_BASE = "https://api.agicto.cn/v1"
DEFAULT_MODEL_ANTHROPIC = "claude-sonnet-4-20250514"
DEFAULT_MODEL_OPENAI = "gpt-5.1-codex-high"
DEFAULT_MAX_TOKENS = 8192
DEFAULT_MAX_DIFF_CHARS = 120_000
DEFAULT_OUTPUT = REPO / "_scratch" / "eval" / "code_review_latest.md"

REVIEW_SYSTEM_PROMPT = """You are a senior code reviewer for manual-kb, a RAG + customer-service email pipeline for industrial gate opener manuals.

Review the provided git diff. Focus on:
1. Bugs and regressions (logic errors, off-by-one, missing error handling that breaks the pipeline)
2. Trust / grounding boundaries — generate_answer and CS email paths must not invent steps, voltages, terminal numbers, or models
3. Env and secrets — .env keys must not be logged; load_dotenv patterns should not overwrite unintentionally
4. Eval gates — changes to run_cs_e2e_gate, style exemplars, or ADR-0003 English pipeline constraints
5. Data contracts — chunks.json / chroma manifest field renames without migration

Output Markdown with sections:
## Summary
(one paragraph)

## Findings
For each issue: ### [severity: critical|major|minor|nit] Title
- **File**: path
- **Issue**: what is wrong
- **Suggestion**: concrete fix

## Positive notes
(brief, optional)

## Verdict
PASS | PASS WITH NITS | NEEDS CHANGES

If the diff is empty or too large to review meaningfully, say so under Summary.
Do not invent findings not supported by the diff."""


def _run_git(args: list[str], *, cwd: Path = REPO) -> str:
    try:
        out = subprocess.check_output(
            ["git", *args],
            cwd=cwd,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"git {' '.join(args)} failed:\n{exc.output}") from exc
    return out


def _run_git_allow_diff_exit(args: list[str], *, cwd: Path = REPO) -> str:
    """git diff exits 1 when differences exist; treat that as success."""
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode in (0, 1):
        return proc.stdout
    raise SystemExit(f"git {' '.join(args)} failed:\n{proc.stdout}{proc.stderr}")


def _has_head(*, cwd: Path = REPO) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        capture_output=True,
    )
    return proc.returncode == 0


def _git_branch_head(*, cwd: Path = REPO) -> tuple[str, str]:
    branch_proc = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    branch = (branch_proc.stdout or "").strip() or "unknown"
    head_proc = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    head = (head_proc.stdout or "").strip() if head_proc.returncode == 0 else "no commits"
    if not _has_head(cwd=cwd):
        branch = f"{branch} (no commits)"
    return branch, head


def _status_paths() -> list[str]:
    out = _run_git(["status", "--porcelain"])
    paths: list[str] = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            paths.append(path)
    return paths


def _diff_no_index(paths: list[str]) -> str:
    null = "NUL" if os.name == "nt" else "/dev/null"
    parts: list[str] = []
    for path in paths:
        full = REPO / path
        if not full.is_file():
            continue
        chunk = _run_git_allow_diff_exit(["diff", "--no-index", null, path])
        if chunk.strip():
            parts.append(chunk)
    return "\n".join(parts)


def _detect_base_branch(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("main", "master"):
        try:
            _run_git(["rev-parse", "--verify", candidate])
            return candidate
        except SystemExit:
            continue
    return "HEAD~1"


def _collect_diff(
    *,
    mode: str,
    base: str,
    files: list[str] | None,
) -> tuple[str, str]:
    """Return (diff_text, description)."""
    if mode == "stdin":
        diff = sys.stdin.read()
        return diff, "stdin"

    if mode == "uncommitted":
        if not _has_head():
            if not files:
                raise SystemExit(
                    "仓库尚无 commit，无法 git diff HEAD。\n"
                    "请指定 --files scripts/review_diff.py …，或 git add 后首次 commit。"
                )
            diff = _diff_no_index(files)
            return diff, "uncommitted (no commits; git diff --no-index)"
        diff = _run_git(["diff", "HEAD"])
        if files:
            diff = _run_git(["diff", "HEAD", "--", *files])
        return diff, "uncommitted (working tree vs HEAD)"

    if mode == "staged":
        diff = _run_git(["diff", "--cached"])
        if files:
            diff = _run_git(["diff", "--cached", "--", *files])
        return diff, "staged (--cached)"

    if mode == "branch":
        merge_base = _run_git(["merge-base", base, "HEAD"]).strip()
        diff = _run_git(["diff", f"{merge_base}...HEAD"])
        if files:
            diff = _run_git(["diff", f"{merge_base}...HEAD", "--", *files])
        return diff, f"branch (merge-base {merge_base}..HEAD vs {base})"

    if mode == "files":
        if not files:
            raise SystemExit("--files requires at least one path")
        if not _has_head():
            diff = _diff_no_index(files)
            return diff, f"files (--no-index): {', '.join(files)}"
        diff = _run_git(["diff", "HEAD", "--", *files])
        return diff, f"files vs HEAD: {', '.join(files)}"

    raise SystemExit(f"unknown diff mode: {mode}")


def _get_config() -> tuple[str, str | None, str, str]:
    backend = os.environ.get("REVIEW_BACKEND", "openai").lower()
    api_key = (
        os.environ.get("REVIEW_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("TRANSLATE_API_KEY")
        or os.environ.get("CAPTION_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or os.environ.get("QA_API_KEY")
    )
    if backend == "anthropic":
        base_url = (
            os.environ.get("ANTHROPIC_BASE_URL")
            or os.environ.get("REVIEW_BASE_URL")
            or DEFAULT_ANTHROPIC_BASE
        ).rstrip("/")
        model = os.environ.get("REVIEW_MODEL", DEFAULT_MODEL_ANTHROPIC)
    else:
        base_url = (
            os.environ.get("REVIEW_BASE_URL")
            or os.environ.get("QA_BASE_URL")
            or os.environ.get("TRANSLATE_BASE_URL")
            or DEFAULT_OPENAI_BASE
        ).rstrip("/")
        model = os.environ.get("REVIEW_MODEL", DEFAULT_MODEL_OPENAI)
    return backend, api_key, base_url, model


def _anthropic_messages_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def _openai_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _call_anthropic(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system: str,
    user_content: str,
    max_tokens: int,
) -> str:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user_content}],
    }
    req = urllib.request.Request(
        _anthropic_messages_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    if not blocks:
        raise ValueError(f"no text in anthropic response: {data!r}")
    return "".join(blocks).strip()


def _call_openai_compat(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system: str,
    user_content: str,
    max_tokens: int,
) -> str:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    }
    req = urllib.request.Request(
        _openai_chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("error"):
        err = data["error"]
        msg = err.get("message") or err.get("code") or str(err)
        raise ValueError(f"API error: {msg}")
    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"no choices in openai response: {data!r}")
    content = ((choices[0].get("message") or {}).get("content") or "").strip()
    if not content:
        raise ValueError(f"empty content in openai response: {data!r}")
    return content


def _call_review_llm(
    *,
    backend: str,
    api_key: str,
    base_url: str,
    model: str,
    diff: str,
    diff_desc: str,
    max_tokens: int,
) -> str:
    branch, head = _git_branch_head()
    user_content = (
        f"Repository: manual-kb\n"
        f"Branch: {branch}\n"
        f"HEAD: {head}\n"
        f"Diff scope: {diff_desc}\n\n"
        f"```diff\n{diff}\n```"
    )
    if backend == "anthropic":
        return _call_anthropic(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system=REVIEW_SYSTEM_PROMPT,
            user_content=user_content,
            max_tokens=max_tokens,
        )
    return _call_openai_compat(
        api_key=api_key,
        base_url=base_url,
        model=model,
        system=REVIEW_SYSTEM_PROMPT,
        user_content=user_content,
        max_tokens=max_tokens,
    )


def _build_report(
    *,
    review_body: str,
    diff_desc: str,
    backend: str,
    model: str,
    truncated: bool,
    original_len: int,
) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    branch, head = _git_branch_head()
    meta = [
        "# Code Review (LLM)",
        "",
        f"- **Generated**: {ts}",
        f"- **Branch**: `{branch}` @ `{head}`",
        f"- **Scope**: {diff_desc}",
        f"- **Backend**: {backend} / `{model}`",
    ]
    if truncated:
        meta.append(
            f"- **Note**: diff truncated from {original_len} to {DEFAULT_MAX_DIFF_CHARS} chars"
        )
    meta.extend(["", "---", ""])
    return "\n".join(meta) + review_body + "\n"


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="LLM code review for git diff")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        "--uncommitted",
        action="store_const",
        const="uncommitted",
        dest="mode",
        help="review working tree vs HEAD (default)",
    )
    scope.add_argument(
        "--staged",
        action="store_const",
        const="staged",
        dest="mode",
        help="review staged changes only",
    )
    scope.add_argument(
        "--branch",
        action="store_const",
        const="branch",
        dest="mode",
        help="review branch vs merge-base with --base",
    )
    scope.add_argument(
        "--stdin",
        action="store_const",
        const="stdin",
        dest="mode",
        help="read diff from stdin",
    )
    parser.set_defaults(mode="uncommitted")
    parser.add_argument(
        "--base",
        default=None,
        help="base branch for --branch (default: main or master)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="limit diff to these paths (implies file-scoped uncommitted if no other mode)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"write report here (default: {DEFAULT_OUTPUT.relative_to(REPO)})",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="also print report to stdout",
    )
    parser.add_argument(
        "--max-diff-chars",
        type=int,
        default=DEFAULT_MAX_DIFF_CHARS,
        help=f"truncate diff beyond this size (default {DEFAULT_MAX_DIFF_CHARS})",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"LLM max output tokens (default {DEFAULT_MAX_TOKENS})",
    )
    args = parser.parse_args()

    mode = args.mode
    if args.files and mode == "uncommitted" and "--branch" not in sys.argv and "--staged" not in sys.argv and "--stdin" not in sys.argv:
        mode = "files"

    diff, diff_desc = _collect_diff(mode=mode, base=_detect_base_branch(args.base), files=args.files)

    if not diff.strip():
        print("[review_diff] no diff to review", file=sys.stderr)
        raise SystemExit(0)

    original_len = len(diff)
    truncated = False
    if original_len > args.max_diff_chars:
        truncated = True
        diff = diff[: args.max_diff_chars] + "\n\n... [diff truncated] ...\n"
        print(
            f"[review_diff] warning: diff truncated {original_len} → {args.max_diff_chars} chars",
            file=sys.stderr,
        )

    backend, api_key, base_url, model = _get_config()
    if not api_key:
        raise SystemExit(
            "未配置 API Key。请在 .env 设置 REVIEW_API_KEY 或 ANTHROPIC_API_KEY "
            "(或 REVIEW_BACKEND=openai 时用 REVIEW_API_KEY / QA_API_KEY)"
        )

    print(
        f"[review_diff] backend={backend} model={model} scope={diff_desc}",
        file=sys.stderr,
    )

    try:
        review_body = _call_review_llm(
            backend=backend,
            api_key=api_key,
            base_url=base_url,
            model=model,
            diff=diff,
            diff_desc=diff_desc,
            max_tokens=args.max_tokens,
        )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"API connection error: {exc.reason}") from exc
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    report = _build_report(
        review_body=review_body,
        diff_desc=diff_desc,
        backend=backend,
        model=model,
        truncated=truncated,
        original_len=original_len,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"[review_diff] wrote {args.output}", file=sys.stderr)

    if args.stdout:
        print(report)


if __name__ == "__main__":
    main()
