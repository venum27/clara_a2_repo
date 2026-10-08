# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 65.7 | 84.0 | 92.7 | 97.3 | 100.0 | 0.0 | 21.0 | 35.0 | 58.0 | 84.3 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 30.3 [25.3, 35.7] | 32.5 [27.6, 37.8] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 30.3 [25.3, 35.7] | 32.5 [27.6, 37.8] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 30.3 [25.3, 35.7] | 32.5 [27.6, 37.8] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 34.3 [29.3, 40.0] | 37.5 [32.3, 43.0] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 33.7 [28.7, 39.3] | 36.6 [31.4, 42.2] |
| score@64 | [18.8, 14.2, 7.3, 7.3, 4.2, 4.2, 4.0, 4.0] | 64.0 vectors | 34.3 [29.3, 40.0] | 37.8 [32.8, 43.3] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 32.7 [27.7, 38.0] | 35.4 [30.5, 40.7] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 32.7 [27.7, 38.3] | 35.6 [30.9, 41.0] |
| score@128 | [32.0, 31.1, 16.2, 15.9, 8.5, 8.5, 7.9, 7.9] | 128.0 vectors | 34.0 [29.0, 39.7] | 37.3 [32.2, 42.8] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (197) | rank 2 (55) | rank 3+ (48) |
|---|---|---|---|
| uniform@32 | 31.5 | 27.8 | 41.6 |
| top_heavy@32 | 31.5 | 27.8 | 41.6 |
| score@32 | 31.5 | 27.8 | 41.6 |
| uniform@64 | 38.1 | 29.8 | 43.8 |
| top_heavy@64 | 36.4 | 30.4 | 44.4 |
| score@64 | 37.6 | 28.9 | 48.9 |
| uniform@128 | 34.1 | 31.5 | 45.2 |
| top_heavy@128 | 34.8 | 31.1 | 44.2 |
| score@128 | 35.9 | 34.4 | 46.6 |
| raw_bm25 | 25.1 | 26.0 | 19.8 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | -0.7 [-3.3, +1.7] | 0.731 | -0.9 [-3.7, +1.6] | 0.735 |
| score@64 vs uniform@64 | +0.0 [-2.3, +2.3] | 0.567 | +0.3 [-2.2, +2.9] | 0.400 |
| top_heavy@128 vs uniform@128 | +0.0 [-1.3, +1.3] | 0.597 | +0.2 [-1.3, +1.7] | 0.365 |
| score@128 vs uniform@128 | +1.3 [+0.3, +2.7] | 0.018 | +1.9 [+0.5, +3.5] | 0.002 |
