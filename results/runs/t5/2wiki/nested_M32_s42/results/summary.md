# Evaluation summary

Run: `runs/t5/2wiki/nested_M32_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 49,152
- Average passage length: 94.9 tokens; compression rate by prefix: m=4: 23.7x, m=8: 11.9x, m=16: 5.9x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 1.0 [0.2, 1.9] | 9.5 [7.8, 11.2] | 525 |
| 8 | 0.8 [0.2, 1.5] | 9.7 [8.0, 11.5] | 525 |
| 16 | 0.8 [0.2, 1.5] | 9.1 [7.4, 10.7] | 525 |
| 32 | 0.6 [0.0, 1.3] | 9.1 [7.5, 10.8] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 34.7 [29.0, 40.0] | 38.9 [33.3, 44.2] | 10 vectors |
| compressed_m8 | 35.3 [29.7, 41.0] | 39.4 [33.9, 44.8] | 20 vectors |
| compressed_m16 | 35.0 [29.7, 40.7] | 38.9 [33.5, 44.5] | 40 vectors |
| compressed_m32 | 35.0 [29.7, 40.7] | 38.9 [33.4, 44.3] | 80 vectors |
| raw_text_gold | 31.3 [26.3, 36.3] | 37.7 [32.7, 42.7] | 393 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 55.3 | 73.3 | 84.3 | 93.0 | 0.0 | 18.3 | 28.0 | 54.0 |
| query reasoner (before E2E) | 42.7 | 58.0 | 72.3 | 90.0 | 0.0 | 11.7 | 20.7 | 39.3 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.8 [32.6, 43.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.8 [32.6, 43.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.8 [32.6, 43.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 34.0 [28.7, 39.3] | 38.0 [32.7, 43.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 33.7 [28.3, 39.3] | 37.6 [32.4, 43.0] |
| score@32 | [15.2, 8.0, 4.4, 4.4] | 32.0 vectors | 34.3 [29.0, 40.0] | 38.2 [32.9, 43.7] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.7 [29.3, 40.3] | 38.2 [32.8, 43.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 35.0 [29.7, 40.7] | 38.9 [33.7, 44.3] |
| score@64 | [30.3, 16.0, 8.8, 8.8] | 64.0 vectors | 34.7 [29.3, 40.3] | 38.6 [33.3, 44.0] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.3 [30.0, 41.0] | 38.7 [33.4, 44.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.3 [30.0, 41.0] | 38.7 [33.4, 44.2] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.3 [30.0, 41.0] | 38.7 [33.4, 44.2] |
| raw_bm25 | - | 495 tokens | 21.0 [16.7, 25.7] | 23.5 [19.0, 28.1] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (166) | rank 2 (54) | rank 3+ (49) | not retrieved (31) |
|---|---|---|---|---|
| uniform@16 | 35.4 | 32.0 | 52.2 | 37.6 |
| top_heavy@16 | 35.4 | 32.0 | 52.2 | 37.6 |
| score@16 | 35.4 | 32.0 | 52.2 | 37.6 |
| uniform@32 | 35.3 | 32.0 | 52.2 | 40.8 |
| top_heavy@32 | 36.3 | 31.9 | 48.9 | 36.6 |
| score@32 | 36.9 | 31.9 | 50.9 | 36.6 |
| uniform@64 | 36.5 | 33.7 | 49.1 | 37.7 |
| top_heavy@64 | 37.1 | 33.7 | 52.2 | 36.6 |
| score@64 | 37.1 | 33.7 | 50.1 | 36.6 |
| uniform@128 | 37.9 | 35.6 | 45.7 | 37.7 |
| top_heavy@128 | 37.9 | 35.6 | 45.7 | 37.7 |
| score@128 | 37.9 | 35.6 | 45.7 | 37.7 |
| raw_bm25 | 22.3 | 23.7 | 31.0 | 17.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-1.7, +1.0] | 0.758 | -0.4 [-2.0, +1.2] | 0.696 |
| score@32 vs uniform@32 | +0.3 [-0.7, +1.7] | 0.392 | +0.2 [-1.0, +1.6] | 0.369 |
| top_heavy@64 vs uniform@64 | +0.3 [-0.7, +1.7] | 0.411 | +0.7 [-0.1, +1.9] | 0.067 |
| score@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.661 | +0.4 [-0.2, +1.3] | 0.162 |
