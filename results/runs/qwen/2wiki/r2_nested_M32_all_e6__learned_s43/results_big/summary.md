# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s43`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 60.8 | 79.7 | 88.0 | 94.8 | 0.0 | 11.1 | 19.9 | 36.8 |
| query reasoner (after E2E) | 74.0 | 88.1 | 94.3 | 98.3 | 0.0 | 29.7 | 43.5 | 66.3 |
| query reasoner (before E2E) | 25.7 | 45.3 | 60.5 | 80.2 | 0.0 | 2.2 | 6.0 | 17.0 |
| random (expected) | 24.5 | 44.2 | 60.1 | 82.2 | 0.0 | 1.7 | 5.2 | 17.8 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 30.6 [29.0, 32.3] | 35.1 [33.5, 36.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 30.6 [29.0, 32.4] | 35.2 [33.7, 36.9] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 30.6 [29.0, 32.3] | 35.1 [33.5, 36.7] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 30.9 [29.3, 32.7] | 36.0 [34.3, 37.7] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 31.0 [29.4, 32.7] | 36.1 [34.4, 37.7] |
| learned@64 | [21.7, 20.6, 11.1, 10.6] | 64.0 vectors | 31.0 [29.4, 32.7] | 36.1 [34.4, 37.8] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [21.7, 20.6, 11.1, 10.6] | 18.8 | 13.6 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (2221) | rank 2 (423) | rank 3+ (253) | not retrieved (103) |
|---|---|---|---|---|
| uniform@32 | 35.5 | 34.9 | 33.2 | 30.8 |
| top_heavy@32 | 35.8 | 34.6 | 32.5 | 31.7 |
| learned@32 | 35.5 | 34.9 | 33.2 | 30.8 |
| uniform@64 | 36.6 | 34.4 | 35.2 | 31.2 |
| top_heavy@64 | 36.7 | 34.8 | 34.1 | 32.8 |
| learned@64 | 36.8 | 34.6 | 34.8 | 31.8 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.0 [-0.4, +0.4] | 0.484 | +0.2 [-0.3, +0.6] | 0.214 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -0.0 [-0.4, +0.4] | 0.579 | -0.2 [-0.6, +0.3] | 0.786 |
| top_heavy@64 vs uniform@64 | +0.0 [-0.3, +0.4] | 0.477 | +0.1 [-0.3, +0.5] | 0.343 |
| learned@64 vs uniform@64 | +0.0 [-0.3, +0.3] | 0.442 | +0.2 [-0.2, +0.5] | 0.179 |
| learned@64 vs top_heavy@64 | +0.0 [-0.3, +0.3] | 0.522 | +0.1 [-0.2, +0.4] | 0.284 |
