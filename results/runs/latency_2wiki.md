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
