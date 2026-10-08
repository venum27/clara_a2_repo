"""Collect all results into one small, text-only folder (no checkpoints): per-run summaries and metrics,
training logs, the data settings, and a combined results_summary.md. Typically a few MB.

Use it to get results off the server by whichever route is easiest:
  * print it and copy-paste:     cat results_export/<name>/results_summary.md
  * push to the team's GitHub repo (the assignment already requires one)
  * download the single archive results_export/<name>.tar.gz

    python export_results.py --name flair2
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tarfile

KEEP = ("results/eval.json", "results/summary.md", "results/qa_predictions.json",
        "scp/train_log.json", "scp/meta.json", "e2e/train_log.json", "e2e/meta.json")


def main(args):
    out = os.path.join(args.out_dir, args.name)
    if os.path.exists(out):
        shutil.rmtree(out)
    n = 0
    for run in sorted(glob.glob(os.path.join(args.runs_dir, "*", "*", "*"))):
        if not os.path.isdir(run):
            continue
        rel = os.path.relpath(run, args.runs_dir)
        for k in KEEP:
            src = os.path.join(run, k)
            if os.path.exists(src) and (args.with_predictions or not k.endswith("qa_predictions.json")):
                dst = os.path.join(out, "runs", rel, k)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
        n += os.path.exists(os.path.join(run, "results", "eval.json"))
    os.makedirs(out, exist_ok=True)
    settings = os.path.join(args.data_dir, "SETTINGS.txt")
    if os.path.exists(settings):
        shutil.copy2(settings, os.path.join(out, "DATA_SETTINGS.txt"))
    subprocess.run([sys.executable, "summarize.py", "--runs_dir", os.path.join(out, "runs"),
                    "--out", os.path.join(out, "results_summary.md")], check=True)
    with tarfile.open(out + ".tar.gz", "w:gz") as tar:
        tar.add(out, arcname=args.name)
    print(f"\n{n} evaluated runs -> {out}/ and {out}.tar.gz ({os.path.getsize(out + '.tar.gz') / 1e6:.2f} MB)")
    print(f"view the tables:  cat {out}/results_summary.md")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", default="flair2")
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--out_dir", default="results_export")
    p.add_argument("--with_predictions", type=int, default=1, help="0 = drop per-question predictions (smaller)")
    main(p.parse_args())
