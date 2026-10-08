# Evaluation summary

Run: `runs/qwen/2wiki/fixed_M16_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 28,672
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 3.0 [1.7, 4.6] | 13.2 [11.2, 15.4] | 525 |
| 8 | 6.9 [4.8, 9.1] | 21.5 [18.8, 24.1] | 525 |
| 16 | 9.3 [7.0, 11.8] | 25.4 [22.6, 28.4] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 26.7 [21.7, 32.0] | 28.9 [23.8, 34.2] | 10 vectors |
| compressed_m8 | 28.0 [23.0, 33.3] | 31.7 [26.7, 36.9] | 20 vectors |
| compressed_m16 | 28.0 [23.0, 33.3] | 31.3 [26.5, 36.6] | 40 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 69.7 | 85.7 | 92.0 | 98.3 | 0.0 | 25.0 | 37.7 | 54.0 |
| query reasoner (before E2E) | 13.0 | 28.3 | 45.3 | 72.7 | 0.0 | 1.3 | 5.7 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 28.0 [23.0, 33.0] | 30.4 [25.3, 35.4] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 28.0 [23.0, 33.0] | 30.4 [25.3, 35.4] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 28.0 [23.0, 33.0] | 30.4 [25.3, 35.4] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 29.3 [24.0, 34.7] | 32.8 [27.6, 38.0] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 30.0 [25.0, 35.3] | 33.2 [28.2, 38.4] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 29.3 [24.3, 34.7] | 32.5 [27.4, 37.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 28.0 [23.0, 33.3] | 31.4 [26.3, 36.7] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (209) | rank 2 (48) | rank 3+ (29) | not retrieved (14) |
|---|---|---|---|---|
| uniform@16 | 26.9 | 31.2 | 38.1 | 64.3 |
| top_heavy@16 | 26.9 | 31.2 | 38.1 | 64.3 |
| score@16 | 26.9 | 31.2 | 38.1 | 64.3 |
| uniform@32 | 29.6 | 33.4 | 39.1 | 66.7 |
| top_heavy@32 | 30.7 | 33.3 | 34.7 | 66.7 |
| score@32 | 29.7 | 33.4 | 34.7 | 66.7 |
| uniform@64 | 27.9 | 36.0 | 32.6 | 66.7 |
| top_heavy@64 | 27.9 | 36.0 | 32.6 | 66.7 |
| score@64 | 27.9 | 36.0 | 32.6 | 66.7 |
| uniform@128 | 27.9 | 36.0 | 32.6 | 66.7 |
| top_heavy@128 | 27.9 | 36.0 | 32.6 | 66.7 |
| score@128 | 27.9 | 36.0 | 32.6 | 66.7 |
| raw_bm25 | 23.1 | 23.4 | 24.8 | 26.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.7 [-1.3, +2.7] | 0.312 | +0.4 [-1.8, +2.5] | 0.369 |
| score@32 vs uniform@32 | +0.0 [-2.0, +1.7] | 0.562 | -0.4 [-2.3, +1.5] | 0.638 |
