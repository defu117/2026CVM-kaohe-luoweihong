#!/usr/bin/env bash
set -euo pipefail

echo "CPU spike test"
echo "Start time: $(date '+%F %T')"

if command -v stress-ng >/dev/null 2>&1; then
  stress-ng --cpu 2 --cpu-method matrixprod -t 60s
else
  echo "stress-ng not found; using a portable busy loop fallback"
  timeout 60s bash -c 'while :; do :; done' &
  timeout 60s bash -c 'while :; do :; done' &
  set +e
  wait
  set -e
fi

echo "End time: $(date '+%F %T')"
