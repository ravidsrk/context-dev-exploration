# Latest Context.dev features (Jul to Oct 2026)

Live probes were run on 2026-10-30 at 11:11 IST (05:41 UTC) with `make latest` (Python SDK 2.41.1). Raw output: `evidence/runs/latest-features-2026-10-30.json`, plus `latest-features-followups-2026-10-30.txt`. The 10 probes reported 28 credits consumed in total.

## Probed features and what came back

**Scrape highlights (Sep 23).** `web.scrape(url="https://stripe.com/pricing", formats={"highlights": True}, highlights_params={"query": ...})` returned one passage: "Standard 2.9% + 30¢ per successful transaction for domestic cards … Pix and UPI 1.8% + 30¢ … Tax Basic … Starting at $0.05". The full Markdown for the same page is 60,562 characters. Cost: 2 credits. Cache status: hit. Time: 541 ms.

**Map with search (Aug 6).** `web.map_urls(domain="stripe.com", search="pricing and fees")` returned these ranked URLs:
- https://stripe.com/pricing (Pricing & Fees)
- https://stripe.com/blog/adaptive-pricing-for-subscriptions (Testing the impact of Adaptive Pricing across 1.5M subscription checkout sessions)
- https://stripe.com/billing/pricing (Stripe Billing | Pricing)
- https://stripe.com/connect/pricing (Pricing information | Stripe Connect)
- https://stripe.com/sigma/pricing (Stripe Sigma | Pricing and Fees)

Cost: 2 credits. Time: 5.7 s. Unfiltered Map for the same domain returns 7,160 URLs.

**Brand by transaction (unified retrieve, Jul 5).** `"STARBUCKS STORE 12345"` with MCC 5814 resolved to Starbucks / starbucks.com. Cost: 10 credits.

**Brand search (Aug 4).** `"linear"` returned linear.app, linear.com (Linear Technology), linearity.io, linearair.com and thomsonlinear.com. Cost: 1 credit. Time: 206 ms.

**Company search (Oct 21).** "Developer tools companies that sell a web scraping API" returned WebScraping.AI, WebScrapingAPI, Edge Scraper, ScraperAPI and Scrape.do. Cost: 2 credits. The SDK has no method for this yet, so the probe calls `client.post`.

**People search (Oct 23).** "Heads of developer relations at API companies in India" returned 0 results and was not charged. "VPs of engineering at fintech companies" returned 10 results for 10 credits. Names and profile URLs are dropped before anything is saved.

**News, natural language (Oct 18).** "web scraping API funding" with no date filter returned a 2020 Luminati review and a 2022 Bright Data review as its top hits. Asking for newest-first returned `400 INPUT_VALIDATION_ERROR: Natural-language searches are ordered by relevance only.` and was not charged. Adding `filter_by.date.from = 2026-09-01` fixed it: the top two hits were a 2026-10-16 article on scraping brands consolidating under a $3.6B umbrella and "Web scraping startup Firecrawl closes $75M investment" (2026-09-22). Cost: 1 credit.

**Answers, fast (Sep 12; sources Oct 4).** The task was "monthly price and included credits of each Context.dev self-serve plan" with a JSON schema. It returned Free $0 / 1,000 credits and Developer **$25** / 10,000 credits, with `null` for Pro, Growth and Scale. The source was context.dev/pricing, `partial` was null, and it cost 10 credits. The live pricing page says Developer is **$20/mo**, Pro $90, Growth $300 and Scale $500. The answer was wrong on one field and empty on three, and nothing in the response flagged either problem.

**Batch (Jul 30, 100K on Oct 15).** Two docs URLs were queued, and `batch.retrieve` later showed `completed` with credits net=2, reserved=2, refunded=0.

**Semantic monitor (Jul 9 / Jul 27).** A page monitor on stripe.com/pricing with the instruction "Alert only when a listed price, fee or plan changes" was created (status `active`, with an initial run id) and deleted in the same probe.

## Not probed (paid-plan, write-heavy, or out of scope)

Authenticated browser profiles (Oct 13), browser actions (Jul 22), prebuilt parsers for Google Maps, app stores, Instagram, G2 and TikTok (Oct 14 to 17), Parse for PDFs and bytes, access policies (Oct 28), webhooks and replay, and ultra-mode Answers and People search (100 and 50 credits).

## Full inventory from the changelog

- 2026-10-28 | Access policies | Control which websites your API requests can reach. An [access policy] is an allowlist or a blocklist of domains. Each domain includes its subdomains, and `*.gov` covers a whole extension. List policy IDs in the new `policies` param on Scrape, Crawl, Map, Search, Answers, News, Brand, Styleguide, Fo
- 2026-10-27 | Ultra mode for People Search | Set `mode: "ultra"` on [People Search] for detailed requests that combine several criteria. Ultra plans a deeper search, judges each candidate against every criterion in your query, and returns a `match.confidence` score from 0 to 1 with each person. Ultra accepts queries up to 5,000 characters and 
- 2026-10-27 | Page numbers in PDF Markdown | Set `includeNumberedPages` to start each PDF page in the Markdown with a `<!-- page N -->` line that uses the page's original number, so you can cite pages or split a document by page. Use `includeNumberedPages=true` on [Parse], or `sharedParams.parsers.pdf.includeNumberedPages` on [Scrape] and batc
- 2026-10-26 | Exact phrases in People, Company, and News search | Put a phrase in double quotes to require it word for word in [People Search], [Company Search], and natural-language [News Search]. Join quoted phrases with `OR` to accept either one, as in `"payroll" OR "invoicing"`, and put `-` before a quoted phrase to exclude it. 
- 2026-10-23 | People Search | [Search people] with a natural-language query, such as "VPs of sales at solar companies in California", and get up to 10 people per page with their current role and employer, location, experience, skills, schools, and profile links. Narrow results by country and years of experience, and page through
- 2026-10-23 | New self-serve plans | 
- 2026-10-21 | Company search | [Search companies] with a natural-language query and get each company's identity, headquarters, and headcount, with pagination. Each request costs **2 credits**; requests with no results are free. 
- 2026-10-21 | Research papers in Search | [Search] now includes indexed research papers for research-style queries. Papers are skipped when domain filters are set. 
- 2026-10-21 | Longer News descriptions | Natural-language [News] results now return extended descriptions, combining the publisher's summary with snippets that matched your query, up to 2,000 characters. 
- 2026-10-21 | Choose where Markdown comes from | Many docs sites publish a Markdown version of each page. Set `markdownParams.sourcePreference` on [Scrape] and [batches], or `sourcePreference` on [Crawl], to rank `html-conversion` and `markdown-direct`. The first usable source wins. 
- 2026-10-21 | Follow only chosen languages in batch crawls | Set `controls.languages` on a [start-URL batch crawl] to `same_as_start_url` or a list such as `["en"]`, so translated copies of a site don't use up `maxUrls`. Links whose language can't be determined are still followed. 
- 2026-10-20 | No per-minute limit on Free | New Free organizations no longer have a per-minute limit; the **2 concurrent requests** limit still applies. Existing and custom allowances are unchanged. See [Rate limits]. 
- 2026-10-20 | Fewer rate-limit digests | The daily [rate-limit digest] is now sent only when more than 20% of your organization's requests in the past 24 hours were rate-limited, up from 5%. 
- 2026-10-19 | Exclude URLs from crawls and site map discovery | Skip URLs with an exclude pattern: A URL that matches the exclude pattern is skipped even when it matches the include pattern, so you can drop sections such as `/blog/`. The start URL is always scraped. 
- 2026-10-18 | Natural-language News search | Ask [News] in plain words, like "chip export restrictions to China", with `searchBy: { type: "natural_language", query }` and get up to **100 matching articles** ranked by relevance. Every News filter still applies, and the playground now opens on natural-language search. 
- 2026-10-18 | Credit exhaustion returns 402 | Authenticated requests rejected for insufficient credits now return **402 USAGE\_EXCEEDED**, including batch reservation failures. Previously these failures returned **401 USAGE\_EXCEEDED**. The error code and envelope fields are unchanged; clients that checked for 401 should handle 402. The public 
- 2026-10-17 | TikTok parsers | Pull TikTok profiles, videos, feeds, comments, followers, and user search results with **seven new [TikTok parsers]**. Use them through Scrape Anything or the playground, without a TikTok login. Video results include a `video_url` you can download directly. 
- 2026-10-17 | People Enrich on every plan | [People Enrich] now works on every plan, including Free, so you can match a person from identity clues without upgrading. Pricing stays at 20 credits per match. 
- 2026-10-16 | Instagram parsers | Extract public profiles, posts, reels, and hashtag, keyword, or location feeds with the three new [Instagram parsers]. Use them through Scrape Anything or the playground, without an Instagram login. 
- 2026-10-16 | Google Maps reviews | Extract up to **1,000 reviews** for a place with the [Google Maps reviews parser], in the API or playground. Choose newest, oldest, most relevant, highest-rated, or lowest-rated order; the default is 100 newest reviews. 
- 2026-10-16 | G2 reviews | Extract the **25 most recent reviews** for a product with the [G2 reviews parser], including ratings, reviewer details, likes, dislikes, and problems solved. Use it in the API or playground with optional star-rating filters in the URL; pagination is unavailable. 
- 2026-10-16 | Language filters for Search and News | Set [Search] `languages`, such as `["en", "de"]`, to narrow results by language; the default is `"all"`. Search and [News] language filters support **74 languages**; results whose language cannot be detected remain eligible. 
- 2026-10-16 | Brand search filters and richer results | Filter [Brand search] by `country` and primary `language`, such as `country=US&language=english`; both filters must match when combined. Results now include `description`, `country`, and `language` when available. 
- 2026-10-16 | Daily rate-limit digest | Rate-limit [account emails] now arrive as one daily digest that names each limit you hit and exactly how many requests it rejected. The digest is sent only when more than 5% of your requests in the past 24 hours were rate-limited, so occasional throttling no longer fills your inbox. 
- 2026-10-15 | Scrape Anything batches up to 100,000 URLs | Submit up to **100,000 URLs**, or crawl a site, in one asynchronous [batch]. Combine Markdown, HTML, screenshots, images, bytes, parsers, product data, highlights, and JSON extraction with the same per-page options as [Scrape Anything]. Create jobs and inspect results from the dashboard too. 
- 2026-10-15 | List browser profiles | [`GET /org/browser/profiles`] lists your organization's [browser profiles] with their creation time, newest first. It costs no credits and needs `logs:read`. Add an optional `description` when you create a profile to label it in that list. 
- 2026-10-14 | Updated request limits | New Free organizations receive **2 concurrent requests and 10 requests per minute**. Both limits apply across the organization. Existing allowances are preserved through the rollout and routine renewals. Plan changes apply the new plan's base limits; explicit overrides remain until cleared. The dash
- 2026-10-14 | Eight prebuilt parsers | [Prebuilt parsers] extract Google Maps businesses, Google Play and App Store app details and reviews, emails, phone numbers, and links without custom extraction rules. Set `formats.parse: true`, `parseParams.type: "prebuilt"`, and a parser name, or choose a parser in the playground. 
- 2026-10-14 | Request fewer Search results | [Search] accepts `numResults` from **1–100**, down from a minimum of 10. The default remains 10. 
- 2026-10-13 | Authenticated scraping with browser profiles | [Sign in once and reuse a saved browser session] with `sharedParams.profile` on Scrape Anything. Browser profiles are available on paid plans and belong to your organization. Create and reuse profiles in the playground. Profile requests bypass shared caches and do not support zero data retention. 
- 2026-10-13 | Search understands relative time | When you omit `freshness`, [Search] can infer a publication window from queries such as "today" or "this week". An explicit `freshness` setting takes precedence. 
- 2026-10-08 | Multilingual Map search | [Map search] matches search terms across website languages to find relevant pages even when their content uses a different language from your query. 
- 2026-10-07 | Longer batch result retention | 
- 2026-10-06 | Monthly credits for every Free organization | [Free organizations] receive **1,000 credits monthly**, whether they signed up with a work or personal email. 
- 2026-10-05 | Search description length | Set `descriptionMaxCharacters` on [Search] to cap each result’s `description`. When it is above 0 and the query has no domain or `freshness` filter, news-index results fill that space with the article passages that best match your query. 
- 2026-10-04 | Search page reads | [Search page reads] now default to a 20-second deadline per page, plus any `waitForMs`, instead of 45 seconds. Set `markdownOptions.timeoutOpts` to change it. Pages that serve an anti-bot challenge report `WEBSITE_BLOCKED` on `markdown.code` and `highlights.code`. 
- 2026-10-04 | JSON extraction on long pages | [JSON extraction] now also reads head metadata (description, canonical URL, language, author, keywords, dates), counts JSON-LD and meta tags separately from the Markdown limit, and keeps the sections that best match your schema on long pages. A successful extraction from a page that did not fit incl
- 2026-10-04 | Answers sources and partial answers | [`sources`] lists the pages and company or profile records read for the answer, followed by URLs cited in `json_content`. With `return-partial`, a model error after evidence was gathered returns a partial answer instead of failing. 
- 2026-10-04 | Parse and credit usage | [Parse] returns `400 INPUT_VALIDATION_ERROR` instead of `WEBSITE_ACCESS_ERROR` for an upload it cannot read or that has no extractable content. [`GET /org/usage`] and [`GET /org/usage/history`] return your credit balance and usage over time. They share the request logs rate limit. 
- 2026-09-29 | Product image deduplication | Set `productParams.dedupeImages: true` to [drop visually duplicate product images], keeping the largest copy. Product adds 1 credit, with no other product surcharge. 
- 2026-09-29 | Removed `EXTERNAL_PROVIDER_ERROR` | `EXTERNAL_PROVIDER_ERROR` is no longer returned. Upstream failures return `500 INTERNAL_ERROR` (Answers and People previously returned 502), failed Scrape `json` outputs report `INTERNAL_ERROR`, and Answers time limits return `504 REQUEST_TIMEOUT`. 
- 2026-09-29 | Longer Search cache windows | [Search Markdown] now defaults `maxAgeMs` to 180 days (`15552000000` ms), or 365 days when only highlights are requested. 
- 2026-09-28 | Highlights on Search | [Search] returns passages relevant to your query with `highlightsOptions.enabled`. Each result reports `highlights.code`, like `markdown.code`. Search Markdown and highlights each add 1 credit per 10 results when at least one result returns them. Search Markdown now defaults `maxAgeMs` to 15 days (`
- 2026-09-27 | Concurrency limits | 
- 2026-09-27 | Browser actions on page monitors | 
- 2026-09-27 | Longer scrape cache windows | 
- 2026-09-26 | Answers page caching | [Answers] can reuse cached page reads: up to 30 days old in `fast` and 7 days in `ultra`. 
- 2026-09-26 | Plan changes and account limits | Upgrades take effect immediately and preserve your remaining credits. Downgrades take effect at renewal and can be cancelled beforehand. Review [billing] for plan changes, Auto-Topup, and spend alerts. Rate-limit reminder emails help you identify sustained throttling. Free organizations receive an e
- 2026-09-26 | Agent Feedback | Agents can [report problems] with API calls, documentation, SDKs, or the CLI. Include a category, a short note, and the affected request ID or URL. [Submit feedback] with any API key, at no credit cost. 
- 2026-09-23 | Auto-Topup in smaller blocks | 
- 2026-09-23 | Highlights format on Scrape | [Find the passages most relevant to a question or topic] with `formats.highlights` and `highlightsParams.query`. Set `maxCharacters` to limit the total length. Highlights also work with [zero data retention]. Adds 3 credits only when passages are returned. 
- 2026-09-23 | Extract product data with scrape | [Extract product details] with `formats.product`, including prices, images, and variants. Results identify whether the URL is a product page and include a normalized product record when available. Adds 1 credit. 
- 2026-09-22 | Scrape Anything | [Scrape a page once] for Markdown, HTML, screenshots, images, original bytes, or selected fields. Choose any combination with `formats`. Control freshness with `maxAgeMs`; use `0` to fetch fresh content. Costs 1 credit, or 2 with browser actions, plus 1 per PDF page recovered by OCR. 
- 2026-09-22 | Map website URLs | [Discover a site's URLs] with available titles, descriptions, keywords, and languages. Filter and search the list, include subdomains, or set a maximum number of links. Costs 1 credit, or 2 when using `search`. 
- 2026-09-22 | SDK updates | All five [SDKs] now support Scrape and Map URLs. Replace the old per-format scraping methods with the unified [Scrape] and [Map] methods. Existing HTTP routes keep working. The [CLI] does not yet include these two commands. 
- 2026-09-20 | Bytes with rendering and cache controls | [Download rendered HTML bytes] after a `waitForMs` delay. Other resources keep their original bytes. Downloads are cached for one day by default, up to 30 days. Use `maxAgeMs=0` to fetch fresh content. Requests with credentials or zero data retention bypass caching. 
- 2026-09-20 | Screenshots with custom headers | Send [custom target headers], including authorized cookies, when taking screenshots. Requests with custom headers bypass caching and return an inline PNG data URL. 
- 2026-09-20 | Country routing for page images | Use `country` to [extract page images from a selected region]. The country applies to both the page and its image downloads. 
- 2026-09-18 | SOC 2 Type II compliance | Context.dev is now SOC 2 Type II compliant. Review security policies, subprocessors, and access to compliance evidence in the [Trust Center]. 
- 2026-09-18 | Screenshots from a full URL | Capture a page from its full URL with [`GET /web/scrape/screenshot`], for 1 credit. See the [screenshot guide] for capture options and examples. 
- 2026-09-18 | Extract fields with CSS | Use CSS selectors to return structured fields alongside a page's HTML, with no additional credits. [`extractRules`] supports text, attributes, lists, and nested objects. 
- 2026-09-18 | Zero data retention for AI endpoints | [Zero data retention] now supports Answers, Search, People Enrich, Images, and Styleguide. Enable it for your organization, send `zdr: "enabled"`, and verify `X-Context-ZDR: true` on supported requests. 
- 2026-09-18 | API keys during onboarding | [Onboarding] now picks up newly created API keys without getting stuck waiting. If loading fails, you can retry; setup prompts become copyable once the key is ready. 
- 2026-09-18 | More reliable scraping and API errors | Pages with large response headers can now be scraped. Temporary gateway failures return a JSON `503` response. See [troubleshooting] for recovery guidance. 
- 2026-09-17 | More reliable payments | Fixed duplicate Auto-Topup charges when several requests reach a low balance together. [Plan upgrades] also wait for successful payment, with a clear recovery path when payment fails. 
- 2026-09-17 | Startup and nonprofit program | Eligible startups and registered nonprofits can [apply for 30% off their first year] on a self-serve annual paid plan, with a private Slack Connect channel. Approval is required; overages are excluded, and existing agreements stay unchanged. 
- 2026-09-16 | Reinforcement learning grants | Teams building reinforcement learning systems can now [apply for Context.dev data credits]. The program page explains eligibility and how to submit a research proposal. 
- 2026-09-15 | Timeout controls and partial results | Set a [request deadline] and choose whether to fail or accept partial results with `timeoutOpts`. Partial results are marked with `partial: true` or `finalDOMState: "still-loading"`. Bytes and Prefetch support fail behavior only. **September 16 update:** partial HTML, Markdown, Images, Screenshot, a
- 2026-09-15 | Download raw resource bytes | [Download images, PDFs, HTML, and other resources] as base64, with file size, content type, final URL, and origin status. Supports files up to 20 MiB, custom headers, country targeting, and zero data retention. Costs 1 credit per download. 
- 2026-09-15 | Parse documents up to 50 MiB | [Parse] now accepts uploads up to **50 MiB**, twice the previous limit. Conversion remains 1 credit, plus 1 credit per PDF page recovered by optional OCR. 
- 2026-09-15 | Request logs and search results | [Request logs] redact recognized credentials in request fields, headers, and URLs. [Web Search] results always include a `description` string, empty when no snippet is available. 
- 2026-09-14 | Advanced monitor controls | Focus [page monitors] on specific content with include and exclude selectors. Changing filters starts a new baseline. Empty filtered results fail the run and preserve the previous baseline. The dashboard adds controls for whitespace, webhook retries, and extraction depth. 
- 2026-09-12 | Answers: web research in two modes | [Ask a question about the live web] and receive JSON with source URLs. **Fast:** 10 credits with a 30-second budget. **Ultra:** 100 credits with a 50-second budget. The API defaults to Ultra; the playground defaults to Fast. 
- 2026-09-12 | Restricted API keys and per-key usage | [Restricted API keys] let you grant only the data, log, monitor, and batch access an integration needs. Existing keys keep full access. Search and filter keys, then open their usage charts and request logs from the dashboard. 
- 2026-09-12 | Team roles and deactivation | Manage [Owner, Admin, and Member roles], transfer ownership, and deactivate or reactivate teammates. Deactivation revokes the person's credentials and prevents invitations or domain auto-join from restoring access. 
- 2026-09-12 | Formatted Slack webhook notifications | Send [monitor] and [batch] events directly to Slack or GovSlack for readable messages with resource links. Other webhook destinations continue receiving JSON. 
- 2026-09-12 | More accurate freshness controls | Brand retrieval and Styleguide now honor `maxAgeMs: 0` and values under one day. Set `0` to fetch fresh data. The three-month default and one-year maximum are unchanged. See [Cache freshness]. 
- 2026-09-11 | Updated Free credit allowances | [Free organizations] with a work email now receive **1,000 credits monthly**. Personal-email organizations receive **250 credits once**, without monthly refills. This replaces the September 6 allowance. **Superseded October 6:** see [current Free credits]. 
- 2026-09-11 | Request log endpoints | [Find requests] by time, endpoint, key, status, error, or tags, and [retrieve an individual call]. Responses now include `request_id` and `X-Request-Id` for tracing. Log endpoints cost 0 credits. 
- 2026-09-11 | Better blocked-page detection | Scraping now recognizes more CAPTCHA, login, and access-denied pages, including pages that return HTTP `200`. These return `WEBSITE_BLOCKED` instead of being billed and cached as usable content. Brand cache metadata also reflects the age of the underlying scrape more accurately. 
- 2026-09-08 | Context.dev for Gemini CLI | [Connect Gemini CLI] to search, scrape, extract, parse, and retrieve brand data from the terminal. The official extension uses browser-based OAuth. 
- 2026-09-08 | Context.dev for Composio | [Use Context.dev through Composio] for scraping, extraction, parsing, brand data, batches, and monitors. Connect an API key to make the toolkit available to your agent framework. 
- 2026-09-07 | Context.dev for Replit | [Connect Context.dev to Replit Agent] to search, scrape, and retrieve company data while building your app. 
- 2026-09-07 | Webhook retries, delivery history, and replay | Configure [automatic webhook retries] for batches and monitors with `webhook.retry`. [Replay failed deliveries] for up to seven days, without rerunning the job or spending credits. Inspect 30 days of delivery history and attempts in the dashboard. 
- 2026-09-06 | Monthly API credits for new Free accounts | New Free accounts received monthly allowances of 500 credits with a work email or 250 with a personal email. Refills preserved balances above the allowance. **Superseded September 11:** see [current Free credits]. 
- 2026-09-06 | Higher default monitor limits | [Monitor allowances] increase from 2 to **10** on Free, 50 to **100** on Developer, and 500 to **1,000** on Pro. Scale's default is **10,000** monitors. 
- 2026-09-06 | More reliable brand profiles and SVG logos | [Brand retrieval] handles redirects, placeholder sites, and error pages more accurately. SVG logos now render more reliably outside the original website. 
- 2026-09-06 | Clearer credit counters and dashboard support | [Dashboard counters] distinguish monthly allowances from bonus balances, and Support chat is available after onboarding. Monthly refills also preserve manually granted balances above the allowance. 
- 2026-09-04 | Zapier 3.1 | [Zapier 3.1] adds event triggers and actions across scraping, extraction, batches, monitors, and brand data. Start a Zap from a website change, monitor run, or finished batch. Existing 3.0 Zaps keep running. 
- 2026-09-03 | Downloadable captured font files | Styleguide now returns captured font files through stable CDN URLs in `fontLinks`, so downloads work outside the source website. See [Extract a design system]. 
- 2026-09-03 | More playground languages | The playground's [language selector] now includes all 120 languages supported by the API, plus automatic detection. 
- 2026-09-03 | Better crawls of redirected documentation sites | [Crawl] follows sites that redirect to a dedicated documentation subdomain and continues beyond the first page more reliably. 
- 2026-09-03 | Context.dev on Zapier | Connect Context.dev to your other apps with the [Zapier integration]. The guide includes setup, available actions, and automation recipes. 
- 2026-09-03 | URL mapping can include subdomains | Set `includeSubdomains: true` to [discover URLs] across a domain and its public subdomains. The default remains `false`; the option is also available in the playground. 
- 2026-09-02 | Enterprise SSO on the Scale plan | Scale organizations can [connect an identity provider] from Organization Settings. Owners create a setup link valid for 24 hours. Verified company-domain teammates are routed to the provider at sign-in. Password sign-in remains available. 
- 2026-09-01 | Create additional organizations | Use the [dashboard's organization switcher] to create another organization when every organization you own is on a paid plan. Each has separate members, API keys, and billing. 
- 2026-08-27 | Cache metadata on every cacheable response | [Cacheable responses] now include `cache_metadata` with a `hit`, `miss`, or `zdr` status and `age_ms`, so your application can see how fresh the data is. 
- 2026-08-26 | Context.dev for Claude | [Connect Context.dev to Claude] from the Connectors Directory to search, scrape, crawl, extract, parse, and monitor the web. 
- 2026-08-26 | Dashboard dark mode | Choose light, dark, or system appearance from the [dashboard user menu]. Your preference is remembered across visits. 
- 2026-08-26 | More reliable slow-page scraping | [Slow-loading pages] have more time to finish browser rendering, and repeat scrapes can reuse a working access route for sites with stricter protection. 
- 2026-08-25 | Pause your plan for up to three months | [Pause a paid plan] for one, two, or three months, starting at renewal. Monthly charges, included-credit allocations, and Auto-Topup pause. Existing credits remain usable. Cancel a scheduled pause, or pay to resume early and restore monthly credits. 
- 2026-08-25 | Office documents with incorrect content types | [Word, Excel, and PowerPoint files] served with incorrect content types are now recognized and parsed instead of being treated as webpage HTML. 
- 2026-08-24 | Timestamped YouTube transcripts | [YouTube transcripts] now include timestamps roughly every 30 seconds, making it easier to trace a passage back to the video. 
- 2026-08-24 | Payment alerts and plan status | Organization owners now receive an email when a subscription payment fails, with a link to [update the payment method]. The dashboard also shows scheduled cancellations. 
- 2026-08-24 | Website names in batch lists | [Batch lists] now show each job's target website, making similar jobs easier to distinguish. 
- 2026-08-23 | Scroll pages before scraping | [Browser actions] now support scrolling to load more content before capturing Markdown, HTML, or Images. Scroll controls are also available in the playground. 
- 2026-08-23 | Duplicate monitors in one click | Choose **[Duplicate]** from a monitor's menu to open a new monitor with the same settings. Change the target and save. 
- 2026-08-23 | Email verification survives mail scanners | Verification links now wait for your confirmation, preventing email security scanners from consuming them before you open them. This applies to signup and account-email changes. 
- 2026-08-22 | Logo Link wordmarks | [Logo Link] now accepts `type=wordmark` to prefer wide wordmarks over square icons. Combine it with `theme=light` or `theme=dark`. 
- 2026-08-22 | Richer playground results | [Playground] results now show page metadata, freshness, and browser-action outcomes, with clearer previews for scrape, extract, brand, and parse requests. Parse displays its OCR credit cost before you run it. 
- 2026-08-21 | Context.dev for ChatGPT | [Add Context.dev to ChatGPT] to search, scrape, crawl, extract, parse, and monitor the web from a conversation. 
- 2026-08-20 | Website privacy controls | Choose which analytics cookies to allow through the website's consent controls. Optional analytics wait for your consent. 
- 2026-08-19 | Context.dev for Cursor | [Install the Cursor plugin] to give your coding agent access to Context.dev's web tools. 
- 2026-08-18 | Context.dev for LangChain | Use [LangChain's Context.dev integration] for search, scraping, extraction, parsing, brand data, monitors, and batches. Install the `langchain-context` package to get started. 
- 2026-08-17 | Clear obstructive popups from screenshots | Set `clearPopups=true` to dismiss obstructive banners, popups, and overlays before [taking a screenshot]. 
- 2026-08-17 | Context.dev for OpenClaw | [Connect OpenClaw] for web search and scraping, with optional OAuth access to Context.dev's public MCP tools. 
- 2026-08-17 | Exclude more domains from web search | [Web Search] now accepts up to 100 excluded domains, giving you more control over which sources appear in results. 
- 2026-08-17 | More accurate brand colors, logos, and contacts | [Brand profiles] better match website colors, preserve original logos, and filter placeholder contact emails. Redirects to shared hosting platforms no longer replace the requested company's brand with the platform's. 
- 2026-08-16 | News Search launches in beta | [Find company news] by name, domain, ticker, or ISIN. Filter by publisher, date, article type, language, or country. Successful searches cost 1 credit per 10 returned articles. A successful search with no articles is free. 
- 2026-08-16 | More control over Brand Search matching | [Brand Search] adds `autocomplete`, `queryBy`, and `typoTolerance`. Choose name or domain matching, prefix matching, and tolerance for up to two typos. These controls are also in the playground. 
- 2026-08-14 | Change your account email securely | Change your email from Personal Settings after confirming your identity and verifying the new address. Your previous address receives a notification, and you stay signed in. 
- 2026-08-13 | Context.dev for Eve | [Add Context.dev to Eve] with `eve add connection/context` for search, scraping, extraction, and brand tools. Each user authorizes their account in the browser. 
- 2026-08-12 | Screenshots now cost 1 credit | Screenshot requests now cost **1 credit**. See [Take a screenshot] for capture options and examples. 
- 2026-08-12 | Earn extra credits | Eligible Free accounts with a personal email can [earn bonus credits] by following Context.dev or submitting a public post for review. The dashboard shows the available rewards and submission status. 
- 2026-08-12 | Better text encoding | Pages, feeds, and sitemaps now respect declared character encodings, reducing garbled text on sites that use older encodings. 
- 2026-08-10 | Prefetch styleguides ahead of time | Queue a styleguide with `type: "styleguide"` on [Prefetch] to reduce the wait for a later Styleguide request. Prefetching costs 0 credits. 
- 2026-08-09 | HTML alongside Markdown in one scrape | Set `includeHTML=true` to [return HTML and Markdown together] from one scrape. Markdown batches support the same option, also available in the playground. 
- 2026-08-07 | Page headings and main content | HTML and Markdown responses now include `metadata.headings` in document order for tables of contents and content routing. [Main-content filtering] also preserves the page's `<main>` landmark. 
- 2026-08-06 | People Enrichment API | [Find a person] from a social URL, name and company, or work email, with a 0–100 match score. The beta is available on paid plans and costs 20 credits per successful match. Free and disposable email inputs are rejected without charge. 
- 2026-08-06 | Employee counts on brand data | [Brand profiles] now include `employees` with a headcount range and an exact count when known. Unknown values are `null`. 
- 2026-08-06 | Relevance search for URL mapping | Give [Map URLs] a `search` phrase such as `pricing and plans` to return matching pages in relevance order. Searched requests cost 2 credits instead of 1. 
- 2026-08-06 | Per-page OCR billing and clearer PDF errors | OCR adds 1 credit per recovered PDF page to the 1-credit request cost. [Enable OCR] with `ocr=true` for Parse or `pdf[ocr]=true` for scraping. Image-only PDFs return `PDF_IMAGES_ONLY` when OCR is needed. 
- 2026-08-06 | Clearer timeouts for new brand lookups | A brand lookup on a new domain with a timeout below 10 seconds now returns `422 COLD_DOMAIN_TIMEOUT_TOO_LOW` immediately. Timeout responses suggest [prefetching] the brand before you need it. 
- 2026-08-06 | YouTube pages become structured Markdown | [Scrape a YouTube video or channel] to receive its available metadata and description as structured Markdown. Videos with retrievable captions also include a transcript. 
- 2026-08-05 | More specific scrape errors | [Identify scrape failures] with clearer errors for oversized content, unresolved domains, and intentionally skipped PDFs. Oversized embedded files no longer fail the entire page scrape. 
- 2026-08-05 | Faster repeat scrapes | [Repeat scrapes] of unchanged pages return faster by reusing the previous Markdown conversion. 
- 2026-08-04 | Brand Search for autocomplete | [Find up to 10 matching companies] by name or domain, with logos for autocomplete and lookup forms. At launch, requests are free on Pro and Scale and cost 1 credit on Free and Starter. **August 6 update:** name matches rank first, and Brand Search is available in the playground. 
- 2026-08-03 | Context.dev MCP is live | [Connect your AI client over MCP] to use Context.dev through browser-based OAuth. Setup guides cover Claude, Claude Code, Cursor, Codex, ChatGPT, and VS Code. 
- 2026-08-02 | Usage charts by product | [Dashboard usage charts] now separate All, Data APIs, Monitors, and Batches, so you can track activity by product. 
- 2026-08-02 | Monitors recover from failed runs | [Monitors] recover from temporary scraping failures instead of pausing after one failed run. Resume an already paused monitor by setting its status to `active`. 
- 2026-08-01 | Credit refills on your billing day | [Monthly credits] now refill on your billing day, including monthly allocations on annual plans. Your allowance covers a full cycle from subscription rather than resetting on the first of the calendar month. Auto-Topup preferences are also preserved across plan changes. 
- 2026-07-30 | Batch scraping for up to 25,000 URLs | [Scrape up to 25,000 URLs asynchronously], using a list, a starting page, or a sitemap. Get Markdown or HTML through polling, webhooks, or downloads. Credits are reserved for the accepted page budget. Only successful pages are charged; unused credits are released. Use item IDs and idempotency keys t
- 2026-07-30 | Connect AI agents over MCP with OAuth | [Connect an AI client over MCP] and authorize it in your browser with OAuth. The consent screen identifies the client and requested access; no API key needs to be pasted into its configuration. 
- 2026-07-27 | Monitor the changes that matter | Give [page monitors] instructions describing which changes matter, such as pricing changes rather than rotating testimonials. Semantic detection filters irrelevant changes; empty or blocked snapshots fail the run without replacing a valid baseline. 
- 2026-07-25 | Usage alerts for overages | Set an [Auto-Topup budget] and receive email alerts at selected spending thresholds. Alerts are a soft cap: API requests, monitors, and Auto-Topup continue after the budget is exceeded. 
- 2026-07-22 | Simpler monitor setup and secret rotation | [Create a monitor] with just `name` and `target`. Scheduling defaults to daily, with detection selected for the target. Check the baseline run using `initial_run_id`. [Rotate webhook signing secrets] without replacing the monitor. The old secret stops signing new deliveries immediately. 
- 2026-07-22 | Browser actions before scraping | [Click, type, or wait] before scraping Markdown, HTML, or Images. Paid plans support up to five ordered actions. Standard requests with actions cost 2 credits and bypass caching. Enriched image requests remain 5 credits. 
- 2026-07-21 | Zero data retention | Eligible scraping and parsing requests now support [zero data retention]. Set `zdr=enabled` to bypass shared caches and retained content logs, and verify the `X-Context-ZDR: true` response header. 
- 2026-07-20 | Default organization | Choose which [organization] opens by default when you use more than one account workspace. 
- 2026-07-18 | Layout-aware PDF parsing | [Parse PDFs] with better tables, reading order, headings, and subscript or superscript text. Display equations are preserved as text. OCR can also recover corrupted text layers. This update applies to Parse. See the guide for current OCR controls and billing. 
- 2026-07-17 | Faster web dashboard | [Dashboard] pages load faster when moving between usage, API keys, team settings, and product views. 
- 2026-07-12 | Request tags for usage tracking | [Tag requests] by customer, feature, or environment, then filter charts and logs by those tags. Add up to 20 labels without changing pricing or caching. Monitor resource tags remain separate. 
- 2026-07-12 | Parse file bytes to Markdown | [Upload documents directly] and get Markdown without hosting a file at a URL. Choose format hints, PDF page ranges, and content controls. Conversion costs 1 credit, with optional OCR charges. The launch limit is 25 MiB, increased to **50 MiB** on September 15. 
- 2026-07-11 | Rate-limit headers on every response | Authenticated responses now include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`, so you can pace calls before hitting the limit. A `429` also includes `Retry-After`. See [Rate limits]. 
- 2026-07-11 | Cleaner main-content Markdown | Main-content filtering removes more navigation, ads, comments, and layout markup from [Markdown scrapes]. The response also includes `contentLength`, measured in UTF-8 bytes, to help detect empty results. 
- 2026-07-11 | Per-run monitor webhooks | Subscribe to [`run.completed`] for a signed webhook after every completed run, including baseline and no-change runs. Existing integrations continue receiving `change.detected` only. Run history adds `webhook_deliveries`. The singular field remains available but is deprecated. 
- 2026-07-11 | Monitor webhook health tracking | Receive an email after three consecutive monitor runs with failed webhook deliveries. A successful delivery or webhook URL change clears the failure streak. Rate-limited receivers are retried using `Retry-After`. See [delivery failures] for recovery steps. 
- 2026-07-10 | Join an organization by email domain | Let teammates with a verified company email domain discover and [join your organization] without an invitation. Manage the setting from the dashboard. 
- 2026-07-09 | Website monitors | [Watch a page, sitemap, or structured data] on a schedule and receive signed webhooks when it changes. Manage monitors, runs, and changes through the API or SDKs, at no credit cost. Successful page and sitemap checks cost 1 credit; extract checks cost 10. Failed or skipped runs are free. 
- 2026-07-07 | Brand lookup from an exact URL | [Retrieve brand data from an exact page] with `type: "by_direct_url"`. Results use that page's content only and cost 10 credits on success. Domain-lookup options such as `maxSpeed`, `force_language`, and `maxAgeMs` are not supported. 
- 2026-07-05 | One request for brand lookups | Use one [`POST /brand/retrieve`] operation for domain, email, name, ticker, and transaction lookups. The `type` field selects the lookup, giving SDK integrations one consistent entry point. 
- 2026-07-05 | One request for prefetching | [Prefetch] now uses one request with a `type` field for queuing brand data by domain or email. 
- 2026-07-05 | API reference navigation | The [API reference] now groups related operations, uses shorter names, and redirects legacy pages to their replacements. 
- 2026-07-04 | Customer referrals | Share your referral link from the dashboard. Referred customers receive 10% off for 12 months, and you earn 10% of their payments for a year. The program is available to existing customers without an application and is separate from the affiliate program. 
- 2026-07-04 | Remove duplicate images | Set `dedupe=true` on [Images] to remove near-duplicate images without changing the request price. 
- 2026-07-04 | Scrape PowerPoint presentations | [Scrape PowerPoint URLs] into Markdown or HTML, including slide text, tables, and speaker notes. Supports PPTX and legacy PPT. Crawls can follow links to presentations. 
- 2026-07-03 | Scrape spreadsheets and CSV files | Scrape [Excel and CSV URLs] into tables. Workbooks return separate sheet tables, and CSV output preserves an optional title or attribution above the header. Markdown, HTML, and Crawl support the new formats. 


## Capability tour (2026-10-30)

`context_dev/capabilities.py`, run by `scripts/run/capabilities_tour.py`, output in
`evidence/runs/capabilities-2026-10-30.json`. One call per capability; credits from `key_metadata`.

| Capability | Call | Input | What came back | Credits |
|---|---|---|---|---|
| Web Search + highlights | `web.search` | "open source web scraping API for AI agents" | 4 results with relevance + passages (aiagentsdirectory, reddit r/LangChain, shattered.io, siliconangle Firecrawl $75M) | 2 |
| Crawl | `web.web_crawl_md` | docs.context.dev/scrape/overview, max 3 | 3 pages, 11.8K–15.1K chars Markdown each, 2 skipped | 3 |
| JSON extraction | `web.scrape` formats.json | context.dev/pricing + plans schema | 7 plans: Free 0/1,000 · Developer $20/10K · Pro $90/100K · Growth $300/500K · Scale $500/1M · Scale 2.5M $950 · Enterprise | 5 |
| Product | `web.scrape` formats.product | allbirds.com men's Tree Runners | is_product_page true, Men's Tree Runner, USD 100.0, in_stock | 2 |
| Prebuilt parser | formats.parse, `google-play` | Duolingo app page | rating 4.746, 51,434,561 ratings, 500,000,000+ downloads | 1 |
| Screenshot | `web.screenshot` | stripe.com | 1920x1080 viewport PNG URL | 1 |
| Styleguide | `web.extract_styleguide` | linear.app | dark mode, accent #7170ff, bg #08090a, spacing xs 6px … xl 96px | 10 |
| Brand by domain | `brand.retrieve` by_domain | linear.app | title, slogan, colors, 3 logos, EIC Technology / Software (B2B), 51–200 employees | 10 |
| Competitors (SDK only, undocumented) | `web.extract_competitors` | linear.app, 5 | Jira (high), Azure DevOps, GitLab, Trello, ClickUp (medium) | 10 |
| Images | formats.images | linear.app | 111 image URLs | 1 |
| Parse | `parse.handle` | tests/fixtures/files/invoice-sample.pdf | exact text back as Markdown | 1 |

Not run: People Enrich (returns personal profiles; skipped on purpose), browser profiles/actions (paid plan),
access policies (enabled per org by support).
