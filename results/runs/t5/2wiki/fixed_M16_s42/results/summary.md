# Evaluation summary

Run: `runs/t5/2wiki/fixed_M16_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 24,576
- Average passage length: 94.9 tokens; compression rate by prefix: m=4: 23.7x, m=8: 11.9x, m=16: 5.9x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 0.8 [0.2, 1.5] | 10.1 [8.4, 11.9] | 525 |
| 8 | 1.0 [0.2, 1.9] | 10.0 [8.3, 11.8] | 525 |
| 16 | 0.8 [0.0, 1.5] | 9.6 [7.8, 11.4] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 33.3 [28.0, 39.0] | 36.8 [31.6, 42.2] | 10 vectors |
| compressed_m8 | 34.7 [29.3, 40.3] | 38.2 [32.9, 43.6] | 20 vectors |
| compressed_m16 | 34.3 [29.0, 40.0] | 38.0 [32.6, 43.5] | 40 vectors |
| raw_text_gold | 31.3 [26.3, 36.3] | 37.7 [32.7, 42.7] | 393 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 54.7 | 71.3 | 79.7 | 91.3 | 0.0 | 14.3 | 24.0 | 46.0 |
| query reasoner (before E2E) | 39.0 | 56.0 | 73.0 | 86.0 | 0.0 | 8.0 | 17.7 | 38.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 36.8 [31.5, 42.1] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 36.8 [31.5, 42.1] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 36.8 [31.5, 42.1] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 34.7 [29.3, 40.3] | 38.0 [32.8, 43.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 34.7 [29.3, 40.3] | 38.2 [33.0, 43.6] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 34.7 [29.3, 40.3] | 38.3 [33.1, 43.7] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.0 [28.7, 39.7] | 37.7 [32.5, 43.1] |
| raw_bm25 | - | 495 tokens | 21.0 [16.7, 25.7] | 23.5 [19.0, 28.1] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (164) | rank 2 (50) | rank 3+ (45) | not retrieved (41) |
|---|---|---|---|---|
| uniform@16 | 33.7 | 40.4 | 40.8 | 39.8 |
| top_heavy@16 | 33.7 | 40.4 | 40.8 | 39.8 |
| score@16 | 33.7 | 40.4 | 40.8 | 39.8 |
| uniform@32 | 36.2 | 39.2 | 40.7 | 40.7 |
| top_heavy@32 | 36.5 | 39.3 | 40.7 | 40.7 |
| score@32 | 36.5 | 39.8 | 40.7 | 40.7 |
| uniform@64 | 36.8 | 39.0 | 40.7 | 36.2 |
| top_heavy@64 | 36.8 | 39.0 | 40.7 | 36.2 |
| score@64 | 36.8 | 39.0 | 40.7 | 36.2 |
| uniform@128 | 36.8 | 39.0 | 40.7 | 36.2 |
| top_heavy@128 | 36.8 | 39.0 | 40.7 | 36.2 |
| score@128 | 36.8 | 39.0 | 40.7 | 36.2 |
| raw_bm25 | 24.6 | 21.5 | 26.9 | 17.5 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.0 [-1.0, +1.0] | 0.660 | +0.2 [-0.8, +1.2] | 0.338 |
| score@32 vs uniform@32 | +0.0 [-1.0, +1.0] | 0.660 | +0.3 [-0.7, +1.3] | 0.287 |
