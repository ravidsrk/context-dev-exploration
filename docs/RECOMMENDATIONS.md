# Top Build Candidates — Context.dev

Ranked by feasibility, credit efficiency, and market fit based on live API testing and documentation review.

## Tier 1: Ship This Week

### 1. Fintech Spend Dashboard with Merchant Logos
- **APIs:** `/brand/transaction_identifier` + Logo Link CDN
- **Why:** Live demo resolved `STARBUCKS STORE 12345` → starbucks.com with logo in 10 credits. Logo Link handles UI embeds for free.
- **Stack:** Plaid/bank feed → Context.dev enrichment → React dashboard with Logo Link `<img>`
- **Credits:** 10/unique merchant (cache by normalized descriptor)
- **Monid add-on:** LinkedIn profile check for merchant verification ($0.0015)

### 2. CRM Lead Auto-Enrichment Webhook
- **APIs:** `/brand/retrieve` (email) + `/brand/prefetch` (email)
- **Why:** Official guide with HubSpot/Salesforce/Zoho/Pipedrive/monday.com patterns. Zapier native integration exists.
- **Stack:** CRM webhook → FastAPI/Express handler → Context.dev → write-back
- **Credits:** 10/lead; prefetch free; 422 auto-filters Gmail/Yahoo
- **Monid add-on:** Employee count for firmographic lead scoring

### 3. Logo Wall / Social Proof Strip
- **APIs:** Logo Link CDN only
- **Why:** Zero API credits. 10K free requests/month. `=IMAGE()` works in Sheets/Excel.
- **Stack:** Customer email domains → `logos.context.dev/?publicClientId=X&domain=Y`
- **Credits:** Free (Logo Link quota, not API credits)

### 4. SaaS Onboarding Brand Prefill
- **APIs:** `/brand/prefetch` (on blur) + `/brand/retrieve` (on submit)
- **Why:** Official use-case guide. Prefetch hides 7–18s cold-hit latency.
- **Stack:** React form → prefetch on email blur → retrieve on step 2
- **Credits:** 10/signup

## Tier 2: Ship This Month

### 5. Documentation RAG Chatbot
- **APIs:** `/web/crawl` + `/web/scrape/sitemap` (preview)
- **Why:** Official guide with Pinecone + OpenAI embedding code. Crawl returns clean markdown (tested: 21,554 chars from stripe.com scrape).
- **Stack:** Context.dev crawl → chunk by heading → embed → vector DB → LLM
- **Credits:** 1/page; preview sitemap for 1 credit

### 6. Competitor Intelligence Dashboard
- **APIs:** `/brand/retrieve` + `/brand/styleguide` + `/web/extract/product`
- **Why:** Combines brand profile, design tokens, and product data. Monid adds social posts and price compare.
- **Stack:** Context.dev foundation → Monid social layer → dashboard UI
- **Credits:** 10 + 50 + 10 per competitor = ~70
- **Monid:** $0.0015/post lookup, $1.188/competitor compare

### 7. Branded Email Template Generator
- **APIs:** `/brand/retrieve` + `/brand/styleguide` + `/web/scrape/screenshot`
- **Why:** Official use-case. Styleguide provides colors, fonts, spacing for LLM HTML generation.
- **Stack:** Domain input → Context.dev brand data → LLM → HTML email
- **Credits:** ~65/domain

### 8. Industry-Tagged Account Database
- **APIs:** `/brand/retrieve` (EIC free inline) + `/web/naics` (when regulatory needed)
- **Why:** Live NAICS demo returned `522320 Financial Transactions Processing` for stripe.com with high confidence.
- **Stack:** Domain list → batch classify → segment/routing rules
- **Credits:** 10/domain (NAICS); 0 extra for EIC on brand retrieve

## Tier 3: Larger Builds

### 9. AI Agent with Context.dev MCP Server
- **APIs:** All via MCP
- **Why:** MCP install guide supports Claude, Cursor, VS Code. Agent can call brand/web/classification tools.
- **Stack:** MCP server → agent skill → user queries
- **Credits:** Per-toolcall

### 10. Price Monitoring SaaS
- **APIs:** `/web/extract/product` + `/web/scrape/markdown`
- **Why:** Product extract returns name, price, features. Monid price-compare for cross-merchant.
- **Stack:** URL watchlist → scheduled extract → alert on change
- **Credits:** 10/product check

### 11. White-Label SaaS Theming Engine
- **APIs:** `/brand/styleguide` + `/brand/fonts`
- **Why:** Returns CSS-ready design tokens. Map to CSS variables for customer-branded UI.
- **Stack:** Customer domain → styleguide → CSS variable injection
- **Credits:** 50/domain (one-time, cache aggressively)

### 12. Campaign Asset Pipeline
- **APIs:** `/brand/retrieve` + `/brand/styleguide` + image gen API
- **Why:** Official use-case. Brand colors/fonts feed into generative image prompts.
- **Stack:** Domain → brand tokens → LLM prompt → image gen → rasterize
- **Credits:** ~60/campaign + image gen costs

## Anti-Patterns (Don't Build These First)

| Pattern | Why Not |
|---------|---------|
| Self-hosted logo CDN | Logo Link is free and purpose-built; re-hosting violates ToS |
| Browser-side API calls | Keys exposed; always proxy through backend |
| Full-site crawl without `maxPages` | Burns credits fast; use sitemap preview first |
| NAICS on every brand lookup | EIC is free inline on `/brand/retrieve` |
| Monid for brand logos | Context.dev is cheaper and more complete for brand data |

## Recommended First Project

**Fintech Spend Dashboard** — combines the highest-readiness APIs (transaction enrichment + Logo Link), has clear market demand, and our live demo proved the core loop works end-to-end.

```python
# Proven in scripts/run_demos.py
txn = identify_transaction(client, "STARBUCKS STORE 12345", country_gl="us", mcc="5814")
# → title: Starbucks, domain: starbucks.com

# UI embed (free)
# <img src="https://logos.context.dev/?publicClientId=XXX&domain=starbucks.com" />
```