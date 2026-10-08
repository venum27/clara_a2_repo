# Evaluation summary

Run: `runs/qwen/2wiki/nested_M32__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 95.3 tokens; compression rate by prefix: m=4: 23.8x, m=8: 11.9x, m=16: 6.0x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 6.1 [4.2, 8.2] | 20.5 [18.0, 23.2] | 525 |
| 8 | 6.5 [4.4, 8.8] | 21.8 [19.2, 24.5] | 525 |
| 16 | 7.0 [5.0, 9.3] | 22.1 [19.4, 24.9] | 525 |
| 32 | 6.9 [4.8, 9.1] | 22.6 [19.8, 25.3] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 34.0 [29.0, 39.3] | 37.0 [31.9, 42.3] | 10 vectors |
| compressed_m8 | 33.7 [28.3, 39.0] | 36.2 [31.0, 41.4] | 20 vectors |
| compressed_m16 | 35.0 [29.7, 40.3] | 37.5 [32.3, 42.9] | 40 vectors |
| compressed_m32 | 35.3 [30.0, 40.7] | 38.0 [32.8, 43.3] | 80 vectors |
| raw_text_gold | 21.3 [16.7, 26.0] | 34.4 [30.0, 39.1] | 391 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 65.7 | 82.0 | 90.7 | 97.7 | 0.0 | 20.7 | 33.7 | 55.7 |
| query reasoner (before E2E) | 30.3 | 48.0 | 63.7 | 84.3 | 0.0 | 3.0 | 6.3 | 17.0 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [29.0, 39.7] | 37.5 [32.4, 42.9] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [29.0, 39.7] | 37.5 [32.4, 42.9] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [29.0, 39.7] | 37.5 [32.4, 42.9] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 34.3 [29.0, 39.7] | 37.5 [32.4, 42.9] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 34.3 [29.0, 40.0] | 37.2 [31.9, 42.7] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 34.3 [29.0, 39.7] | 37.1 [31.9, 42.5] |
| score@32 | [15.2, 8.0, 4.4, 4.4] | 32.0 vectors | 34.3 [29.0, 39.7] | 37.1 [31.9, 42.5] |
| learned@32 | [13.9, 4.5, 8.1, 5.6] | 32.0 vectors | 34.0 [28.7, 39.3] | 36.7 [31.5, 42.1] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.3 [29.0, 39.7] | 37.0 [31.9, 42.4] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 34.7 [29.3, 40.3] | 37.3 [32.3, 42.7] |
| score@64 | [30.3, 16.0, 8.8, 8.8] | 64.0 vectors | 34.7 [29.3, 40.3] | 37.3 [32.3, 42.7] |
| learned@64 | [14.6, 12.0, 29.4, 8.0] | 64.0 vectors | 34.7 [29.3, 40.0] | 37.5 [32.2, 43.0] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.7 [30.3, 41.3] | 38.1 [32.7, 43.6] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.7 [30.3, 41.3] | 38.1 [32.7, 43.6] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.7 [30.3, 41.3] | 38.1 [32.7, 43.6] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 35.7 [30.3, 41.3] | 38.1 [32.7, 43.6] |
| raw_bm25 | - | 490 tokens | 15.7 [11.7, 20.0] | 23.5 [19.7, 27.6] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [13.9, 4.5, 8.1, 5.6] | 9.3 | 7.0 |
| 64 | [14.6, 12.0, 29.4, 8.0] | 16.3 | 15.8 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (197) | rank 2 (49) | rank 3+ (39) | not retrieved (15) |
|---|---|---|---|---|
| uniform@16 | 36.5 | 31.6 | 37.7 | 68.9 |
| top_heavy@16 | 36.5 | 31.6 | 37.7 | 68.9 |
| score@16 | 36.5 | 31.6 | 37.7 | 68.9 |
| learned@16 | 36.5 | 31.6 | 37.7 | 68.9 |
| uniform@32 | 36.1 | 31.6 | 37.5 | 68.9 |
| top_heavy@32 | 36.1 | 31.2 | 37.5 | 68.9 |
| score@32 | 36.1 | 31.2 | 37.5 | 68.9 |
| learned@32 | 36.0 | 31.2 | 37.5 | 62.2 |
| uniform@64 | 36.3 | 33.7 | 35.2 | 62.2 |
| top_heavy@64 | 35.9 | 33.3 | 37.4 | 68.9 |
| score@64 | 35.9 | 33.3 | 37.4 | 68.9 |
| learned@64 | 36.7 | 33.3 | 37.4 | 62.2 |
| uniform@128 | 37.1 | 34.6 | 37.7 | 62.2 |
| top_heavy@128 | 37.1 | 34.6 | 37.7 | 62.2 |
| score@128 | 37.1 | 34.6 | 37.7 | 62.2 |
| learned@128 | 37.1 | 34.6 | 37.7 | 62.2 |
| raw_bm25 | 22.6 | 28.2 | 23.9 | 18.0 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.0 [-1.3, +1.3] | 0.604 | -0.1 [-1.4, +1.3] | 0.558 |
| score@32 vs uniform@32 | +0.0 [-1.3, +1.3] | 0.604 | -0.1 [-1.4, +1.3] | 0.558 |
| learned@32 vs uniform@32 | -0.3 [-2.0, +1.3] | 0.707 | -0.5 [-2.2, +1.2] | 0.712 |
| learned@32 vs top_heavy@32 | -0.3 [-1.3, +0.7] | 0.822 | -0.4 [-1.6, +0.7] | 0.822 |
| top_heavy@64 vs uniform@64 | +0.3 [-0.7, +1.7] | 0.381 | +0.3 [-0.9, +1.7] | 0.323 |
| score@64 vs uniform@64 | +0.3 [-0.7, +1.7] | 0.381 | +0.3 [-0.9, +1.7] | 0.323 |
| learned@64 vs uniform@64 | +0.3 [+0.0, +1.0] | 0.388 | +0.5 [-0.3, +1.5] | 0.142 |
| learned@64 vs top_heavy@64 | +0.0 [-1.3, +1.3] | 0.613 | +0.2 [-1.2, +1.5] | 0.416 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
