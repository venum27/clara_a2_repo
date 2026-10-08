"""Stage 2 -- end-to-end retrieval + generation with rank-dependent memory budgets.

The compressor is frozen, so every candidate passage is compressed once and cached (max_mem vectors each). Per
training question:
  1. the query reasoner encodes the question; scores = cosine(first r query vectors, first r document vectors)
  2. straight-through top-k picks k documents (hard forward, softmax gradient backward)
  3. an allocation policy turns the total budget into per-slot prefix lengths (rank order)
  4. the generator reads [question ; prefix of doc 1 ; ... ; prefix of doc k] and is trained with NTP on the
     gold answer -- the only training signal; gradients reach the query reasoner through the ST estimator.

Budget allocation (--train_alloc):
  learned    the proposed method: a budget head chooses how the --total_budget vectors are split across the k
             documents, trained end to end from the answer loss (each question uses exactly the total)
  mixed      rule-based baselines: uniform and top_heavy sampled per step, so ONE model can be evaluated under both
  uniform / top_heavy / score   a single rule

    python train_e2e.py --run_dir runs/qwen/hotpotqa/nested_M32_s42 --dataset hotpotqa --train_alloc learned
"""
import argparse
import os
import random
import time

import torch
from tqdm import tqdm

from nclara.allocation import allocate
from nclara.budget import BudgetHead, head_features, save_head
from nclara.modeling import load_from_checkpoint
from nclara.utils import (all_gold_at_k, get_device, hit_at_k, parse_int_list, precision_context, read_json,
                          set_seed, write_json)

E2E_INSTRUCTION = ("Answer the question using the retrieved documents. Reply with a short answer only.\n"
                   "Question: {q}\nAnswer:")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run_dir", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--k", type=int, default=4, help="documents passed to the generator")
    p.add_argument("--total_budget", type=int, default=64, help="total memory vectors across the k documents")
    p.add_argument("--train_alloc", choices=["learned", "mixed", "uniform", "top_heavy", "score"], default="mixed")
    p.add_argument("--train_totals", default="",
                   help="learned: totals sampled per step, e.g. 32,64 (default: --total_budget only)")
    p.add_argument("--budget_samples", type=int, default=2,
                   help="learned: budget samples per question (leave-one-out baseline); 1 = moving-average baseline")
    p.add_argument("--budget_lr", type=float, default=1e-3, help="learned: learning rate of the budget head")
    p.add_argument("--entropy_coef", type=float, default=0.02, help="learned: entropy bonus against early collapse")
    p.add_argument("--r_score", type=int, default=16, help="prefix length used for retrieval scoring")
    p.add_argument("--tau", type=float, default=0.5, help="straight-through softmax temperature")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--amp", choices=["none", "bf16"], default="none",
                   help="bf16 autocast for forward passes (use on L40S/A100; not supported on a T4)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tiny", action="store_true")
    return p


def main(args):
    set_seed(args.seed)
    device = get_device()
    ac = precision_context(args.amp, device)
    model, meta = load_from_checkpoint(os.path.join(args.run_dir, "scp"), device=device, tiny=args.tiny)
    allowed = meta["prefix_set"]
    r = min(args.r_score, model.max_mem)
    learned = args.train_alloc == "learned"
    if learned and meta["mode"] == "fixed":
        raise SystemExit("learned budgets need a nested compressor (a fixed one has a single valid length)")
    policies = ["uniform", "top_heavy"] if args.train_alloc == "mixed" else [args.train_alloc]
    if meta["mode"] == "fixed":
        policies = ["uniform"]            # a fixed-length compressor only has one valid length
    if not learned:
        for pol in policies:
            allocate(pol, args.k, args.total_budget, allowed, scores=[0.0] * args.k)   # fail early if infeasible

    # Query reasoner starts as a copy of the trained compressor (paper; A1 did the same).
    n = model.copy_adapter("compressor", "query_reasoner")
    with torch.no_grad():
        model.mem_query.copy_(model.mem_doc)
    model.set_trainable(["query_reasoner", "generator"], mem_query=True)
    params = model.trainable_parameters()
    groups = [{"params": params, "lr": args.lr}]
    head, baseline = None, None
    if learned:
        head = BudgetHead(model.hidden_size, allowed, args.k).to(device)
        totals = parse_int_list(args.train_totals) if args.train_totals else [args.total_budget]
        for t in totals:
            head.patterns(args.k, t, device)                     # fail early if a total is infeasible
        groups.append({"params": list(head.parameters()), "lr": args.budget_lr})
        min_len = min(allowed)
    opt = torch.optim.AdamW(groups)
    clip_params = params + (list(head.parameters()) if head is not None else [])

    records = read_json(os.path.join(args.data_dir, f"{args.dataset}_train.json"))
    records = [rec for rec in records if len(rec["paragraphs"]) >= args.k]
    model.model.eval()
    cache = {}
    with torch.no_grad(), ac():
        for rec in tqdm(records, desc="caching compressed passages"):
            for ptxt in rec["paragraphs"]:
                if ptxt not in cache:
                    cache[ptxt] = model.compress(ptxt, "compressor")[0].detach()
    before = model.lora_snapshot()
    print(f"[E2E] {len(records)} questions | {len(cache)} cached passages | copied {n} tensors "
          f"compressor->query_reasoner | k={args.k} | r={r} | " +
          (f"learned budgets, totals {totals}, lengths {allowed}" if learned
           else f"budget={args.total_budget} policies={policies}"))

    rng = random.Random(args.seed)
    log = {"args": vars(args), "epochs": []}
    model.model.train()
    t0 = time.time()
    for epoch in range(args.epochs):
        rng.shuffle(records)
        hits, full, losses = 0, 0, []                     # reset every epoch (A1's counter was cumulative)
        gold_b, other_b, ents, top_share = [], [], [], []
        for rec in tqdm(records, desc=f"E2E epoch {epoch + 1}/{args.epochs}"):
            instr = E2E_INSTRUCTION.format(q=rec["question"])
            with ac():
                cands = [cache[ptxt] for ptxt in rec["paragraphs"]]
                q, _ = model.compress(rec["question"], "query_reasoner", is_query=True)
                scores = model.score(q, cands, r)
                Z = model.st_topk(scores, args.k, args.tau)
                chosen = Z.detach().argmax(dim=1).tolist()
                if not learned:
                    policy = rng.choice(policies)
                    budgets = allocate(policy, args.k, args.total_budget, allowed,
                                       scores=scores.detach()[chosen].tolist())
                    loss = model.gen_loss(instr, model.gather_slots(Z, cands, budgets), rec["answer"])
                    ntp = loss
                else:
                    logits = head(*head_features(q, cands, chosen, scores, r, min_len))
                    total = rng.choice(totals)
                    sample_losses, logps = [], []
                    for _ in range(args.budget_samples):
                        budgets, logp, ent = head.choose(logits, total)
                        sample_losses.append(model.gen_loss(instr, model.gather_slots(Z, cands, budgets),
                                                            rec["answer"]))
                        logps.append(logp)
                        for c, b in zip(chosen, budgets):
                            (gold_b if c in rec["gold_idx"] else other_b).append(b)
                        top_share.append(budgets[0] / total)
                    ntp = torch.stack(sample_losses).mean()
                    L = torch.stack([x.detach().float() for x in sample_losses])
                    if args.budget_samples > 1:        # leave-one-out baseline: better than the others -> reinforce
                        adv = (L.sum() - L) / (len(L) - 1) - L
                    else:                              # moving-average baseline
                        baseline = L.mean().item() if baseline is None else 0.9 * baseline + 0.1 * L.mean().item()
                        adv = baseline - L
                    policy_loss = -(adv * torch.stack(logps)).mean()
                    loss = ntp + policy_loss - args.entropy_coef * ent
                    ents.append(ent.item())
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(clip_params, 1.0)
            opt.step()
            losses.append(ntp.item())
            hits += hit_at_k(chosen, rec["gold_idx"], args.k)
            full += all_gold_at_k(chosen, rec["gold_idx"], args.k)
        ep = {"epoch": epoch + 1, "loss": sum(losses) / len(losses),
              "train_hit@k": 100 * hits / len(records), "train_all_gold@k": 100 * full / len(records)}
        if learned:
            mean = lambda v: sum(v) / len(v) if v else float("nan")
            ep.update({"split_entropy": mean(ents), "top1_share_of_budget": mean(top_share),
                       "avg_budget_gold_docs": mean(gold_b), "avg_budget_other_docs": mean(other_b)})
        log["epochs"].append(ep)
        print(f"  epoch {epoch + 1}: loss {ep['loss']:.3f} | train hit@{args.k} {ep['train_hit@k']:.1f}% | "
              f"all-gold@{args.k} {ep['train_all_gold@k']:.1f}%" +
              (f" | rank-1 share {ep['top1_share_of_budget']:.2f} | split entropy {ep['split_entropy']:.2f}"
               f" | budget gold {ep['avg_budget_gold_docs']:.1f} vs other {ep['avg_budget_other_docs']:.1f}"
               if learned else ""))

    log["minutes"] = (time.time() - t0) / 60
    log["delta_vs_start"] = model.delta_report(before)
    out = os.path.join(args.run_dir, "e2e")
    model.save(out, extra_meta={**{k: v for k, v in meta.items() if k not in model.meta()},
                                "stage": "e2e", "k": args.k, "total_budget": args.total_budget,
                                "train_alloc": args.train_alloc, "r_score": r, "tau": args.tau,
                                "train_totals": totals if learned else None,
                                "budget_samples": args.budget_samples if learned else None,
                                "entropy_coef": args.entropy_coef if learned else None})
    if learned:
        save_head(head, os.path.join(out, "budget_head.pt"))
    write_json(log, os.path.join(out, "train_log.json"))
    d = log["delta_vs_start"]
    print(f"  compressor changed {d['compressor']['changed']}/{d['compressor']['tensors']} (expect 0) | "
          f"query_reasoner {d['query_reasoner']['changed']}/{d['query_reasoner']['tensors']} | "
          f"generator {d['generator']['changed']}/{d['generator']['tensors']}")
    print(f"  saved -> {out}")


if __name__ == "__main__":
    main(build_parser().parse_args())
