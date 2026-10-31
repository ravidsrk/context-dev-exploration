# Docs coverage audit, 2026-10-31

`scripts/run/docs_audit.py` makes one small live call per feature on docs.context.dev
that the capability tour and latest-features probes didn't cover. Evidence:
`evidence/runs/docs-audit-2026-10-31.json` (large strings trimmed).

| Probe | Endpoint / option | Result | Credits |
|---|---|---|---|
| custom_parser | scrape `parse` + CSS rules, news.ycombinator.com | 30 stories {title,url}; cache hit 50 h old | 1 |
| parser_emails | prebuilt `emails`, python.org/about/help | 3 addresses | 1 |
| parser_links | prebuilt `links`, docs intro | 52 links | 1 |
| youtube | scrape markdown, "Me at the zoo" | title, channel, views, timestamped transcript | 1 |
| screenshot_images_meta | screenshot viewport + images, linear.app | base64 screenshot, 111 image URLs | 1 |
| browser_actions | `perform` "Click the More link" + wait | landed on ?p=2, 8.2 s | 2 |
| country_fresh | country DE, maxAgeMs 0, highlights | 1 weak passage ("Shop iPhone") | 2 |
| pdf_scrape | arXiv 1706.03762 highlights | abstract passage, 0.9 s (cache hit) | 2 |
| bytes | favicon.ico | contentType + base64 | 1 |
| map_regex | urlRegex prebuilt-parsers | 21 URLs | 1 |
| search_filters | includeDomains + freshness last_month | 5 results; `month` rejected (400, free) | 1 |
| answers_ultra | Developer plan price | $20 / 10,000 credits, source /pricing, 5.1 s | 100 |
| brand_name / email / ticker / url | by_name Linear, by_email vercel, by_ticker AAPL, by_direct_url | linear.app, vercel.com, apple.com, stripe.com | 40 |
| brand_autocomplete | query "lin" | 10 candidates, linkedin.com first | 1 |
| styleguide | linear.app | dark mode, accent #7170ff, Inter Variable 72px h1 | 10 |
| prefetch | brand posthog.com | queued | 0 |
| people_enrich | Patrick Collison @ stripe.com | candidate, score 98; bio was filler text | 20 |
| monitor_sitemap | sitemap target, /changelog* | baseline in 0.3 s, 1 credit, then deleted | 1 |
| usage, usage_history, logs, monitor_limits, webhook_deliveries | account APIs | all 200, 0 credits | 0 |

Total: 186 credits.
