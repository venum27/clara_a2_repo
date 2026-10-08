# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 60.8 | 79.7 | 88.0 | 94.8 | 0.0 | 11.1 | 19.9 | 36.8 |
| query reasoner (after E2E) | 71.6 | 87.2 | 93.2 | 98.1 | 0.0 | 28.6 | 43.6 | 67.1 |
| query reasoner (before E2E) | 25.7 | 45.3 | 60.5 | 80.2 | 0.0 | 2.2 | 6.0 | 17.0 |
| random (expected) | 24.5 | 44.2 | 60.1 | 82.2 | 0.0 | 1.7 | 5.2 | 17.8 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 30.7 [29.1, 32.4] | 35.0 [33.4, 36.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 30.6 [28.9, 32.3] | 35.0 [33.3, 36.6] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 30.7 [29.1, 32.4] | 35.0 [33.4, 36.7] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 30.7 [29.0, 32.4] | 35.4 [33.7, 37.0] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 30.8 [29.2, 32.5] | 35.5 [33.8, 37.1] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 30.7 [29.0, 32.4] | 35.4 [33.7, 37.0] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (2147) | rank 2 (468) | rank 3+ (286) | not retrieved (99) |
|---|---|---|---|---|
| uniform@32 | 35.2 | 36.0 | 33.2 | 32.0 |
| top_heavy@32 | 35.5 | 35.2 | 32.2 | 30.3 |
| learned@32 | 35.2 | 36.0 | 33.2 | 32.0 |
| uniform@64 | 35.6 | 36.1 | 33.8 | 31.0 |
| top_heavy@64 | 35.7 | 36.4 | 34.5 | 28.6 |
| learned@64 | 35.6 | 36.1 | 33.8 | 31.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.1 [-0.5, +0.2] | 0.784 | -0.0 [-0.5, +0.4] | 0.547 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | +0.1 [-0.2, +0.5] | 0.264 | +0.0 [-0.4, +0.5] | 0.453 |
| top_heavy@64 vs uniform@64 | +0.1 [-0.3, +0.5] | 0.287 | +0.1 [-0.3, +0.6] | 0.328 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | -0.1 [-0.5, +0.3] | 0.764 | -0.1 [-0.6, +0.3] | 0.672 |
