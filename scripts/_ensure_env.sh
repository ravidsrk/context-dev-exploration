#!/usr/bin/env bash
# Shared venv + npm install for agent/probe scripts.
set -euo pipefail
_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "${_ROOT}/.venv/bin/python" ]]; then
  python3 -m venv "${_ROOT}/.venv"
  "${_ROOT}/.venv/bin/pip" install -r "${_ROOT}/requirements.txt"
fi

export PATH="${_ROOT}/.venv/bin:${PATH}"

if [[ ! -d "${_ROOT}/typescript/node_modules" ]]; then
  (cd "${_ROOT}/typescript" && npm install)
fi