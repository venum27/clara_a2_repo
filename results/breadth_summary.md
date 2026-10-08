# Breadth vs depth at an equal budget (Qwen, round 2)

F1 (%), uniform split; mean +- std over E2E seeds. Difference: 8 documents minus 4 documents, paired over all (question, seed) pairs, with 95% interval. The 8-document models were trained reading 4 documents.

| Dataset | E2E trained with | Budget | 4 docs | 8 docs | Difference [95% CI] | Seeds |
|---|---|---|---|---|---|---|
| 2wiki | rule splits | 32 (4 x 8 vs 8 x 4) | 36.4 +- 0.3 | 34.2 +- 1.5 | -2.2 [-3.8, -0.6] | 3 |
| 2wiki | rule splits | 64 (4 x 16 vs 8 x 8) | 36.8 +- 2.1 | 37.5 +- 0.3 | +0.8 [-0.7, +2.3] | 3 |
| 2wiki | budget head | 32 (4 x 8 vs 8 x 4) | 38.8 +- 2.3 | 36.8 +- 2.5 | -2.0 [-3.5, -0.6] | 3 |
| 2wiki | budget head | 64 (4 x 16 vs 8 x 8) | 39.7 +- 2.0 | 38.5 +- 1.6 | -1.1 [-2.7, +0.4] | 3 |
| hotpotqa | rule splits | 32 (4 x 8 vs 8 x 4) | 19.8 +- 0.8 | 20.3 +- 0.4 | +0.5 [-0.8, +1.8] | 3 |
| hotpotqa | rule splits | 64 (4 x 16 vs 8 x 8) | 19.4 +- 1.1 | 20.0 +- 0.6 | +0.5 [-0.8, +1.9] | 3 |
| hotpotqa | budget head | 32 (4 x 8 vs 8 x 4) | 20.7 +- 1.7 | 19.5 +- 1.0 | -1.2 [-2.7, +0.2] | 3 |
| hotpotqa | budget head | 64 (4 x 16 vs 8 x 8) | 19.8 +- 1.2 | 19.8 +- 1.2 | -0.0 [-1.5, +1.4] | 3 |

## Retrieval: questions with both gold documents among those read (%)

| Dataset | E2E trained with | top 3 | top 5 | top 8 | Seeds |
|---|---|---|---|---|---|
| 2wiki | rule splits | 34.8 +- 3.0 | 60.3 +- 2.3 | 85.6 +- 1.3 | 3 |
| 2wiki | budget head | 36.6 +- 0.8 | 61.4 +- 0.5 | 87.7 +- 1.0 | 3 |
| hotpotqa | rule splits | 33.0 +- 3.2 | 60.6 +- 2.5 | 86.4 +- 0.8 | 3 |
| hotpotqa | budget head | 34.0 +- 2.5 | 59.8 +- 3.4 | 85.5 +- 1.6 | 3 |

# Latency and memory, 2wiki (NVIDIA L40S, batch size 1, median over 100 questions)

Decoding forced to 16 tokens. F1 from the runs' own evaluation (uniform split).

| Setting | Memory vectors | Input positions | Prefill (ms) | Decode (ms/token) | Total (ms) | KV cache (KB) | F1 |
|---|---|---|---|---|---|---|---|
| nested, 4 docs x 4 | 16 | 109 | 21.2 | 19.19 | 328 | 1499 | 35.8 |
| nested, 4 docs x 8 | 32 | 125 | 21.0 | 19.19 | 328 | 1691 | 36.2 |
| nested, 8 docs x 4 | 32 | 153 | 21.3 | 19.17 | 328 | 2027 | 34.1 |
| nested, 4 docs x 16 | 64 | 157 | 21.3 | 19.18 | 328 | 2075 | 37.4 |
| nested, 8 docs x 8 | 64 | 185 | 21.4 | 19.17 | 328 | 2411 | 36.6 |
| nested, 4 docs x 32 | 128 | 221 | 21.4 | 19.13 | 327 | 2843 | 37.3 |
| CLaRa-style fixed-16, 4 docs x 16 | 64 | 157 | 21.7 | 19.17 | 329 | 2075 | 37.7 |
| raw text, BM25 top-4 | - | 569 | 15.4 | 13.42 | 230 | 7025 | - |
| raw text, BM25 top-8 | - | 905 | 16.3 | 13.40 | 231 | 11047 | - |

Offline: compressing one passage 25.1 ms; encoding a question 24.9 ms; scoring the candidates 0.41 ms.
Index per passage: nested model 56 KB (32 vectors, serves every budget) vs one fixed-rate model per rate (4, 8, 16, 32 vectors) 105 KB plus four trained compressors.


# Latency and memory, hotpotqa (NVIDIA L40S, batch size 1, median over 100 questions)

Decoding forced to 16 tokens. F1 from the runs' own evaluation (uniform split).

| Setting | Memory vectors | Input positions | Prefill (ms) | Decode (ms/token) | Total (ms) | KV cache (KB) | F1 |
|---|---|---|---|---|---|---|---|
| nested, 4 docs x 4 | 16 | 112 | 19.9 | 18.09 | 309 | 1532 | 21.7 |
| nested, 4 docs x 8 | 32 | 128 | 19.8 | 18.06 | 309 | 1724 | 23.0 |
| nested, 8 docs x 4 | 32 | 156 | 20.0 | 18.05 | 309 | 2060 | 18.3 |
| nested, 4 docs x 16 | 64 | 160 | 20.0 | 18.05 | 309 | 2108 | 21.4 |
| nested, 8 docs x 8 | 64 | 188 | 20.1 | 18.03 | 309 | 2444 | 18.4 |
| nested, 4 docs x 32 | 128 | 224 | 20.2 | 18.01 | 308 | 2876 | 20.4 |
| CLaRa-style fixed-16, 4 docs x 16 | 64 | 160 | 20.5 | 18.04 | 309 | 2108 | 21.9 |
| raw text, BM25 top-4 | - | 623 | 15.2 | 12.64 | 217 | 7665 | - |
| raw text, BM25 top-8 | - | 1184 | 18.7 | 12.64 | 221 | 14400 | - |

Offline: compressing one passage 23.9 ms; encoding a question 23.6 ms; scoring the candidates 0.38 ms.
Index per passage: nested model 56 KB (32 vectors, serves every budget) vs one fixed-rate model per rate (4, 8, 16, 32 vectors) 105 KB plus four trained compressors.

