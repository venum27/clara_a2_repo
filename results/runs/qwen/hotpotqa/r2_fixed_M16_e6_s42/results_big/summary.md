# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_fixed_M16_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 70.2 | 83.5 | 90.0 | 95.6 | 0.0 | 21.7 | 34.5 | 52.0 |
| query reasoner (after E2E) | 50.8 | 70.2 | 80.4 | 93.7 | 0.0 | 14.6 | 27.0 | 51.9 |
| query reasoner (before E2E) | 38.0 | 55.6 | 67.9 | 84.5 | 0.0 | 6.5 | 14.1 | 32.7 |
| random (expected) | 20.1 | 37.9 | 53.5 | 77.9 | 0.0 | 2.3 | 6.8 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 11.9 [10.7, 13.0] | 19.4 [18.1, 20.6] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.8 [10.7, 13.0] | 19.8 [18.5, 20.9] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.5 [10.4, 12.6] | 19.8 [18.5, 21.0] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.5 [10.4, 12.6] | 19.8 [18.5, 21.0] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (1523) | rank 2 (583) | rank 3+ (538) | not retrieved (356) |
|---|---|---|---|---|
| uniform@32 | 22.5 | 17.7 | 15.3 | 14.7 |
| top_heavy@32 | 23.9 | 17.3 | 14.1 | 14.6 |
| uniform@64 | 23.3 | 19.2 | 14.7 | 13.3 |
| top_heavy@64 | 23.3 | 19.2 | 14.7 | 13.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.0 [-0.5, +0.4] | 0.597 | +0.4 [-0.2, +1.0] | 0.081 |
