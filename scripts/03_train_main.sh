#!/usr/bin/env bash
# Main runs for both backbones and both datasets (nested_M32 + fixed_M16), 3 seeds, bf16, in the background.
# Resumable: finished stages are skipped, so re-run this after any interruption.
set -euo pipefail
cd "$(dirname "$0")"
TAG=main ./_launch.sh --preset main --seeds "${SEEDS:-42,43,44}"
