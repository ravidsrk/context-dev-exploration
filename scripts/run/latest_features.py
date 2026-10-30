#!/usr/bin/env python3
"""Run live probes for Context.dev features shipped since July 2026.

Writes evidence/runs/latest-features-<UTC date>.json and prints a summary.
Budget: about 40 credits per full run (see LATEST_CREDITS). The monitor it
creates is deleted at the end so nothing keeps billing.

Usage: CONTEXT_DEV_API_KEY=... python scripts/run/latest_features.py [--skip monitor,batch]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
import time
import traceback

from context.dev import APIStatusError

from context_dev import latest
from context_dev.client import create_client, get_api_key

ROOT = pathlib.Path(__file__).resolve().parents[2]

PROBES = [
    ("scrape_highlights", lambda c: latest.scrape_highlights(
        c, "https://stripe.com/pricing", "What does Stripe charge per card transaction?")),
    ("map_search", lambda c: latest.map_search(c, "stripe.com", "pricing and fees")),
    ("brand_by_transaction", lambda c: latest.brand_by_transaction(
        c, "STARBUCKS STORE 12345", mcc=5814)),
    ("brand_search", lambda c: latest.brand_search(c, "linear")),
    ("company_search", lambda c: latest.company_search(
        c, "Developer tools companies that sell a web scraping API")),
    ("people_search", lambda c: latest.people_search(
        c, "Heads of developer relations at API companies in India")),
    ("news_search", lambda c: latest.news_search(c, "web scraping API funding", limit=10)),
    ("answers_fast", lambda c: latest.answers_fast(
        c,
        "What is the monthly price and included credits of each Context.dev self-serve plan?",
        {"type": "object", "properties": {"plans": {"type": "array", "items": {
            "type": "object", "properties": {
                "name": {"type": "string"}, "monthly_usd": {"type": "number"},
                "credits": {"type": "number"}}}}}},
    )),
    ("batch", lambda c: latest.submit_batch(
        c, ["https://docs.context.dev/changelog", "https://docs.context.dev/pricing"])),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", default="", help="comma-separated probe names")
    args = ap.parse_args()
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    try:
        get_api_key()
    except RuntimeError as e:
        print(f"SKIP: {e}", file=sys.stderr)
        return 2
    client = create_client()
    started = dt.datetime.now(dt.timezone.utc)
    results: dict[str, object] = {}
    for name, fn in PROBES:
        if name in skip:
            continue
        t0 = time.monotonic()
        try:
            out = fn(client)
            results[name] = {"ok": True, "ms": int((time.monotonic() - t0) * 1000), "result": out}
        except APIStatusError as e:
            results[name] = {"ok": False, "status": e.status_code, "error": str(e)[:300]}
        except Exception as e:  # keep going; record the failure as evidence
            results[name] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300],
                             "trace": traceback.format_exc(limit=2)[-600:]}
        print(f"[{name}] {json.dumps(results[name], default=str)[:400]}")

    if "monitor" not in skip:
        t0 = time.monotonic()
        try:
            m = latest.create_semantic_monitor(
                client, "https://stripe.com/pricing",
                "Alert only when a listed price, fee or plan changes. Ignore testimonials and layout.")
            mid = m["monitor_id"]
            if mid:
                m["cleanup"] = latest.delete_monitor(client, mid)
            results["semantic_monitor"] = {"ok": True, "ms": int((time.monotonic() - t0) * 1000), "result": m}
        except APIStatusError as e:
            results["semantic_monitor"] = {"ok": False, "status": e.status_code, "error": str(e)[:300]}
        print(f"[semantic_monitor] {json.dumps(results['semantic_monitor'], default=str)[:400]}")

    out = {
        "started_utc": started.isoformat(),
        "sdk": "context.dev (python) " + __import__("importlib.metadata").metadata.version("context.dev"),
        "credits_reported": sum(
            (r.get("result") or {}).get("credits") or 0 for r in results.values() if isinstance(r, dict)
        ),
        "results": results,
    }
    path = ROOT / "evidence" / "runs" / f"latest-features-{started:%Y-%m-%d}.json"
    path.write_text(json.dumps(out, indent=2, default=str))
    print(f"wrote {path.relative_to(ROOT)}  credits_reported={out['credits_reported']}")
    return 0 if all(r.get("ok") for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
