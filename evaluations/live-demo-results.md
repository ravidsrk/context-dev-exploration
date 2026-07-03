# Live API Demo Results

Captured from `scripts/run_demos.py` on 2026-07-03. All 11 product surfaces exercised.

## Endpoints Probed

| Demo | Endpoint | Key Result |
|------|----------|------------|
| Prefetch | `utility.prefetch` | status: ok (0 credits) |
| Brand Retrieve | `/brand/retrieve` | Stripe + logo URL |
| Scrape Markdown | `/web/scrape/markdown` | 21,554 chars |
| Sitemap | `/web/scrape/sitemap` | 6,165 URLs discovered |
| Crawl | `/web/crawl` (max_pages=2) | num_succeeded: 2 |
| Transaction | `/brand/transaction_identifier` | Starbucks → starbucks.com |
| NAICS | `/web/naics` | 522320 (high) |
| SIC | `/web/sic` | 6199 FINANCE SERVICES (high) |
| Fonts | `web.extract_fonts` | sohne-var |
| Styleguide | `web.extract_styleguide` | 3 colors, typography present |
| Screenshot | `web.screenshot` | PNG URL returned |

## Credits Consumed (approximate per full run)
- Prefetch: 0
- Brand retrieve: 10 (cached)
- Scrape markdown: 1
- Sitemap: 1
- Crawl (2 pages): 2
- Transaction: 10
- NAICS: 10
- SIC: 10
- Fonts: 5
- Styleguide: 50
- Screenshot: 5
- **Total: ~104 credits per full demo run**