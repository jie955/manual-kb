#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
page_identity.py — manifest 权威的页面身份（chunk_id / parent_id / page_range / page_key）。

设计约束（BL-PDF-04）：
  - normalize_page_chunks() 是纯后处理：仅改 JSON 字段，**不发起网络 / VLM 调用**。
  - 对印刷页（printed_page 已设），若 VLM 已用正确 canonical id，覆写为 **恒等变换**（回归 p9/p18/p20）。
  - images[].file / image_id **不在本模块 scope**（见 docs/排期.md §8 · BL-PDF-02）。
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

DOC_PREFIX_DEFAULT = "a3s-manual"


def page_key(entry: dict) -> str:
    if entry.get("printed_page") is not None:
        return f"printed:{int(entry['printed_page'])}"
    return f"idx:{int(entry['pdf_index'])}"


def canonical_parent_id(entry: dict, doc_prefix: str = DOC_PREFIX_DEFAULT) -> str:
    if entry.get("printed_page") is not None:
        return f"{doc_prefix}-p{int(entry['printed_page'])}"
    return f"{doc_prefix}-idx{int(entry['pdf_index'])}"


def page_range_for_entry(entry: dict) -> list[int]:
    """printed 页用印刷页码；前置页用 pdf_index（与印刷页码可能同数字，靠 page_key 区分）。"""
    if entry.get("printed_page") is not None:
        n = int(entry["printed_page"])
        return [n, n]
    n = int(entry["pdf_index"])
    return [n, n]


def child_suffix(chunk_id: str, doc_prefix: str = DOC_PREFIX_DEFAULT) -> str:
    """从 chunk_id 提取 canonical parent 之后的后缀（含 leading hyphen）。"""
    m = re.match(
        rf"^{re.escape(doc_prefix)}-(?:p\d+|idx\d+)(?P<suffix>.*)$",
        chunk_id,
    )
    if m:
        return m.group("suffix")
    return ""


def normalize_page_chunks(
    page_chunks: list[dict],
    entry: dict,
    *,
    doc_prefix: str = DOC_PREFIX_DEFAULT,
) -> list[dict]:
    """
    将单页 VLM 输出对齐 manifest 权威身份。

    纯函数：不读盘、不访问网络。输入现有 JSON 数组即可（含 .vlm_cache 解析结果）。
    印刷页若已是 canonical 命名，chunk_id 列表不变。
    """
    if not page_chunks:
        return []

    canonical = canonical_parent_id(entry, doc_prefix)
    pk = page_key(entry)
    pr = page_range_for_entry(entry)

    normalized: list[dict] = []
    for raw in page_chunks:
        c = deepcopy(raw)
        c["page_key"] = pk
        c["page_range"] = list(pr)

        is_parent = c.get("is_retrievable") is False and not c.get("parent_id")
        suffix = child_suffix(c.get("chunk_id", ""), doc_prefix)

        if is_parent:
            c["chunk_id"] = canonical
        else:
            if c.get("parent_id"):
                c["parent_id"] = canonical
            if suffix:
                c["chunk_id"] = canonical + suffix
            elif c.get("chunk_id") == canonical:
                pass
            elif not c.get("parent_id") and c.get("is_retrievable"):
                c["chunk_id"] = canonical + "-" + _slug_tail(c.get("chunk_id", "chunk"))

        normalized.append(c)

    return _dedupe_single_page_parents(normalized, canonical)


def _slug_tail(chunk_id: str, fallback: str = "chunk") -> str:
    part = chunk_id.rsplit("-", 1)[-1] if chunk_id else fallback
    return part or fallback


def _dedupe_single_page_parents(chunks: list[dict], canonical: str) -> list[dict]:
    parents = [
        i
        for i, c in enumerate(chunks)
        if c.get("is_retrievable") is False and not c.get("parent_id")
    ]
    if len(parents) <= 1:
        return chunks

    out = list(chunks)
    keep_i = max(parents, key=lambda i: _parent_richness(chunks[i]))
    for i in parents:
        if i == keep_i:
            out[i]["chunk_id"] = canonical
            continue
        out[i] = None
    return [c for c in out if c is not None]


def _parent_richness(chunk: dict) -> int:
    zh = (chunk.get("content_zh") or "").strip()
    en = (chunk.get("content_en") or "").strip()
    return len(zh) + len(en)


def chunk_ids_for_page(page_chunks: list[dict]) -> list[str]:
    return [c["chunk_id"] for c in page_chunks if c.get("chunk_id")]


def assert_printed_page_identity_unchanged(
    before: list[dict],
    after: list[dict],
    *,
    label: str = "",
) -> None:
    """回归：印刷好页 normalize 前后 chunk_id 列表须完全一致。"""
    b = chunk_ids_for_page(before)
    a = chunk_ids_for_page(after)
    if b != a:
        raise AssertionError(
            f"{label} chunk_id changed:\n  before={b}\n  after={a}"
        )


def build_vlm_cache_key(
    image_path: Path,
    user_text: str,
    page_type: str,
    model: str,
    cache_version: str,
    *,
    file_hash_fn,
) -> str:
    return (
        file_hash_fn(image_path)
        + "|"
        + page_type
        + "|"
        + hashlib.sha256(user_text.encode()).hexdigest()[:16]
        + "|"
        + model
        + "|"
        + cache_version
    )


def duplicate_chunk_id_report(chunks: list[dict]) -> tuple[int, list[str]]:
    """
    返回 (重复 chunk_id 种类数, 重复 id 列表)。
    与 BL-PDF-04 验收一致：p1/p3 各算 1 种重复。
    """
    ids = [c["chunk_id"] for c in chunks if c.get("chunk_id")]
    counts = Counter(ids)
    dup_ids = sorted(cid for cid, n in counts.items() if n > 1)
    return len(dup_ids), dup_ids


def assert_printed_page_canonical_p2(
    after: list[dict],
    *,
    printed: int = 2,
    doc_prefix: str = DOC_PREFIX_DEFAULT,
) -> None:
    """
    p2 反例样本：无 duplicate，但须确认 normalize 后仍为印刷页命名空间（非前置页 idx）。
    """
    expected_parent = f"{doc_prefix}-p{printed}"
    expected_pk = f"printed:{printed}"
    parent = next(
        (c for c in after if c.get("chunk_id") == expected_parent),
        None,
    )
    if parent is None:
        raise AssertionError(f"missing parent {expected_parent!r}")
    if parent.get("page_key") != expected_pk:
        raise AssertionError(
            f"p{printed} page_key={parent.get('page_key')!r} != {expected_pk!r}"
        )
    for c in after:
        if c.get("page_key") and c["page_key"] != expected_pk:
            raise AssertionError(f"p{printed} chunk {c.get('chunk_id')} wrong page_key")
        cid = c.get("chunk_id", "")
        if f"{doc_prefix}-idx" in cid:
            raise AssertionError(f"p{printed} misclassified as front matter: {cid!r}")
        pid = c.get("parent_id")
        if pid and pid != expected_parent:
            raise AssertionError(f"p{printed} child parent_id={pid!r} != {expected_parent!r}")


def lookup_vlm_cache_raw(
    cache: dict,
    image_path: Path,
    user_text: str,
    page_type: str,
    model: str,
    cache_version: str,
    *,
    file_hash_fn,
) -> str | None:
    """
    查找 cache 原文。精确键未命中时，按「文件哈希|page_type|」前缀回退
    （兼容 prompt 文案变更导致的 user_text 哈希变化）。
    """
    exact = build_vlm_cache_key(
        image_path, user_text, page_type, model, cache_version, file_hash_fn=file_hash_fn
    )
    if exact in cache:
        return cache[exact]
    fh = file_hash_fn(image_path)
    prefix = f"{fh}|{page_type}|"
    suffix = f"|{model}|{cache_version}"
    matches = sorted(k for k in cache if k.startswith(prefix) and k.endswith(suffix))
    if matches:
        if len(matches) > 1:
            print(
                f"[cache] fuzzy pick 1/{len(matches)} for {image_path.name} ({page_type})",
                file=sys.stderr,
            )
        return cache[matches[0]]
    return None


def load_chunks_from_cache(
    manifest: dict,
    cache: dict,
    pages_dir: Path,
    *,
    normalize: bool,
    doc_prefix: str = DOC_PREFIX_DEFAULT,
    model: str = "gemini-2.5-flash",
    cache_version: str = "vlm1",
    parse_json_array=None,
    file_hash_fn=None,
    pilot_chunks_path: Path | None = None,
    pilot_reuse: set[int] | None = None,
) -> list[dict]:
    """从 cache 组装 chunks；normalize=False 为 VLM 原始 id（用于 duplicate before）。"""
    from pdf_vlm_parser import (
        _file_hash,
        _parse_json_array,
        build_user_prompt,
        load_pilot_chunks_for_pages,
        page_image_path,
    )

    if parse_json_array is None:
        parse_json_array = _parse_json_array
    if file_hash_fn is None:
        file_hash_fn = _file_hash
    if pilot_reuse is None:
        pilot_reuse = set()
    if pilot_chunks_path is None:
        pilot_chunks_path = Path(__file__).resolve().parent / "_scratch" / "vlm_pilot" / "pilot_chunks.json"

    all_chunks: list[dict] = []
    for entry in manifest.get("pages") or []:
        printed = entry.get("printed_page")
        printed_int = int(printed) if printed is not None else None

        if (
            printed_int is not None
            and printed_int in pilot_reuse
            and pilot_chunks_path.is_file()
        ):
            pilot_for = load_pilot_chunks_for_pages(pilot_chunks_path, {printed_int})
            if pilot_for:
                page_chunks = (
                    normalize_page_chunks(pilot_for, entry, doc_prefix=doc_prefix)
                    if normalize
                    else pilot_for
                )
                all_chunks.extend(page_chunks)
                continue

        image_path = page_image_path(entry, pages_dir)
        if not image_path.is_file():
            print(
                f"[renormalize] skip {page_key(entry)}: missing {image_path}",
                file=sys.stderr,
            )
            continue
        page_type = entry.get("page_type", "other")
        user_text = build_user_prompt(entry, manifest)
        raw = lookup_vlm_cache_raw(
            cache,
            image_path,
            user_text,
            page_type,
            model,
            cache_version,
            file_hash_fn=file_hash_fn,
        )
        if raw is None:
            print(
                f"[renormalize] skip {page_key(entry)}: cache miss",
                file=sys.stderr,
            )
            continue
        raw_chunks = parse_json_array(raw)
        if normalize:
            page_chunks = normalize_page_chunks(
                raw_chunks, entry, doc_prefix=doc_prefix
            )
        else:
            page_chunks = raw_chunks
        all_chunks.extend(page_chunks)
    return all_chunks


def renormalize_chunks_from_cache(
    manifest: dict,
    cache: dict,
    pages_dir: Path,
    *,
    doc_prefix: str = DOC_PREFIX_DEFAULT,
    model: str = "gemini-2.5-flash",
    cache_version: str = "vlm1",
    parse_json_array=None,
    file_hash_fn=None,
) -> list[dict]:
    """
    从 .vlm_cache.json 重建 manual_chunks，**不调用 VLM API**。

    需要与 pdf_vlm_parser.parse_pages 相同的 cache 键；pilot 复用页需另行 merge。
    """
    return load_chunks_from_cache(
        manifest,
        cache,
        pages_dir,
        normalize=True,
        doc_prefix=doc_prefix,
        model=model,
        cache_version=cache_version,
        parse_json_array=parse_json_array,
        file_hash_fn=file_hash_fn,
        pilot_reuse=set(manifest.get("pilot_reuse") or []),
    )


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_vlm_cache(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
