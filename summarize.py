"""Collect every runs/<backbone>/<dataset>/<run>/results/eval.json into one markdown file of report tables.

    python summarize.py --runs_dir runs
"""
import argparse
import collections
import glob
import os
import re

import numpy as np

from nclara.utils import read_json


def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--budget", type=int, default=64, help="total budget for the headline QA comparison")
    p.add_argument("--out", default=None)
    return p


def get(d, *keys, default=None):
    """Nested lookup that also accepts int keys for JSON's string keys."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        if k in d:
            d = d[k]
        elif str(k) in d:
            d = d[str(k)]
        else:
            return default
    return d


def _diff(r, a, b):
    x, y = get(r, "qa", "results", a, "F1", "mean"), get(r, "qa", "results", b, "F1", "mean")
    return None if x is None or y is None else x - y


def f(x):
    return "-" if x is None else f"{x:.1f}"


def main(args):
    rows = []
    for path in sorted(glob.glob(os.path.join(args.runs_dir, "*", "*", "*", "results", "eval.json"))):
        res = read_json(path)
        bb, ds, run = path.split(os.sep)[-5:-2]
        rows.append((bb, ds, run, res))
    if not rows:
        print(f"no results found under {args.runs_dir}")
        return
    B = args.budget
    L = ["# Results across runs\n", "F1 (%) unless stated. Per-run details and confidence intervals are in each "
         "run's results/summary.md.\n",
         "## Compressor-only QA on held-out synthetic questions, by prefix length (F1)\n",
         "| Backbone | Dataset | Run | m=4 | m=8 | m=16 | m=32 |", "|---|---|---|---|---|---|---|"]
    for bb, ds, run, r in rows:
        L.append(f"| {bb} | {ds} | {run} | " + " | ".join(f(get(r, "scp_curve", m, "F1", "mean"))
                                                          for m in (4, 8, 16, 32)) + " |")
    L += ["\n## Retrieval (hit@1 / all-gold@2, %)\n",
          "| Backbone | Dataset | Run | Random | BM25 | Reasoner before E2E | Reasoner after E2E |",
          "|---|---|---|---|---|---|---|"]
    for bb, ds, run, r in rows:
        cells = []
        for m in ("random (expected)", "BM25", "query reasoner (before E2E)", "query reasoner (after E2E)"):
            cells.append(f"{f(get(r, 'retrieval', m, 'hit@1', 'mean'))} / {f(get(r, 'retrieval', m, 'all_gold@2', 'mean'))}")
        L.append(f"| {bb} | {ds} | {run} | " + " | ".join(cells) + " |")
    L += [f"\n## End-to-end QA at a total budget of {B} memory vectors (F1)\n",
          f"| Backbone | Dataset | Run | uniform | top_heavy | score | learned | learned - uniform [95% CI] | "
          f"learned - top_heavy [95% CI] | Raw text BM25 (F1 / tokens) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for bb, ds, run, r in rows:
        q = get(r, "qa", "results", default={}) or {}

        def test(name):
            t = get(r, "qa", "paired_tests", name, "F1")
            return f"{t['diff']:+.1f} [{t['lo']:+.1f}, {t['hi']:+.1f}]" if t else "-"
        raw = q.get("raw_bm25", {})
        L.append(f"| {bb} | {ds} | {run} | {f(get(q, f'uniform@{B}', 'F1', 'mean'))} | "
                 f"{f(get(q, f'top_heavy@{B}', 'F1', 'mean'))} | {f(get(q, f'score@{B}', 'F1', 'mean'))} | "
                 f"{f(get(q, f'learned@{B}', 'F1', 'mean'))} | {test(f'learned@{B} vs uniform@{B}')} | "
                 f"{test(f'learned@{B} vs top_heavy@{B}')} | "
                 f"{f(get(raw, 'F1', 'mean'))} / {f(raw.get('context_tokens'))} |")
    L += [f"\n## Learned budgets at {B} vectors: mean vectors per document\n",
          "| Backbone | Dataset | Run | by rank slot | gold documents | other documents |", "|---|---|---|---|---|---|"]
    for bb, ds, run, r in rows:
        lb = get(r, "qa", "learned_budgets", B)
        if lb:
            L.append(f"| {bb} | {ds} | {run} | {lb.get('avg_vectors_by_rank')} | {f(lb.get('avg_vectors_gold_docs'))} | "
                     f"{f(lb.get('avg_vectors_other_docs'))} |")
    L += ["\n## Accuracy vs budget (F1)\n", "| Backbone | Dataset | Run | Split | 16 | 32 | 64 | 128 |",
          "|---|---|---|---|---|---|---|---|"]
    for bb, ds, run, r in rows:
        for pol in ("uniform", "top_heavy", "learned"):
            vals = [get(r, "qa", "results", f"{pol}@{b}", "F1", "mean") for b in (16, 32, 64, 128)]
            if any(v is not None for v in vals):
                L.append(f"| {bb} | {ds} | {run} | {pol} | " + " | ".join(f(v) for v in vals) + " |")
    # ---- ours vs the original CLaRa code, paired on the same questions
    from nclara.utils import f1_score, paired_bootstrap
    L += [f"\n## Ours vs the original CLaRa code, paired on the same questions ({B} vectors per question, F1)\n",
          "| Backbone | Dataset | Ours (run: split) | Official CLaRa | Ours | Difference [95% CI] | P(not better) |",
          "|---|---|---|---|---|---|---|"]
    by_key = {(bb, ds, run): r for bb, ds, run, r in rows}
    for (bb, ds, run), r in sorted(by_key.items()):
        if not run.startswith("clara_official"):
            continue
        off_path = os.path.join(args.runs_dir, bb, ds, run, "results", "qa_predictions.json")
        if not os.path.exists(off_path):
            continue
        official = {p["id"]: p for p in read_json(off_path)}
        seed = run.rsplit("_s", 1)[-1]
        ours_runs = sorted(o for (b2, d2, o) in by_key if b2 == bb and d2 == ds and not o.startswith("clara_official")
                           and o.endswith(f"_s{seed}"))
        for ours_run in ours_runs:                # learned split for learned runs, uniform for fixed, else top-heavy
            split = f"learned@{B}" if "__learned" in ours_run else (f"uniform@{B}" if "fixed" in ours_run
                                                                     else f"top_heavy@{B}")
            p = os.path.join(args.runs_dir, bb, ds, ours_run, "results", "qa_predictions.json")
            if not os.path.exists(p):
                continue
            ours = {e["id"]: e for e in read_json(p) if split in e.get("preds", {})}
            ids = sorted(set(ours) & set(official))
            if not ids:
                continue
            a = [f1_score(ours[i]["preds"][split], ours[i]["gold"]) for i in ids]
            b = [f1_score(official[i]["pred"], official[i]["gold"]) for i in ids]
            t = paired_bootstrap(a, b)
            L.append(f"| {bb} | {ds} | {ours_run}: {split} | {100 * np.mean(b):.1f} | {100 * np.mean(a):.1f} | "
                     f"{t['diff']:+.1f} [{t['lo']:+.1f}, {t['hi']:+.1f}] | {t['p_not_better']:.3f} |")

    # ---- mean +- std across seeds (runs named <config>_s<seed>)
    groups = collections.defaultdict(list)
    for bb, ds, run, r in rows:
        groups[(bb, ds, re.sub(r"_s\d+$", "", run))].append(r)
    metrics = {
        "SCP F1 m=4": lambda r: get(r, "scp_curve", 4, "F1", "mean"),
        "SCP F1 m=16": lambda r: get(r, "scp_curve", 16, "F1", "mean"),
        "hit@1 after E2E": lambda r: get(r, "retrieval", "query reasoner (after E2E)", "hit@1", "mean"),
        "hit@1 gain from E2E": lambda r: (
            get(r, "retrieval", "query reasoner (after E2E)", "hit@1", "mean")
            - get(r, "retrieval", "query reasoner (before E2E)", "hit@1", "mean"))
        if get(r, "retrieval", "query reasoner (before E2E)", "hit@1", "mean") is not None
        and get(r, "retrieval", "query reasoner (after E2E)", "hit@1", "mean") is not None else None,
        f"uniform@{B} F1": lambda r: get(r, "qa", "results", f"uniform@{B}", "F1", "mean"),
        f"top_heavy@{B} F1": lambda r: get(r, "qa", "results", f"top_heavy@{B}", "F1", "mean"),
        f"learned@{B} F1": lambda r: get(r, "qa", "results", f"learned@{B}", "F1", "mean"),
        "learned gold / other vectors": None,
        "top_heavy - uniform @32": lambda r: _diff(r, "top_heavy@32", "uniform@32"),
        "learned - uniform @32": lambda r: _diff(r, "learned@32", "uniform@32"),
        f"top_heavy - uniform @{B}": lambda r: _diff(r, f"top_heavy@{B}", f"uniform@{B}"),
        f"learned - uniform @{B}": lambda r: _diff(r, f"learned@{B}", f"uniform@{B}"),
        "memory gain (gold - none)": lambda r: None,      # filled from diagnose.json below
    }
    L += ["\n## Mean +- std across seeds\n", "| Backbone | Dataset | Config | Seeds | " + " | ".join(metrics) + " |",
          "|---" * (len(metrics) + 4) + "|"]
    diag = {}
    for bb, ds, run, r in rows:
        p = os.path.join(args.runs_dir, bb, ds, run, "results", "diagnose.json")
        if os.path.exists(p):
            d = read_json(p)
            diag[(bb, ds, run)] = d["gold memory (all)"]["F1"]["mean"] - d["no memory"]["F1"]["mean"]
    run_names = {id(r): run for bb, ds, run, r in rows}
    for (bb, ds, cfg), rs in sorted(groups.items()):
        cells = []
        for name, fn in metrics.items():
            if name == "memory gain (gold - none)":
                vals = [diag[(bb, ds, run_names[id(r)])] for r in rs if (bb, ds, run_names[id(r)]) in diag]
                cells.append("-" if not vals else (f"{vals[0]:+.1f}" if len(vals) == 1
                                                   else f"{np.mean(vals):+.1f} +- {np.std(vals, ddof=1):.1f}"))
                continue
            if fn is None:
                g = [get(r, "qa", "learned_budgets", B, "avg_vectors_gold_docs") for r in rs]
                o = [get(r, "qa", "learned_budgets", B, "avg_vectors_other_docs") for r in rs]
                g, o = [x for x in g if x is not None], [x for x in o if x is not None]
                cells.append(f"{np.mean(g):.1f} / {np.mean(o):.1f}" if g and o else "-")
                continue
            vals = [v for v in (fn(r) for r in rs) if v is not None]
            cells.append("-" if not vals else (f"{np.mean(vals):.1f}" if len(vals) == 1
                                               else f"{np.mean(vals):.1f} +- {np.std(vals, ddof=1):.1f}"))
        L.append(f"| {bb} | {ds} | {cfg} | {len(rs)} | " + " | ".join(cells) + " |")

    out = args.out or os.path.join(args.runs_dir, "results_summary.md")
    with open(out, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"summary of {len(rows)} runs -> {out}")


if __name__ == "__main__":
    main(build_parser().parse_args())
