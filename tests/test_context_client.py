"""Unit tests for Context.dev client — mocked + optional integration."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from context.dev import APIStatusError

from src.context_client import (
    RETRYABLE_STATUS,
    classify_naics,
    classify_sic,
    crawl_markdown,
    extract_fonts,
    extract_styleguide,
    get_api_key,
    identify_transaction,
    prefetch_domain,
    retrieve_brand,
    scrape_markdown,
    scrape_screenshot,
    scrape_sitemap,
    with_retry,
)


def _brand_response(title="Acme", domain="acme.com", logos=None, industries=None):
    logos = logos if logos is not None else [SimpleNamespace(url="https://cdn/logo.png")]
    return SimpleNamespace(
        brand=SimpleNamespace(
            title=title,
            domain=domain,
            logos=logos,
            industries=industries,
        )
    )


class TestGetApiKey:
    def test_raises_without_env(self, monkeypatch):
        monkeypatch.delenv("CONTEXT_DEV_API_KEY", raising=False)
        monkeypatch.delenv("CONTEXT_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="CONTEXT_DEV_API_KEY"):
            get_api_key()

    def test_reads_context_dev_api_key(self, monkeypatch):
        monkeypatch.setenv("CONTEXT_DEV_API_KEY", "ctxt_secret_test")
        assert get_api_key() == "ctxt_secret_test"

    def test_falls_back_to_context_api_key(self, monkeypatch):
        monkeypatch.delenv("CONTEXT_DEV_API_KEY", raising=False)
        monkeypatch.setenv("CONTEXT_API_KEY", "ctxt_secret_fallback")
        assert get_api_key() == "ctxt_secret_fallback"


class TestWithRetry:
    def test_succeeds_first_try(self):
        assert with_retry(lambda: 42) == 42

    def test_retries_on_408(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 2:
                raise APIStatusError(
                    message="timeout",
                    response=MagicMock(status_code=408),
                    body=None,
                )
            return "ok"

        with patch("src.context_client.time.sleep"):
            assert with_retry(flaky) == "ok"
        assert calls["n"] == 2

    def test_retries_on_429(self):
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise APIStatusError(
                    message="rate limited",
                    response=MagicMock(status_code=429),
                    body=None,
                )
            return "ok"

        with patch("src.context_client.time.sleep"):
            assert with_retry(flaky, max_retries=3) == "ok"
        assert calls["n"] == 3

    def test_does_not_retry_on_401(self):
        def fail():
            raise APIStatusError(
                message="unauthorized",
                response=MagicMock(status_code=401),
                body=None,
            )

        with pytest.raises(APIStatusError):
            with_retry(fail)

    def test_retryable_status_codes(self):
        assert 408 in RETRYABLE_STATUS
        assert 429 in RETRYABLE_STATUS


class TestRetrieveBrand:
    def test_maps_brand_fields(self):
        client = MagicMock()
        client.brand.retrieve.return_value = _brand_response()
        result = retrieve_brand(client, "acme.com")
        assert result["title"] == "Acme"
        assert result["domain"] == "acme.com"
        assert result["logo_url"] == "https://cdn/logo.png"

    def test_handles_empty_logos(self):
        client = MagicMock()
        client.brand.retrieve.return_value = _brand_response(logos=[])
        result = retrieve_brand(client, "acme.com")
        assert result["logo_url"] is None
        assert result["title"] == "Acme"

    def test_handles_missing_brand_object(self):
        client = MagicMock()
        client.brand.retrieve.return_value = SimpleNamespace(brand=None)
        result = retrieve_brand(client, "acme.com")
        assert result["title"] is None
        assert result["domain"] == "acme.com"


class TestScrapeMarkdown:
    def test_returns_markdown_length(self):
        client = MagicMock()
        client.web.web_scrape_md.return_value = SimpleNamespace(
            url="https://acme.com",
            markdown="# Hello\n\nWorld",
        )
        result = scrape_markdown(client, "https://acme.com")
        assert result["markdown_length"] == 14
        assert "Hello" in result["markdown"]

    def test_handles_none_markdown(self):
        client = MagicMock()
        client.web.web_scrape_md.return_value = SimpleNamespace(url="https://acme.com", markdown=None)
        result = scrape_markdown(client, "https://acme.com")
        assert result["markdown_length"] == 0


class TestIdentifyTransaction:
    def test_resolves_merchant(self):
        client = MagicMock()
        client.brand.identify_from_transaction.return_value = _brand_response(
            title="Starbucks", domain="starbucks.com"
        )
        result = identify_transaction(client, "STARBUCKS 123", mcc="5814")
        assert result["domain"] == "starbucks.com"
        client.brand.identify_from_transaction.assert_called_once()

    def test_handles_missing_brand(self):
        client = MagicMock()
        client.brand.identify_from_transaction.return_value = SimpleNamespace(brand=None)
        result = identify_transaction(client, "UNKNOWN MERCHANT")
        assert result["domain"] is None


class TestClassifyNaics:
    def test_parses_codes(self):
        client = MagicMock()
        client.industry.retrieve_naics.return_value = SimpleNamespace(
            domain="stripe.com",
            codes=[SimpleNamespace(code="522320", name="FinTech", confidence="high")],
        )
        result = classify_naics(client, "stripe.com")
        assert result["codes"][0]["code"] == "522320"
        assert result["domain"] == "stripe.com"


class TestClassifySic:
    def test_parses_sic_codes(self):
        client = MagicMock()
        client.industry.retrieve_sic.return_value = SimpleNamespace(
            domain="stripe.com",
            codes=[SimpleNamespace(code="7372", name="Software", confidence="medium")],
        )
        result = classify_sic(client, "stripe.com")
        assert result["codes"][0]["code"] == "7372"


class TestPrefetchDomain:
    def test_returns_status(self):
        client = MagicMock()
        client.utility.prefetch.return_value = SimpleNamespace(status="ok", domain="stripe.com")
        result = prefetch_domain(client, "stripe.com")
        assert result["status"] == "ok"


class TestExtractStyleguide:
    def test_counts_colors(self):
        client = MagicMock()
        colors = SimpleNamespace(accent="#533afd", background="#ffffff", text="#81b81a")
        client.web.extract_styleguide.return_value = SimpleNamespace(
            domain="stripe.com",
            styleguide=SimpleNamespace(colors=colors, typography=SimpleNamespace()),
        )
        result = extract_styleguide(client, "stripe.com")
        assert result["color_count"] == 3
        assert result["has_typography"] is True


class TestExtractFonts:
    def test_lists_font_names(self):
        client = MagicMock()
        client.web.extract_fonts.return_value = SimpleNamespace(
            domain="stripe.com",
            fonts=[SimpleNamespace(font="Inter"), SimpleNamespace(font="Roboto")],
        )
        result = extract_fonts(client, "stripe.com")
        assert result["font_count"] == 2
        assert "Inter" in result["font_names"]


class TestScrapeScreenshot:
    def test_returns_screenshot_url(self):
        client = MagicMock()
        client.web.screenshot.return_value = SimpleNamespace(
            screenshot="https://cdn.example.com/shot.png"
        )
        result = scrape_screenshot(client, "stripe.com")
        assert result["has_screenshot"] is True


class TestCrawlMarkdown:
    def test_counts_succeeded_pages(self):
        client = MagicMock()
        client.web.web_crawl_md.return_value = SimpleNamespace(
            results=[
                SimpleNamespace(success=True, markdown="# Page 1"),
                SimpleNamespace(success=True, markdown="# Page 2"),
            ],
            metadata=SimpleNamespace(num_succeeded=2),
        )
        result = crawl_markdown(client, "https://stripe.com", max_pages=2)
        assert result["num_succeeded"] == 2
        assert result["pages_with_markdown"] == 2


class TestScrapeSitemap:
    def test_returns_url_count(self):
        client = MagicMock()
        client.web.web_scrape_sitemap.return_value = SimpleNamespace(
            urls=["https://stripe.com/", "https://stripe.com/pricing"]
        )
        result = scrape_sitemap(client, "stripe.com")
        assert result["url_count"] == 2


@pytest.mark.integration
class TestLiveIntegration:
    """Run with: CONTEXT_DEV_API_KEY=... pytest -m integration -v"""

    def test_brand_retrieve_live(self):
        from src.context_client import create_client

        client = create_client()
        result = retrieve_brand(client, "stripe.com")
        assert result["title"]
        assert result["logo_url"]

    def test_scrape_markdown_live(self):
        from src.context_client import create_client

        client = create_client()
        result = scrape_markdown(client, "https://stripe.com")
        assert result["markdown_length"] > 0