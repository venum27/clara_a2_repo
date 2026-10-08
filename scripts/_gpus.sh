# Sourced by the other scripts. GPUS lists the GPUs to use (default "0,1"); HotpotQA goes on the first,
# 2Wiki on the second (with one GPU listed, both datasets share it).
IFS=',' read -r -a GPU_LIST <<< "${GPUS:-0,1}"
gpu_for() {
    local i
    case "$1" in hotpotqa) i=0 ;; 2wiki) i=1 ;; *) echo "unknown dataset $1" >&2; return 1 ;; esac
    echo "${GPU_LIST[$(( i % ${#GPU_LIST[@]} ))]}"
}
warn_if_busy() {   # warn (never block) if another user's work is on this GPU
    command -v nvidia-smi > /dev/null || return 0
    local line used util
    line=$(nvidia-smi -i "$1" --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits 2>/dev/null) || return 0
    used=${line%%,*}; util=${line##*, }
    if [ "${used// /}" -gt 2000 ] || [ "${util// /}" -gt 20 ]; then
        echo "  note: GPU $1 already has ${used// /} MiB in use and is ${util// /}% busy (other users?)." \
             "Jobs still run; see ./scripts/00_check_gpus.sh"
    fi
}
