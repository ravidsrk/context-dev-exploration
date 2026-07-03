#!/usr/bin/env bash
# Run Python + TypeScript probes twice; append to dual-lang-demos.log
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/evidence/dual-lang-demos.log"
: >"$LOG"

run_once() {
  local n=$1
  {
    echo "========== RUN $n @ $(date -u +%Y-%m-%dT%H:%M:%SZ) =========="
    echo "--- Python demos ---"
    cd "$ROOT" && python scripts/run_demos.py 2>&1 | head -40
    echo "--- TypeScript probe ---"
    cd "$ROOT/typescript" && npm run probe 2>&1
    echo ""
  } | tee -a "$LOG"
}

run_once 1
run_once 2
echo "Wrote $LOG"