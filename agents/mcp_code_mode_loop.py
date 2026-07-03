#!/usr/bin/env python3
"""
MCP Code Mode agent loop: search_docs → LLM execute plan → run → observe.

Mirrors hosted MCP at context-dev.stlmcp.com (search_docs + execute tools).

Run:
  CONTEXT_DEV_API_KEY=... OPEN_ROUTER_KEY=... \\
    python agents/mcp_code_mode_loop.py "Get stripe.com brand, design tokens, and site scale"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_policy import plan_mcp_execute  # noqa: E402
from src.context_client import (  # noqa: E402
    create_client,
    extract_styleguide,
    retrieve_brand,
    scrape_sitemap,
)

DOC_INDEX = Path(__file__).resolve().parent / "sdk_doc_index.json"


def search_docs(query: str, limit: int = 3) -> list[dict[str, str]]:
    """MCP search_docs analogue — keyword search over local SDK index."""
    entries = json.loads(DOC_INDEX.read_text())
    q = query.lower()
    scored: list[tuple[int, dict]] = []
    for entry in entries:
        score = sum(1 for kw in entry["keywords"] if kw in q)
        if score:
            scored.append((score, entry))
    scored.sort(key=lambda x: -x[0])
    hits = [e for _, e in scored[:limit]]
    if not hits:
        hits = entries[:limit]
    return [
        {
            "id": h["id"],
            "signature": h["signature"],
            "returns": h["returns"],
            "credits": str(h["credits"]),
        }
        for h in hits
    ]


def execute_plan(plan: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str], int]:
    """MCP execute analogue — run composed SDK operations, return filtered JSON."""
    client = create_client()
    ops_run: list[str] = []
    credits = 0
    out: dict[str, Any] = {}

    for step in plan:
        op = step.get("op", "")
        args = step.get("args") or {}
        domain = args.get("domain", "")

        if op == "brand.retrieve":
            brand = retrieve_brand(client, domain)
            out["identity"] = {
                "title": brand.get("title"),
                "logo_url": brand.get("logo_url"),
            }
            credits += 10
            ops_run.append(f"brand.retrieve({domain})")
        elif op == "web.extract_styleguide":
            style = extract_styleguide(client, domain)
            out["design_tokens"] = {
                "color_count": style.get("color_count"),
                "has_typography": style.get("has_typography"),
            }
            credits += 10
            ops_run.append(f"web.extract_styleguide({domain})")
        elif op in ("web.scrape_sitemap", "web.web_scrape_sitemap"):
            sm = scrape_sitemap(client, domain)
            out["site_scale"] = {
                "url_count": sm.get("url_count"),
                "sample_paths": sm.get("sample_urls"),
            }
            credits += 1
            ops_run.append(f"web.scrape_sitemap({domain})")

    out["credits_estimated"] = credits
    return out, ops_run, credits


def run_code_mode_loop(goal: str) -> dict[str, Any]:
    doc_query = goal if "brand" in goal.lower() else f"brand styleguide sitemap {goal}"
    doc_hits = search_docs(doc_query)
    execute_plan_steps, policy_source = plan_mcp_execute(goal, doc_hits)
    result, ops_run, credits = execute_plan(plan_steps := execute_plan_steps)

    return {
        "goal": goal,
        "search_docs": {"query": doc_query, "hits": doc_hits},
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