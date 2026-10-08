# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_S1_s44`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 5.5 [3.6, 7.4] | 21.6 [19.0, 24.2] | 525 |
| 8 | 7.0 [5.1, 9.3] | 23.8 [21.2, 26.5] | 525 |
| 16 | 8.8 [6.5, 11.2] | 25.7 [23.0, 28.7] | 525 |
| 32 | 9.0 [6.7, 11.4] | 26.6 [23.8, 29.4] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 35.3 [30.0, 40.7] | 38.8 [33.5, 44.3] | 10 vectors |
| compressed_m8 | 36.0 [30.7, 41.7] | 40.0 [34.7, 45.3] | 20 vectors |
| compressed_m16 | 36.7 [31.3, 42.0] | 40.8 [35.5, 46.1] | 40 vectors |
| compressed_m32 | 36.3 [31.0, 41.7] | 41.1 [35.9, 46.5] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 67.0 | 84.7 | 91.3 | 97.7 | 0.0 | 23.3 | 36.7 | 59.7 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.1 [32.0, 42.5] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.1 [32.0, 42.5] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.1 [32.0, 42.5] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.1 [32.0, 42.5] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.3, 42.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 35.0 [29.7, 40.7] | 38.4 [33.1, 43.9] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 35.0 [29.7, 40.7] | 38.5 [33.2, 43.9] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.3, 42.7] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 35.3 [30.0, 40.7] | 39.1 [33.8, 44.5] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 35.7 [30.3, 41.0] | 39.9 [34.6, 45.2] |
| score@64 | [30.9, 16.0, 8.6, 8.6] | 64.0 vectors | 35.7 [30.3, 41.0] | 39.7 [34.4, 45.0] |
| learned@64 | [15.8, 14.7, 17.0, 16.5] | 64.0 vectors | 34.7 [29.3, 40.0] | 39.1 [33.7, 44.4] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 36.0 [30.7, 41.7] | 40.3 [34.9, 45.8] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 36.0 [30.7, 41.7] | 40.3 [34.9, 45.8] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 36.0 [30.7, 41.7] | 40.3 [34.9, 45.8] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 36.0 [30.7, 41.7] | 40.3 [34.9, 45.8] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [15.8, 14.7, 17.0, 16.5] | 15.1 | 16.7 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (201) | rank 2 (53) | rank 3+ (33) | not retrieved (13) |
|---|---|---|---|---|
| uniform@16 | 36.0 | 34.1 | 41.5 | 56.4 |
| top_heavy@16 | 36.0 | 34.1 | 41.5 | 56.4 |
| score@16 | 36.0 | 34.1 | 41.5 | 56.4 |
| learned@16 | 36.0 | 34.1 | 41.5 | 56.4 |
| uniform@32 | 36.5 | 35.5 | 39.6 | 56.4 |
| top_heavy@32 | 37.4 | 36.2 | 41.2 | 56.4 |
| score@32 | 37.5 | 36.2 | 41.2 | 56.4 |
| learned@32 | 36.5 | 35.5 | 39.6 | 56.4 |
| uniform@64 | 37.4 | 33.4 | 48.7 | 64.1 |
| top_heavy@64 | 38.6 | 36.4 | 43.9 | 64.1 |
| score@64 | 38.3 | 36.4 | 43.9 | 64.1 |
| learned@64 | 38.0 | 33.2 | 45.6 | 64.1 |
| uniform@128 | 38.3 | 36.6 | 46.3 | 71.8 |
| top_heavy@128 | 38.3 | 36.6 | 46.3 | 71.8 |
| score@128 | 38.3 | 36.6 | 46.3 | 71.8 |
| learned@128 | 38.3 | 36.6 | 46.3 | 71.8 |
| raw_bm25 | 22.6 | 21.0 | 32.2 | 25.3 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +1.3 [-0.3, +3.3] | 0.100 | +0.9 [-0.9, +2.8] | 0.174 |
| score@32 vs uniform@32 | +1.3 [-0.3, +3.3] | 0.100 | +1.0 [-0.8, +2.9] | 0.147 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -1.3 [-3.3, +0.3] | 0.955 | -0.9 [-2.8, +0.9] | 0.826 |
| top_heavy@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.402 | +0.8 [-0.6, +2.4] | 0.143 |
| score@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.402 | +0.6 [-0.8, +2.1] | 0.212 |
| learned@64 vs uniform@64 | -0.7 [-2.0, +0.7] | 0.905 | -0.0 [-1.4, +1.4] | 0.473 |
| learned@64 vs top_heavy@64 | -1.0 [-2.3, +0.0] | 1.000 | -0.8 [-2.3, +0.6] | 0.856 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
