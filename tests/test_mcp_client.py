"""Tests for hosted MCP client."""

from __future__ import annotations

import json
from unittest.mock import patch

from context_dev.mcp import client as mcp_client


def test_hosted_search_docs_parses_sse():
    sse = (
        'event: message\n'
        'data: {"result":{"content":[{"type":"text","text":"[{\\"method\\":\\"client.brand.retrieve\\",'
        '\\"summary\\":\\"Retrieve brand\\",\\"description\\":\\"by domain\\",\\"params\\":[\\"x\\"]}]"}]},'
        '"jsonrpc":"2.0","id":42}\n'
    )
    with patch.object(mcp_client.urllib.request, "urlopen") as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = sse.encode()
        with patch.object(mcp_client, "_api_key", return_value="test-key"):
            hits, source = mcp_client.hosted_search_docs("brand retrieve")

    assert source == "hosted_mcp"
    assert hits[0]["id"] == "client.brand.retrieve"
    assert "Retrieve brand" in hits[0]["returns"]


def test_search_docs_prefers_hosted_in_code_mode():
    import context_dev.loops.mcp_code_mode as loop

    fake_hits = [{"id": "client.brand.retrieve", "signature": "x", "returns": "y", "credits": "", "description": ""}]
    with patch.object(loop, "hosted_search_docs", return_value=(fake_hits, "hosted_mcp")):
        hits, source = loop.search_docs("brand retrieve stripe.com")
    assert source == "hosted_mcp"
    assert hits[0]["id"] == "client.brand.retrieve"