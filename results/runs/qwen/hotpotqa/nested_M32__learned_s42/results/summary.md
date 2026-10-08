# Evaluation summary

Run: `runs/qwen/hotpotqa/nested_M32__learned_s42`

All scores in %, with 95% bootstrap confidence intervals in brackets.

## Parameters and compression

- Backbone: Qwen/Qwen2.5-0.5B-Instruct (decoder-only), base parameters: 494,032,768
- LoRA parameters per adapter: {'compressor': 2162688, 'generator': 2162688, 'query_reasoner': 2162688}
- Memory-embedding parameters: 57,344
- Average passage length: 132.5 tokens; compression rate by prefix: m=4: 33.1x, m=8: 16.6x, m=16: 8.3x, m=32: 4.1x

## Compressor-only QA on held-out synthetic questions (SCP checkpoint)

| Prefix m | EM | F1 | n |
|---|---|---|---|
| 4 | 4.0 [2.5, 5.8] | 16.5 [14.2, 18.9] | 520 |
| 8 | 3.5 [2.1, 5.0] | 15.8 [13.4, 18.0] | 520 |
| 16 | 3.8 [2.3, 5.6] | 16.4 [14.0, 18.7] | 520 |
| 32 | 3.8 [2.3, 5.6] | 16.2 [13.8, 18.3] | 520 |

## Oracle: gold passages only

| Input | EM | F1 | Context size |
|---|---|---|---|
| compressed_m4 | 13.0 [9.3, 17.0] | 21.9 [18.0, 26.0] | 8 vectors |
| compressed_m8 | 13.3 [9.7, 17.3] | 22.3 [18.2, 26.3] | 16 vectors |
| compressed_m16 | 15.0 [11.0, 19.3] | 24.0 [20.0, 28.2] | 32 vectors |
| compressed_m32 | 14.0 [10.0, 18.3] | 22.1 [18.1, 26.4] | 64 vectors |
| raw_text_gold | 21.0 [16.3, 25.7] | 36.3 [31.9, 40.6] | 210 tokens |

## Retrieval

| Method | hit@1 | hit@2 | hit@3 | hit@5 | all_gold@1 | all_gold@2 | all_gold@3 | all_gold@5 |
|---|---|---|---|---|---|---|---|---|
| BM25 | 68.7 | 84.0 | 89.3 | 95.0 | 0.0 | 20.7 | 34.3 | 51.3 |
| query reasoner (after E2E) | 55.3 | 77.0 | 87.7 | 95.3 | 0.0 | 19.0 | 35.7 | 60.3 |
| query reasoner (before E2E) | 44.7 | 63.3 | 76.7 | 90.3 | 0.0 | 13.3 | 22.3 | 44.0 |
| random (expected) | 20.1 | 37.9 | 53.4 | 77.9 | 0.0 | 2.2 | 6.7 | 22.4 |

## End-to-end QA

| Setting | Budgets | Context | EM | F1 |
|---|---|---|---|---|
| uniform@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.0 [8.3, 16.0] | 20.0 [16.2, 24.0] |
| top_heavy@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.0 [8.3, 16.0] | 20.0 [16.2, 24.0] |
| score@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.0 [8.3, 16.0] | 20.0 [16.2, 24.0] |
| learned@16 | [4.0, 4.0, 4.0, 4.0] | 16.0 vectors | 12.0 [8.3, 16.0] | 20.0 [16.2, 24.0] |
| uniform@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.0 [9.3, 17.0] | 20.7 [16.8, 24.8] |
| top_heavy@32 | [16.0, 8.0, 4.0, 4.0] | 32.0 vectors | 13.7 [10.0, 17.7] | 21.5 [17.4, 25.6] |
| score@32 | [15.4, 8.0, 4.3, 4.3] | 32.0 vectors | 13.7 [10.0, 17.7] | 21.2 [17.2, 25.2] |
| learned@32 | [8.0, 8.0, 8.0, 8.0] | 32.0 vectors | 13.0 [9.3, 17.0] | 20.7 [16.8, 24.8] |
| uniform@64 | [16.0, 16.0, 16.0, 16.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.3 [17.3, 25.4] |
| top_heavy@64 | [32.0, 16.0, 8.0, 8.0] | 64.0 vectors | 13.0 [9.3, 17.0] | 20.9 [17.0, 25.0] |
| score@64 | [30.8, 16.0, 8.6, 8.6] | 64.0 vectors | 13.0 [9.3, 17.0] | 21.1 [17.1, 25.0] |
| learned@64 | [9.5, 21.8, 22.3, 10.4] | 64.0 vectors | 12.7 [9.0, 16.7] | 20.7 [16.8, 24.7] |
| uniform@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 21.0 [17.1, 25.1] |
| top_heavy@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 21.0 [17.1, 25.1] |
| score@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 21.0 [17.1, 25.1] |
| learned@128 | [32.0, 32.0, 32.0, 32.0] | 128.0 vectors | 13.0 [9.3, 17.0] | 21.0 [17.1, 25.1] |
| raw_bm25 | - | 528 tokens | 8.7 [5.7, 11.7] | 21.7 [18.1, 25.5] |

How the learned head spends its budget (mean vectors per document):

| Total | By rank slot | Gold documents | Other documents |
|---|---|---|---|
| 16 | [4.0, 4.0, 4.0, 4.0] | 4.0 | 4.0 |
| 32 | [8.0, 8.0, 8.0, 8.0] | 8.0 | 8.0 |
| 64 | [9.5, 21.8, 22.3, 10.4] | 14.9 | 16.6 |
| 128 | [32.0, 32.0, 32.0, 32.0] | 32.0 | 32.0 |

F1 by where the first gold document was ranked (number of questions in brackets):

| Setting | rank 1 (166) | rank 2 (65) | rank 3+ (45) | not retrieved (24) |
|---|---|---|---|---|
| uniform@16 | 24.2 | 13.9 | 14.8 | 17.5 |
| top_heavy@16 | 24.2 | 13.9 | 14.8 | 17.5 |
| score@16 | 24.2 | 13.9 | 14.8 | 17.5 |
| learned@16 | 24.2 | 13.9 | 14.8 | 17.5 |
| uniform@32 | 25.3 | 15.2 | 13.8 | 16.3 |
| top_heavy@32 | 26.1 | 15.2 | 13.9 | 20.8 |
| score@32 | 25.7 | 15.2 | 13.9 | 19.7 |
| learned@32 | 25.3 | 15.2 | 13.8 | 16.3 |
| uniform@64 | 24.3 | 17.8 | 18.4 | 14.7 |
| top_heavy@64 | 23.7 | 17.9 | 18.4 | 14.7 |
| score@64 | 23.7 | 18.5 | 18.4 | 14.7 |
| learned@64 | 23.4 | 17.3 | 18.4 | 15.6 |
| uniform@128 | 25.6 | 17.9 | 14.2 | 10.0 |
| top_heavy@128 | 25.6 | 17.9 | 14.2 | 10.0 |
| score@128 | 25.6 | 17.9 | 14.2 | 10.0 |
| learned@128 | 25.6 | 17.9 | 14.2 | 10.0 |
| raw_bm25 | 20.8 | 26.6 | 20.8 | 16.7 |

Paired bootstrap at equal budget, first setting minus second (percentage points):

| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |
|---|---|---|---|---|
| learned@16 vs uniform@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@16 vs top_heavy@16 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| top_heavy@32 vs uniform@32 | +0.7 [+0.0, +1.7] | 0.128 | +0.8 [-0.3, +2.0] | 0.095 |
| score@32 vs uniform@32 | +0.7 [+0.0, +1.7] | 0.128 | +0.5 [-0.4, +1.6] | 0.176 |
| learned@32 vs uniform@32 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@32 vs top_heavy@32 | -0.7 [-1.7, +0.0] | 1.000 | -0.8 [-2.0, +0.3] | 0.905 |
| top_heavy@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.691 | -0.3 [-1.2, +0.4] | 0.750 |
| score@64 vs uniform@64 | +0.0 [-1.0, +1.0] | 0.691 | -0.2 [-1.1, +0.5] | 0.653 |
| learned@64 vs uniform@64 | -0.3 [-1.0, +0.0] | 1.000 | -0.6 [-1.5, +0.1] | 0.948 |
| learned@64 vs top_heavy@64 | -0.3 [-1.0, +0.0] | 1.000 | -0.3 [-0.7, +0.2] | 0.875 |
| learned@128 vs uniform@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
| learned@128 vs top_heavy@128 | +0.0 [+0.0, +0.0] | 1.000 | +0.0 [+0.0, +0.0] | 1.000 |
