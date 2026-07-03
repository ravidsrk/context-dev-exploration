# Classification API Exploration Lane

Industry classification and transaction enrichment.

| Endpoint | Credits | Demo |
|----------|---------|------|
| `/web/naics` | 10 | `scripts/run_demos.py` (stripe.com) |
| `/web/sic` | 10 | Documented in USE_CASES.md |
| `/brand/transaction_identifier` | 10 | `scripts/run_demos.py` |
| EIC (inline) | 0 extra | On every `/brand/retrieve` response |

See `src/context_client.py` for `classify_naics()` and `identify_transaction()`.