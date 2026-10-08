"""Stage 1 -- (nested) Salient Compressor Pretraining.

For every passage the compressor produces `max_mem` memory vectors ONCE; the generator is then trained to answer
each synthetic question (and to write the paraphrase) from only a PREFIX M[:m] of them:

  --mode nested --nest_loss sample : one random m from --prefix_set per example (nested dropout)
  --mode nested --nest_loss all    : every m in --prefix_set per example, losses averaged (Matryoshka style)
  --mode fixed                     : always all max_mem vectors (original CLaRa SCP; the baseline)

Loss per (example, m):  NTP(target | question, M[:m])  +  lambda * || mean(M[:m]) - mean(h_doc) ||^2

    python train_scp.py --backbone qwen --dataset hotpotqa --mode nested --max_mem 32
    python train_scp.py --backbone qwen --dataset hotpotqa --mode fixed  --max_mem 16
"""
import argparse
import collections
import os
import random
import time

import torch
import torch.nn.functional as F
from tqdm import tqdm

from nclara.modeling import load_model
from nclara.utils import get_device, parse_int_list, precision_context, read_json, set_seed, write_json

QA_INSTRUCTION = "Answer the question based on the document. Reply with a short answer only.\nQuestion: {q}\nAnswer:"
PARA_INSTRUCTION = "Rewrite the document in your own words."


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--backbone", choices=["qwen", "t5"], required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--run_dir", default=None, help="default: runs/<backbone>/<dataset>/<mode>_M<max_mem>...")
    p.add_argument("--mode", choices=["nested", "fixed"], default="nested")
    p.add_argument("--max_mem", type=int, default=32)
    p.add_argument("--prefix_set", default="4,8,16,32")
    p.add_argument("--nest_loss", choices=["sample", "all"], default="sample")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--lambda_mse", type=float, default=0.1)
    p.add_argument("--mse_detach_doc", type=int, default=1,
                   help="1: treat mean(h_doc) as a fixed target (stop-gradient); 0: gradients flow into both sides")
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--max_doc_tokens", type=int, default=256)
    p.add_argument("--max_paraphrase_chars", type=int, default=400)
    p.add_argument("--rescale_memory", type=int, default=0,
                   help="Qwen only: rescale memory vectors to token-embedding norm before the generator reads them")
    p.add_argument("--amp", choices=["none", "bf16"], default="none",
                   help="bf16 autocast for forward passes (use on L40S/A100; not supported on a T4)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tiny", action="store_true")
    return p


def default_run_dir(args):
    tag = f"{args.mode}_M{args.max_mem}" + (f"_{args.nest_loss}" if args.mode == "nested" else "")
    tag += f"_lam{args.lambda_mse:g}" + ("_rescale" if args.rescale_memory else "") + f"_s{args.seed}"
    return os.path.join("runs", args.backbone, args.dataset, tag)


def examples_for(doc_rec, max_para_chars):
    ex = [(QA_INSTRUCTION.format(q=qa["question"]), qa["answer"], "qa")
          for qa in doc_rec.get("simple_qa", []) + doc_rec.get("complex_qa", [])]
    if doc_rec.get("paraphrase"):
        ex.append((PARA_INSTRUCTION, doc_rec["paraphrase"][:max_para_chars], "para"))
    return ex


def main(args):
    set_seed(args.seed)
    device = get_device()
    ac = precision_context(args.amp, device)
    run_dir = args.run_dir or default_run_dir(args)
    prefix_set = [args.max_mem] if args.mode == "fixed" else sorted(parse_int_list(args.prefix_set))
    assert max(prefix_set) <= args.max_mem, "prefix lengths cannot exceed max_mem"

    docs = [d for d in read_json(os.path.join(args.data_dir, f"{args.dataset}_scp.json")) if d["split"] == "train"]
    model = load_model(args.backbone, max_mem=args.max_mem, lora_r=args.lora_r, device=device, tiny=args.tiny,
                       max_doc_tokens=args.max_doc_tokens, rescale_memory=bool(args.rescale_memory))
    model.set_trainable(["compressor", "generator"], mem_doc=True)
    params = model.trainable_parameters()
    opt = torch.optim.AdamW(params, lr=args.lr)
    before = model.lora_snapshot()
    print(f"[SCP {args.mode}] {args.backbone}/{args.dataset}: {len(docs)} passages | prefixes {prefix_set} | "
          f"trainable params {sum(p.numel() for p in params):,} | device {device}")

    rng = random.Random(args.seed)
    log = {"args": vars(args), "prefix_set": prefix_set, "epochs": []}
    model.model.train()
    t0 = time.time()
    for epoch in range(args.epochs):
        rng.shuffle(docs)
        ce_by_m = collections.defaultdict(list)
        mse_all, steps = [], 0
        for d in tqdm(docs, desc=f"SCP epoch {epoch + 1}/{args.epochs}"):
            exs = examples_for(d, args.max_paraphrase_chars)
            if not exs:
                continue
            # one (example, prefix) term at a time: each term is backpropagated as soon as it is computed, so only one
            # generator graph is in memory at once; the shared compressor graph is kept until the last term.
            # Gradients are identical to averaging all terms and calling backward once.
            jobs = [(instr, tgt, m) for instr, tgt, _kind in exs
                    for m in (prefix_set if args.nest_loss == "all" else [rng.choice(prefix_set)])]
            opt.zero_grad(set_to_none=True)
            with ac():
                M, doc_h = model.compress(d["document"], "compressor")
                target_mean = doc_h.mean(0).detach() if args.mse_detach_doc else doc_h.mean(0)
            for j, (instr, tgt, m) in enumerate(jobs):
                with ac():
                    ce = model.gen_loss(instr, [M[:m]], tgt)
                    mse = F.mse_loss(M[:m].mean(0), target_mean)
                    term = (ce + args.lambda_mse * mse) / len(jobs)
                term.backward(retain_graph=j < len(jobs) - 1)
                ce_by_m[m].append(ce.item())
                mse_all.append(mse.item())
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            steps += 1
        ep = {"epoch": epoch + 1, "steps": steps,
              "ce_by_prefix": {m: sum(v) / len(v) for m, v in sorted(ce_by_m.items())},
              "mse": sum(mse_all) / max(len(mse_all), 1)}
        log["epochs"].append(ep)
        print(f"  epoch {epoch + 1}: CE by prefix " +
              " ".join(f"m={m}:{v:.3f}" for m, v in ep["ce_by_prefix"].items()) + f" | MSE {ep['mse']:.4f}")

    log["minutes"] = (time.time() - t0) / 60
    log["delta_vs_start"] = model.delta_report(before)
    out = os.path.join(run_dir, "scp")
    model.save(out, extra_meta={"stage": "scp", "mode": args.mode, "prefix_set": prefix_set,
                                "nest_loss": args.nest_loss, "lambda_mse": args.lambda_mse,
                                "dataset": args.dataset, "seed": args.seed})
    write_json(log, os.path.join(out, "train_log.json"))
    print(f"  adapter changes since start: " +
          ", ".join(f"{a} {r['changed']}/{r['tensors']}" for a, r in log["delta_vs_start"].items()))
    print(f"  saved -> {out}")
    return run_dir


if __name__ == "__main__":
    main(build_parser().parse_args())
