# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 68.9 | 83.9 | 89.3 | 95.0 | 99.7 | 0.0 | 20.7 | 34.4 | 51.5 | 71.6 |
| query reasoner (after E2E) | 57.5 | 75.9 | 84.6 | 95.3 | 99.7 | 0.0 | 20.4 | 36.5 | 63.5 | 86.6 |
| query reasoner (before E2E) | 39.1 | 55.2 | 66.6 | 85.3 | 98.0 | 0.0 | 10.0 | 18.4 | 34.4 | 65.6 |
| random (expected) | 20.0 | 37.8 | 53.4 | 77.8 | 97.8 | 0.0 | 2.2 | 6.7 | 22.2 | 62.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.1] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.1] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.1] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 11.4 [8.0, 15.1] | 18.4 [14.5, 22.0] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 11.4 [8.0, 15.1] | 20.2 [16.4, 24.0] |
| score@64 | [18.8, 13.7, 7.3, 7.3, 4.4, 4.4, 4.0, 4.0] | 64.0 vectors | 11.0 [7.7, 14.7] | 19.3 [15.4, 23.0] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 10.7 [7.4, 14.0] | 18.3 [14.6, 21.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 10.7 [7.4, 14.0] | 19.4 [15.6, 23.2] |
| score@128 | [32.0, 30.4, 16.6, 15.8, 9.1, 8.8, 7.7, 7.7] | 128.0 vectors | 10.0 [6.7, 13.4] | 18.5 [14.9, 22.1] |
| raw_bm25 | - | 1072 tokens | 7.4 [4.7, 10.7] | 20.9 [17.6, 24.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (172) | rank 2 (55) | rank 3+ (71) | not retrieved (1) |
|---|---|---|---|---|
| uniform@32 | 22.0 | 17.7 | 10.3 | 0.0 |
| top_heavy@32 | 22.0 | 17.7 | 10.3 | 0.0 |
| score@32 | 22.0 | 17.7 | 10.3 | 0.0 |
| uniform@64 | 20.8 | 19.1 | 12.1 | 0.0 |
| top_heavy@64 | 23.3 | 19.1 | 13.6 | 0.0 |
| score@64 | 22.3 | 19.1 | 12.6 | 0.0 |
| uniform@128 | 20.0 | 16.0 | 16.2 | 0.0 |
| top_heavy@128 | 22.5 | 14.0 | 16.2 | 0.0 |
| score@128 | 20.8 | 15.2 | 16.0 | 0.0 |
| raw_bm25 | 18.9 | 27.6 | 20.8 | 0.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +0.0 [-1.7, +1.7] | 0.575 | +1.8 [+0.3, +3.5] | 0.009 |
| score@64 vs uniform@64 | -0.3 [-2.0, +1.0] | 0.768 | +1.0 [-0.4, +2.3] | 0.084 |
| top_heavy@128 vs uniform@128 | +0.0 [-1.3, +1.3] | 0.627 | +1.1 [-0.3, +2.6] | 0.073 |
| score@128 vs uniform@128 | -0.7 [-1.7, +0.0] | 1.000 | +0.3 [-0.8, +1.3] | 0.346 |
