# Evaluation summary

Run: `runs/qwen/hotpotqa/nested_M32_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x, m=32: 4.1x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 4.0 [2.5, 5.8] | 16.5 [14.2, 18.9] | 520 |
| 8 | 3.5 [2.1, 5.0] | 15.8 [13.4, 18.0] | 520 |
| 16 | 3.8 [2.3, 5.6] | 16.4 [14.0, 18.7] | 520 |
| 32 | 3.8 [2.3, 5.6] | 16.2 [13.8, 18.3] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 13.0 [9.3, 17.0] | 22.7 [18.8, 26.9] | 8 vectors |
| compressed_m8 | 11.7 [8.3, 15.3] | 21.8 [17.9, 25.8] | 16 vectors |
| compressed_m16 | 11.7 [8.3, 15.7] | 21.9 [18.0, 25.9] | 32 vectors |
| compressed_m32 | 12.3 [8.7, 16.3] | 22.0 [18.1, 25.9] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 58.3 | 79.7 | 89.3 | 96.7 | 0.0 | 21.3 | 34.7 | 61.7 |
| query reasoner (before E2E) | 44.7 | 63.3 | 76.7 | 90.3 | 0.0 | 13.3 | 22.3 | 44.0 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 19.1 [15.4, 23.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 19.1 [15.4, 23.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 19.1 [15.4, 23.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 12.7 [9.3, 16.7] | 21.1 [17.2, 25.2] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 12.7 [9.0, 16.3] | 21.0 [17.2, 25.1] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 12.7 [9.0, 16.3] | 21.0 [17.2, 25.1] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 11.3 [8.0, 15.0] | 19.8 [16.1, 23.8] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 11.7 [8.3, 15.3] | 20.4 [16.6, 24.3] |
| score@64 | [31.0, 16.0, 8.5, 8.5] | 64.0 vectors | 11.7 [8.3, 15.3] | 20.5 [16.7, 24.4] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.0 [8.3, 16.0] | 20.9 [17.0, 24.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.0 [8.3, 16.0] | 20.9 [17.0, 24.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.0 [8.3, 16.0] | 20.9 [17.0, 24.9] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (175) | rank 2 (64) | rank 3+ (41) | not retrieved (20) |
|---|---|---|---|---|
| uniform@16 | 21.8 | 18.0 | 11.3 | 15.5 |
| top_heavy@16 | 21.8 | 18.0 | 11.3 | 15.5 |
| score@16 | 21.8 | 18.0 | 11.3 | 15.5 |
| uniform@32 | 24.8 | 19.8 | 11.9 | 11.1 |
| top_heavy@32 | 24.5 | 19.4 | 11.1 | 15.5 |
| score@32 | 24.5 | 19.4 | 11.1 | 15.5 |
| uniform@64 | 22.6 | 17.6 | 15.4 | 11.1 |
| top_heavy@64 | 23.0 | 19.2 | 15.4 | 11.1 |
| score@64 | 23.0 | 19.2 | 16.2 | 11.1 |
| uniform@128 | 23.4 | 19.7 | 15.4 | 14.4 |
| top_heavy@128 | 23.4 | 19.7 | 15.4 | 14.4 |
| score@128 | 23.4 | 19.7 | 15.4 | 14.4 |
| raw_bm25 | 20.7 | 28.7 | 13.9 | 24.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +0.0 [-1.3, +1.3] | 0.608 | -0.1 [-1.7, +1.6] | 0.550 |
| score@32 vs uniform@32 | +0.0 [-1.3, +1.3] | 0.608 | -0.1 [-1.7, +1.6] | 0.550 |
| top_heavy@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.419 | +0.6 [-0.8, +2.0] | 0.216 |
| score@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.419 | +0.7 [-0.6, +2.1] | 0.169 |
