#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/evidence/agent-loop.log"
SCRATCH="${SCRATCH:-/var/folders/x1/lp15c92s5mj6jnccnpqf98g80000gn/T/grok-goal-95a1fe78957a/implementer}"
DOMAIN="${1:-stripe.com}"
mkdir -p "$SCRATCH" "$(dirname "$LOG")"

if [[ -z "${CONTEXT_DEV_API_KEY:-}" ]]; then
  echo "ERROR: CONTEXT_DEV_API_KEY must be set" >&2
  exit 1
fi

GOAL="Get ${DOMAIN} brand identity, design tokens, and site scale for a sales dossier"

{
  echo "========== Agent loops @ $(date -u +%Y-%m-%dT%H:%M:%SZ) domain=$DOMAIN =========="
  echo "--- research_scout_loop (LLM plan) ---"
  python "$ROOT/agents/research_scout_loop.py" "$DOMAIN"
  echo "scout_exit: $?"
  echo "--- mcp_code_mode_loop (search_docs + execute) ---"
  python "$ROOT/agents/mcp_code_mode_loop.py" "$GOAL"
  echo "code_mode_exit: $?"
} | tee "$LOG"

cp "$LOG" "$SCRATCH/agent-loop.log"
echo "Wrote $LOG and $SCRATCH/agent-loop.log"