# Not All Documents Deserve Equal Space: Adaptive Memory Budgets for CLaRa

CS 613 (NLP), IIT Gandhinagar, Assignment 2. Team Black Box Vectors.

We extend CLaRa (compressed-memory retrieval-augmented generation) with **nested memory tokens**, so that one
compressor and one stored index serve every compression rate, and a **learned budget head**, which splits a fixed
total of memory vectors across the retrieved documents and is trained end to end from the answer loss. We compare
against the authors' own CLaRa code run on our data, against our re-implementation of CLaRa, and against our
Assignment 1.

## Repository layout

| Path | Contents |
|---|---|
| `nclara/` | model (both backbones, nested memory, straight-through top-k), budget head, hand-designed splits, metrics, dataset loading |
| `prepare_data.py`, `synth_scp_data.py` | question sampling; synthetic SCP data with Qwen2.5-14B-Instruct and answer verification |
| `train_scp.py`, `train_e2e.py`, `run_pipeline.py` | compressor pretraining (SCP), end-to-end training, the run orchestrator |
| `evaluate.py`, `diagnose_memory.py`, `make_big_eval.py`, `benchmark_latency.py` | evaluation, memory diagnostic, 3,000-question evaluation set, latency benchmark |
| `summarize*.py` | the summary tables in `results/` |
| `official_clara/` | running the official CLaRa code (apple/ml-clara) on our data and scoring it with our metrics |
| `sanity_checks.py`, `check_setup.py`, `show_step.py` | pre-flight checks, setup check, step-by-step evidence viewer |
| `scripts/` | the server workflow, in order (below) |
| `results/` | all results: summary tables and every run's evaluation files |
| `logs/` | the run logs (progress bars reduced to their final state) |
| `data/` | the sampled questions and our synthetic SCP data |

Model checkpoints are not included (size); everything in the report can be checked from `results/` and `logs/`.

## Where each table of the report comes from

| Report | File |
|---|---|
| Compressor QA by prefix length, retrieval, end-to-end QA by budget, seeds | `results/results_summary.md` |
| Memory diagnostic | `results/diagnose_summary.md` |
| Breadth vs. depth, latency and memory | `results/breadth_summary.md`, `results/latency_*.md` |
| Larger evaluation (3,000 questions), ours vs. the official CLaRa code | `results/big_eval_summary.md` |
| Any single run | `results/runs/<backbone>/<dataset>/<run>/results*/summary.md` |

Run names: `nested_M32` / `fixed_M16` are the first configuration (one prefix per step, 3 SCP epochs);
`r2_nested_M32_all_e6` / `r2_fixed_M16_e6` the final one (every prefix per step, 6 epochs); `__learned` adds the
budget head; `_s42/_s43/_s44` is the seed; `clara_official_CR16` is the official code.

## Reproducing (Flair 2: 2x L40S)

```bash
./scripts/00_setup_check.sh        # packages, GPUs, models, datasets
./scripts/01_prepare_data.sh       # questions + synthetic SCP data (Qwen2.5-14B-Instruct)
./scripts/03_train_main.sh         # first configuration, both backbones
./official_clara/setup_official.sh && ./scripts/06_official_clara.sh   # official CLaRa baseline
./scripts/07_round2.sh             # final configuration (Qwen)
./scripts/08_round2_seeds.sh       # E2E seeds 43 and 44
./scripts/09_breadth_latency.sh    # breadth test and latency benchmark
./scripts/10_big_eval.sh           # 3,000-question evaluation
./scripts/12_ablation_s1.sh        # ablation: budget head with one sampled split./scripts/status.sh                # progress at any time
```

Every script runs in the background, writes to `logs/`, and resumes where it stopped. `python3 sanity_checks.py
--backbone qwen` verifies gradients, prefix independence, straight-through retrieval and the budget head in about a
minute. `python3 show_step.py <n>` prints the evidence for each step of the pipeline.
