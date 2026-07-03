#!/usr/bin/env bash
# Run Python + TypeScript probes twice; full output (no truncation).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/evidence/dual-lang-demos.log"
SCRATCH="${SCRATCH:-/var/folders/x1/lp15c92s5mj6jnccnpqf98g80000gn/T/grok-goal-95a1fe78957a/implementer}"
mkdir -p "$SCRATCH" "$(dirname "$LOG")"
: >"$LOG"

if [[ -z "${CONTEXT_DEV_API_KEY:-}" ]]; then
  echo "ERROR: CONTEXT_DEV_API_KEY must be set" >&2
  exit 1
fi

run_once() {
  local n=$1
  {
    echo "========== RUN $n @ $(date -u +%Y-%m-%dT%H:%M:%SZ) =========="
    echo "--- Python demos ---"
    (cd "$ROOT" && python scripts/run_demos.py)
    echo "python_exit: $?"
    echo "--- TypeScript probe ---"
    (cd "$ROOT/typescript" && npm run probe)
    echo "typescript_exit: $?"
    echo ""
  } | tee -a "$LOG"
}

run_once 1
run_once 2

cp "$LOG" "$SCRATCH/dual-lang-demos.log"
echo "Wrote $LOG and $SCRATCH/dual-lang-demos.log"