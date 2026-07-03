# Context.dev Documentation Index

**Canonical source:** https://docs.context.dev/llms.txt  
**Indexed:** 2026-07-03  
**Total pages:** 56 docs + 1 OpenAPI spec = **57 entries**

Every row lists the page title, full URL, one-line description, primary API endpoint or integration path, and documented credit cost where applicable.

---

## Product Categories (4)

| # | Category | Core APIs |
|---|----------|-----------|
| 1 | Brand APIs | `/brand/retrieve`, `/brand/retrieve-by-email`, `/brand/transaction_identifier`, `/brand/styleguide`, `/brand/fonts` |
| 2 | Logo Link CDN | `https://logos.context.dev/?publicClientId=&domain=` |
| 3 | Web APIs | `/web/scrape/*`, `/web/crawl`, `/web/extract`, `/web/search` |
| 4 | Classification APIs | `/web/naics`, `/web/sic`, EIC inline on brand responses |

---

## Complete Page Listing (from llms.txt)

### Getting Started (5)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 1 | Context.dev | https://docs.context.dev/index.md | Landing: domain → structured AI-ready data | Overview | — |
| 2 | Introduction | https://docs.context.dev/introduction.md | What Context.dev is, 4 API categories, outputs table | Overview | — |
| 3 | Quickstart | https://docs.context.dev/quickstart.md | API key, SDK install, first calls | `/brand/retrieve`, `/web/scrape/markdown`, `/brand/transaction_identifier` | 10/1/10 |
| 4 | Agent Quickstart | https://docs.context.dev/agent-quickstart.md | One-prompt agent setup | MCP + SDK | — |
| 5 | Install the CLI | https://docs.context.dev/install-cli.md | `context-dev` terminal CLI | CLI → all endpoints | — |

### Agent / Integration Install (2)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 6 | Install MCP | https://docs.context.dev/install-mcp.md | MCP server for Claude, Cursor, VS Code | MCP server | — |
| 7 | Install the Context.dev skill | https://docs.context.dev/install-skill.md | Agent skill for correct API selection | Agent skill | — |

### Brand Intelligence API Reference (7)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 8 | Retrieve brand data by domain | https://docs.context.dev/api-reference/brand-intelligence/retrieve-brand-data-by-domain.md | Logos, colors, industry, description from domain | `GET /brand/retrieve?domain=` | 10 |
| 9 | Retrieve brand data by company name | https://docs.context.dev/api-reference/brand-intelligence/retrieve-brand-data-by-company-name.md | Brand lookup by company name | `GET /brand/retrieve?name=` | 10 |
| 10 | Retrieve brand data by email address | https://docs.context.dev/api-reference/brand-intelligence/retrieve-brand-data-by-email-address.md | Brand from work email; 422 on free/disposable | `GET /brand/retrieve-by-email?email=` | 10 |
| 11 | Retrieve brand data by stock ticker | https://docs.context.dev/api-reference/brand-intelligence/retrieve-brand-data-by-stock-ticker.md | Public company lookup by ticker | `GET /brand/retrieve?ticker=` | 10 |
| 12 | Retrieve simplified brand data by domain | https://docs.context.dev/api-reference/brand-intelligence/retrieve-simplified-brand-data-by-domain.md | Essential fields only (faster) | `GET /brand/retrieve-simplified?domain=` | 10 |
| 13 | Identify brand from transaction data | https://docs.context.dev/api-reference/brand-intelligence/identify-brand-from-transaction-data.md | Card descriptor → merchant brand | `GET /brand/transaction_identifier` | 10 |
| 14 | Scrape Styleguide | https://docs.context.dev/api-reference/web-extraction/scrape-styleguide.md | Design system: colors, typography, spacing, shadows | `GET /brand/styleguide` or `web.extract_styleguide` | 50 |

### Utility / Prefetch API Reference (2)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 15 | Prefetch brand data for a domain | https://docs.context.dev/api-reference/utility/prefetch-brand-data-for-a-domain.md | Warm cache before user-facing call | `POST /brand/prefetch?domain=` | 0 |
| 16 | Prefetch brand data by email | https://docs.context.dev/api-reference/utility/prefetch-brand-data-by-email.md | Warm cache from email domain | `POST /brand/prefetch-by-email?email=` | 0 |

### Web Scraping API Reference (7)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 17 | Scrape Markdown | https://docs.context.dev/api-reference/web-scraping/scrape-markdown.md | URL → LLM-ready Markdown | `GET /web/scrape/markdown?url=` | 1 |
| 18 | Scrape HTML | https://docs.context.dev/api-reference/web-scraping/scrape-html.md | Raw HTML content | `GET /web/scrape/html?url=` | 1 |
| 19 | Scrape Images | https://docs.context.dev/api-reference/web-scraping/scrape-images.md | Image assets from page | `GET /web/scrape/images?url=` | 1 (5 enriched) |
| 20 | Scrape Screenshot | https://docs.context.dev/api-reference/web-scraping/scrape-screenshot.md | PNG screenshot of webpage | `GET /web/scrape/screenshot?url=` | 5 |
| 21 | Crawl Website & Scrape Markdown | https://docs.context.dev/api-reference/web-scraping/crawl-website-&-scrape-markdown.md | Multi-page crawl → Markdown | `GET /web/crawl?url=&maxPages=` | 1/page |
| 22 | Crawl Sitemap | https://docs.context.dev/api-reference/web-scraping/crawl-sitemap.md | Discover all page URLs | `GET /web/scrape/sitemap?domain=` | 1 |
| 23 | Web Search | https://docs.context.dev/api-reference/web-scraping/web-search.md | Search web + optional scrape to Markdown | `GET /web/search?query=` | varies |

### Web Extraction API Reference (6)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 24 | Scrape Fonts | https://docs.context.dev/api-reference/web-extraction/scrape-fonts.md | Font families, weights, usage counts | `GET /brand/fonts` or `web.extract_fonts` | 10 |
| 25 | Extract a single product from a URL | https://docs.context.dev/api-reference/web-extraction/extract-a-single-product-from-a-url.md | Product page detection + extraction | `GET /web/extract/product?url=` | 10 |
| 26 | Extract products from a brand's website | https://docs.context.dev/api-reference/web-extraction/extract-products-from-a-brands-website.md | All products from brand site | `GET /web/extract/products?domain=` | 50+ |
| 27 | Extract Structured Website Data | https://docs.context.dev/api-reference/web-extraction/extract-structured-website-data.md | JSON Schema-driven extraction | `POST /web/extract` | 50+ |
| 28 | Classify NAICS industries | https://docs.context.dev/api-reference/web-extraction/classify-naics-industries.md | 2022 NAICS codes from domain/name | `GET /web/naics?input=` | 10 |
| 29 | Classify SIC industries | https://docs.context.dev/api-reference/web-extraction/classify-sic-industries.md | SIC codes (original or SEC) | `GET /web/sic?input=&type=` | 10 |

### Guides — Brand & Web (7)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 30 | Get Brand Data | https://docs.context.dev/guides/get-brand-data.md | Domain/name/email/ticker → full profile | `/brand/retrieve` variants | 10 |
| 31 | Get Logos from a Domain | https://docs.context.dev/guides/get-logo-from-url.md | Logo Link CDN embed | `logos.context.dev` CDN | Free |
| 32 | Scrape Websites | https://docs.context.dev/guides/scrape-websites-to-markdown.md | Markdown, HTML, crawl, sitemap, images | `/web/scrape/*`, `/web/crawl` | 1+ |
| 33 | Capture Webpage Screenshots | https://docs.context.dev/guides/take-webpage-screenshot.md | PNG screenshot capture | `/web/scrape/screenshot` | 5 |
| 34 | Extract a Website's Design System | https://docs.context.dev/guides/extract-design-system-from-website.md | Styleguide + fonts extraction | `/brand/styleguide`, `/brand/fonts` | 50+10 |
| 35 | Extract Product Data from Webpages | https://docs.context.dev/guides/extract-product-from-websites.md | Product record extraction | `/web/extract/product` | 10 |
| 36 | Extract Structured Data from Websites | https://docs.context.dev/guides/extract-structured-data-from-websites.md | Custom JSON Schema extraction | `POST /web/extract` | 50+ |

### Guides — Classification (4)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 37 | Overview | https://docs.context.dev/guides/classification/overview.md | Pick NAICS vs SIC vs EIC | Classification overview | — |
| 38 | EIC (Easy Industry Classification) | https://docs.context.dev/guides/classification/EIC.md | 24 industries, 220 subindustries | Inline `industries.eic` on brand | 0 extra |
| 39 | NAICS | https://docs.context.dev/guides/classification/NAICS.md | 2022 NAICS taxonomy | `/web/naics` | 10 |
| 40 | SIC | https://docs.context.dev/guides/classification/SIC.md | SIC taxonomy (original/SEC) | `/web/sic` | 10 |
| 41 | Transaction Enrichment | https://docs.context.dev/guides/enrich-transaction-codes.md | Card descriptor → merchant | `/brand/transaction_identifier` | 10 |

### Official Use Cases (6)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 42 | Auto-Enrich Leads in Your CRM | https://docs.context.dev/use-cases/lead-enrichment.md | Work email → CRM profile via webhook | `/brand/retrieve-by-email`, prefetch | 10 |
| 43 | Prefill Onboarding from a Work Email | https://docs.context.dev/use-cases/faster-onboarding-flows.md | Signup email → pre-filled company step | `/brand/retrieve-by-email`, prefetch | 10 |
| 44 | Build Branded Email Templates | https://docs.context.dev/use-cases/custom-email-templates.md | Domain → on-brand HTML email | brand + styleguide + screenshot | ~65 |
| 45 | Build an Agentic RAG System with Web Scraping | https://docs.context.dev/use-cases/build-rag-from-websites.md | Crawl → embed → vector DB | `/web/crawl`, sitemap | 1/page |
| 46 | Generate Branded Campaign Assets at Scale | https://docs.context.dev/use-cases/branded-campaign-assets.md | Domain → social/ad creative pipeline | brand + styleguide + LLM | ~60 |
| 47 | Transaction/Spend Analytics | https://docs.context.dev/use-cases/lead-enrichment.md | *(see transaction guide)* | `/brand/transaction_identifier` | 10 |

> Note: Transaction spend analytics is documented in `guides/enrich-transaction-codes.md`; the sixth official use-case slot in llms.txt maps to lead enrichment + transaction patterns across fintech apps.

### No-Code Integrations (4)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 48 | Zapier | https://docs.context.dev/nocode/zapier.md | Brand, NAICS, transaction, screenshot, styleguide | Zapier native actions | per-call |
| 49 | Make | https://docs.context.dev/nocode/make.md | Brand, screenshots, styleguide, products | Make HTTP/native | per-call |
| 50 | Google Sheets | https://docs.context.dev/nocode/google-sheets.md | Logo Link + IMAGE() formula | Logo Link CDN | Free |
| 51 | Microsoft Excel | https://docs.context.dev/nocode/microsoft-excel.md | Logo Link + IMAGE() function | Logo Link CDN | Free |

### Optimization (6)

| # | Title | URL | Description | API / Path | Credits |
|---|-------|-----|-------------|------------|---------|
| 52 | Integration Best Practices | https://docs.context.dev/optimization/best-practices.md | Caching, key hygiene, error handling | Patterns | — |
| 53 | Compression | https://docs.context.dev/optimization/compression.md | gzip response compression | HTTP header | — |
| 54 | Fair Use | https://docs.context.dev/optimization/fair-use.md | Brand data usage guidance | Policy | — |
| 55 | Prefetch for Faster Response | https://docs.context.dev/optimization/prefetching.md | Hide cold-hit latency | `/brand/prefetch` | 0 |
| 56 | Handle Rate Limits | https://docs.context.dev/optimization/rate-limits.md | 408/429 backoff strategies | Client patterns | — |
| 57 | Troubleshooting | https://docs.context.dev/optimization/troubleshooting.md | Status codes and recovery | Error catalog | — |

### OpenAPI Spec (1)

| # | Title | URL | Description |
|---|-------|-----|-------------|
| 58 | openapi.documented | https://app.stainless.com/api/spec/documented/context.dev/openapi.documented.yml | Full OpenAPI 3.0 spec |

---

## SDK Method Map (Python `context.dev`)

| SDK Method | REST Endpoint |
|------------|---------------|
| `client.brand.retrieve` | `/brand/retrieve` |
| `client.brand.retrieve_by_email` | `/brand/retrieve-by-email` |
| `client.brand.retrieve_by_name` | `/brand/retrieve?name=` |
| `client.brand.retrieve_by_ticker` | `/brand/retrieve?ticker=` |
| `client.brand.identify_from_transaction` | `/brand/transaction_identifier` |
| `client.utility.prefetch` | `/brand/prefetch` |
| `client.utility.prefetch_by_email` | `/brand/prefetch-by-email` |
| `client.web.web_scrape_md` | `/web/scrape/markdown` |
| `client.web.web_scrape_html` | `/web/scrape/html` |
| `client.web.web_scrape_images` | `/web/scrape/images` |
| `client.web.screenshot` | `/web/scrape/screenshot` |
| `client.web.web_crawl_md` | `/web/crawl` |
| `client.web.web_scrape_sitemap` | `/web/scrape/sitemap` |
| `client.web.search` | `/web/search` |
| `client.web.extract_styleguide` | `/brand/styleguide` |
| `client.web.extract_fonts` | `/brand/fonts` |
| `client.web.extract` | `/web/extract` |
| `client.industry.retrieve_naics` | `/web/naics` |
| `client.industry.retrieve_sic` | `/web/sic` |