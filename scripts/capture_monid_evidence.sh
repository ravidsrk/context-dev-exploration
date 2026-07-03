#!/usr/bin/env bash
# Capture raw Monid CLI transcripts for verification evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${ROOT}/evidence/monid-deep-runs.log"
SCRATCH="${SCRATCH:-/var/folders/x1/lp15c92s5mj6jnccnpqf98g80000gn/T/grok-goal-95a1fe78957a/implementer}"
mkdir -p "$SCRATCH" "$(dirname "$LOG")"
export NO_COLOR=1

if [[ -z "${MONID_API_KEY:-}" ]]; then
  echo "ERROR: MONID_API_KEY must be set" >&2
  exit 1
fi

: >"$LOG"

{
  echo "========== MONID DISCOVER: job postings =========="
  monid discover -q "job postings hiring signals company" -l 3
  echo "discover_exit: $?"

  echo ""
  echo "========== MONID DISCOVER: tech stack =========="
  monid discover -q "tech stack detection website technologies" -l 3
  echo "discover_exit: $?"

  echo ""
  echo "========== MONID DISCOVER: news =========="
  monid discover -q "news articles company press releases" -l 3
  echo "discover_exit: $?"

  echo ""
  echo "========== MONID LIVE RUN: LinkedIn jobs (Stripe) =========="
  monid run -p tikhub -e /api/v1/linkedin/web_v2/search_jobs \
    --query '{"keywords":"Stripe","count":3,"time_range":"past_month"}' -w 60
  echo "run_exit: $?"

  echo ""
  echo "========== MONID LIVE RUN: company-tech-stack =========="
  monid run -p api.strale.io -e /x402/company-tech-stack \
    --query '{"domain":"stripe.com"}' -w 60
  echo "run_exit: $?"

  echo ""
  echo "========== MONID LIVE RUN: tech-stack-detect =========="
  monid run -p api.strale.io -e /x402/tech-stack-detect \
    --query '{"domain":"stripe.com"}' -w 60
  echo "run_exit: $?"
} 2>&1 | tee "$LOG"

cp "$LOG" "$SCRATCH/monid-deep-runs.log"
echo "Wrote $LOG and $SCRATCH/monid-deep-runs.log"