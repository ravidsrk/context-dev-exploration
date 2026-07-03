# Context.dev Documentation Index

Canonical source: [docs.context.dev/llms.txt](https://docs.context.dev/llms.txt)  
Indexed: 2026-07-03

## Product Categories (4)

1. **Brand APIs** — Resolve domains into logos, colors, company profiles, styleguides, fonts
2. **Logo Link CDN** — Embed logos via CDN without API calls
3. **Web APIs** — Scrape, crawl, screenshot, extract products/structured data
4. **Classification APIs** — NAICS, SIC, EIC industry codes; transaction enrichment

## Integration Surfaces

| Surface | Doc | Path |
|---------|-----|------|
| SDKs | Quickstart | TypeScript, Python, Ruby, Go, PHP |
| REST API | API Reference | `https://api.context.dev/v1` |
| MCP Server | install-mcp.md | Claude, Cursor, VS Code |
| CLI | install-cli.md | `context-dev` CLI |
| Skill | install-skill.md | Agent skill for coding agents |
| No-code | Zapier, Make, Google Sheets, Excel | nocode/*.md |

---

## All Documentation Pages

### Getting Started

| Page | URL | Summary |
|------|-----|---------|
| Introduction | /introduction.md | Product overview, 4 API categories, outputs table |
| Quickstart | /quickstart.md | API key, SDK install, first calls |
| Agent Quickstart | /agent-quickstart.md | One-prompt agent setup |
| Index | /index.md | Landing page |

### Brand Intelligence API Reference

| Endpoint | Credits | Description |
|----------|---------|-------------|
| GET /brand/retrieve | 10 | By domain, name, email, ticker, ISIN |
| GET /brand/retrieve (simplified) | — | Essential fields only |
| GET /brand/transaction_identifier | 10 | Card descriptor → merchant brand |
| GET /brand/styleguide | 50 | Design system extraction |
| GET /brand/fonts | 10 | Font families and usage |

### Web Scraping API Reference

| Endpoint | Credits | Description |
|----------|---------|-------------|
| GET /web/scrape/markdown | 1 | URL → LLM-ready Markdown |
| GET /web/scrape/html | 1 | Raw HTML |
| GET /web/scrape/images | 1 (5 enriched) | Image assets extraction |
| GET /web/scrape/screenshot | 5 | PNG screenshot |
| GET /web/crawl | 1/page | Multi-page Markdown crawl |
| GET /web/crawl/sitemap | 1 | Discover all URLs |
| GET /web/search | varies | Web search + optional scrape |

### Web Extraction API Reference

| Endpoint | Credits | Description |
|----------|---------|-------------|
| GET /web/extract/product | 10 | Single product page |
| GET /web/extract/products | 50+ | All products from brand site |
| POST /web/extract/structured | 50+ | JSON Schema-driven extraction |
| GET /web/naics | 10 | NAICS industry classification |
| GET /web/sic | 10 | SIC industry classification |

### Utility API Reference

| Endpoint | Credits | Description |
|----------|---------|-------------|
| POST /brand/prefetch | 0 | Warm cache for domain |
| POST /brand/prefetch/email | 0 | Warm cache from email domain |

### Guides

| Guide | APIs Used |
|-------|-----------|
| Get Brand Data | /brand/retrieve |
| Get Logos (Logo Link) | logos.context.dev CDN |
| Scrape Websites | /web/scrape/markdown, /web/crawl |
| Take Screenshot | /web/scrape/screenshot |
| Extract Design System | /brand/styleguide, /brand/fonts |
| Extract Product | /web/extract/product, /web/extract/products |
| Extract Structured Data | /web/extract/structured |
| Transaction Enrichment | /brand/transaction_identifier |
| Classification Overview | /web/naics, /web/sic, EIC inline |
| NAICS | /web/naics |
| SIC | /web/sic |
| EIC | Inline on brand responses |

### Official Use Cases (6)

| Use Case | Primary APIs |
|----------|--------------|
| Lead Enrichment in CRM | /brand/retrieve (email), Zapier webhook |
| Faster Onboarding Flows | /brand/retrieve (email), prefetch |
| Custom Email Templates | /brand/retrieve, /brand/styleguide, /web/scrape/screenshot |
| Build RAG from Websites | /web/crawl, /web/scrape/markdown |
| Branded Campaign Assets | /brand/retrieve, /brand/styleguide, LLM generation |
| Transaction/Spend Analytics | /brand/transaction_identifier |

### Optimization

| Page | Topic |
|------|-------|
| Best Practices | Caching, error handling, key hygiene |
| Compression | gzip response compression |
| Fair Use | Brand data usage guidance |
| Prefetching | Hide cold-hit latency |
| Rate Limits | 408/429 backoff, client cache |
| Troubleshooting | Status codes, recovery patterns |

### No-Code Integrations

| Platform | Capabilities |
|----------|--------------|
| Zapier | Brand, NAICS, transaction, screenshot, styleguide |
| Make | Brand lookups, screenshots, styleguide, products |
| Google Sheets | Logo Link + IMAGE() formula |
| Microsoft Excel | Logo Link + IMAGE() function |

### Install Guides

| Tool | Purpose |
|------|---------|
| install-cli.md | Terminal access to all APIs |
| install-mcp.md | MCP server for AI agents |
| install-skill.md | Agent skill for correct API selection |

### OpenAPI

- Spec: `https://app.stainless.com/api/spec/documented/context.dev/openapi.documented.yml`