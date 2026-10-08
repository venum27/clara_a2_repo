# Evaluation summary

Run: `runs/qwen/2wiki/nested_M32_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 6.1 [4.2, 8.2] | 20.5 [18.0, 23.2] | 525 |
| 8 | 6.5 [4.4, 8.8] | 21.8 [19.2, 24.5] | 525 |
| 16 | 7.0 [5.0, 9.3] | 22.1 [19.4, 24.9] | 525 |
| 32 | 6.9 [4.8, 9.1] | 22.6 [19.8, 25.3] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 32.3 [27.0, 37.3] | 35.4 [30.2, 40.4] | 10 vectors |
| compressed_m8 | 31.3 [26.3, 36.7] | 34.2 [29.1, 39.3] | 20 vectors |
| compressed_m16 | 33.0 [27.7, 38.3] | 35.9 [30.7, 41.1] | 40 vectors |
| compressed_m32 | 32.0 [26.7, 37.3] | 34.6 [29.4, 40.0] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 66.7 | 83.0 | 92.0 | 98.7 | 0.0 | 23.0 | 36.0 | 61.0 |
| query reasoner (before E2E) | 30.3 | 48.0 | 63.7 | 84.3 | 0.0 | 3.0 | 6.3 | 17.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.3] | 35.9 [30.5, 41.1] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.3] | 35.9 [30.5, 41.1] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.3] | 35.9 [30.5, 41.1] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.3 [28.3, 38.7] | 36.1 [31.0, 41.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 33.0 [28.0, 38.3] | 35.6 [30.5, 40.9] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 33.3 [28.3, 38.7] | 36.0 [30.9, 41.3] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [29.0, 39.3] | 36.5 [31.5, 41.8] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 34.7 [29.7, 40.0] | 37.1 [31.9, 42.4] |
| score@64 | [30.8, 16.0, 8.6, 8.6] | 64.0 vectors | 34.3 [29.3, 39.7] | 36.9 [31.7, 42.2] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 33.3 [28.3, 38.7] | 35.5 [30.4, 40.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 33.3 [28.3, 38.7] | 35.5 [30.4, 40.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 33.3 [28.3, 38.7] | 35.5 [30.4, 40.9] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (200) | rank 2 (49) | rank 3+ (41) | not retrieved (10) |
|---|---|---|---|---|
| uniform@16 | 36.1 | 30.9 | 32.7 | 70.0 |
| top_heavy@16 | 36.1 | 30.9 | 32.7 | 70.0 |
| score@16 | 36.1 | 30.9 | 32.7 | 70.0 |
| uniform@32 | 36.8 | 30.9 | 32.2 | 64.0 |
| top_heavy@32 | 35.8 | 34.3 | 32.2 | 53.3 |
| score@32 | 35.8 | 34.3 | 32.2 | 63.3 |
| uniform@64 | 36.2 | 33.3 | 35.4 | 63.3 |
| top_heavy@64 | 36.5 | 36.3 | 34.7 | 63.3 |
| score@64 | 36.5 | 34.3 | 35.4 | 63.3 |
| uniform@128 | 34.8 | 30.9 | 37.8 | 63.3 |
| top_heavy@128 | 34.8 | 30.9 | 37.8 | 63.3 |
| score@128 | 34.8 | 30.9 | 37.8 | 63.3 |
| raw_bm25 | 21.5 | 30.2 | 26.0 | 18.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-2.0, +1.3] | 0.718 | -0.5 [-2.3, +1.3] | 0.696 |
| score@32 vs uniform@32 | +0.0 [-1.7, +1.7] | 0.585 | -0.1 [-1.7, +1.6] | 0.571 |
| top_heavy@64 vs uniform@64 | +0.7 [-0.7, +2.0] | 0.227 | +0.6 [-0.7, +2.2] | 0.188 |
| score@64 vs uniform@64 | +0.3 [-0.7, +1.7] | 0.395 | +0.4 [-0.8, +1.8] | 0.268 |
