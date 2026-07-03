# Why Context.dev Changes What Agents Can Be

This is not a use-case list. It is a **reasoning chain**: what problem agents actually have, what primitives Context.dev provides, how those primitives compose into agent families, where Monid extends the loop, and why MCP Code Mode is an architectural shift—not a feature bullet.

---

## 1. The failure mode most agent builders ignore

Agents do not fail because the LLM is dumb. They fail because **the world model is wrong**.

| Symptom | Root cause | What teams build instead |
|---------|------------|--------------------------|
| "What's Acme Corp's pricing?" → hallucinated tiers | No structured perception of `/pricing` | Custom Playwright per competitor |
| Lead email `jane@acme.io` → wrong company | Weak entity resolution | Clearbit + Hunter + guesswork |
| Card feed `SQ *CAFE 12TH` → user confusion | No merchant graph | Manual MCC tables |
| RAG answers cite stale docs | No observe/diff loop on sitemap | Re-crawl everything weekly |
| White-label UI looks generic | No design token extraction | Designers hand-copy colors |

Context.dev is aimed at **grounding**: turning messy real-world identifiers and URLs into **typed, cacheable facts** an agent can plan over.

That is a different product category than "brand API." Brand endpoints are one resolver in a larger **perception operating system**.

---

## 2. Perception primitives (compose these, don't memorize endpoints)

Think in **cognitive roles**, not REST paths:

```
RESOLVE   — messy id → canonical company record
INGEST    — URL frontier → clean markdown episodes
EXTRACT   — question + JSON Schema → typed answer (no XPath)
CLASSIFY  — domain → NAICS / SIC / EIC (compliance routing)
THEME     — domain → logos, colors, fonts, screenshots
SEARCH    — query → ranked URLs (active perception)
PREFETCH  — hide 7s cold latency on known intent
```

**Composition law:** Almost every valuable agent is `RESOLVE → (CLASSIFY | THEME | INGEST | EXTRACT)* → ACT → OBSERVE`.

Official docs show six recipes. The platform supports **any loop where step one is "what is this thing in the real world?"**

---

## 3. MCP Code Mode is not "another integration path"

Context.dev's hosted MCP (`context-dev.stlmcp.com`) exposes **two tools**: `search_docs` and `execute`.

The agent writes TypeScript:

```typescript
async function run(client) {
  const domain = "stripe.com";
  const brand = await client.brand.retrieve({ domain });
  const style = await client.web.extractStyleguide({ domain });
  const sm = await client.web.webScrapeSitemap({ domain });
  return { identity: brand.brand?.title, tokens: style.colors, scale: sm.urls?.length };
}
```

**Why this matters (with evidence, not marketing):**

Stainless published evals against the Increase banking API (31 tasks). SDK Code Mode MCP scored **98% completeness** vs **70%** for dynamic per-endpoint tool discovery. Token use does not scale with API surface area—context stays O(1) tools while capability stays O(all endpoints).

Implications for Context.dev agents:

1. **Perception plans can be one round-trip** — brand + styleguide + sitemap in a single `execute`, not three tool calls bloating context.
2. **Agents self-discover API shape** via `search_docs` — you don't ship a 40-tool MCP server.
3. **TypeScript is the native execution language** in the sandbox; Python orchestrators should call hosted `execute` (see `context_dev/loops/mcp_code_mode.py` and `typescript/src/mcp_code_mode_loop.ts`).

This repo runs both paths against the same hosted MCP with live evidence in `evidence/runs/agent-loop.log`.

---

## 4. Agent families (derived from composition, not copied from docs)

### Family A — Entity Graph Agents

**Primitive stack:** `RESOLVE` (domain, email, ticker, ISIN, transaction string, company name)

**Reasoning:** Once you have a canonical domain, every downstream agent shares one hub. Build the resolver once as a **sub-agent tool**; sales, finance, support, and compliance agents all call it.

**Examples beyond docs:**
- Procurement deduplication: match `STRIPE PAYMENTS` txn lines and `Stripe, Inc.` invoices to one domain
- Podcast sponsor resolver: NER on transcript → `retrieve?name=` → Logo Link for show notes
- Marketplace seller verification: claimed brand vs resolved domain vs styleguide screenshot diff

**Moat:** Transaction enrichment (50M+ merchant map) is not rebuildable without data partnerships.

---

### Family B — Episodic Memory Agents (RAG that stays true)

**Primitive stack:** `INGEST` (sitemap → crawl/scrape) + `OBSERVE` (hash/diff)

**Reasoning:** Vector RAG fails when ingestion is brittle. Context.dev returns **LLM-ready markdown** and stealth crawl—your agent's job is **frontier management** (which URLs matter) and **change detection**, not HTML plumbing.

**Examples beyond docs:**
- Competitive pricing watchdog: crawl `/pricing` only, `extract(pricing_schema)`, diff weekly
- Developer docs drift agent: your own sitemap growth + changelog crawl
- Legal exhibit chain: scrape + screenshot + timestamp + content hash for custody
- Insurance FNOL enricher: resolve business → scrape location page → NAICS for vertical model

**Credit discipline:** Crawl is 1 credit/page. Agents must **plan budgets** in the PLAN phase—novel requirement most frameworks skip.

---

### Family C — Schema Interrogation Agents (universal parsers)

**Primitive stack:** `EXTRACT` with JSON Schema field descriptions

**Reasoning:** Maintaining per-site XPath is O(sites). Maintaining schemas is O(questions). When layout changes, you refine field descriptions—not selectors.

**Examples:**
- Directory / "Alternative to" factory at SEO scale
- ESG supplier surveys: extract sustainability fields from heterogeneous pages
- Government filing harvesters: extract structured rows from arbitrary portals
- Product catalog ingesters: `extract(product)` per SKU from sitemap candidates

---

### Family D — Ambient UI Agents (zero-shot white-label)

**Primitive stack:** `THEME` (styleguide, fonts, screenshot) + Logo Link CDN (free, frontend-safe)

**Reasoning:** Multi-tenant products need per-customer visual grounding without a design team per account. Logo Link is **~20ms, no API credits**—critical for edge and email clients.

**Examples:**
- Invoice PDF theming for B2B billing platforms
- Event booth screens: badge company → logo + industry in <1s with `prefetch`
- Franchise brand police: styleguide diff vs canonical franchisor domain
- Partner integration pages: detect stack (Monid) + theme code blocks to their tokens

---

### Family E — Financial Perception Agents

**Primitive stack:** `RESOLVE(transaction)` + `CLASSIFY` + narrative ACT

**Reasoning:** Users don't trust categorization they can't explain. Sub-agent narrates *why* `AMZN MKTP` → Amazon with NAICS code.

**Examples:**
- Merchant dispute explainer (neobank trust UX)
- Spend analytics by industry with confidence tiers
- Tax categorization with low-confidence human queue

---

### Family F — Temporal Intelligence Agents (Context.dev + Monid)

**Primitive stack:** Context.dev static layer + Monid velocity layer

Context.dev answers **what** and **what's on their site**. Monid answers **what changed recently** and **how they operate**.

| Signal | Monid endpoint (discover) | Cost | Agent use |
|--------|---------------------------|------|-----------|
| Hiring velocity | TikHub `search_jobs` | $0.0015 | Expansion / layoff risk |
| Social narrative | TikHub `get_company_posts` | $0.0015 | Sales triggers |
| Tech stack | Strale `company-tech-stack` | $0.011 | Integration / vendor risk |
| Domain age | Strale `domain-age-check` | $0.011 | Fraud / phishing |
| Email deliverability | Strale `email-deliverability-check` | $0.011 | Lead quality gate |
| SEC / public co | Strale `us-company-data` | $0.011 | Compliance (degrade on 500) |
| Pricing structure | Strale `pricing-page-extract` | $0.36 | When extract schema insufficient |
| Positioning compare | Strale `competitor-compare` | $1.19 | Strategic memo, not per-lead |

**Production rule:** Temporal agents need **graceful degradation** (Akta news and SEC EDGAR returned 500 in our live runs—fallback to `web.search`, Exa, or retry queue).

---

### Family G — Meta-Agents (agents that build agents)

**Primitive stack:** MCP `search_docs` + `execute`

**Reasoning:** Your product agent shouldn't hardcode Context.dev endpoints. It discovers docs and composes calls in sandbox—same pattern Stainless evals show winning for complex APIs.

Runnable in **Python** (`context_dev/loops/mcp_code_mode.py`) and **TypeScript** (`typescript/src/mcp_code_mode_loop.ts`).

---

## 5. Multi-agent topologies (where it gets "much bigger")

Single-loop agents are demos. Production systems combine families:

```
                    ┌─────────────────────┐
                    │   Orchestrator      │
                    │ (goal decomposition)│
                    └──────────┬──────────┘
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
  │  Resolver   │      │  Curator    │      │  Sentinel   │
  │  Family A   │      │  Family B   │      │  Family B   │
  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
              Context.dev perception + Monid temporal
```

**Orchestration patterns:**

1. **Resolver-as-tool** — every workflow starts with canonical domain
2. **Shared vector memory** — Curator ingests; Interrogator answers from same index
3. **Event-driven outreach** — Monid post/job spike → Sales agent ACT
4. **Credit-aware planner** — Orchestrator assigns per-sub-agent credit budgets
5. **Human-in-the-loop gates** — low-confidence txn resolution or ESG extract nulls

---

## 6. Verticals unlocked (not in official guides)

| Vertical | Agent story | Primitive mix |
|----------|-------------|---------------|
| Neobanking | Explain every txn line | Family E |
| Procurement / SOC2 | Vendor questionnaires from domain + stack | A + F + C |
| Private equity | M&A screen: NAICS + jobs + news + crawl | A + B + F |
| DevTools / DevRel | Partner readiness + docs drift | D + G + B |
| Insurance | FNOL business resolve + classify | A + C |
| Legal tech | Exhibit builder with chain of custody | B |
| HR tech | Layoff early warning (jobs + careers crawl) | F + B |
| Programmatic SEO | Comparison pages at scale with verified logos | C + D |
| Fraud / trust | Domain age + email rep + brand mismatch | F + A |
| Media | Sponsor extraction → resolve → assets | A + D |

---

## 7. Python vs TypeScript — when to use which

| Layer | Python | TypeScript |
|-------|--------|------------|
| LLM orchestration, CRM, data warehouse | Primary | — |
| MCP Code Mode `execute` sandbox | Call hosted MCP | Native codegen target |
| Edge / signup prefetch / Logo Link UI | — | Primary |
| Long-running scout loops | `research_scout_loop.py` | `scout_loop.ts` |
| Tests & codegen | pytest + mocks | probe + npm scripts |

**Both languages should share the same perception contract:** hosted MCP for multi-step `execute`, direct SDK for simple probes.

---

## 8. What Context.dev does *not* solve (honest bounds)

- Authenticated / logged-in pages
- Sub-second social firehoses (use Monid)
- Private databases you already own
- Fine-grained DOM on one page you control forever (maybe DIY)
- Guaranteed news/SEC uptime (degrade gracefully)

Agents that need these must **plan fallbacks** in the OBSERVE phase.

---

## 9. How to read the rest of this repo

| Doc | Purpose |
|-----|---------|
| **This file** | Reasoning framework — start here |
| `AGENT_ARCHITECTURES.md` | 12 archetypes with loop diagrams |
| `AGENT_OPPORTUNITIES.md` | 20 concrete builds with cost notes |
| `MONID_DEEP_RESEARCH.md` | Temporal layer evidence |
| `agents/*.py` + `typescript/src/*` | Runnable loops, both languages |
| `evidence/runs/agent-loop.log` | Live hosted MCP execute proof |

---

## 10. One-sentence thesis

**Context.dev lets you treat the public web and messy identifiers as a typed sensorium; MCP Code Mode lets agents write their own perception programs; Monid adds time. Together they turn "enrichment" into composable agent cognition—not a CRM field populate.**