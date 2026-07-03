"""Canonical op mapping for MCP search_docs / LLM execute plan IDs."""

from __future__ import annotations

from typing import Any

# Exactly three executable perception ops in the code-mode demo loop.
CANONICAL_OPS = frozenset(
    {
        "brand.retrieve",
        "web.extract_styleguide",
        "web.scrape_sitemap",
    }
)

# Hosted MCP + LLM ids → canonical op. retrieveSimplified maps to brand.retrieve.
_OP_ALIASES: dict[str, str] = {
    "brand.retrieve": "brand.retrieve",
    "client.brand.retrieve": "brand.retrieve",
    "client.brand.retrievesimplified": "brand.retrieve",
    "client.brand.retrieveSimplified": "brand.retrieve",
    "client.brand.retrievebyname": "brand.retrieve",
    "client.brand.retrieveByName": "brand.retrieve",
    "client.brand.retrievebyemail": "brand.retrieve",
    "client.brand.retrieveByEmail": "brand.retrieve",
    "web.extract_styleguide": "web.extract_styleguide",
    "client.web.extract_styleguide": "web.extract_styleguide",
    "client.web.extractStyleguide": "web.extract_styleguide",
    "web.scrape_sitemap": "web.scrape_sitemap",
    "web.web_scrape_sitemap": "web.scrape_sitemap",
    "client.brand.webscrapesitemap": "web.scrape_sitemap",
    "client.brand.webScrapeSitemap": "web.scrape_sitemap",
    "client.web.webScrapeSitemap": "web.scrape_sitemap",
}

# Credit cost per canonical op (matches Context.dev pricing).
OP_CREDITS: dict[str, int] = {
    "brand.retrieve": 10,
    "web.extract_styleguide": 10,
    "web.scrape_sitemap": 1,
}


def canonicalize_op(op_id: str) -> str | None:
    """Map hosted/LLM op id to a canonical executable op, or None if unsupported."""
    if not op_id:
        return None
    stripped = op_id.strip()
    if stripped in CANONICAL_OPS:
        return stripped
    if stripped in _OP_ALIASES:
        return _OP_ALIASES[stripped]
    lowered = stripped.lower()
    if lowered in _OP_ALIASES:
        return _OP_ALIASES[lowered]
    return None


def normalize_execute_plan(
    goal: str,
    raw_plan: list[dict[str, Any]],
    hits: list[dict[str, str]],
    domain: str,
) -> list[dict[str, Any]]:
    """
    Always canonicalize ops — never pass raw LLM/hosted ids to execute_plan.
    Uses raw_plan steps first; falls back to search_docs hit ids when empty.
    """
    candidates: list[dict[str, Any]] = list(raw_plan) if raw_plan else []
    if not candidates and hits:
        candidates = [{"op": h.get("id", ""), "args": {}} for h in hits]

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for step in candidates:
        canonical = canonicalize_op(str(step.get("op", "")))
        if not canonical or canonical in seen:
            continue
        args = dict(step.get("args") or {})
        args.setdefault("domain", domain)
        normalized.append({"op": canonical, "args": args})
        seen.add(canonical)

    # Goal mentions site scale but plan omitted sitemap — add from hits/goal hint.
    if "web.scrape_sitemap" not in seen and (
        "scale" in goal.lower() or any("sitemap" in (h.get("id") or "").lower() for h in hits)
    ):
        normalized.append({"op": "web.scrape_sitemap", "args": {"domain": domain}})

    if not normalized:
        normalized = [
            {"op": "brand.retrieve", "args": {"domain": domain}},
            {"op": "web.extract_styleguide", "args": {"domain": domain}},
            {"op": "web.scrape_sitemap", "args": {"domain": domain}},
        ]

    return normalized