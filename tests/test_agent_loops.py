"""Tests for agent loop modules (mocked + fixture-driven MCP path)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import agents.mcp_code_mode_loop as code_mode
import agents.research_scout_loop as scout_loop
from tests.test_mcp_op_map import LOG_SEARCH_HITS

FIXTURES = Path(__file__).resolve().parent / "fixtures"


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
        patch.object(scout_loop, "plan_scout_perception", return_value=(["naics", "sitemap"], "llm")),
    ):
        result = scout_loop.run_loop("stripe.com")

    assert result["company"] == "Stripe"
    assert result["policy_source"] == "llm"


def test_mcp_code_mode_uses_hosted_execute_path():
    """Full path: camelCase LLM plan → canonicalize → hosted_execute (not local SDK)."""
    goal = "Get stripe.com brand identity, design tokens, and site scale for a sales dossier"
    fake_hits = [{"id": hid, "signature": "", "returns": "", "credits": "", "description": ""} for hid in LOG_SEARCH_HITS]
    llm_raw_plan = [
        {"op": "client.brand.retrieveSimplified", "args": {"domain": "stripe.com"}},
        {"op": "client.web.extractStyleguide", "args": {"domain": "stripe.com"}},
    ]
    hosted_result = {
        "result": {
            "identity": {"title": "Stripe", "logo_url": "https://logo.test/x.jpg"},
            "design_tokens": {"color_count": 3, "has_typography": True},
            "site_scale": {"url_count": 6165, "sample_paths": ["https://stripe.com/legal"]},
        }
    }

    with (
        patch.object(code_mode, "hosted_search_docs", return_value=(fake_hits, "hosted_mcp")),
        patch.object(code_mode, "plan_mcp_execute", return_value=(llm_raw_plan, "llm")),
        patch.object(code_mode, "hosted_execute", return_value=hosted_result) as mock_exec,
    ):
        result = code_mode.run_code_mode_loop(goal)

    mock_exec.assert_called_once()
    ts_code = mock_exec.call_args[0][0]
    assert "client.web.extractStyleguide" in ts_code
    assert result["execute_source"] == "hosted_mcp_execute"
    assert result["ops_run"][0].startswith("hosted:execute")
    assert result["result"]["identity"]["title"] == "Stripe"
    assert result["credits_estimated"] == 21


def test_mcp_code_mode_end_to_end_via_recorded_sse_fixtures():
    """Drive search_docs + execute through real _mcp_request (urllib mocked to fixture SSE)."""
    goal = "Get stripe.com brand identity, design tokens, and site scale"
    search_sse = (FIXTURES / "mcp_search_docs_sse.txt").read_text().encode()
    execute_sse = (FIXTURES / "mcp_execute_sse.txt").read_text().encode()
    responses = [search_sse, execute_sse]
    llm_raw_plan = [
        {"op": "client.brand.retrieve", "args": {"domain": "stripe.com"}},
        {"op": "client.web.extractStyleguide", "args": {"domain": "stripe.com"}},
        {"op": "client.web.webScrapeSitemap", "args": {"domain": "stripe.com"}},
    ]

    def fake_urlopen(req, timeout=60):
        body = responses.pop(0)

        class Resp:
            def read(self):
                return body

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return Resp()

    with (
        patch("agents.mcp_client.urllib.request.urlopen", side_effect=fake_urlopen),
        patch("agents.mcp_client._api_key", return_value="test-key"),
        patch.object(code_mode, "plan_mcp_execute", return_value=(llm_raw_plan, "llm")),
    ):
        result = code_mode.run_code_mode_loop(goal)

    assert result["search_docs"]["source"] == "hosted_mcp"
    assert result["execute_source"] == "hosted_mcp_execute"
    assert result["execute_typescript"] is not None
    assert "async function run(client)" in result["execute_typescript"]
    assert result["result"]["identity"]["title"] == "Stripe"
    assert result["result"]["site_scale"]["url_count"] == 6165
    assert result["ops_run"][0].startswith("hosted:execute")


def test_mcp_code_mode_falls_back_to_local_on_execute_error():
    goal = "Get stripe.com brand and design tokens"
    fake_hits = [{"id": "client.brand.retrieve", "signature": "", "returns": "", "credits": "", "description": ""}]
    plan = [{"op": "brand.retrieve", "args": {"domain": "stripe.com"}}]
    fake_brand = {"title": "Stripe", "logo_url": "https://logo.test/x.jpg"}

    with (
        patch.object(code_mode, "hosted_search_docs", return_value=(fake_hits, "hosted_mcp")),
        patch.object(code_mode, "plan_mcp_execute", return_value=(plan, "llm")),
        patch.object(code_mode, "hosted_execute", side_effect=RuntimeError("sandbox down")),
        patch.object(code_mode, "create_client", return_value=MagicMock()),
        patch.object(code_mode, "retrieve_brand", return_value=fake_brand),
    ):
        result = code_mode.run_code_mode_loop(goal)

    assert "local_sdk_fallback" in result["execute_source"]
    assert result["result"]["identity"]["title"] == "Stripe"