#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_answer.py

RAG 生成式问答：基于检索上下文，调用 OpenAI 兼容 API 组织自然语言回答。
必须 grounded：不得编造步骤、电压、型号。

环境变量（与 translate 共用，或单独 QA_*）:
  QA_API_KEY / TRANSLATE_API_KEY / OPENAI_API_KEY
  QA_BASE_URL / TRANSLATE_BASE_URL
  QA_MODEL / TRANSLATE_MODEL
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 2048
RETRY_MAX_TOKENS = 4096
CS_EMAIL_LONG_MAX_TOKENS = 6144

# Prompt templates live in domains/<id>/prompts/. Names below resolve lazily for compat.
_PROMPT_NAMES = frozenset(
    {"QA_SYSTEM_PROMPT", "QA_SYSTEM_PROMPT_EN", "CS_EMAIL_SYSTEM_PROMPT_EN"}
)


def __getattr__(name: str):
    if name in _PROMPT_NAMES:
        from domains.loader import get_default_domain

        pack = get_default_domain().prompts
        if name == "QA_SYSTEM_PROMPT":
            return pack.qa_system_zh
        if name == "QA_SYSTEM_PROMPT_EN":
            return pack.qa_system_en
        if name == "CS_EMAIL_SYSTEM_PROMPT_EN":
            return pack.cs_email_system_en
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# Troubleshooting step starters for CS email post-normalize (F1 no-response ladder).
_CS_STEP_STARTER_RES = (
    r"Please measure the voltage",
    r"If the voltage is above",
    r"Disconnect all accessories",
    r"If there is still no (?:luck|response)",
    r"If it still does not help",
    r"If it still doesn't help",
    r"Next, please check the motor",
    r"Please check the motor",
    r"If the motor is fine but",
    r"Disconnect the BLUE",
)
_CS_VOLTAGE_BELOW_CONTINUATION = re.compile(r"^If the voltage is below", re.IGNORECASE)
_CS_STEP_LINE_RE = re.compile(
    r"^(?:"
    + "|".join(_CS_STEP_STARTER_RES)
    + r")",
    re.IGNORECASE,
)
_CS_STEP_SPLIT_RE = re.compile(
    r"(?<=\n)(?="
    + "|".join(_CS_STEP_STARTER_RES)
    + r")",
    re.IGNORECASE,
)
_CS_FOOTER_FROM_STEP_RE = re.compile(
    r"^([\s\S]*?)(\s+(?:Please let me know the result|Please let me know the results|"
    r"Please let me know the result one by one|And also please reply|"
    r"All TOPENS products|Thank you again)[\s\S]*)$",
    re.IGNORECASE,
)
_CS_PROCEED_REF_RE = re.compile(
    r"\b(?:proceed to|and then proceed to)\s+(?:step|test)\s*\d*"
    r"|\bcheck(?:\s+the)?\s+(?:next\s+)?step\s*\d*",
    re.IGNORECASE,
)
_CS_GO_ON_TROUBLESHOOTING_RE = re.compile(
    r"(?:If it still doesn'?t help,?\s*)?go on the troubleshooting below\.?\s*",
    re.IGNORECASE,
)


def _clean_cs_cross_refs(text: str) -> str:
    text = _CS_PROCEED_REF_RE.sub(
        " If so, please continue with the next step below.", text
    )
    text = re.sub(r"If so, please\s*(?=\.|,|\n|If )", "", text, flags=re.IGNORECASE)
    return _CS_GO_ON_TROUBLESHOOTING_RE.sub("\n\n", text)


def _split_numbered_step_blocks(raw: str) -> tuple[str, list[str]]:
    matches = list(re.finditer(r"(?m)^\d+\.\s+", raw))
    if len(matches) < 2:
        return raw, []
    intro = raw[: matches[0].start()].strip()
    steps: list[str] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = raw[start:end].strip()
        steps.append(re.sub(r"^\d+\.\s*", "", block).strip())
    return intro, steps


def _normalize_numbered_steps(raw: str) -> str:
    intro, steps = _split_numbered_step_blocks(raw)
    if len(steps) < 2:
        return raw

    processed: list[str] = []
    for step in steps:
        step = _clean_cs_cross_refs(step)
        processed.append(step)

    footer_mid = ""
    if processed:
        fm = _CS_FOOTER_FROM_STEP_RE.match(processed[-1])
        if fm:
            processed[-1] = fm.group(1).strip()
            footer_mid = fm.group(2).strip()

    chunks: list[str] = []
    if intro:
        chunks.append(intro)
    for i, step in enumerate(processed, 1):
        chunks.append(f"{i}. {step}")
    if footer_mid:
        chunks.append(footer_mid)
    return "\n\n".join(chunks)


def _normalize_unnumbered_steps(raw: str) -> str:
    paras = [p.strip() for p in re.split(r"\n\n+", raw) if p.strip()]
    intro: list[str] = []
    steps: list[str] = []
    for para in paras:
        if _CS_VOLTAGE_BELOW_CONTINUATION.match(para) and steps:
            steps[-1] += "\n\n" + para
        elif _CS_STEP_LINE_RE.match(para):
            steps.append(para)
        elif steps:
            steps[-1] += "\n\n" + para
        else:
            intro.append(para)

    if len(steps) < 2:
        steps = _split_cs_steps_by_lines(raw, intro)

    footer_mid = ""
    if steps:
        fm = _CS_FOOTER_FROM_STEP_RE.match(steps[-1])
        if fm:
            steps[-1] = fm.group(1).strip()
            footer_mid = fm.group(2).strip()

    if not steps:
        body = raw
        if footer_mid:
            body = f"{body}\n\n{footer_mid}".strip()
        return body

    chunks: list[str] = []
    if intro:
        chunks.append("\n\n".join(intro))
    for i, step in enumerate(steps, 1):
        step = re.sub(r"^\d+\.\s*", "", step.strip())
        chunks.append(f"{i}. {step}")
    if footer_mid:
        chunks.append(footer_mid)
    return "\n\n".join(chunks)


def _preprocess_cs_email_body(raw: str) -> str:
    raw = _clean_cs_cross_refs(raw)
    starter_alt = "|".join(_CS_STEP_STARTER_RES)
    raw = re.sub(
        rf"([.!?])\s+({starter_alt})",
        r"\1\n\n\2",
        raw,
        flags=re.IGNORECASE,
    )
    return _CS_STEP_SPLIT_RE.sub("\n\n", raw)


def normalize_cs_email_reply(text: str) -> str:
    """
    Post-process CS email body: split glued steps, strip fragment glue, re-number 1..N.
    Keeps intro/closing structure; moves media/address/warranty out of the last step.
    """
    if not (text or "").strip():
        return text

    raw = text.strip().replace("\r\n", "\n")

    closing = ""
    br = re.search(r"\n(Best regards,[\s\S]*)$", raw, re.IGNORECASE)
    if br:
        closing = br.group(1).strip()
        raw = raw[: br.start()].strip()

    raw = _preprocess_cs_email_body(raw)

    if len(re.findall(r"(?m)^\d+\.\s+", raw)) >= 2:
        body = _normalize_numbered_steps(raw)
    else:
        body = _normalize_unnumbered_steps(raw)

    if closing:
        return f"{body}\n\n{closing}".strip()
    return body.strip()


def _detect_glued_steps(text: str) -> bool:
    lines = (text or "").split("\n")
    for i in range(1, len(lines)):
        if re.match(r"^\d+\.\s", lines[i].strip()) and lines[i - 1].strip():
            return True
    return False


def audit_cs_email_reply(text: str, *, mail_type: str = "troubleshoot") -> dict:
    """Mechanical preflight for human E-H scoring (not semantic quality)."""
    body = text or ""
    steps = re.findall(r"(?m)^(\d+)\.\s", body)
    return {
        "step_count": len(steps),
        "proceed_ref": bool(_CS_PROCEED_REF_RE.search(body)),
        "check_step_ref": bool(
            re.search(r"check(?:\s+the)?\s+(?:next\s+)?step", body, re.IGNORECASE)
        ),
        "glued_steps": _detect_glued_steps(body),
        "mail_type": mail_type,
    }


def _cs_email_incomplete(text: str, *, mail_type: str = "troubleshoot") -> tuple[bool, str]:
    if mail_type == "presales":
        return False, ""
    t = (text or "").lower()
    if "best regards" not in t:
        return True, "missing sign-off"
    checks = [
        ("results", r"please let me know"),
        ("media", r"video|photo|picture"),
        ("address", r"shipping address|zip code|\bzip\b"),
    ]
    missing = [name for name, pat in checks if not re.search(pat, t, re.IGNORECASE)]
    if len(missing) >= 2:
        return True, f"missing closing: {', '.join(missing)}"
    return False, ""


def _cs_email_max_tokens(hits: list[dict], response_mode: str) -> int:
    if response_mode != "cs_email":
        return DEFAULT_MAX_TOKENS
    if hits and str(hits[0].get("group_id") or "") == "qa_011":
        return CS_EMAIL_LONG_MAX_TOKENS
    return RETRY_MAX_TOKENS


def _split_cs_steps_by_lines(raw: str, intro: list[str]) -> list[str]:
    """Line-level fallback when steps are glued with single newlines only."""
    intro_text = "\n\n".join(intro).strip()
    start = 0
    if intro_text and intro_text in raw:
        start = raw.find(intro_text) + len(intro_text)
    elif re.search(r"Checked with our engineer", raw, re.IGNORECASE):
        m = re.search(r"Checked with our engineer[^\n]*(?:\n[^\n]+)?", raw, re.IGNORECASE)
        if m:
            start = m.end()

    tail = raw[start:].strip()
    if not tail:
        return []

    lines = [ln.strip() for ln in tail.split("\n") if ln.strip()]
    steps: list[str] = []
    buf: list[str] = []
    for line in lines:
        if _CS_VOLTAGE_BELOW_CONTINUATION.match(line) and buf:
            buf.append(line)
            continue
        if _CS_STEP_LINE_RE.match(line) and buf:
            steps.append("\n\n".join(buf))
            buf = [line]
        elif _CS_STEP_LINE_RE.match(line) and not buf:
            buf = [line]
        elif buf:
            buf.append(line)
        elif not steps:
            continue
    if buf:
        steps.append("\n\n".join(buf))
    return steps


def _extract_customer_first_name(customer_email: str) -> str | None:
    """Parse first name from TOPENS contact-form style emails (Name: / Name:\\nFirst ...)."""
    text = customer_email or ""
    m = re.search(r"(?im)^Name:\s*\n\s*(\S+)", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?im)^Name:\s*(\S+)", text)
    if m and m.group(1).lower() not in ("name",):
        return m.group(1).strip()
    return None


def _get_config() -> tuple[str | None, str, str]:
    api_key = (
        os.environ.get("QA_API_KEY")
        or os.environ.get("TRANSLATE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    base_url = (
        os.environ.get("QA_BASE_URL")
        or os.environ.get("TRANSLATE_BASE_URL")
        or DEFAULT_BASE_URL
    ).rstrip("/")
    model = (
        os.environ.get("QA_MODEL")
        or os.environ.get("TRANSLATE_MODEL")
        or DEFAULT_MODEL
    )
    return api_key, base_url, model


def _chat_url(base_url: str) -> str:
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


from context_builder import build_context_for_hits
from style_exemplars import build_cs_email_system_prompt


def _looks_truncated(text: str, *, locale: str = "zh") -> bool:
    """启发式：句中截断或未闭合 Markdown。"""
    t = text.strip()
    if not t:
        return True
    if t[-1] in "。！？.!?":
        return False
    if t.endswith("**") or t.count("**") % 2 == 1:
        return True
    if locale == "zh" and t.endswith(("若", "请", "：", ":", "、", "，", ",", "（", "(")):
        return True
    if locale == "en" and t.endswith((",", ":", ";", "(", "[", "—", "-")):
        return True
    return len(t) < 80


def _call_chat(
    *,
    api_key: str,
    base_url: str,
    model: str,
    system: str,
    user_content: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    locale: str = "zh",
    disable_thinking: bool = False,
) -> tuple[str | None, bool]:
    """返回 (content, truncated)。"""
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "max_completion_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
    }
    if disable_thinking:
        payload["thinking"] = {"type": "disabled"}
    req = urllib.request.Request(
        _chat_url(base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    choices = data.get("choices") or []
    if not choices:
        return None, False

    choice = choices[0]
    msg = choice.get("message") or {}
    content = (msg.get("content") or "").strip()
    if not content and not disable_thinking:
        return _call_chat(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system=system,
            user_content=user_content,
            max_tokens=max_tokens,
            locale=locale,
            disable_thinking=True,
        )
    if not content:
        return None, False

    finish = choice.get("finish_reason") or ""
    truncated = finish == "length" or _looks_truncated(content, locale=locale)
    retry_cap = CS_EMAIL_LONG_MAX_TOKENS if max_tokens >= RETRY_MAX_TOKENS else RETRY_MAX_TOKENS
    if truncated and max_tokens < retry_cap:
        usage = data.get("usage") or {}
        next_tokens = retry_cap if max_tokens < RETRY_MAX_TOKENS else CS_EMAIL_LONG_MAX_TOKENS
        print(
            f"[generate_answer] 输出疑似截断 finish={finish!r} "
            f"completion_tokens={usage.get('completion_tokens')} "
            f"len={len(content)} → max_tokens={next_tokens} 重试",
            file=sys.stderr,
        )
        return _call_chat(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system=system,
            user_content=user_content,
            max_tokens=next_tokens,
            locale=locale,
            disable_thinking=disable_thinking,
        )
    return content, truncated


def generate_answer(
    user_query: str,
    hits: list[dict],
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    locale: str = "zh",
    response_mode: str = "qa",
    scenario_id: str | None = None,
    style_enabled: bool = True,
    mail_type: str | None = None,
) -> tuple[str | None, bool, str | None]:
    """
    基于 Top-K 检索结果生成回答。
    locale: zh | en
    response_mode: qa | cs_email
    scenario_id: optional eval id (cs_xxxx) for style routing / hold-out notes
    mail_type: troubleshoot | presales — affects incomplete detection
    返回 (正文, 是否截断/不完整, incomplete_reason)。未配置 API KEY 时 (None, False, None)。
    """
    key, url, mdl = _get_config()
    api_key = api_key or key
    base_url = (base_url or url).rstrip("/")
    model = model or mdl

    if not api_key:
        return None, False, None
    if not hits:
        if locale == "en":
            return (
                "We could not find a matching troubleshooting entry. "
                "Please contact TOPENS support with your order number and model.",
                False,
                None,
            )
        return "未检索到相关手册条目，请换一种说法或联系技术支持。", False, None

    context_parts = build_context_for_hits(
        hits, locale=locale, response_mode=response_mode
    )
    pin: str | None = None
    if locale == "en" and response_mode == "cs_email":
        from domains.eval_pack import context_force_include_groups, pinned_reference

        force_include = (
            context_force_include_groups(scenario_id) if scenario_id else frozenset()
        )
        context_parts = build_context_for_hits(
            hits,
            locale=locale,
            response_mode=response_mode,
            force_include_groups=force_include,
        )
        pin = pinned_reference(scenario_id) if scenario_id else None
        if pin:
            context_parts = [
                "--- Reference 0 ---\n"
                "Authoritative Joyce troubleshooting ladder (eval anchor; highest priority):\n"
                f"{pin}"
            ] + context_parts

    primary = hits[0]
    section = str(primary.get("section") or "")
    question = str(primary.get("question") or "")

    from domains.loader import get_default_domain

    prompts = get_default_domain().prompts
    effective_mail_type = mail_type or "troubleshoot"

    if locale == "en" and response_mode == "cs_email":
        system, _style = build_cs_email_system_prompt(
            section=section,
            question=question,
            customer_email=user_query,
            hits=hits,
            scenario_id=scenario_id,
            style_enabled=style_enabled,
        )
        first = _extract_customer_first_name(user_query)
        greet = f"Use Dear {first} in the greeting." if first else "Use Dear Customer if no name is found."
        user_content = (
            f"Customer email (English):\n{user_query}\n\n"
            + "\n\n".join(context_parts)
        )
        if effective_mail_type == "presales" and scenario_id:
            from domains.eval_pack import presales_brief

            brief = presales_brief(scenario_id)
            if brief:
                user_content += (
                    "\n\n--- Presales product brief (authoritative facts and links; "
                    "use these models as gate openers, not remotes) ---\n"
                    f"{brief}\n"
                )
                user_content += (
                    "\nMANDATORY presales output: include every purchasing URL from the brief "
                    "above as plain text (label each link with the product name). "
                    "Do not skip or summarize away links. "
                    "Cover arm, control board, and power-mode distinctions from the brief."
                )
        elif scenario_id:
            from domains.eval_pack import generation_brief

            gbrief = generation_brief(scenario_id)
            if gbrief:
                user_content += (
                    "\n\n--- Joyce reference anchors (cover these facts in numbered steps; "
                    "do not invent steps beyond references + anchors) ---\n"
                    f"{gbrief}\n"
                )
        if pin:
            ref_order = (
                "Follow Reference 0 numbered step order as the authoritative Joyce ladder; "
                "output all steps without merging or skipping. "
                "Use other references only for supplementary wording."
            )
        else:
            ref_order = (
                "Follow Reference 1 numbered step order when present; "
                "do not reorder or swap ladders from other references."
            )
        user_content += (
            "\n\nWrite the outbound reply email body. "
            f"{greet} Plain text only—no markdown asterisks or [text](url) links; paste URLs directly. "
            "Use Joyce, Lori, or Heidi as the signing agent—never output bracket placeholders. "
            f"{ref_order} "
            "Format: each troubleshooting step on its own line starting with 1. 2. 3. (plain text), "
            "with a blank line between steps. "
            "Never write 'proceed to test/step N' or 'check step N'. "
            "Keep voltage-below-22V branches inside the same step as the voltage test."
        )
        if any(str(h.get("group_id") or "") == "qa_002" for h in hits):
            user_content += (
                " For TC148 push-button cases: if Reference 1 lists extension-cable disconnect / "
                "short-cable test before instant-short, put that as step 1 even when the customer "
                "already tried jumpering terminals."
            )
    elif locale == "en":
        system = prompts.qa_system_en.replace("{section}", section).replace(
            "{question}", question
        )
        user_content = (
            f"User question (English):\n{user_query}\n\n"
            + "\n\n".join(context_parts)
            + "\n\nAnswer based on the references above."
        )
    else:
        system = prompts.qa_system_zh.replace("{section}", section).replace(
            "{question}", question
        )
        user_content = (
            f"用户问题：{user_query}\n\n"
            + "\n\n".join(context_parts)
            + "\n\n请基于以上资料回答。"
        )

    cs_max_tokens = _cs_email_max_tokens(hits, response_mode)
    cs_disable_thinking = response_mode == "cs_email"

    try:
        content, truncated = _call_chat(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system=system,
            user_content=user_content,
            max_tokens=cs_max_tokens,
            locale=locale,
            disable_thinking=cs_disable_thinking,
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"[generate_answer] API 失败: {e}", file=sys.stderr)
        return None, False, None

    incomplete_reason: str | None = None
    if content and locale == "en" and response_mode == "cs_email":
        content = normalize_cs_email_reply(content)
        incomplete, incomplete_reason = _cs_email_incomplete(
            content, mail_type=effective_mail_type
        )
        if incomplete:
            truncated = True

    if truncated and content:
        print("[generate_answer] 警告：回答仍可能不完整", file=sys.stderr)

    return content or None, bool(truncated and content), incomplete_reason


if __name__ == "__main__":
    sample_hit = {
        "section": "一、电源问题",
        "question": "控制板灯不亮（适配器）",
        "content_zh": "1 检查接线，测控制板BAT端口的电压\n2 如果电压正常，检查保险丝",
        "images": [{"file": "image_001.png", "caption": "保险丝位置示意图"}],
    }
    ans, trunc, _inc = generate_answer("控制板灯不亮怎么办", [sample_hit])
    print(ans or "(未配置 QA_API_KEY)")
    if trunc:
        print("(truncated)", file=sys.stderr)
