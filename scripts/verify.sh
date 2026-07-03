#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="${SCRATCH:-/var/folders/x1/lp15c92s5mj6jnccnpqf98g80000gn/T/grok-goal-95a1fe78957a/implementer}"
mkdir -p "$SCRATCH"

if [[ -z "${CONTEXT_DEV_API_KEY:-}" ]]; then
  echo "ERROR: CONTEXT_DEV_API_KEY must be set"
  exit 1
fi

echo "=== Unit tests ==="
make -C "$ROOT" test 2>&1 | tee "$SCRATCH/pytest-verify.log"

echo "=== Dual-language probes (2 runs) ==="
bash "$ROOT/scripts/run_dual_lang_probes.sh"

echo "=== Agent loops (scout + MCP code mode + evidence validator) ==="
bash "$ROOT/scripts/run_agent_loops.sh" stripe.com
python "$ROOT/scripts/validate_agent_loop_evidence.py"

if [[ -n "${MONID_API_KEY:-}" ]]; then
  echo "=== Monid evidence capture ==="
  bash "$ROOT/scripts/capture_monid_evidence.sh"
else
  echo "SKIP: MONID_API_KEY not set — monid capture skipped"
fi

echo "=== All verification passed ==="