#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_server.py

RAG 演示服务：检索 + 可选生成式问答 + 静态 demo 页面。

用法:
  cd qa-doc-extractor
  $env:TRANSFORMERS_OFFLINE = "1"
  python qa_server.py --unified-cs --images-dir _scratch/run-006/images

English CS（推荐）：三库自动路由，单端口 Demo。
  python qa_server.py --unified-cs --demo-presentation cs-email --images-dir _scratch/run-006/images

单库联调（工程师）：
  python qa_server.py --chroma-dir _scratch/run-007/chroma_captioned --images-dir _scratch/run-006/images

浏览器打开 http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from retrieval_engine import RetrievalConfig

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR  # manual-kb 仓库根
DEFAULT_CHROMA = SCRIPT_DIR / "_scratch/run-007/chroma_captioned"
DEFAULT_IMAGES = SCRIPT_DIR / "_scratch/run-006/images"
MANUAL_IMAGE_DIRS = (
    SCRIPT_DIR / "_scratch/vlm_a3s_full/images",
    SCRIPT_DIR / "_scratch/vlm_ad5s_full/images",
)
DEFAULT_MODEL = SCRIPT_DIR / "_scratch/modelscope/BAAI/bge-m3"
DEMO_DIR = SCRIPT_DIR / "demo"

# 预加载检索模型（启动时一次）
_chunk_by_id: dict[str, dict[str, Any]] | None = None
_config: RetrievalConfig | None = None
_unified_libraries: dict | None = None
_unified_cs: bool = False
_merged_retrieval: bool = False
_allowed_libraries: list[str] | None = None
_domain_id: str = "topens"


def _load_dotenv() -> None:
    """加载 repo 根 .env 与脚本目录 .env（后者覆盖）。"""
    def _apply(path: Path, *, override: bool) -> None:
        if not path.is_file():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if not key:
                continue
            if override:
                os.environ[key] = val
            else:
                os.environ.setdefault(key, val)

    _apply(REPO_ROOT / ".env", override=False)
    _apply(SCRIPT_DIR / ".env", override=True)


def _llm_configured() -> bool:
    from generate_answer import _get_config

    return bool(_get_config()[0])


def _init_engine(chroma_dir: Path, model: str) -> None:
    global _chunk_by_id, _config
    from retrieval_engine import RetrievalConfig, load_manifest

    _chunk_by_id, _ = load_manifest(chroma_dir)
    _config = RetrievalConfig(chroma_dir=chroma_dir, model=model, k=3)


def _dedupe_display_hits(hits: list[dict]) -> list[dict]:
    from agents.cs_email_workflow import dedupe_display_hits

    return dedupe_display_hits(hits)


def _image_lookup_dirs(primary: Path) -> list[Path]:
    dirs: list[Path] = []
    if primary.is_dir():
        dirs.append(primary)
    for extra in MANUAL_IMAGE_DIRS:
        if extra.is_dir() and extra not in dirs:
            dirs.append(extra)
    return dirs


def _init_unified(
    model: str,
    *,
    k: int = 3,
    index: str = "zh",
    merged: bool = False,
    allowed_libraries: list[str] | None = None,
) -> None:
    global _unified_libraries
    from library_router import load_unified_libraries

    _unified_libraries = load_unified_libraries(
        model,
        k=k,
        index=index,
        merged=merged,
        allowed_libraries=allowed_libraries,
    )


def _ask(
    query: str,
    *,
    use_llm: bool = True,
    locale: str = "zh",
    response_mode: str = "qa",
    force_library: str | None = None,
    include_trace: bool = False,
) -> dict:
    from retrieval_engine import resolve_context, search
    from generate_answer import generate_answer
    from engine.trace import RunTrace, detect_context_zh_leak
    from domains.loader import get_default_domain

    if _unified_cs and _unified_libraries and response_mode == "cs_email":
        from agents.cs_email_workflow import run_cs_email_workflow

        include_manual = _merged_retrieval and (
            response_mode == "cs_email" or locale == "en"
        )
        wf = run_cs_email_workflow(
            query,
            _unified_libraries,
            domain_id=_domain_id,
            force_library=force_library,
            include_manual=include_manual,
            generate=use_llm,
            style_enabled=True,
            dedupe_hits=True,
        )
        from image_utils import localize_images

        display_locale = locale if locale in ("en", "zh") else "zh"
        hits = wf.hits
        for hit in hits:
            hit["images"] = localize_images(hit.get("images"), display_locale)

        payload = {
            "query": query,
            "locale": locale,
            "response_mode": response_mode,
            "generated_answer": wf.generated_answer,
            "llm_status": wf.llm_status if use_llm else "skipped",
            "llm_truncated": wf.llm_truncated,
            "reply_incomplete": wf.reply_incomplete,
            "incomplete_reason": wf.incomplete_reason,
            "llm_configured": _llm_configured(),
            "hits": hits,
            **wf.routing_meta(),
        }
        if include_trace:
            payload["trace"] = wf.trace.to_dict()
        return payload

    routing_meta: dict[str, Any] = {}
    trace = RunTrace(domain_id=_domain_id)

    if _unified_cs and _unified_libraries:
        from library_router import hits_to_context, unified_search

        include_manual = _merged_retrieval and (
            response_mode == "cs_email" or locale == "en"
        )
        routing, hits_raw = unified_search(
            query,
            _unified_libraries,
            force_library=force_library,
            include_manual=include_manual,
        )
        lib = _unified_libraries[routing.matched_library]
        hits = _dedupe_display_hits(hits_to_context(hits_raw, lib.chunk_by_id))
        routing_meta = {
            "unified": True,
            "matched_library": routing.matched_library,
            "matched_library_label": routing.matched_library_label,
            "routing_method": routing.routing_method,
            "library_scores": routing.library_scores,
            "keyword_hits": routing.keyword_hits,
        }
        trace.product_id = routing.matched_library
        trace.routing_method = routing.routing_method
        trace.route_reason = (
            ",".join(routing.keyword_hits) if routing.keyword_hits else routing.routing_method
        )
        trace.index_paths = {
            "chroma": str(lib.config.chroma_dir),
        }
    else:
        if _config is None or _chunk_by_id is None:
            raise RuntimeError("retrieval engine not initialized; call _init_engine first")

        hits_raw = search(_config, query)
        hits = []
        for hit in hits_raw:
            meta = {"chunk_id": hit.chunk_id, **hit.metadata}
            ctx = resolve_context(meta, _chunk_by_id)
            hits.append(
                {
                    "rank": hit.rank,
                    "score": hit.score,
                    "group_id": hit.group_id,
                    **ctx,
                }
            )
        trace.index_paths = {"chroma": str(_config.chroma_dir)}

    generated = None
    llm_truncated = False
    reply_incomplete = False
    incomplete_reason = None
    llm_status = "skipped"
    llm_configured = _llm_configured()
    gen_hits = hits
    if (
        locale == "en"
        and response_mode == "cs_email"
        and routing_meta.get("matched_library")
    ):
        from pilot_en_context import enrich_hits_for_cs_email

        gen_hits = enrich_hits_for_cs_email(hits, routing_meta["matched_library"])
    if use_llm:
        if not llm_configured:
            llm_status = "no_api_key"
        else:
            generated, llm_truncated, incomplete_reason = generate_answer(
                query,
                gen_hits,
                locale=locale,
                response_mode=response_mode,
            )
            reply_incomplete = bool(incomplete_reason)
            llm_status = "ok" if generated else "failed"
            from generate_answer import _get_config

            _, _, mdl = _get_config()
            trace.model_name = mdl
            if response_mode == "cs_email":
                try:
                    from style_exemplars import select_style

                    style = select_style(query, gen_hits)
                    if style is not None:
                        trace.style_family = style.family_id
                except Exception:
                    pass

    from image_utils import localize_images

    display_locale = locale if locale in ("en", "zh") else "zh"
    for hit in hits:
        hit["images"] = localize_images(hit.get("images"), display_locale)

    trace.retrieved_hit_ids = [
        str(h.get("chunk_id") or "") for h in hits if h.get("chunk_id")
    ]
    trace.retrieved_group_ids = [
        str(h.get("group_id") or "") for h in hits if h.get("group_id")
    ]
    if locale == "en" and response_mode == "cs_email":
        from context_builder import build_context_for_hits

        blocks = build_context_for_hits(
            gen_hits, locale=locale, response_mode=response_mode
        )
        trace.context_language_leak = detect_context_zh_leak(blocks)
    domain = get_default_domain(_domain_id)
    trace.policy_version = domain.meta.id
    trace.style_pack_version = domain.style.version
    trace.prompt_pack_version = domain.prompts.version

    payload = {
        "query": query,
        "locale": locale,
        "response_mode": response_mode,
        "generated_answer": generated,
        "llm_status": llm_status,
        "llm_truncated": llm_truncated,
        "reply_incomplete": reply_incomplete,
        "incomplete_reason": incomplete_reason,
        "llm_configured": llm_configured,
        "hits": hits,
        **routing_meta,
    }
    if include_trace:
        payload["trace"] = trace.to_dict()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="QA RAG demo server")
    parser.add_argument("--chroma-dir", type=Path, default=DEFAULT_CHROMA)
    parser.add_argument("--images-dir", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--model", default=str(DEFAULT_MODEL))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--demo-presentation",
        choices=("cs-email", "zh-troubleshooting"),
        default="cs-email",
        help="Default API presentation when client omits locale/mode (demo: cs-email)",
    )
    parser.add_argument(
        "--unified-cs",
        action="store_true",
        help="Load all product libraries; auto-route query (English CS demo)",
    )
    parser.add_argument(
        "--merged-retrieval",
        action="store_true",
        help="Use BL-RET-01a merged index: ts Top1 + manual supplement (Wave 3 · B 轴)",
    )
    parser.add_argument(
        "--allowed-libraries",
        default="",
        help="Comma-separated library ids (e.g. a3s,ad5s) to hide TC148 in demo",
    )
    parser.add_argument(
        "--domain",
        default="topens",
        help="Domain pack id under domains/ (default: topens)",
    )
    parser.add_argument(
        "--response-mode",
        default="",
        help="Override default response mode (e.g. cs_email); empty keeps demo-presentation default",
    )
    parser.add_argument(
        "--locale",
        default="",
        help="Override default locale (e.g. en); empty keeps demo-presentation default",
    )
    parser.add_argument(
        "--allowed-products",
        default="",
        help="Alias of --allowed-libraries (comma-separated product ids)",
    )
    args = parser.parse_args()
    global _unified_cs, _merged_retrieval, _allowed_libraries, _domain_id
    _domain_id = str(args.domain).strip() or "topens"
    from domains.loader import get_default_domain

    get_default_domain(_domain_id)  # fail fast on bad / incomplete domain pack
    _unified_cs = bool(args.unified_cs)
    _merged_retrieval = bool(args.merged_retrieval)
    allowed_raw = args.allowed_products.strip() or args.allowed_libraries.strip()
    _allowed_libraries = (
        [x.strip() for x in allowed_raw.split(",") if x.strip()]
        if allowed_raw
        else (["a3s", "ad5s"] if args.demo_presentation == "cs-email" else None)
    )
    if _unified_cs and not args.merged_retrieval and args.demo_presentation == "cs-email":
        _merged_retrieval = True
    demo_defaults = {
        "locale": args.locale.strip()
        or ("en" if args.demo_presentation == "cs-email" else "zh"),
        "response_mode": args.response_mode.strip()
        or ("cs_email" if args.demo_presentation == "cs-email" else "qa"),
        "use_llm": args.demo_presentation == "cs-email",
    }

    if not _unified_cs and not args.chroma_dir.is_dir():
        raise SystemExit(
            f"chroma dir not found: {args.chroma_dir}\n"
            "先运行: python embed_ingest_local.py _scratch/run-006/caption-run-v2/chunks_captioned.json "
            "_scratch/run-007/chroma_captioned --model _scratch/modelscope/BAAI/bge-m3"
        )
    if _unified_cs:
        from library_router import LIBRARY_SPECS, filter_library_specs, resolve_chroma_dir

        retrieval_index = "en" if args.demo_presentation == "cs-email" else "zh"
        specs = filter_library_specs(_allowed_libraries)
        missing: list[str] = []
        for spec in specs:
            if not resolve_chroma_dir(spec["id"], index=retrieval_index).is_dir():
                missing.append(spec["id"])
            if _merged_retrieval:
                from library_router import resolve_merged_chroma_dir

                if not resolve_merged_chroma_dir(spec["id"]).is_dir():
                    missing.append(f"{spec['id']}(merged)")
        if missing:
            raise SystemExit(
                f"--unified-cs: missing chroma ({retrieval_index}) for: {', '.join(missing)}"
            )

    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import FileResponse
        import uvicorn
    except ImportError:
        raise SystemExit("pip install fastapi uvicorn") from None

    _load_dotenv()
    if _llm_configured():
        from generate_answer import _get_config

        _, _, mdl = _get_config()
        print(f"LLM ready: {mdl}", file=sys.stderr)
    else:
        print("LLM: no QA_API_KEY / TRANSLATE_API_KEY (检索-only)", file=sys.stderr)

    print("loading embedding model...", file=sys.stderr)
    from retrieval_engine import _load_embed_model

    _load_embed_model(args.model)
    if _unified_cs:
        from library_router import filter_library_specs

        retrieval_index = "en" if args.demo_presentation == "cs-email" else "zh"
        lib_ids = [s["id"] for s in filter_library_specs(_allowed_libraries)]
        print(
            f"loading unified libraries ({retrieval_index}-index: {', '.join(lib_ids)})"
            f"{' · merged+manual' if _merged_retrieval else ''}...",
            file=sys.stderr,
        )
        _init_unified(
            args.model,
            k=3,
            index=retrieval_index,
            merged=_merged_retrieval,
            allowed_libraries=_allowed_libraries,
        )
        print("unified CS mode: auto library routing enabled.", file=sys.stderr)
    else:
        _init_engine(args.chroma_dir, args.model)
        warn_groups = sorted(
            {
                c.get("group_id")
                for c in _chunk_by_id.values()
                if c.get("structure_warnings")
            }
        )
        if warn_groups:
            print(
                f"structure_warnings: {len(warn_groups)} group(s) need review: "
                + ", ".join(warn_groups),
                file=sys.stderr,
            )
    print("ready.", file=sys.stderr)

    app = FastAPI(title="QA Troubleshooting Demo")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    image_dirs = _image_lookup_dirs(args.images_dir)

    @app.get("/images/{filename:path}")
    def serve_image(filename: str):
        from fastapi import HTTPException
        from image_utils import public_image_file

        name = public_image_file(filename)
        if not name or name != Path(name).name:
            raise HTTPException(404, "image not found")
        for directory in image_dirs:
            path = directory / name
            if path.is_file():
                return FileResponse(path)
        raise HTTPException(404, "image not found")

    @app.get("/")
    def index():
        index_path = DEMO_DIR / "index.html"
        if not index_path.is_file():
            raise HTTPException(404, "demo/index.html not found")
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.get("/api/health")
    def health():
        if _unified_cs and _unified_libraries:
            from library_router import filter_library_specs

            return {
                "status": "ok",
                "unified": True,
                "merged_retrieval": _merged_retrieval,
                "libraries": list(_unified_libraries.keys()),
            }
        return {"status": "ok", "chroma": str(args.chroma_dir), "unified": False}

    @app.get("/api/config")
    def config():
        from generate_answer import _get_config
        from library_router import PRODUCT_CATALOG_LINKS, filter_library_specs
        from domains.loader import get_default_domain

        _, _, model = _get_config()
        domain = get_default_domain(_domain_id)
        payload = {
            "llm_configured": _llm_configured(),
            "llm_model": model if _llm_configured() else None,
            "demo_presentation": args.demo_presentation,
            "domain_id": domain.meta.id,
            "domain_display_name": domain.meta.display_name,
            "brand": domain.meta.brand,
            "default_locale": demo_defaults["locale"],
            "default_response_mode": demo_defaults["response_mode"],
            "default_use_llm": demo_defaults["use_llm"],
            "available_modes": ["cs_email", "qa"],
            "unified": _unified_cs,
            "merged_retrieval": _merged_retrieval,
            "product_catalog_links": PRODUCT_CATALOG_LINKS,
            "catalog_links": PRODUCT_CATALOG_LINKS,
            "products": [
                {"id": p.id, "label": p.label, "aliases": list(p.aliases)}
                for p in domain.products
                if not _allowed_libraries or p.id in _allowed_libraries
            ],
        }
        if _unified_cs:
            payload["libraries"] = [
                {"id": s["id"], "label": s["label"]}
                for s in filter_library_specs(_allowed_libraries)
            ]
        return payload

    @app.post("/api/ask")
    async def ask(body: dict):
        query = (body.get("query") or "").strip()
        if not query:
            raise HTTPException(400, "query required")
        use_llm = body.get("use_llm", demo_defaults["use_llm"])
        locale = body.get("locale") or demo_defaults["locale"]
        response_mode = body.get("response_mode") or demo_defaults["response_mode"]
        force_library = body.get("library") or body.get("force_library") or body.get("product")
        include_trace = bool(body.get("include_trace") or body.get("trace"))
        return _ask(
            query,
            use_llm=bool(use_llm),
            locale=str(locale),
            response_mode=str(response_mode),
            force_library=str(force_library) if force_library else None,
            include_trace=include_trace,
        )

    @app.get("/api/ask")
    def ask_get(
        q: str = "",
        llm: int | None = None,
        locale: str | None = None,
        response_mode: str | None = None,
        library: str | None = None,
        include_trace: int = 0,
    ):
        if not q.strip():
            raise HTTPException(400, "q required")
        use_llm = demo_defaults["use_llm"] if llm is None else bool(llm)
        return _ask(
            q.strip(),
            use_llm=use_llm,
            locale=locale or demo_defaults["locale"],
            response_mode=response_mode or demo_defaults["response_mode"],
            force_library=library,
            include_trace=bool(include_trace),
        )

    print(f"demo: http://{args.host}:{args.port}/", file=sys.stderr)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
