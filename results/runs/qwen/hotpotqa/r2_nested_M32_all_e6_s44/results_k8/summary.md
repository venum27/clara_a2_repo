# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 68.9 | 83.9 | 89.3 | 95.0 | 99.7 | 0.0 | 20.7 | 34.4 | 51.5 | 71.6 |
| query reasoner (after E2E) | 55.9 | 74.9 | 83.3 | 93.3 | 99.7 | 0.0 | 16.4 | 30.1 | 59.2 | 86.0 |
| query reasoner (before E2E) | 39.1 | 55.2 | 66.6 | 85.3 | 98.0 | 0.0 | 10.0 | 18.4 | 34.4 | 65.6 |
| random (expected) | 20.0 | 37.8 | 53.4 | 77.8 | 97.8 | 0.0 | 2.2 | 6.7 | 22.2 | 62.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 12.7 [9.0, 16.7] | 20.7 [16.8, 24.7] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 12.7 [9.0, 16.7] | 20.7 [16.8, 24.7] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 12.7 [9.0, 16.7] | 20.7 [16.8, 24.7] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 12.7 [9.0, 16.7] | 20.4 [16.5, 24.6] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 13.7 [10.0, 18.1] | 21.3 [17.3, 25.5] |
| score@64 | [18.0, 14.2, 7.5, 7.5, 4.4, 4.4, 4.0, 4.0] | 64.0 vectors | 13.0 [9.4, 17.1] | 20.0 [16.2, 24.1] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 11.4 [8.0, 15.1] | 19.3 [15.6, 23.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 11.7 [8.4, 15.4] | 19.4 [15.7, 23.4] |
| score@128 | [32.0, 30.3, 16.4, 15.8, 9.0, 8.8, 7.8, 7.8] | 128.0 vectors | 13.0 [9.4, 17.1] | 19.9 [16.2, 24.1] |
| raw_bm25 | - | 1072 tokens | 7.4 [4.7, 10.7] | 20.9 [17.6, 24.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (167) | rank 2 (57) | rank 3+ (74) | not retrieved (1) |
|---|---|---|---|---|
| uniform@32 | 22.7 | 19.1 | 17.8 | 0.0 |
| top_heavy@32 | 22.7 | 19.1 | 17.8 | 0.0 |
| score@32 | 22.7 | 19.1 | 17.8 | 0.0 |
| uniform@64 | 21.0 | 18.2 | 21.2 | 0.0 |
| top_heavy@64 | 22.5 | 20.1 | 19.7 | 0.0 |
| score@64 | 21.1 | 17.6 | 19.8 | 0.0 |
| uniform@128 | 19.8 | 15.7 | 21.0 | 0.0 |
| top_heavy@128 | 19.2 | 19.7 | 20.1 | 0.0 |
| score@128 | 19.8 | 20.1 | 20.3 | 0.0 |
| raw_bm25 | 21.5 | 19.6 | 20.7 | 0.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +1.0 [-1.0, +3.0] | 0.208 | +0.8 [-1.2, +2.9] | 0.233 |
| score@64 vs uniform@64 | +0.3 [+0.0, +1.0] | 0.376 | -0.4 [-1.5, +0.7] | 0.763 |
| top_heavy@128 vs uniform@128 | +0.3 [-1.0, +1.7] | 0.412 | +0.2 [-1.7, +2.0] | 0.431 |
| score@128 vs uniform@128 | +1.7 [+0.3, +3.3] | 0.005 | +0.7 [-0.9, +2.4] | 0.230 |
