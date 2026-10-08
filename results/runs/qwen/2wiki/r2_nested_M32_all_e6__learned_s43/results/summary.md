# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s43`

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
| compressed_m4 | 35.3 [30.0, 40.7] | 38.8 [33.4, 44.1] | 10 vectors |
| compressed_m8 | 38.0 [32.7, 43.7] | 42.6 [37.2, 47.9] | 20 vectors |
| compressed_m16 | 37.3 [32.0, 43.0] | 41.7 [36.5, 47.2] | 40 vectors |
| compressed_m32 | 37.7 [32.3, 43.3] | 42.0 [36.9, 47.4] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 71.7 | 87.7 | 93.7 | 96.7 | 0.0 | 25.7 | 35.7 | 61.0 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 35.0 [29.7, 40.3] | 37.9 [32.6, 43.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 35.0 [29.7, 40.3] | 37.9 [32.6, 43.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 35.0 [29.7, 40.3] | 37.9 [32.6, 43.2] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 35.0 [29.7, 40.3] | 37.9 [32.6, 43.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 36.3 [30.7, 41.7] | 40.0 [34.3, 45.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 35.7 [30.3, 41.0] | 40.1 [34.8, 45.4] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 36.0 [30.7, 41.3] | 40.6 [35.4, 45.9] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 36.3 [30.7, 41.7] | 40.0 [34.3, 45.4] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 37.0 [31.3, 42.3] | 41.2 [35.7, 46.5] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 36.0 [30.7, 41.7] | 40.2 [34.6, 45.6] |
| score@64 | [30.8, 16.0, 8.6, 8.6] | 64.0 vectors | 36.0 [30.7, 41.7] | 40.4 [34.8, 45.6] |
| learned@64 | [23.0, 20.3, 10.3, 10.4] | 64.0 vectors | 36.0 [30.7, 41.7] | 40.6 [35.0, 45.9] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 37.3 [32.0, 43.0] | 41.4 [36.0, 46.8] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 37.3 [32.0, 43.0] | 41.4 [36.0, 46.8] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 37.3 [32.0, 43.0] | 41.4 [36.0, 46.8] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 37.3 [32.0, 43.0] | 41.4 [36.0, 46.8] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [23.0, 20.3, 10.3, 10.4] | 19.1 | 13.4 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (215) | rank 2 (48) | rank 3+ (22) | not retrieved (15) |
|---|---|---|---|---|
| uniform@16 | 36.6 | 34.5 | 38.6 | 66.6 |
| top_heavy@16 | 36.6 | 34.5 | 38.6 | 66.6 |
| score@16 | 36.6 | 34.5 | 38.6 | 66.6 |
| learned@16 | 36.6 | 34.5 | 38.6 | 66.6 |
| uniform@32 | 38.6 | 38.5 | 38.4 | 66.6 |
| top_heavy@32 | 39.2 | 35.0 | 41.7 | 66.6 |
| score@32 | 40.0 | 35.0 | 41.7 | 66.6 |
| learned@32 | 38.6 | 38.5 | 38.4 | 66.6 |
| uniform@64 | 40.2 | 36.8 | 42.9 | 66.6 |
| top_heavy@64 | 39.2 | 35.3 | 41.5 | 69.2 |
| score@64 | 39.2 | 35.3 | 43.4 | 69.2 |
| learned@64 | 39.5 | 35.0 | 44.4 | 69.2 |
| uniform@128 | 39.3 | 38.9 | 48.9 | 69.4 |
| top_heavy@128 | 39.3 | 38.9 | 48.9 | 69.4 |
| score@128 | 39.3 | 38.9 | 48.9 | 69.4 |
| learned@128 | 39.3 | 38.9 | 48.9 | 69.4 |
| raw_bm25 | 21.9 | 31.3 | 19.5 | 27.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-2.3, +1.3] | 0.816 | +0.1 [-1.9, +2.2] | 0.466 |
| score@32 vs uniform@32 | -0.3 [-2.0, +1.3] | 0.727 | +0.7 [-1.2, +2.7] | 0.239 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | +0.7 [-1.3, +2.3] | 0.289 | -0.1 [-2.2, +1.9] | 0.534 |
| top_heavy@64 vs uniform@64 | -1.0 [-2.3, +0.0] | 1.000 | -0.9 [-2.3, +0.2] | 0.934 |
| score@64 vs uniform@64 | -1.0 [-2.3, +0.0] | 1.000 | -0.8 [-2.1, +0.3] | 0.903 |
| learned@64 vs uniform@64 | -1.0 [-2.3, +0.0] | 1.000 | -0.6 [-1.8, +0.5] | 0.832 |
| learned@64 vs top_heavy@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.4 [-0.1, +0.9] | 0.070 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
