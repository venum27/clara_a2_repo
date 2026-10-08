# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 68.9 | 83.9 | 89.3 | 95.0 | 99.7 | 0.0 | 20.7 | 34.4 | 51.5 | 71.6 |
| query reasoner (after E2E) | 59.5 | 73.9 | 83.3 | 95.3 | 100.0 | 0.0 | 19.1 | 34.1 | 58.5 | 86.3 |
| query reasoner (before E2E) | 39.1 | 55.2 | 66.6 | 85.3 | 98.0 | 0.0 | 10.0 | 18.4 | 34.4 | 65.6 |
| random (expected) | 20.0 | 37.8 | 53.4 | 77.8 | 97.8 | 0.0 | 2.2 | 6.7 | 22.2 | 62.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.1] | 20.0 [16.1, 24.0] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.1] | 20.0 [16.1, 24.0] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.1] | 20.0 [16.1, 24.0] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 13.0 [9.4, 17.1] | 20.5 [16.4, 24.4] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 12.0 [8.4, 15.7] | 19.9 [16.0, 23.8] |
| score@64 | [18.6, 14.0, 7.3, 7.3, 4.4, 4.4, 4.0, 4.0] | 64.0 vectors | 12.4 [8.7, 16.1] | 20.0 [16.1, 23.8] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 12.4 [8.7, 16.4] | 19.8 [15.8, 23.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 12.7 [9.0, 16.7] | 19.7 [15.9, 23.9] |
| score@128 | [32.0, 30.6, 16.4, 15.8, 8.8, 8.7, 7.8, 7.8] | 128.0 vectors | 13.7 [10.0, 17.7] | 20.7 [16.8, 24.9] |
| raw_bm25 | - | 1072 tokens | 7.4 [4.7, 10.7] | 20.9 [17.6, 24.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (178) | rank 2 (43) | rank 3+ (78) |
|---|---|---|---|
| uniform@32 | 21.1 | 20.2 | 17.6 |
| top_heavy@32 | 21.1 | 20.2 | 17.6 |
| score@32 | 21.1 | 20.2 | 17.6 |
| uniform@64 | 21.9 | 17.8 | 18.8 |
| top_heavy@64 | 21.8 | 18.4 | 16.6 |
| score@64 | 22.2 | 17.9 | 16.2 |
| uniform@128 | 20.6 | 17.2 | 19.2 |
| top_heavy@128 | 19.6 | 15.3 | 22.4 |
| score@128 | 21.4 | 16.0 | 21.4 |
| raw_bm25 | 20.1 | 19.3 | 23.5 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | -1.0 [-2.7, +0.7] | 0.920 | -0.6 [-2.4, +1.2] | 0.730 |
| score@64 vs uniform@64 | -0.7 [-2.3, +0.7] | 0.846 | -0.5 [-2.2, +1.1] | 0.700 |
| top_heavy@128 vs uniform@128 | +0.3 [-1.0, +2.0] | 0.409 | -0.0 [-1.7, +1.6] | 0.517 |
| score@128 vs uniform@128 | +1.3 [+0.3, +2.7] | 0.018 | +0.9 [-0.3, +2.3] | 0.093 |
