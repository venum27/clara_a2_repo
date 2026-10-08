# Baseline: the original CLaRa code

This folder runs the **authors' own implementation** ([apple/ml-clara](https://github.com/apple/ml-clara), pinned
commit `ee93341`) as a baseline. It is trained on exactly our data and evaluated on exactly our questions with
exactly our metrics, and its results appear in the same tables as our models (run name `clara_official_CR<rate>`).

## Steps (on Flair 2, from `~/clara_nested`)

```bash
./official_clara/setup_official.sh     # once: clones the code, builds official_clara/.venv, applies the patches
./scripts/06_official_clara.sh         # converts our data, trains + evaluates on both datasets (one GPU each)
```

Run it after `01_prepare_data.sh` (it needs our data). It can run alongside the main runs if GPU memory allows;
check with `./scripts/00_check_gpus.sh`. `CRS=16,32` also trains the 32x rate (8 vectors per document, 32 per
question). Resumable: re-running skips finished stages.

## What runs

The official three-stage pipeline with Qwen2.5-0.5B-Instruct:

| Stage | Official name | Data (converted from ours) | Settings |
|---|---|---|---|
| 1 | `stage1` compression pretraining | our SCP passages: all QA pairs of a passage as one target, plus its paraphrase | lr 1e-4, MSE loss, 3 epochs |
| 2 | `stage1_2` instruction tuning | our training questions with their gold passages plus BM25 distractors (4 per question) | lr 1e-4, 1 epoch |
| 3 | `stage2` end-to-end | our training questions with their 10 candidates | lr 5e-6, constant schedule, 3 epochs, top-4 |

Compression rate 16 with 256-token documents gives 16 memory vectors per document and 64 per question, the same
budget as our `B=64` comparisons.

## Changes to the official code

Environment only; the model, losses, prompts, data flow and straight-through top-k are untouched
(`patch_official.py`, each patch checked against the pinned commit):

1. attention implementation read from an environment variable instead of hard-coded FlashAttention; PyTorch's
   `sdpa` is used unless FlashAttention is installed (`FLASH=1 ./official_clara/setup_official.sh`);
2. `torch.optim.AdamW` instead of DeepSpeed's FusedAdam, which compiles a CUDA kernel that fails when the system CUDA
   compiler (13.1) differs from PyTorch's (12.8); same algorithm and arguments;
3. only without FlashAttention: a stand-in for two FlashAttention helper modules imported at load time but used only
   by multi-GPU ring attention.

Run settings that differ from the official scripts, because our data is thousands of examples rather than millions:
batch size 16 instead of 128/32, one GPU instead of four, and 3 epochs for stages 1 and 3 (matching our models)
instead of 1.

## Limits

The official code supports decoder-only models only, so there is no official FLAN-T5 baseline; for FLAN-T5 our
re-implementation (`fixed_M16`) is the CLaRa baseline. Evaluation uses the official `generate_from_questions`
(greedy decoding) and, for hit@5, the official model's own scoring of all candidates.
