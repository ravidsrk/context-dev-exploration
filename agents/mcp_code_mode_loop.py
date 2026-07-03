#!/usr/bin/env python3
"""
MCP Code Mode agent loop: hosted search_docs → LLM execute plan → run → observe.

Calls the real Context.dev MCP server at context-dev.stlmcp.com for search_docs.
Execute step runs composed SDK calls via Python client (canonical ops only).

Run:
  CONTEXT_DEV_API_KEY=... OPEN_ROUTER_KEY=... \\
    python agents/mcp_code_mode_loop.py "Get stripe.com brand, design tokens, and site scale"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_policy import plan_mcp_execute  # noqa: E402
from agents.mcp_client import extract_domain_from_goal, hosted_search_docs  # noqa: E402
from agents.mcp_op_map import OP_CREDITS, normalize_execute_plan  # noqa: E402
from src.context_client import (  # noqa: E402
    create_client,
    extract_styleguide,
    retrieve_brand,
    scrape_sitemap,
)

DOC_INDEX = Path(__file__).resolve().parent / "sdk_doc_index.json"


def search_docs_local_fallback(query: str, limit: int = 3) -> list[dict[str, str]]:
    """Offline fallback only when hosted MCP is unreachable."""
    entries = json.loads(DOC_INDEX.read_text())
    q = query.lower()
    scored: list[tuple[int, dict]] = []
    for entry in entries:
        score = sum(1 for kw in entry["keywords"] if kw in q)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda x: -x[0])
    hits = [e for _, e in scored[:limit]] or entries[:limit]
    return [
        {
            "id": h["id"],
            "signature": h["signature"],
            "returns": h["returns"],
            "credits": str(h["credits"]),
            "description": "",
        }
        for h in hits
    ]


def search_docs(query: str, limit: int = 5) -> tuple[list[dict[str, str]], str]:
    """Prefer hosted MCP search_docs; fall back to local index if MCP fails."""
    try:
        hits, source = hosted_search_docs(query, language="typescript")
        return hits[:limit], source
    except Exception as exc:
        local = search_docs_local_fallback(query, limit)
        return local, f"local_fallback:{type(exc).__name__}"


def _apply_brand(client, domain: str, out: dict[str, Any]) -> None:
    brand = retrieve_brand(client, domain)
    out["identity"] = {
        "title": brand.get("title"),
        "logo_url": brand.get("logo_url"),
    }


def _apply_styleguide(client, domain: str, out: dict[str, Any]) -> None:
    style = extract_styleguide(client, domain)
    out["design_tokens"] = {
        "color_count": style.get("color_count"),
        "has_typography": style.get("has_typography"),
    }


def _apply_sitemap(client, domain: str, out: dict[str, Any]) -> None:
    sm = scrape_sitemap(client, domain)
    out["site_scale"] = {
        "url_count": sm.get("url_count"),
        "sample_paths": sm.get("sample_urls"),
    }


# Table-driven dispatch: canonical op → handler
_CANONICAL_HANDLERS: dict[str, Callable[[Any, str, dict[str, Any]], None]] = {
    "brand.retrieve": _apply_brand,
    "web.extract_styleguide": _apply_styleguide,
    "web.scrape_sitemap": _apply_sitemap,
}


def execute_plan(plan: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str], int]:
    """Execute composed SDK operations — accepts only canonical ops."""
    client = create_client()
    ops_run: list[str] = []
    credits = 0
    out: dict[str, Any] = {}

    for step in plan:
        op = step.get("op", "")
        handler = _CANONICAL_HANDLERS.get(op)
        if not handler:
            continue
        args = step.get("args") or {}
        domain = args.get("domain", "")
        if not domain:
            continue
        handler(client, domain, out)
        credits += OP_CREDITS.get(op, 0)
        ops_run.append(f"{op}({domain})")

    out["credits_estimated"] = credits
    return out, ops_run, credits


def run_code_mode_loop(goal: str) -> dict[str, Any]:
    domain = extract_domain_from_goal(goal)
    doc_query = goal
    doc_hits, docs_source = search_docs(doc_query)
    raw_plan, policy_source = plan_mcp_execute(goal, doc_hits)
    plan_steps = normalize_execute_plan(goal, raw_plan, doc_hits, domain)
    result, ops_run, credits = execute_plan(plan_steps)

    return {
        "goal": goal,
        "search_docs": {
            "query": doc_query,
            "source": docs_source,
            "hits": doc_hits,
        },
        "execute_plan": plan_steps,
        "policy_source": policy_source,
        "result": result,
        "ops_run": ops_run,
        "credits_estimated": credits,
    }


def main() -> int:
    goal = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "Get stripe.com brand identity, design tokens, and site scale"
    )
    print(json.dumps(run_code_mode_loop(goal), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())