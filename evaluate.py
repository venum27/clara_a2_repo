"""Evaluate a run: every table needed for the Assignment 2 report.

Sections (--sections, comma separated):
  params     parameter counts per adapter and compression rate for each prefix length
  scp_curve  compressor-only QA on HELD-OUT synthetic questions vs prefix length (does nesting work?). For a fixed
             model, lengths below max_mem are truncations it was never trained on (the 'truncate the original' test).
  oracle     generator given only the gold passages, each cut to m vectors, vs a raw-text reader of the same passages
  retrieval  hit@k and all-gold@k: BM25, random (exact expectation), query reasoner before and after E2E training
  qa         end-to-end EM/F1 for the learned budget head and every rule-based policy x total budget, the raw-text
             BM25 baseline, paired bootstrap tests at equal budget, results by the rank of the answer document, and
             how the learned head spends its budget (by rank, gold vs other documents)

    python evaluate.py --run_dir runs/qwen/hotpotqa/nested_M32_sample_lam0.1_s42 --dataset hotpotqa
"""
import argparse
import collections
import os

import numpy as np
import torch
from tqdm import tqdm

from nclara.allocation import allocate
from nclara.budget import head_features, load_head
from nclara.modeling import load_from_checkpoint
from nclara.utils import (all_gold_at_k, bootstrap_ci, exact_match, f1_score, get_device, hit_at_k,
                          paired_bootstrap, parse_int_list, parse_str_list, precision_context,
                          random_all_gold_at_k,
                          random_hit_at_k, read_json, set_seed, write_json)
from train_e2e import E2E_INSTRUCTION
from train_scp import QA_INSTRUCTION

RAW_PROMPT = ("Answer the question using the context. Reply with a short answer only.\n"
              "Context: {ctx}\nQuestion: {q}\nAnswer:")


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run_dir", required=True)
    p.add_argument("--dataset", required=True)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--sections", default="params,scp_curve,oracle,retrieval,qa")
    p.add_argument("--prefixes", default="4,8,16,32", help="prefix lengths for curves (capped at max_mem)")
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--totals", default="16,32,64,128")
    p.add_argument("--policies", default="uniform,top_heavy,score")
    p.add_argument("--retrieval_ks", default="1,2,3,5")
    p.add_argument("--n_eval", type=int, default=None)
    p.add_argument("--max_new_tokens", type=int, default=24)
    p.add_argument("--amp", choices=["none", "bf16"], default="none",
                   help="bf16 autocast for forward passes (use on L40S/A100; not supported on a T4)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eval_name", default="eval", help="evaluation file: data/<dataset>_<eval_name>.json")
    p.add_argument("--no_raw", action="store_true", help="skip the raw-text reader in the QA section")
    p.add_argument("--out_name", default="results",
                   help="results folder inside the run (e.g. results_k8 for a breadth test, so results/ is kept)")
    p.add_argument("--tiny", action="store_true")
    return p


def qa_scores(preds, golds):
    em = [exact_match(p, g) for p, g in zip(preds, golds)]
    f1 = [f1_score(p, g) for p, g in zip(preds, golds)]
    return em, f1


def summarise(em, f1):
    return {"EM": bootstrap_ci(em), "F1": bootstrap_ci(f1), "n": len(em)}


def fmt(ci):
    return f"{ci['mean']:.1f} [{ci['lo']:.1f}, {ci['hi']:.1f}]"


def bm25_rank(question, paragraphs):
    from rank_bm25 import BM25Okapi
    bm = BM25Okapi([p.lower().split() for p in paragraphs])
    return list(np.argsort(-bm.get_scores(question.lower().split())))


# ---------------------------------------------------------------------------------------------- sections
def section_params(model, records, prefixes):
    lengths = [model.n_tokens(p) for rec in records for p in rec["paragraphs"]]
    avg = float(np.mean(lengths))
    return {**model.param_counts(), "avg_passage_tokens": avg,
            "compression_rate_by_prefix": {m: avg / m for m in prefixes}}


@torch.no_grad()
def section_scp_curve(model, docs, prefixes, max_new):
    model.model.eval()
    preds, golds = collections.defaultdict(list), []
    for d in tqdm(docs, desc="scp_curve"):
        qas = d.get("simple_qa", []) + d.get("complex_qa", [])
        if not qas:
            continue
        M, _ = model.compress(d["document"], "compressor")
        for qa in qas:
            golds.append(qa["answer"])
            for m in prefixes:
                preds[m].append(model.generate(QA_INSTRUCTION.format(q=qa["question"]), [M[:m]], max_new))
    return {m: summarise(*qa_scores(preds[m], golds)) for m in prefixes}


@torch.no_grad()
def section_oracle(model, records, cache, prefixes, max_new):
    model.model.eval()
    preds, raw_preds, raw_tokens, golds = collections.defaultdict(list), [], [], []
    for rec in tqdm(records, desc="oracle"):
        gold_txt = [rec["paragraphs"][i] for i in rec["gold_idx"]]
        golds.append(rec["answer"])
        for m in prefixes:
            preds[m].append(model.generate(E2E_INSTRUCTION.format(q=rec["question"]),
                                           [cache[t][:m] for t in gold_txt], max_new))
        pred, n_tok = model.generate_raw(RAW_PROMPT.format(ctx=" ".join(gold_txt), q=rec["question"]), max_new)
        raw_preds.append(pred)
        raw_tokens.append(sum(model.n_tokens(t) for t in gold_txt))
    out = {f"compressed_m{m}": {**summarise(*qa_scores(preds[m], golds)),
                                "context_vectors": m * float(np.mean([len(r["gold_idx"]) for r in records]))}
           for m in prefixes}
    out["raw_text_gold"] = {**summarise(*qa_scores(raw_preds, golds)), "context_tokens": float(np.mean(raw_tokens))}
    return out


@torch.no_grad()
def reasoner_rankings(model, records, cache, r, return_queries=False):
    model.model.eval()
    ranks, scores, queries = [], [], []
    for rec in records:
        q, _ = model.compress(rec["question"], "query_reasoner", is_query=True)
        s = model.score(q, [cache[t] for t in rec["paragraphs"]], r)
        ranks.append(s.argsort(descending=True).tolist())
        scores.append(s.tolist())
        queries.append(q.detach())
    return (ranks, scores, queries) if return_queries else (ranks, scores)


def retrieval_table(rankings, records, ks):
    table = {}
    for name, ranks in rankings.items():
        row = {}
        for k in ks:
            row[f"hit@{k}"] = bootstrap_ci([hit_at_k(rk, rec["gold_idx"], k) for rk, rec in zip(ranks, records)])
            row[f"all_gold@{k}"] = bootstrap_ci([all_gold_at_k(rk, rec["gold_idx"], k)
                                                 for rk, rec in zip(ranks, records)])
        by_type = collections.defaultdict(list)
        for rk, rec in zip(ranks, records):
            by_type[rec.get("type", "unknown")].append(hit_at_k(rk, rec["gold_idx"], 1))
        row["hit@1_by_type"] = {t: {"mean": 100 * float(np.mean(v)), "n": len(v)} for t, v in by_type.items()}
        table[name] = row
    table["random (expected)"] = {
        **{f"hit@{k}": {"mean": 100 * float(np.mean([random_hit_at_k(len(r["paragraphs"]), len(r["gold_idx"]), k)
                                                      for r in records]))} for k in ks},
        **{f"all_gold@{k}": {"mean": 100 * float(np.mean([random_all_gold_at_k(len(r["paragraphs"]),
                                                                                 len(r["gold_idx"]), k)
                                                           for r in records]))} for k in ks}}
    return table


def gold_rank_bucket(top, gold_idx):
    for pos, i in enumerate(top):
        if i in gold_idx:
            return "rank 1" if pos == 0 else ("rank 2" if pos == 1 else "rank 3+")
    return "not retrieved"


@torch.no_grad()
def section_qa(model, records, cache, ranks, scores, k, totals, policies, allowed, max_new,
               head=None, queries=None, r=16, raw=True):
    model.model.eval()
    golds = [rec["answer"] for rec in records]
    preds = collections.defaultdict(list)
    budgets_used = collections.defaultdict(list)          # per key: the split used for each question
    per_example, buckets = [], []
    gold_budget, other_budget = collections.defaultdict(list), collections.defaultdict(list)
    for n_ex, (rec, rk, sc) in enumerate(tqdm(list(zip(records, ranks, scores)), desc="qa")):
        top = rk[:k]
        cands = [cache[rec["paragraphs"][i]] for i in top]
        buckets.append(gold_rank_bucket(top, rec["gold_idx"]))
        memo, ex = {}, {"id": rec["id"], "question": rec["question"], "gold": rec["answer"], "topk": top,
                        "gold_idx": rec["gold_idx"], "gold_rank": buckets[-1], "preds": {}, "budgets": {}}
        splits = {}
        for total in totals:
            for pol in policies:
                try:
                    splits[f"{pol}@{total}"] = tuple(allocate(pol, k, total, allowed, scores=[sc[i] for i in top]))
                except ValueError:
                    pass
            if head is not None:
                try:
                    logits = head(*head_features(queries[n_ex], [cache[rec["paragraphs"][i]] for i in top],
                                                 list(range(k)), torch.tensor([sc[i] for i in top]).to(model.device),
                                                 r, min(allowed)))
                    b, _, _ = head.choose(logits, total, greedy=True)
                    splits[f"learned@{total}"] = tuple(b)
                    for i, bi in zip(top, b):
                        (gold_budget if i in rec["gold_idx"] else other_budget)[total].append(bi)
                except ValueError:
                    pass
        for key, b in splits.items():
            if b not in memo:
                memo[b] = model.generate(E2E_INSTRUCTION.format(q=rec["question"]),
                                         [c[:bi] for c, bi in zip(cands, b)], max_new)
            preds[key].append(memo[b])
            budgets_used[key].append(list(b))
            ex["preds"][key], ex["budgets"][key] = memo[b], list(b)
        if raw:
            bm = bm25_rank(rec["question"], rec["paragraphs"])[:k]
            ctx = " ".join(rec["paragraphs"][i] for i in bm)
            pred, n_prompt = model.generate_raw(RAW_PROMPT.format(ctx=ctx, q=rec["question"]), max_new)
            preds["raw_bm25"].append(pred)
            ex["preds"]["raw_bm25"] = pred
            ex["raw_context_tokens"] = sum(model.n_tokens(rec["paragraphs"][i]) for i in bm)
        per_example.append(ex)

    results = {}
    for key, pr in preds.items():
        em, f1 = qa_scores(pr, golds)
        results[key] = {**summarise(em, f1), "_em": em, "_f1": f1}
        if key in budgets_used:
            per_slot = np.mean(np.array(budgets_used[key], dtype=float), axis=0)
            results[key]["budgets"] = [round(float(x), 1) for x in per_slot]      # mean vectors per rank slot
            results[key]["context_vectors"] = round(float(per_slot.sum()), 1)
        by = collections.defaultdict(list)
        for bucket, v in zip(buckets, f1):
            by[bucket].append(v)
        results[key]["F1_by_gold_rank"] = {b: {"mean": 100 * float(np.mean(v)), "n": len(v)} for b, v in by.items()}
    if raw:
        results["raw_bm25"]["context_tokens"] = float(np.mean([e["raw_context_tokens"] for e in per_example]))

    tests = {}
    for total in totals:
        pairs = [(f"{pol}@{total}", f"uniform@{total}") for pol in policies if pol != "uniform"]
        pairs += [(f"learned@{total}", f"uniform@{total}"), (f"learned@{total}", f"top_heavy@{total}")]
        for key, base in pairs:
            if key not in results or base not in results:
                continue
            if budgets_used[key] == budgets_used[base] and not key.startswith("learned"):
                continue                      # identical rule-based splits on every question; nothing to test
            tests[f"{key} vs {base}"] = {"EM": paired_bootstrap(results[key]["_em"], results[base]["_em"]),
                                         "F1": paired_bootstrap(results[key]["_f1"], results[base]["_f1"])}
    for v in results.values():
        v.pop("_em", None)
        v.pop("_f1", None)
    learned_budgets = {t: {"avg_vectors_gold_docs": float(np.mean(gold_budget[t])) if gold_budget[t] else None,
                           "avg_vectors_other_docs": float(np.mean(other_budget[t])) if other_budget[t] else None,
                           "avg_vectors_by_rank": results.get(f"learned@{t}", {}).get("budgets")}
                       for t in totals if f"learned@{t}" in results}
    return {"results": results, "paired_tests": tests, "learned_budgets": learned_budgets,
            "gold_rank_counts": {b: buckets.count(b) for b in sorted(set(buckets))}}, per_example


# ---------------------------------------------------------------------------------------------- report
def write_summary(res, path, run_dir):
    L = [f"# Evaluation summary\n\nRun: `{run_dir}`\n",
         "All scores in %, with 95% bootstrap confidence intervals in brackets.\n"]
    if "params" in res:
        p = res["params"]
        L += ["## Parameters and compression\n",
              f"- Backbone: {p['model_name']} ({p['architecture']}), base parameters: {p['base_params']:,}",
              f"- LoRA parameters per adapter: {p['lora_params_per_adapter']}",
              f"- Memory-embedding parameters: {p['memory_embedding_params']:,}",
              f"- Average passage length: {p['avg_passage_tokens']:.1f} tokens; compression rate by prefix: " +
              ", ".join(f"m={m}: {v:.1f}x" for m, v in p["compression_rate_by_prefix"].items()) + "\n"]
    if "scp_curve" in res:
        L += ["## Compressor-only QA on held-out synthetic questions (SCP checkpoint)\n",
              "| Prefix m | EM | F1 | n |", "|---|---|---|---|"]
        L += [f"| {m} | {fmt(v['EM'])} | {fmt(v['F1'])} | {v['n']} |" for m, v in res["scp_curve"].items()]
        L.append("")
    if "oracle" in res:
        L += ["## Oracle: gold passages only\n", "| Input | EM | F1 | Context size |", "|---|---|---|---|"]
        for k, v in res["oracle"].items():
            size = f"{v['context_tokens']:.0f} tokens" if "context_tokens" in v else f"{v['context_vectors']:.0f} vectors"
            L.append(f"| {k} | {fmt(v['EM'])} | {fmt(v['F1'])} | {size} |")
        L.append("")
    if "retrieval" in res:
        ks = sorted({int(c.split("@")[1]) for c in next(iter(res["retrieval"].values())) if "@" in c and "by_type" not in c})
        cols = [f"hit@{k}" for k in ks] + [f"all_gold@{k}" for k in ks]
        L += ["## Retrieval\n", "| Method | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
        for name, row in res["retrieval"].items():
            L.append(f"| {name} | " + " | ".join(f"{row[c]['mean']:.1f}" for c in cols) + " |")
        L.append("")
    if "qa" in res:
        L += ["## End-to-end QA\n", "| Setting | Budgets | Context | EM | F1 |", "|---|---|---|---|---|"]
        for key, v in res["qa"]["results"].items():
            size = f"{v['context_vectors']} vectors" if "context_vectors" in v else f"{v.get('context_tokens', 0):.0f} tokens"
            L.append(f"| {key} | {v.get('budgets', '-')} | {size} | {fmt(v['EM'])} | {fmt(v['F1'])} |")
        lb = res["qa"].get("learned_budgets") or {}
        if lb:
            L += ["\nHow the learned head spends its budget (mean vectors per document):\n",
                  "| Total | By rank slot | Gold documents | Other documents |", "|---|---|---|---|"]
            for t, v in lb.items():
                g, o = v["avg_vectors_gold_docs"], v["avg_vectors_other_docs"]
                L.append(f"| {t} | {v['avg_vectors_by_rank']} | {'-' if g is None else f'{g:.1f}'} | "
                         f"{'-' if o is None else f'{o:.1f}'} |")
        counts = res["qa"].get("gold_rank_counts", {})
        order = [b for b in ("rank 1", "rank 2", "rank 3+", "not retrieved") if b in counts]
        if order:
            L += ["\nF1 by where the first gold document was ranked (number of questions in brackets):\n",
                  "| Setting | " + " | ".join(f"{b} ({counts[b]})" for b in order) + " |",
                  "|---" * (len(order) + 1) + "|"]
            for key, v in res["qa"]["results"].items():
                by = v.get("F1_by_gold_rank", {})
                L.append(f"| {key} | " + " | ".join(f"{by[b]['mean']:.1f}" if b in by else "-" for b in order) + " |")
        if res["qa"]["paired_tests"]:
            L += ["\nPaired bootstrap at equal budget, first setting minus second (percentage points):\n",
                  "| Comparison | dEM [95% CI] | P(not better) | dF1 [95% CI] | P(not better) |", "|---|---|---|---|---|"]
            for name, t in res["qa"]["paired_tests"].items():
                L.append(f"| {name} | {t['EM']['diff']:+.1f} [{t['EM']['lo']:+.1f}, {t['EM']['hi']:+.1f}] | "
                         f"{t['EM']['p_not_better']:.3f} | {t['F1']['diff']:+.1f} [{t['F1']['lo']:+.1f}, "
                         f"{t['F1']['hi']:+.1f}] | {t['F1']['p_not_better']:.3f} |")
        L.append("")
    with open(path, "w") as f:
        f.write("\n".join(L))


def main(args):
    set_seed(args.seed)
    device = get_device()
    with precision_context(args.amp, device)():
        return _run(args, device)


def _run(args, device):
    sections = parse_str_list(args.sections)
    scp_dir, e2e_dir = os.path.join(args.run_dir, "scp"), os.path.join(args.run_dir, "e2e")
    out_dir = os.path.join(args.run_dir, args.out_name)
    records = read_json(os.path.join(args.data_dir, f"{args.dataset}_{args.eval_name}.json"))[: args.n_eval]
    short = sum(len(r["paragraphs"]) < args.k for r in records)
    if short:   # reading k documents needs at least k candidates (a few HotpotQA questions have only 6)
        records = [r for r in records if len(r["paragraphs"]) >= args.k]
        print(f"{short} questions have fewer than k={args.k} candidates and are skipped; {len(records)} remain")
    res = {}

    if "scp_curve" in sections:
        model, meta = load_from_checkpoint(scp_dir, device=device, tiny=args.tiny)
        prefixes = [m for m in parse_int_list(args.prefixes) if m <= model.max_mem]
        docs = [d for d in read_json(os.path.join(args.data_dir, f"{args.dataset}_scp.json")) if d["split"] == "heldout"]
        res["scp_curve"] = section_scp_curve(model, docs, prefixes, args.max_new_tokens)
        del model
        torch.cuda.empty_cache()

    need_e2e = [s for s in sections if s in ("params", "oracle", "retrieval", "qa")]
    if need_e2e:
        if not os.path.exists(e2e_dir):
            raise FileNotFoundError(f"{e2e_dir} not found; run train_e2e.py first (needed for {need_e2e})")
        model, meta = load_from_checkpoint(e2e_dir, device=device, tiny=args.tiny)
        model.model.eval()
        prefixes = [m for m in parse_int_list(args.prefixes) if m <= model.max_mem]
        cache = {}
        with torch.no_grad():
            for rec in tqdm(records, desc="compressing eval passages"):
                for t in rec["paragraphs"]:
                    if t not in cache:
                        cache[t] = model.compress(t, "compressor")[0]
        r = meta.get("r_score", min(16, model.max_mem))

        if "params" in sections:
            res["params"] = section_params(model, records, prefixes)
        if "oracle" in sections:
            res["oracle"] = section_oracle(model, records, cache, prefixes, args.max_new_tokens)
        ranks, scores, queries = reasoner_rankings(model, records, cache, r, return_queries=True)
        head_path = os.path.join(e2e_dir, "budget_head.pt")
        head = load_head(head_path, device) if os.path.exists(head_path) else None
        if head is not None and head.k != args.k:
            print(f"budget head was trained for k={head.k}, evaluating k={args.k}: learned split skipped")
            head = None
        if "qa" in sections:
            res["qa"], per_example = section_qa(model, records, cache, ranks, scores, args.k,
                                                parse_int_list(args.totals), parse_str_list(args.policies),
                                                prefixes, args.max_new_tokens, head=head, queries=queries, r=r,
                                                raw=not args.no_raw)
            write_json(per_example, os.path.join(out_dir, "qa_predictions.json"))
        if "retrieval" in sections:
            rankings = {"BM25": [bm25_rank(rec["question"], rec["paragraphs"]) for rec in records],
                        "query reasoner (after E2E)": ranks}
            # Same model, query reasoner reset to its starting point (copy of the SCP compressor). The compressor
            # is frozen during E2E, so the cached document vectors are unchanged.
            model.load_state(scp_dir)
            model.copy_adapter("compressor", "query_reasoner")
            with torch.no_grad():
                model.mem_query.copy_(model.mem_doc)
            rankings["query reasoner (before E2E)"], _ = reasoner_rankings(model, records, cache, r)
            res["retrieval"] = retrieval_table(rankings, records, parse_int_list(args.retrieval_ks))

    res["meta"] = {"run_dir": args.run_dir, "dataset": args.dataset, "n_eval": len(records), "k": args.k}
    write_json(res, os.path.join(out_dir, "eval.json"))
    write_summary(res, os.path.join(out_dir, "summary.md"), args.run_dir)
    print(f"results -> {out_dir}/eval.json and summary.md")
    return res


if __name__ == "__main__":
    main(build_parser().parse_args())
