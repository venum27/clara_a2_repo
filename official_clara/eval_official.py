"""Evaluate a model trained with the OFFICIAL CLaRa code on this project's evaluation questions, with this
project's metrics, and write results in this project's format so summarize.py puts them in the same tables.

Runs inside the official environment (official_clara/.venv). Answers come from the official
`generate_from_questions` (its own straight-through top-k, prompts and greedy decoding). The full ranking of the ten
candidates, needed for hit@5 and the random/BM25 comparison, is computed with the official model's own compressor,
query reasoner and cosine scoring, exactly as inside that function.

    python official_clara/eval_official.py --ckpt official_clara/runs/hotpotqa_CR16/stage2 --dataset hotpotqa \\
        --compress_rate 16 --run_dir runs/qwen/hotpotqa/clara_official_CR16_s42
"""
import argparse
import collections
import os
import sys

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))                       # this project (nclara, evaluate)
sys.path.insert(0, os.path.join(HERE, "ml-clara"))              # the official code

from nclara.utils import (all_gold_at_k, bootstrap_ci, clean_prediction, exact_match, f1_score,  # noqa: E402
                          hit_at_k, random_all_gold_at_k, random_hit_at_k, read_json, write_json)


def gold_rank_bucket(top, gold_idx):
    for pos, i in enumerate(top):
        if i in gold_idx:
            return "rank 1" if pos == 0 else ("rank 2" if pos == 1 else "rank 3+")
    return "not retrieved"


@torch.no_grad()
def full_ranking(model, questions, documents):
    """The official scoring (query reasoner vs. compressed documents, cosine over flattened memory), all candidates."""
    q_tok = model._prepare_encoder_inputs(questions, max_length=model.doc_max_length)
    model.decoder.set_adapter("query_reasoner_adapter")
    q = model._compr_query_reasoner_stage2(q_tok["input_ids"].to(model.decoder.device),
                                           q_tok["attention_mask"].to(model.decoder.device))
    d_tok = model._prepare_encoder_inputs(sum(documents, []), max_length=model.doc_max_length)
    d, _ = model.compress(d_tok["input_ids"].to(model.decoder.device), d_tok["attention_mask"].to(model.decoder.device))
    d = d.reshape(len(questions), len(documents[0]), -1)
    scores = torch.bmm(F.normalize(q.to(d.dtype), dim=-1).unsqueeze(1).float(),
                       F.normalize(d, dim=-1).float().transpose(1, 2)).squeeze(1)
    return scores.argsort(dim=-1, descending=True).tolist()


def main(args):
    from openrlhf.models.modeling_clara import CLaRa
    records = read_json(os.path.join(args.data_dir, f"{args.dataset}_{args.eval_name}.json"))[: args.n_eval]
    model = CLaRa.from_pretrained(args.ckpt, training_stage="stage2", generation_top_k=args.k,
                                  doc_max_length=args.doc_max_length, compress_rate=args.compress_rate)
    model = model.to("cuda").to(torch.bfloat16).eval()
    n_mem = args.doc_max_length // args.compress_rate
    print(f"official CLaRa from {args.ckpt}: {n_mem} memory vectors per document, top-{args.k} "
          f"-> {n_mem * args.k} vectors per question")

    groups = collections.defaultdict(list)                     # batch questions with the same number of candidates
    for i, rec in enumerate(records):
        groups[len(rec["paragraphs"])].append(i)
    preds, topks, ranks = [None] * len(records), [None] * len(records), [None] * len(records)
    for n, idx in groups.items():
        if n < args.k:
            continue
        for s in tqdm(range(0, len(idx), args.batch_size), desc=f"eval ({n} candidates)"):
            b = idx[s: s + args.batch_size]
            qs = [records[i]["question"] for i in b]
            docs = [records[i]["paragraphs"] for i in b]
            out, topk = model.generate_from_questions(questions=qs, documents=docs,
                                                      max_new_tokens=args.max_new_tokens, stage2_mips=False)
            full = full_ranking(model, qs, docs)
            for j, i in enumerate(b):
                preds[i], topks[i], ranks[i] = clean_prediction(out[j]), topk[j].tolist(), full[j]
    keep = [i for i in range(len(records)) if preds[i] is not None]
    recs = [records[i] for i in keep]
    golds = [r["answer"] for r in recs]
    em = [exact_match(preds[i], g) for i, g in zip(keep, golds)]
    f1 = [f1_score(preds[i], g) for i, g in zip(keep, golds)]
    buckets = [gold_rank_bucket(topks[i], r["gold_idx"]) for i, r in zip(keep, recs)]
    by = collections.defaultdict(list)
    for bkt, v in zip(buckets, f1):
        by[bkt].append(v)
    key = f"uniform@{n_mem * args.k}"                          # official CLaRa gives every document the same budget
    qa = {"results": {key: {"EM": bootstrap_ci(em), "F1": bootstrap_ci(f1), "n": len(em),
                            "budgets": [float(n_mem)] * args.k, "context_vectors": float(n_mem * args.k),
                            "F1_by_gold_rank": {k: {"mean": 100 * float(np.mean(v)), "n": len(v)}
                                                for k, v in by.items()}}},
          "paired_tests": {}, "gold_rank_counts": {b: buckets.count(b) for b in sorted(set(buckets))}}
    ks = [1, 2, 3, 5]
    row = {}
    for k in ks:
        row[f"hit@{k}"] = bootstrap_ci([hit_at_k(ranks[i], r["gold_idx"], k) for i, r in zip(keep, recs)])
        row[f"all_gold@{k}"] = bootstrap_ci([all_gold_at_k(ranks[i], r["gold_idx"], k) for i, r in zip(keep, recs)])
    agree = float(np.mean([ranks[i][: args.k] == topks[i] for i in keep]))
    retrieval = {
        "query reasoner (after E2E)": row,
        "random (expected)": {
            **{f"hit@{k}": {"mean": 100 * float(np.mean([random_hit_at_k(len(r["paragraphs"]), len(r["gold_idx"]), k)
                                                          for r in recs]))} for k in ks},
            **{f"all_gold@{k}": {"mean": 100 * float(np.mean([random_all_gold_at_k(len(r["paragraphs"]),
                                                                                     len(r["gold_idx"]), k)
                                                               for r in recs]))} for k in ks}}}
    res = {"qa": qa, "retrieval": retrieval,
           "meta": {"run_dir": args.run_dir, "dataset": args.dataset, "n_eval": len(recs), "k": args.k,
                    "implementation": "official CLaRa code (apple/ml-clara), patched for environment only",
                    "checkpoint": args.ckpt, "memory_vectors_per_doc": n_mem,
                    "ranking_matches_official_topk": agree}}
    out_dir = os.path.join(args.run_dir, args.out_name)
    write_json(res, os.path.join(out_dir, "eval.json"))
    write_json([{"id": r["id"], "question": r["question"], "gold": r["answer"], "pred": preds[i], "topk": topks[i],
                 "gold_idx": r["gold_idx"]} for i, r in zip(keep, recs)], os.path.join(out_dir, "qa_predictions.json"))
    with open(os.path.join(out_dir, "summary.md"), "w") as f:
        f.write(f"# Official CLaRa baseline\n\nCheckpoint `{args.ckpt}`, {len(recs)} questions, {n_mem} vectors per "
                f"document, top-{args.k}.\n\n| EM | F1 | hit@1 | hit@3 | hit@5 | all-gold@2 |\n|---|---|---|---|---|---|\n"
                f"| {100 * np.mean(em):.1f} | {100 * np.mean(f1):.1f} | {row['hit@1']['mean']:.1f} | "
                f"{row['hit@3']['mean']:.1f} | {row['hit@5']['mean']:.1f} | {row['all_gold@2']['mean']:.1f} |\n\n"
                f"Recomputed ranking agrees with the official top-{args.k} on {100 * agree:.0f}% of questions.\n")
    print(f"EM {100 * np.mean(em):.1f} | F1 {100 * np.mean(f1):.1f} | hit@1 {row['hit@1']['mean']:.1f} | "
          f"ranking agreement {100 * agree:.0f}% -> {out_dir}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ckpt", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--run_dir", required=True)
    p.add_argument("--compress_rate", type=int, default=16)
    p.add_argument("--eval_name", default="eval", help="evaluation file: data/<dataset>_<eval_name>.json")
    p.add_argument("--out_name", default="results", help="results folder inside the run")
    p.add_argument("--doc_max_length", type=int, default=256)
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--n_eval", type=int, default=None)
    p.add_argument("--batch_size", type=int, default=8)
    p.add_argument("--max_new_tokens", type=int, default=24)
    main(p.parse_args())
