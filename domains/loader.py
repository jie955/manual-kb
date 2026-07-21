#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Load and validate domain YAML packs."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from domains.models import (
    CatalogLink,
    ContextPolicy,
    DomainConfig,
    DomainMeta,
    IndexBinding,
    KeywordPattern,
    ProductSpec,
    PromptPack,
    ResponsePolicy,
    RoutingPolicy,
    SpecialRouteRule,
    StyleFamilySpec,
    StylePack,
)

DOMAINS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = DOMAINS_ROOT.parent
DEFAULT_DOMAIN_ID = "topens"


class DomainConfigError(ValueError):
    """Raised when domain pack fails schema / referential checks."""


def _read_yaml(path: Path) -> Any:
    if not path.is_file():
        raise DomainConfigError(f"missing domain config: {path}")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if data is None:
        raise DomainConfigError(f"empty domain config: {path}")
    return data


def _require_keys(data: dict[str, Any], keys: list[str], *, where: str) -> None:
    missing = [k for k in keys if k not in data]
    if missing:
        raise DomainConfigError(f"{where}: missing keys {missing}")


def _parse_domain_meta(data: dict[str, Any]) -> DomainMeta:
    _require_keys(
        data,
        ["id", "display_name", "default_locale", "default_response_mode"],
        where="domain.yaml",
    )
    return DomainMeta(
        id=str(data["id"]),
        display_name=str(data["display_name"]),
        default_locale=str(data["default_locale"]),
        default_response_mode=str(data["default_response_mode"]),
        brand=str(data.get("brand") or data["display_name"]),
    )


def _parse_products(data: dict[str, Any]) -> tuple[tuple[ProductSpec, ...], tuple[CatalogLink, ...]]:
    _require_keys(data, ["products"], where="products.yaml")
    products: list[ProductSpec] = []
    for i, row in enumerate(data["products"] or []):
        _require_keys(row, ["id", "label", "doc_title"], where=f"products[{i}]")
        products.append(
            ProductSpec(
                id=str(row["id"]),
                label=str(row["label"]),
                doc_title=str(row["doc_title"]),
                aliases=tuple(str(a) for a in (row.get("aliases") or [])),
                display_order=int(row.get("display_order", i)),
            )
        )
    if not products:
        raise DomainConfigError("products.yaml: at least one product required")

    links: list[CatalogLink] = []
    for i, row in enumerate(data.get("catalog_links") or []):
        _require_keys(row, ["family", "label", "url"], where=f"catalog_links[{i}]")
        links.append(
            CatalogLink(
                family=str(row["family"]),
                label=str(row["label"]),
                url=str(row["url"]),
                kind=str(row.get("kind") or "catalog"),
            )
        )
    return tuple(products), tuple(links)


def _parse_indices(data: dict[str, Any], product_ids: set[str]) -> dict[str, IndexBinding]:
    _require_keys(data, ["indices"], where="indices.yaml")
    out: dict[str, IndexBinding] = {}
    for i, row in enumerate(data["indices"] or []):
        _require_keys(
            row,
            ["product_id", "chroma_zh", "chroma_en", "chroma_merged"],
            where=f"indices[{i}]",
        )
        pid = str(row["product_id"])
        if pid not in product_ids:
            raise DomainConfigError(f"indices.yaml: unknown product_id {pid!r}")
        out[pid] = IndexBinding(
            product_id=pid,
            chroma_zh=str(row["chroma_zh"]),
            chroma_en=str(row["chroma_en"]),
            chroma_merged=str(row["chroma_merged"]),
        )
    missing = product_ids - set(out)
    if missing:
        raise DomainConfigError(f"indices.yaml: missing bindings for {sorted(missing)}")
    return out


def _as_pattern(value: Any) -> str:
    """Join list fragments with no separator (preserves regex adjacency)."""
    if isinstance(value, list):
        return "".join(str(x) for x in value)
    return str(value)


def _parse_routing(data: dict[str, Any], product_ids: set[str]) -> RoutingPolicy:
    keywords: list[KeywordPattern] = []
    for i, row in enumerate(data.get("keyword_patterns") or []):
        _require_keys(row, ["product_id", "pattern"], where=f"keyword_patterns[{i}]")
        pid = str(row["product_id"])
        if pid not in product_ids:
            raise DomainConfigError(f"routing.yaml keyword_patterns[{i}]: unknown product {pid!r}")
        keywords.append(KeywordPattern(product_id=pid, pattern=_as_pattern(row["pattern"])))

    specials: list[SpecialRouteRule] = []
    for i, row in enumerate(data.get("special_rules") or []):
        _require_keys(row, ["product_id", "pattern"], where=f"special_rules[{i}]")
        pid = str(row["product_id"])
        if pid not in product_ids:
            raise DomainConfigError(f"routing.yaml special_rules[{i}]: unknown product {pid!r}")
        specials.append(
            SpecialRouteRule(
                product_id=pid,
                pattern=_as_pattern(row["pattern"]),
                exclude_patterns=tuple(_as_pattern(x) for x in (row.get("exclude_patterns") or [])),
                require_patterns=tuple(_as_pattern(x) for x in (row.get("require_patterns") or [])),
                reason=str(row.get("reason") or ""),
            )
        )
    return RoutingPolicy(
        keyword_patterns=tuple(keywords),
        special_rules=tuple(specials),
        fallback=str(data.get("fallback") or "fan_out"),
    )


def _parse_policies(data: dict[str, Any], product_ids: set[str]) -> ResponsePolicy:
    ctx_raw = data.get("context") or {}
    excludes_raw = ctx_raw.get("cs_email_top1_excludes") or {}
    top1_excludes: dict[str, frozenset[str]] = {}
    for gid, others in excludes_raw.items():
        top1_excludes[str(gid)] = frozenset(str(x) for x in (others or []))

    context = ContextPolicy(
        cs_email_en_max_chars=int(ctx_raw.get("cs_email_en_max_chars", 3200)),
        score_margin_top1_only=float(ctx_raw.get("score_margin_top1_only", 0.012)),
        top1_excludes=top1_excludes,
        forbid_content_zh_in_en=bool(ctx_raw.get("forbid_content_zh_in_en", True)),
    )
    # product_ids reserved for future policy refs (allowed products, etc.)
    _ = product_ids
    return ResponsePolicy(
        default_locale=str(data.get("default_locale") or "en"),
        default_response_mode=str(data.get("default_response_mode") or "cs_email"),
        context=context,
    )


def _validate_catalog_links(links: tuple[CatalogLink, ...], product_ids: set[str]) -> None:
    for link in links:
        if link.family != "all" and link.family not in product_ids:
            raise DomainConfigError(
                f"catalog link family {link.family!r} is not a known product id"
            )


def _resolve_repo_path(relpath: str) -> Path:
    return REPO_ROOT / relpath


def _read_text_file(path: Path, *, where: str) -> str:
    if not path.is_file():
        raise DomainConfigError(f"{where}: missing file {path}")
    return path.read_text(encoding="utf-8")


def _parse_style_pack(root: Path, hold_out_from_evals: frozenset[str] | None = None) -> StylePack:
    styles_root = root / "styles"
    manifest = _read_yaml(styles_root / "styles.yaml")
    version = str(manifest.get("version") or "1")
    router_rel = str(manifest.get("family_router") or "family_router.json")
    principles_rel = str(manifest.get("principles") or "principles_en.md")
    router_path = styles_root / router_rel
    principles_path = styles_root / principles_rel
    if not router_path.is_file():
        raise DomainConfigError(f"styles: missing family router {router_path}")

    import json

    router_data = json.loads(router_path.read_text(encoding="utf-8"))
    default_family = str(router_data.get("default_family") or "")
    if not default_family:
        raise DomainConfigError("styles: default_family required in family_router")

    group_hints = {str(k): str(v) for k, v in (router_data.get("group_hints") or {}).items()}
    scenario_overrides = {
        str(k): str(v) for k, v in (router_data.get("scenario_overrides") or {}).items()
    }
    families_raw = router_data.get("families") or {}
    if not families_raw:
        raise DomainConfigError("styles: at least one style family required")

    families: dict[str, StyleFamilySpec] = {}
    for fam_id, spec in families_raw.items():
        exemplar_rel = str(spec.get("exemplar") or "")
        if not exemplar_rel:
            raise DomainConfigError(f"styles: family {fam_id!r} missing exemplar path")
        exemplar_path = styles_root / exemplar_rel
        if not exemplar_path.is_file():
            raise DomainConfigError(f"styles: exemplar not found for {fam_id!r}: {exemplar_path}")
        families[str(fam_id)] = StyleFamilySpec(
            family_id=str(fam_id),
            exemplar_relpath=exemplar_rel,
            keywords=tuple(str(k) for k in (spec.get("keywords") or [])),
            email_sources=tuple(str(x) for x in (spec.get("email_sources") or [])),
        )

    if default_family not in families:
        raise DomainConfigError(f"styles: default_family {default_family!r} not in families")

    hold_out_raw = router_data.get("hold_out_gate") or []
    hold_out = frozenset(str(x) for x in hold_out_raw)
    if hold_out_from_evals and hold_out != hold_out_from_evals:
        raise DomainConfigError(
            f"styles hold_out_gate {sorted(hold_out)} != evals style_holdout {sorted(hold_out_from_evals)}"
        )

    for cs_id in hold_out:
        for fam in families.values():
            if cs_id in fam.email_sources and fam.exemplar_relpath.endswith(f"{cs_id}.md"):
                raise DomainConfigError(
                    f"styles: hold-out {cs_id} wired as runtime exemplar file for {fam.family_id}"
                )

    scenario_rel = str(
        manifest.get("scenario_map_relpath") or "_scratch/eval/cs_email_query_map.json"
    )
    scenario_map_path = _resolve_repo_path(scenario_rel)
    if not scenario_map_path.is_file():
        raise DomainConfigError(f"styles: scenario map not found: {scenario_map_path}")

    presales_types = frozenset(
        str(x) for x in (manifest.get("presales_types") or ["presales"])
    )

    return StylePack(
        root=styles_root,
        version=version,
        default_family=default_family,
        group_hints=group_hints,
        families=families,
        principles_path=principles_path,
        hold_out_gate=hold_out,
        scenario_map_path=scenario_map_path,
        presales_types=presales_types,
        warranty_scenario_substring=str(manifest.get("warranty_scenario_substring") or "0025"),
        scenario_overrides=scenario_overrides,
    )


def _parse_prompt_pack(root: Path) -> PromptPack:
    prompts_root = root / "prompts"
    manifest = _read_yaml(prompts_root / "prompts.yaml")
    version = str(manifest.get("version") or "1")

    def _load_key(key: str, default_name: str) -> str:
        rel = str(manifest.get(key) or default_name)
        return _read_text_file(prompts_root / rel, where=f"prompts.{key}").strip()

    return PromptPack(
        root=prompts_root,
        version=version,
        cs_email_system_en=_load_key("cs_email_system_en", "cs_email_system_en.md"),
        qa_system_en=_load_key("qa_system_en", "qa_system_en.md"),
        qa_system_zh=_load_key("qa_system_zh", "qa_system_zh.md"),
    )


def _eval_style_holdout(root: Path) -> frozenset[str] | None:
    eval_gates = root / "evals" / "gates.yaml"
    if not eval_gates.is_file():
        return None
    data = _read_yaml(eval_gates)
    hold = data.get("style_holdout")
    if not hold:
        return None
    return frozenset(str(x) for x in hold)


def load_domain(domain_id: str = DEFAULT_DOMAIN_ID, *, domains_root: Path | None = None) -> DomainConfig:
    """Load domain pack from domains/<id>/ and validate referential integrity."""
    root = (domains_root or DOMAINS_ROOT) / domain_id
    if not root.is_dir():
        raise DomainConfigError(f"domain pack not found: {root}")

    meta = _parse_domain_meta(_read_yaml(root / "domain.yaml"))
    if meta.id != domain_id:
        raise DomainConfigError(
            f"domain.yaml id {meta.id!r} does not match directory {domain_id!r}"
        )

    products, catalog_links = _parse_products(_read_yaml(root / "products.yaml"))
    product_ids = {p.id for p in products}
    _validate_catalog_links(catalog_links, product_ids)

    indices = _parse_indices(_read_yaml(root / "indices.yaml"), product_ids)
    routing = _parse_routing(_read_yaml(root / "routing.yaml"), product_ids)
    response = _parse_policies(_read_yaml(root / "policies.yaml"), product_ids)
    style = _parse_style_pack(root, hold_out_from_evals=_eval_style_holdout(root))
    prompts = _parse_prompt_pack(root)

    return DomainConfig(
        meta=meta,
        products=products,
        catalog_links=catalog_links,
        indices=indices,
        routing=routing,
        response=response,
        style=style,
        prompts=prompts,
        root=root,
        raw={},
    )


@lru_cache(maxsize=8)
def get_default_domain(domain_id: str = DEFAULT_DOMAIN_ID) -> DomainConfig:
    return load_domain(domain_id)


def clear_domain_cache() -> None:
    get_default_domain.cache_clear()
