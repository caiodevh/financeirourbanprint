#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ -x "dist/FinanceiroUrbanoPrint" ]]; then
  nohup "dist/FinanceiroUrbanoPrint" >/dev/null 2>&1 &
  exit 0
fi

if [[ -x ".venv/bin/python" ]]; then
  nohup ".venv/bin/python" "run.py" >/dev/null 2>&1 &
  exit 0
fi

nohup python "run.py" >/dev/null 2>&1 &
