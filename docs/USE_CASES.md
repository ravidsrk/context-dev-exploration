# Context.dev Use-Case Catalog

Complete catalog of official use-case guides plus derived build opportunities, grouped by API product category.

## Product Categories

| Category | Core Value | Credit Range |
|----------|-----------|--------------|
| Brand APIs | Domain → logos, colors, profile, socials, industry | 10–50 |
| Logo Link CDN | Embed logos via CDN (no API call) | Free (10K/mo) |
| Web APIs | Scrape, crawl, screenshot, extract | 1–50+ |
| Classification APIs | NAICS, SIC, transaction enrichment | 10 |

---

## Official Use-Case Guides (6)

### 1. Auto-Enrich Leads in CRM
- **APIs:** `GET /brand/retrieve` (by email), `POST /brand/prefetch` (email), optional `POST /web/extract` (structured)
- **Outcome:** Work email → full company profile written back to CRM before rep opens record
- **Credits:** 10/lead (prefetch free); extract adds 10+
- **Integrations:** HubSpot, Salesforce, Zoho, Pipedrive, monday.com webhooks; Zapier native

### 2. Prefill Onboarding from Work Email
- **APIs:** `GET /brand/retrieve` (email), `POST /brand/prefetch` (email)
- **Outcome:** Step 1 email → step 2 shows logo, description, socials pre-filled
- **Credits:** 10/signup; prefetch hides cold-hit latency
- **Pattern:** Fire prefetch on email blur; retrieve on form submit

### 3. Build Branded Email Templates
- **APIs:** `/brand/retrieve`, `/brand/styleguide`, `/web/scrape/images`, `/web/scrape/screenshot`
- **Outcome:** Domain → on-brand HTML email with logo, colors, typography, hero screenshot
- **Credits:** 10 + 50 (styleguide) + 5 (screenshot) ≈ 65/domain
- **Stack:** Context.dev → LLM generates HTML using styleguide tokens

### 4. Build Agentic RAG from Websites
- **APIs:** `/web/crawl` (markdown), `/web/scrape/sitemap` (preview), optional `/web/extract`
- **Outcome:** Entire docs site → chunked embeddings → queryable knowledge base
- **Credits:** 1/page crawled; sitemap preview = 1 credit
- **Stack:** Context.dev crawl → OpenAI embeddings → Pinecone/pgvector

### 5. Generate Branded Campaign Assets at Scale
- **APIs:** `/brand/retrieve`, `/brand/styleguide`, `/web/scrape/screenshot`
- **Outcome:** Domain → automated social/ad creative pipeline with brand colors/fonts
- **Credits:** 10 + 50 + 5 per campaign batch
- **Stack:** Context.dev brand data → image gen API → rasterized assets

### 6. Transaction/Spend Analytics Enrichment
- **APIs:** `GET /brand/transaction_identifier`, optional `/web/naics`
- **Outcome:** `AMZN MKTP US` → Amazon logo, industry, clean merchant name
- **Credits:** 10/transaction; cache by normalized descriptor
- **Stack:** Plaid/bank feed → Context.dev → categorized spend dashboard

---

## Brand APIs — Derived Use Cases

| Use Case | APIs | Outcome | Credits |
|----------|------|---------|---------|
| Partner logo wall | Logo Link CDN | Auto-populate "trusted by" from signup emails | Free |
| Investor dashboard ticker enrichment | `/brand/retrieve` (ticker) | Stock ticker → company profile + logo | 10 |
| White-label SaaS theming | `/brand/styleguide`, `/brand/fonts` | Customer domain → CSS variables for UI | 50+10 |
| KYC/firmographic enrichment | `/brand/retrieve` (domain) | Address, phone, industry for compliance | 10 |
| Sales prospecting cards | `/brand/retrieve` (name/domain) | One-pager with logo, socials, description | 10 |
| Email signature generator | `/brand/retrieve` + Logo Link | Employee email domain → branded signature | 10 |
| Competitor profile pages | `/brand/retrieve` (domain) | Structured competitor dossier foundation | 10 |
| Directory/marketplace listings | Logo Link + `/brand/retrieve` | Vendor domain → logo + metadata, no upload | Free+10 |
| Churn save offer personalization | `/brand/styleguide` | Cancel flow styled to customer's brand | 50 |
| HR onboarding portal branding | `/brand/retrieve` (email) | New hire's previous employer aesthetic | 10 |

---

## Logo Link CDN — Derived Use Cases

| Use Case | Integration | Outcome | Credits |
|----------|-------------|---------|---------|
| CRM contact avatars | `<img src="logos.context.dev/...">` | Logo per company domain in list views | Free |
| Google Sheets logo columns | `=IMAGE("logos.context.dev/...")` | Spreadsheet enrichment at scale | Free |
| Excel logo columns | `=IMAGE()` in M365 | Same for Excel workflows | Free |
| Transaction feed icons | Logo Link in fintech UI | Merchant logos next to descriptors | Free |
| Email template logos | `<img>` in HTML email | Always-fresh logos, 24h browser cache | Free |
| Landing page social proof | Dynamic logo strip from customer domains | "Trusted by" without asset hosting | Free |

---

## Web APIs — Derived Use Cases

| Use Case | APIs | Outcome | Credits |
|----------|------|---------|---------|
| Docs chatbot / support bot | `/web/crawl` | Internal docs → RAG chatbot | 1/page |
| Price monitoring | `/web/extract/product` | Product URL → name, price, features | 10 |
| Competitor pricing pages | `/web/scrape/markdown` + LLM | Clean markdown → structured pricing | 1 |
| Link preview cards | `/web/scrape/screenshot` | URL → PNG for social/sharing | 5 |
| Website change monitoring | Monitors API (webhook) | Alert on page/sitemap changes | varies |
| Legal/compliance page archive | `/web/scrape/markdown` | Terms/privacy → versioned markdown | 1 |
| Product catalog scraper | `/web/extract/products` | Brand site → full product list | 50+ |
| Structured comparison pages | `/web/extract` (JSON Schema) | "Has free trial?", "pricing tiers" | 50+ |
| Font matching for emails/PDFs | `/brand/fonts` | Downloadable @font-face URLs | 10 |
| Web search + scrape pipeline | `/web/search` | Query → results as markdown | varies |
| PDF/DOCX ingestion | `/web/scrape/markdown` (pdf param) | Document URL → text for LLMs | 1 |
| Design system documentation | `/brand/styleguide` | Auto-generate design token docs | 50 |

---

## Classification APIs — Derived Use Cases

| Use Case | APIs | Outcome | Credits |
|----------|------|---------|---------|
| SEC/regulatory reporting | `/web/naics` | Domain → NAICS 2022 codes | 10 |
| Tax/accounting SIC codes | `/web/sic` | Domain → SIC (original or SEC) | 10 |
| Lead segmentation/routing | EIC inline on `/brand/retrieve` | Industry-based sales routing | 0 extra |
| Expense categorization | `/brand/transaction_identifier` | Bank descriptor → merchant + industry | 10 |
| Subscription identification | `/brand/transaction_identifier` | `NETFLIX.COM` → Netflix profile | 10 |
| MCC-based fallback icons | `/brand/transaction_identifier` + MCC | Ambiguous descriptors resolved | 10 |
| Portfolio company tagging | `/web/naics` + `/web/sic` | VC portfolio industry classification | 20 |
| Market map generation | `/web/naics` (batch) | Classify competitor set by industry | 10 each |

---

## Integration Surfaces — Use Cases

| Surface | Use Case | Path |
|---------|----------|------|
| MCP Server | AI agent with brand/web tools | `install-mcp.md` → Cursor/Claude |
| CLI | Terminal brand lookups, CI scripts | `context-dev brand retrieve --domain` |
| Skill | Agent auto-selects correct API | `install-skill.md` |
| Zapier | No-code CRM enrichment | Trigger: new lead → Context.dev → CRM update |
| Make | Visual automation scenarios | HTTP module or native integration |
| SDK (TS/Python/Go/Ruby/PHP) | Backend enrichment services | `quickstart.md` patterns |

---

## Utility/Prefetch — Use Cases

| Use Case | API | Outcome | Credits |
|----------|-----|---------|---------|
| Hide cold-hit latency | `POST /brand/prefetch` | Warm cache before user-facing call | 0 |
| Signup form optimization | `POST /brand/prefetch` (email) | Prefetch on email field blur | 0 |
| Batch domain warming | `POST /brand/prefetch` (loop) | Pre-warm known domain list | 0 |

---

## Combo Architectures (Context.dev + External Tools)

| Architecture | Context.dev Role | External Tool Role |
|--------------|------------------|-------------------|
| Full prospect dossier | Brand profile, logo, industry | Monid: LinkedIn posts, employee count |
| Competitive intelligence | Styleguide, product extract | Monid: social listening, price compare |
| RAG + brand context | Web crawl markdown | OpenAI embeddings + vector DB |
| Campaign generation | Brand colors, fonts, logos | Image gen API (DALL-E, Flux) |
| Spend analytics | Transaction enrichment | Plaid/banking API for raw descriptors |

---

## Credit Budget Guide (500 free credits)

| Priority | Calls | Est. Credits |
|----------|-------|--------------|
| Brand retrieve (cache hits) | 20 domains | 200 |
| Web scrape markdown | 50 pages | 50 |
| Transaction enrichment | 10 descriptors | 100 |
| NAICS classification | 10 domains | 100 |
| Styleguide (selective) | 1 domain | 50 |
| **Total** | | **~500** |