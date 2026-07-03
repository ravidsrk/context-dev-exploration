#!/usr/bin/env python3
"""
Single planning CLI for scout + MCP code-mode loops (Python and TypeScript executors).

Usage:
  python agents/plan_cli.py scout <domain> [brand_json]
  python agents/plan_cli.py mcp <goal> [hits_json]

Stdout: JSON with plan_steps/execute_plan and policy_source.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.llm_policy import plan_mcp_execute, plan_scout_perception  # noqa: E402
from agents.mcp_client import extract_domain_from_goal  # noqa: E402
from agents.mcp_op_map import normalize_execute_plan  # noqa: E402

DEFAULT_SCOUT_GOAL = (
    "Build a sales intelligence dossier with industry, site scale, and pricing signals."
)


def _parse_json(s: str | None, default: Any) -> Any:
    if not s:
        return default
    return json.loads(s)


def cmd_scout(domain: str, brand_json: str | None, goal: str | None) -> dict[str, Any]:
    brand = _parse_json(brand_json, {"title": None, "logo_url": None})
    steps, policy_source = plan_scout_perception(
        domain, brand, goal or DEFAULT_SCOUT_GOAL
    )
    return {
        "domain": domain,
        "goal": goal or DEFAULT_SCOUT_GOAL,
        "plan_steps": steps,
        "policy_source": policy_source,
    }


def cmd_mcp(goal: str, hits_json: str | None) -> dict[str, Any]:
    hits = _parse_json(hits_json, [])
    domain = extract_domain_from_goal(goal)
    raw_plan, policy_source = plan_mcp_execute(goal, hits)
    execute_plan = normalize_execute_plan(goal, raw_plan, hits, domain)
    return {
        "goal": goal,
        "domain": domain,
        "execute_plan": execute_plan,
        "policy_source": policy_source,
        "raw_plan": raw_plan,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent planning CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    scout_p = sub.add_parser("scout", help="Plan scout perceive steps")
    scout_p.add_argument("domain")
    scout_p.add_argument("brand_json", nargs="?", default=None, help="JSON brand object")
    scout_p.add_argument("--goal", default=None)

    mcp_p = sub.add_parser("mcp", help="Plan MCP execute steps")
    mcp_p.add_argument("goal")
    mcp_p.add_argument("hits_json", nargs="?", default=None, help="JSON search_docs hits")

    args = parser.parse_args()
    if args.command == "scout":
        out = cmd_scout(args.domain, args.brand_json, args.goal)
    else:
        out = cmd_mcp(args.goal, args.hits_json)

    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())