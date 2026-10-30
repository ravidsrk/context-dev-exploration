#!/usr/bin/env python3
"""Check that every SDK method this repo calls still exists.

Mocked unit tests use MagicMock/SimpleNamespace, so they keep passing after
an SDK method is removed. This check introspects the installed SDK instead.
It makes no network calls and needs no API key.
"""

from __future__ import annotations

import importlib.metadata
import sys

from context.dev import ContextDev

USED = [
    "brand.retrieve", "brand.search", "utility.prefetch",
    "industry.retrieve_naics", "industry.retrieve_sic",
    "web.scrape", "web.map_urls", "web.web_crawl_md", "web.screenshot",
    "web.extract_styleguide", "web.answers",
    "people.search", "news.search", "monitors.create", "monitors.delete", "batch.submit",
]
# Methods the July 2026 code used that were removed from the SDK.
REMOVED_JULY = [
    "web.web_scrape_md", "web.web_scrape_sitemap",
    "brand.identify_from_transaction", "web.extract_fonts",
]


def has(client: ContextDev, dotted: str) -> bool:
    obj = client
    for part in dotted.split("."):
        if not hasattr(obj, part):
            return False
        obj = getattr(obj, part)
    return True


def main() -> int:
    client = ContextDev(api_key="sdk-compat-no-network")
    print(f"context.dev {importlib.metadata.version('context.dev')}")
    missing = [m for m in USED if not has(client, m)]
    for m in USED:
        print(f"  {'OK     ' if m not in missing else 'MISSING'} {m}")
    for m in REMOVED_JULY:
        print(f"  {'gone   ' if not has(client, m) else 'back?  '} {m} (July 2026 call)")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
