# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s43`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | hit@8 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 | all_gold@8 |
|---|---|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 99.3 | 0.0 | 12.0 | 22.0 | 36.0 | 63.7 |
| query reasoner (after E2E) | 71.7 | 87.7 | 93.7 | 96.7 | 99.7 | 0.0 | 25.7 | 35.7 | 61.0 | 88.7 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 97.7 | 0.0 | 1.7 | 5.0 | 16.7 | 49.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 98.3 | 0.0 | 1.7 | 5.0 | 17.3 | 55.1 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 35.3 [29.7, 40.7] | 39.0 [33.6, 44.2] |
| top_heavy@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 35.3 [29.7, 40.7] | 39.0 [33.6, 44.2] |
| score@32 | [4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 32.0 vectors | 35.3 [29.7, 40.7] | 39.0 [33.6, 44.2] |
| uniform@64 | [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0] | 64.0 vectors | 36.0 [30.3, 41.3] | 39.4 [33.8, 44.8] |
| top_heavy@64 | [32.0, 8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0] | 64.0 vectors | 35.3 [30.0, 41.0] | 39.0 [33.6, 44.3] |
| score@64 | [18.9, 14.1, 7.3, 7.3, 4.3, 4.3, 4.0, 4.0] | 64.0 vectors | 35.0 [29.3, 40.7] | 38.5 [33.1, 43.8] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0, 16.0] | 128.0 vectors | 36.0 [30.3, 41.7] | 39.7 [34.3, 45.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 16.0, 4.0, 4.0, 4.0, 4.0] | 128.0 vectors | 36.3 [31.0, 42.0] | 40.1 [34.7, 45.4] |
| score@128 | [32.0, 31.0, 16.1, 16.0, 8.5, 8.5, 8.0, 8.0] | 128.0 vectors | 36.3 [31.0, 41.7] | 40.4 [35.1, 45.7] |
| raw_bm25 | - | 816 tokens | 14.7 [10.7, 18.7] | 24.4 [20.3, 28.2] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (215) | rank 2 (48) | rank 3+ (36) | not retrieved (1) |
|---|---|---|---|---|
| uniform@32 | 37.5 | 36.4 | 52.5 | 0.0 |
| top_heavy@32 | 37.5 | 36.4 | 52.5 | 0.0 |
| score@32 | 37.5 | 36.4 | 52.5 | 0.0 |
| uniform@64 | 38.5 | 34.3 | 51.7 | 40.0 |
| top_heavy@64 | 38.2 | 34.3 | 50.8 | 0.0 |
| score@64 | 36.8 | 35.8 | 52.4 | 40.0 |
| uniform@128 | 38.5 | 35.3 | 52.6 | 40.0 |
| top_heavy@128 | 38.4 | 35.3 | 57.2 | 40.0 |
| score@128 | 38.6 | 35.3 | 58.0 | 40.0 |
| raw_bm25 | 22.7 | 36.3 | 19.7 | 0.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@64 vs uniform@64 | -0.7 [-3.3, +2.0] | 0.739 | -0.5 [-3.3, +2.4] | 0.647 |
| score@64 vs uniform@64 | -1.0 [-3.3, +1.3] | 0.846 | -0.9 [-3.5, +1.2] | 0.785 |
| top_heavy@128 vs uniform@128 | +0.3 [-1.3, +2.0] | 0.438 | +0.4 [-1.3, +2.1] | 0.309 |
| score@128 vs uniform@128 | +0.3 [-1.0, +1.7] | 0.407 | +0.7 [-0.8, +2.1] | 0.172 |
