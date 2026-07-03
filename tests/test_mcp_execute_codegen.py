"""Tests for TypeScript codegen used by hosted MCP execute."""

from __future__ import annotations

from agents.mcp_execute_codegen import build_execute_typescript


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