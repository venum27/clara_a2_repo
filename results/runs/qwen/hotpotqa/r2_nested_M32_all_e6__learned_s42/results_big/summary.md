# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 70.2 | 83.5 | 90.0 | 95.6 | 0.0 | 21.7 | 34.5 | 52.0 |
| query reasoner (after E2E) | 57.7 | 76.1 | 85.4 | 94.9 | 0.0 | 18.9 | 33.9 | 57.3 |
| query reasoner (before E2E) | 43.7 | 62.2 | 73.6 | 88.1 | 0.0 | 8.5 | 16.4 | 37.0 |
| random (expected) | 20.1 | 37.9 | 53.5 | 77.9 | 0.0 | 2.3 | 6.8 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 11.1 [10.1, 12.3] | 18.5 [17.3, 19.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.2 [10.2, 12.4] | 18.7 [17.5, 19.9] |
| learned@32 | [6.7, 5.1, 15.5, 4.7] | 32.0 vectors | 11.2 [10.1, 12.3] | 18.6 [17.3, 19.8] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.3 [10.3, 12.5] | 18.8 [17.6, 20.1] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 11.5 [10.4, 12.7] | 19.0 [17.8, 20.2] |
| learned@64 | [14.9, 15.6, 17.4, 16.1] | 64.0 vectors | 11.3 [10.2, 12.5] | 18.7 [17.5, 20.0] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 32 | [6.7, 5.1, 15.5, 4.7] | 7.6 | 8.2 |
| 64 | [14.9, 15.6, 17.4, 16.1] | 15.8 | 16.1 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (1732) | rank 2 (552) | rank 3+ (459) | not retrieved (257) |
|---|---|---|---|---|
| uniform@32 | 20.1 | 17.6 | 16.0 | 13.8 |
| top_heavy@32 | 20.6 | 17.4 | 15.8 | 14.1 |
| learned@32 | 20.2 | 16.9 | 16.6 | 14.5 |
| uniform@64 | 20.5 | 17.0 | 16.5 | 15.1 |
| top_heavy@64 | 21.0 | 16.8 | 16.4 | 14.7 |
| learned@64 | 20.4 | 16.8 | 16.5 | 15.4 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.1 [-0.2, +0.4] | 0.321 | +0.2 [-0.2, +0.6] | 0.140 |
| learned@32 vs uniform@32 | +0.1 [-0.2, +0.3] | 0.368 | +0.1 [-0.3, +0.4] | 0.312 |
| learned@32 vs top_heavy@32 | -0.0 [-0.4, +0.3] | 0.621 | -0.1 [-0.6, +0.3] | 0.739 |
| top_heavy@64 vs uniform@64 | +0.2 [-0.2, +0.5] | 0.192 | +0.2 [-0.2, +0.6] | 0.204 |
| learned@64 vs uniform@64 | -0.0 [-0.2, +0.1] | 0.756 | -0.1 [-0.3, +0.1] | 0.907 |
| learned@64 vs top_heavy@64 | -0.2 [-0.6, +0.2] | 0.879 | -0.3 [-0.7, +0.1] | 0.911 |
