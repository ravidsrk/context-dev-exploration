#!/usr/bin/env python3
"""Run live Context.dev API demonstrations across product surfaces."""

from __future__ import annotations

import json

from context_dev.client import (
    classify_naics,
    classify_sic,
    crawl_markdown,
    create_client,
    extract_fonts,
    extract_styleguide,
    identify_transaction,
    prefetch_domain,
    retrieve_brand,
    scrape_markdown,
    scrape_screenshot,
    scrape_sitemap,
)

DOMAIN = "stripe.com"
URL = "https://stripe.com"


def main() -> int:
    client = create_client()

    print("=== Prefetch Domain (0 credits) ===")
    prefetch = prefetch_domain(client, DOMAIN)
    print(f"  status: {prefetch['status']}")
    print(f"  domain: {prefetch['domain']}")

    print("\n=== Brand Retrieve Demo ===")
    brand = retrieve_brand(client, DOMAIN)
    print(f"  title: {brand['title']}")
    print(f"  domain: {brand['domain']}")
    print(f"  logo_url: {brand['logo_url']}")

    print("\n=== Web Scrape Markdown Demo ===")
    scrape = scrape_markdown(client, URL)
    print(f"  url: {scrape['url']}")
    print(f"  markdown_length: {scrape['markdown_length']}")

    print("\n=== Sitemap Discovery Demo ===")
    sitemap = scrape_sitemap(client, DOMAIN)
    print(f"  url_count: {sitemap['url_count']}")
    print(f"  sample_urls: {sitemap['sample_urls']}")

    print("\n=== Web Crawl Markdown Demo (max_pages=2) ===")
    crawl = crawl_markdown(client, URL, max_pages=2)
    print(f"  num_succeeded: {crawl['num_succeeded']}")
    print(f"  pages_with_markdown: {crawl['pages_with_markdown']}")

    print("\n=== Transaction Enrichment Demo ===")
    txn = identify_transaction(
        client,
        transaction_info="STARBUCKS STORE 12345",
        country_gl="us",
        mcc="5814",
    )
    print(f"  title: {txn['title']}")
    print(f"  domain: {txn['domain']}")

    print("\n=== NAICS Classification Demo ===")
    naics = classify_naics(client, DOMAIN)
    print(f"  domain: {naics['domain']}")
    print(f"  codes: {naics['codes'][:2] if naics['codes'] else []}")

    print("\n=== SIC Classification Demo ===")
    sic = classify_sic(client, DOMAIN)
    print(f"  domain: {sic['domain']}")
    print(f"  codes: {sic['codes'][:2] if sic['codes'] else []}")

    print("\n=== Extract Fonts Demo ===")
    fonts = extract_fonts(client, DOMAIN)
    print(f"  font_count: {fonts['font_count']}")
    print(f"  font_names: {fonts['font_names']}")

    print("\n=== Extract Styleguide Demo ===")
    styleguide = extract_styleguide(client, DOMAIN)
    print(f"  color_count: {styleguide['color_count']}")
    print(f"  has_typography: {styleguide['has_typography']}")

    print("\n=== Screenshot Demo ===")
    shot = scrape_screenshot(client, DOMAIN)
    print(f"  has_screenshot: {shot['has_screenshot']}")
    print(f"  screenshot_url: {shot['screenshot_url']}")

    # Validation gates
    assert prefetch.get("status") or prefetch.get("domain"), "prefetch must return status or domain"
    assert brand["title"], "brand.title must be non-empty"
    assert brand["logo_url"], "brand logo URL must be present"
    assert scrape["markdown_length"] > 0, "markdown must be non-empty"
    assert sitemap["url_count"] > 0, "sitemap must discover URLs"
    assert crawl["num_succeeded"] >= 1, "crawl numSucceeded must be >= 1"
    assert txn["domain"], "transaction brand.domain must be resolved"
    assert naics["codes"], "NAICS codes must be non-empty"
    assert sic["codes"], "SIC codes must be non-empty"
    assert fonts["font_count"] >= 0, "fonts response must be parseable"
    assert styleguide["color_count"] > 0, "styleguide must return colors"
    assert shot["has_screenshot"], "screenshot URL must be present"

    print("\n=== All demos passed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())