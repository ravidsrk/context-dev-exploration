#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/evidence/agent-loop.log"
DOMAIN="${1:-stripe.com}"

{
  echo "========== Agent loops @ $(date -u +%Y-%m-%dT%H:%M:%SZ) domain=$DOMAIN =========="
  echo "--- research_scout_loop ---"
  python "$ROOT/agents/research_scout_loop.py" "$DOMAIN"
  echo "--- mcp_style_loop ---"
  python "$ROOT/agents/mcp_style_loop.py" "$DOMAIN"
} | tee "$LOG"

echo "Wrote $LOG"