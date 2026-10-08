# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 60.8 | 79.7 | 88.0 | 94.8 | 0.0 | 11.1 | 19.9 | 36.8 |
| query reasoner (after E2E) | 71.6 | 87.1 | 93.4 | 98.5 | 0.0 | 29.3 | 43.7 | 67.7 |
| query reasoner (before E2E) | 25.7 | 45.3 | 60.5 | 80.2 | 0.0 | 2.2 | 6.0 | 17.0 |
| random (expected) | 24.5 | 44.2 | 60.1 | 82.2 | 0.0 | 1.7 | 5.2 | 17.8 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 31.5 [29.9, 33.1] | 36.5 [34.8, 38.1] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 31.6 [29.9, 33.2] | 36.7 [35.0, 38.3] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 31.5 [29.9, 33.1] | 36.5 [34.8, 38.1] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 31.7 [30.1, 33.3] | 36.9 [35.3, 38.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 31.9 [30.3, 33.5] | 37.1 [35.5, 38.7] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 31.7 [30.1, 33.3] | 37.0 [35.4, 38.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (2148) | rank 2 (464) | rank 3+ (289) | not retrieved (99) |
|---|---|---|---|---|
| uniform@32 | 35.3 | 40.2 | 40.0 | 35.3 |
| top_heavy@32 | 35.6 | 40.2 | 39.4 | 36.2 |
| learned@32 | 35.3 | 40.2 | 40.0 | 35.3 |
| uniform@64 | 36.2 | 38.7 | 39.7 | 37.0 |
| top_heavy@64 | 36.5 | 38.2 | 40.1 | 36.4 |
| learned@64 | 36.3 | 38.7 | 39.7 | 37.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.1 [-0.3, +0.5] | 0.402 | +0.2 [-0.3, +0.6] | 0.225 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -0.1 [-0.5, +0.3] | 0.658 | -0.2 [-0.6, +0.3] | 0.775 |
| top_heavy@64 vs uniform@64 | +0.3 [-0.1, +0.6] | 0.090 | +0.2 [-0.2, +0.6] | 0.160 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.1] | 0.383 | +0.1 [+0.0, +0.1] | 0.130 |
| learned@64 vs top_heavy@64 | -0.2 [-0.6, +0.1] | 0.906 | -0.2 [-0.5, +0.2] | 0.763 |
