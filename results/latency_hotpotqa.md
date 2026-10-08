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
