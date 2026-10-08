# Evaluation summary

Run: `runs/qwen/hotpotqa/fixed_M16_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 28,672
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 2.5 [1.2, 3.8] | 13.0 [11.0, 15.1] | 520 |
| 8 | 2.3 [1.2, 3.7] | 13.5 [11.5, 15.6] | 520 |
| 16 | 6.2 [4.2, 8.3] | 18.8 [16.3, 21.4] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 12.3 [8.7, 16.3] | 19.7 [16.0, 23.7] | 8 vectors |
| compressed_m8 | 12.0 [8.7, 16.0] | 19.1 [15.4, 23.1] | 16 vectors |
| compressed_m16 | 15.0 [11.0, 19.3] | 25.1 [21.0, 29.5] | 32 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 63.0 | 78.0 | 86.3 | 96.3 | 0.0 | 22.7 | 36.3 | 62.0 |
| query reasoner (before E2E) | 47.7 | 62.0 | 72.7 | 88.0 | 0.0 | 10.3 | 20.3 | 40.0 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.8 [16.1, 24.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.8 [16.1, 24.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.8 [16.1, 24.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 11.0 [7.7, 14.7] | 17.9 [14.2, 21.8] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 14.0 [10.3, 18.0] | 21.5 [17.5, 25.7] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 14.0 [10.3, 18.0] | 21.4 [17.5, 25.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| top_heavy@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| score@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| uniform@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| top_heavy@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| score@128 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 15.0 [11.3, 19.3] | 21.4 [17.3, 25.9] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (189) | rank 2 (45) | rank 3+ (45) | not retrieved (21) |
|---|---|---|---|---|
| uniform@16 | 20.7 | 16.6 | 20.9 | 17.3 |
| top_heavy@16 | 20.7 | 16.6 | 20.9 | 17.3 |
| score@16 | 20.7 | 16.6 | 20.9 | 17.3 |
| uniform@32 | 17.8 | 18.3 | 19.4 | 14.2 |
| top_heavy@32 | 22.7 | 23.3 | 19.0 | 12.1 |
| score@32 | 22.7 | 22.5 | 19.0 | 12.3 |
| uniform@64 | 21.9 | 26.4 | 20.7 | 7.9 |
| top_heavy@64 | 21.9 | 26.4 | 20.7 | 7.9 |
| score@64 | 21.9 | 26.4 | 20.7 | 7.9 |
| uniform@128 | 21.9 | 26.4 | 20.7 | 7.9 |
| top_heavy@128 | 21.9 | 26.4 | 20.7 | 7.9 |
| score@128 | 21.9 | 26.4 | 20.7 | 7.9 |
| raw_bm25 | 22.0 | 31.1 | 14.4 | 14.8 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| top_heavy@32 vs uniform@32 | +3.0 [+1.0, +5.0] | 0.001 | +3.6 [+1.6, +5.9] | 0.001 |
| score@32 vs uniform@32 | +3.0 [+1.0, +5.0] | 0.001 | +3.5 [+1.5, +5.8] | 0.001 |
