#!/usr/bin/env python3
"""
MCP Code Mode-style composed perception (single "execute" block).

Mirrors what the hosted MCP server does: one invocation chains brand +
styleguide + sitemap and returns a filtered payload (not raw API blobs).

Run: CONTEXT_DEV_API_KEY=... python agents/mcp_style_loop.py stripe.com
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.context_client import (  # noqa: E402
    create_client,
    extract_styleguide,
    retrieve_brand,
    scrape_sitemap,
)


def execute_composed(domain: str) -> dict:
    """Single composed tool call — analogous to MCP `execute` TypeScript."""
    client = create_client()

    brand = retrieve_brand(client, domain)
    style = extract_styleguide(client, domain)
    sitemap = scrape_sitemap(client, domain)

    # Filter to agent-consumable shape (MCP returns only what was asked)
    return {
        "domain": domain,
        "identity": {
            "title": brand.get("title"),
            "logo_url": brand.get("logo_url"),
        },
        "design_tokens": {
            "color_count": style.get("color_count"),
            "has_typography": style.get("has_typography"),
        },
        "site_scale": {
            "url_count": sitemap.get("url_count"),
            "sample_paths": sitemap.get("sample_urls"),
        },
        "credits_estimated": 10 + 10 + 1,
        "composition": ["brand.retrieve", "web.extract_styleguide", "web.sitemap"],
    }


def main() -> int:
    domain = sys.argv[1] if len(sys.argv) > 1 else "stripe.com"
    print(json.dumps(execute_composed(domain), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())