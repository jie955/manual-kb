#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CS Email Agent Workflow v1 — shared path for API, demo, and eval runners (ADR §6)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from context_builder import build_context_for_hits
from domains.loader import get_default_domain
from engine.trace import RunTrace, detect_context_zh_leak
from generate_answer import (
    _get_config,
    audit_cs_email_reply,
    generate_answer,
)
from library_router import UnifiedLibrary, hits_to_context, unified_search
from pilot_en_context import enrich_hits_for_cs_email
from domains.prompt_style import StyleSelection, select_style


def dedupe_display_hits(hits: list[dict]) -> list[dict]:
    """Collapse duplicate troubleshooting chunks; keep manual supplement visible."""
    seen_ts: set[str] = set()
    out: list[dict] = []
    for h in hits:
        gid = str(h.get("group_id") or "")
        dtype = h.get("doc_type") or "troubleshooting"
        if dtype != "installation_manual":
            if gid in seen_ts:
                continue
            seen_ts.add(gid)
        out.append(h)
    for i, h in enumerate(out, start=1):
        h["rank"] = i
    return out


def _gen_hit_rows(hits: list[dict]) -> list[dict]:
    return [
        {
            "section": r.get("section"),
            "question": r.get("question"),
            "content_zh": r.get("content_zh"),
            "content_en": r.get("content_en"),
            "images": r.get("images") or [],
            "links": r.get("links") or [],
            "customer_reply_templates": r.get("customer_reply_templates") or [],
            "group_id": r.get("group_id"),
            "chunk_id": r.get("chunk_id"),
            "doc_type": r.get("doc_type"),
        }
        for r in hits
    ]


@dataclass
class CsEmailWorkflowResult:
    """Outcome of one CS email workflow run."""

    customer_email: str
    search_query: str
    hits: list[dict]
    gen_hits: list[dict]
    matched_library: str
    matched_library_label: str
    routing_method: str
    library_scores: dict[str, float]
    keyword_hits: list[str]
    generated_answer: str | None = None
    llm_status: str = "skipped"
    llm_truncated: bool = False
    reply_incomplete: bool = False
    incomplete_reason: str | None = None
    style: StyleSelection | None = None
    context_zh_leak: bool = False
    reply_audit: dict[str, Any] | None = None
    trace: RunTrace = field(default_factory=RunTrace)
    top3_group_ids: list[str] = field(default_factory=list)

    def routing_meta(self) -> dict[str, Any]:
        return {
            "unified": True,
            "matched_library": self.matched_library,
            "matched_library_label": self.matched_library_label,
            "routing_method": self.routing_method,
            "library_scores": self.library_scores,
            "keyword_hits": self.keyword_hits,
        }

    def style_meta(self, *, repo_root: Any | None = None) -> dict[str, Any] | None:
        if not self.style:
            return None
        meta: dict[str, Any] = {
            "family_id": self.style.family_id,
            "match_reason": self.style.match_reason,
        }
        if repo_root is not None:
            try:
                meta["exemplar"] = str(self.style.exemplar_path.relative_to(repo_root))
            except ValueError:
                meta["exemplar"] = str(self.style.exemplar_path)
        return meta


def run_cs_email_workflow(
    customer_email: str,
    libraries: dict[str, UnifiedLibrary],
    *,
    search_query: str | None = None,
    domain_id: str = "topens",
    force_library: str | None = None,
    include_manual: bool = False,
    scenario_id: str | None = None,
    generate: bool = True,
    api_key: str | None = None,
    mail_type: str | None = None,
    style_enabled: bool = True,
    dedupe_hits: bool = True,
    hit_postprocess: Callable[[list[dict]], list[dict]] | None = None,
) -> CsEmailWorkflowResult:
    """
    Deterministic CS email pipeline:
    route → retrieve → enrich → context leak check → style → generate → audit → trace.
    """
    query = (search_query or customer_email).strip()
    email = customer_email.strip()
    domain = get_default_domain(domain_id)
    trace = RunTrace(domain_id=domain_id)
    trace.policy_version = domain.meta.id
    trace.style_pack_version = domain.style.version
    trace.prompt_pack_version = domain.prompts.version

    routing, hits_raw = unified_search(
        query,
        libraries,
        force_library=force_library,
        include_manual=include_manual,
    )
    lib = libraries[routing.matched_library]
    hits = hits_to_context(hits_raw, lib.chunk_by_id)
    if dedupe_hits:
        hits = dedupe_display_hits(hits)
    if hit_postprocess:
        hits = hit_postprocess(hits)

    gen_hits = enrich_hits_for_cs_email(_gen_hit_rows(hits), routing.matched_library)
    from domains.eval_pack import context_force_include_groups

    force_include = context_force_include_groups(scenario_id, domain_id=domain_id)
    blocks = build_context_for_hits(
        gen_hits,
        locale="en",
        response_mode="cs_email",
        force_include_groups=force_include,
    )
    zh_leak = detect_context_zh_leak(blocks)

    trace.product_id = routing.matched_library
    trace.routing_method = routing.routing_method
    trace.route_reason = (
        ",".join(routing.keyword_hits) if routing.keyword_hits else routing.routing_method
    )
    trace.index_paths = {"chroma": str(lib.config.chroma_dir)}
    trace.retrieved_hit_ids = [
        str(h.get("chunk_id") or "") for h in hits if h.get("chunk_id")
    ]
    trace.retrieved_group_ids = [
        str(h.get("group_id") or "") for h in hits if h.get("group_id")
    ]
    trace.context_language_leak = zh_leak

    effective_mail_type = mail_type or "troubleshoot"
    style_sel: StyleSelection | None = None
    generated: str | None = None
    truncated = False
    incomplete_reason: str | None = None
    llm_status = "skipped"
    reply_audit: dict[str, Any] | None = None

    key = api_key if api_key is not None else _get_config()[0]
    if generate:
        if not key:
            llm_status = "no_api_key"
        elif not gen_hits:
            llm_status = "failed"
        else:
            style_sel = select_style(
                email,
                gen_hits,
                scenario_id=scenario_id,
                enabled=style_enabled,
                domain_id=domain_id,
            )
            if style_sel:
                trace.style_family = style_sel.family_id
            generated, truncated, incomplete_reason = generate_answer(
                email,
                gen_hits,
                api_key=key,
                locale="en",
                response_mode="cs_email",
                scenario_id=scenario_id,
                style_enabled=style_enabled,
                mail_type=effective_mail_type,
            )
            llm_status = "ok" if generated else "failed"
            _, _, mdl = _get_config()
            trace.model_name = mdl

    if generate:
        reply_audit = audit_cs_email_reply(generated or "", mail_type=effective_mail_type)
        reply_audit["truncated"] = truncated
        if incomplete_reason:
            reply_audit["incomplete_reason"] = incomplete_reason
        trace.validation_result = reply_audit

    return CsEmailWorkflowResult(
        customer_email=email,
        search_query=query,
        hits=hits,
        gen_hits=gen_hits,
        matched_library=routing.matched_library,
        matched_library_label=routing.matched_library_label,
        routing_method=routing.routing_method,
        library_scores=routing.library_scores,
        keyword_hits=list(routing.keyword_hits),
        generated_answer=generated,
        llm_status=llm_status,
        llm_truncated=truncated,
        reply_incomplete=bool(incomplete_reason),
        incomplete_reason=incomplete_reason,
        style=style_sel,
        context_zh_leak=zh_leak,
        reply_audit=reply_audit,
        trace=trace,
        top3_group_ids=[h.group_id for h in hits_raw[:3]],
    )
