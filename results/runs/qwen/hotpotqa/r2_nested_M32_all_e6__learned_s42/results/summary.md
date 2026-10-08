# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s42`

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
| compressed_m4 | 12.3 [8.7, 16.3] | 20.8 [16.8, 25.0] | 8 vectors |
| compressed_m8 | 13.0 [9.3, 17.0] | 22.5 [18.5, 26.6] | 16 vectors |
| compressed_m16 | 14.3 [10.7, 18.7] | 23.6 [19.5, 27.7] | 32 vectors |
| compressed_m32 | 12.3 [9.0, 16.3] | 22.4 [18.5, 26.4] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 57.3 | 76.0 | 84.7 | 95.3 | 0.0 | 20.3 | 36.3 | 63.7 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 21.7 [17.9, 25.9] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 21.7 [17.9, 25.9] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 21.7 [17.9, 25.9] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 21.7 [17.9, 25.9] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.7 [10.0, 17.7] | 23.0 [19.0, 27.2] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 14.3 [10.7, 18.3] | 23.0 [19.0, 27.2] |
| score@32 | [15.7, 8.0, 4.2, 4.2] | 32.0 vectors | 14.3 [10.7, 18.3] | 23.0 [19.0, 27.2] |
| learned@32 | [6.7, 5.1, 15.5, 4.8] | 32.0 vectors | 13.3 [9.7, 17.3] | 22.7 [18.6, 26.9] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 12.3 [9.0, 16.3] | 21.4 [17.7, 25.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 13.3 [9.7, 17.3] | 21.7 [17.9, 26.0] |
| score@64 | [31.3, 16.0, 8.3, 8.3] | 64.0 vectors | 13.3 [9.7, 17.3] | 21.6 [17.8, 25.9] |
| learned@64 | [15.3, 15.5, 17.4, 15.8] | 64.0 vectors | 12.7 [9.3, 16.7] | 21.5 [17.7, 25.7] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.7 [8.3, 15.7] | 20.4 [16.6, 24.4] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.7 [8.3, 15.7] | 20.4 [16.6, 24.4] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.7 [8.3, 15.7] | 20.4 [16.6, 24.4] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 11.7 [8.3, 15.7] | 20.4 [16.6, 24.4] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [6.7, 5.1, 15.5, 4.8] | 7.6 | 8.2 |
| 64 | [15.3, 15.5, 17.4, 15.8] | 15.6 | 16.2 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (172) | rank 2 (56) | rank 3+ (46) | not retrieved (26) |
|---|---|---|---|---|
| uniform@16 | 25.3 | 22.1 | 13.0 | 12.6 |
| top_heavy@16 | 25.3 | 22.1 | 13.0 | 12.6 |
| score@16 | 25.3 | 22.1 | 13.0 | 12.6 |
| learned@16 | 25.3 | 22.1 | 13.0 | 12.6 |
| uniform@32 | 26.7 | 21.3 | 13.2 | 19.1 |
| top_heavy@32 | 26.4 | 23.1 | 15.3 | 14.1 |
| score@32 | 26.4 | 23.1 | 15.3 | 14.1 |
| learned@32 | 27.1 | 20.6 | 12.9 | 15.2 |
| uniform@64 | 26.6 | 17.9 | 11.7 | 11.7 |
| top_heavy@64 | 27.1 | 18.1 | 11.2 | 13.1 |
| score@64 | 27.1 | 17.5 | 11.2 | 13.1 |
| learned@64 | 26.9 | 17.9 | 11.7 | 11.0 |
| uniform@128 | 23.9 | 17.1 | 14.5 | 14.6 |
| top_heavy@128 | 23.9 | 17.1 | 14.5 | 14.6 |
| score@128 | 23.9 | 17.1 | 14.5 | 14.6 |
| learned@128 | 23.9 | 17.1 | 14.5 | 14.6 |
| raw_bm25 | 22.7 | 21.6 | 23.9 | 11.7 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.227 | +0.1 [-1.3, +1.5] | 0.466 |
| score@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.227 | +0.1 [-1.3, +1.5] | 0.466 |
| learned@32 vs uniform@32 | -0.3 [-1.0, +0.0] | 1.000 | -0.3 [-1.3, +0.6] | 0.732 |
| learned@32 vs top_heavy@32 | -1.0 [-2.3, +0.0] | 1.000 | -0.4 [-1.7, +1.0] | 0.683 |
| top_heavy@64 vs uniform@64 | +1.0 [+0.0, +2.3] | 0.048 | +0.3 [-1.0, +1.7] | 0.347 |
| score@64 vs uniform@64 | +1.0 [+0.0, +2.3] | 0.048 | +0.2 [-1.1, +1.6] | 0.404 |
| learned@64 vs uniform@64 | +0.3 [+0.0, +1.0] | 0.357 | +0.1 [-0.4, +0.6] | 0.404 |
| learned@64 vs top_heavy@64 | -0.7 [-1.7, +0.0] | 1.000 | -0.2 [-1.7, +1.1] | 0.603 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
