#!/usr/bin/env bash
# Re-evaluate the trained Qwen models on a larger test set: N_BIG questions per dataset (default 3000; N_BIG=all for
# every remaining validation question), disjoint from all training and earlier evaluation questions. Evaluates the
# official CLaRa code, our method (round 2, budget head, seeds 42-44) and our CLaRa re-implementation (round 2
# fixed-16). Nothing is retrained; results go to results_big/ in each run. Writes runs/big_eval_summary.md. Resumable.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
source scripts/_gpus.sh
export PYTORCH_CUDA_ALLOC_CONF=${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}
mkdir -p logs
"$PY" make_big_eval.py --datasets "${DATASETS:-hotpotqa,2wiki}" --n "${N_BIG:-3000}"
OFF=official_clara
STUB=""; $OFF/.venv/bin/python -c "import flash_attn" 2>/dev/null || STUB=":$PWD/$OFF/flash_attn_stub"
for ds in $(echo "${DATASETS:-hotpotqa,2wiki}" | tr ',' ' '); do
    gpu=$(gpu_for "$ds"); warn_if_busy "$gpu"
    ( d=runs/qwen/$ds/clara_official_CR16_s42
      if [ ! -f "$d/results_big/eval.json" ]; then
          echo "[$ds] official CLaRa on the larger set ($(date))"
          CUDA_VISIBLE_DEVICES=$gpu PYTHONPATH="$PWD/$OFF/ml-clara$STUB" $OFF/.venv/bin/python $OFF/eval_official.py \
              --ckpt "$OFF/runs/${ds}_CR16/stage2" --dataset "$ds" --compress_rate 16 --k 4 --run_dir "$d" \
              --eval_name evalbig --out_name results_big
      fi
      for run in r2_fixed_M16_e6_s42 r2_nested_M32_all_e6__learned_s42 r2_nested_M32_all_e6__learned_s43 \
                 r2_nested_M32_all_e6__learned_s44; do
          d=runs/qwen/$ds/$run
          [ -f "$d/results_big/eval.json" ] && continue
          echo "[$ds] $run on the larger set ($(date))"
          CUDA_VISIBLE_DEVICES=$gpu "$PY" evaluate.py --run_dir "$d" --dataset "$ds" --eval_name evalbig \
              --out_name results_big --sections retrieval,qa --totals 32,64 --policies uniform,top_heavy --no_raw --amp bf16
      done
      "$PY" summarize_big.py
    ) >> "logs/big_eval_${ds}.log" 2>&1 &
    echo "GPU $gpu: larger evaluation on $ds -> logs/big_eval_${ds}.log"
done
echo "running in the background. When both are done: runs/big_eval_summary.md"
