# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_S1_s43`

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
| compressed_m4 | 14.3 [10.7, 18.7] | 23.0 [18.9, 27.3] | 8 vectors |
| compressed_m8 | 14.3 [10.7, 18.7] | 23.1 [19.1, 27.5] | 16 vectors |
| compressed_m16 | 15.3 [11.7, 19.7] | 23.9 [19.8, 28.5] | 32 vectors |
| compressed_m32 | 13.3 [9.7, 17.7] | 21.9 [17.9, 26.2] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 61.7 | 79.0 | 86.7 | 96.3 | 0.0 | 22.0 | 38.0 | 61.3 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 20.8 [16.8, 25.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 20.8 [16.8, 25.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 20.8 [16.8, 25.0] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 13.3 [9.7, 17.3] | 20.8 [16.8, 25.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 14.0 [10.3, 18.0] | 20.9 [17.0, 24.9] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.3 [10.0, 17.3] | 20.3 [16.4, 24.4] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 13.3 [10.0, 17.3] | 20.3 [16.4, 24.4] |
| learned@32 | [7.2, 8.1, 8.2, 8.5] | 32.0 vectors | 12.7 [9.3, 16.7] | 19.3 [15.5, 23.4] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.7 [10.0, 17.7] | 20.6 [16.6, 24.9] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 13.7 [10.0, 18.0] | 21.0 [17.1, 25.3] |
| score@64 | [31.0, 16.0, 8.5, 8.5] | 64.0 vectors | 13.7 [10.0, 18.0] | 20.8 [16.7, 25.1] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.7 [10.0, 17.7] | 20.6 [16.6, 24.9] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.7 [10.0, 17.7] | 21.6 [17.6, 25.8] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.7 [10.0, 17.7] | 21.6 [17.6, 25.8] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.7 [10.0, 17.7] | 21.6 [17.6, 25.8] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.7 [10.0, 17.7] | 21.6 [17.6, 25.8] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [7.2, 8.1, 8.2, 8.5] | 7.5 | 8.3 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (185) | rank 2 (52) | rank 3+ (43) | not retrieved (20) |
|---|---|---|---|---|
| uniform@16 | 22.0 | 23.9 | 15.2 | 13.3 |
| top_heavy@16 | 22.0 | 23.9 | 15.2 | 13.3 |
| score@16 | 22.0 | 23.9 | 15.2 | 13.3 |
| learned@16 | 22.0 | 23.9 | 15.2 | 13.3 |
| uniform@32 | 21.5 | 27.9 | 13.2 | 13.3 |
| top_heavy@32 | 20.9 | 27.9 | 12.1 | 13.3 |
| score@32 | 20.9 | 27.9 | 12.1 | 13.3 |
| learned@32 | 19.6 | 26.5 | 12.1 | 13.3 |
| uniform@64 | 21.8 | 24.5 | 13.6 | 14.8 |
| top_heavy@64 | 22.5 | 23.9 | 14.1 | 14.8 |
| score@64 | 22.3 | 23.9 | 13.0 | 14.8 |
| learned@64 | 21.8 | 24.5 | 13.6 | 14.8 |
| uniform@128 | 22.1 | 23.4 | 18.6 | 19.4 |
| top_heavy@128 | 22.1 | 23.4 | 18.6 | 19.4 |
| score@128 | 22.1 | 23.4 | 18.6 | 19.4 |
| learned@128 | 22.1 | 23.4 | 18.6 | 19.4 |
| raw_bm25 | 22.1 | 20.6 | 23.4 | 16.7 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.898 | -0.5 [-1.8, +0.6] | 0.775 |
| score@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.898 | -0.5 [-1.8, +0.6] | 0.775 |
| learned@32 vs uniform@32 | -1.3 [-3.0, +0.0] | 0.976 | -1.5 [-3.3, -0.0] | 0.978 |
| learned@32 vs top_heavy@32 | -0.7 [-2.3, +1.0] | 0.855 | -1.0 [-2.9, +0.7] | 0.883 |
| top_heavy@64 vs uniform@64 | +0.0 [-1.3, +1.3] | 0.588 | +0.4 [-0.5, +1.4] | 0.205 |
| score@64 vs uniform@64 | +0.0 [-1.3, +1.3] | 0.588 | +0.1 [-0.7, +1.1] | 0.396 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.0 [-1.3, +1.3] | 0.616 | -0.4 [-1.4, +0.5] | 0.794 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
