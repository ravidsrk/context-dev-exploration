#!/usr/bin/env bash
# Capture raw Monid CLI transcripts + discover JSON (5+ queries, 3+ live runs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
LOG="${ROOT}/evidence/monid/monid-deep-runs.log"
EVIDENCE="${ROOT}/evidence/monid"
SCRATCH="${SCRATCH:-/var/folders/x1/lp15c92s5mj6jnccnpqf98g80000gn/T/grok-goal-95a1fe78957a/implementer}"
mkdir -p "$SCRATCH" "$EVIDENCE"
export NO_COLOR=1

if [[ -z "${MONID_API_KEY:-}" ]]; then
  echo "ERROR: MONID_API_KEY must be set" >&2
  exit 1
fi

: >"$LOG"

# 7 targeted discover queries (matches docs/research/MONID_DEEP_RESEARCH.md)
declare -a DISCOVER_QUERIES=(
  "company funding rounds venture capital"
  "job postings hiring signals company"
  "website change monitoring diff"
  "tech stack detection website technologies"
  "news articles company press releases"
  "app store reviews product ratings"
  "company social media posts"
)

idx=1
for q in "${DISCOVER_QUERIES[@]}"; do
  slug=$(echo "$q" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-40)
  json_out="${EVIDENCE}/monid-discover-${idx}-${slug}.json"
  {
    echo "========== MONID DISCOVER #$idx: $q =========="
    monid discover -q "$q" -l 3 -j | tee "$json_out"
    echo "discover_exit: ${PIPESTATUS[0]}"
    echo "json_saved: $json_out"
    echo ""
  } >>"$LOG" 2>&1
  cp "$json_out" "$SCRATCH/" 2>/dev/null || true
  idx=$((idx + 1))
done

{
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
} >>"$LOG" 2>&1

cp "$LOG" "$SCRATCH/monid-deep-runs.log"
echo "Wrote $LOG (${idx} discover queries) and $SCRATCH/monid-deep-runs.log"