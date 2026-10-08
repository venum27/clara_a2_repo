"""Results on the larger evaluation set (results_big/ in each run), in one file: runs/big_eval_summary.md.

  1. Ours vs the original CLaRa code at 64 memory vectors per question, paired on the same questions: our method
     (round 2, budget head, seeds 42-44; differences pooled over all question-seed pairs) and our CLaRa
     re-implementation (round 2 fixed-16).
  2. Does the learned split beat the uniform split (our method, pooled over seeds), at 32 and 64 vectors?

    python3 summarize_big.py
"""
import argparse
import glob
import os

import numpy as np

from nclara.utils import exact_match, f1_score, paired_bootstrap, read_json

METHOD = "r2_nested_M32_all_e6__learned"
CLARA_OURS = "r2_fixed_M16_e6_s42"
OFFICIAL = "clara_official_CR16_s42"


def ours(run_dir, split):
    p = os.path.join(run_dir, "results_big", "qa_predictions.json")
    if not os.path.exists(p):
        return None
    return {e["id"]: (e["preds"][split], e["gold"]) for e in read_json(p) if split in e.get("preds", {})}


def official(run_dir):
    p = os.path.join(run_dir, "results_big", "qa_predictions.json")
    return {e["id"]: (e["pred"], e["gold"]) for e in read_json(p)} if os.path.exists(p) else None


def hit1(run_dir):
    p = os.path.join(run_dir, "results_big", "eval.json")
    if not os.path.exists(p):
        return None
    r = read_json(p).get("retrieval", {}).get("query reasoner (after E2E)", {}).get("hit@1")
    return None if r is None else r["mean"]


def scores(pred):
    return ({i: f1_score(p, g) for i, (p, g) in pred.items()}, {i: exact_match(p, g) for i, (p, g) in pred.items()})


def ci(t):
    return f"{t['diff']:+.1f} [{t['lo']:+.1f}, {t['hi']:+.1f}]"


def fmt(v):
    return "-" if not v else (f"{np.mean(v):.1f}" if len(v) == 1 else f"{np.mean(v):.1f} +- {np.std(v, ddof=1):.1f}")


def main(args):
    L = ["# Larger evaluation (Qwen, 64 memory vectors per question)\n"]
    vs = ["## Ours vs the original CLaRa code, paired on the same questions (F1 and EM, %)\n",
          "| Dataset | Questions | Official CLaRa F1 / EM / hit@1 | System | F1 / EM / hit@1 | F1 difference [95% CI] | "
          "EM difference [95% CI] |", "|---|---|---|---|---|---|---|"]
    split = ["\n## Does the learned split beat the uniform split? (our method, pooled over seeds, F1 points)\n",
             "| Dataset | Budget | Seeds | Questions | learned - uniform [95% CI] | top-heavy - uniform [95% CI] |",
             "|---|---|---|---|---|---|"]
    for ds_dir in sorted(glob.glob(os.path.join(args.runs_dir, "qwen", "*"))):
        ds = os.path.basename(ds_dir)
        off = official(os.path.join(ds_dir, OFFICIAL))
        method_runs = sorted(glob.glob(os.path.join(ds_dir, f"{METHOD}_s*")))
        if off:
            off_f1, off_em = scores(off)
            off_txt = (f"{100 * np.mean(list(off_f1.values())):.1f} / {100 * np.mean(list(off_em.values())):.1f} / "
                       f"{fmt([hit1(os.path.join(ds_dir, OFFICIAL))] if hit1(os.path.join(ds_dir, OFFICIAL)) else [])}")
            systems = [(f"our method (budget head), {len(method_runs)} seeds", [(r, "learned@64") for r in method_runs]),
                       ("our CLaRa re-implementation (fixed-16)", [(os.path.join(ds_dir, CLARA_OURS), "uniform@64")])]
            for label, runs in systems:
                a_f1, b_f1, a_em, b_em, f1s, ems, hits = [], [], [], [], [], [], []
                for run, sp in runs:
                    pr = ours(run, sp)
                    if not pr:
                        continue
                    f1, em = scores(pr)
                    ids = sorted(set(f1) & set(off_f1))
                    a_f1 += [f1[i] for i in ids]
                    b_f1 += [off_f1[i] for i in ids]
                    a_em += [em[i] for i in ids]
                    b_em += [off_em[i] for i in ids]
                    f1s.append(100 * np.mean([f1[i] for i in ids]))
                    ems.append(100 * np.mean([em[i] for i in ids]))
                    if hit1(run) is not None:
                        hits.append(hit1(run))
                if not a_f1:
                    continue
                n = len(a_f1) // max(len(f1s), 1)
                vs.append(f"| {ds} | {n} | {off_txt} | {label} | {fmt(f1s)} / {fmt(ems)} / {fmt(hits)} | "
                          f"{ci(paired_bootstrap(a_f1, b_f1))} | {ci(paired_bootstrap(a_em, b_em))} |")
        for B in (32, 64):
            lu, tu, b_l, b_t, n_seeds = [], [], [], [], 0
            for run in method_runs:
                u, le, th = ours(run, f"uniform@{B}"), ours(run, f"learned@{B}"), ours(run, f"top_heavy@{B}")
                if not (u and le and th):
                    continue
                n_seeds += 1
                fu, fl, ft = scores(u)[0], scores(le)[0], scores(th)[0]
                ids = sorted(set(fu) & set(fl) & set(ft))
                lu += [fl[i] for i in ids]
                tu += [ft[i] for i in ids]
                b_l += [fu[i] for i in ids]
            if lu:
                split.append(f"| {ds} | {B} | {n_seeds} | {len(lu) // n_seeds} | {ci(paired_bootstrap(lu, b_l))} | "
                             f"{ci(paired_bootstrap(tu, b_l))} |")
    L += vs + split
    out = os.path.join(args.runs_dir, "big_eval_summary.md")
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"-> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--runs_dir", default="runs")
    main(p.parse_args())
