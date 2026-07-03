"""Integration tests for MCP client using recorded SSE fixtures (real response shape)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from agents import mcp_client

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_hosted_search_docs_parses_recorded_sse():
    sse = (FIXTURES / "mcp_search_docs_sse.txt").read_text()
    with patch.object(mcp_client.urllib.request, "urlopen") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = sse.encode()
        with patch.object(mcp_client, "_api_key", return_value="test-key"):
            hits, source = mcp_client.hosted_search_docs("brand retrieve styleguide")

    assert source == "hosted_mcp"
    assert hits[0]["id"] == "client.brand.retrieve"
    assert any("extractStyleguide" in h["id"] for h in hits)


def test_hosted_execute_parses_recorded_sse():
    sse = (FIXTURES / "mcp_execute_sse.txt").read_text()
    with patch.object(mcp_client.urllib.request, "urlopen") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = sse.encode()
        with patch.object(mcp_client, "_api_key", return_value="test-key"):
            out = mcp_client.hosted_execute("async function run(client) { return {}; }", "test")

    assert out["result"]["identity"]["title"] == "Stripe"
    assert out["result"]["site_scale"]["url_count"] == 6165