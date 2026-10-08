# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s44`

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
| compressed_m4 | 34.3 [29.3, 40.0] | 38.2 [33.0, 43.6] | 10 vectors |
| compressed_m8 | 33.7 [28.7, 39.0] | 38.4 [33.4, 43.8] | 20 vectors |
| compressed_m16 | 35.3 [30.3, 40.7] | 40.4 [35.5, 45.8] | 40 vectors |
| compressed_m32 | 36.3 [31.3, 42.0] | 41.8 [36.8, 47.2] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 69.3 | 87.0 | 93.3 | 98.0 | 0.0 | 22.7 | 37.3 | 62.0 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.4, 43.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.4, 43.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.4, 43.0] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.7 [28.3, 39.0] | 37.6 [32.4, 43.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 35.0 [29.7, 40.3] | 40.3 [35.1, 45.5] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 35.7 [30.3, 41.3] | 40.4 [35.2, 45.8] |
| score@32 | [15.2, 8.0, 4.4, 4.4] | 32.0 vectors | 35.7 [30.3, 41.3] | 40.3 [35.1, 45.7] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 35.0 [29.7, 40.3] | 40.3 [35.1, 45.5] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 35.7 [30.3, 41.0] | 40.4 [35.3, 45.7] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 35.3 [30.0, 40.7] | 40.2 [35.0, 45.5] |
| score@64 | [30.4, 16.0, 8.8, 8.8] | 64.0 vectors | 35.3 [30.0, 40.7] | 40.0 [34.8, 45.4] |
| learned@64 | [16.0, 16.0, 16.0, 16.1] | 64.0 vectors | 35.7 [30.3, 41.0] | 40.4 [35.3, 45.7] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 40.4 [35.1, 46.0] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 40.4 [35.1, 46.0] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 40.4 [35.1, 46.0] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.0 [29.7, 40.3] | 40.4 [35.1, 46.0] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [16.0, 16.0, 16.0, 16.1] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (208) | rank 2 (53) | rank 3+ (26) | not retrieved (13) |
|---|---|---|---|---|
| uniform@16 | 35.1 | 34.2 | 51.0 | 64.1 |
| top_heavy@16 | 35.1 | 34.2 | 51.0 | 64.1 |
| score@16 | 35.1 | 34.2 | 51.0 | 64.1 |
| learned@16 | 35.1 | 34.2 | 51.0 | 64.1 |
| uniform@32 | 38.4 | 37.1 | 49.9 | 63.7 |
| top_heavy@32 | 38.7 | 37.1 | 49.1 | 63.7 |
| score@32 | 38.5 | 37.1 | 49.1 | 63.7 |
| learned@32 | 38.4 | 37.1 | 49.9 | 63.7 |
| uniform@64 | 38.8 | 36.3 | 49.1 | 66.3 |
| top_heavy@64 | 38.8 | 34.4 | 49.9 | 66.3 |
| score@64 | 38.5 | 34.4 | 49.9 | 66.3 |
| learned@64 | 38.8 | 36.3 | 49.1 | 66.3 |
| uniform@128 | 38.4 | 34.8 | 54.9 | 66.3 |
| top_heavy@128 | 38.4 | 34.8 | 54.9 | 66.3 |
| score@128 | 38.4 | 34.8 | 54.9 | 66.3 |
| learned@128 | 38.4 | 34.8 | 54.9 | 66.3 |
| raw_bm25 | 21.7 | 23.4 | 33.3 | 33.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.224 | +0.1 [-1.4, +1.9] | 0.434 |
| score@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.224 | +0.0 [-1.5, +1.7] | 0.496 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -0.7 [-2.0, +0.7] | 0.903 | -0.1 [-1.9, +1.4] | 0.566 |
| top_heavy@64 vs uniform@64 | -0.3 [-1.3, +0.7] | 0.811 | -0.2 [-1.6, +1.2] | 0.627 |
| score@64 vs uniform@64 | -0.3 [-1.3, +0.7] | 0.811 | -0.4 [-1.8, +0.8] | 0.737 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.3 [-0.7, +1.3] | 0.394 | +0.2 [-1.2, +1.6] | 0.373 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
