# Monid Deep Research — Agent Combo Architectures

Phase 2 research: **5+ discover queries**, **3+ live runs**, reasoning about how Monid extends Context.dev agents — not a recap of Phase 1 LinkedIn profile runs.

---

## Research questions we asked

1. What **temporal signals** does Context.dev lack for agent loops?
2. Which Monid endpoints are **cheap enough** for per-lead agent calls?
3. Where does Monid **overlap** vs **complement** Context.dev perception?
4. What **multi-agent combos** emerge from pairing both?

---

## Phase 3 discover (additional agent signals)

| Query | Top hit | Price | Agent family |
|-------|---------|-------|--------------|
| domain WHOIS registration | Strale `domain-age-check` | $0.011 | Fraud / vendor onboarding |
| SEC filings 10-K | Strale `us-company-data` | $0.011 | Public-company compliance |
| email deliverability | Strale `email-deliverability-check` | $0.011 | Lead-quality gate before RESOLVE |
| competitor pricing SaaS | Strale `pricing-page-extract` | $0.36 | Family C when schema extract fails |
| competitor compare | Strale `competitor-compare` | $1.19 | Strategic intel (batch, not per-lead) |

Live notes: `us-company-data` for Stripe returned SEC HTTP 500 (degrade path required). `domain-age-check` for stripe.com returned 200 (fraud-agent viable).

---

## Discover queries (7)

| # | Query | Top hit | Score | Price | Agent use |
|---|-------|---------|-------|-------|-----------|
| 1 | company funding rounds venture capital | blockrun `/surf/fund/ranking` | 0.75 | $0.00825 | Investor scout agent |
| 2 | job postings hiring signals company | tikhub `search_jobs` | 0.74 | $0.0015 | Hiring velocity / layoff risk |
| 3 | website change monitoring diff | exa `/contents` | 0.72 | $0.002 | RAG observe step |
| 4 | tech stack detection website technologies | strale `tech-stack-detect` | 0.90 | $0.036 | Vendor risk / integration fit |
| 5 | news articles company press releases | akta `/v1/news` | 0.72 | $0.005+ | Sales triggers, risk |
| 6 | app store reviews product ratings | apify `amazon-reviews-extractor` | 0.70 | $0.00135/result | Product intel agent |
| 7 | company social media posts | tikhub `get_company_posts` | 0.75 | $0.0015 | Messaging velocity |

**Insight:** Monid clusters into **firmographic velocity** (jobs, posts, news), **technical fingerprint** (stack), and **marketplace/review** surfaces Context.dev does not touch.

---

## Live runs (3 categories)

### Run A: Hiring signals — TikHub LinkedIn jobs

```bash
monid run -p tikhub -e /api/v1/linkedin/web_v2/search_jobs \
  --query '{"keywords":"Stripe","count":5,"time_range":"past_month"}' -w
```

**Cost:** $0.0015  
**Result:** 5 Stripe PM roles (Global Payouts, Startup Products, etc.) with `posted_at`, `location`, LinkedIn URLs.  
**Agent reasoning:** Job title **themes** reveal product bets (payouts, enterprise) before press releases. Pair with Context.dev `brand.retrieve` for static profile → **expansion signal agent**.

**Evidence:** `evidence/monid-jobs-stripe.json`

### Run B: Tech stack — Strale company-tech-stack

```bash
monid run -p api.strale.io -e /x402/company-tech-stack \
  --query '{"domain":"stripe.com"}' -w
```

**Cost:** $0.011  
**Result:** Next.js, React, Nginx, Google Workspace, ElevenLabs chat widget, Stripe CDN, DNS/MX records.  
**Agent reasoning:** Context.dev tells you *what* Stripe is; Monid tells you *how they build* — critical for integration/partner agents and vendor security questionnaires.

**Evidence:** `evidence/monid-techstack-stripe.json`

### Run C: Tech stack detect — Strale tech-stack-detect

```bash
monid run -p api.strale.io -e /x402/tech-stack-detect \
  --query '{"domain":"stripe.com"}' -w
```

**Cost:** $0.03564  
**Result:** Overlapping signal with Run B; higher-level categories (analytics: Google Analytics, payment_processor: Stripe).  
**Agent reasoning:** Use cheaper `company-tech-stack` ($0.011) in loops; reserve detect for disputed/low-confidence domains.

**Evidence:** `evidence/monid-techstack-detect-stripe.json`

### Failed run: Akta news (documented)

```bash
monid run -p akta -e /v1/news --query '{"company":"https://stripe.com","limit":3}' -w
```

**Result:** HTTP 500 (retried with `stripe.com` — same).  
**Agent implication:** News layer needs fallback (Exa search, `web.search` via Context.dev, or retry queue). Production agents must **degrade gracefully**.

---

## Context.dev vs Monid: division of labor

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGENT PERCEPTION LAYER                       │
├────────────────────────────┬────────────────────────────────────┤
│      Context.dev           │           Monid                     │
│  (stable, typed, cached)   │  (volatile, social, marketplace)   │
├────────────────────────────┼────────────────────────────────────┤
│ Logo, colors, fonts        │ LinkedIn posts, jobs               │
│ Domain/email/ticker/txn ID │ Tech stack fingerprint             │
│ NAICS, SIC, EIC            │ News sentiment (when available)    │
│ Scrape/crawl/screenshot    │ Twitter mentions, reviews          │
│ Schema extract             │ Competitor compare ($1.19)         │
│ Web search                 │ VC rankings, crypto surf         │
└────────────────────────────┴────────────────────────────────────┘
```

**Rule for agent designers:** Context.dev = **canonical entity record**. Monid = **delta since last run**.

---

## Five agent-combo architectures (reasoned)

### Combo 1: Temporal Sales Trigger

```
Trigger: Monid new LinkedIn post detected
  → Context.dev brand.retrieve for talk track context
  → LLM draft outreach referencing post + brand.slogan
  → CRM act
```

**Why both:** Post text without brand voice sounds generic; brand without posts misses timing.

### Combo 2: Integration Partner Scout

```
Context.dev sitemap → find /docs, /api pages
Monid company-tech-stack → prospect's frameworks
  → Agent plans SDK example in their stack (React vs Vue)
```

**Why both:** Scrape gives content; stack tells **how** to embed.

### Combo 3: Vendor Risk Tiering

```
Context.dev NAICS + brand.address
Monid tech-stack → hosting, CDN, analytics vendors
  → Policy engine assigns tier
```

**Why both:** Industry code alone misses subprocessors (Segment, Cloudflare, etc.).

### Combo 4: Competitive Motion Detector

```
Context.dev crawl /pricing weekly (hash)
Monid jobs at competitor (role titles)
  → Infer strategy shift (hiring sales vs eng)
```

**Why both:** Price changes are lagging; hiring is leading indicator.

### Combo 5: RAG Freshness with Social Grounding

```
Context.dev crawl docs → vector index
Monid posts → "what we announced lately"
  → Agent answers user questions with doc RAG + social recency footnote
```

**Why both:** Docs are truth; posts are **narrative frame** customers hear.

---

## Cost model for agent loops

| Step | Provider | Unit cost | Frequency |
|------|----------|-----------|-----------|
| Entity resolve | Context.dev | 10 cr (~$0.10) | Once per domain, cache 90d |
| Page scrape | Context.dev | 1 cr | Perceive as needed |
| LinkedIn jobs | Monid | $0.0015 | Weekly per target |
| Tech stack | Monid | $0.011 | Quarterly per vendor |
| Posts | Monid | $0.0015 | Daily for watchlist |

**Example watchlist (50 companies):**  
- Context.dev: 50 × 10cr = 500cr one-time + incremental crawls  
- Monid daily posts: 50 × $0.0015 × 30 = **$2.25/mo**  

Agents must **cache Context.dev** aggressively; Monid is cheap enough for **frequent observe steps**.

---

## Discoveries that change agent design

1. **Jobs search is sub-cent** — enables per-lead hiring signals, not just enterprise watchlists.
2. **Tech stack has two price tiers** — agents should prefer `company-tech-stack` over `tech-stack-detect` in loops.
3. **News via Akta is flaky** — design fallback perception paths; never single-source temporal data.
4. **Competitor-compare is $1.19** — batch/monthly, not per-request in tight loops.
5. **Exa contents at $0.002** — alternative observe step for URL diff when Context.dev crawl is overkill.

---

## Evidence files

| File | Run | Cost |
|------|-----|------|
| `evidence/monid-jobs-stripe.json` | LinkedIn jobs | $0.0015 |
| `evidence/monid-techstack-stripe.json` | company-tech-stack | $0.011 |
| `evidence/monid-techstack-detect-stripe.json` | tech-stack-detect | $0.03564 |

Full discover JSON: `evidence/monid/monid-discover-{1..7}-*.json` (captured by `scripts/capture/monid_evidence.sh`). Raw CLI transcript: `evidence/monid/monid-deep-runs.log`.