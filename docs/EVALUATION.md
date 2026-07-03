# Context.dev Use-Case Evaluation Matrix

Scoring: **Build Complexity** (1=easy, 5=hard), **Credit Cost** (per operation), **Production Readiness** (1=prototype, 5=ship today), **Monid Synergy** (0=none, 3=high value add).

## Official Use Cases

| Use Case | APIs | Complexity | Credits | Readiness | Monid | Notes |
|----------|------|------------|---------|-----------|-------|-------|
| CRM lead enrichment | `/brand/retrieve` (email) | 2 | 10/lead | 5 | 2 | Zapier native; webhook pattern proven |
| Onboarding prefill | `/brand/retrieve` (email), prefetch | 2 | 10/signup | 5 | 1 | Prefetch hides latency; 422 filters free email |
| Branded email templates | brand + styleguide + screenshot | 3 | ~65 | 4 | 2 | LLM HTML gen adds complexity |
| RAG from websites | `/web/crawl` | 3 | 1/page | 4 | 0 | Needs vector DB; crawl is turnkey |
| Campaign assets | brand + styleguide | 4 | ~60 | 3 | 3 | Image gen pipeline; Monid adds social tone |
| Transaction enrichment | `/brand/transaction_identifier` | 2 | 10/txn | 5 | 2 | 50M merchants; cache by descriptor |

## Brand APIs — Top Derived

| Use Case | APIs | Complexity | Credits | Readiness | Monid | Notes |
|----------|------|------------|---------|-----------|-------|-------|
| Logo wall (Logo Link) | CDN only | 1 | Free | 5 | 0 | Zero backend; domain restrictions required |
| White-label theming | `/brand/styleguide` | 3 | 50 | 4 | 0 | CSS variable mapping needed |
| Sales prospecting cards | `/brand/retrieve` | 2 | 10 | 5 | 2 | Monid adds employee count, posts |
| KYC enrichment | `/brand/retrieve` | 2 | 10 | 4 | 1 | Address + industry sufficient for most KYC |
| Email signatures | brand + Logo Link | 1 | 10 | 5 | 0 | Simple img + text template |

## Web APIs — Top Derived

| Use Case | APIs | Complexity | Credits | Readiness | Monid | Notes |
|----------|------|------------|---------|-----------|-------|-------|
| Docs chatbot | `/web/crawl` | 3 | 1/page | 4 | 0 | Official RAG guide is complete |
| Price monitoring | `/web/extract/product` | 2 | 10 | 4 | 1 | Monid price-compare for cross-merchant |
| Link previews | `/web/scrape/screenshot` | 1 | 5 | 5 | 0 | Single API call; hosted PNG |
| Structured extraction | `/web/extract` | 3 | 50+ | 3 | 0 | JSON Schema design is the hard part |
| PDF ingestion | `/web/scrape/markdown` | 1 | 1 | 5 | 0 | Native PDF/DOCX/XLSX support |

## Classification APIs — Top Derived

| Use Case | APIs | Complexity | Credits | Readiness | Monid | Notes |
|----------|------|------------|---------|-----------|-------|-------|
| Spend analytics | `/brand/transaction_identifier` | 2 | 10 | 5 | 2 | Core fintech use case |
| NAICS reporting | `/web/naics` | 1 | 10 | 5 | 0 | Regulatory compliance ready |
| Lead segmentation | EIC inline | 1 | 0 extra | 5 | 1 | Free with brand retrieve |
| Expense categorization | transaction + NAICS | 2 | 20 | 4 | 0 | Two-call pipeline |

## Integration Surfaces

| Surface | Complexity | Readiness | Best For |
|---------|------------|-----------|----------|
| SDK (Python/TS) | 1 | 5 | Backend services |
| REST/curl | 1 | 5 | Scripts, CI |
| MCP Server | 2 | 4 | AI agent tooling |
| CLI | 1 | 5 | Terminal workflows |
| Zapier/Make | 1 | 5 | No-code automation |
| Logo Link CDN | 1 | 5 | Frontend embeds |

## Scoring Summary

### Highest ROI (Readiness ≥4, Complexity ≤2)

1. **Logo Link CDN** — Free, zero backend, ship today
2. **CRM lead enrichment** — 10 credits, webhook pattern documented
3. **Transaction enrichment** — 10 credits, 50M merchants, fintech-ready
4. **Onboarding prefill** — Prefetch + retrieve, proven pattern
5. **Link preview screenshots** — 5 credits, single call

### Medium Effort, High Value (Complexity 3, Readiness ≥3)

1. **RAG pipeline** — Crawl is turnkey; embedding layer is standard
2. **White-label theming** — Styleguide → CSS variables
3. **Branded email templates** — Multi-API but well-documented
4. **Price monitoring** — Product extract + optional Monid compare

### Higher Effort (Complexity ≥4)

1. **Campaign asset generation** — Needs image gen pipeline
2. **Structured comparison pages** — JSON Schema design per use case
3. **Full competitive intelligence** — Multi-API + Monid social layer

## Credit Economics

| Plan | Credits | Logo Link | Best Use |
|------|---------|-----------|----------|
| Free | 500 (one-time) | 10K/mo | Prototyping, Logo Link production |
| Hobby $25 | 10K/mo | 100K/mo | Small SaaS enrichment |
| Starter $49 | 30K/mo | 500K/mo | CRM integration at scale |
| Pro $149 | 200K/mo | 2.5M/mo | Fintech transaction enrichment |

**Cost optimization patterns:**
- Cache brand responses by domain (3-month default maxAge)
- Use Logo Link for frontend logos (free, separate quota)
- Prefetch (0 credits) before user-facing calls
- Batch NAICS only when EIC inline is insufficient
- Cap crawl `maxPages` and use sitemap preview first