#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${DATA_DIR:-/data}/samples"
mkdir -p "${DATA_DIR:-/data}/flamegraphs"
mkdir -p "${DATA_DIR:-/data}/tmp"

exec python3 -m profiler.server

