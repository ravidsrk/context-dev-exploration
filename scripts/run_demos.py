#!/usr/bin/env python3
"""Run live Context.dev API demonstrations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.context_client import (
    classify_naics,
    create_client,
    identify_transaction,
    retrieve_brand,
    scrape_markdown,
)


def main() -> int:
    client = create_client()
    results: dict = {}

    print("=== Brand Retrieve Demo ===")
    brand = retrieve_brand(client, "stripe.com")
    results["brand"] = brand
    print(f"  title: {brand['title']}")
    print(f"  domain: {brand['domain']}")
    print(f"  logo_url: {brand['logo_url']}")

    print("\n=== Web Scrape Markdown Demo ===")
    scrape = scrape_markdown(client, "https://stripe.com")
    results["scrape"] = {
        "url": scrape["url"],
        "markdown_length": scrape["markdown_length"],
        "markdown_preview": (scrape["markdown"] or "")[:200],
    }
    print(f"  url: {scrape['url']}")
    print(f"  markdown_length: {scrape['markdown_length']}")

    print("\n=== Transaction Enrichment Demo ===")
    txn = identify_transaction(
        client,
        transaction_info="STARBUCKS STORE 12345",
        country_gl="us",
        mcc="5814",
    )
    results["transaction"] = txn
    print(f"  title: {txn['title']}")
    print(f"  domain: {txn['domain']}")

    print("\n=== NAICS Classification Demo ===")
    naics = classify_naics(client, "stripe.com")
    results["naics"] = naics
    print(f"  domain: {naics['domain']}")
    print(f"  codes: {naics['codes'][:2] if naics['codes'] else []}")

    # Validation gates
    assert brand["title"], "brand.title must be non-empty"
    assert brand["logo_url"], "brand logo URL must be present"
    assert scrape["markdown_length"] > 0, "markdown must be non-empty"
    assert txn["domain"], "transaction brand.domain must be resolved"
    assert naics["codes"], "NAICS codes must be non-empty"

    print("\n=== All demos passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())