# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 69.3 | 87.0 | 93.3 | 98.0 | 100.0 | 0.0 | 22.7 | 37.3 | 62.0 | 87.7 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 33.3 [28.0, 39.0] | 37.4 [32.2, 42.5] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 33.3 [28.0, 39.0] | 37.4 [32.2, 42.5] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 33.3 [28.0, 39.0] | 37.4 [32.2, 42.5] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 34.3 [29.0, 40.0] | 39.4 [34.3, 44.9] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 35.0 [29.7, 40.3] | 39.7 [34.5, 45.1] |
| score@64 | [19.0, 13.8, 7.2, 7.2, 4.3, 4.3, 4.0, 4.0] | 64.0 vectors | 34.7 [29.3, 40.3] | 39.7 [34.6, 45.2] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 35.0 [29.7, 40.7] | 39.2 [34.0, 44.6] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 33.7 [28.3, 39.0] | 38.4 [33.3, 43.8] |
| score@128 | [32.0, 30.8, 16.5, 15.8, 8.8, 8.6, 7.8, 7.8] | 128.0 vectors | 35.3 [30.0, 41.0] | 40.2 [35.0, 45.8] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (208) | rank 2 (53) | rank 3+ (39) |
|---|---|---|---|
| uniform@32 | 34.7 | 35.7 | 54.1 |
| top_heavy@32 | 34.7 | 35.7 | 54.1 |
| score@32 | 34.7 | 35.7 | 54.1 |
| uniform@64 | 38.5 | 32.0 | 54.8 |
| top_heavy@64 | 38.0 | 34.0 | 56.6 |
| score@64 | 38.2 | 34.1 | 54.8 |
| uniform@128 | 39.0 | 32.5 | 49.7 |
| top_heavy@128 | 37.6 | 33.9 | 49.1 |
| score@128 | 39.3 | 35.5 | 51.7 |
| raw_bm25 | 25.8 | 19.1 | 24.5 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +0.7 [-1.0, +2.7] | 0.288 | +0.3 [-1.6, +2.2] | 0.396 |
| score@64 vs uniform@64 | +0.3 [-1.3, +2.3] | 0.420 | +0.2 [-1.5, +1.9] | 0.391 |
| top_heavy@128 vs uniform@128 | -1.3 [-3.0, +0.0] | 0.977 | -0.8 [-2.6, +0.8] | 0.824 |
| score@128 vs uniform@128 | +0.3 [-1.0, +1.7] | 0.411 | +1.0 [-0.7, +2.6] | 0.120 |
