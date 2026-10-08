#!/usr/bin/env bash
# Baseline from the ORIGINAL CLaRa code (apple/ml-clara), Qwen2.5-0.5B, trained on exactly our data and evaluated with
# exactly our metrics. Run official_clara/setup_official.sh once first. Runs in the background, one GPU per dataset.
#   CRS: compression rates to train (default 16 = 16 vectors/doc, 64 per question like our B=64; add 32 for B=32)
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
source scripts/_gpus.sh
[ -f official_clara/.venv/bin/activate ] || { echo "run official_clara/setup_official.sh first"; exit 1; }
"$PY" official_clara/convert_data.py --datasets "${DATASETS:-hotpotqa,2wiki}" --k "${K:-4}"
mkdir -p logs
for ds in $(echo "${DATASETS:-hotpotqa,2wiki}" | tr ',' ' '); do
    gpu=$(gpu_for "$ds"); warn_if_busy "$gpu"
    ( for cr in $(echo "${CRS:-16}" | tr ',' ' '); do
          CUDA_VISIBLE_DEVICES=$gpu PORT=$((29500 + gpu * 100 + cr)) official_clara/run_official.sh "$ds" "$cr"
      done ) >> "logs/official_${ds}.log" 2>&1 &
    echo "GPU $gpu: official CLaRa on $ds (compression rates ${CRS:-16}) -> logs/official_${ds}.log"
done
echo "running in the background. Check progress: ./scripts/status.sh"
