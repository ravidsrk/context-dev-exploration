"""Thin Context.dev API client with env-based auth and 408/429 retry."""

from __future__ import annotations

import os
import time
from typing import Any, Callable, TypeVar

from context.dev import APIStatusError, ContextDev

T = TypeVar("T")

RETRYABLE_STATUS = {408, 429}


def get_api_key() -> str:
    key = os.environ.get("CONTEXT_DEV_API_KEY") or os.environ.get("CONTEXT_API_KEY")
    if not key:
        raise RuntimeError(
            "CONTEXT_DEV_API_KEY environment variable is required. "
            "Never hardcode API keys in source."
        )
    return key


def create_client() -> ContextDev:
    return ContextDev(api_key=get_api_key())


def with_retry(
    fn: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> T:
    """Execute fn with exponential backoff on 408/429."""
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            return fn()
        except APIStatusError as e:
            last_err = e
            if e.status_code in RETRYABLE_STATUS and attempt < max_retries - 1:
                time.sleep(base_delay * (2**attempt))
                continue
            raise
    raise last_err  # type: ignore[misc]


def _safe_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _first_logo_url(logos: Any) -> str | None:
    if not logos:
        return None
    for logo in logos:
        url = getattr(logo, "url", None)
        if url:
            return _safe_str(url)
    return None


def _parse_industry_codes(codes: Any) -> list[dict[str, str]]:
    if not codes:
        return []
    parsed: list[dict[str, str]] = []
    for item in codes:
        code = _safe_str(getattr(item, "code", None))
        name = _safe_str(getattr(item, "name", None))
        confidence = _safe_str(getattr(item, "confidence", None))
        if code and name:
            entry: dict[str, str] = {"code": code, "name": name}
            if confidence:
                entry["confidence"] = confidence
            parsed.append(entry)
    return parsed


def retrieve_brand(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.brand.retrieve(domain=domain))
    brand = getattr(response, "brand", None)
    if brand is None:
        return {"title": None, "domain": domain, "logo_url": None, "industries": None}
    return {
        "title": _safe_str(getattr(brand, "title", None)),
        "domain": _safe_str(getattr(brand, "domain", None)) or domain,
        "logo_url": _first_logo_url(getattr(brand, "logos", None)),
        "industries": getattr(brand, "industries", None),
    }


def scrape_markdown(client: ContextDev, url: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.web_scrape_md(url=url))
    markdown = getattr(response, "markdown", None) or ""
    return {
        "url": _safe_str(getattr(response, "url", None)) or url,
        "markdown": markdown,
        "markdown_length": len(markdown),
    }


def identify_transaction(
    client: ContextDev,
    transaction_info: str,
    country_gl: str = "us",
    mcc: str | None = None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "transaction_info": transaction_info,
        "country_gl": country_gl,
    }
    if mcc:
        kwargs["mcc"] = mcc
    response = with_retry(lambda: client.brand.identify_from_transaction(**kwargs))
    brand = getattr(response, "brand", None)
    if brand is None:
        return {"title": None, "domain": None, "industries": None}
    return {
        "title": _safe_str(getattr(brand, "title", None)),
        "domain": _safe_str(getattr(brand, "domain", None)),
        "industries": getattr(brand, "industries", None),
    }


def classify_naics(client: ContextDev, input_value: str) -> dict[str, Any]:
    response = with_retry(lambda: client.industry.retrieve_naics(input=input_value))
    return {
        "domain": _safe_str(getattr(response, "domain", None)),
        "codes": _parse_industry_codes(getattr(response, "codes", None)),
    }


def classify_sic(client: ContextDev, input_value: str) -> dict[str, Any]:
    response = with_retry(
        lambda: client.industry.retrieve_sic(input=input_value, type="latest_sec")
    )
    return {
        "domain": _safe_str(getattr(response, "domain", None)),
        "codes": _parse_industry_codes(getattr(response, "codes", None)),
    }


def prefetch_domain(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.utility.prefetch(domain=domain))
    return {
        "status": _safe_str(getattr(response, "status", None)),
        "domain": _safe_str(getattr(response, "domain", None)) or domain,
    }


def _count_styleguide_colors(colors: Any) -> int:
    if colors is None:
        return 0
    if isinstance(colors, (list, tuple)):
        return len(colors)
    # StyleguideColors is a structured object (accent, background, text, ...)
    if hasattr(colors, "model_dump"):
        data = colors.model_dump()
        return sum(1 for v in data.values() if v)
    if isinstance(colors, dict):
        return sum(1 for v in colors.values() if v)
    return sum(
        1
        for field in ("accent", "background", "text", "primary", "secondary")
        if _safe_str(getattr(colors, field, None))
    )


def extract_styleguide(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.extract_styleguide(domain=domain))
    styleguide = getattr(response, "styleguide", None)
    colors = getattr(styleguide, "colors", None) if styleguide else None
    typography = getattr(styleguide, "typography", None) if styleguide else None
    return {
        "domain": _safe_str(getattr(response, "domain", None)) or domain,
        "color_count": _count_styleguide_colors(colors),
        "has_typography": typography is not None,
    }


def extract_fonts(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.extract_fonts(domain=domain))
    fonts = getattr(response, "fonts", None) or []
    font_names = [
        _safe_str(
            getattr(f, "font", None)
            or getattr(f, "family", None)
            or getattr(f, "name", None)
        )
        for f in fonts
    ]
    font_names = [n for n in font_names if n]
    return {
        "domain": _safe_str(getattr(response, "domain", None)) or domain,
        "font_count": len(font_names),
        "font_names": font_names[:5],
    }


def scrape_screenshot(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.screenshot(domain=domain))
    screenshot_url = _safe_str(getattr(response, "screenshot", None))
    return {
        "domain": domain,
        "screenshot_url": screenshot_url,
        "has_screenshot": bool(screenshot_url),
    }


def crawl_markdown(
    client: ContextDev, url: str, max_pages: int = 2
) -> dict[str, Any]:
    response = with_retry(
        lambda: client.web.web_crawl_md(url=url, max_pages=max_pages)
    )
    results = getattr(response, "results", None) or []
    metadata = getattr(response, "metadata", None)
    num_succeeded = getattr(metadata, "num_succeeded", None) if metadata else None
    succeeded = sum(1 for r in results if getattr(r, "success", False))
    return {
        "seed_url": url,
        "num_results": len(results),
        "num_succeeded": num_succeeded if num_succeeded is not None else succeeded,
        "pages_with_markdown": sum(
            1 for r in results if len(getattr(r, "markdown", None) or "") > 0
        ),
    }


def scrape_sitemap(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.web_scrape_sitemap(domain=domain))
    urls = getattr(response, "urls", None) or []
    return {
        "domain": domain,
        "url_count": len(urls),
        "sample_urls": [_safe_str(u) for u in urls[:3] if _safe_str(u)],
    }