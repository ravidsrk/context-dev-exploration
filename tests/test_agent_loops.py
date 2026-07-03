"""Tests for agent loop modules (mocked Context.dev + LLM policy)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import agents.mcp_code_mode_loop as code_mode
import agents.research_scout_loop as scout_loop
from tests.test_mcp_op_map import LOG_SEARCH_HITS


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


def test_mcp_code_mode_executes_camelcase_llm_plan():
    """
    Reproduces the real failing seam: LLM returns client.brand.retrieveSimplified
    and client.web.extractStyleguide — normalize must canonicalize before execute.
    """
    goal = "Get stripe.com brand identity, design tokens, and site scale for a sales dossier"
    fake_hits = [
        {
            "id": hid,
            "signature": "",
            "returns": "",
            "credits": "",
            "description": "",
        }
        for hid in LOG_SEARCH_HITS
    ]
    llm_raw_plan = [
        {"op": "client.brand.retrieveSimplified", "args": {"domain": "stripe.com"}},
        {"op": "client.web.extractStyleguide", "args": {"domain": "stripe.com"}},
    ]
    fake_brand = {"title": "Stripe", "logo_url": "https://logo.test/x.jpg"}
    fake_style = {"color_count": 3, "has_typography": True}
    fake_sitemap = {"url_count": 6165, "sample_urls": ["https://stripe.com/legal"]}

    with (
        patch.object(code_mode, "hosted_search_docs", return_value=(fake_hits, "hosted_mcp")),
        patch.object(code_mode, "plan_mcp_execute", return_value=(llm_raw_plan, "llm")),
        patch.object(code_mode, "create_client", return_value=MagicMock()),
        patch.object(code_mode, "retrieve_brand", return_value=fake_brand),
        patch.object(code_mode, "extract_styleguide", return_value=fake_style),
        patch.object(code_mode, "scrape_sitemap", return_value=fake_sitemap),
    ):
        result = code_mode.run_code_mode_loop(goal)

    assert result["search_docs"]["source"] == "hosted_mcp"
    assert result["policy_source"] == "llm"
    assert result["ops_run"] == [
        "brand.retrieve(stripe.com)",
        "web.extract_styleguide(stripe.com)",
        "web.scrape_sitemap(stripe.com)",
    ]
    assert result["credits_estimated"] == 21
    assert result["result"]["identity"]["title"] == "Stripe"
    assert result["result"]["design_tokens"]["color_count"] == 3
    assert result["result"]["site_scale"]["url_count"] == 6165
    # execute_plan in output must be canonical, not camelCase
    assert all(
        s["op"] in ("brand.retrieve", "web.extract_styleguide", "web.scrape_sitemap")
        for s in result["execute_plan"]
    )


def test_search_docs_local_fallback_on_mcp_error():
    with patch.object(code_mode, "hosted_search_docs", side_effect=RuntimeError("network")):
        hits, source = code_mode.search_docs("brand logo retrieve domain")
    assert "local_fallback" in source
    assert any("brand.retrieve" in h["id"] for h in hits)