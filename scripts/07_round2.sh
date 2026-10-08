#!/usr/bin/env bash
# Round 2 (Qwen, both datasets, seed 42): nested pretraining with the loss on EVERY prefix length in every step, 6 epochs,
# with rule-based splits and with the learned budget head; plus fixed-16 retrained for 6 epochs. After each evaluation the
# memory diagnostic runs automatically. HotpotQA on the first GPU in GPUS, 2Wiki on the second. Resumable.
set -euo pipefail
cd "$(dirname "$0")"
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
BACKBONES=${BACKBONES:-qwen} TAG=round2 ./_launch.sh --preset round2 --seeds "${SEEDS:-42}" --diagnose
