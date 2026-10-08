#!/usr/bin/env bash
# Single-sample ablation (Qwen, both datasets): the budget head trained with ONE sampled split per question instead of
# two, on the final-configuration compressor, E2E seeds 42-44, each evaluated with the memory diagnostic. Tests
# whether the gain from training with the budget head comes from averaging the answer loss over two splits.
# The three seeds of a dataset run in parallel on its GPU; SEQUENTIAL=1 runs them one after another. Resumable.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
source scripts/_gpus.sh
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
mkdir -p logs
for ds in $(echo "${DATASETS:-hotpotqa,2wiki}" | tr ',' ' '); do
    gpu=$(gpu_for "$ds"); warn_if_busy "$gpu"
    if [ "${SEQUENTIAL:-0}" = "1" ]; then
        ( CUDA_VISIBLE_DEVICES=$gpu "$PY" run_pipeline.py --backbones qwen --datasets "$ds" --amp bf16 --require_data \
              --preset round2_s1 --seeds "${SEEDS:-42,43,44}" --diagnose ) >> "logs/s1_qwen_${ds}.log" 2>&1 &
    else
        for s in $(echo "${SEEDS:-42,43,44}" | tr ',' ' '); do
            ( CUDA_VISIBLE_DEVICES=$gpu "$PY" run_pipeline.py --backbones qwen --datasets "$ds" --amp bf16 --require_data \
                  --preset round2_s1 --seeds "$s" --diagnose ) >> "logs/s1_qwen_${ds}_s${s}.log" 2>&1 &
            sleep 20
        done
    fi
    echo "GPU $gpu: single-sample ablation on $ds -> logs/s1_qwen_${ds}*.log"
done
echo "running in the background. Check progress: ./scripts/status.sh"
