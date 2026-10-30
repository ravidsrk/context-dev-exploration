"""Capability tour: one small, documented call per Context.dev capability that
the July and October probes did not already cover.

Every function returns a JSON-safe summary plus ``credits`` from
``key_metadata.credits_consumed``. No person names or contact details are
kept in summaries. Docs index: https://docs.context.dev/llms.txt (2026-10-30).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context.dev import ContextDev

from context_dev.client import with_retry


def _d(r: Any) -> dict[str, Any]:
    return r.model_dump(exclude_none=True)


def _credits(d: dict[str, Any]) -> int | None:
    return (d.get("key_metadata") or {}).get("credits_consumed")


def web_search(client: ContextDev, query: str) -> dict[str, Any]:
    """Search with highlights per result (docs: search/page-content)."""
    d = _d(with_retry(lambda: client.web.search(query=query, num_results=5, highlights_options={"enabled": True})))
    return {
        "query": query,
        "results": [
            {"url": r.get("url"), "relevance": r.get("relevance"),
             "highlight_head": ((r.get("highlights") or {}).get("highlights") or [""])[0][:200]}
            for r in d.get("results", [])
        ],
        "credits": _credits(d),
    }


def crawl(client: ContextDev, url: str, max_pages: int = 3) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.web_crawl_md(url=url, max_pages=max_pages)))
    return {
        "start_url": url,
        "pages": [{"url": r["metadata"].get("url"), "markdown_chars": len(r.get("markdown", ""))} for r in d.get("results", [])],
        "metadata": {k: v for k, v in (d.get("metadata") or {}).items() if "_" in k},
        "credits": _credits(d),
    }


PRICING_SCHEMA = {
    "type": "object",
    "properties": {"plans": {"type": "array", "items": {"type": "object", "properties": {
        "name": {"type": "string"}, "price_usd_per_month": {"type": "number"},
        "credits_per_month": {"type": "number"}}}}},
}


def scrape_json(client: ContextDev, url: str, schema: dict[str, Any] = PRICING_SCHEMA) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.scrape(url=url, formats={"json": True}, json_params={"schema": schema})))
    return {"url": url, "data": (d.get("json_") or {}).get("data"), "credits": _credits(d)}


def scrape_product(client: ContextDev, url: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.scrape(url=url, formats={"product": True})))
    data = (d.get("product") or {}).get("data") or {}
    p = data.get("product") or {}
    keep = ("name", "brand", "price", "currency", "availability", "category", "sku")
    return {"url": url, "is_product_page": data.get("is_product_page"),
            "product": {k: p.get(k) for k in keep}, "variant_count": len(p.get("variants") or []),
            "credits": _credits(d)}


def prebuilt_parser(client: ContextDev, url: str, parser: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.scrape(url=url, formats={"parse": True}, parse_params={"type": "prebuilt", "parser": parser})))
    data = (d.get("parsed") or {}).get("data") or {}
    keep = ("app_id", "name", "rating", "rating_count", "downloads", "offered_by")
    return {"url": url, "parser": parser, "fields": {k: data.get(k) for k in keep}, "credits": _credits(d)}


def screenshot(client: ContextDev, domain: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.screenshot(domain=domain, clear_popups=True)))
    return {k: d.get(k) for k in ("domain", "screenshot", "screenshot_type", "width", "height")} | {"credits": _credits(d)}


def styleguide(client: ContextDev, domain: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.extract_styleguide(domain=domain)))
    s = d.get("styleguide") or {}
    return {"domain": domain, "mode": s.get("mode"), "colors": s.get("colors"),
            "spacing": s.get("element_spacing"), "fonts": list((s.get("font_links") or {}))[:4],
            "credits": _credits(d)}


def brand_by_domain(client: ContextDev, domain: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.brand.retrieve(type="by_domain", domain=domain)))
    b = d.get("brand") or {}
    return {"domain": domain, "title": b.get("title"), "slogan": b.get("slogan"),
            "colors": [c.get("hex") for c in b.get("colors", [])][:3],
            "logo_types": [l.get("type") for l in b.get("logos", [])],
            "industries": b.get("industries"), "employees": b.get("employees"),
            "links": sorted((b.get("links") or {}).keys()), "credits": _credits(d)}


def competitors(client: ContextDev, domain: str, n: int = 5) -> dict[str, Any]:
    """SDK 2.41 web.extract_competitors; not yet in the docs index (2026-10-30)."""
    d = _d(with_retry(lambda: client.web.extract_competitors(domain=domain, num_competitors=n)))
    return {"domain": domain, "field": (d.get("target") or {}).get("field"),
            "competitors": [{"name": c.get("name"), "domain": c.get("domain"), "confidence": c.get("confidence")}
                            for c in d.get("competitors", [])],
            "credits": _credits(d)}


def images(client: ContextDev, url: str) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.web.scrape(url=url, formats={"images": True})))
    imgs = (d.get("images") or {}).get("data") or []
    return {"url": url, "image_count": len(imgs), "first": [i.get("url") for i in imgs[:3]], "credits": _credits(d)}


def parse_file(client: ContextDev, path: Path) -> dict[str, Any]:
    d = _d(with_retry(lambda: client.parse.handle(path.read_bytes(), extension=path.suffix.lstrip("."))))
    md = d.get("markdown") or ""
    if isinstance(md, dict):
        md = md.get("data") or ""
    return {"file": path.name, "markdown": str(md)[:400], "keys": sorted(d.keys()), "credits": _credits(d)}
