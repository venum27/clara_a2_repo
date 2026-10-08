# Evaluation summary

Run: `runs/qwen/2wiki/r2_fixed_M16_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 28,672
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 4.2 [2.7, 6.1] | 13.8 [11.6, 16.1] | 525 |
| 8 | 4.8 [3.0, 6.7] | 17.0 [14.6, 19.5] | 525 |
| 16 | 10.9 [8.2, 13.3] | 27.9 [24.8, 30.7] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 33.7 [28.3, 39.3] | 36.7 [31.3, 41.9] | 10 vectors |
| compressed_m8 | 33.0 [27.3, 38.3] | 36.4 [31.2, 41.6] | 20 vectors |
| compressed_m16 | 36.3 [31.0, 42.0] | 40.5 [35.2, 46.0] | 40 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 64.0 | 81.0 | 91.3 | 96.0 | 0.0 | 21.3 | 32.7 | 54.0 |
| query reasoner (before E2E) | 15.3 | 35.3 | 49.7 | 74.7 | 0.0 | 1.3 | 4.3 | 13.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.0, 39.0] | 36.3 [30.9, 41.5] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.0, 39.0] | 36.3 [30.9, 41.5] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.0, 39.0] | 36.3 [30.9, 41.5] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.7 [28.0, 39.0] | 36.5 [30.9, 41.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 34.3 [29.0, 39.7] | 37.9 [32.6, 43.1] |
| score@32 | [15.3, 8.0, 4.3, 4.3] | 32.0 vectors | 34.3 [29.0, 39.7] | 38.0 [32.7, 43.3] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.3] | 37.7 [32.4, 43.0] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (192) | rank 2 (51) | rank 3+ (41) | not retrieved (16) |
|---|---|---|---|---|
| uniform@16 | 33.0 | 38.6 | 46.7 | 41.7 |
| top_heavy@16 | 33.0 | 38.6 | 46.7 | 41.7 |
| score@16 | 33.0 | 38.6 | 46.7 | 41.7 |
| uniform@32 | 33.1 | 38.1 | 45.5 | 47.9 |
| top_heavy@32 | 34.7 | 44.8 | 42.8 | 42.1 |
| score@32 | 34.7 | 44.8 | 43.6 | 42.1 |
| uniform@64 | 34.3 | 42.7 | 47.8 | 35.8 |
| top_heavy@64 | 34.3 | 42.7 | 47.8 | 35.8 |
| score@64 | 34.3 | 42.7 | 47.8 | 35.8 |
| uniform@128 | 34.3 | 42.7 | 47.8 | 35.8 |
| top_heavy@128 | 34.3 | 42.7 | 47.8 | 35.8 |
| score@128 | 34.3 | 42.7 | 47.8 | 35.8 |
| raw_bm25 | 22.8 | 19.8 | 29.3 | 28.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.7 [-1.7, +3.0] | 0.350 | +1.4 [-1.2, +4.1] | 0.141 |
| score@32 vs uniform@32 | +0.7 [-1.7, +3.0] | 0.350 | +1.6 [-1.1, +4.2] | 0.120 |
