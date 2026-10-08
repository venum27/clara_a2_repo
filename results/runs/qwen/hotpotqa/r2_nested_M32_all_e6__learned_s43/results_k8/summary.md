# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s43`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 68.9 | 83.9 | 89.3 | 95.0 | 99.7 | 0.0 | 20.7 | 34.4 | 51.5 | 71.6 |
| query reasoner (after E2E) | 55.2 | 73.6 | 82.6 | 93.3 | 99.0 | 0.0 | 18.7 | 31.4 | 57.2 | 83.6 |
| query reasoner (before E2E) | 39.1 | 55.2 | 66.6 | 85.3 | 98.0 | 0.0 | 10.0 | 18.4 | 34.4 | 65.6 |
| random (expected) | 20.0 | 37.8 | 53.4 | 77.8 | 97.8 | 0.0 | 2.2 | 6.7 | 22.2 | 62.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.0 [9.4, 17.1] | 20.2 [16.4, 24.0] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.0 [9.4, 17.1] | 20.2 [16.4, 24.0] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.0 [9.4, 17.1] | 20.2 [16.4, 24.0] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 12.4 [8.7, 16.4] | 20.6 [16.8, 24.4] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 11.7 [8.4, 15.4] | 19.5 [15.7, 23.4] |
| score@64 | [19.4, 13.7, 7.1, 7.1, 4.3, 4.3, 4.0, 4.0] | 64.0 vectors | 12.0 [8.4, 15.7] | 20.2 [16.5, 24.1] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 11.4 [8.0, 15.1] | 19.4 [15.5, 23.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 11.7 [8.4, 15.4] | 19.7 [15.8, 23.5] |
| score@128 | [32.0, 30.8, 16.4, 15.8, 8.7, 8.6, 7.9, 7.9] | 128.0 vectors | 12.7 [9.0, 16.4] | 20.0 [16.1, 24.0] |
| raw_bm25 | - | 1072 tokens | 7.4 [4.7, 10.7] | 20.9 [17.6, 24.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (165) | rank 2 (55) | rank 3+ (76) | not retrieved (3) |
|---|---|---|---|---|
| uniform@32 | 21.5 | 16.2 | 21.1 | 0.0 |
| top_heavy@32 | 21.5 | 16.2 | 21.1 | 0.0 |
| score@32 | 21.5 | 16.2 | 21.1 | 0.0 |
| uniform@64 | 20.8 | 19.1 | 21.8 | 0.0 |
| top_heavy@64 | 21.5 | 16.5 | 18.0 | 0.0 |
| score@64 | 21.6 | 18.2 | 19.5 | 0.0 |
| uniform@128 | 20.6 | 15.8 | 19.9 | 0.0 |
| top_heavy@128 | 20.9 | 18.3 | 19.1 | 0.0 |
| score@128 | 21.8 | 18.0 | 18.3 | 0.0 |
| raw_bm25 | 20.5 | 26.8 | 17.9 | 4.4 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | -0.7 [-2.0, +0.3] | 0.912 | -1.0 [-3.0, +0.7] | 0.870 |
| score@64 vs uniform@64 | -0.3 [-1.3, +0.7] | 0.824 | -0.3 [-2.0, +1.2] | 0.661 |
| top_heavy@128 vs uniform@128 | +0.3 [-1.0, +1.7] | 0.432 | +0.4 [-1.3, +2.0] | 0.314 |
| score@128 vs uniform@128 | +1.3 [+0.0, +3.0] | 0.060 | +0.7 [-0.9, +2.4] | 0.219 |
