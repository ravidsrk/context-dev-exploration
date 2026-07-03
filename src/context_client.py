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


def retrieve_brand(client: ContextDev, domain: str) -> dict[str, Any]:
    response = with_retry(lambda: client.brand.retrieve(domain=domain))
    return {
        "title": response.brand.title,
        "domain": response.brand.domain,
        "logo_url": response.brand.logos[0].url if response.brand.logos else None,
        "industries": getattr(response.brand, "industries", None),
    }


def scrape_markdown(client: ContextDev, url: str) -> dict[str, Any]:
    response = with_retry(lambda: client.web.web_scrape_md(url=url))
    return {
        "url": response.url,
        "markdown": response.markdown,
        "markdown_length": len(response.markdown or ""),
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
    return {
        "title": response.brand.title,
        "domain": response.brand.domain,
        "industries": getattr(response.brand, "industries", None),
    }


def classify_naics(client: ContextDev, input_value: str) -> dict[str, Any]:
    response = with_retry(lambda: client.industry.retrieve_naics(input=input_value))
    codes = [
        {"code": c.code, "name": c.name, "confidence": c.confidence}
        for c in (response.codes or [])
    ]
    return {
        "domain": response.domain,
        "codes": codes,
    }