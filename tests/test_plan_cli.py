"""Tests for shared plan_cli.py planner."""

from __future__ import annotations

import json
from unittest.mock import patch

from context_dev.planning.cli import cmd_mcp, cmd_scout


def test_cmd_scout_fallback_without_openrouter():
    with patch.dict("os.environ", {"OPEN_ROUTER_KEY": ""}, clear=False):
        out = cmd_scout("stripe.com", json.dumps({"title": "Stripe", "logo_url": "x"}), None)
    assert out["policy_source"] == "fallback"
    assert "naics" in out["plan_steps"]


def test_cmd_mcp_normalizes_camelcase_plan():
    hits = [{"id": "client.web.extractStyleguide", "signature": "", "returns": "", "credits": "", "description": ""}]
    raw = [{"op": "client.brand.retrieveSimplified", "args": {"domain": "stripe.com"}}]
    goal = "Get stripe.com brand identity, design tokens, and site scale"
    with (
        patch.dict("os.environ", {"OPEN_ROUTER_KEY": ""}, clear=False),
        patch("context_dev.planning.cli.plan_mcp_execute", return_value=(raw, "llm")),
    ):
        out = cmd_mcp(goal, json.dumps(hits))
    ops = [s["op"] for s in out["execute_plan"]]
    assert "brand.retrieve" in ops
    assert out["policy_source"] == "llm"