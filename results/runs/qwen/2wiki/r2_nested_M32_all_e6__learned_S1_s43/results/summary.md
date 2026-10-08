# Evaluation summary

Run: `runs/qwen/2wiki/r2_nested_M32_all_e6__learned_S1_s43`

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
| compressed_m4 | 33.7 [28.3, 39.3] | 37.4 [32.0, 42.8] | 10 vectors |
| compressed_m8 | 34.3 [29.0, 39.7] | 39.2 [33.9, 44.7] | 20 vectors |
| compressed_m16 | 34.0 [28.7, 39.7] | 38.4 [33.2, 43.7] | 40 vectors |
| compressed_m32 | 34.7 [29.3, 40.3] | 39.1 [33.8, 44.5] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 70.3 | 88.0 | 94.0 | 96.7 | 0.0 | 21.7 | 33.0 | 59.0 |
| query reasoner (before E2E) | 27.0 | 46.0 | 57.7 | 81.7 | 0.0 | 1.7 | 5.0 | 16.7 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 38.7] | 36.5 [31.3, 41.9] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 38.7] | 36.5 [31.3, 41.9] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 38.7] | 36.5 [31.3, 41.9] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 38.7] | 36.5 [31.3, 41.9] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 34.3 [29.0, 39.7] | 38.4 [33.0, 43.6] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 33.7 [28.0, 39.0] | 37.8 [32.5, 43.1] |
| score@32 | [15.5, 8.0, 4.2, 4.2] | 32.0 vectors | 34.0 [28.3, 39.3] | 38.2 [32.8, 43.4] |
| learned@32 | [7.6, 8.0, 8.2, 8.2] | 32.0 vectors | 33.0 [27.7, 38.3] | 37.2 [32.0, 42.3] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 33.7 [28.3, 39.0] | 38.3 [33.0, 43.5] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 33.3 [28.0, 38.7] | 37.4 [32.2, 42.6] |
| score@64 | [31.0, 16.0, 8.5, 8.5] | 64.0 vectors | 33.3 [28.0, 38.7] | 37.5 [32.3, 42.7] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 33.7 [28.3, 39.0] | 38.3 [33.0, 43.5] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.7 [29.3, 40.3] | 38.8 [33.6, 44.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.7 [29.3, 40.3] | 38.8 [33.6, 44.1] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.7 [29.3, 40.3] | 38.8 [33.6, 44.1] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.7 [29.3, 40.3] | 38.8 [33.6, 44.1] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [7.6, 8.0, 8.2, 8.2] | 8.5 | 7.6 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (211) | rank 2 (53) | rank 3+ (23) | not retrieved (13) |
|---|---|---|---|---|
| uniform@16 | 34.6 | 35.9 | 46.9 | 51.8 |
| top_heavy@16 | 34.6 | 35.9 | 46.9 | 51.8 |
| score@16 | 34.6 | 35.9 | 46.9 | 51.8 |
| learned@16 | 34.6 | 35.9 | 46.9 | 51.8 |
| uniform@32 | 38.5 | 32.2 | 41.4 | 56.0 |
| top_heavy@32 | 37.7 | 32.4 | 41.4 | 56.0 |
| score@32 | 38.2 | 32.4 | 41.4 | 56.0 |
| learned@32 | 36.9 | 32.4 | 42.7 | 51.4 |
| uniform@64 | 37.8 | 33.3 | 42.7 | 59.1 |
| top_heavy@64 | 37.1 | 31.6 | 41.4 | 59.1 |
| score@64 | 37.1 | 31.6 | 42.6 | 59.1 |
| learned@64 | 37.8 | 33.3 | 42.7 | 59.1 |
| uniform@128 | 37.2 | 36.1 | 47.9 | 60.0 |
| top_heavy@128 | 37.2 | 36.1 | 47.9 | 60.0 |
| score@128 | 37.2 | 36.1 | 47.9 | 60.0 |
| learned@128 | 37.2 | 36.1 | 47.9 | 60.0 |
| raw_bm25 | 22.0 | 30.1 | 19.0 | 28.7 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | -0.7 [-1.7, +0.0] | 1.000 | -0.5 [-1.7, +0.5] | 0.789 |
| score@32 vs uniform@32 | -0.3 [-1.0, +0.0] | 1.000 | -0.2 [-1.2, +0.7] | 0.610 |
| learned@32 vs uniform@32 | -1.3 [-3.3, +0.3] | 0.956 | -1.2 [-3.3, +0.8] | 0.867 |
| learned@32 vs top_heavy@32 | -0.7 [-2.7, +1.0] | 0.823 | -0.7 [-2.9, +1.3] | 0.740 |
| top_heavy@64 vs uniform@64 | -0.3 [-1.7, +0.7] | 0.803 | -0.9 [-2.2, +0.1] | 0.963 |
| score@64 vs uniform@64 | -0.3 [-1.7, +0.7] | 0.803 | -0.8 [-2.1, +0.2] | 0.944 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.3 [-0.7, +1.7] | 0.407 | +0.9 [-0.1, +2.2] | 0.037 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
