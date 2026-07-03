"""Tests for agent loop modules (mocked Context.dev client)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import agents.mcp_style_loop as mcp_loop
import agents.research_scout_loop as scout_loop


def test_research_scout_loop_structure():
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
    ):
        result = scout_loop.run_loop("stripe.com")

    assert result["company"] == "Stripe"
    assert result["logo_url"] == "https://logo.test/x.jpg"
    assert result["industry"]["code"] == "522320"
    assert result["sitemap_urls"] == 100
    assert result["has_pricing_content"] is True
    assert result["credits_estimated"] >= 20
    assert "observation" in result
    assert 0 < result["observation"]["confidence"] <= 1.0


def test_mcp_style_loop_composition():
    fake_brand = {"title": "Stripe", "logo_url": "https://logo.test/x.jpg"}
    fake_style = {"color_count": 3, "has_typography": True}
    fake_sitemap = {"url_count": 50, "sample_urls": ["https://stripe.com/legal"]}

    with (
        patch.object(mcp_loop, "create_client", return_value=MagicMock()),
        patch.object(mcp_loop, "retrieve_brand", return_value=fake_brand),
        patch.object(mcp_loop, "extract_styleguide", return_value=fake_style),
        patch.object(mcp_loop, "scrape_sitemap", return_value=fake_sitemap),
    ):
        result = mcp_loop.execute_composed("stripe.com")

    assert result["identity"]["title"] == "Stripe"
    assert result["design_tokens"]["color_count"] == 3
    assert result["site_scale"]["url_count"] == 50
    assert len(result["composition"]) == 3
    assert result["credits_estimated"] == 21