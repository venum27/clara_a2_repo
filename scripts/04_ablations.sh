#!/usr/bin/env bash
# Ablation runs, one seed, after 03 has finished (the E2E-only ablations reuse the seed-42 nested checkpoint).
set -euo pipefail
cd "$(dirname "$0")"
TAG=ablations ./_launch.sh --preset ablations --seeds "${SEEDS:-42}"
