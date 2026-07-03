"""Tests for LLM policy fallbacks."""

from __future__ import annotations

from unittest.mock import patch

from agents.llm_policy import plan_mcp_execute, plan_scout_perception


def test_scout_policy_fallback_without_api_key():
    brand = {"title": "Acme", "logo_url": "https://x.test"}
    steps, source = plan_scout_perception("acme.com", brand)
    assert source == "fallback"
    assert "naics" in steps


def test_mcp_execute_fallback():
    docs = [{"id": "brand.retrieve", "signature": "x", "returns": "y", "credits": "10"}]
    plan, source = plan_mcp_execute("get stripe.com info", docs)
    assert source == "fallback"
    assert plan[0]["op"] == "brand.retrieve"


def test_scout_policy_llm_path():
    brand = {"title": "Stripe", "logo_url": "https://x.test"}
    with patch(
        "agents.llm_policy._openrouter_chat",
        return_value='["naics","pricing_scrape"]',
    ):
        steps, source = plan_scout_perception("stripe.com", brand)
    assert source == "llm"
    assert steps == ["naics", "pricing_scrape"]