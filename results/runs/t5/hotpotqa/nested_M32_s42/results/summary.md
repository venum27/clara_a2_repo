# Evaluation summary

Run: `runs/t5/hotpotqa/nested_M32_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 49,152
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x, m=32: 4.1x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 2.9 [1.5, 4.2] | 13.8 [11.7, 16.0] | 520 |
| 8 | 3.1 [1.7, 4.4] | 14.6 [12.3, 16.9] | 520 |
| 16 | 3.1 [1.7, 4.4] | 14.1 [11.9, 16.3] | 520 |
| 32 | 3.5 [1.9, 5.0] | 14.2 [12.0, 16.4] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 11.0 [7.7, 14.7] | 19.2 [15.5, 22.9] | 8 vectors |
| compressed_m8 | 10.7 [7.3, 14.0] | 19.2 [15.5, 22.9] | 16 vectors |
| compressed_m16 | 11.3 [7.7, 15.0] | 20.1 [16.2, 23.9] | 32 vectors |
| compressed_m32 | 12.0 [8.3, 15.7] | 20.2 [16.3, 24.0] | 64 vectors |
| raw_text_gold | 57.3 [51.7, 63.0] | 72.0 [67.2, 76.4] | 208 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 49.7 | 67.3 | 78.0 | 91.0 | 0.0 | 16.7 | 26.3 | 50.7 |
| query reasoner (before E2E) | 42.7 | 59.7 | 71.0 | 89.0 | 0.0 | 16.0 | 25.7 | 48.3 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.3, 14.7] | 18.4 [14.7, 22.1] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.3, 14.7] | 18.4 [14.7, 22.1] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.3, 14.7] | 18.4 [14.7, 22.1] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 10.7 [7.3, 14.3] | 18.3 [14.6, 22.0] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 18.5 [14.8, 22.2] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 11.0 [7.7, 14.7] | 18.5 [14.8, 22.2] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.3 [7.0, 13.7] | 18.2 [14.5, 21.9] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 10.7 [7.3, 14.0] | 18.4 [14.6, 22.1] |
| score@64 | [30.9, 16.0, 8.5, 8.5] | 64.0 vectors | 10.7 [7.3, 14.0] | 18.4 [14.6, 22.1] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.0 [7.7, 14.7] | 18.5 [14.7, 22.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.0 [7.7, 14.7] | 18.5 [14.7, 22.1] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.0 [7.7, 14.7] | 18.5 [14.7, 22.1] |
| raw_bm25 | - | 528 tokens | 19.0 [14.7, 23.3] | 26.0 [21.5, 30.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (149) | rank 2 (53) | rank 3+ (54) | not retrieved (44) |
|---|---|---|---|---|
| uniform@16 | 20.6 | 17.2 | 16.1 | 15.1 |
| top_heavy@16 | 20.6 | 17.2 | 16.1 | 15.1 |
| score@16 | 20.6 | 17.2 | 16.1 | 15.1 |
| uniform@32 | 21.0 | 15.6 | 16.1 | 15.1 |
| top_heavy@32 | 21.5 | 15.3 | 16.1 | 15.1 |
| score@32 | 21.5 | 15.3 | 16.1 | 15.1 |
| uniform@64 | 20.7 | 15.6 | 16.4 | 15.1 |
| top_heavy@64 | 21.3 | 15.6 | 15.7 | 15.1 |
| score@64 | 21.3 | 15.6 | 15.7 | 15.1 |
| uniform@128 | 20.8 | 16.1 | 17.1 | 15.1 |
| top_heavy@128 | 20.8 | 16.1 | 17.1 | 15.1 |
| score@128 | 20.8 | 16.1 | 17.1 | 15.1 |
| raw_bm25 | 29.9 | 18.6 | 18.2 | 31.1 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.3 [+0.0, +1.0] | 0.371 | +0.2 [-0.9, +1.2] | 0.365 |
| score@32 vs uniform@32 | +0.3 [+0.0, +1.0] | 0.371 | +0.2 [-0.9, +1.2] | 0.365 |
| top_heavy@64 vs uniform@64 | +0.3 [-0.7, +1.3] | 0.390 | +0.1 [-1.0, +1.3] | 0.423 |
| score@64 vs uniform@64 | +0.3 [-0.7, +1.3] | 0.390 | +0.1 [-1.0, +1.3] | 0.423 |
