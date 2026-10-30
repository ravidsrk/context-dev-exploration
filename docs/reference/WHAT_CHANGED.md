# What changed since July 2026

Re-run on 2026-10-30 with `context.dev` 2.41.1 (Python) and 3.19.1 (TypeScript).

## 1. The SDK moved under the code

Brand.dev renamed to Context.dev on 2026-03-21. Between July and October the API consolidated. On Sep 22, Scrape and Map became single endpoints with a `formats` option, and the SDKs replaced the per-format methods with them. Of the 11 Python SDK methods the July client called, 4 no longer exist:

| July call | October replacement |
|---|---|
| `web.web_scrape_md(url)` | `web.scrape(url, formats={"markdown": True})`, then read `markdown.data` |
| `web.web_scrape_sitemap(domain)` | `web.map_urls(domain)`, which returns `urls[].url` and `title` |
| `brand.identify_from_transaction(...)` | `brand.retrieve(type="by_transaction", ...)` |
| `web.extract_fonts(domain)` | not in the SDK; `GET /web/fonts` still works via `client.get` |

TypeScript went from 0.1.x to 3.x. The `client.brand.webScrapeMd`, `webScrapeSitemap`, `retrieveNaics` and `styleguide` calls became `client.web.scrape`, `client.web.mapUrls`, `client.industry.retrieveNaics` and `client.web.extractStyleguide`. `brand.retrieve` now takes a `type` discriminator.

## 2. Why the tests did not notice

`tests/test_context_client.py` used plain `MagicMock()` clients. A `MagicMock` accepts any attribute, so `client.web.web_scrape_md` kept "working" after it was deleted from the SDK. The tests now build mocks with `create_autospec(ContextDev(...), instance=True)`, so calling a removed method raises `AttributeError`. `TestSdkSurface.test_july_methods_are_gone` pins the four removals, and `make sdk-compat` checks every method the repo uses without making network calls.

## 3. The July pricing check was wrong

The July scout loop scraped `https://stripe.com/pricing` and set `has_pricing_content = len(markdown) > 100`. The Markdown it got started with the navigation menu (`- Products - Solutions - Developers ...`), and the check still passed. The October page is 60,562 characters of Markdown, so a length check tells you nothing.

Both loops now ask Scrape for **highlights** (Sep 23), which are passages relevant to a query. They count the page as having pricing only if at least one passage comes back. Live output from `evidence/runs/ts-scout-loop-3x-2026-10-30.txt`:

```
"has_pricing_content": true,
"pricing_preview": "[Standard > 2.9% + 30¢] per successful transaction for domestic cards … [Buy Now Pay Later] 5.99% + 30¢ … Dispute countered fee $15.00"
```

## 4. The hosted MCP URL is dead

`context_dev/mcp/client.py` still points at the Stainless-hosted MCP URL used in July, which now returns HTTP 525. Context.dev's own hosted MCP went live on Aug 3 and uses OAuth. The code-mode loops are left as July artifacts and have not been ported in this branch.

## 5. Credit numbers drift too

The Sep 23 changelog says highlights cost +3 credits. The pricing page on 2026-10-30 lists Highlights at +1. `context_dev/latest.py` uses +1 and says so in a comment. The live probe agrees: a highlights scrape of stripe.com/pricing reported 2 credits consumed (scrape 1 + highlights 1). Treat `key_metadata.credits_consumed` in responses as the source of truth.
