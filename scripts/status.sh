#!/usr/bin/env bash
# What is running, what has finished, GPU use.
cd "$(dirname "$0")/.."
echo "== running jobs"; pgrep -af "run_pipeline.py|synth_scp_data.py|train_sft|eval_official|evaluate.py|benchmark_latency|diagnose_memory" | grep -v pgrep || echo "(none)"
echo "== finished evaluations: $(ls -d runs/*/*/*/results 2>/dev/null | wc -l)"
ls -d runs/*/*/*/results 2>/dev/null | sed 's#/results##; s#^runs/#  #'
echo "== last log lines"
for f in logs/*.log; do [ -f "$f" ] && { echo "-- $f"; tail -c 400 "$f" | tr '\r' '\n' | grep -v '^\s*$' | tail -n 2; }; done
command -v nvidia-smi > /dev/null && nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total --format=csv
