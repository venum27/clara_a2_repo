"""Run the whole Assignment 2 pipeline: data -> SCP data synthesis -> SCP -> end-to-end -> evaluation -> summary.

Presets
  main       the proposed method (nested memory + learned budget head), the same nested compressor with rule-based
             splits (uniform / top-heavy), and the CLaRa-style fixed-16 baseline
  ablations  main + budget-head variants (no entropy bonus, one sample with a moving-average baseline, trained at
             64 only), nest_loss=all, lambda_mse in {0, 1}, rescaled memory (Qwen), E2E with uniform splits only,
             short-prefix retrieval scoring (r=4) and a sharper straight-through temperature (tau=0.1)

Examples
  python run_pipeline.py --tiny                                   # CPU smoke test, a few minutes, numbers meaningless
  python run_pipeline.py --backbones qwen --datasets hotpotqa     # one backbone/dataset on a Colab T4
  python run_pipeline.py --backbones qwen,t5 --datasets hotpotqa,2wiki --preset ablations
  python run_pipeline.py --backbones qwen --datasets hotpotqa --seeds 42,43,44 --amp bf16   # on an L40S
  python run_pipeline.py --backbones qwen --preset round2 --diagnose --amp bf16             # round 2
  python run_pipeline.py --backbones qwen --preset round2_seeds --seeds 43,44 --diagnose    # round-2 E2E seeds
Finished stages are skipped when their checkpoint exists, so an interrupted Colab session can simply be re-run.
"""
import argparse
import os
import shutil

import evaluate
import prepare_data
import summarize
import synth_scp_data
import train_e2e
import train_scp
from nclara.utils import parse_int_list, parse_str_list

MAIN_RUNS = [
    {"name": "nested_M32", "scp": {"mode": "nested", "max_mem": 32, "nest_loss": "sample"}, "e2e": {}},
    # the proposed method: same nested compressor, budget split learned end to end
    {"name": "nested_M32__learned", "reuse_scp": "nested_M32",
     "e2e": {"train_alloc": "learned", "train_totals": "32,64"}},
    {"name": "fixed_M16", "scp": {"mode": "fixed", "max_mem": 16}, "e2e": {"train_alloc": "uniform"}},
]
# Round 2 (Qwen): give every prefix a training signal in every step and train longer, so that more memory vectors can
# carry more information; fixed-16 is retrained for the same 6 epochs so the comparison stays fair.
ROUND2_RUNS = [
    {"name": "r2_nested_M32_all_e6", "scp": {"mode": "nested", "max_mem": 32, "nest_loss": "all", "epochs": 6},
     "e2e": {}},
    {"name": "r2_nested_M32_all_e6__learned", "reuse_scp": "r2_nested_M32_all_e6",
     "e2e": {"train_alloc": "learned", "train_totals": "32,64"}},
    {"name": "r2_fixed_M16_e6", "scp": {"mode": "fixed", "max_mem": 16, "epochs": 6}, "e2e": {"train_alloc": "uniform"}},
]
# Extra seeds for round 2, end-to-end only: seeds 43 and 44 copy the seed-42 round-2 compressor and retrain only the
# query reasoner / generator (and budget head). Same run names as round 2, so the summary averages over seeds.
ROUND2_SEED_RUNS = [
    {"name": "r2_nested_M32_all_e6", "reuse_scp": "r2_nested_M32_all_e6", "reuse_scp_seed": 42, "e2e": {}},
    {"name": "r2_nested_M32_all_e6__learned", "reuse_scp": "r2_nested_M32_all_e6", "reuse_scp_seed": 42,
     "e2e": {"train_alloc": "learned", "train_totals": "32,64"}},
]
# Single-sample ablation: the budget head trained with ONE sampled split per question (moving-average baseline)
# instead of two (leave-one-out baseline), on the same final-configuration compressor (seed 42). Tests whether the
# gain from training with the budget head comes from averaging the answer loss over two splits per question.
ROUND2_S1_RUNS = [
    {"name": "r2_nested_M32_all_e6__learned_S1", "reuse_scp": "r2_nested_M32_all_e6", "reuse_scp_seed": 42,
     "e2e": {"train_alloc": "learned", "train_totals": "32,64", "budget_samples": 1}},
]
ABLATION_RUNS = [
    {"name": "nested_M32__learned_ent0", "reuse_scp": "nested_M32",
     "e2e": {"train_alloc": "learned", "train_totals": "32,64", "entropy_coef": 0.0}},
    {"name": "nested_M32__learned_S1", "reuse_scp": "nested_M32",
     "e2e": {"train_alloc": "learned", "train_totals": "32,64", "budget_samples": 1}},
    {"name": "nested_M32__learned_B64only", "reuse_scp": "nested_M32",
     "e2e": {"train_alloc": "learned", "train_totals": "64"}},
    {"name": "nested_M32_allprefix", "scp": {"mode": "nested", "max_mem": 32, "nest_loss": "all"}, "e2e": {}},
    {"name": "nested_M32_lam0", "scp": {"mode": "nested", "max_mem": 32, "lambda_mse": 0.0}, "e2e": {}},
    {"name": "nested_M32_lam1", "scp": {"mode": "nested", "max_mem": 32, "lambda_mse": 1.0}, "e2e": {}},
    # memory vectors rescaled to token-embedding norm before the generator reads them (decoder-only issue)
    {"name": "nested_M32_rescale", "scp": {"mode": "nested", "max_mem": 32, "rescale_memory": 1}, "e2e": {},
     "backbones": ["qwen"]},
    # E2E-only ablations reuse the main nested SCP checkpoint
    {"name": "nested_M32__e2e_uniform", "reuse_scp": "nested_M32", "e2e": {"train_alloc": "uniform"}},
    {"name": "nested_M32__e2e_r4", "reuse_scp": "nested_M32", "e2e": {"r_score": 4}},
    {"name": "nested_M32__e2e_tau0.1", "reuse_scp": "nested_M32", "e2e": {"tau": 0.1}},
]


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--backbones", default="qwen,t5")
    p.add_argument("--datasets", default="hotpotqa,2wiki")
    p.add_argument("--preset", choices=["main", "ablations", "round2", "round2_seeds", "round2_s1"], default="main")
    p.add_argument("--diagnose", action="store_true",
                   help="after each evaluation, also run the memory diagnostic (no / wrong / gold memory)")
    p.add_argument("--n_train", type=int, default=300)
    p.add_argument("--n_eval", type=int, default=100)
    p.add_argument("--synth_model", default="Qwen/Qwen2.5-14B-Instruct")
    p.add_argument("--max_scp_docs", type=int, default=800)
    p.add_argument("--scp_epochs", type=int, default=3)
    p.add_argument("--e2e_epochs", type=int, default=3)
    p.add_argument("--seeds", default="42", help="comma-separated; each seed trains and evaluates every run")
    p.add_argument("--data_seed", type=int, default=42, help="seed for sampling questions and synthesising data")
    p.add_argument("--amp", choices=["none", "bf16"], default="none", help="bf16 on L40S/A100; none on a T4")
    p.add_argument("--n_eval_used", type=int, default=None, help="evaluate on only the first N eval questions")
    p.add_argument("--only_data", action="store_true", help="prepare data + SCP synthesis, then stop")
    p.add_argument("--require_data", action="store_true",
                   help="fail if data/ is incomplete instead of creating it (data is built by scripts/01_prepare_data.sh)")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--tiny", action="store_true", help="toy data + tiny random models on CPU (smoke test)")
    return p


def call(module, argv):
    return module.main(module.build_parser().parse_args(argv))


def main(args):
    if args.tiny:
        args.n_train, args.n_eval, args.scp_epochs, args.e2e_epochs = 40, 12, 2, 2
        args.amp = "none"
        args.data_dir, args.runs_dir = "tiny_data", "tiny_runs"
    tiny = ["--tiny"] if args.tiny else []
    datasets = parse_str_list(args.datasets)

    if args.require_data and not args.tiny:
        needed = [os.path.join(args.data_dir, f"{d}_{part}.json") for d in datasets for part in ("train", "eval", "scp")]
        absent = [p for p in needed if not os.path.exists(p)]
        if absent:
            raise SystemExit(f"missing data files {absent}; run ./scripts/01_prepare_data.sh first")
    missing = [d for d in datasets if not os.path.exists(os.path.join(args.data_dir, f"{d}_eval.json"))]
    if missing:
        call(prepare_data, ["--datasets", ",".join(missing), "--n_train", str(args.n_train), "--n_eval",
                            str(args.n_eval), "--seed", str(args.data_seed), "--data_dir", args.data_dir] + tiny)
    missing = [d for d in datasets if not os.path.exists(os.path.join(args.data_dir, f"{d}_scp.json"))]
    if missing:
        call(synth_scp_data, ["--datasets", ",".join(missing), "--data_dir", args.data_dir, "--synth_model",
                              args.synth_model, "--max_docs", str(args.max_scp_docs), "--seed",
                              str(args.data_seed)] + tiny)
    if args.only_data:
        return

    amp = ["--amp", args.amp]
    runs = {"round2": ROUND2_RUNS, "round2_seeds": ROUND2_SEED_RUNS, "round2_s1": ROUND2_S1_RUNS}.get(
        args.preset, MAIN_RUNS + (ABLATION_RUNS if args.preset == "ablations" else []))
    for seed in parse_int_list(args.seeds):
        for bb in parse_str_list(args.backbones):
            for ds in datasets:
                for run in runs:
                    if bb not in run.get("backbones", [bb]):
                        continue
                    run_dir = os.path.join(args.runs_dir, bb, ds, f"{run['name']}_s{seed}")
                    scp_dir = os.path.join(run_dir, "scp")
                    print(f"\n######## seed {seed} | {bb} | {ds} | {run['name']}")
                    if not os.path.exists(os.path.join(scp_dir, "meta.json")):
                        if "reuse_scp" in run:
                            src_seed = run.get("reuse_scp_seed", seed)
                            src = os.path.join(args.runs_dir, bb, ds, f"{run['reuse_scp']}_s{src_seed}", "scp")
                            if not os.path.exists(os.path.join(src, "meta.json")):
                                raise SystemExit(f"{src} not found: run the run it reuses first")
                            shutil.copytree(src, scp_dir)
                        else:
                            argv = ["--backbone", bb, "--dataset", ds, "--data_dir", args.data_dir, "--run_dir",
                                    run_dir, "--epochs", str(args.scp_epochs), "--seed", str(seed)] + amp
                            for k, v in run["scp"].items():
                                argv += [f"--{k}", str(v)]
                            call(train_scp, argv + tiny)
                    if not os.path.exists(os.path.join(run_dir, "e2e", "meta.json")):
                        argv = ["--run_dir", run_dir, "--dataset", ds, "--data_dir", args.data_dir,
                                "--epochs", str(args.e2e_epochs), "--seed", str(seed)] + amp
                        for k, v in run["e2e"].items():
                            argv += [f"--{k}", str(v)]
                        call(train_e2e, argv + tiny)
                    if not os.path.exists(os.path.join(run_dir, "results", "eval.json")):
                        argv = ["--run_dir", run_dir, "--dataset", ds, "--data_dir", args.data_dir,
                                "--seed", str(seed)] + amp
                        if args.n_eval_used:
                            argv += ["--n_eval", str(args.n_eval_used)]
                        call(evaluate, argv + tiny)
                    if args.diagnose and not os.path.exists(os.path.join(run_dir, "results", "diagnose.json")):
                        import diagnose_memory
                        diagnose_memory.diagnose(run_dir, ds, args.data_dir, args.n_eval_used or 300,
                                                 "none" if args.tiny else args.amp, args.tiny)
    call(summarize, ["--runs_dir", args.runs_dir])


if __name__ == "__main__":
    main(build_parser().parse_args())
