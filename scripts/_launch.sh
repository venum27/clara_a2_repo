#!/usr/bin/env bash
# Internal helper used by 02-04. Starts one background pipeline job per (backbone, dataset):
#   HotpotQA on the first GPU in GPUS, 2Wiki on the second (default GPUS=0,1); on each GPU the backbones run side
#   by side (SEQUENTIAL=1: one after another).
# Arguments are passed through to run_pipeline.py. Waits for all jobs if WAIT=1.
set -euo pipefail
cd "$(dirname "$0")/.."
source scripts/_env.sh
BACKBONES=${BACKBONES:-qwen,t5}; DATASETS=${DATASETS:-hotpotqa,2wiki}; TAG=${TAG:-run}
mkdir -p logs
source scripts/_gpus.sh
pids=()
for ds in ${DATASETS//,/ }; do
    gpu=$(gpu_for "$ds")
    warn_if_busy "$gpu"
    if [ "${SEQUENTIAL:-0}" = "1" ]; then
        log="logs/${TAG}_${ds}.log"
        CUDA_VISIBLE_DEVICES=$gpu nohup "$PY" run_pipeline.py --backbones "$BACKBONES" --datasets "$ds" \
            --amp bf16 --require_data "$@" >> "$log" 2>&1 &
        pids+=($!); echo "GPU $gpu: $BACKBONES on $ds (one after another) -> $log"
    else
        for bb in ${BACKBONES//,/ }; do
            log="logs/${TAG}_${bb}_${ds}.log"
            CUDA_VISIBLE_DEVICES=$gpu nohup "$PY" run_pipeline.py --backbones "$bb" --datasets "$ds" \
                --amp bf16 --require_data "$@" >> "$log" 2>&1 &
            pids+=($!); echo "GPU $gpu: $bb on $ds -> $log"
        done
    fi
done
if [ "${WAIT:-0}" = "1" ]; then
    status=0
    for p in "${pids[@]}"; do wait "$p" || status=1; done
    exit $status
fi
echo "running in the background. Check progress: ./scripts/status.sh"
