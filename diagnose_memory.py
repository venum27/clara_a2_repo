"""Does the compressed memory carry answer information? For every finished run (or one --run_dir), the trained
generator answers the evaluation questions with:
  no memory      the question alone
  wrong memory   the gold passages of a DIFFERENT question, all memory vectors (32 nested, 16 fixed)
  gold memory    the question's own gold passages, 4 vectors and all vectors each
If 'no memory' and 'wrong memory' score close to 'gold memory', the memory carries little answer information.
Results go to <run>/results/diagnose.json and are printed as one table.

    python3 diagnose_memory.py                      # every run that has an e2e checkpoint
    python3 diagnose_memory.py --run_dir runs/qwen/hotpotqa/nested_M32_s42
"""
import argparse
import glob
import os

import numpy as np
import torch
from tqdm import tqdm

from nclara.modeling import load_from_checkpoint
from nclara.utils import (bootstrap_ci, exact_match, f1_score, get_device, precision_context, read_json, set_seed,
                          write_json)
from train_e2e import E2E_INSTRUCTION


@torch.no_grad()
def diagnose(run_dir, dataset, data_dir, n_eval, amp, tiny):
    device = get_device()
    model, meta = load_from_checkpoint(os.path.join(run_dir, "e2e"), device=device, tiny=tiny)
    model.model.eval()
    records = read_json(os.path.join(data_dir, f"{dataset}_eval.json"))[:n_eval]
    m_small, m_large = min(4, model.max_mem), model.max_mem
    preds = {"no memory": [], "wrong memory (all)": [], "gold memory (4)": [], "gold memory (all)": []}
    with precision_context(amp, device)():
        gold_mem = [[model.compress(r["paragraphs"][i], "compressor")[0] for i in r["gold_idx"]]
                    for r in tqdm(records, desc=f"compressing gold passages ({run_dir})")]
        for n, r in enumerate(tqdm(records, desc="answering")):
            instr = E2E_INSTRUCTION.format(q=r["question"])
            other = gold_mem[(n + len(records) // 2) % len(records)]      # a different question's passages
            preds["no memory"].append(model.generate(instr, []))
            preds["wrong memory (all)"].append(model.generate(instr, [m[:m_large] for m in other]))
            preds["gold memory (4)"].append(model.generate(instr, [m[:m_small] for m in gold_mem[n]]))
            preds["gold memory (all)"].append(model.generate(instr, [m[:m_large] for m in gold_mem[n]]))
    golds = [r["answer"] for r in records]
    res = {k: {"EM": bootstrap_ci([exact_match(p, g) for p, g in zip(v, golds)]),
               "F1": bootstrap_ci([f1_score(p, g) for p, g in zip(v, golds)]), "n": len(golds)}
           for k, v in preds.items()}
    res["vectors_all"] = m_large
    write_json(res, os.path.join(run_dir, "results", "diagnose.json"))
    del model
    torch.cuda.empty_cache()
    return res


def main(args):
    set_seed(0)
    if args.run_dir:
        runs = [args.run_dir]
    else:
        runs = sorted(os.path.dirname(os.path.dirname(p))
                      for p in glob.glob(os.path.join(args.runs_dir, "*", "*", "*", "e2e", "meta.json")))
    rows = []
    for run in runs:
        dataset = run.rstrip("/").split(os.sep)[-2]
        out = os.path.join(run, "results", "diagnose.json")
        res = read_json(out) if os.path.exists(out) and not args.force else \
            diagnose(run, dataset, args.data_dir, args.n_eval, args.amp, args.tiny)
        rows.append((run, res))
    if not rows:
        print("no finished runs found (need <run>/e2e/meta.json)")
        return
    keys = ["no memory", "wrong memory (all)", "gold memory (4)", "gold memory (all)"]
    lines = ["| Run | all = | " + " | ".join(keys) + " |", "|---" * (len(keys) + 2) + "|"]
    for run, res in rows:
        lines.append(f"| {os.path.relpath(run, args.runs_dir)} | {res.get('vectors_all', '-')} | " +
                     " | ".join(f"{res[k]['F1']['mean']:.1f} [{res[k]['F1']['lo']:.1f}, {res[k]['F1']['hi']:.1f}]"
                                if k in res else "-" for k in keys) + " |")
    text = "F1 (%) with the trained generator:\n\n" + "\n".join(lines) + "\n"
    print("\n" + text)
    with open(os.path.join(args.runs_dir, "diagnose_summary.md"), "w") as f:
        f.write(text)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run_dir", default=None)
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--n_eval", type=int, default=300)
    p.add_argument("--amp", choices=["none", "bf16"], default="bf16")
    p.add_argument("--force", action="store_true", help="recompute runs that already have diagnose.json")
    p.add_argument("--tiny", action="store_true")
    main(p.parse_args())
