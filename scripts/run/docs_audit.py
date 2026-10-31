#!/usr/bin/env python3
"""Docs-coverage audit: one small live call per documented feature the earlier
tours did not exercise. Raw HTTP against https://api.context.dev/v1 so every
parameter matches docs.context.dev exactly.

Writes evidence/runs/docs-audit-<UTC date>.json (responses trimmed, no key).
Budget: about 200 credits, most of it one Answers `ultra` call (100).
Usage: CONTEXT_DEV_API_KEY=... python scripts/run/docs_audit.py [--only a,b]
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, pathlib, time, urllib.parse, urllib.request, urllib.error

BASE = "https://api.context.dev/v1"
ROOT = pathlib.Path(__file__).resolve().parents[2]

def call(method, path, body=None, params=None, timeout=120):
    url = BASE + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + os.environ["CONTEXT_DEV_API_KEY"],
        "Content-Type": "application/json", "User-Agent": "context-dev-exploration/docs-audit"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, hdr, raw = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, hdr, raw = e.code, dict(e.headers), e.read()
    ms = int((time.time() - t) * 1000)
    try: js = json.loads(raw)
    except Exception: js = {"_raw": raw[:300].decode(errors="replace")}
    credits = hdr.get("X-Credits-Used") or hdr.get("x-credits-used")
    if credits is None and isinstance(js, dict):
        credits = (js.get("key_metadata") or {}).get("credits_consumed")
    return {"status": status, "ms": ms, "credits": credits, "body": js}

S = "/web/scrape"
PROBES = {
 "custom_parser": ("POST", S, {"url": "https://news.ycombinator.com/", "formats": {"parse": True},
     "parseParams": {"rules": {"stories": {"selector": ".titleline", "type": "list",
                                            "output": {"title": "a", "url": "a@href"}}}}}),
 "parser_emails": ("POST", S, {"url": "https://www.python.org/about/help/", "formats": {"parse": True},
     "parseParams": {"type": "prebuilt", "parser": "emails"}}),
 "parser_links": ("POST", S, {"url": "https://docs.context.dev/introduction", "formats": {"parse": True},
     "parseParams": {"type": "prebuilt", "parser": "links"}}),
 "youtube": ("POST", S, {"url": "https://www.youtube.com/watch?v=jNQXAC9IVRw", "formats": {"markdown": True}}),
 "screenshot_images_meta": ("POST", S, {"url": "https://linear.app", "formats": {"screenshot": True, "images": True},
     "screenshotParams": {"area": "viewport"}}),
 "browser_actions": ("POST", S, {"url": "https://news.ycombinator.com/", "formats": {"markdown": True},
     "sharedParams": {"actions": [{"type": "perform", "action": "Click the More link at the bottom"},
                                   {"type": "wait", "milliseconds": 1000}]}}),
 "country_fresh": ("POST", S, {"url": "https://www.apple.com/shop/buy-iphone", "formats": {"highlights": True},
     "highlightsParams": {"query": "iPhone starting price"}, "sharedParams": {"country": "DE"}, "maxAgeMs": 0}),
 "pdf_scrape": ("POST", S, {"url": "https://arxiv.org/pdf/1706.03762", "formats": {"highlights": True},
     "highlightsParams": {"query": "BLEU score on WMT 2014 English-to-German"}}),
 "bytes": ("POST", S, {"url": "https://www.context.dev/favicon.ico", "formats": {"bytes": True}}),
 "map_regex": ("GET", "/web/urls", None, {"domain": "docs.context.dev", "urlRegex": ".*/scrape/prebuilt-parsers/.*", "maxLinks": 50}),
 "search_filters": ("POST", "/web/search", {"query": "Context.dev changelog", "numResults": 5,
     "includeDomains": ["context.dev"], "freshness": "last_month"}),
 "answers_ultra": ("POST", "/web/answers", {"mode": "ultra",
     "task": "What does the Developer plan of Context.dev cost per month and how many credits does it include? Use context.dev pages.",
     "json_format": {"plan": "Developer", "monthly_usd": 20, "credits": 10000, "source_url": "https://..."}}, None, 200),
 "brand_name": ("POST", "/brand/retrieve", {"type": "by_name", "name": "Linear"}),
 "brand_email": ("POST", "/brand/retrieve", {"type": "by_email", "email": "hello@vercel.com"}),
 "brand_ticker": ("POST", "/brand/retrieve", {"type": "by_ticker", "ticker": "AAPL"}),
 "brand_url": ("POST", "/brand/retrieve", {"type": "by_direct_url", "direct_url": "https://stripe.com/pricing"}),
 "brand_autocomplete": ("GET", "/brand/search", None, {"query": "lin", "autocomplete": "true"}),
 "styleguide": ("GET", "/web/styleguide", None, {"domain": "linear.app"}),
 "prefetch": ("POST", "/utility/prefetch", {"type": "brand", "identifier": {"domain": "posthog.com"}}),
 "people_enrich": ("POST", "/people/enrich", {"name": {"first": "Patrick", "last": "Collison"}, "company": {"domain": "stripe.com"}}),
 "monitor_limits": ("GET", "/monitors/limits", None, None),
 "usage": ("GET", "/org/usage", None, None),
 "usage_history": ("GET", "/org/usage/history", None, {"interval": "day"}),
 "logs": ("GET", "/org/logs", None, {"limit": 5, "errors_only": "true"}),
 "webhook_deliveries": ("POST", "/webhooks/deliveries", {"type": "batch"}),
}

def trim(o, n=0):
    if n > 5: return "..."
    if isinstance(o, dict): return {k: ("<base64 %d chars>" % len(v) if isinstance(v, str) and len(v) > 2000 else trim(v, n+1)) for k, v in o.items()}
    if isinstance(o, list): return [trim(x, n+1) for x in o[:12]] + (["... %d more" % (len(o)-12)] if len(o) > 12 else [])
    if isinstance(o, str) and len(o) > 1500: return o[:1500] + "...[%d chars]" % len(o)
    return o

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", default=""); a = ap.parse_args()
    only = {x for x in a.only.split(",") if x}
    out = ROOT / "evidence/runs" / f"docs-audit-{dt.datetime.now(dt.timezone.utc):%Y-%m-%d}.json"
    res = json.loads(out.read_text()) if out.exists() else {}
    for name, p in PROBES.items():
        if only and name not in only: continue
        m, path, body, *rest = p
        params = rest[0] if rest else None; to = rest[1:]
        r = call(m, path, body, params, *(to or []))
        full = r["body"]
        r["body"] = trim(full)
        res[name] = r
        print(f"{name:24s} {r['status']} {r['ms']:>6}ms credits={r['credits']}")
    # sitemap monitor: create, run once, read, delete (1 credit per run)
    if not only or "monitor_sitemap" in only:
        c = call("POST", "/monitors", {"name": "docs-audit sitemap", "target": {"type": "sitemap",
              "url": "https://docs.context.dev/sitemap.xml", "include": ["/changelog*"]}})
        mid = (c["body"] or {}).get("id") or ((c["body"] or {}).get("monitor") or {}).get("id")
        rec = {"create": {k: c[k] for k in ("status", "ms", "credits")}, "create_body": trim(c["body"])}
        if mid:
            time.sleep(20)
            rec["runs"] = trim(call("GET", f"/monitors/{mid}/runs")["body"])
            d = call("DELETE", f"/monitors/{mid}"); rec["delete"] = d["status"]
        res["monitor_sitemap"] = rec
        print("monitor_sitemap", c["status"], "deleted", rec.get("delete"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print("wrote", out.relative_to(ROOT))

if __name__ == "__main__":
    main()
