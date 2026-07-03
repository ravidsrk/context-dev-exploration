#!/usr/bin/env python3
"""
MCP Code Mode agent loop: hosted search_docs → plan → hosted execute (TS sandbox).

1. search_docs — real MCP tool at context-dev.stlmcp.com
2. plan — OpenRouter LLM maps hits to ops (canonicalized via mcp_op_map)
3. execute — hosted MCP execute runs TypeScript in Stainless sandbox
4. observe — structured JSON result; local Python SDK only as fallback

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
from agents.mcp_client import (  # noqa: E402
    extract_domain_from_goal,
    hosted_execute,
    hosted_search_docs,
)
from agents.mcp_execute_codegen import build_execute_typescript  # noqa: E402
from agents.mcp_op_map import OP_CREDITS, normalize_execute_plan  # noqa: E402

DOC_INDEX = Path(__file__).resolve().parent / "sdk_doc_index.json"


def search_docs_local_fallback(query: str, limit: int = 3) -> list[dict[str, str]]:
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
    try:
        hits, source = hosted_search_docs(query, language="typescript")
        return hits[:limit], source
    except Exception as exc:
        return search_docs_local_fallback(query, limit), f"local_fallback:{type(exc).__name__}"


def execute_plan_local(plan: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str], int]:
    """Fallback: Python SDK when hosted execute fails."""
    from src.context_client import (  # lazy: hosted path needs no SDK install
        create_client,
        extract_styleguide,
        retrieve_brand,
        scrape_sitemap,
    )

    client = create_client()
    ops_run: list[str] = []
    credits = 0
    out: dict[str, Any] = {}

    for step in plan:
        op = step.get("op", "")
        domain = (step.get("args") or {}).get("domain", "")
        if not domain:
            continue
        if op == "brand.retrieve":
            brand = retrieve_brand(client, domain)
            out["identity"] = {"title": brand.get("title"), "logo_url": brand.get("logo_url")}
            credits += OP_CREDITS.get(op, 0)
            ops_run.append(f"local:{op}({domain})")
        elif op == "web.extract_styleguide":
            style = extract_styleguide(client, domain)
            out["design_tokens"] = {
                "color_count": style.get("color_count"),
                "has_typography": style.get("has_typography"),
            }
            credits += OP_CREDITS.get(op, 0)
            ops_run.append(f"local:{op}({domain})")
        elif op == "web.scrape_sitemap":
            sm = scrape_sitemap(client, domain)
            out["site_scale"] = {"url_count": sm.get("url_count"), "sample_paths": sm.get("sample_urls")}
            credits += OP_CREDITS.get(op, 0)
            ops_run.append(f"local:{op}({domain})")

    out["credits_estimated"] = credits
    return out, ops_run, credits


def execute_plan_hosted(
    goal: str, domain: str, plan: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[str], str, str]:
    """
    Hosted MCP execute: TypeScript sandbox composes SDK calls in one invocation.
    Returns (result, ops_run, execute_source, typescript_code).
    """
    code = build_execute_typescript(domain, plan)
    raw = hosted_execute(code, intent=goal)
    if "raw" in raw and "error" in str(raw.get("raw", "")).lower():
        raise RuntimeError(raw["raw"])

    payload = raw.get("result") if isinstance(raw.get("result"), dict) else raw
    if not payload or not payload.get("identity"):
        raise RuntimeError(f"hosted execute empty result: {raw}")

    ops = [step.get("op", "") for step in plan]
    ops_run = [f"hosted:execute({op})" for op in ops if op]
    return payload, ops_run, "hosted_mcp_execute", code


def run_code_mode_loop(goal: str) -> dict[str, Any]:
    domain = extract_domain_from_goal(goal)
    doc_hits, docs_source = search_docs(goal)
    raw_plan, policy_source = plan_mcp_execute(goal, doc_hits)
    plan_steps = normalize_execute_plan(goal, raw_plan, doc_hits, domain)

    execute_source = "hosted_mcp_execute"
    typescript_code = ""
    credits = 0
    try:
        result, ops_run, execute_source, typescript_code = execute_plan_hosted(
            goal, domain, plan_steps
        )
        credits = sum(OP_CREDITS.get(s["op"], 0) for s in plan_steps)
        result["credits_estimated"] = credits
    except Exception as exc:
        result, ops_run, credits = execute_plan_local(plan_steps)
        execute_source = f"local_sdk_fallback:{type(exc).__name__}"

    return {
        "goal": goal,
        "search_docs": {"query": goal, "source": docs_source, "hits": doc_hits},
        "execute_plan": plan_steps,
        "policy_source": policy_source,
        "execute_source": execute_source,
        "execute_typescript": typescript_code or None,
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