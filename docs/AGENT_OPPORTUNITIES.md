# Agent-Powered Build Opportunities

Fifteen-plus **novel** systems you can build — not copies of Context.dev's six official use-case guides. Each entry includes **why** it works, **which agent archetype** applies, **API mapping**, and **cost notes**.

Official guides covered: lead enrichment, faster onboarding, custom emails, RAG from websites, branded campaigns, MCP install. Everything below goes beyond those.

---

## 1. Merchant Dispute Explainer Agent

**What:** Cardholder sees `SQ *CAFE BLUE BTLR` → agent resolves merchant, shows logo, category, map link, and plain-English explanation.

**Why novel:** Combines `transaction_identifier` with narrative generation — not in any official guide. Trust UX for neobanks.

**Archetype:** Fintech Spend (Arch 7)  
**APIs:** `transaction_identifier` (10cr), Logo Link CDN (free)  
**Why Context.dev:** Merchant database is the moat; DIY requires payment network data deals.

---

## 2. Vendor Onboarding Risk Agent

**What:** Paste vendor domain → auto-fill security questionnaire (hosting, industry, HQ, data processors detected).

**Why novel:** Pairs NAICS/SIC with Monid tech-stack (live: Stripe → Next.js, Nginx, Google Workspace).

**Archetype:** Compliance (Arch 10)  
**APIs:** `brand.retrieve`, `retrieve_naics`, Monid `company-tech-stack` ($0.011)  
**Why not docs-only:** Requires multi-source fusion + policy rubric, not single endpoint call.

---

## 3. "Call Prep in 60 Seconds" Sales Agent

**What:** Before Zoom, agent builds dossier: brand profile, last 3 LinkedIn posts, open job titles signaling expansion, NAICS for ICP.

**Why novel:** Temporal layer (Monid posts + jobs) on static brand — official enrichment guide stops at firmographics.

**Archetype:** Sales Copilot (Arch 6) + Research Scout (Arch 1)  
**APIs:** `brand.retrieve` (10cr), Monid jobs ($0.0015), Monid posts ($0.0015)  
**Cost:** ~$0.12 Context + ~$0.005 Monid per dossier.

---

## 4. Pricing Page Mutation Watchdog

**What:** Weekly agent crawls competitor `/pricing`, extracts structured tiers, diffs vs last snapshot, alerts on changes.

**Why novel:** Uses crawl + `extract(product)` as **observe** step in a continuous loop — not one-shot scrape.

**Archetype:** Competitive Intel (Arch 8)  
**APIs:** `sitemap`, `crawl` (1cr/page), `extract` with pricing schema (10cr)  
**DIY trap:** Selectors break; schema extraction survives layout changes.

---

## 5. Customer Support "Company Context" Sidebar

**What:** Support ticket includes email domain → sidebar shows logo, industry, docs links scraped to markdown for agent context.

**Why novel:** Real-time RAG injection into ticket workflow, not standalone chatbot.

**Archetype:** RAG Curator (Arch 3) + Entity Resolver (Arch 2)  
**APIs:** `retrieve-by-email`, `scrape` on docs URL (1cr), `prefetch` on repeat visitors

---

## 6. White-Label Invoice Generator Agent

**What:** B2B billing platform themes PDF invoices to each client's brand (colors, fonts, logo) automatically.

**Why novel:** Styleguide + fonts + Logo Link for **document** output, not email templates (official #3).

**Archetype:** Theming (Arch 5)  
**APIs:** `extract_styleguide` (10cr), `extract_fonts` (5cr), Logo Link CDN

---

## 7. Directory / "Alternative To" Page Factory Agent

**What:** Input: competitor list → output: SEO comparison pages with logos, feature matrices from structured extract, screenshots.

**Why novel:** Programmatic SEO at scale with **verified** brand assets and extracted features — not LLM-guessed.

**Archetype:** Structured Extraction (Arch 4) + Theming (Arch 5)  
**APIs:** `brand.retrieve` × N, `web.extract(schema)`, `screenshot` (5cr each)

---

## 8. M&A Target Screener Agent

**What:** Screen domains against thesis: industry code range, employee growth (Monid), tech stack fit, recent news sentiment.

**Why novel:** Multi-signal investment workflow; Context.dev gives industry + site content; Monid gives velocity.

**Archetype:** Research Scout (Arch 1) + Compliance (Arch 10)  
**APIs:** `retrieve_naics`, `crawl` (blog), Monid jobs/news

---

## 9. Procurement Duplicate Vendor Detector

**What:** Match "Stripe Inc" vs "STRIPE PAYMENTS" expense lines to canonical domain via transaction + brand name paths.

**Why novel:** Entity resolution across **dissimilar identifiers** — core agent pattern, not a marketing use case.

**Archetype:** Entity Resolver (Arch 2)  
**APIs:** `transaction_identifier`, `retrieve?name=`, fuzzy merge in agent memory

---

## 10. Podcast / Newsletter Sponsor Matcher Agent

**What:** Given show transcript, extract mentioned companies → enrich with logos for show notes + verify sponsorship conflicts.

**Why novel:** NLP extract → Context.dev resolve pipeline for **media workflows**.

**Archetype:** Entity Resolver + Theming  
**APIs:** `retrieve?name=`, Logo Link, `brand.links`

---

## 11. Franchise Compliance Auditor Agent

**What:** Franchisee submits location → agent verifies web presence matches brand styleguide; flags off-brand colors/fonts.

**Why novel:** Automated brand police using **computed styleguide diff**, not manual design review.

**Archetype:** Theming (Arch 5)  
**APIs:** `extract_styleguide` on franchisee site vs canonical brand domain

---

## 12. Insurance FNOL (First Notice) Enricher Agent

**What:** Claim mentions business name → resolve domain, NAICS for vertical risk model, scrape location page.

**Why novel:** Regulated industry classification + web evidence chain.

**Archetype:** Compliance + Entity Resolver  
**APIs:** `retrieve_naics`, `retrieve_sic`, `scrape`

---

## 13. Developer Advocate "Docs Drift" Agent

**What:** Monitor your own docs site: sitemap growth, crawl changelog, alert when code samples reference deprecated APIs.

**Why novel:** Self-introspection agent — same RAG primitives applied to **your** domain.

**Archetype:** RAG Curator (Arch 3)  
**APIs:** `sitemap`, `crawl`, optional `web.search` for broken links

---

## 14. Event Booth Personalization Agent

**What:** Attendee badge scan (company on badge) → instant booth screen with their logo, industry, recent news headline.

**Why novel:** Sub-second perception loop at edge; `prefetch` + Logo Link for latency.

**Archetype:** Onboarding Concierge (Arch 12) + Research Scout  
**APIs:** `prefetch`, `retrieve`, Logo Link CDN (~20ms)

---

## 15. Legal Deposition Exhibit Builder Agent

**What:** Counsel provides URL list → agent scrapes to markdown, screenshots, timestamps, hashes for exhibit chain of custody.

**Why novel:** Evidentiary workflow combining scrape + screenshot + crawl metadata.

**Archetype:** RAG Curator + Structured Extraction  
**APIs:** `scrape`, `screenshot`, `crawl` with metadata logging

---

## 16. Marketplace Seller Verification Agent

**What:** Seller claims brand X → agent verifies domain ownership signals, styleguide match, transaction history if provided.

**Why novel:** Fraud prevention combining brand + transaction + visual signals.

**Archetype:** Entity Resolver + Fintech  
**APIs:** `brand.retrieve`, `transaction_identifier`, `screenshot`

---

## 17. HR Tech: Layoff Risk Early Warning Agent

**What:** Track hiring velocity (Monid jobs) + news sentiment + crawl careers page size — composite risk score.

**Why novel:** **Temporal workforce signals** absent from brand API; requires Monid pairing.

**Archetype:** Research Scout + Competitive Intel  
**APIs:** Monid `search_jobs`, Context `sitemap` + `crawl` on /careers

---

## 18. API Partner Readiness Agent

**What:** SaaS wants integration page → agent detects their stack (Monid), pulls brand assets, generates SDK snippet themed to their design system.

**Why novel:** DevRel automation — brand + tech stack + styleguide for **partner** sites.

**Archetype:** Theming + MCP Coding Agent (Arch 9)  
**APIs:** `extract_styleguide`, Monid tech-stack, MCP `execute` for codegen

---

## 19. Carbon / ESG Report Context Agent

**What:** Resolve supplier domains → NAICS for emissions factors, scrape sustainability pages via structured extract.

**Why novel:** ESG data collection is perception-heavy across heterogeneous sites.

**Archetype:** Compliance + Structured Extraction  
**APIs:** `retrieve_naics`, `web.extract` with ESG schema

---

## 20. Agent Benchmark Harness ("Perception Score")

**What:** Meta-system: given 100 domains, measure resolution accuracy, latency, credit cost vs DIY baseline.

**Why novel:** Turns Context.dev into **eval infrastructure** for agent builders — not a product feature but a platform play.

**Archetype:** Meta / MCP Native  
**APIs:** Full surface + logging; compare to Playwright baseline

---

## Prioritization matrix

| Build | Effort | Credit burn | Monid needed | Defensibility |
|-------|--------|-------------|--------------|---------------|
| Merchant Dispute Explainer | Low | Low | No | High (txn data) |
| Call Prep 60s | Low | Medium | Yes | Medium |
| Pricing Watchdog | Medium | High | Optional | Medium |
| Directory Factory | High | High | No | High (SEO scale) |
| Vendor Risk | Medium | Low | Yes | High (enterprise) |
| Docs Drift | Low | Medium | No | Medium (DX) |

---

## What makes these "agent" builds vs scripts

1. **Loops with memory** — diff vs prior scrape, not one-shot fetch  
2. **Planning under budget** — credit-aware tool selection  
3. **Multi-source fusion** — Context.dev + Monid + LLM synthesis  
4. **Sub-agents** — resolver as shared tool  
5. **MCP Code Mode** — composed perception in one call  

See `agents/research_scout_loop.py` for a minimal runnable loop implementing #3 (Call Prep pattern).