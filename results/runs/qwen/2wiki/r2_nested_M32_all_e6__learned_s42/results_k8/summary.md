# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 69.3 | 85.7 | 92.7 | 97.7 | 99.7 | 0.0 | 23.0 | 36.7 | 61.3 | 86.7 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.0 [26.0, 36.7] | 34.1 [29.1, 39.7] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.0 [26.0, 36.7] | 34.1 [29.1, 39.7] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.0 [26.0, 36.7] | 34.1 [29.1, 39.7] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 32.7 [27.3, 38.3] | 36.6 [31.5, 42.0] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 33.7 [28.7, 39.3] | 37.1 [31.9, 42.6] |
| score@64 | [19.1, 13.9, 7.2, 7.2, 4.3, 4.3, 4.0, 4.0] | 64.0 vectors | 33.7 [28.3, 39.3] | 37.2 [31.9, 42.8] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 32.0 [27.0, 37.3] | 35.7 [30.8, 41.0] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 32.0 [27.0, 37.3] | 35.4 [30.5, 40.6] |
| score@128 | [32.0, 30.9, 16.3, 15.9, 8.6, 8.5, 7.9, 7.9] | 128.0 vectors | 32.7 [27.7, 38.0] | 35.8 [30.7, 41.0] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (208) | rank 2 (49) | rank 3+ (42) | not retrieved (1) |
|---|---|---|---|---|
| uniform@32 | 30.7 | 42.5 | 41.3 | 33.3 |
| top_heavy@32 | 30.7 | 42.5 | 41.3 | 33.3 |
| score@32 | 30.7 | 42.5 | 41.3 | 33.3 |
| uniform@64 | 34.6 | 41.6 | 40.8 | 33.3 |
| top_heavy@64 | 35.2 | 39.7 | 43.1 | 33.3 |
| score@64 | 35.4 | 41.7 | 40.8 | 33.3 |
| uniform@128 | 33.1 | 43.4 | 38.7 | 66.7 |
| top_heavy@128 | 32.3 | 43.5 | 41.3 | 33.3 |
| score@128 | 33.6 | 41.5 | 40.2 | 33.3 |
| raw_bm25 | 24.9 | 27.1 | 19.7 | 0.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +1.0 [-0.7, +2.7] | 0.170 | +0.4 [-1.4, +2.3] | 0.339 |
| score@64 vs uniform@64 | +1.0 [-0.7, +3.0] | 0.167 | +0.5 [-1.1, +2.2] | 0.265 |
| top_heavy@128 vs uniform@128 | +0.0 [-2.0, +2.0] | 0.558 | -0.3 [-2.4, +1.7] | 0.609 |
| score@128 vs uniform@128 | +0.7 [-1.3, +2.7] | 0.323 | +0.1 [-1.9, +2.0] | 0.487 |
