#!/usr/bin/env bash
# Sample the questions, then synthesise SCP training data (HotpotQA on the first GPU in GPUS, 2Wiki on the
# second; with one GPU, one dataset after the other).
# Both backbones train on this same data. Existing data is kept unless FORCE=1.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
N_TRAIN=${N_TRAIN:-2000}; N_EVAL=${N_EVAL:-500}; MAX_DOCS=${MAX_DOCS:-4000}
SYNTH=${SYNTH:-Qwen/Qwen2.5-14B-Instruct}   # data generator only (already in the cache); ~30 GB of GPU memory
SYNTH_BATCH=${SYNTH_BATCH:-8}
source scripts/_gpus.sh
mkdir -p logs data
if [ "${FORCE:-0}" = "1" ] || [ ! -f data/hotpotqa_eval.json ] || [ ! -f data/2wiki_eval.json ]; then
    "$PY" prepare_data.py --datasets hotpotqa,2wiki --n_train "$N_TRAIN" --n_eval "$N_EVAL"
fi
for ds in hotpotqa 2wiki; do
    if [ "${FORCE:-0}" = "1" ] || [ ! -f "data/${ds}_scp.json" ]; then
        gpu=$(gpu_for "$ds"); warn_if_busy "$gpu"
        echo "synthesising $ds on GPU $gpu"
        CUDA_VISIBLE_DEVICES=$gpu nohup "$PY" synth_scp_data.py --datasets "$ds" --synth_model "$SYNTH" \
            --max_docs "$MAX_DOCS" --batch_size "$SYNTH_BATCH" > "logs/synth_${ds}.log" 2>&1 &
        if [ "${#GPU_LIST[@]}" -eq 1 ]; then wait; fi     # one GPU: don't load two copies of the synthesiser at once
    fi
done
echo "synthesis running on both GPUs (follow with: tail -f logs/synth_*.log); waiting..."
wait
for d in hotpotqa 2wiki; do test -f "data/${d}_scp.json" || { echo "synthesis for $d failed; see logs/synth_$d.log"; exit 1; }; done
echo "N_TRAIN=$N_TRAIN N_EVAL=$N_EVAL MAX_DOCS=$MAX_DOCS SYNTH=$SYNTH" | tee data/SETTINGS.txt
grep -h "passages |" logs/synth_hotpotqa.log logs/synth_2wiki.log || true
echo "next: ./scripts/02_pilot.sh"
