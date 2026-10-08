"""Show the evidence for one step of the pipeline, cleanly, on one screen, for the report's screenshots. Almost
everything is read from the logs and result files the runs already wrote; only steps 1, 2 and 4 run something
(each in about a minute or less). Run from the project folder on the server (or from the repository).

    python3 show_step.py            # list the steps
    python3 show_step.py 5          # show step 5
"""
import glob
import os
import re
import subprocess
import sys

RUNS = "runs" if os.path.isdir("runs") else os.path.join("results", "runs")
SKIP = ("r2it_",)                       # runs that are not part of the report


def clean_log(path, keep=None, last=None):
    """Lines of a log with progress bars reduced to their final state and library warnings dropped."""
    if not os.path.exists(path):
        return [f"(missing: {path})"]
    raw = open(path, "rb").read().decode("utf-8", errors="replace")
    out = []
    for line in raw.split("\n"):
        line = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line.split("\r")[-1]).rstrip()
        if not line or "warnings.warn" in line or "Warning:" in line or "past_key_values" in line:
            continue
        if keep and not any(k in line for k in keep):
            continue
        if out and out[-1] == line:
            continue
        out.append(line)
    return out[-last:] if last else out


def header(title):
    print("=" * 100)
    print(title)
    print("=" * 100)


def show_lines(title, lines):
    print(f"\n-- {title}")
    for line in lines:
        print(line[:220])


def show_file(path, drop=()):
    if not os.path.exists(path):
        print(f"(missing: {path})")
        return
    for line in open(path).read().splitlines():
        if not any(d in line for d in drop):
            print(line)


def run(cmd):
    print(f"$ {cmd}\n")
    subprocess.run(cmd, shell=True)


KEY_TRAIN = ("########", "CE by prefix", "compressor changed", "results ->", "Training stage", "EM ", "training ")


def step1():
    header("Step 1: setup check (packages, GPUs, backbones, synthesiser, datasets)")
    if os.path.exists("setup_report.txt"):
        show_file("setup_report.txt")
    else:
        run("./scripts/00_setup_check.sh")


def step2():
    header("Step 2: GPU check")
    run("./scripts/00_check_gpus.sh")


def step3():
    header("Step 3: data preparation and SCP data synthesis (Qwen2.5-14B-Instruct)")
    for ds in ("hotpotqa", "2wiki"):
        show_lines(f"logs/synth_{ds}.log", clean_log(f"logs/synth_{ds}.log", last=3))
    print("\n-- data files")
    import json
    for f in sorted(glob.glob("data/*.json")):
        try:
            n = len(json.load(open(f)))
        except Exception:
            n = "?"
        print(f"{f:40s} {n} records")


def step4():
    header("Step 4: sanity checks on the real backbones (gradients, prefix independence, straight-through, budget head)")
    run("python3 sanity_checks.py --backbone qwen 2>&1 | grep -E 'PASS|FAIL|checks passed'")
    run("python3 sanity_checks.py --backbone t5 2>&1 | grep -E 'PASS|FAIL|checks passed'")


def step5():
    header("Step 5: training, first configuration (one prefix per step, 3 SCP epochs; both backbones)")
    for f in sorted(glob.glob("logs/main_*.log")):
        show_lines(f, clean_log(f, keep=KEY_TRAIN)[-14:])


def step6():
    header("Step 6: official CLaRa code trained on our data and evaluated with our metrics")
    for f in sorted(glob.glob("logs/official_*.log")):
        show_lines(f, clean_log(f, keep=("training stage", "Training stage", "EM ", "dropped", "records"))[-8:])


def step7():
    header("Step 7: training, final configuration (every prefix per step, 6 SCP epochs; Qwen)")
    for f in sorted(glob.glob("logs/round2_*.log")):
        show_lines(f, clean_log(f, keep=KEY_TRAIN)[-14:])


def step8():
    header("Step 8: final configuration, E2E seeds 43 and 44")
    for f in sorted(glob.glob("logs/seeds_*.log")):
        show_lines(f, clean_log(f, keep=KEY_TRAIN)[-10:])


def step9():
    header("Step 9: all evaluated runs")
    runs = sorted(p for p in glob.glob(os.path.join(RUNS, "*", "*", "*"))
                  if os.path.exists(os.path.join(p, "results", "eval.json"))
                  and not os.path.basename(p).startswith(SKIP))
    for p in runs:
        extra = [x for x in ("results_k8", "results_big") if os.path.exists(os.path.join(p, x, "eval.json"))]
        print(f"{os.path.relpath(p, RUNS):55s} results" + "".join(f" + {x}" for x in extra))
    print(f"\n{len(runs)} evaluated runs")


def step10():
    header("Step 10: results summary (300 questions per dataset)")
    path = os.path.join(RUNS, "results_summary.md")
    if not os.path.exists(path):
        print(f"(missing: {path})")
        return
    text = open(path).read()
    for title in ("## End-to-end QA", "## Mean +- std across seeds"):
        if title in text:
            part = text[text.index(title):]
            nxt = part.find("\n## ", 3)
            print("\n".join(l for l in (part if nxt < 0 else part[:nxt]).splitlines() if not any(s in l for s in SKIP)))
            print()


def step11():
    header("Step 11: memory diagnostic (no memory / wrong memory / gold memory)")
    show_file(os.path.join(RUNS, "diagnose_summary.md"), drop=SKIP)


def step12():
    header("Step 12: breadth test and latency benchmark")
    show_file(os.path.join(RUNS, "breadth_summary.md"), drop=SKIP)


def step13():
    header("Step 13: larger evaluation, 3,000 questions per dataset (ours vs the official CLaRa code)")
    path = os.path.join(RUNS, "big_eval_summary.md")
    if not os.path.exists(path):
        print(f"(missing: {path})")
        return
    text = open(path).read()
    if "## Does instruction tuning help?" in text:          # not part of the report
        text = text[:text.index("## Does instruction tuning help?")]
    for line in text.splitlines():
        if "instruction tuning" not in line:
            print(line)


TITLES = ["setup check", "GPU check", "data preparation", "sanity checks (runs, about 2 minutes)",
          "training, first configuration", "official CLaRa code", "training, final configuration", "extra seeds",
          "all evaluated runs", "results summary", "memory diagnostic", "breadth and latency",
          "larger evaluation (3,000 questions)"]
STEPS = [step1, step2, step3, step4, step5, step6, step7, step8, step9, step10, step11, step12, step13]

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1].isdigit() or not 1 <= int(sys.argv[1]) <= len(STEPS):
        print(__doc__)
        for i, t in enumerate(TITLES, start=1):
            print(f"  {i:2d}  {t}")
        sys.exit(0)
    STEPS[int(sys.argv[1]) - 1]()
