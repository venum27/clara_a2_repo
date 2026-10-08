# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6_s42`

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
| compressed_m4 | 12.3 [8.7, 16.3] | 21.6 [17.7, 25.7] | 8 vectors |
| compressed_m8 | 12.7 [9.3, 16.7] | 22.0 [18.1, 26.1] | 16 vectors |
| compressed_m16 | 13.3 [9.7, 17.3] | 22.6 [18.7, 26.8] | 32 vectors |
| compressed_m32 | 12.7 [9.0, 16.3] | 22.6 [18.6, 26.6] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 57.0 | 74.0 | 84.3 | 95.0 | 0.0 | 20.3 | 36.3 | 63.7 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.3 [8.7, 16.3] | 20.3 [16.3, 24.3] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.3 [8.7, 16.3] | 20.3 [16.3, 24.3] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.3 [8.7, 16.3] | 20.3 [16.3, 24.3] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 12.0 [8.3, 15.7] | 19.2 [15.4, 22.9] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.7 [8.3, 15.3] | 18.5 [14.8, 22.3] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 11.7 [8.3, 15.3] | 18.5 [14.8, 22.3] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.0 [7.7, 14.7] | 18.8 [15.1, 22.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 11.3 [8.0, 15.0] | 19.7 [15.9, 23.6] |
| score@64 | [30.9, 16.0, 8.5, 8.5] | 64.0 vectors | 11.0 [7.7, 14.7] | 19.5 [15.7, 23.4] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.7 [9.3, 16.7] | 21.1 [17.1, 25.3] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.7 [9.3, 16.7] | 21.1 [17.1, 25.3] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.7 [9.3, 16.7] | 21.1 [17.1, 25.3] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (171) | rank 2 (51) | rank 3+ (50) | not retrieved (28) |
|---|---|---|---|---|
| uniform@16 | 23.2 | 21.9 | 16.0 | 7.0 |
| top_heavy@16 | 23.2 | 21.9 | 16.0 | 7.0 |
| score@16 | 23.2 | 21.9 | 16.0 | 7.0 |
| uniform@32 | 22.8 | 20.9 | 10.9 | 8.9 |
| top_heavy@32 | 21.4 | 20.6 | 11.8 | 8.9 |
| score@32 | 21.4 | 20.6 | 11.8 | 8.9 |
| uniform@64 | 23.0 | 18.5 | 12.1 | 5.2 |
| top_heavy@64 | 23.5 | 20.3 | 13.7 | 6.1 |
| score@64 | 23.5 | 20.3 | 13.2 | 5.2 |
| uniform@128 | 23.9 | 23.1 | 17.5 | 7.0 |
| top_heavy@128 | 23.9 | 23.1 | 17.5 | 7.0 |
| score@128 | 23.9 | 23.1 | 17.5 | 7.0 |
| raw_bm25 | 24.6 | 18.3 | 16.7 | 18.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-1.0, +0.0] | 1.000 | -0.7 [-2.0, +0.6] | 0.821 |
| score@32 vs uniform@32 | -0.3 [-1.0, +0.0] | 1.000 | -0.7 [-2.0, +0.6] | 0.821 |
| top_heavy@64 vs uniform@64 | +0.3 [-0.7, +1.7] | 0.380 | +1.0 [-0.0, +2.1] | 0.032 |
| score@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.641 | +0.8 [-0.2, +1.9] | 0.065 |
