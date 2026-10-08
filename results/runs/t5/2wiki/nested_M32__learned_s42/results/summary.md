# Evaluation summary

Run: `runs/t5/2wiki/nested_M32__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 49,152
- Average passage length: 94.9 tokens; compression rate by prefix: m=4: 23.7x, m=8: 11.9x, m=16: 5.9x, m=32: 3.0x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 1.0 [0.2, 1.9] | 9.5 [7.8, 11.2] | 525 |
| 8 | 0.8 [0.2, 1.5] | 9.7 [8.0, 11.5] | 525 |
| 16 | 0.8 [0.2, 1.5] | 9.1 [7.4, 10.7] | 525 |
| 32 | 0.6 [0.0, 1.3] | 9.1 [7.5, 10.8] | 525 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 34.0 [28.3, 39.3] | 38.2 [32.8, 43.5] | 10 vectors |
| compressed_m8 | 35.0 [29.7, 40.7] | 39.1 [33.6, 44.6] | 20 vectors |
| compressed_m16 | 35.3 [30.0, 40.7] | 39.1 [33.6, 44.5] | 40 vectors |
| compressed_m32 | 35.0 [29.3, 40.3] | 38.7 [33.2, 44.1] | 80 vectors |
| raw_text_gold | 31.3 [26.3, 36.3] | 37.7 [32.7, 42.7] | 393 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 58.3 | 80.0 | 85.7 | 94.7 | 0.0 | 12.0 | 22.0 | 36.0 |
| query reasoner (after E2E) | 53.0 | 70.7 | 82.3 | 93.3 | 0.0 | 16.3 | 26.0 | 50.0 |
| query reasoner (before E2E) | 42.7 | 58.0 | 72.3 | 90.0 | 0.0 | 11.7 | 20.7 | 39.3 |
| random (expected) | 24.9 | 44.9 | 60.7 | 82.7 | 0.0 | 1.7 | 5.0 | 17.3 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 37.7 [32.4, 43.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 37.7 [32.4, 43.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 37.7 [32.4, 43.0] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 33.3 [28.0, 39.0] | 37.7 [32.4, 43.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 33.3 [28.0, 39.0] | 37.5 [32.1, 42.9] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 34.0 [28.7, 39.7] | 38.2 [32.8, 43.6] |
| score@32 | [15.3, 8.0, 4.4, 4.4] | 32.0 vectors | 34.0 [28.7, 39.7] | 38.2 [32.8, 43.6] |
| learned@32 | [8.1, 7.5, 7.1, 9.3] | 32.0 vectors | 34.3 [29.0, 40.0] | 38.4 [32.9, 43.9] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.3 [29.0, 40.0] | 37.8 [32.2, 43.4] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 34.3 [29.0, 40.0] | 38.0 [32.4, 43.4] |
| score@64 | [30.5, 16.0, 8.7, 8.7] | 64.0 vectors | 34.3 [29.0, 40.0] | 37.9 [32.3, 43.4] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 34.3 [29.0, 40.0] | 37.8 [32.2, 43.4] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.6 [32.3, 42.9] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.6 [32.3, 42.9] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.6 [32.3, 42.9] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 34.0 [28.7, 39.7] | 37.6 [32.3, 42.9] |
| raw_bm25 | - | 495 tokens | 21.0 [16.7, 25.7] | 23.5 [19.0, 28.1] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.1, 7.5, 7.1, 9.3] | 7.7 | 8.2 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (159) | rank 2 (53) | rank 3+ (54) | not retrieved (34) |
|---|---|---|---|---|
| uniform@16 | 33.7 | 33.0 | 54.7 | 36.5 |
| top_heavy@16 | 33.7 | 33.0 | 54.7 | 36.5 |
| score@16 | 33.7 | 33.0 | 54.7 | 36.5 |
| learned@16 | 33.7 | 33.0 | 54.7 | 36.5 |
| uniform@32 | 33.7 | 32.0 | 54.7 | 36.4 |
| top_heavy@32 | 35.5 | 32.2 | 52.9 | 36.2 |
| score@32 | 35.5 | 32.2 | 52.9 | 36.2 |
| learned@32 | 35.4 | 32.2 | 54.7 | 36.2 |
| uniform@64 | 34.9 | 29.9 | 54.7 | 37.2 |
| top_heavy@64 | 35.1 | 29.9 | 54.7 | 37.2 |
| score@64 | 34.9 | 29.9 | 54.7 | 37.2 |
| learned@64 | 34.9 | 29.9 | 54.7 | 37.2 |
| uniform@128 | 34.1 | 32.5 | 52.9 | 37.2 |
| top_heavy@128 | 34.1 | 32.5 | 52.9 | 37.2 |
| score@128 | 34.1 | 32.5 | 52.9 | 37.2 |
| learned@128 | 34.1 | 32.5 | 52.9 | 37.2 |
| raw_bm25 | 22.5 | 22.6 | 31.0 | 17.2 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.223 | +0.7 [-0.6, +2.0] | 0.154 |
| score@32 vs uniform@32 | +0.7 [-0.7, +2.0] | 0.223 | +0.7 [-0.6, +2.0] | 0.154 |
| learned@32 vs uniform@32 | +1.0 [+0.0, +2.3] | 0.052 | +0.9 [-0.1, +2.2] | 0.043 |
| learned@32 vs top_heavy@32 | +0.3 [+0.0, +1.3] | 0.368 | +0.2 [-0.2, +1.1] | 0.373 |
| top_heavy@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.1 [+0.0, +0.4] | 0.129 |
| score@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 0.361 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.0 [+0.0, +0.0] | 1.000 | -0.1 [-0.4, +0.0] | 1.000 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
