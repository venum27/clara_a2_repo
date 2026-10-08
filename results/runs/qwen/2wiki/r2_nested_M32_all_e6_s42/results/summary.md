# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 5.5 [3.6, 7.4] | 21.6 [19.0, 24.2] | 525 |
| 8 | 7.0 [5.1, 9.3] | 23.8 [21.2, 26.5] | 525 |
| 16 | 8.8 [6.5, 11.2] | 25.7 [23.0, 28.7] | 525 |
| 32 | 9.0 [6.7, 11.4] | 26.6 [23.8, 29.4] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 32.3 [27.3, 38.0] | 35.3 [30.3, 40.7] | 10 vectors |
| compressed_m8 | 35.3 [30.0, 41.0] | 39.7 [34.4, 45.3] | 20 vectors |
| compressed_m16 | 35.0 [29.7, 40.7] | 39.5 [34.2, 44.9] | 40 vectors |
| compressed_m32 | 32.7 [27.7, 38.0] | 36.5 [31.5, 41.9] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 65.7 | 84.0 | 92.7 | 97.3 | 0.0 | 21.0 | 35.0 | 58.0 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.7 [26.3, 37.0] | 34.5 [29.4, 39.9] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.7 [26.3, 37.0] | 34.5 [29.4, 39.9] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.7 [26.3, 37.0] | 34.5 [29.4, 39.9] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.0 [27.7, 38.3] | 36.7 [31.4, 42.2] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 32.7 [27.7, 38.0] | 35.6 [30.5, 40.9] |
| score@32 | [15.3, 8.0, 4.3, 4.3] | 32.0 vectors | 32.7 [27.7, 38.0] | 35.8 [30.7, 41.1] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 31.7 [26.7, 37.0] | 34.5 [29.5, 39.9] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 32.0 [27.0, 37.7] | 35.8 [30.7, 41.3] |
| score@64 | [30.7, 16.0, 8.7, 8.7] | 64.0 vectors | 32.0 [27.0, 37.7] | 35.6 [30.5, 41.1] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 32.7 [27.7, 38.0] | 35.8 [30.8, 40.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 32.7 [27.7, 38.0] | 35.8 [30.8, 40.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 32.7 [27.7, 38.0] | 35.8 [30.8, 40.9] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (197) | rank 2 (55) | rank 3+ (38) | not retrieved (10) |
|---|---|---|---|---|
| uniform@16 | 33.6 | 30.4 | 39.9 | 53.3 |
| top_heavy@16 | 33.6 | 30.4 | 39.9 | 53.3 |
| score@16 | 33.6 | 30.4 | 39.9 | 53.3 |
| uniform@32 | 35.9 | 30.2 | 43.2 | 63.3 |
| top_heavy@32 | 36.7 | 26.6 | 38.0 | 53.3 |
| score@32 | 37.1 | 26.5 | 38.0 | 53.3 |
| uniform@64 | 34.1 | 27.5 | 39.0 | 63.3 |
| top_heavy@64 | 34.9 | 31.8 | 39.5 | 63.3 |
| score@64 | 34.5 | 31.6 | 39.5 | 63.3 |
| uniform@128 | 35.1 | 31.7 | 38.4 | 63.3 |
| top_heavy@128 | 35.1 | 31.7 | 38.4 | 63.3 |
| score@128 | 35.1 | 31.7 | 38.4 | 63.3 |
| raw_bm25 | 23.3 | 24.4 | 22.2 | 27.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-2.3, +1.7] | 0.692 | -1.1 [-3.2, +0.9] | 0.862 |
| score@32 vs uniform@32 | -0.3 [-2.3, +1.7] | 0.692 | -0.9 [-2.9, +1.0] | 0.819 |
| top_heavy@64 vs uniform@64 | +0.3 [-1.0, +2.0] | 0.405 | +1.3 [-0.3, +3.2] | 0.050 |
| score@64 vs uniform@64 | +0.3 [-1.0, +2.0] | 0.405 | +1.1 [-0.5, +2.8] | 0.086 |
