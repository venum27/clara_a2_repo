# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 70.2 | 83.5 | 90.0 | 95.6 | 0.0 | 21.7 | 34.5 | 52.0 |
| query reasoner (after E2E) | 57.1 | 76.1 | 85.0 | 94.8 | 0.0 | 19.2 | 34.2 | 56.9 |
| query reasoner (before E2E) | 43.7 | 62.2 | 73.6 | 88.1 | 0.0 | 8.5 | 16.4 | 37.0 |
| random (expected) | 20.1 | 37.9 | 53.5 | 77.9 | 0.0 | 2.3 | 6.8 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 12.0 [10.9, 13.2] | 19.8 [18.6, 21.0] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 12.0 [10.8, 13.1] | 19.8 [18.6, 21.1] |
| learned@32 | [7.4, 6.8, 11.7, 6.1] | 32.0 vectors | 12.2 [11.1, 13.4] | 19.9 [18.6, 21.1] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.9 [10.8, 13.2] | 19.7 [18.5, 21.0] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 12.0 [10.8, 13.2] | 19.8 [18.6, 21.0] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.9 [10.8, 13.2] | 19.7 [18.5, 21.0] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [7.4, 6.8, 11.7, 6.1] | 7.9 | 8.1 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (1713) | rank 2 (571) | rank 3+ (446) | not retrieved (270) |
|---|---|---|---|---|
| uniform@32 | 21.0 | 19.3 | 18.5 | 15.5 |
| top_heavy@32 | 21.3 | 18.5 | 18.5 | 14.7 |
| learned@32 | 21.2 | 19.1 | 18.5 | 15.7 |
| uniform@64 | 21.5 | 18.0 | 18.1 | 15.3 |
| top_heavy@64 | 21.6 | 17.7 | 18.5 | 15.2 |
| learned@64 | 21.5 | 18.0 | 18.1 | 15.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.1 [-0.5, +0.3] | 0.664 | -0.0 [-0.4, +0.4] | 0.527 |
| learned@32 vs uniform@32 | +0.2 [-0.2, +0.5] | 0.202 | +0.1 [-0.3, +0.5] | 0.294 |
| learned@32 vs top_heavy@32 | +0.2 [-0.2, +0.6] | 0.136 | +0.1 [-0.3, +0.6] | 0.293 |
| top_heavy@64 vs uniform@64 | +0.0 [-0.3, +0.4] | 0.456 | +0.1 [-0.3, +0.5] | 0.379 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | -0.0 [-0.4, +0.3] | 0.620 | -0.1 [-0.5, +0.3] | 0.621 |
