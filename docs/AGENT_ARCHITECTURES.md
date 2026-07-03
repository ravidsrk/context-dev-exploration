# Agent Architectures on Context.dev

This document is **not** a use-case catalog. It is a reasoning layer: what kinds of autonomous agents become possible when Context.dev is the perception substrate, how those agents loop, where Monid fills gaps Context.dev cannot cover, and why building the same thing yourself is a trap.

---

## The core thesis

Most agents fail at **grounding**, not reasoning. They hallucinate company facts, scrape broken HTML, maintain Puppeteer farms, and burn tokens cleaning markdown. Context.dev collapses that entire layer into typed JSON from arbitrary identifiers (domain, email, ticker, transaction string, URL).

**Context.dev is best understood as an agent perception API**, not a "brand API." The brand endpoints are one slice of a broader primitive set:

| Primitive | Agent cognitive role |
|-----------|---------------------|
| `brand.retrieve*` | Entity resolution → world model |
| `web.scrape` / `crawl` | Episodic memory ingestion |
| `web.extract(schema)` | Structured tool output (no parser code) |
| `web.search` | Active perception / research |
| `industry.*` | Taxonomy routing & compliance segmentation |
| `transaction_identifier` | Financial entity resolution |
| `extract_styleguide` / `fonts` / `screenshot` | Environment theming for UI agents |
| `utility.prefetch` | Latency shaping for interactive loops |
| Logo Link CDN | Zero-cost visual grounding in UIs |

The hosted MCP server's **Code Mode** ([install-mcp](https://docs.context.dev/install-mcp.md)) changes the architecture again: instead of 20 single-purpose tools, the agent gets `search_docs` + `execute` and writes TypeScript that composes multiple SDK calls in one sandboxed invocation. That means **multi-step perception can be one tool round-trip** — critical for token-budget and latency in agent loops.

---

## Why Context.dev beats DIY scraping (reasoning, not marketing)

| DIY approach | Hidden cost | Context.dev alternative |
|--------------|-------------|-------------------------|
| Puppeteer/Playwright per site | Ops, CAPTCHA, layout drift | `web.scrape` / `crawl` with proxy+stealth included |
| Cheerio + custom selectors | Breaks on redesign; N parsers for N sites | `web.extract` with JSON Schema — one interface |
| Logo favicon hacks | Wrong aspect, missing dark mode | `brand.retrieve` + Logo Link CDN |
| Clearbit/Brandfetch + scraper + classifier | 3 vendors, 3 auth flows | Single API key, unified types |
| Transaction string → merchant | Proprietary MCC tables, stale mappings | 50M+ merchant map via `transaction_identifier` |
| "Get company from email" | DNS MX guessing, LinkedIn scraping | `brand.retrieve-by-email` |
| Design tokens from site | Manual inspection or headless CSS walk | `extract_styleguide` in one call |
| Agent with 15 MCP tools | Context window eaten by tool defs | Code Mode: 2 tools, arbitrary composition |

**When DIY still wins:** You need sub-second real-time social feeds, private authenticated pages, or bespoke DOM logic on a single site you control. Context.dev is optimized for **cross-domain, cross-tenant** perception at scale.

**When Monid layers on top:** Real-time LinkedIn posts, job velocity, tech-stack fingerprinting, news sentiment, Twitter mentions — signals Context.dev does not emit. See [MONID_DEEP_RESEARCH.md](MONID_DEEP_RESEARCH.md).

---

## The agent loop pattern

Every archetype below follows the same skeleton:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  PERCEIVE   │ ──► │    PLAN     │ ──► │     ACT     │ ──► │   OBSERVE   │
│ (Context.dev│     │ (LLM policy)│     │ (tools/APIs)│     │ (verify +   │
│  + Monid)   │     │             │     │             │     │  memory)    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       ▲                                                          │
       └──────────────────────────────────────────────────────────┘
```

**Perceive** = resolve entities and pull structured facts.  
**Plan** = decide next tool call given goal + memory.  
**Act** = write CRM row, send email, generate asset, file ticket.  
**Observe** = diff against prior state, score confidence, update memory.

Context.dev dominates **Perceive** and parts of **Observe** (sitemap diff, crawl snapshots). Monid extends **Perceive** into social/temporal dimensions.

---

## Archetype 1: Research Scout Agent

**Goal:** Given a company name or domain, produce a living intelligence brief.

**Loop:**
1. **Perceive:** `brand.retrieve(domain)` → title, description, socials, industries, links
2. **Perceive:** `web.scrape(markdown)` on pricing/docs URLs from `brand.links`
3. **Perceive (Monid):** LinkedIn posts + job search → hiring velocity, messaging themes
4. **Plan:** Identify gaps (no pricing page? stale blog?)
5. **Act:** Write brief to Notion/Slack; queue human review if confidence low
6. **Observe:** Store hash of markdown; next run diffs via crawl

**Why Context.dev:** One domain input unlocks logo, industry codes, and link graph without orchestrating 4 APIs.  
**Monid gap-fill:** Employee count, recent posts, open roles (live run: 5 Stripe PM roles in past month, $0.0015).  
**Credit budget:** ~12–25 credits/company (brand + 2 scrapes + optional NAICS).

---

## Archetype 2: Entity Resolution / Enrichment Agent

**Goal:** Turn messy identifiers into a canonical company record.

**Inputs:** work email, ticker, ISIN, raw transaction string, company name.

**Loop:**
1. **Perceive:** Route to correct `brand.retrieve*` variant
2. **Perceive:** `industry.retrieve_naics` + `retrieve_sic` for compliance tags
3. **Perceive (Monid):** `company-tech-stack` to validate domain is active SaaS
4. **Plan:** Merge fields; resolve conflicts (LinkedIn name vs brand title)
5. **Act:** Upsert CRM / data warehouse
6. **Observe:** Track enrichment coverage %; re-queue failures

**Why not DIY:** Transaction enrichment alone requires merchant databases most teams don't have. Context.dev ships 50M+ mappings.  
**Agent insight:** This is the **hub agent** other agents call — build it once as a sub-agent tool.

---

## Archetype 3: RAG Ingestion & Curator Agent

**Goal:** Keep a vector index fresh from customer/competitor websites.

**Loop:**
1. **Perceive:** `web.scrape_sitemap` → URL frontier (Stripe: 6,165 URLs)
2. **Plan:** Rank URLs (docs > blog > careers); cap crawl budget
3. **Perceive:** `web.crawl` or per-page `scrape` → clean markdown
4. **Act:** Chunk, embed, upsert vector DB
5. **Observe:** Compare sitemap cardinality; alert on new paths

**Why Context.dev:** Markdown is LLM-ready; no html2text pipeline. Crawl includes stealth.  
**Novel twist:** Use `web.search` with domain filter as **active perception** when sitemap is incomplete.  
**Cost control:** 1 credit/page crawl; agent must plan page budgets explicitly.

---

## Archetype 4: Structured Extraction Agent ("Describe this URL")

**Goal:** Answer typed questions about arbitrary pages without writing parsers.

**Loop:**
1. **Perceive:** User supplies URL + JSON Schema (fields + descriptions)
2. **Perceive:** `web.extract(schema)` → typed JSON
3. **Plan:** If null fields, try alternate URLs from sitemap
4. **Act:** Return tool result to parent agent or DB
5. **Observe:** Validate against JSON Schema; retry with refined descriptions

**Why Context.dev:** Schema-driven extraction is the **universal parser** — comparison pages, directory listings, gov filings.  
**Beats DIY:** You don't maintain per-site XPath when layouts change; you maintain schemas (cheaper).

---

## Archetype 5: Design / White-Label Theming Agent

**Goal:** Generate UI, emails, or PDFs that match a customer's brand.

**Loop:**
1. **Perceive:** `brand.retrieve` → logos, colors
2. **Perceive:** `extract_styleguide` + `extract_fonts` → typography, spacing, shadows
3. **Perceive:** `screenshot` → visual reference for layout fidelity
4. **Plan:** Map tokens to design system (Tailwind, email MJML)
5. **Act:** Render template; Logo Link CDN for `<img>` (free, frontend-safe)
6. **Observe:** Screenshot diff or human rubric score

**Why Context.dev:** Styleguide extraction is 10 credits vs weeks of design tooling integration.  
**MCP Code Mode win:** One `execute` call can chain retrieve → styleguide → filter colors → return token JSON.

---

## Archetype 6: Sales & CRM Copilot Agent

**Goal:** Prep reps before calls; score leads; trigger outreach.

**Loop:**
1. **Perceive:** `brand.retrieve(email)` on inbound lead
2. **Perceive:** `prefetch(domain)` on signup (paid) to hide cold latency
3. **Perceive (Monid):** LinkedIn posts → "they announced X yesterday"
4. **Plan:** Score ICP fit via NAICS + employee signals
5. **Act:** Draft email using brand voice + recent post themes
6. **Observe:** Track reply rate; feed back to scoring weights

**Why Context.dev:** Email→company is a single call; no Clearbit + Hunter + scraper chain.  
**Monid pairing:** Posts give **temporal triggers** static brand data lacks.

---

## Archetype 7: Fintech Spend Intelligence Agent

**Goal:** Turn card feed strings into actionable spend analytics.

**Loop:**
1. **Perceive:** `transaction_identifier` per line item
2. **Perceive:** `industry.retrieve_naics` on resolved domain
3. **Plan:** Aggregate by industry, merchant, confidence tier
4. **Act:** Dashboard update, budget alerts, tax categorization
5. **Observe:** Flag low-confidence resolutions for human review

**Why Context.dev:** Core product strength — merchant map is not replicable without data partnerships.  
**Agent twist:** Sub-agent explains *why* "AMZN MKTP" → Amazon with category code for user trust.

---

## Archetype 8: Competitive Intelligence Watch Agent

**Goal:** Monitor competitor positioning, pricing, and narrative shifts.

**Loop:**
1. **Perceive:** `brand.retrieve` on competitor set → baseline profile
2. **Perceive:** `extract(product)` on pricing URLs
3. **Perceive:** `crawl` limited to /pricing, /changelog, /blog
4. **Perceive (Monid):** `competitor-compare` or `tech-stack-detect` (Stripe → Next.js, React, ElevenLabs chat)
5. **Plan:** Diff markdown hashes week-over-week
6. **Act:** Alert + summary memo
7. **Observe:** Store snapshots; tune crawl scope

**Why Context.dev + Monid:** Context.dev owns **owned-media** changes; Monid owns **positioning analysis** and stack fingerprinting.

---

## Archetype 9: MCP-Native Coding Agent (Meta-Agent)

**Goal:** The agent building your product uses Context.dev as a tool without you wiring endpoints.

**Architecture:**
- MCP hosted at `https://context-dev.stlmcp.com`
- Tools: `search_docs`, `execute` only
- Agent writes TypeScript in sandbox calling `client.brand.retrieve()`, etc.

**Loop:**
1. **Perceive:** User asks "get stripe.com colors and pricing URL"
2. **Plan:** `search_docs` for retrieve + links shape
3. **Act:** `execute` TypeScript composing calls
4. **Observe:** Return filtered JSON (not full brand blob)

**Why this matters:** Tool surface area stays O(1) while capability stays O(all endpoints). This is the **reference architecture** for Context.dev in Cursor/Claude Code — see runnable example in `agents/mcp_style_loop.py`.

---

## Archetype 10: Compliance & Vendor Risk Agent

**Goal:** Classify vendors for SOC2, procurement, or regulatory reporting.

**Loop:**
1. **Perceive:** `brand.retrieve(domain)` + `retrieve_naics` + `retrieve_sic`
2. **Perceive (Monid):** tech stack → data residency hints (CDN, hosting)
3. **Plan:** Map to internal risk rubric
4. **Act:** Fill vendor questionnaire; flag high-risk jurisdictions
5. **Observe:** Annual re-classification on domain change

**Why Context.dev:** NAICS/SIC are first-class, not LLM-guessed industry labels.

---

## Archetype 11: Product Catalog Harvester Agent

**Goal:** Ingest e-commerce or SaaS pricing catalogs.

**Loop:**
1. **Perceive:** `sitemap` → product URL candidates
2. **Perceive:** `extract(product)` per SKU or `extract(products)` batch
3. **Plan:** Deduplicate; handle pagination via crawl
4. **Act:** Normalize to internal product schema
5. **Observe:** Price change detection on re-run

**Credit warning:** Product extraction is 10+ credits; agent must batch and cache aggressively.

---

## Archetype 12: Onboarding Concierge Agent

**Goal:** Zero-friction signup — prefill company, show logo, theme UI instantly.

**Loop:**
1. **Perceive:** On email blur → `retrieve-by-email` or `prefetch_by_email`
2. **Perceive:** Logo Link CDN embed (no API call)
3. **Act:** Prefill form; apply CSS variables from brand colors
4. **Observe:** Track correction rate (user overrides company)

**Latency note:** Cold brand hit ~7s p50; `prefetch` (paid) or optimistic UI required.

---

## Composition: Multi-Agent Systems

Real products combine archetypes:

```
                    ┌──────────────────────┐
                    │  Orchestrator Agent  │
                    └──────────┬───────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
   │ Entity Resolver│   │ Research Scout │   │ Theming Agent │
   │ (Arch 2)       │   │ (Arch 1)       │   │ (Arch 5)      │
   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
           │                   │                   │
           └───────────────────┴───────────────────┘
                               │
                    Context.dev perception layer
                    Monid temporal/social layer
```

**Orchestration patterns:**
- **Resolver as tool:** All agents call enrichment sub-agent first
- **Shared memory:** Vector store from Arch 3 feeds Arch 4 Q&A
- **Event-driven:** Monid post detection triggers Arch 6 outreach

---

## Credit & latency discipline for agents

From [agent-quickstart](https://docs.context.dev/agent-quickstart.md):

| Operation | Credits | Agent implication |
|-----------|---------|-------------------|
| brand retrieve | 10 | Cache 3 months; dedupe by domain |
| scrape markdown | 1 | Prefer over crawl for single pages |
| crawl | 1/page | Hard cap `maxPages` in plan step |
| styleguide | 10 | Run once per customer, not per request |
| search | 1/result | Cap results in plan |
| prefetch | 0 (paid) | Call on signup intent |

Agents should **plan credit spend** before perceive-heavy loops — this is a novel requirement most agent frameworks ignore.

---

## Evidence & runnable code

| Artifact | Path |
|----------|------|
| Python agent loop (research scout) | `agents/research_scout_loop.py` |
| MCP-style composed perception | `agents/mcp_style_loop.py` |
| Python probes | `scripts/run_demos.py` |
| TypeScript probes | `typescript/src/probe.ts` |
| Monid deep runs | `docs/MONID_DEEP_RESEARCH.md` |
| Novel build ideas | `docs/AGENT_OPPORTUNITIES.md` |