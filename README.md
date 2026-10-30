# Context.dev Exploration

Deep evaluation of [Context.dev](https://context.dev) APIs, agent architectures, and build opportunities.

Repository: https://github.com/ravidsrk/context-dev-exploration

## What this repo contains

- **Agent reasoning** — why Context.dev is a perception substrate, not a brand API
- **12 agent archetypes** — perceive→plan→act→observe loops with cost notes
- **20 build opportunities** — reasoned agent-powered products beyond official guides
- **Dual-language probes** — Python (`scripts/run/demos.py`) + TypeScript (`typescript/src/probe.ts`)
- **Runnable agent loops** — scout + MCP code-mode (Python and TypeScript executors)
- **Monid research** — temporal/social signals that extend Context.dev agents

## Repository layout

```
context-dev-exploration/
├── context_dev/           # Python package (client, loops, MCP, planning)
│   ├── client.py
│   ├── loops/             # scout + mcp_code_mode entry points
│   ├── mcp/               # hosted MCP client, codegen, op map
│   ├── planning/          # shared LLM planner (Python + TS bridge)
│   └── data/              # SDK doc index for local search_docs fallback
├── typescript/src/        # TS probes, loops, plan_cli bridge
├── scripts/
│   ├── lib/               # shared env setup
│   ├── run/               # demos, agent loops, dual-lang probes
│   ├── verify/            # full verification + evidence validator
│   └── capture/           # Monid evidence capture
├── docs/                  # reasoning, agents, research, reference
├── tests/
├── fixtures/              # recorded API samples
└── evidence/              # live run logs (runs/, monid/)
```

## October 2026 update

The July code was written against `context.dev` 1.x (Python) and 0.1.x (TypeScript). By October, 4 of the 11 Python SDK methods it called were gone, the Stainless-hosted MCP URL returned HTTP 525, and the mocked unit tests still passed. This branch migrates both SDKs, switches the tests to autospecced mocks so drift fails loudly, and adds probes for features shipped since July.

- [What changed since July](docs/reference/WHAT_CHANGED.md): the drift, the fix, and the July pricing-check bug
- [Latest features](docs/reference/LATEST_FEATURES.md): feature inventory Jul 3 to Oct 28, 2026, with real probe output
- Evidence: `evidence/runs/*-2026-10-30.*`

```bash
make sdk-compat   # offline: checks every SDK method this repo calls still exists
make latest       # live: ~40 credits across 10 new-feature probes
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export CONTEXT_DEV_API_KEY="ctxt_secret_..."

make test              # unit tests (mocked)
make demos             # live API probes (Python)
make verify            # full verification (tests + probes + agent loops)

# TypeScript probes + agent loops
cd typescript && npm install && npm run probe
npm run scout-loop -- stripe.com
npm run mcp-code-mode -- "Get stripe.com brand identity, design tokens, and site scale"

# Agent loops (Python + TS, hosted MCP execute) + evidence validation
make agent-loops
make dual-lang
```

Optional: `export OPEN_ROUTER_KEY=...` for LLM planning; `export MONID_API_KEY=...` for Monid capture in `make verify`.

## Documentation

See [docs/README.md](docs/README.md) for the full map. Start here:

- [Agent Reasoning](docs/start-here/AGENT_REASONING.md) — perception OS thesis
- [Agent Architectures](docs/agents/AGENT_ARCHITECTURES.md) — 12 archetypes
- [Agent Opportunities](docs/agents/AGENT_OPPORTUNITIES.md) — 20 build ideas
- [Monid Deep Research](docs/research/MONID_DEEP_RESEARCH.md) — combo architectures + live runs

Reference catalog: [USE_CASES](docs/reference/USE_CASES.md), [DOC_INDEX](docs/reference/DOC_INDEX.md), [EVALUATION](docs/reference/EVALUATION.md), [RECOMMENDATIONS](docs/reference/RECOMMENDATIONS.md).

## License

MIT