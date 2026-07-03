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