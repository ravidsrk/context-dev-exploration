"""Unit tests for Context.dev client — mocked + optional integration."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from context.dev import APIStatusError

from src.context_client import (
    RETRYABLE_STATUS,
    get_api_key,
    with_retry,
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


@pytest.mark.integration
class TestLiveIntegration:
    """Run with: CONTEXT_DEV_API_KEY=... pytest -m integration -v"""

    def test_brand_retrieve_live(self):
        from src.context_client import create_client, retrieve_brand

        client = create_client()
        result = retrieve_brand(client, "stripe.com")
        assert result["title"]
        assert result["logo_url"]

    def test_scrape_markdown_live(self):
        from src.context_client import create_client, scrape_markdown

        client = create_client()
        result = scrape_markdown(client, "https://stripe.com")
        assert result["markdown_length"] > 0