#!/usr/bin/env bash
# Sanity checks on both real models, then a short pilot of both backbones on HotpotQA (Qwen and FLAN-T5 side by
# side on HotpotQA's GPU, as in the full runs) to measure timing before committing GPU days.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
source scripts/_gpus.sh
CUDA_VISIBLE_DEVICES=$(gpu_for hotpotqa) "$PY" sanity_checks.py --backbone qwen
CUDA_VISIBLE_DEVICES=$(gpu_for 2wiki) "$PY" sanity_checks.py --backbone t5
TAG=pilot DATASETS=hotpotqa WAIT=1 ./scripts/_launch.sh --preset main --seeds 42 --n_eval_used 100 --runs_dir runs_pilot
"$PY" summarize.py --runs_dir runs_pilot
cat runs_pilot/results_summary.md
echo; echo "== minutes per stage (pilot scale: 100 eval questions)"
for f in runs_pilot/*/hotpotqa/*/{scp,e2e}/train_log.json; do
    echo "$f: $(grep -o '"minutes": [0-9.]*' "$f" | cut -d' ' -f2)"
done
