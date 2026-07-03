#!/usr/bin/env python3
"""
Minimal agent loop: Research Scout (perceive → plan → act → observe).

Demonstrates credit-aware perception using Context.dev only.
Run: CONTEXT_DEV_API_KEY=... python agents/research_scout_loop.py stripe.com
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.context_client import (  # noqa: E402
    classify_naics,
    create_client,
    retrieve_brand,
    scrape_markdown,
    scrape_sitemap,
)


@dataclass
class ScoutMemory:
    domain: str
    brand: dict | None = None
    naics: dict | None = None
    pricing_snippet: str | None = None
    sitemap_count: int = 0
    credits_estimated: int = 0
    plan: list[str] = field(default_factory=list)
    brief: dict | None = None


def perceive_brand(memory: ScoutMemory, client) -> None:
    memory.brand = retrieve_brand(client, memory.domain)
    memory.credits_estimated += 10
    memory.plan.append("retrieve_brand")


def perceive_naics(memory: ScoutMemory, client) -> None:
    memory.naics = classify_naics(client, memory.domain)
    memory.credits_estimated += 10
    memory.plan.append("classify_naics")


def perceive_sitemap(memory: ScoutMemory, client) -> None:
    sm = scrape_sitemap(client, memory.domain)
    memory.sitemap_count = sm["url_count"]
    memory.credits_estimated += 1
    memory.plan.append("scrape_sitemap")


def perceive_pricing_page(memory: ScoutMemory, client) -> None:
    url = f"https://{memory.domain}/pricing"
    page = scrape_markdown(client, url)
    memory.credits_estimated += 1
    memory.plan.append(f"scrape_markdown:{url}")
    md = page.get("markdown") or ""
    memory.pricing_snippet = md[:500] if md else None


def plan_next_steps(memory: ScoutMemory) -> list[str]:
    """Simple policy: always brand+naics; sitemap if unknown size; pricing if link exists."""
    steps = ["brand", "naics", "sitemap"]
    if memory.brand and memory.brand.get("title"):
        steps.append("pricing_scrape")
    return steps


def act_write_brief(memory: ScoutMemory) -> dict:
    top_naics = (memory.naics or {}).get("codes", [])[:1]
    memory.brief = {
        "domain": memory.domain,
        "company": (memory.brand or {}).get("title"),
        "logo_url": (memory.brand or {}).get("logo_url"),
        "industry": top_naics[0] if top_naics else None,
        "sitemap_urls": memory.sitemap_count,
        "has_pricing_content": bool(memory.pricing_snippet),
        "pricing_preview": (memory.pricing_snippet or "")[:200] or None,
        "credits_estimated": memory.credits_estimated,
        "tools_called": memory.plan,
    }
    return memory.brief


def observe(memory: ScoutMemory) -> dict:
    """Observe step: confidence heuristics for downstream agents."""
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
    }


def run_loop(domain: str) -> dict:
    client = create_client()
    memory = ScoutMemory(domain=domain)

    # Perceive
    perceive_brand(memory, client)
    planned = plan_next_steps(memory)
    if "naics" in planned:
        perceive_naics(memory, client)
    if "sitemap" in planned:
        perceive_sitemap(memory, client)
    if "pricing_scrape" in planned:
        perceive_pricing_page(memory, client)

    # Act
    brief = act_write_brief(memory)

    # Observe
    observation = observe(memory)
    brief["observation"] = observation
    return brief


def main() -> int:
    domain = sys.argv[1] if len(sys.argv) > 1 else "stripe.com"
    result = run_loop(domain)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())