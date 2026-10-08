# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_S1_s42`

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
| compressed_m4 | 12.7 [9.0, 16.7] | 21.3 [17.2, 25.6] | 8 vectors |
| compressed_m8 | 14.3 [10.3, 18.3] | 23.4 [19.0, 27.7] | 16 vectors |
| compressed_m16 | 14.7 [10.7, 19.0] | 23.9 [19.6, 28.3] | 32 vectors |
| compressed_m32 | 15.0 [11.0, 19.3] | 24.0 [19.8, 28.5] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 57.3 | 76.0 | 84.3 | 95.0 | 0.0 | 19.3 | 36.7 | 64.0 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.3, 16.3] | 20.7 [16.8, 24.8] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.3, 16.3] | 20.7 [16.8, 24.8] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.3, 16.3] | 20.7 [16.8, 24.8] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.3, 16.3] | 20.7 [16.8, 24.8] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 14.0 [10.3, 18.0] | 21.8 [17.9, 26.1] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.3 [9.7, 17.3] | 21.1 [17.2, 25.2] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 13.3 [9.7, 17.3] | 21.1 [17.2, 25.2] |
| learned@32 | [7.8, 7.9, 8.1, 8.2] | 32.0 vectors | 12.7 [9.3, 16.7] | 21.0 [17.2, 25.0] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 20.8 [16.9, 25.0] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 19.5 [15.7, 23.6] |
| score@64 | [30.8, 16.0, 8.6, 8.6] | 64.0 vectors | 13.0 [9.3, 17.0] | 19.7 [15.8, 23.8] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 20.8 [16.9, 25.0] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [8.7, 16.0] | 20.3 [16.5, 24.4] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [8.7, 16.0] | 20.3 [16.5, 24.4] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [8.7, 16.0] | 20.3 [16.5, 24.4] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 12.3 [8.7, 16.0] | 20.3 [16.5, 24.4] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [7.8, 7.9, 8.1, 8.2] | 8.1 | 7.9 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (172) | rank 2 (56) | rank 3+ (47) | not retrieved (25) |
|---|---|---|---|---|
| uniform@16 | 21.7 | 26.5 | 17.0 | 7.4 |
| top_heavy@16 | 21.7 | 26.5 | 17.0 | 7.4 |
| score@16 | 21.7 | 26.5 | 17.0 | 7.4 |
| learned@16 | 21.7 | 26.5 | 17.0 | 7.4 |
| uniform@32 | 23.7 | 25.4 | 17.3 | 9.5 |
| top_heavy@32 | 22.5 | 26.3 | 16.7 | 8.5 |
| score@32 | 22.5 | 26.3 | 16.7 | 8.5 |
| learned@32 | 21.8 | 26.0 | 18.2 | 9.5 |
| uniform@64 | 22.7 | 25.4 | 16.9 | 5.3 |
| top_heavy@64 | 21.5 | 22.1 | 17.6 | 4.3 |
| score@64 | 21.2 | 23.7 | 17.6 | 4.3 |
| learned@64 | 22.7 | 25.4 | 16.9 | 5.3 |
| uniform@128 | 21.7 | 21.4 | 22.3 | 5.2 |
| top_heavy@128 | 21.7 | 21.4 | 22.3 | 5.2 |
| score@128 | 21.7 | 21.4 | 22.3 | 5.2 |
| learned@128 | 21.7 | 21.4 | 22.3 | 5.2 |
| raw_bm25 | 24.9 | 18.8 | 15.6 | 17.5 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.914 | -0.7 [-2.0, +0.4] | 0.875 |
| score@32 vs uniform@32 | -0.7 [-2.0, +0.7] | 0.914 | -0.7 [-2.0, +0.4] | 0.875 |
| learned@32 vs uniform@32 | -1.3 [-2.7, -0.3] | 1.000 | -0.8 [-2.1, +0.2] | 0.943 |
| learned@32 vs top_heavy@32 | -0.7 [-2.0, +0.7] | 0.909 | -0.1 [-1.3, +1.0] | 0.591 |
| top_heavy@64 vs uniform@64 | +0.0 [-1.7, +1.7] | 0.595 | -1.3 [-3.0, +0.3] | 0.945 |
| score@64 vs uniform@64 | +0.0 [-1.7, +1.7] | 0.595 | -1.2 [-2.8, +0.3] | 0.940 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.0 [-1.7, +1.7] | 0.576 | +1.3 [-0.3, +3.0] | 0.055 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
