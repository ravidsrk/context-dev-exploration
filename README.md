# Context.dev Exploration

Deep evaluation of [Context.dev](https://context.dev) APIs, use-cases, and build opportunities.

Repository: https://github.com/ravidsrk/context-dev-exploration

## What this repo contains

- **Agent architectures** — 12 archetypes with perceive→plan→act→observe loops and reasoning (not a docs dump)
- **Agent opportunities** — 20 novel agent-powered builds beyond official use-case guides
- **Dual-language probes** — Python (`scripts/run_demos.py`) + TypeScript (`typescript/src/probe.ts`)
- **Runnable agent loops** — `agents/research_scout_loop.py` (LLM plan), `agents/mcp_code_mode_loop.py` (search_docs + execute)
- **Live API demos** — Brand, web, classification, design extraction, transaction enrichment
- **Monid deep research** — Temporal/social signals that extend Context.dev agents

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export CONTEXT_DEV_API_KEY="ctxt_secret_..."
make test          # unit tests (mocked)
make demos         # live API probes (Python)
./scripts/verify.sh  # full verification (2 demo runs)

# TypeScript probes + agent loops
cd typescript && npm install && npm run probe
npm run scout-loop -- stripe.com
npm run mcp-code-mode -- "Get stripe.com brand identity, design tokens, and site scale"

# Full dual-language agent loops (Python + TS, hosted MCP execute)
./scripts/run_agent_loops.sh stripe.com
./scripts/run_dual_lang_probes.sh
```

## API categories

| Category | Key endpoints | Credits |
|----------|---------------|---------|
| Brand APIs | `/brand/retrieve`, `/brand/transaction_identifier` | 10 |
| Logo Link CDN | `logos.context.dev/?domain=` | Free (10K/mo) |
| Web APIs | `/web/scrape/markdown`, `/web/crawl`, `/web/extract` | 1–50+ |
| Classification | `/web/naics`, `/web/sic` | 10 |

## Documentation

- [Agent Architectures](docs/AGENT_ARCHITECTURES.md) — **Start here** for what agents you can build and why
- [Agent Opportunities](docs/AGENT_OPPORTUNITIES.md) — 20 reasoned build ideas with cost notes
- [Monid Deep Research](docs/MONID_DEEP_RESEARCH.md) — Agent combo architectures + live runs
- [Doc Index](docs/DOC_INDEX.md) — All pages from docs.context.dev
- [Use Cases](docs/USE_CASES.md) — API surface catalog
- [Evaluation](docs/EVALUATION.md) — Feasibility matrix
- [Recommendations](docs/RECOMMENDATIONS.md) — Top build candidates
- [Monid Research](docs/MONID_RESEARCH.md) — Phase 1 pairing notes

## License

MIT