# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 66.0 | 85.7 | 92.7 | 97.7 | 100.0 | 0.0 | 24.3 | 37.7 | 60.3 | 85.3 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.3 [26.0, 36.7] | 35.0 [29.9, 40.3] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.3 [26.0, 36.7] | 35.0 [29.9, 40.3] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 31.3 [26.0, 36.7] | 35.0 [29.9, 40.3] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 34.3 [29.0, 39.7] | 37.8 [32.8, 43.1] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 34.7 [29.3, 40.3] | 38.6 [33.4, 44.0] |
| score@64 | [19.2, 13.6, 7.2, 7.2, 4.4, 4.4, 4.0, 4.0] | 64.0 vectors | 34.3 [29.0, 40.0] | 38.1 [33.0, 43.4] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.8 [32.5, 43.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 33.7 [28.3, 39.0] | 37.1 [31.9, 42.6] |
| score@128 | [32.0, 30.4, 16.5, 15.8, 8.9, 8.8, 7.9, 7.9] | 128.0 vectors | 33.7 [28.3, 39.3] | 37.3 [32.0, 42.9] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (198) | rank 2 (59) | rank 3+ (43) |
|---|---|---|---|
| uniform@32 | 34.6 | 29.3 | 44.6 |
| top_heavy@32 | 34.6 | 29.3 | 44.6 |
| score@32 | 34.6 | 29.3 | 44.6 |
| uniform@64 | 37.0 | 34.4 | 46.3 |
| top_heavy@64 | 37.7 | 35.1 | 48.0 |
| score@64 | 37.1 | 34.0 | 48.4 |
| uniform@128 | 38.5 | 32.5 | 42.3 |
| top_heavy@128 | 36.3 | 34.5 | 44.4 |
| score@128 | 37.6 | 34.5 | 39.7 |
| raw_bm25 | 25.2 | 23.0 | 22.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +0.3 [-0.7, +1.3] | 0.407 | +0.8 [-0.8, +2.4] | 0.149 |
| score@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.666 | +0.3 [-0.9, +1.4] | 0.309 |
| top_heavy@128 vs uniform@128 | -0.3 [-2.0, +1.3] | 0.722 | -0.7 [-2.7, +1.1] | 0.779 |
| score@128 vs uniform@128 | -0.3 [-1.3, +0.7] | 0.802 | -0.6 [-2.1, +0.9] | 0.764 |
