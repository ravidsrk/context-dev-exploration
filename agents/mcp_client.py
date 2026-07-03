"""HTTP client for Context.dev hosted MCP (search_docs + execute)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

MCP_URL = os.environ.get("CONTEXT_DEV_MCP_URL", "https://context-dev.stlmcp.com")


def _api_key() -> str:
    key = os.environ.get("CONTEXT_DEV_API_KEY") or os.environ.get("CONTEXT_API_KEY")
    if not key:
        raise RuntimeError("CONTEXT_DEV_API_KEY is required for hosted MCP calls")
    return key


def _parse_sse_payload(raw: str) -> dict[str, Any]:
    for line in raw.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    raise RuntimeError(f"No SSE data in MCP response: {raw[:300]}")


def _mcp_request(method: str, params: dict[str, Any] | None = None, req_id: int = 1) -> dict[str, Any]:
    body: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        body["params"] = params

    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "context-dev-exploration/1.0 (MCP client)",
            "x-context-dev-api-key": _api_key(),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"MCP HTTP {e.code}: {e.read().decode()[:500]}") from e

    payload = _parse_sse_payload(raw)
    if "error" in payload:
        raise RuntimeError(f"MCP error: {payload['error']}")
    return payload.get("result", payload)


def hosted_search_docs(
    query: str,
    language: str = "typescript",
    detail: str = "default",
) -> tuple[list[dict[str, str]], str]:
    """
    Call hosted MCP search_docs tool at context-dev.stlmcp.com.
    Returns (normalized_hits, source_tag).
    """
    result = _mcp_request(
        "tools/call",
        {
            "name": "search_docs",
            "arguments": {"query": query, "language": language, "detail": detail},
        },
        req_id=42,
    )
    content = result.get("content") or []
    text = ""
    for block in content:
        if block.get("type") == "text":
            text = block.get("text") or ""
            break
    if not text:
        raise RuntimeError("search_docs returned empty content")

    methods = json.loads(text)
    hits: list[dict[str, str]] = []
    for m in methods[:5]:
        hits.append(
            {
                "id": m.get("method", ""),
                "signature": (m.get("params") or [""])[0] if m.get("params") else "",
                "returns": m.get("summary", ""),
                "credits": "",
                "description": m.get("description", ""),
            }
        )
    return hits, "hosted_mcp"


def hosted_execute(code: str, intent: str = "") -> dict[str, Any]:
    """Call hosted MCP execute tool (TypeScript sandbox)."""
    args: dict[str, str] = {"code": code}
    if intent:
        args["intent"] = intent
    result = _mcp_request("tools/call", {"name": "execute", "arguments": args}, req_id=43)
    content = result.get("content") or []
    for block in content:
        if block.get("type") == "text":
            text = block.get("text") or ""
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"raw": text}
    return {"content": content}


def extract_domain_from_goal(goal: str) -> str:
    match = re.search(r"[\w-]+\.[\w]{2,}", goal.lower())
    return match.group() if match else "stripe.com"