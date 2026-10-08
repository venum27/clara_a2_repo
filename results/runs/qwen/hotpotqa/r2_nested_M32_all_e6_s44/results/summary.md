# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x, m=32: 4.1x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 6.2 [4.2, 8.3] | 19.4 [16.9, 21.9] | 520 |
| 8 | 6.7 [4.6, 9.0] | 19.6 [17.0, 22.2] | 520 |
| 16 | 6.9 [4.6, 9.0] | 19.3 [16.7, 21.9] | 520 |
| 32 | 5.6 [3.7, 7.7] | 18.9 [16.3, 21.3] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 13.3 [9.7, 17.3] | 23.8 [19.8, 28.1] | 8 vectors |
| compressed_m8 | 14.0 [10.3, 18.0] | 23.1 [19.1, 27.4] | 16 vectors |
| compressed_m16 | 14.0 [10.3, 18.3] | 23.3 [19.2, 27.5] | 32 vectors |
| compressed_m32 | 14.0 [10.3, 18.0] | 24.1 [19.8, 28.3] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 55.7 | 75.0 | 83.3 | 93.3 | 0.0 | 16.3 | 30.0 | 59.0 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.3, 16.7] | 20.6 [16.7, 24.6] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.3, 16.7] | 20.6 [16.7, 24.6] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.3, 16.7] | 20.6 [16.7, 24.6] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.0 [9.7, 17.0] | 20.6 [16.8, 24.8] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.7 [10.0, 17.7] | 21.0 [17.2, 25.1] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 13.7 [10.0, 17.7] | 20.9 [17.0, 25.0] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 20.8 [17.2, 24.9] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 12.3 [8.7, 16.0] | 20.9 [17.1, 24.8] |
| score@64 | [30.9, 16.0, 8.5, 8.5] | 64.0 vectors | 12.3 [8.7, 16.0] | 20.9 [17.1, 24.8] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.3 [9.7, 17.3] | 20.8 [17.1, 25.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.3 [9.7, 17.3] | 20.8 [17.1, 25.1] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.3 [9.7, 17.3] | 20.8 [17.1, 25.1] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (167) | rank 2 (58) | rank 3+ (47) | not retrieved (28) |
|---|---|---|---|---|
| uniform@16 | 22.2 | 22.1 | 17.2 | 13.4 |
| top_heavy@16 | 22.2 | 22.1 | 17.2 | 13.4 |
| score@16 | 22.2 | 22.1 | 17.2 | 13.4 |
| uniform@32 | 21.2 | 21.8 | 19.7 | 15.7 |
| top_heavy@32 | 22.7 | 23.2 | 17.4 | 12.5 |
| score@32 | 22.7 | 22.5 | 17.4 | 12.5 |
| uniform@64 | 22.1 | 21.3 | 20.5 | 12.7 |
| top_heavy@64 | 22.6 | 22.0 | 18.8 | 11.5 |
| score@64 | 22.6 | 22.0 | 18.8 | 11.5 |
| uniform@128 | 20.4 | 20.8 | 21.1 | 23.0 |
| top_heavy@128 | 20.4 | 20.8 | 21.1 | 23.0 |
| score@128 | 20.4 | 20.8 | 21.1 | 23.0 |
| raw_bm25 | 24.6 | 15.7 | 19.9 | 19.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.234 | +0.5 [-0.9, +1.9] | 0.254 |
| score@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.234 | +0.3 [-1.0, +1.7] | 0.320 |
| top_heavy@64 vs uniform@64 | -0.7 [-1.7, +0.0] | 1.000 | +0.0 [-1.3, +1.2] | 0.496 |
| score@64 vs uniform@64 | -0.7 [-1.7, +0.0] | 1.000 | +0.0 [-1.3, +1.2] | 0.496 |
