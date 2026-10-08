# Sourced by every script. Uses the server's existing Python and packages. Models and datasets are loaded from the
# Hugging Face cache and downloaded automatically the first time they are needed.
# OFFLINE=1 forbids downloads (useful if a long run should never touch the network); PY=... picks another Python.
PY=${PY:-python3}
if [ "${OFFLINE:-0}" = "1" ]; then
    export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
fi
export TOKENIZERS_PARALLELISM=false
