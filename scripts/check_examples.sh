#!/usr/bin/env bash
# Compile and run every course example. Usage: scripts/check_examples.sh [--update] [filter...]
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/check_examples.py "$@"
