"""Learned per-document memory budgets.

CLaRa learns WHICH documents to read (straight-through top-k). The budget head learns HOW MUCH of each selected
document to read: for every retrieved document it outputs a distribution over prefix lengths (e.g. 4/8/16/32
memory vectors). It is trained end to end from the answer loss alone, with a constraint on the average number of
vectors per question. This only works because nested SCP makes every prefix of the memory a valid compression.

Exact budget. The head only chooses among splits whose total is EXACTLY the budget B (e.g. for 64 vectors over four
documents: [16,16,16,16], every arrangement of [32,16,8,8], ...). Every question therefore uses the same number of
vectors as the uniform baseline, so any gain comes from reallocation alone, and uniform and top-heavy are themselves
among the options. A split's score is the sum of its documents' length scores, normalised over the feasible splits.
Because lengths are scored per document, one trained head can be used at any total budget.

Training signal. A split is a discrete choice, and feeding the generator zero-padded vectors would not match
inference (where a prefix is simply shorter), so splits are sampled and prefixes truncated exactly as at inference.
The head is trained with the score-function (REINFORCE) estimator: samples whose answer loss is lower than the other
samples' become more likely (leave-one-out baseline), with a small entropy bonus against early collapse.
"""
import itertools
import torch
import torch.nn as nn
import torch.nn.functional as F


class BudgetHead(nn.Module):
    """Scores each selected document's candidate prefix lengths from the query, the document and its retrieval score.

    Inputs are detached from the retriever and compressor: the head only learns from the budget signal.
    """

    def __init__(self, hidden_size, lengths, k, proj=128, width=128):
        super().__init__()
        self.lengths = sorted(int(x) for x in lengths)
        self.k = k
        self.proj_q = nn.Linear(hidden_size, proj)
        self.proj_d = nn.Linear(hidden_size, proj)
        self.mlp = nn.Sequential(nn.Linear(3 * proj + 2 + k, width), nn.GELU(), nn.Linear(width, len(self.lengths)))
        nn.init.zeros_(self.mlp[-1].weight)      # start from a uniform distribution over lengths
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, q_pool, d_pools, scores):
        """q_pool (H,), d_pools (n, H) and scores (n,) for the selected documents in rank order -> logits (n, L)."""
        n = d_pools.shape[0]
        q = self.proj_q(F.normalize(q_pool.float(), dim=-1)).unsqueeze(0).expand(n, -1)
        d = self.proj_d(F.normalize(d_pools.float(), dim=-1))
        s = scores.float()
        rank = torch.eye(self.k, device=d.device)[:n]
        extra = torch.cat([s[:, None], (s - s.max())[:, None], rank], dim=-1)
        return self.mlp(torch.cat([q, d, q * d, extra], dim=-1))

    def patterns(self, n, total, device):
        """All length assignments (as indices into self.lengths) for n documents that sum exactly to total."""
        key = (n, total)
        if not hasattr(self, "_cache"):
            self._cache = {}
        if key not in self._cache:
            pats = [p for p in itertools.product(range(len(self.lengths)), repeat=n)
                    if sum(self.lengths[i] for i in p) == total]
            if not pats:
                raise ValueError(f"no split of {total} vectors over {n} documents uses lengths {self.lengths}")
            self._cache[key] = torch.tensor(pats, dtype=torch.long)
        return self._cache[key].to(device)

    def split_distribution(self, logits, total):
        pats = self.patterns(logits.shape[0], total, logits.device)          # (P, n)
        rows = torch.arange(logits.shape[0], device=logits.device)
        return torch.distributions.Categorical(logits=logits[rows, pats].sum(dim=1)), pats

    def choose(self, logits, total, greedy=False):
        """Pick a split summing exactly to total: sampled during training, most likely at evaluation.
        Returns (budgets as ints in document order, log-probability, entropy)."""
        dist, pats = self.split_distribution(logits, total)
        j = dist.probs.argmax() if greedy else dist.sample()
        return [self.lengths[i] for i in pats[j].tolist()], dist.log_prob(j), dist.entropy()


def head_features(query_mem, cand_mems, chosen, scores, r, min_len):
    """Detached inputs for the head: pooled query vectors, pooled leading vectors of each chosen document, scores."""
    q_pool = query_mem[:r].mean(0).detach()
    d_pools = torch.stack([cand_mems[c][:min_len].mean(0) for c in chosen]).detach()
    return q_pool, d_pools, scores.detach()[chosen]


def save_head(head, path):
    torch.save({"state": head.state_dict(), "lengths": head.lengths, "k": head.k,
                "hidden_size": head.proj_q.in_features}, path)


def load_head(path, device):
    ck = torch.load(path, map_location=device)
    head = BudgetHead(ck["hidden_size"], ck["lengths"], ck["k"]).to(device)
    head.load_state_dict(ck["state"])
    head.eval()
    return head
