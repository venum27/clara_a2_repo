# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_S1_s44`

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
| compressed_m4 | 14.0 [10.3, 18.0] | 23.2 [19.2, 27.6] | 8 vectors |
| compressed_m8 | 15.7 [11.7, 20.0] | 25.2 [21.0, 29.6] | 16 vectors |
| compressed_m16 | 14.0 [10.3, 18.0] | 22.7 [18.8, 26.9] | 32 vectors |
| compressed_m32 | 14.7 [11.0, 18.7] | 23.2 [19.3, 27.4] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 56.3 | 75.0 | 85.7 | 95.3 | 0.0 | 17.3 | 34.3 | 62.3 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 14.0 [10.3, 18.0] | 21.1 [17.3, 25.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 14.0 [10.3, 18.0] | 21.1 [17.3, 25.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 14.0 [10.3, 18.0] | 21.1 [17.3, 25.2] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 14.0 [10.3, 18.0] | 21.1 [17.3, 25.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 15.3 [11.3, 19.3] | 22.5 [18.4, 26.8] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 14.7 [10.7, 18.7] | 21.4 [17.4, 25.7] |
| score@32 | [15.5, 8.0, 4.2, 4.2] | 32.0 vectors | 14.7 [10.7, 18.7] | 21.3 [17.3, 25.6] |
| learned@32 | [7.6, 8.1, 8.3, 8.1] | 32.0 vectors | 15.7 [11.7, 20.0] | 22.2 [18.1, 26.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.7 [10.0, 17.7] | 20.7 [16.8, 24.8] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 14.3 [10.7, 18.7] | 21.4 [17.5, 25.7] |
| score@64 | [31.0, 16.0, 8.5, 8.5] | 64.0 vectors | 14.3 [10.7, 18.7] | 21.4 [17.5, 25.7] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.7 [10.0, 17.7] | 20.7 [16.8, 24.8] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 15.0 [11.3, 19.0] | 22.6 [18.6, 26.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 15.0 [11.3, 19.0] | 22.6 [18.6, 26.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 15.0 [11.3, 19.0] | 22.6 [18.6, 26.9] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 15.0 [11.3, 19.0] | 22.6 [18.6, 26.9] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [7.6, 8.1, 8.3, 8.1] | 8.2 | 7.9 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (169) | rank 2 (56) | rank 3+ (52) | not retrieved (23) |
|---|---|---|---|---|
| uniform@16 | 23.8 | 19.7 | 12.4 | 24.7 |
| top_heavy@16 | 23.8 | 19.7 | 12.4 | 24.7 |
| score@16 | 23.8 | 19.7 | 12.4 | 24.7 |
| learned@16 | 23.8 | 19.7 | 12.4 | 24.7 |
| uniform@32 | 24.4 | 23.3 | 12.6 | 28.5 |
| top_heavy@32 | 24.3 | 20.4 | 12.2 | 23.3 |
| score@32 | 24.5 | 20.4 | 10.7 | 23.3 |
| learned@32 | 24.7 | 23.7 | 11.7 | 23.7 |
| uniform@64 | 23.0 | 19.5 | 13.8 | 22.3 |
| top_heavy@64 | 25.2 | 17.7 | 12.7 | 22.3 |
| score@64 | 25.2 | 17.7 | 12.7 | 22.3 |
| learned@64 | 23.0 | 19.5 | 13.8 | 22.3 |
| uniform@128 | 22.8 | 23.6 | 18.7 | 27.2 |
| top_heavy@128 | 22.8 | 23.6 | 18.7 | 27.2 |
| score@128 | 22.8 | 23.6 | 18.7 | 27.2 |
| learned@128 | 22.8 | 23.6 | 18.7 | 27.2 |
| raw_bm25 | 23.5 | 19.2 | 18.2 | 22.9 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-1.7, +0.0] | 1.000 | -1.1 [-2.4, +0.1] | 0.965 |
| score@32 vs uniform@32 | -0.7 [-1.7, +0.0] | 1.000 | -1.2 [-2.5, -0.1] | 0.990 |
| learned@32 vs uniform@32 | +0.3 [-1.0, +1.7] | 0.403 | -0.3 [-1.8, +1.2] | 0.671 |
| learned@32 vs top_heavy@32 | +1.0 [-0.3, +2.7] | 0.113 | +0.8 [-0.6, +2.3] | 0.146 |
| top_heavy@64 vs uniform@64 | +0.7 [-1.0, +2.7] | 0.282 | +0.7 [-1.1, +2.6] | 0.205 |
| score@64 vs uniform@64 | +0.7 [-1.0, +2.7] | 0.282 | +0.7 [-1.1, +2.6] | 0.205 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | -0.7 [-2.7, +1.0] | 0.830 | -0.7 [-2.6, +1.1] | 0.795 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
