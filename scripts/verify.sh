#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${CONTEXT_DEV_API_KEY:-}" ]]; then
  echo "ERROR: CONTEXT_DEV_API_KEY must be set"
  exit 1
fi

echo "=== Unit tests ==="
pytest tests/ -v -m "not integration"

echo "=== Live demos (run 1) ==="
python scripts/run_demos.py

echo "=== Live demos (run 2) ==="
python scripts/run_demos.py

echo "=== All verification passed ==="