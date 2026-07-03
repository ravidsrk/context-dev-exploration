#!/usr/bin/env python3
"""Synthesize Context.dev + Monid pairing notes via OpenRouter (low-cost inference)."""

from __future__ import annotations

import json
import os
import sys
import urllib.request

PROMPT = """Summarize how Monid (LinkedIn posts, social search, competitor pricing via discover/inspect/run CLI)
complements Context.dev (brand logos, web scrape/crawl, transaction enrichment, NAICS/SIC classification)
for building sales intelligence and competitive monitoring products.
Be specific about which platform handles which data layer. ~200 words."""


def main() -> int:
    api_key = os.environ.get("OPEN_ROUTER_KEY")
    if not api_key:
        print("OPEN_ROUTER_KEY not set; skipping synthesis", file=sys.stderr)
        return 1

    payload = json.dumps(
        {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": PROMPT}],
            "max_tokens": 300,
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

    content = data["choices"][0]["message"]["content"]
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())