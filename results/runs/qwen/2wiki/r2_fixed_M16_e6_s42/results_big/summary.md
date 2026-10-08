# Evaluation summary

Run: `runs/qwen/2wiki/r2_fixed_M16_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 60.8 | 79.7 | 88.0 | 94.8 | 0.0 | 11.1 | 19.9 | 36.8 |
| query reasoner (after E2E) | 67.6 | 84.8 | 91.9 | 97.8 | 0.0 | 22.5 | 37.4 | 59.4 |
| query reasoner (before E2E) | 15.2 | 35.5 | 52.3 | 77.0 | 0.0 | 1.1 | 4.3 | 17.4 |
| random (expected) | 24.5 | 44.2 | 60.1 | 82.2 | 0.0 | 1.7 | 5.2 | 17.8 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 28.3 [26.6, 29.9] | 31.9 [30.2, 33.5] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 30.5 [28.9, 32.2] | 35.1 [33.4, 36.8] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 31.2 [29.6, 32.9] | 35.7 [34.1, 37.4] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 31.2 [29.6, 32.9] | 35.7 [34.1, 37.4] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (2028) | rank 2 (517) | rank 3+ (330) | not retrieved (125) |
|---|---|---|---|---|
| uniform@32 | 30.3 | 33.8 | 34.7 | 41.1 |
| top_heavy@32 | 35.2 | 33.8 | 35.1 | 38.7 |
| uniform@64 | 34.9 | 37.4 | 37.2 | 39.3 |
| top_heavy@64 | 34.9 | 37.4 | 37.2 | 39.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +2.3 [+1.5, +3.1] | 0.000 | +3.2 [+2.4, +4.1] | 0.000 |
