#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate.py

用途：
    针对 answer_zh 为空（原文本身只有英文说明）的问答组，调用大模型把英文正文
    翻译/摘要成中文，专供 embedding_text 检索匹配使用（方案 B）。

重要原则：
    - 翻译结果只用于检索匹配（embedding_text），不作为面向用户的权威答案展示。
    - 结果落盘缓存（按原文内容哈希做 key），避免重复调用、重复计费。
    - 调用失败时优雅降级：返回 None，由 chunk_builder 走 fallback_to_english。

依赖（OpenAI 兼容路由）：
    TRANSLATE_API_KEY   路由 KEY（也可用 OPENAI_API_KEY）
    TRANSLATE_BASE_URL  如 https://api.openai.com/v1 或你的网关 /v1
    TRANSLATE_MODEL     如 gpt-4o-mini、deepseek-chat、qwen-turbo 等

用法：
    python translate.py "Some English maintenance text..."
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"

DEFAULT_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".translate_cache.json"
)

TRANSLATE_SYSTEM_PROMPT = (
    "你是技术文档翻译助手。任务：把用户提供的英文故障排查/维修说明，"
    "翻译成简体中文摘要，专门用于知识库的检索匹配（embedding），不是给终端用户看的最终答案。\n"
    "要求：\n"
    "1. 完整保留所有关键技术信息（电压值、型号、部件名称、阈值、操作动作），不要省略或简化到失去可检索性；\n"
    "2. 语言自然、简洁，不需要逐字直译，但不能改变原意，尤其是数值和判断条件；\n"
    "3. 只输出翻译结果本身，不要任何解释、前缀或markdown标记。"
)


def _load_cache(cache_path: str) -> dict:
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_cache(cache_path: str, cache: dict) -> None:
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _chat_completions_url(base_url: str) -> str:
    base = _normalize_base_url(base_url)
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _get_config() -> tuple[str | None, str, str]:
    api_key = os.environ.get("TRANSLATE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("TRANSLATE_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("TRANSLATE_MODEL", DEFAULT_MODEL)
    return api_key, base_url, model


def _call_openai_compatible_api(
    english_text: str,
    *,
    api_key: str,
    base_url: str,
    model: str,
) -> str:
    """调用 OpenAI 兼容 /chat/completions，失败时抛出异常由上层捕获。"""
    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
            {"role": "user", "content": english_text},
        ],
    }
    request = urllib.request.Request(
        _chat_completions_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))

    choices = data.get("choices") or []
    if not choices:
        raise ValueError(f"API 返回结果中没有 choices: {data}")

    message = choices[0].get("message") or {}
    content = (message.get("content") or "").strip()
    if not content:
        raise ValueError(f"API 返回结果中没有文本内容: {data}")
    return content


def translate_batch(texts: list[str], cache_path: str = DEFAULT_CACHE_PATH) -> dict[str, str | None]:
    """
    批量翻译入口。
    返回 {原文: 译文或 None}。None 表示未配置 KEY 或调用失败。
    """
    api_key, base_url, model = _get_config()
    cache = _load_cache(cache_path)
    results: dict[str, str | None] = {}

    if not api_key:
        print(
            "[translate] 警告：未检测到 TRANSLATE_API_KEY / OPENAI_API_KEY，"
            "跳过翻译，相关组将走 fallback_to_english。",
            file=sys.stderr,
        )
        return {text: None for text in texts}

    cache_dirty = False
    for text in texts:
        key = _text_hash(text)
        if key in cache:
            results[text] = cache[key]
            continue

        try:
            translated = _call_openai_compatible_api(
                text, api_key=api_key, base_url=base_url, model=model
            )
            cache[key] = translated
            results[text] = translated
            cache_dirty = True
        except (urllib.error.URLError, ValueError, TimeoutError, json.JSONDecodeError) as e:
            print(f"[translate] 翻译失败，将走降级策略: {e}", file=sys.stderr)
            results[text] = None

    if cache_dirty:
        _save_cache(cache_path, cache)

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python translate.py \"英文文本\"")
        print("")
        print("环境变量:")
        print("  TRANSLATE_API_KEY   路由 KEY")
        print("  TRANSLATE_BASE_URL  OpenAI 兼容 base URL（默认 https://api.openai.com/v1）")
        print("  TRANSLATE_MODEL     模型名（默认 gpt-4o-mini）")
        sys.exit(1)
    sample_text = sys.argv[1]
    result = translate_batch([sample_text])
    print(result[sample_text])
