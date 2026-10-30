"""Probes for Context.dev features shipped after the July 2026 exploration.

Each function makes one documented call, returns a small JSON-safe summary,
and reports the credits the API says it consumed (``key_metadata``) so runs
can be reconciled against the published price list.

Feature dates come from https://docs.context.dev/changelog (read 2026-10-30).
"""

from __future__ import annotations

from typing import Any

from context.dev import ContextDev

from context_dev.client import _ns, _safe_str, with_retry

# Published credit prices (docs.context.dev pricing + changelog, 2026-10-30).
LATEST_CREDITS: dict[str, int] = {
    "scrape_markdown": 1,
    # Highlights launched at +3 (changelog, Sep 23); pricing page now says +1.
    "scrape_highlights": 1 + 1,
    "map_search": 2,  # Map with `search` (Aug 6)
    "answers_fast": 10,  # Answers fast (Sep 12)
    "brand_by_transaction": 10,  # unified brand/retrieve (Jul 5); 0 on NOT_FOUND
    "brand_search": 1,  # 1 on Free/Starter at launch, free on Pro/Scale
    "company_search": 2,  # Oct 21; free when empty
    "people_search_fast": 10,  # Oct 23, per page with results
    "news_search": 1,  # 1 per 10 articles
    "monitor_create": 0,  # management calls are free; each page run costs 1
    "batch_submit_per_url": 1,
}


def _credits(response: Any) -> int | None:
    meta = getattr(response, "key_metadata", None)
    return getattr(meta, "credits_consumed", None) if meta is not None else None


def scrape_highlights(client: ContextDev, url: str, query: str) -> dict[str, Any]:
    """Scrape Anything (Sep 22) + highlights format (Sep 23)."""
    r = with_retry(
        lambda: client.web.scrape(
            url=url,
            formats={"markdown": True, "highlights": True},
            highlights_params={"query": query, "max_characters": 1200},
        )
    )
    md = getattr(r, "markdown", None)
    hl = getattr(r, "highlights", None)
    text = (getattr(md, "data", None) if md else None) or ""
    cache = getattr(r, "cache_metadata", None)
    return {
        "url": url,
        "query": query,
        "markdown_length": len(text),
        "markdown_head": text[:400],
        "highlights": list((getattr(hl, "data", None) if hl else None) or [])[:3],
        "highlights_code": _safe_str(getattr(hl, "error_code", None)) if hl else None,
        "cache_status": _safe_str(getattr(cache, "status", None)) if cache else None,
        "credits": _credits(r),
    }


def map_search(client: ContextDev, domain: str, search: str, max_links: int = 5) -> dict[str, Any]:
    """Map URLs with relevance search (Aug 6, unified Sep 22)."""
    r = with_retry(lambda: client.web.map_urls(domain=domain, search=search, max_links=max_links))
    urls = getattr(r, "urls", None) or []
    return {
        "domain": domain,
        "search": search,
        "urls": [
            {"url": _safe_str(getattr(u, "url", None)), "title": _safe_str(getattr(u, "title", None))}
            for u in urls[:max_links]
        ],
        "credits": _credits(r),
    }


def answers_fast(client: ContextDev, task: str, json_format: dict[str, Any]) -> dict[str, Any]:
    """Answers (Sep 12) in fast mode: 10 credits, 30-second budget."""
    r = with_retry(lambda: client.web.answers(task=task, json_format=json_format, mode="fast"))
    return {
        "task": task,
        "json_content": getattr(r, "json_content", None),
        "sources": list(getattr(r, "sources", None) or [])[:8],
        "partial": getattr(r, "partial", None),
        "credits": _credits(r),
    }


def brand_by_transaction(
    client: ContextDev, transaction_info: str, country_gl: str = "us", mcc: int | None = None
) -> dict[str, Any]:
    """Unified POST /brand/retrieve with type=by_transaction (Jul 5)."""
    kwargs: dict[str, Any] = {"transaction_info": transaction_info, "country_gl": country_gl}
    if mcc is not None:
        kwargs["mcc"] = mcc
    r = with_retry(lambda: client.brand.retrieve(type="by_transaction", **kwargs))
    b = getattr(r, "brand", None)
    return {
        "transaction_info": transaction_info,
        "title": _safe_str(getattr(b, "title", None)) if b else None,
        "domain": _safe_str(getattr(b, "domain", None)) if b else None,
        "credits": _credits(r),
    }


def brand_search(client: ContextDev, query: str) -> dict[str, Any]:
    """Brand Search for autocomplete (Aug 4; filters Oct 16)."""
    r = with_retry(lambda: client.brand.search(query=query))
    results = getattr(r, "results", None) or []
    return {
        "query": query,
        "results": [
            {"name": _safe_str(getattr(x, "name", None)),
             "domain": _safe_str(getattr(x, "domain", None))}
            for x in results[:5]
        ],
        "credits": _credits(r),
    }


def company_search(client: ContextDev, query: str) -> dict[str, Any]:
    """Company search (Oct 21). Not in Python SDK 2.41.1, so call the route."""
    raw = with_retry(
        lambda: client.post("/company/search", body={"query": query}, cast_to=object)
    )
    r = _ns(raw) if isinstance(raw, dict) else raw
    results = getattr(r, "results", None) or []
    out = []
    for c in results[:5]:
        out.append({
            "name": _safe_str(getattr(c, "name", None) or getattr(c, "title", None)),
            "domain": _safe_str(getattr(c, "domain", None)),
        })
    return {"query": query, "results": out, "credits": _credits(r)}


def people_search(client: ContextDev, query: str) -> dict[str, Any]:
    """People Search (Oct 23), fast mode: 10 credits per page with results."""
    r = with_retry(lambda: client.people.search(query=query, mode="fast"))
    results = getattr(r, "results", None) or []
    out = []
    for p in results[:5]:
        role = getattr(p, "role", None)
        company = getattr(role, "company", None) if role else None
        # Names and profile URLs are personal data: keep only role + employer.
        out.append({
            "title": _safe_str(getattr(role, "title", None)) if role else None,
            "company": _safe_str(getattr(company, "name", None)) if company else None,
            "seniority": _safe_str(getattr(role, "seniority", None)) if role else None,
        })
    return {"query": query, "result_count": len(results), "results": out, "credits": _credits(r)}


def news_search(client: ContextDev, query: str, limit: int = 10) -> dict[str, Any]:
    """Natural-language News search (Oct 18)."""
    r = with_retry(
        lambda: client.news.search(
            search_by={"type": "natural_language", "query": query}, limit=limit
        )
    )
    arts = getattr(r, "data", None) or []
    return {
        "query": query,
        "articles": [
            {"title": _safe_str(getattr(a, "title", None)),
             "url": _safe_str(getattr(a, "url", None)),
             "published": _safe_str(getattr(a, "published_at", None))}
            for a in arts[:5]
        ],
        "credits": _credits(r),
    }


def create_semantic_monitor(client: ContextDev, url: str, instructions: str) -> dict[str, Any]:
    """Page monitor with semantic change detection (Jul 9 + Jul 27).

    The caller is responsible for deleting it (see delete_monitor) so a
    probe run does not leave a daily 1-credit check behind.
    """
    r = with_retry(
        lambda: client.monitors.create(
            name=f"probe: {url}",
            target={"type": "page", "url": url, "instructions": instructions},
            change_detection={"type": "semantic"},
            tags=["context-dev-exploration"],
        )
    )
    return {
        "monitor_id": _safe_str(getattr(r, "id", None)),
        "status": _safe_str(getattr(r, "status", None)),
        "initial_run_id": _safe_str(getattr(r, "initial_run_id", None)),
        "url": url,
        "instructions": instructions,
    }


def delete_monitor(client: ContextDev, monitor_id: str) -> dict[str, Any]:
    with_retry(lambda: client.monitors.delete(monitor_id))
    return {"monitor_id": monitor_id, "deleted": True}


def submit_batch(client: ContextDev, urls: list[str]) -> dict[str, Any]:
    """Async Scrape Anything batch (Jul 30: 25K, Oct 15: 100K URLs)."""
    r = with_retry(
        lambda: client.batch.submit(
            input={"mode": "scrape", "data": {"format": "markdown", "urls": [{"url": u} for u in urls]}},
            tags=["context-dev-exploration"],
        )
    )
    return {
        "batch_id": _safe_str(getattr(r, "id", None)),
        "status": _safe_str(getattr(r, "status", None)),
        "url_count": len(urls),
        "invalid_urls": len(getattr(r, "invalid_urls", None) or []),
        "credits": _credits(r),
    }
