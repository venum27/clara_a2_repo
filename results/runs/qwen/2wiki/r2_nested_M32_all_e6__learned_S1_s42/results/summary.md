# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_S1_s42`

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
| compressed_m4 | 36.3 [31.0, 42.0] | 39.8 [34.4, 45.4] | 10 vectors |
| compressed_m8 | 36.7 [31.0, 42.3] | 40.8 [35.4, 46.3] | 20 vectors |
| compressed_m16 | 36.3 [31.0, 42.0] | 40.2 [34.8, 45.8] | 40 vectors |
| compressed_m32 | 33.7 [28.7, 39.3] | 37.3 [32.3, 42.7] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 70.3 | 88.0 | 92.7 | 97.0 | 0.0 | 24.0 | 36.7 | 61.3 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [28.7, 40.0] | 37.9 [32.3, 43.4] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [28.7, 40.0] | 37.9 [32.3, 43.4] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [28.7, 40.0] | 37.9 [32.3, 43.4] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [28.7, 40.0] | 37.9 [32.3, 43.4] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 35.0 [29.7, 40.3] | 39.0 [33.7, 44.4] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 35.3 [30.0, 41.0] | 39.5 [34.1, 45.0] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 35.3 [30.0, 41.0] | 39.5 [34.1, 45.0] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 35.0 [29.7, 40.3] | 39.0 [33.7, 44.4] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.3 [29.0, 39.7] | 38.3 [33.0, 43.6] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 34.7 [29.3, 40.0] | 38.9 [33.7, 44.4] |
| score@64 | [30.9, 16.0, 8.6, 8.6] | 64.0 vectors | 34.7 [29.3, 40.0] | 38.9 [33.7, 44.4] |
| learned@64 | [17.1, 16.7, 16.1, 14.1] | 64.0 vectors | 34.3 [29.0, 39.7] | 38.6 [33.4, 43.9] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.8 [32.7, 43.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.8 [32.7, 43.2] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.8 [32.7, 43.2] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.8 [32.7, 43.2] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [17.1, 16.7, 16.1, 14.1] | 17.5 | 14.7 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (211) | rank 2 (53) | rank 3+ (22) | not retrieved (14) |
|---|---|---|---|---|
| uniform@16 | 36.9 | 39.4 | 44.1 | 38.1 |
| top_heavy@16 | 36.9 | 39.4 | 44.1 | 38.1 |
| score@16 | 36.9 | 39.4 | 44.1 | 38.1 |
| learned@16 | 36.9 | 39.4 | 44.1 | 38.1 |
| uniform@32 | 37.2 | 40.7 | 44.1 | 52.4 |
| top_heavy@32 | 38.0 | 41.1 | 41.8 | 52.4 |
| score@32 | 38.0 | 41.1 | 41.8 | 52.4 |
| learned@32 | 37.2 | 40.7 | 44.1 | 52.4 |
| uniform@64 | 36.2 | 39.5 | 46.4 | 52.4 |
| top_heavy@64 | 37.0 | 39.9 | 46.4 | 52.4 |
| score@64 | 37.0 | 39.9 | 46.4 | 52.4 |
| learned@64 | 37.0 | 40.0 | 41.8 | 52.4 |
| uniform@128 | 36.2 | 39.4 | 41.8 | 50.0 |
| top_heavy@128 | 36.2 | 39.4 | 41.8 | 50.0 |
| score@128 | 36.2 | 39.4 | 41.8 | 50.0 |
| learned@128 | 36.2 | 39.4 | 41.8 | 50.0 |
| raw_bm25 | 23.3 | 21.6 | 26.5 | 28.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.3 [-0.7, +1.3] | 0.403 | +0.5 [-0.8, +1.9] | 0.248 |
| score@32 vs uniform@32 | +0.3 [-0.7, +1.3] | 0.403 | +0.5 [-0.8, +1.9] | 0.248 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -0.3 [-1.3, +0.7] | 0.821 | -0.5 [-1.9, +0.8] | 0.753 |
| top_heavy@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.402 | +0.6 [-0.9, +2.2] | 0.217 |
| score@64 vs uniform@64 | +0.3 [-1.0, +1.7] | 0.402 | +0.6 [-0.9, +2.2] | 0.217 |
| learned@64 vs uniform@64 | +0.0 [-1.3, +1.3] | 0.617 | +0.3 [-1.0, +1.7] | 0.344 |
| learned@64 vs top_heavy@64 | -0.3 [-2.0, +1.0] | 0.762 | -0.3 [-1.9, +1.3] | 0.671 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
