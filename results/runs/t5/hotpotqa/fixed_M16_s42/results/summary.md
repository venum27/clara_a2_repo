# Evaluation summary

Run: `runs/t5/hotpotqa/fixed_M16_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 24,576
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 2.9 [1.5, 4.2] | 13.9 [11.7, 16.0] | 520 |
| 8 | 2.7 [1.3, 4.0] | 13.9 [11.7, 16.0] | 520 |
| 16 | 2.9 [1.5, 4.2] | 14.2 [12.0, 16.3] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 11.7 [8.0, 15.3] | 20.6 [16.7, 24.6] | 8 vectors |
| compressed_m8 | 10.3 [7.0, 14.0] | 19.3 [15.5, 23.0] | 16 vectors |
| compressed_m16 | 10.7 [7.3, 14.3] | 19.5 [15.6, 23.2] | 32 vectors |
| raw_text_gold | 57.3 [51.7, 63.0] | 72.0 [67.2, 76.4] | 208 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 48.3 | 66.3 | 76.7 | 90.3 | 0.0 | 19.0 | 29.3 | 55.0 |
| query reasoner (before E2E) | 45.0 | 61.7 | 74.3 | 88.7 | 0.0 | 17.3 | 27.0 | 48.3 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.3 [7.7, 15.0] | 20.2 [16.4, 24.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.3 [7.7, 15.0] | 20.2 [16.4, 24.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.3 [7.7, 15.0] | 20.2 [16.4, 24.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 10.7 [7.3, 14.0] | 19.0 [15.3, 22.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 19.3 [15.5, 23.0] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 11.0 [7.7, 14.7] | 19.2 [15.4, 22.9] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.0 [7.0, 13.7] | 18.7 [15.0, 22.4] |
| raw_bm25 | - | 528 tokens | 19.0 [14.7, 23.3] | 26.0 [21.5, 30.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (145) | rank 2 (54) | rank 3+ (54) | not retrieved (47) |
|---|---|---|---|---|
| uniform@16 | 21.6 | 15.3 | 26.8 | 14.2 |
| top_heavy@16 | 21.6 | 15.3 | 26.8 | 14.2 |
| score@16 | 21.6 | 15.3 | 26.8 | 14.2 |
| uniform@32 | 19.6 | 16.6 | 23.9 | 14.4 |
| top_heavy@32 | 20.2 | 17.1 | 23.8 | 13.6 |
| score@32 | 20.2 | 17.1 | 23.4 | 13.6 |
| uniform@64 | 19.7 | 14.7 | 24.6 | 13.4 |
| top_heavy@64 | 19.7 | 14.7 | 24.6 | 13.4 |
| score@64 | 19.7 | 14.7 | 24.6 | 13.4 |
| uniform@128 | 19.7 | 14.7 | 24.6 | 13.4 |
| top_heavy@128 | 19.7 | 14.7 | 24.6 | 13.4 |
| score@128 | 19.7 | 14.7 | 24.6 | 13.4 |
| raw_bm25 | 28.5 | 25.7 | 19.9 | 25.4 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.3 [+0.0, +1.0] | 0.362 | +0.2 [-0.8, +1.4] | 0.340 |
| score@32 vs uniform@32 | +0.3 [+0.0, +1.0] | 0.362 | +0.1 [-0.9, +1.3] | 0.403 |
