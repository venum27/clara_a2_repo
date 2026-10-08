"""Breadth vs depth at an equal budget, for the round-2 Qwen models, plus the latency tables, in one file:
runs/breadth_summary.md.

For each dataset and E2E training type (rule splits / budget head), over seeds 42-44:
  B=32: 4 documents x 8 vectors (results/)  vs  8 documents x 4 vectors (results_k8/)
  B=64: 4 documents x 16 vectors            vs  8 documents x 8 vectors
Each row gives mean +- std over seeds and a paired bootstrap over all (question, seed) pairs.

    python3 summarize_breadth.py
"""
import argparse
import glob
import os

import numpy as np

from nclara.utils import f1_score, paired_bootstrap, read_json

CONFIGS = (("rule splits", "r2_nested_M32_all_e6"), ("budget head", "r2_nested_M32_all_e6__learned"))


def per_question(run_dir, folder, split):
    p = os.path.join(run_dir, folder, "qa_predictions.json")
    if not os.path.exists(p):
        return None
    return {e["id"]: f1_score(e["preds"][split], e["gold"]) for e in read_json(p) if split in e.get("preds", {})}


def fmt(v):
    return "-" if not v else (f"{np.mean(v):.1f}" if len(v) == 1 else f"{np.mean(v):.1f} +- {np.std(v, ddof=1):.1f}")


def main(args):
    L = ["# Breadth vs depth at an equal budget (Qwen, round 2)\n",
         "F1 (%), uniform split; mean +- std over E2E seeds. Difference: 8 documents minus 4 documents, paired over all "
         "(question, seed) pairs, with 95% interval. The 8-document models were trained reading 4 documents.\n",
         "| Dataset | E2E trained with | Budget | 4 docs | 8 docs | Difference [95% CI] | Seeds |",
         "|---|---|---|---|---|---|---|"]
    retr = ["\n## Retrieval: questions with both gold documents among those read (%)\n",
            "| Dataset | E2E trained with | top 3 | top 5 | top 8 | Seeds |", "|---|---|---|---|---|---|"]
    for ds in sorted(os.listdir(os.path.join(args.runs_dir, "qwen"))):
        for label, cfg in CONFIGS:
            runs = sorted(glob.glob(os.path.join(args.runs_dir, "qwen", ds, f"{cfg}_s*")))
            runs = [r for r in runs if os.path.exists(os.path.join(r, "results_k8", "eval.json"))]
            if not runs:
                continue
            for B, d4, d8 in ((32, "4 x 8", "8 x 4"), (64, "4 x 16", "8 x 8")):
                a_all, b_all, m4, m8 = [], [], [], []
                for r in runs:
                    q4 = per_question(r, "results", f"uniform@{B}")
                    q8 = per_question(r, "results_k8", f"uniform@{B}")
                    if not q4 or not q8:
                        continue
                    ids = sorted(set(q4) & set(q8))
                    m4.append(100 * np.mean([q4[i] for i in ids]))
                    m8.append(100 * np.mean([q8[i] for i in ids]))
                    b_all += [q4[i] for i in ids]
                    a_all += [q8[i] for i in ids]
                if not a_all:
                    continue
                t = paired_bootstrap(a_all, b_all)
                L.append(f"| {ds} | {label} | {B} ({d4} vs {d8}) | {fmt(m4)} | {fmt(m8)} | "
                         f"{t['diff']:+.1f} [{t['lo']:+.1f}, {t['hi']:+.1f}] | {len(m4)} |")
            vals = {k: [] for k in (3, 5, 8)}
            for r in runs:
                row = read_json(os.path.join(r, "results_k8", "eval.json"))["retrieval"]["query reasoner (after E2E)"]
                for k in vals:
                    if f"all_gold@{k}" in row:
                        vals[k].append(row[f"all_gold@{k}"]["mean"])
            retr.append(f"| {ds} | {label} | {fmt(vals[3])} | {fmt(vals[5])} | {fmt(vals[8])} | {len(runs)} |")
    L += retr
    for p in sorted(glob.glob(os.path.join(args.runs_dir, "latency_*.md"))):
        L += ["", open(p).read()]
    out = os.path.join(args.runs_dir, "breadth_summary.md")
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"-> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs_dir", default="runs")
    main(p.parse_args())
