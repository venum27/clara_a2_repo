# Larger evaluation (Qwen, 64 memory vectors per question)

## Ours vs the original CLaRa code, paired on the same questions (F1 and EM, %)

| Dataset | Questions | Official CLaRa F1 / EM / hit@1 | System | F1 / EM / hit@1 | F1 difference [95% CI] | EM difference [95% CI] |
|---|---|---|---|---|---|---|
| 2wiki | 3000 | 31.9 / 29.0 / 54.3 | our method (budget head), 3 seeds | 36.2 +- 0.8 / 31.1 +- 0.5 / 72.4 +- 1.4 | +4.2 [+3.3, +5.1] | +2.1 [+1.3, +3.0] |
| 2wiki | 3000 | 31.9 / 29.0 / 54.3 | our CLaRa re-implementation (fixed-16) | 35.7 / 31.2 / 67.6 | +3.8 [+2.2, +5.3] | +2.3 [+0.6, +3.7] |
| hotpotqa | 3000 | 17.5 / 11.1 / 56.7 | our method (budget head), 3 seeds | 19.2 +- 0.5 / 11.7 +- 0.4 / 55.8 +- 2.8 | +1.8 [+1.0, +2.5] | +0.6 [-0.0, +1.3] |
| hotpotqa | 3000 | 17.5 / 11.1 / 56.7 | our CLaRa re-implementation (fixed-16) | 19.8 / 11.5 / 50.8 | +2.3 [+1.0, +3.5] | +0.4 [-0.8, +1.6] |

## Does the learned split beat the uniform split? (our method, pooled over seeds, F1 points)

| Dataset | Budget | Seeds | Questions | learned - uniform [95% CI] | top-heavy - uniform [95% CI] |
|---|---|---|---|---|---|
| 2wiki | 32 | 3 | 3000 | +0.0 [+0.0, +0.0] | +0.1 [-0.1, +0.3] |
| 2wiki | 64 | 3 | 3000 | +0.1 [-0.0, +0.2] | +0.1 [-0.1, +0.4] |
| hotpotqa | 32 | 3 | 3000 | +0.1 [-0.1, +0.3] | +0.1 [-0.2, +0.3] |
| hotpotqa | 64 | 3 | 3000 | +0.0 [-0.1, +0.2] | +0.1 [-0.1, +0.3] |
