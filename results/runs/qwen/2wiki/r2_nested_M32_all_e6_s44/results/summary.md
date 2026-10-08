# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6_s44`

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
| compressed_m4 | 33.3 [28.0, 38.7] | 36.0 [30.7, 41.2] | 10 vectors |
| compressed_m8 | 35.3 [30.0, 41.0] | 39.5 [34.2, 45.0] | 20 vectors |
| compressed_m16 | 34.3 [29.0, 39.7] | 38.8 [33.6, 44.1] | 40 vectors |
| compressed_m32 | 36.3 [30.7, 41.7] | 40.6 [35.2, 46.0] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 66.0 | 85.7 | 92.7 | 97.7 | 0.0 | 24.3 | 37.7 | 60.3 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.3 [26.0, 36.7] | 34.5 [29.4, 39.6] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.3 [26.0, 36.7] | 34.5 [29.4, 39.6] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 31.3 [26.0, 36.7] | 34.5 [29.4, 39.6] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 32.7 [27.7, 38.0] | 36.4 [31.3, 41.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 33.3 [28.0, 38.7] | 36.3 [31.2, 41.6] |
| score@32 | [15.3, 8.0, 4.3, 4.3] | 32.0 vectors | 33.3 [28.0, 38.7] | 36.3 [31.2, 41.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 33.7 [28.3, 39.0] | 37.4 [32.3, 42.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 33.3 [28.0, 38.7] | 37.0 [32.0, 42.2] |
| score@64 | [30.6, 16.0, 8.7, 8.7] | 64.0 vectors | 33.3 [28.0, 38.7] | 37.1 [32.0, 42.3] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 39.0 [33.8, 44.3] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 39.0 [33.8, 44.3] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 39.0 [33.8, 44.3] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (198) | rank 2 (59) | rank 3+ (30) | not retrieved (13) |
|---|---|---|---|---|
| uniform@16 | 33.7 | 30.4 | 45.0 | 41.8 |
| top_heavy@16 | 33.7 | 30.4 | 45.0 | 41.8 |
| score@16 | 33.7 | 30.4 | 45.0 | 41.8 |
| uniform@32 | 34.7 | 34.5 | 45.7 | 49.5 |
| top_heavy@32 | 35.7 | 32.8 | 41.9 | 49.5 |
| score@32 | 35.7 | 32.8 | 41.9 | 49.5 |
| uniform@64 | 36.8 | 30.3 | 46.5 | 57.1 |
| top_heavy@64 | 35.7 | 30.9 | 47.5 | 60.2 |
| score@64 | 35.9 | 30.9 | 47.5 | 60.2 |
| uniform@128 | 38.1 | 34.1 | 46.7 | 57.1 |
| top_heavy@128 | 38.1 | 34.1 | 46.7 | 57.1 |
| score@128 | 38.1 | 34.1 | 46.7 | 57.1 |
| raw_bm25 | 23.2 | 23.9 | 23.0 | 27.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.228 | -0.1 [-1.6, +1.5] | 0.553 |
| score@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.228 | -0.1 [-1.6, +1.5] | 0.553 |
| top_heavy@64 vs uniform@64 | -0.3 [-1.7, +0.7] | 0.826 | -0.3 [-1.4, +0.5] | 0.758 |
| score@64 vs uniform@64 | -0.3 [-1.7, +0.7] | 0.826 | -0.2 [-1.2, +0.6] | 0.681 |
