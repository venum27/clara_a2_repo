# Evaluation summary

Run: `runs/t5/hotpotqa/nested_M32__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: google/flan-t5-base (encoder-decoder), base parameters: 247,577,856
- LoRA parameters per adapter: {'compressor': 3538944, 'generator': 3538944, 'query_reasoner': 3538944}
- Memory-embedding parameters: 49,152
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x, m=32: 4.1x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 2.9 [1.5, 4.2] | 13.8 [11.7, 16.0] | 520 |
| 8 | 3.1 [1.7, 4.4] | 14.6 [12.3, 16.9] | 520 |
| 16 | 3.1 [1.7, 4.4] | 14.1 [11.9, 16.3] | 520 |
| 32 | 3.5 [1.9, 5.0] | 14.2 [12.0, 16.4] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 11.3 [7.7, 15.0] | 18.8 [15.0, 22.6] | 8 vectors |
| compressed_m8 | 11.7 [8.0, 15.3] | 19.6 [15.8, 23.4] | 16 vectors |
| compressed_m16 | 11.7 [8.0, 15.3] | 20.2 [16.4, 24.1] | 32 vectors |
| compressed_m32 | 12.0 [8.3, 15.7] | 20.0 [16.2, 23.9] | 64 vectors |
| raw_text_gold | 57.3 [51.7, 63.0] | 72.0 [67.2, 76.4] | 208 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 45.0 | 68.0 | 77.7 | 92.3 | 0.0 | 17.3 | 29.0 | 50.7 |
| query reasoner (before E2E) | 42.7 | 59.7 | 71.0 | 89.0 | 0.0 | 16.0 | 25.7 | 48.3 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.2] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.2] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.2] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 11.0 [7.7, 14.7] | 18.3 [14.5, 22.2] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 10.7 [7.3, 14.3] | 18.3 [14.5, 22.1] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 10.7 [7.3, 14.3] | 18.4 [14.6, 22.1] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 10.7 [7.3, 14.3] | 18.4 [14.6, 22.1] |
| learned@32 | [9.1, 6.5, 7.4, 8.9] | 32.0 vectors | 10.7 [7.3, 14.3] | 18.8 [15.1, 22.6] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.7 [7.3, 14.3] | 18.7 [14.9, 22.4] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 10.7 [7.3, 14.3] | 18.4 [14.7, 22.2] |
| score@64 | [30.9, 16.0, 8.6, 8.6] | 64.0 vectors | 10.7 [7.3, 14.3] | 18.4 [14.7, 22.2] |
| learned@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 10.7 [7.3, 14.3] | 18.7 [14.9, 22.4] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 10.0 [6.7, 13.3] | 17.5 [13.8, 21.2] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 10.0 [6.7, 13.3] | 17.5 [13.8, 21.2] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 10.0 [6.7, 13.3] | 17.5 [13.8, 21.2] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 10.0 [6.7, 13.3] | 17.5 [13.8, 21.2] |
| raw_bm25 | - | 528 tokens | 19.0 [14.7, 23.3] | 26.0 [21.5, 30.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [9.1, 6.5, 7.4, 8.9] | 8.3 | 7.9 |
| 64 | [16.0, 16.0, 16.0, 16.0] | 16.0 | 16.0 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (135) | rank 2 (69) | rank 3+ (50) | not retrieved (46) |
|---|---|---|---|---|
| uniform@16 | 18.0 | 20.3 | 18.4 | 15.8 |
| top_heavy@16 | 18.0 | 20.3 | 18.4 | 15.8 |
| score@16 | 18.0 | 20.3 | 18.4 | 15.8 |
| learned@16 | 18.0 | 20.3 | 18.4 | 15.8 |
| uniform@32 | 19.1 | 20.0 | 16.4 | 15.3 |
| top_heavy@32 | 19.2 | 20.0 | 16.4 | 15.8 |
| score@32 | 19.2 | 20.0 | 16.4 | 15.8 |
| learned@32 | 19.7 | 20.0 | 17.8 | 15.8 |
| uniform@64 | 19.4 | 21.2 | 16.5 | 15.5 |
| top_heavy@64 | 19.4 | 20.0 | 16.4 | 15.3 |
| score@64 | 19.4 | 20.0 | 16.4 | 15.3 |
| learned@64 | 19.4 | 21.2 | 16.5 | 15.5 |
| uniform@128 | 18.5 | 17.9 | 16.4 | 15.3 |
| top_heavy@128 | 18.5 | 17.9 | 16.4 | 15.3 |
| score@128 | 18.5 | 17.9 | 16.4 | 15.3 |
| learned@128 | 18.5 | 17.9 | 16.4 | 15.3 |
| raw_bm25 | 27.8 | 21.9 | 27.6 | 25.1 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.1 [-0.4, +0.7] | 0.315 |
| score@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.1 [-0.4, +0.7] | 0.315 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.6 [+0.1, +1.3] | 0.020 |
| learned@32 vs top_heavy@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.5 [+0.0, +1.1] | 0.019 |
| top_heavy@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | -0.3 [-1.0, +0.3] | 0.819 |
| score@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | -0.3 [-1.0, +0.3] | 0.819 |
| learned@64 vs uniform@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@64 vs top_heavy@64 | +0.0 [+0.0, +0.0] | 1.000 | +0.3 [-0.3, +1.0] | 0.188 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
