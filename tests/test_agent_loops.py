"""Tests for agent loop modules (mocked Context.dev + LLM policy)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import agents.mcp_code_mode_loop as code_mode
import agents.research_scout_loop as scout_loop


def test_research_scout_loop_uses_llm_plan():
    fake_brand = {"title": "Stripe", "domain": "stripe.com", "logo_url": "https://logo.test/x.jpg"}
    fake_naics = {"domain": "stripe.com", "codes": [{"code": "522320", "name": "Fin", "confidence": "high"}]}
    fake_sitemap = {"url_count": 100, "sample_urls": ["https://stripe.com/a"]}
    fake_scrape = {"markdown": "x" * 600, "url": "https://stripe.com/pricing", "markdown_length": 600}

    with (
        patch.object(scout_loop, "create_client", return_value=MagicMock()),
        patch.object(scout_loop, "retrieve_brand", return_value=fake_brand),
        patch.object(scout_loop, "classify_naics", return_value=fake_naics),
        patch.object(scout_loop, "scrape_sitemap", return_value=fake_sitemap),
        patch.object(scout_loop, "scrape_markdown", return_value=fake_scrape),
        patch.object(
            scout_loop,
            "plan_scout_perception",
            return_value=(["naics", "sitemap"], "llm"),
        ),
    ):
        result = scout_loop.run_loop("stripe.com")

    assert result["company"] == "Stripe"
    assert result["policy_source"] == "llm"
    assert result["plan_steps"] == ["naics", "sitemap"]
    assert "classify_naics" in result["perceive_log"]
    assert result["observation"]["confidence"] > 0.5


def test_mcp_code_mode_uses_hosted_search_docs():
    fake_hits = [
        {
            "id": "client.brand.retrieve",
            "signature": "domain",
            "returns": "Retrieve brand",
            "credits": "",
            "description": "",
        }
    ]
    plan = [
        {"op": "brand.retrieve", "args": {"domain": "stripe.com"}},
        {"op": "web.extract_styleguide", "args": {"domain": "stripe.com"}},
        {"op": "web.scrape_sitemap", "args": {"domain": "stripe.com"}},
    ]
    fake_brand = {"title": "Stripe", "logo_url": "https://logo.test/x.jpg"}
    fake_style = {"color_count": 3, "has_typography": True}
    fake_sitemap = {"url_count": 50, "sample_urls": ["https://stripe.com/legal"]}

    with (
        patch.object(code_mode, "hosted_search_docs", return_value=(fake_hits, "hosted_mcp")),
        patch.object(code_mode, "create_client", return_value=MagicMock()),
        patch.object(code_mode, "retrieve_brand", return_value=fake_brand),
        patch.object(code_mode, "extract_styleguide", return_value=fake_style),
        patch.object(code_mode, "scrape_sitemap", return_value=fake_sitemap),
        patch.object(code_mode, "plan_mcp_execute", return_value=(plan, "llm")),
    ):
        result = code_mode.run_code_mode_loop("Get stripe.com brand and design tokens")

    assert result["search_docs"]["source"] == "hosted_mcp"
    assert result["policy_source"] == "llm"
    assert result["result"]["identity"]["title"] == "Stripe"
    assert result["credits_estimated"] == 21


def test_search_docs_local_fallback_on_mcp_error():
    with patch.object(code_mode, "hosted_search_docs", side_effect=RuntimeError("network")):
        hits, source = code_mode.search_docs("brand logo retrieve domain")
    assert "local_fallback" in source
    assert any("brand.retrieve" in h["id"] for h in hits)