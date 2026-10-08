#!/usr/bin/env bash
# Breadth test + latency benchmark (Qwen, round-2 models). For each dataset on its own GPU: re-evaluate the six round-2
# E2E models (rule splits and budget head, seeds 42-44) reading 8 documents instead of 4 at the same totals (results go
# to results_k8/, results/ is untouched), then time every setting. Writes runs/breadth_summary.md. Resumable.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
source scripts/_gpus.sh
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
mkdir -p logs
for ds in $(echo "${DATASETS:-hotpotqa,2wiki}" | tr ',' ' '); do
    gpu=$(gpu_for "$ds"); warn_if_busy "$gpu"
    ( for cfg in r2_nested_M32_all_e6 r2_nested_M32_all_e6__learned; do
          for s in $(echo "${SEEDS:-42,43,44}" | tr ',' ' '); do
              d=runs/qwen/$ds/${cfg}_s$s
              [ -f "$d/results_k8/eval.json" ] && continue
              echo "[$ds] 8-document evaluation of ${cfg}_s$s ($(date))"
              CUDA_VISIBLE_DEVICES=$gpu "$PY" evaluate.py --run_dir "$d" --dataset "$ds" --k 8 --totals 32,64,128 \
                  --sections retrieval,qa --retrieval_ks 1,2,3,5,8 --amp bf16 --out_name results_k8
          done
      done
      [ -f "runs/latency_$ds.json" ] || CUDA_VISIBLE_DEVICES=$gpu "$PY" benchmark_latency.py --dataset "$ds"
      "$PY" summarize_breadth.py
    ) >> "logs/breadth_${ds}.log" 2>&1 &
    echo "GPU $gpu: breadth test + latency on $ds -> logs/breadth_${ds}.log"
done
echo "running in the background. When both are done: runs/breadth_summary.md"
