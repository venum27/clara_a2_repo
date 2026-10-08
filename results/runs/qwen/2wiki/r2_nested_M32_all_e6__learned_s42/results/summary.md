# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_s42`

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
| compressed_m4 | 33.3 [28.0, 39.0] | 36.5 [31.2, 41.9] | 10 vectors |
| compressed_m8 | 33.7 [28.3, 39.0] | 37.7 [32.4, 43.1] | 20 vectors |
| compressed_m16 | 34.3 [29.0, 40.0] | 38.5 [33.3, 43.9] | 40 vectors |
| compressed_m32 | 34.3 [29.3, 40.0] | 37.6 [32.6, 43.1] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 69.3 | 85.7 | 92.7 | 97.7 | 0.0 | 23.0 | 36.7 | 61.3 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.7] | 35.8 [30.4, 41.3] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.7] | 35.8 [30.4, 41.3] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.7] | 35.8 [30.4, 41.3] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.0 [27.7, 38.7] | 35.8 [30.4, 41.3] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 32.3 [27.3, 37.7] | 36.2 [30.9, 41.5] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 33.7 [28.3, 39.0] | 38.0 [32.8, 43.5] |
| score@32 | [15.2, 8.0, 4.4, 4.4] | 32.0 vectors | 34.0 [28.7, 39.3] | 38.3 [33.2, 43.9] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 32.3 [27.3, 37.7] | 36.2 [30.9, 41.5] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 33.0 [27.7, 38.3] | 37.4 [32.2, 42.7] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 33.7 [28.3, 39.3] | 37.9 [32.8, 43.4] |
| score@64 | [30.4, 16.0, 8.8, 8.8] | 64.0 vectors | 33.7 [28.3, 39.3] | 37.9 [32.8, 43.4] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 33.0 [27.7, 38.3] | 37.4 [32.2, 42.7] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.3] | 37.3 [32.1, 42.8] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.3] | 37.3 [32.1, 42.8] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.3] | 37.3 [32.1, 42.8] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.3] | 37.3 [32.1, 42.8] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (208) | rank 2 (49) | rank 3+ (33) | not retrieved (10) |
|---|---|---|---|---|
| uniform@16 | 33.0 | 42.5 | 42.2 | 40.0 |
| top_heavy@16 | 33.0 | 42.5 | 42.2 | 40.0 |
| score@16 | 33.0 | 42.5 | 42.2 | 40.0 |
| learned@16 | 33.0 | 42.5 | 42.2 | 40.0 |
| uniform@32 | 32.8 | 43.5 | 41.5 | 53.3 |
| top_heavy@32 | 35.1 | 46.7 | 38.5 | 53.3 |
| score@32 | 35.1 | 46.7 | 41.5 | 53.3 |
| learned@32 | 32.8 | 43.5 | 41.5 | 53.3 |
| uniform@64 | 33.9 | 47.1 | 39.7 | 53.3 |
| top_heavy@64 | 34.9 | 46.6 | 39.1 | 53.3 |
| score@64 | 34.9 | 46.6 | 39.1 | 53.3 |
| learned@64 | 33.9 | 47.1 | 39.7 | 53.3 |
| uniform@128 | 34.6 | 44.8 | 38.5 | 53.3 |
| top_heavy@128 | 34.6 | 44.8 | 38.5 | 53.3 |
| score@128 | 34.6 | 44.8 | 38.5 | 53.3 |
| learned@128 | 34.6 | 44.8 | 38.5 | 53.3 |
| raw_bm25 | 22.7 | 23.4 | 27.4 | 27.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +1.3 [+0.0, +3.0] | 0.063 | +1.8 [+0.1, +3.6] | 0.017 |
| score@32 vs uniform@32 | +1.7 [+0.3, +3.3] | 0.005 | +2.1 [+0.6, +3.9] | 0.001 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -1.3 [-3.0, +0.0] | 0.976 | -1.8 [-3.6, -0.1] | 0.984 |
| top_heavy@64 vs uniform@64 | +0.7 [-0.7, +2.0] | 0.217 | +0.5 [-0.8, +1.9] | 0.225 |
| score@64 vs uniform@64 | +0.7 [-0.7, +2.0] | 0.217 | +0.5 [-0.8, +1.9] | 0.225 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | -0.7 [-2.0, +0.7] | 0.914 | -0.5 [-1.9, +0.8] | 0.775 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
