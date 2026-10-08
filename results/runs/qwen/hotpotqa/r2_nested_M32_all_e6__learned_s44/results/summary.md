# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s44`

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
| compressed_m4 | 11.7 [8.3, 15.3] | 21.2 [17.3, 25.3] | 8 vectors |
| compressed_m8 | 14.7 [11.0, 18.7] | 23.2 [19.1, 27.5] | 16 vectors |
| compressed_m16 | 14.0 [10.3, 18.3] | 23.0 [18.8, 27.2] | 32 vectors |
| compressed_m32 | 14.3 [10.7, 18.3] | 22.6 [18.6, 26.8] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 59.3 | 74.0 | 83.3 | 95.3 | 0.0 | 19.0 | 34.0 | 58.7 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.1 [16.3, 24.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.1 [16.3, 24.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.1 [16.3, 24.2] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.0 [9.7, 17.0] | 20.1 [16.3, 24.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 14.0 [10.3, 18.0] | 20.2 [16.4, 24.3] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.3 [9.7, 17.3] | 19.5 [15.8, 23.8] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 13.3 [9.7, 17.3] | 19.4 [15.7, 23.7] |
| learned@32 | [7.4, 6.6, 12.4, 5.6] | 32.0 vectors | 13.7 [10.0, 17.7] | 20.1 [16.3, 24.4] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 12.3 [8.7, 16.3] | 19.5 [15.8, 23.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 19.7 [15.9, 24.1] |
| score@64 | [31.0, 16.0, 8.5, 8.5] | 64.0 vectors | 13.0 [9.3, 17.0] | 19.7 [15.9, 24.1] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 12.3 [8.7, 16.3] | 19.5 [15.8, 23.6] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 14.3 [10.7, 18.3] | 21.8 [18.0, 26.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 14.3 [10.7, 18.3] | 21.8 [18.0, 26.1] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 14.3 [10.7, 18.3] | 21.8 [18.0, 26.1] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 14.3 [10.7, 18.3] | 21.8 [18.0, 26.1] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [7.4, 6.6, 12.4, 5.6] | 7.9 | 8.1 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (178) | rank 2 (44) | rank 3+ (48) | not retrieved (30) |
|---|---|---|---|---|
| uniform@16 | 22.1 | 19.7 | 14.6 | 17.9 |
| top_heavy@16 | 22.1 | 19.7 | 14.6 | 17.9 |
| score@16 | 22.1 | 19.7 | 14.6 | 17.9 |
| learned@16 | 22.1 | 19.7 | 14.6 | 17.9 |
| uniform@32 | 21.1 | 20.2 | 16.5 | 20.3 |
| top_heavy@32 | 20.8 | 19.9 | 16.4 | 16.2 |
| score@32 | 20.6 | 19.9 | 16.4 | 16.2 |
| learned@32 | 21.6 | 19.3 | 17.7 | 16.2 |
| uniform@64 | 21.6 | 19.2 | 15.0 | 15.0 |
| top_heavy@64 | 22.0 | 17.7 | 15.0 | 16.5 |
| score@64 | 22.0 | 17.7 | 15.0 | 16.5 |
| learned@64 | 21.6 | 19.2 | 15.0 | 15.0 |
| uniform@128 | 22.1 | 22.0 | 20.5 | 22.2 |
| top_heavy@128 | 22.1 | 22.0 | 20.5 | 22.2 |
| score@128 | 22.1 | 22.0 | 20.5 | 22.2 |
| learned@128 | 22.1 | 22.0 | 20.5 | 22.2 |
| raw_bm25 | 24.0 | 14.0 | 22.9 | 17.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.908 | -0.6 [-2.1, +0.6] | 0.823 |
| score@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.908 | -0.7 [-2.2, +0.5] | 0.866 |
| learned@32 vs uniform@32 | -0.3 [-1.7, +0.7] | 0.827 | -0.0 [-1.1, +0.8] | 0.500 |
| learned@32 vs top_heavy@32 | +0.3 [-1.0, +1.7] | 0.398 | +0.6 [-0.7, +2.0] | 0.177 |
| top_heavy@64 vs uniform@64 | +0.7 [+0.0, +1.7] | 0.131 | +0.2 [-1.1, +1.4] | 0.367 |
| score@64 vs uniform@64 | +0.7 [+0.0, +1.7] | 0.131 | +0.2 [-1.1, +1.4] | 0.363 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | -0.7 [-1.7, +0.0] | 1.000 | -0.2 [-1.4, +1.1] | 0.633 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
