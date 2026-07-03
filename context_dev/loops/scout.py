#!/usr/bin/env python3
"""
Research Scout agent loop: perceive → plan (LLM) → act → observe.

1. Perceive: brand.retrieve (always)
2. Plan: OpenRouter LLM picks next perceive tools under credit budget
3. Act: run planned Context.dev calls, write brief
4. Observe: confidence + revisit interval

Run:
  CONTEXT_DEV_API_KEY=... OPEN_ROUTER_KEY=... python -m context_dev.loops.scout stripe.com
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field

from context_dev.client import (
    classify_naics,
    create_client,
    retrieve_brand,
    scrape_markdown,
    scrape_sitemap,
)
from context_dev.planning.cli import cmd_scout


@dataclass
class ScoutMemory:
    domain: str
    goal: str = "Build a sales intelligence dossier with industry, site scale, and pricing signals."
    brand: dict | None = None
    naics: dict | None = None
    pricing_snippet: str | None = None
    sitemap_count: int = 0
    credits_estimated: int = 0
    perceive_log: list[str] = field(default_factory=list)
    plan_steps: list[str] = field(default_factory=list)
    policy_source: str = ""
    brief: dict | None = None


PERCEIVE_HANDLERS = {
    "naics": "classify_naics",
    "sitemap": "scrape_sitemap",
    "pricing_scrape": "scrape_pricing",
}


def perceive_brand(memory: ScoutMemory, client) -> None:
    memory.brand = retrieve_brand(client, memory.domain)
    memory.credits_estimated += 10
    memory.perceive_log.append("retrieve_brand")


def perceive_naics(memory: ScoutMemory, client) -> None:
    memory.naics = classify_naics(client, memory.domain)
    memory.credits_estimated += 10
    memory.perceive_log.append("classify_naics")


def perceive_sitemap(memory: ScoutMemory, client) -> None:
    sm = scrape_sitemap(client, memory.domain)
    memory.sitemap_count = sm["url_count"]
    memory.credits_estimated += 1
    memory.perceive_log.append("scrape_sitemap")


def perceive_pricing_page(memory: ScoutMemory, client) -> None:
    url = f"https://{memory.domain}/pricing"
    page = scrape_markdown(client, url)
    memory.credits_estimated += 1
    memory.perceive_log.append(f"scrape_markdown:{url}")
    md = page.get("markdown") or ""
    memory.pricing_snippet = md[:500] if md else None


def execute_plan(memory: ScoutMemory, client, steps: list[str]) -> None:
    handlers = {
        "naics": lambda: perceive_naics(memory, client),
        "sitemap": lambda: perceive_sitemap(memory, client),
        "pricing_scrape": lambda: perceive_pricing_page(memory, client),
    }
    for step in steps:
        fn = handlers.get(step)
        if fn:
            fn()


def act_write_brief(memory: ScoutMemory) -> dict:
    top_naics = (memory.naics or {}).get("codes", [])[:1]
    memory.brief = {
        "domain": memory.domain,
        "goal": memory.goal,
        "company": (memory.brand or {}).get("title"),
        "logo_url": (memory.brand or {}).get("logo_url"),
        "industry": top_naics[0] if top_naics else None,
        "sitemap_urls": memory.sitemap_count,
        "has_pricing_content": bool(memory.pricing_snippet),
        "pricing_preview": (memory.pricing_snippet or "")[:200] or None,
        "credits_estimated": memory.credits_estimated,
        "policy_source": memory.policy_source,
        "plan_steps": memory.plan_steps,
        "perceive_log": memory.perceive_log,
    }
    return memory.brief


def observe(memory: ScoutMemory) -> dict:
    confidence = 0.5
    if memory.brand and memory.brand.get("title"):
        confidence += 0.2
    if memory.naics and memory.naics.get("codes"):
        confidence += 0.15
    if memory.sitemap_count > 100:
        confidence += 0.1
    if memory.pricing_snippet:
        confidence += 0.05
    return {
        "confidence": round(min(confidence, 1.0), 2),
        "recommend_revisit_days": 7 if memory.sitemap_count > 1000 else 30,
        "policy_source": memory.policy_source,
    }


def run_loop(domain: str, goal: str | None = None) -> dict:
    client = create_client()
    memory = ScoutMemory(domain=domain)
    if goal:
        memory.goal = goal

    # Perceive (bootstrap)
    perceive_brand(memory, client)

    # Plan (shared plan_cli — same JSON TS loops consume)
    brand_for_plan = {
        "title": (memory.brand or {}).get("title"),
        "logo_url": (memory.brand or {}).get("logo_url"),
    }
    plan = cmd_scout(memory.domain, json.dumps(brand_for_plan), memory.goal)
    memory.plan_steps = plan["plan_steps"]
    memory.policy_source = plan["policy_source"]

    # Act (execute planned perception)
    execute_plan(memory, client, memory.plan_steps)
    brief = act_write_brief(memory)

    # Observe
    brief["observation"] = observe(memory)
    return brief


def main() -> int:
    domain = sys.argv[1] if len(sys.argv) > 1 else "stripe.com"
    goal = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(run_loop(domain, goal), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())