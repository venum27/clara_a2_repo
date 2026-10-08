#!/usr/bin/env bash
# One time: fetch the official CLaRa code at a pinned commit and build its own Python environment
# (official_clara/.venv), with the versions from its requirements.txt. This does not touch the main project's Python.
#   FLASH=1 also tries to install FlashAttention (optional; PyTorch's sdpa attention is used otherwise).
set -euo pipefail
cd "$(dirname "$0")"
COMMIT=ee93341b922e2d8f1df84263f2b4edfc1a601841
[ -d ml-clara/.git ] || git clone https://github.com/apple/ml-clara.git ml-clara
git -C ml-clara fetch -q origin "$COMMIT" 2>/dev/null || true
git -C ml-clara checkout -q "$COMMIT"
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# PyTorch 2.8 as pinned by the official code, built for CUDA 12.8 (what Flair 2's driver supports)
pip install "torch==2.8.0" --index-url https://download.pytorch.org/whl/cu128
pip install "transformers==4.56.2" "peft==0.17.1" "deepspeed==0.18.1" "accelerate==1.10.1" "datasets==3.2.0" \
    "torchdata==0.11.0" "einops==0.8.1" "sentencepiece==0.2.0" "huggingface-hub==0.35.3" "numpy==1.26.4" \
    safetensors tqdm jinja2 requests scikit-learn
if [ "${FLASH:-0}" = "1" ]; then
    pip install "flash-attn==2.8.3" --no-build-isolation || echo "FlashAttention install failed; sdpa will be used"
fi
python patch_official.py ml-clara
STUB=""; python -c "import flash_attn" 2>/dev/null || STUB=":$PWD/flash_attn_stub"
PYTHONPATH="$PWD/ml-clara$STUB" python - << 'PY'
import torch, deepspeed, transformers, peft
from openrlhf.models.modeling_clara import CLaRa
print(f"official CLaRa imports OK | torch {torch.__version__} (CUDA {torch.version.cuda}) | GPUs {torch.cuda.device_count()}"
      f" | transformers {transformers.__version__} | peft {peft.__version__} | deepspeed {deepspeed.__version__}")
assert torch.cuda.is_available(), "PyTorch cannot see the GPUs"
PY
echo "official environment ready. next: ./scripts/06_official_clara.sh"
