"""Apply the minimal, environment-only patches the official CLaRa code needs on Flair 2 (one GPU, driver CUDA 12.8).
None of them changes the method (model, losses, data flow, straight-through top-k, hyperparameters):

  1. attention implementation: the code hard-codes flash_attention_2; read it from $CLARA_ATTN instead
     (set by run_official.sh to flash_attention_2 if FlashAttention is installed, else PyTorch's sdpa).
  2. optimiser: DeepSpeed's FusedAdam compiles a CUDA kernel on first use, which fails when the system CUDA
     compiler (13.1) differs from PyTorch's CUDA (12.8). With $CLARA_TORCH_ADAMW=1, torch.optim.AdamW is used
     instead: the same algorithm and the same arguments (lr, betas, weight_decay).
  3. only if FlashAttention is not installed: a stand-in `flash_attn` package providing the names imported at
     module load by ring_attn_utils.py. They are used only for multi-GPU sequence parallelism (ring attention), which
     a single-GPU run never enables; calling them raises an error rather than silently doing something else.

Every patch is checked against the pinned commit and is idempotent.

    python official_clara/patch_official.py official_clara/ml-clara
"""
import os
import sys

PINNED_COMMIT = "ee93341b922e2d8f1df84263f2b4edfc1a601841"

PATCHES = [
    ("openrlhf/cli/train_sft.py",
     "        attn_implementation='flash_attention_2',",
     "        attn_implementation=os.environ.get('CLARA_ATTN', 'flash_attention_2'),  # patched: see official_clara/"),
    ("openrlhf/models/modeling_clara.py",
     "        attn_implementation='flash_attention_2'",
     "        attn_implementation=__import__('os').environ.get('CLARA_ATTN', 'flash_attention_2')  # patched"),
    ("openrlhf/utils/deepspeed/deepspeed.py",
     "        AdamOptimizer = DeepSpeedCPUAdam if self.adam_offload else FusedAdam",
     "        AdamOptimizer = DeepSpeedCPUAdam if self.adam_offload else (\n"
     "            torch.optim.AdamW if os.environ.get('CLARA_TORCH_ADAMW') == '1' else FusedAdam)  # patched"),
]

STUB = {
    "flash_attn/__init__.py": '"""Stand-in (see official_clara/patch_official.py): real FlashAttention is not installed."""\n',
    "flash_attn/bert_padding.py": '''from einops import rearrange  # noqa: F401  (re-exported like the real module)


def _unavailable(*args, **kwargs):
    raise RuntimeError("flash_attn is not installed; this code path (ring attention / padding-free training) "
                       "needs the real package")


index_first_axis = pad_input = unpad_input = _unavailable
''',
    "flash_attn/utils/__init__.py": "",
    "flash_attn/utils/distributed.py": '''def all_gather(*args, **kwargs):
    raise RuntimeError("flash_attn is not installed; all_gather is only used by ring attention")
''',
}


def main(repo, stub_dir):
    head = os.path.join(repo, ".git", "HEAD")
    if os.path.exists(head):
        ref = open(head).read().strip()
        sha = open(os.path.join(repo, ".git", ref[5:])).read().strip() if ref.startswith("ref:") else ref
        if sha != PINNED_COMMIT:
            print(f"WARNING: official repo is at {sha[:12]}, patches were written for {PINNED_COMMIT[:12]}")
    for rel, old, new in PATCHES:
        path = os.path.join(repo, rel)
        src = open(path).read()
        if new in src:
            print(f"already patched: {rel}")
            continue
        if src.count(old) != 1:
            sys.exit(f"cannot patch {rel}: expected exactly one occurrence of\n  {old.strip()}")
        open(path, "w").write(src.replace(old, new))
        print(f"patched: {rel}")
    try:
        import flash_attn  # noqa: F401
        print("FlashAttention is installed: no stand-in needed")
    except ImportError:
        for rel, text in STUB.items():
            p = os.path.join(stub_dir, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(text)
        print(f"FlashAttention not installed: wrote stand-in package to {stub_dir} (added to PYTHONPATH by the run "
              f"script); attention will use PyTorch sdpa")


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "official_clara/ml-clara"
    main(repo, os.path.join(os.path.dirname(os.path.abspath(repo)), "flash_attn_stub"))
