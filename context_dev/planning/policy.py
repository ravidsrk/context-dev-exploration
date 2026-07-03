"""OpenRouter LLM policy for agent plan steps (with deterministic fallback)."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from typing import Any


def _openrouter_chat(prompt: str, max_tokens: int = 200) -> str:
    api_key = os.environ.get("OPEN_ROUTER_KEY")
    if not api_key:
        raise RuntimeError("OPEN_ROUTER_KEY not set")

    payload = json.dumps(
        {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0,
        }
    ).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def _parse_json_array(text: str) -> list[str]:
    match = re.search(r"\[[\s\S]*?\]", text)
    if not match:
        return []
    try:
        parsed = json.loads(match.group())
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except json.JSONDecodeError:
        pass
    return []


ALLOWED_SCOUT_STEPS = ("naics", "sitemap", "pricing_scrape")


def plan_scout_perception(
    domain: str,
    brand: dict[str, Any],
    goal: str = "Build a sales intelligence dossier with industry, site scale, and pricing signals.",
) -> tuple[list[str], str]:
    """
    LLM policy step: decide which Context.dev perceive tools to call after brand retrieve.
    Returns (steps, policy_source).
    """
    title = brand.get("title") or domain
    prompt = f"""You are an agent planner with a credit budget.

Goal: {goal}
Domain: {domain}
Brand resolved: title={title!r}, logo={bool(brand.get('logo_url'))}

Available perceive tools (pick subset, ordered):
- "naics" — industry classification (10 credits)
- "sitemap" — URL count / site scale (1 credit)
- "pricing_scrape" — scrape /pricing markdown (1 credit)

Reply with ONLY a JSON array of tool names to call, e.g. ["naics","sitemap","pricing_scrape"].
Skip tools that don't help the goal. Always include naics for sales dossiers."""

    try:
        raw = _openrouter_chat(prompt)
        steps = [s for s in _parse_json_array(raw) if s in ALLOWED_SCOUT_STEPS]
        if steps:
            return steps, "llm"
    except Exception:
        pass

    # Deterministic fallback when LLM unavailable
    fallback = ["naics", "sitemap"]
    if brand.get("title"):
        fallback.append("pricing_scrape")
    return fallback, "fallback"


def plan_mcp_execute(
    goal: str,
    doc_hits: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], str]:
    """
    LLM writes an execute plan (list of SDK operations) from search_docs hits.
    """
    docs_text = json.dumps(doc_hits, indent=2)
    prompt = f"""You simulate Context.dev MCP Code Mode `execute`.

User goal: {goal}

SDK docs from search_docs:
{docs_text}

Write a JSON array of operations to run. Each item: {{"op": "<name>", "args": {{...}}}}.
Allowed ops: brand.retrieve, web.extract_styleguide, web.scrape_sitemap
Example: [{{"op":"brand.retrieve","args":{{"domain":"stripe.com"}}}},{{"op":"web.extract_styleguide","args":{{"domain":"stripe.com"}}}}]

Reply ONLY with the JSON array."""

    try:
        raw = _openrouter_chat(prompt, max_tokens=300)
        match = re.search(r"\[[\s\S]*\]", raw)
        if match:
            plan = json.loads(match.group())
            if isinstance(plan, list) and plan:
                return plan, "llm"
    except Exception:
        pass

    domain_match = re.search(r"[\w.-]+\.[a-z]{2,}", goal.lower())
    domain = domain_match.group() if domain_match else "stripe.com"
    return [
        {"op": "brand.retrieve", "args": {"domain": domain}},
        {"op": "web.extract_styleguide", "args": {"domain": domain}},
        {"op": "web.scrape_sitemap", "args": {"domain": domain}},
    ], "fallback"