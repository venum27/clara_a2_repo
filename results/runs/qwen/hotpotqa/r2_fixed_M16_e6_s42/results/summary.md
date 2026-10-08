# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_fixed_M16_e6_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 28,672
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 6.0 [4.0, 8.1] | 18.5 [15.9, 21.0] | 520 |
| 8 | 6.3 [4.4, 8.5] | 19.6 [17.0, 22.1] | 520 |
| 16 | 6.9 [4.8, 9.2] | 21.8 [19.2, 24.4] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 13.7 [10.0, 17.7] | 22.0 [18.1, 26.1] | 8 vectors |
| compressed_m8 | 13.3 [9.7, 17.3] | 22.1 [18.0, 26.2] | 16 vectors |
| compressed_m16 | 12.3 [8.7, 16.0] | 23.3 [19.3, 27.4] | 32 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 52.7 | 71.3 | 81.7 | 94.3 | 0.0 | 15.0 | 28.0 | 51.3 |
| query reasoner (before E2E) | 37.3 | 57.0 | 70.7 | 84.0 | 0.0 | 7.3 | 16.7 | 34.3 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 20.6 [16.9, 24.8] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 20.6 [16.9, 24.8] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 20.6 [16.9, 24.8] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 14.0 [10.3, 18.0] | 22.3 [18.4, 26.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.7 [10.0, 18.0] | 21.7 [17.7, 25.7] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 13.3 [9.7, 17.3] | 21.6 [17.7, 25.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (158) | rank 2 (56) | rank 3+ (57) | not retrieved (29) |
|---|---|---|---|---|
| uniform@16 | 22.4 | 18.1 | 14.7 | 27.4 |
| top_heavy@16 | 22.4 | 18.1 | 14.7 | 27.4 |
| score@16 | 22.4 | 18.1 | 14.7 | 27.4 |
| uniform@32 | 24.2 | 19.3 | 18.3 | 25.2 |
| top_heavy@32 | 23.0 | 20.6 | 17.2 | 25.2 |
| score@32 | 22.4 | 20.6 | 18.4 | 25.2 |
| uniform@64 | 25.4 | 20.4 | 11.7 | 26.2 |
| top_heavy@64 | 25.4 | 20.4 | 11.7 | 26.2 |
| score@64 | 25.4 | 20.4 | 11.7 | 26.2 |
| uniform@128 | 25.4 | 20.4 | 11.7 | 26.2 |
| top_heavy@128 | 25.4 | 20.4 | 11.7 | 26.2 |
| score@128 | 25.4 | 20.4 | 11.7 | 26.2 |
| raw_bm25 | 23.9 | 23.9 | 17.2 | 14.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | -0.3 [-1.7, +1.0] | 0.749 | -0.6 [-2.4, +1.2] | 0.738 |
| score@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.907 | -0.7 [-2.3, +0.9] | 0.793 |
