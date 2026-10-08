"""Shared helpers: seeding, JSON I/O, QA metrics, bootstrap confidence intervals, random-retrieval baselines."""
import collections
import json
import math
import os
import random
import re
import string

import numpy as np
import torch


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def precision_context(amp, device):
    """Returns a factory for the forward-pass context. 'bf16' = autocast to bfloat16 on GPUs that support it
    (L40S / A100 / H100; not the T4). Weights, LoRA updates and the optimiser stay in fp32."""
    import contextlib
    if device == "cuda":
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    if amp == "bf16" and device == "cuda":
        if not torch.cuda.is_bf16_supported():
            print("[precision] bf16 not supported on this GPU; falling back to fp32")
            return contextlib.nullcontext
        return lambda: torch.autocast("cuda", dtype=torch.bfloat16)
    return contextlib.nullcontext


def read_json(path):
    with open(path) as f:
        return json.load(f)


def write_json(obj, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def parse_int_list(s):
    if isinstance(s, (list, tuple)):
        return [int(x) for x in s]
    return [int(x) for x in str(s).split(",") if str(x).strip()]


def parse_str_list(s):
    if isinstance(s, (list, tuple)):
        return list(s)
    return [x.strip() for x in str(s).split(",") if x.strip()]


# ---------------------------------------------------------------- QA metrics (standard SQuAD/HotpotQA style)
def normalize_answer(s: str) -> str:
    s = str(s).lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    return " ".join(s.split())


def exact_match(pred: str, gold: str) -> int:
    return int(normalize_answer(pred) == normalize_answer(gold))


def f1_score(pred: str, gold: str) -> float:
    p, g = normalize_answer(pred).split(), normalize_answer(gold).split()
    common = collections.Counter(p) & collections.Counter(g)
    same = sum(common.values())
    if same == 0:
        return 0.0
    precision, recall = same / len(p), same / len(g)
    return 2 * precision * recall / (precision + recall)


def clean_prediction(text: str) -> str:
    """Keep the first non-empty line and drop a leading 'Answer:' if the model repeats it."""
    for line in str(text).split("\n"):
        line = line.strip()
        if line:
            return re.sub(r"^(answer|a)\s*[:\-]\s*", "", line, flags=re.I).strip()
    return ""


# ---------------------------------------------------------------- robustness: bootstrap CIs
def bootstrap_ci(values, n_boot=2000, alpha=0.05, seed=0):
    """Mean and percentile bootstrap CI, returned in percent."""
    vals = np.asarray(values, dtype=float)
    if len(vals) == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan")}
    rng = np.random.default_rng(seed)
    means = vals[rng.integers(0, len(vals), size=(n_boot, len(vals)))].mean(axis=1)
    return {"mean": 100 * float(vals.mean()),
            "lo": 100 * float(np.percentile(means, 100 * alpha / 2)),
            "hi": 100 * float(np.percentile(means, 100 * (1 - alpha / 2)))}


def paired_bootstrap(a, b, n_boot=2000, seed=0):
    """Paired bootstrap for mean(a) - mean(b) on the same examples.
    Returns the difference (percentage points), its 95% CI and the fraction of resamples where a <= b."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    d = a - b
    rng = np.random.default_rng(seed)
    boots = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
    return {"diff": 100 * float(d.mean()),
            "lo": 100 * float(np.percentile(boots, 2.5)),
            "hi": 100 * float(np.percentile(boots, 97.5)),
            "p_not_better": float((boots <= 0).mean())}


# ---------------------------------------------------------------- retrieval metrics and random baselines
def hit_at_k(ranked, gold, k):
    """1 if at least one gold document is in the top-k (the metric used in A1)."""
    return int(len(set(ranked[:k]) & set(gold)) > 0)


def all_gold_at_k(ranked, gold, k):
    """1 if every gold document is in the top-k (full supporting-evidence recall, stricter for multi-hop)."""
    return int(set(gold) <= set(ranked[:k]))


def random_hit_at_k(n, g, k):
    """Expected hit@k when ranking n candidates (g of them gold) uniformly at random."""
    k = min(k, n)
    if n - g < k:
        return 1.0
    return 1.0 - math.comb(n - g, k) / math.comb(n, k)


def random_all_gold_at_k(n, g, k):
    k = min(k, n)
    if k < g:
        return 0.0
    return math.comb(n - g, k - g) / math.comb(n, k)
