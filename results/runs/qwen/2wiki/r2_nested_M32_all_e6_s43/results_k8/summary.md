# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6_s43`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 63.7 | 85.3 | 94.3 | 97.7 | 100.0 | 0.0 | 21.3 | 31.7 | 62.7 | 87.0 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 32.3 [26.7, 37.7] | 35.1 [29.7, 40.4] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 32.3 [26.7, 37.7] | 35.1 [29.7, 40.4] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 32.3 [26.7, 37.7] | 35.1 [29.7, 40.4] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 33.7 [28.0, 39.0] | 37.3 [31.9, 42.4] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 33.7 [28.3, 39.0] | 37.3 [31.9, 42.6] |
| score@64 | [18.7, 14.0, 7.3, 7.3, 4.3, 4.3, 4.0, 4.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 38.0 [32.6, 43.3] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 34.0 [28.7, 39.3] | 38.2 [32.9, 43.4] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 33.7 [28.3, 39.0] | 38.2 [32.9, 43.4] |
| score@128 | [32.0, 30.8, 16.3, 15.8, 8.7, 8.6, 7.9, 7.9] | 128.0 vectors | 33.7 [28.3, 39.3] | 37.8 [32.6, 43.2] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (191) | rank 2 (65) | rank 3+ (44) |
|---|---|---|---|
| uniform@32 | 35.5 | 32.9 | 36.4 |
| top_heavy@32 | 35.5 | 32.9 | 36.4 |
| score@32 | 35.5 | 32.9 | 36.4 |
| uniform@64 | 36.4 | 39.7 | 37.7 |
| top_heavy@64 | 37.4 | 38.3 | 35.5 |
| score@64 | 37.4 | 39.7 | 37.7 |
| uniform@128 | 36.8 | 41.6 | 38.7 |
| top_heavy@128 | 37.6 | 38.0 | 40.9 |
| score@128 | 37.5 | 37.8 | 39.4 |
| raw_bm25 | 25.3 | 22.4 | 23.7 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | +0.0 [-2.0, +1.7] | 0.573 | +0.0 [-2.0, +2.1] | 0.499 |
| score@64 vs uniform@64 | +0.3 [-1.3, +2.0] | 0.421 | +0.6 [-1.2, +2.5] | 0.242 |
| top_heavy@128 vs uniform@128 | -0.3 [-1.7, +1.0] | 0.757 | +0.0 [-1.7, +1.7] | 0.479 |
| score@128 vs uniform@128 | -0.3 [-1.7, +0.7] | 0.815 | -0.3 [-1.6, +0.9] | 0.678 |
