# Evaluation summary

Run: `runs/qwen/hotpotqa/r2_nested_M32_all_e6__learned_s43`

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
| compressed_m4 | 12.0 [8.7, 16.0] | 20.4 [16.4, 24.3] | 8 vectors |
| compressed_m8 | 13.0 [9.3, 17.0] | 22.0 [17.9, 26.2] | 16 vectors |
| compressed_m16 | 13.7 [10.0, 18.0] | 22.9 [18.7, 27.2] | 32 vectors |
| compressed_m32 | 13.7 [10.0, 17.7] | 22.3 [18.2, 26.4] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 55.0 | 73.3 | 82.7 | 93.3 | 0.0 | 18.7 | 31.3 | 57.0 |
| query reasoner (before E2E) | 39.0 | 55.0 | 66.7 | 85.3 | 0.0 | 10.0 | 18.3 | 34.7 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.0 [15.0, 23.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.0 [15.0, 23.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.0 [15.0, 23.0] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.7 [9.0, 16.7] | 19.0 [15.0, 23.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.0 [9.3, 17.0] | 19.9 [16.0, 24.0] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 12.7 [9.0, 16.7] | 20.3 [16.6, 24.5] |
| score@32 | [15.5, 8.0, 4.3, 4.3] | 32.0 vectors | 12.7 [9.0, 16.7] | 20.3 [16.6, 24.5] |
| learned@32 | [12.3, 5.9, 4.6, 9.3] | 32.0 vectors | 14.0 [10.3, 18.0] | 21.4 [17.6, 25.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 12.0 [8.7, 16.0] | 19.3 [15.5, 23.3] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 12.0 [8.7, 16.0] | 18.9 [15.1, 22.9] |
| score@64 | [30.9, 16.0, 8.5, 8.5] | 64.0 vectors | 12.0 [8.7, 16.0] | 18.9 [15.1, 22.9] |
| learned@64 | [24.6, 13.1, 8.0, 18.3] | 64.0 vectors | 11.3 [8.0, 15.0] | 18.3 [14.7, 22.2] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 20.5 [16.7, 24.6] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 20.5 [16.7, 24.6] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 20.5 [16.7, 24.6] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 20.5 [16.7, 24.6] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [12.3, 5.9, 4.6, 9.3] | 9.0 | 7.5 |
| 64 | [24.6, 13.1, 8.0, 18.3] | 18.7 | 14.6 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (165) | rank 2 (55) | rank 3+ (50) | not retrieved (30) |
|---|---|---|---|---|
| uniform@16 | 19.2 | 17.1 | 25.2 | 11.0 |
| top_heavy@16 | 19.2 | 17.1 | 25.2 | 11.0 |
| score@16 | 19.2 | 17.1 | 25.2 | 11.0 |
| learned@16 | 19.2 | 17.1 | 25.2 | 11.0 |
| uniform@32 | 20.7 | 19.6 | 21.6 | 12.9 |
| top_heavy@32 | 21.2 | 19.3 | 22.5 | 14.1 |
| score@32 | 21.2 | 19.3 | 22.5 | 14.1 |
| learned@32 | 22.3 | 21.1 | 22.8 | 14.8 |
| uniform@64 | 21.8 | 13.8 | 20.3 | 13.9 |
| top_heavy@64 | 21.4 | 14.4 | 18.4 | 13.9 |
| score@64 | 21.7 | 13.6 | 18.4 | 13.9 |
| learned@64 | 20.7 | 12.6 | 19.1 | 13.9 |
| uniform@128 | 20.6 | 19.6 | 22.7 | 18.1 |
| top_heavy@128 | 20.6 | 19.6 | 22.7 | 18.1 |
| score@128 | 20.6 | 19.6 | 22.7 | 18.1 |
| learned@128 | 20.6 | 19.6 | 22.7 | 18.1 |
| raw_bm25 | 21.1 | 25.4 | 21.0 | 19.4 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.3 [-1.7, +0.7] | 0.811 | +0.5 [-1.0, +1.9] | 0.248 |
| score@32 vs uniform@32 | -0.3 [-1.7, +0.7] | 0.811 | +0.5 [-1.0, +1.9] | 0.248 |
| learned@32 vs uniform@32 | +1.0 [-0.3, +2.7] | 0.116 | +1.6 [+0.1, +3.1] | 0.019 |
| learned@32 vs top_heavy@32 | +1.3 [-0.3, +3.0] | 0.066 | +1.1 [-0.2, +2.7] | 0.059 |
| top_heavy@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.669 | -0.4 [-1.5, +0.6] | 0.780 |
| score@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.669 | -0.4 [-1.4, +0.5] | 0.775 |
| learned@64 vs uniform@64 | -0.7 [-1.7, +0.0] | 1.000 | -1.0 [-2.2, -0.1] | 0.983 |
| learned@64 vs top_heavy@64 | -0.7 [-2.0, +0.3] | 0.918 | -0.6 [-2.0, +0.7] | 0.819 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
