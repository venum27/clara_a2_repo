#!/usr/bin/env bash
# Train the OFFICIAL CLaRa pipeline (stage1 -> stage1_2 -> stage2) on one dataset at one compression rate, on the GPU in
# CUDA_VISIBLE_DEVICES, then evaluate it on our evaluation questions with our metrics.
#   usage: official_clara/run_official.sh <dataset> <compress_rate>
# Finished stages are skipped, so the script can be re-run after an interruption.
set -euo pipefail
cd "$(dirname "$0")/.."
DS=$1; CR=${2:-16}
OFF=official_clara
MODEL=${MODEL:-Qwen/Qwen2.5-0.5B-Instruct}
K=${K:-4}                         # documents per question, as in our runs
TBS=${TBS:-16}; MBS=${MBS:-2}     # small-data batch size (official scripts: 128 / 32 for millions of examples)
PORT=${PORT:-$((29500 + RANDOM % 1000))}
source $OFF/.venv/bin/activate
STUB=""; python -c "import flash_attn" 2>/dev/null || STUB=":$PWD/$OFF/flash_attn_stub"
export PYTHONPATH="$PWD/$OFF/ml-clara$STUB"
export CLARA_TORCH_ADAMW=1
if [ -z "$STUB" ]; then export CLARA_ATTN=flash_attention_2; FA="--flash_attn"; else export CLARA_ATTN=sdpa; FA=""; fi
DATA=$OFF/data/$DS; OUT=$OFF/runs/${DS}_CR${CR}
mkdir -p "$OUT" logs
COMMON="--pretrain $MODEL --train_batch_size $TBS --micro_train_batch_size $MBS --logging_steps 10 --save_steps -1 \
        --zero_stage 2 --bf16 --doc_max_length 256 --compress_rate $CR --gradient_checkpointing $FA"
stage () {   # name, extra args...
    local name=$1; shift
    if [ -f "$OUT/$name/config.json" ]; then echo "[$DS CR$CR] $name already trained"; return; fi
    echo "[$DS CR$CR] training $name ($(date))"
    torchrun --nproc_per_node 1 --master_port "$PORT" -m openrlhf.cli.train_sft $COMMON \
        --save_path "$OUT/$name" --ckpt_path "$OUT/ckpt_$name" "$@"
}
# Stage 1: salient compressor pretraining (QA + paraphrase targets, MSE alignment); 3 epochs like our SCP
stage stage1   --stage stage1 --dataset $DATA/stage1_pretrain.jsonl --max_len 2048 --max_epochs ${EPOCHS1:-3} \
               --learning_rate 1e-4 --generation_top_k 1 --qa_loss --mse_loss
# Stage 1_2: compression instruction tuning (question + K passages -> answer); 1 epoch as in the official script
stage stage1_2 --stage stage1_2 --pretrain_checkpoint $OUT/stage1 --dataset $DATA/stage1_2_instruction.jsonl \
               --max_len 2048 --max_epochs ${EPOCHS12:-1} --learning_rate 1e-4 --generation_top_k $K --mse_loss
# Stage 2: end-to-end retrieval + generation over the 10 candidates; official lr and scheduler; 3 epochs like ours
stage stage2   --stage stage2 --pretrain_checkpoint $OUT/stage1_2 --dataset $DATA/stage2_end_to_end.jsonl \
               --max_len 1024 --max_epochs ${EPOCHS2:-3} --learning_rate 5e-6 --lr_scheduler constant \
               --generation_top_k $K --qa_loss
RUN=runs/qwen/$DS/clara_official_CR${CR}_s42
if [ -f "$RUN/results/eval.json" ]; then echo "[$DS CR$CR] already evaluated"; exit 0; fi
python $OFF/eval_official.py --ckpt "$OUT/stage2" --dataset "$DS" --compress_rate "$CR" --k "$K" --run_dir "$RUN"
