#!/usr/bin/env bash
# Round-2 extra seeds (Qwen, both datasets): seeds 43 and 44 reuse the seed-42 round-2 compressor and retrain only the
# end-to-end stage, once with rule-based splits and once with the learned budget head; each is evaluated and diagnosed.
# Needs round 2 (07_round2.sh) finished for seed 42. HotpotQA on the first GPU in GPUS, 2Wiki on the second. Resumable.
set -euo pipefail
cd "$(dirname "$0")"
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
BACKBONES=${BACKBONES:-qwen} TAG=seeds ./_launch.sh --preset round2_seeds --seeds "${SEEDS:-43,44}" --diagnose
