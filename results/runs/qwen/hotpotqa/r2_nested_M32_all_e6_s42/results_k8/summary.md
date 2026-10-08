# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 68.9 | 83.9 | 89.3 | 95.0 | 99.7 | 0.0 | 20.7 | 34.4 | 51.5 | 71.6 |
| query reasoner (after E2E) | 57.2 | 73.9 | 84.3 | 95.0 | 99.7 | 0.0 | 20.4 | 36.5 | 63.5 | 86.0 |
| query reasoner (before E2E) | 39.1 | 55.2 | 66.6 | 85.3 | 98.0 | 0.0 | 10.0 | 18.4 | 34.4 | 65.6 |
| random (expected) | 20.0 | 37.8 | 53.4 | 77.8 | 97.8 | 0.0 | 2.2 | 6.7 | 22.2 | 62.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.4] | 20.4 [16.4, 24.5] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.4] | 20.4 [16.4, 24.5] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 13.4 [9.7, 17.4] | 20.4 [16.4, 24.5] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 11.4 [8.0, 15.1] | 19.3 [15.4, 23.0] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 10.4 [7.0, 13.7] | 18.8 [15.2, 22.5] |
| score@64 | [18.6, 13.9, 7.3, 7.3, 4.4, 4.4, 4.0, 4.0] | 64.0 vectors | 11.4 [8.0, 15.1] | 19.8 [15.9, 23.5] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 11.0 [7.7, 14.7] | 18.9 [15.0, 22.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 12.4 [8.7, 16.1] | 19.8 [15.9, 23.7] |
| score@128 | [32.0, 30.6, 16.5, 15.8, 8.9, 8.7, 7.8, 7.8] | 128.0 vectors | 11.7 [8.4, 15.4] | 19.0 [15.2, 23.0] |
| raw_bm25 | - | 1072 tokens | 7.4 [4.7, 10.7] | 20.9 [17.6, 24.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (171) | rank 2 (50) | rank 3+ (77) | not retrieved (1) |
|---|---|---|---|---|
| uniform@32 | 23.9 | 21.3 | 12.2 | 0.0 |
| top_heavy@32 | 23.9 | 21.3 | 12.2 | 0.0 |
| score@32 | 23.9 | 21.3 | 12.2 | 0.0 |
| uniform@64 | 23.5 | 17.5 | 11.2 | 0.0 |
| top_heavy@64 | 23.4 | 15.0 | 11.3 | 0.0 |
| score@64 | 23.9 | 19.1 | 11.4 | 0.0 |
| uniform@128 | 21.9 | 16.2 | 14.1 | 0.0 |
| top_heavy@128 | 23.3 | 15.0 | 15.3 | 0.0 |
| score@128 | 22.7 | 15.0 | 13.8 | 0.0 |
| raw_bm25 | 20.4 | 20.8 | 22.3 | 0.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | -1.0 [-2.7, +0.7] | 0.921 | -0.5 [-2.2, +1.2] | 0.710 |
| score@64 vs uniform@64 | +0.0 [-1.3, +1.3] | 0.588 | +0.5 [-1.0, +2.0] | 0.260 |
| top_heavy@128 vs uniform@128 | +1.3 [-0.0, +3.0] | 0.067 | +0.9 [-0.8, +2.6] | 0.151 |
| score@128 vs uniform@128 | +0.7 [-0.7, +2.0] | 0.236 | +0.1 [-1.3, +1.6] | 0.446 |
