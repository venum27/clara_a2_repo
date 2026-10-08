"""Query-time budget allocation: how many memory tokens each retrieved document gets.

All policies take the documents in rank order (slot 0 = highest-scoring) and return one prefix length per
slot. Every length is drawn from `allowed` (the prefix lengths seen during nested SCP), so the generator is
only ever given prefixes it was trained on.
"""
import math

POLICIES = ("uniform", "top_heavy", "score")


def _snap_down(x, allowed):
    fits = [a for a in allowed if a <= x]
    return max(fits) if fits else None


def allocate(policy, k, total, allowed, scores=None, temperature=0.1):
    allowed = sorted(set(int(a) for a in allowed))
    lo = allowed[0]
    if total < lo * k:
        raise ValueError(f"total budget {total} is below the minimum {lo} x {k} slots")

    if policy == "uniform":
        # CLaRa's behaviour: every document gets the same budget.
        return [_snap_down(total // k, allowed)] * k

    if policy == "top_heavy":
        # Give each slot, in rank order, the largest prefix that still leaves the minimum for the rest.
        out, remaining = [], total
        for i in range(k):
            b = _snap_down(remaining - lo * (k - i - 1), allowed)
            out.append(b)
            remaining -= b
        return out

    if policy == "score":
        # Budget proportional to softmax(retrieval score / T), snapped down, leftover handed out by rank.
        if scores is None:
            raise ValueError("the 'score' policy needs the top-k retrieval scores")
        s = [float(x) for x in scores][:k]
        mx = max(s)
        w = [math.exp((x - mx) / temperature) for x in s]
        z = sum(w)
        out = [_snap_down(total * wi / z, allowed) or lo for wi in w]
        while sum(out) > total:                       # rounding up to `lo` can overshoot
            j = max(range(k), key=lambda i: (out[i], i))
            out[j] = _snap_down(out[j] - 1, allowed) or lo
        upgraded = True
        while upgraded:                               # spend leftover budget, best-ranked first
            upgraded = False
            for i in range(k):
                bigger = [a for a in allowed if a > out[i]]
                if bigger and sum(out) - out[i] + bigger[0] <= total:
                    out[i] = bigger[0]
                    upgraded = True
                    break
        return out

    raise ValueError(f"unknown policy {policy!r}; choose from {POLICIES}")
