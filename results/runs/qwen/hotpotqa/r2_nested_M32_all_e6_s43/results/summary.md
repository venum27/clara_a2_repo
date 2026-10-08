# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6_s43`

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
| compressed_m4 | 11.7 [8.3, 15.7] | 20.3 [16.4, 24.4] | 8 vectors |
| compressed_m8 | 14.0 [10.3, 18.0] | 23.0 [19.1, 27.3] | 16 vectors |
| compressed_m16 | 13.3 [9.7, 17.7] | 22.1 [18.1, 26.4] | 32 vectors |
| compressed_m32 | 13.7 [10.0, 17.7] | 22.3 [18.2, 26.4] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 60.7 | 77.0 | 85.7 | 94.0 | 0.0 | 17.7 | 32.3 | 59.0 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.7 [16.9, 25.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.7 [16.9, 25.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.7 [16.9, 25.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.3 [9.7, 17.3] | 20.4 [16.5, 24.6] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 11.7 [8.3, 15.7] | 18.5 [14.8, 22.5] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 11.7 [8.3, 15.7] | 18.6 [14.9, 22.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 12.7 [9.3, 16.7] | 19.6 [15.7, 23.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 12.3 [9.0, 16.3] | 19.1 [15.3, 23.1] |
| score@64 | [30.9, 16.0, 8.5, 8.5] | 64.0 vectors | 12.3 [9.0, 16.3] | 19.1 [15.3, 23.1] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [9.0, 16.3] | 20.8 [16.7, 24.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [9.0, 16.3] | 20.8 [16.7, 24.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [9.0, 16.3] | 20.8 [16.7, 24.9] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (182) | rank 2 (49) | rank 3+ (41) | not retrieved (28) |
|---|---|---|---|---|
| uniform@16 | 21.0 | 27.0 | 19.8 | 9.1 |
| top_heavy@16 | 21.0 | 27.0 | 19.8 | 9.1 |
| score@16 | 21.0 | 27.0 | 19.8 | 9.1 |
| uniform@32 | 20.9 | 25.8 | 18.7 | 10.0 |
| top_heavy@32 | 18.1 | 23.9 | 18.9 | 11.3 |
| score@32 | 18.1 | 23.9 | 19.6 | 11.3 |
| uniform@64 | 18.7 | 30.4 | 20.1 | 5.4 |
| top_heavy@64 | 19.4 | 26.9 | 17.7 | 5.4 |
| score@64 | 19.4 | 26.9 | 17.7 | 5.4 |
| uniform@128 | 21.2 | 26.2 | 17.6 | 13.0 |
| top_heavy@128 | 21.2 | 26.2 | 17.6 | 13.0 |
| score@128 | 21.2 | 26.2 | 17.6 | 13.0 |
| raw_bm25 | 22.7 | 20.9 | 18.8 | 21.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -1.7 [-3.7, +0.0] | 0.987 | -1.9 [-3.9, -0.1] | 0.979 |
| score@32 vs uniform@32 | -1.7 [-3.7, +0.0] | 0.987 | -1.8 [-3.8, +0.0] | 0.971 |
| top_heavy@64 vs uniform@64 | -0.3 [-1.7, +1.0] | 0.760 | -0.5 [-2.0, +1.0] | 0.737 |
| score@64 vs uniform@64 | -0.3 [-1.7, +1.0] | 0.760 | -0.5 [-2.0, +1.0] | 0.737 |
