# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s43`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 70.2 | 83.5 | 90.0 | 95.6 | 0.0 | 21.7 | 34.5 | 52.0 |
| query reasoner (after E2E) | 52.6 | 72.3 | 82.7 | 93.3 | 0.0 | 16.1 | 29.7 | 52.7 |
| query reasoner (before E2E) | 43.7 | 62.2 | 73.6 | 88.1 | 0.0 | 8.5 | 16.4 | 37.0 |
| random (expected) | 20.1 | 37.9 | 53.5 | 77.9 | 0.0 | 2.3 | 6.8 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 11.8 [10.7, 13.0] | 19.0 [17.7, 20.2] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.5 [10.4, 12.7] | 18.9 [17.7, 20.2] |
| learned@32 | [12.5, 5.7, 4.7, 9.1] | 32.0 vectors | 11.7 [10.5, 12.8] | 19.0 [17.8, 20.2] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.8 [10.7, 12.9] | 19.2 [17.9, 20.4] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 12.0 [10.8, 13.2] | 19.2 [18.0, 20.5] |
| learned@64 | [23.8, 13.5, 8.0, 18.7] | 64.0 vectors | 12.0 [10.8, 13.1] | 19.3 [18.0, 20.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [12.5, 5.7, 4.7, 9.1] | 8.9 | 7.5 |
| 64 | [23.8, 13.5, 8.0, 18.7] | 18.2 | 14.9 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (1577) | rank 2 (593) | rank 3+ (506) | not retrieved (324) |
|---|---|---|---|---|
| uniform@32 | 20.6 | 17.6 | 17.1 | 17.0 |
| top_heavy@32 | 20.8 | 17.1 | 16.9 | 16.1 |
| learned@32 | 21.0 | 17.2 | 16.9 | 16.1 |
| uniform@64 | 21.4 | 17.3 | 16.8 | 15.3 |
| top_heavy@64 | 21.5 | 17.3 | 16.8 | 15.7 |
| learned@64 | 21.5 | 17.7 | 16.4 | 16.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-0.7, +0.1] | 0.931 | -0.1 [-0.5, +0.3] | 0.625 |
| learned@32 vs uniform@32 | -0.1 [-0.5, +0.2] | 0.825 | +0.1 [-0.3, +0.4] | 0.403 |
| learned@32 vs top_heavy@32 | +0.1 [-0.2, +0.5] | 0.251 | +0.1 [-0.2, +0.5] | 0.257 |
| top_heavy@64 vs uniform@64 | +0.2 [-0.1, +0.5] | 0.134 | +0.1 [-0.3, +0.5] | 0.338 |
| learned@64 vs uniform@64 | +0.2 [-0.1, +0.5] | 0.161 | +0.2 [-0.2, +0.5] | 0.227 |
| learned@64 vs top_heavy@64 | -0.0 [-0.4, +0.3] | 0.604 | +0.1 [-0.3, +0.5] | 0.382 |
