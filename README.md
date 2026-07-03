# Context.dev Exploration

Deep evaluation of [Context.dev](https://context.dev) APIs, use-cases, and build opportunities.

## What this repo contains

- **Live API demos** — Brand lookup, web scrape, and classification/transaction enrichment
- **Use-case catalog** — Every product surface from docs.context.dev plus derived build ideas
- **Evaluation matrix** — Feasibility, credit cost, and production readiness scores
- **Monid research** — How external intelligence tools complement Context.dev

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export CONTEXT_DEV_API_KEY="ctxt_secret_..."
make test          # unit tests (mocked)
make demos         # live API probes
./scripts/verify.sh  # full verification (2 demo runs)
```

## API categories

| Category | Key endpoints | Credits |
|----------|---------------|---------|
| Brand APIs | `/brand/retrieve`, `/brand/transaction_identifier` | 10 |
| Logo Link CDN | `logos.context.dev/?domain=` | Free (10K/mo) |
| Web APIs | `/web/scrape/markdown`, `/web/crawl`, `/web/extract` | 1–50+ |
| Classification | `/web/naics`, `/web/sic` | 10 |

## Documentation

- [Doc Index](docs/DOC_INDEX.md) — All pages from docs.context.dev
- [Use Cases](docs/USE_CASES.md) — Official + derived build ideas
- [Evaluation](docs/EVALUATION.md) — Feasibility matrix
- [Recommendations](docs/RECOMMENDATIONS.md) — Top build candidates
- [Monid Research](docs/MONID_RESEARCH.md) — External intelligence pairing

## License

MIT