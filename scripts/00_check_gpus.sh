#!/usr/bin/env bash
# Flair 2 is shared: show each GPU's free memory, utilisation and who is using it, and suggest a GPUS setting.
# Run before steps 1-4 (and whenever jobs seem slow).
set -uo pipefail
echo "== GPUs"
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits |
while IFS=', ' read -r idx used total util; do
    printf "GPU %s: %5s / %s MiB used, %3s%% busy\n" "$idx" "$used" "$total" "$util"
done
echo "== compute processes (user, pid, GPU memory)"
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader,nounits 2>/dev/null |
while IFS=', ' read -r uuid pid mem; do
    idx=$(nvidia-smi --query-gpu=index,uuid --format=csv,noheader | grep "$uuid" | cut -d, -f1)
    printf "GPU %s  %-16s pid %-9s %6s MiB\n" "$idx" "$(ps -o user= -p "$pid" 2>/dev/null || echo '?')" "$pid" "$mem"
done
free_gpus=$(nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits |
            awk -F', ' '$2 < 2000 && $3 < 20 {printf "%s%s", sep, $1; sep=","}')
echo
echo "Idle GPUs right now: ${free_gpus:-none}"
cat << MSG
Default is GPUS=0,1 (HotpotQA on the first, 2Wiki on the second). Our jobs need only a few GB each, so a GPU with
other users' idle processes still works, but if someone starts training there your jobs slow down. Options:
  GPUS=0,1   both GPUs (default)
  GPUS=1     only GPU 1: both datasets share it (slower, but never competes with other users on GPU 0)
Example: GPUS=1 ./scripts/03_train_main.sh
MSG
