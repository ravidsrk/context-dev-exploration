"""Tests for MCP op canonicalization — exact ids from failed agent-loop.log capture."""

from __future__ import annotations

from agents.mcp_op_map import canonicalize_op, normalize_execute_plan

# From evidence/agent-loop.log execute_plan (hosted MCP + LLM output)
LOG_EXECUTE_OPS = [
    "client.brand.retrieveSimplified",
    "client.web.extractStyleguide",
]

LOG_SEARCH_HITS = [
    "client.brand.identifyFromTransaction",
    "client.brand.retrieveSimplified",
    "client.ai.extractProducts",
    "client.web.extractStyleguide",
    "client.brand.retrieveByTicker",
]


def test_canonicalize_exact_agent_loop_ids():
    assert canonicalize_op("client.brand.retrieveSimplified") == "brand.retrieve"
    assert canonicalize_op("client.web.extractStyleguide") == "web.extract_styleguide"


def test_canonicalize_common_hosted_variants():
    assert canonicalize_op("client.brand.retrieve") == "brand.retrieve"
    assert canonicalize_op("client.brand.webScrapeSitemap") == "web.scrape_sitemap"
    assert canonicalize_op("brand.retrieve") == "brand.retrieve"


def test_unmapped_ops_return_none():
    assert canonicalize_op("client.brand.identifyFromTransaction") is None
    assert canonicalize_op("client.ai.extractProducts") is None


def test_normalize_maps_llm_camelcase_plan():
    goal = "Get stripe.com brand identity, design tokens, and site scale for a sales dossier"
    raw_plan = [
        {"op": "client.brand.retrieveSimplified", "args": {"domain": "stripe.com"}},
        {"op": "client.web.extractStyleguide", "args": {"domain": "stripe.com"}},
    ]
    hits = [{"id": id_} for id_ in LOG_SEARCH_HITS]
    plan = normalize_execute_plan(goal, raw_plan, hits, "stripe.com")

    ops = [s["op"] for s in plan]
    assert ops[0] == "brand.retrieve"
    assert ops[1] == "web.extract_styleguide"
    assert "web.scrape_sitemap" in ops  # goal mentions site scale
    assert all(s["args"]["domain"] == "stripe.com" for s in plan)


def test_normalize_from_hits_when_raw_plan_empty():
    hits = [{"id": id_} for id_ in LOG_SEARCH_HITS]
    plan = normalize_execute_plan("stripe.com brand", [], hits, "stripe.com")
    ops = {s["op"] for s in plan}
    assert "brand.retrieve" in ops
    assert "web.extract_styleguide" in ops