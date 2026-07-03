"""Tests for TypeScript codegen used by hosted MCP execute."""

from __future__ import annotations

from context_dev.mcp.codegen import build_execute_typescript


def test_build_execute_typescript_includes_web_namespace():
    code = build_execute_typescript(
        "stripe.com",
        [
            {"op": "brand.retrieve", "args": {"domain": "stripe.com"}},
            {"op": "web.extract_styleguide", "args": {"domain": "stripe.com"}},
            {"op": "web.scrape_sitemap", "args": {"domain": "stripe.com"}},
        ],
    )
    assert "client.brand.retrieve" in code
    assert "client.web.extractStyleguide" in code
    assert "client.web.webScrapeSitemap" in code
    assert "filter(Boolean).length" in code
    assert "async function run(client)" in code
    # Hosted sandbox rejects client.brand.styleguide / brand.styleguide property access.
    assert "client.brand.styleguide" not in code
    assert "brand.styleguide" not in code
    assert "client.brand.webScrapeSitemap" not in code


def test_golden_codegen_from_agent_loop_execute_plan():
    """Golden plan from evidence/runs/agent-loop.log MCP section — must not TS2339 in sandbox."""
    plan = [
        {"op": "brand.retrieve", "args": {"domain": "stripe.com"}},
        {"op": "web.extract_styleguide", "args": {"domain": "stripe.com"}},
        {"op": "web.scrape_sitemap", "args": {"domain": "stripe.com"}},
    ]
    code = build_execute_typescript("stripe.com", plan)
    assert "client.web.extractStyleguide" in code
    assert "client.web.webScrapeSitemap" in code
    assert "client.brand.styleguide" not in code
    assert "client.brand.webScrapeSitemap" not in code
    assert "as {" not in code  # no Colors cast that broke sandbox