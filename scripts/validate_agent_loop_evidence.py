#!/usr/bin/env python3
"""Validate evidence/agent-loop.log contract (freshness + policy_source shape)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "evidence" / "agent-loop.log"

LEGACY_POLICY = frozenset({"typescript_heuristic", "typescript_direct"})
ALLOWED_POLICY = frozenset({"llm", "fallback"})

SOURCE_PATHS = [
    ROOT / "agents" / "plan_cli.py",
    ROOT / "agents" / "research_scout_loop.py",
    ROOT / "agents" / "mcp_code_mode_loop.py",
    ROOT / "typescript" / "src" / "scout_loop.ts",
    ROOT / "typescript" / "src" / "mcp_code_mode_loop.ts",
    ROOT / "typescript" / "src" / "plan_cli.ts",
]

SECTION_MARKERS = [
    ("python_scout", r"--- Python research_scout_loop.*?\n(.*?)\npython_scout_exit:"),
    ("python_mcp", r"--- Python mcp_code_mode_loop.*?\n(.*?)\npython_code_mode_exit:"),
    ("ts_scout", r"--- TypeScript scout_loop.*?\n(.*?)\nts_scout_exit:"),
    ("ts_mcp", r"--- TypeScript mcp_code_mode_loop.*?\n(.*?)\nts_code_mode_exit:"),
]


def _extract_json(block: str) -> dict:
    start = block.find("{")
    if start < 0:
        raise ValueError("no JSON object in section")
    depth = 0
    for i in range(start, len(block)):
        if block[i] == "{":
            depth += 1
        elif block[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(block[start : i + 1])
    raise ValueError("unbalanced JSON in section")


def _check_freshness() -> None:
    if not LOG.exists():
        raise SystemExit(f"MISSING: {LOG}")
    log_mtime = LOG.stat().st_mtime
    newest = max(p.stat().st_mtime for p in SOURCE_PATHS if p.exists())
    if log_mtime < newest - 1:
        raise SystemExit(
            f"STALE: {LOG} mtime older than planner/loop sources — re-run run_agent_loops.sh"
        )


def _check_legacy(text: str) -> None:
    for bad in LEGACY_POLICY:
        if bad in text:
            raise SystemExit(f"LEGACY policy_source string found: {bad}")


def _validate_section(name: str, data: dict) -> None:
    policy = data.get("policy_source")
    if policy not in ALLOWED_POLICY:
        raise SystemExit(f"{name}: policy_source={policy!r} not in {ALLOWED_POLICY}")

    if "mcp" in name:
        ops = data.get("ops_run") or []
        credits = data.get("credits_estimated") or 0
        if len(ops) < 1:
            raise SystemExit(f"{name}: ops_run empty")
        if credits <= 0:
            raise SystemExit(f"{name}: credits_estimated must be > 0")
        code = data.get("execute_typescript") or ""
        if "client.brand.styleguide" in code:
            raise SystemExit(f"{name}: execute_typescript uses forbidden client.brand.styleguide")
        if "client.brand.webScrapeSitemap" in code:
            raise SystemExit(f"{name}: execute_typescript uses forbidden client.brand.webScrapeSitemap")

    if "scout" in name:
        steps = data.get("plan_steps") or []
        if not steps:
            raise SystemExit(f"{name}: plan_steps empty")


def main() -> int:
    _check_freshness()
    text = LOG.read_text()
    _check_legacy(text)

    for name, pattern in SECTION_MARKERS:
        m = re.search(pattern, text, re.DOTALL)
        if not m:
            raise SystemExit(f"MISSING section: {name}")
        data = _extract_json(m.group(1))
        _validate_section(name, data)

    print(f"OK: {LOG} passes evidence contract (4 sections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())