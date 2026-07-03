# Monid Research — Complementing Context.dev

Research conducted via Monid CLI (`monid discover`, `monid inspect`, `monid run`) per [docs.monid.ai](https://docs.monid.ai/).

## What Monid Provides That Context.dev Does Not

| Capability | Context.dev | Monid |
|------------|-------------|-------|
| Brand logos, colors, profile | ✅ Core product | ❌ |
| Web scrape to markdown | ✅ Core product | Partial (via Apify actors) |
| Transaction enrichment | ✅ 50M+ merchants | ❌ |
| Industry classification (NAICS/SIC) | ✅ Built-in | ❌ |
| LinkedIn company posts | ❌ (socials URLs only) | ✅ TikHub endpoints |
| LinkedIn employee data | ❌ | ✅ Apify harvestapi |
| Twitter/X post search | ❌ | ✅ Apify, blockrun.ai |
| Competitor price comparison | ❌ | ✅ api.strale.io |
| Real-time social listening | ❌ | ✅ Multiple providers |

**Key insight:** Context.dev excels at structured brand/web extraction from domains. Monid excels at real-time external intelligence from social platforms, marketplaces, and third-party APIs.

---

## Monid Tool Invocations (Live)

### 1. Discover: Company Social Media Posts

```bash
monid discover -q "company social media posts" -l 5
```

**Results:**
| Provider | Endpoint | Price | Use |
|----------|----------|-------|-----|
| tikhub | `/api/v1/linkedin/web_v2/get_company_posts` | $0.0015/call | Recent LinkedIn posts |
| tikhub | `/api/v1/linkedin/web/get_company_posts` | $0.006/call | Company posts (v1) |
| blockrun.ai | `/api/v1/surf/search/social/posts` | $0.00825/call | Tweet full-text search |

**Context.dev pairing:** Use `/brand/retrieve` for company profile, then Monid for recent social activity to build a "company pulse" dashboard.

### 2. Discover: LinkedIn Company Profiles

```bash
monid discover -q "linkedin company profile" -l 5
```

**Results:**
| Provider | Endpoint | Price | Use |
|----------|----------|-------|-----|
| tikhub | `/api/v1/linkedin/web_v2/get_company_profile` | $0.0015/call | Full company profile |
| apify | `/harvestapi/linkedin-company-employees` | $0.018/result | Employee extraction |

### 3. Live Run: Stripe LinkedIn Profile

```bash
monid inspect -p tikhub -e /api/v1/linkedin/web_v2/get_company_profile
monid run -p tikhub -e /api/v1/linkedin/web_v2/get_company_profile \
  --query '{"url":"stripe"}' -w -o monid-linkedin-stripe.json
```

**Cost:** $0.0015  
**Key fields returned:**
- `employee_count`: 16,620
- `recent_posts[]`: 4 posts with dates, text, URLs
- `description`: Full LinkedIn company description
- `address`: HQ location
- `logo`: LinkedIn-hosted logo URL

**Comparison with Context.dev `/brand/retrieve` (stripe.com):**

| Field | Context.dev | Monid LinkedIn |
|-------|-------------|----------------|
| Company name | Stripe | Stripe |
| Description | ✅ Website-derived | ✅ LinkedIn-derived |
| Logo | ✅ CDN-hosted variants | LinkedIn CDN only |
| Employee count | ❌ | ✅ 16,620 |
| Recent social posts | ❌ (URLs only) | ✅ Full post text + dates |
| Industry codes | ✅ EIC/NAICS | ❌ |
| Brand colors | ✅ Hex palette | ❌ |
| Stock ticker | ✅ | ❌ |
| Address | ✅ | ✅ |

---

## Combo Architecture Patterns

### Pattern 1: Sales Intelligence Dossier
```
Context.dev /brand/retrieve(domain)  →  logo, colors, industry, socials
Monid tikhub/get_company_profile     →  employee_count, recent_posts
Monid tikhub/get_company_posts       →  engagement signals
```
**Use case:** CRM enrichment beyond static brand data — add "hiring velocity" and "recent announcements" signals.

### Pattern 2: Competitive Monitoring
```
Context.dev /web/extract/product     →  competitor pricing page structure
Context.dev /brand/styleguide        →  competitor design tokens
Monid api.strale.io/price-compare    →  cross-merchant price comparison
Monid blockrun.ai/social/posts       →  brand mention sentiment
```
**Use case:** Automated competitive intelligence dashboard.

### Pattern 3: Lead Scoring Enhancement
```
Context.dev /brand/retrieve(email)   →  company profile for lead
Monid tikhub/get_company_profile     →  employee_count for firmographic score
Context.dev /web/naics               →  industry for ICP matching
```
**Use case:** Enrich CRM leads with firmographic signals Context.dev doesn't provide.

### Pattern 4: Campaign Asset Pipeline
```
Context.dev /brand/retrieve          →  logos, colors, slogan
Context.dev /brand/styleguide        →  typography, spacing, shadows
Monid tikhub/get_company_posts       →  recent messaging themes
→ LLM generates on-brand campaign copy aligned with recent social tone
```
**Use case:** Branded campaign assets (official use-case #5) with social context.

### Pattern 5: Transaction + Social Verification
```
Context.dev /brand/transaction_identifier  →  merchant identity
Monid tikhub/get_company_profile           →  verify merchant still active
```
**Use case:** Fraud detection — cross-reference transaction merchant against live LinkedIn presence.

---

## Cost Comparison

| Operation | Context.dev | Monid |
|-----------|-------------|-------|
| Company profile | 10 credits (~$0.10) | $0.0015 (LinkedIn) |
| Social posts (10) | N/A | ~$0.0015 |
| Web scrape page | 1 credit (~$0.01) | varies by provider |
| Industry classification | 10 credits | N/A |
| Competitor compare | N/A | $1.188/call |

**Recommendation:** Use Context.dev for brand/web foundation; layer Monid for real-time social and market signals at low marginal cost.

---

## Monid Docs Gap

- `docs.monid.ai/llms.txt` returns 404
- Primary documentation via CLI `--help`, skill file, and discover/inspect workflow
- Fallback: Monid skill at `~/.claude/skills/monid/SKILL.md`

---

### 4. Discover: Twitter Brand Mentions

```bash
monid discover -q "twitter brand mentions" -l 3
```

| Provider | Endpoint | Price | Context.dev Pairing |
|----------|----------|-------|---------------------|
| api.strale.io | `/x402/brand-mention-search` | $0.033/call | Layer on `/brand/retrieve` for mention monitoring |
| mesh.heurist.xyz | `/x402/agents/ElfaTwitterIntelligenceAgent/search_mentions` | $0.011/call | Token/topic mention search |
| tikhub | `/api/v1/twitter/web/fetch_trending` | $0.0015/call | Trending context for brand campaigns |

### 5. Live Run: Stripe LinkedIn Posts

```bash
monid run -p tikhub -e /api/v1/linkedin/web_v2/get_company_posts \
  --query '{"url":"stripe"}' -w -o monid-linkedin-posts-stripe.json
```

**Cost:** $0.0015  
**Returned:** 4 recent posts with text, URLs, and `date_published` timestamps.  
**Pairing:** Context.dev `/brand/retrieve` gives static profile; Monid posts give **messaging velocity** for sales triggers ("they just announced X").

### 6. Discover: Competitor Pricing (re-run)

```bash
monid discover -q "competitor pricing data" -l 5
```

| Provider | Endpoint | Price | Pairing |
|----------|----------|-------|---------|
| api.strale.io | `/x402/competitor-compare` | $1.188/call | After Context.dev `/web/extract/product` |
| api.strale.io | `/x402/price-compare` | $0.011/call | Cross-merchant price comparison |

---

## OpenRouter Synthesis (Low-Cost Inference)

Used `OPEN_ROUTER_KEY` with `openai/gpt-4o-mini` to synthesize the pairing architecture. Reproducible via:

```bash
export OPEN_ROUTER_KEY="sk-or-v1-..."
python scripts/synthesize_pairing.py
```

**Synthesis output** (captured in `implementer/openrouter-synthesis.txt`):

> Monid enhances sales intelligence via LinkedIn posts, social search, and competitor pricing for real-time market insights. Context.dev provides brand logos, web scrape, transaction enrichment, and NAICS — creating a comprehensive data ecosystem. Brand identity and web presence from Context.dev enrich Monid's social insights; transaction enrichment reveals purchase behaviors; NAICS enables targeted outreach. Together they provide a multifaceted sales landscape view.

This confirms the layered architecture: **Context.dev = structured foundation**, **Monid = real-time external signals**, **OpenRouter = synthesis/narrative layer**.

---

## Evidence Files

| File | Description |
|------|-------------|
| `monid-linkedin-stripe.json` | Live LinkedIn company profile ($0.0015) |
| `monid-linkedin-posts-stripe.json` | Live LinkedIn company posts ($0.0015) |
| `openrouter-synthesis.txt` | GPT-4o-mini pairing synthesis |
| `scripts/synthesize_pairing.py` | Reproducible OpenRouter synthesis script |