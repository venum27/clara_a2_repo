"""Latency and memory per question (Qwen, batch size 1): our nested model at several budgets and breadths, CLaRa's
operating point (fixed-16 model, 4 documents x 16 vectors) and raw text. Also offline costs: compression time per
passage and index storage when one nested model serves every rate vs. one fixed-rate model per rate.

Online steps timed (median over questions, after warm-up):
  query      encoding the question with the query reasoner
  scoring    cosine scoring of the cached candidates
  prefill    the generator's forward pass over the whole input (time to first token)
  decode     per generated token, with decoding forced to exactly --decode_tokens tokens so that answer length does not
             distort the comparison
KV cache: the generator's key/value cache per question, computed from the model configuration.

    python3 benchmark_latency.py --dataset 2wiki        # writes runs/latency_2wiki.json and .md
"""
import argparse
import os
import statistics
import time

import torch
from tqdm import tqdm

from evaluate import RAW_PROMPT, bm25_rank
from nclara.modeling import load_from_checkpoint
from nclara.utils import get_device, precision_context, read_json, set_seed, write_json
from train_e2e import E2E_INSTRUCTION

SETTINGS = [  # (name, model, documents, vectors per document)
    ("nested, 4 docs x 4", "nested", 4, 4),
    ("nested, 4 docs x 8", "nested", 4, 8),
    ("nested, 8 docs x 4", "nested", 8, 4),
    ("nested, 4 docs x 16", "nested", 4, 16),
    ("nested, 8 docs x 8", "nested", 8, 8),
    ("nested, 4 docs x 32", "nested", 4, 32),
    ("CLaRa-style fixed-16, 4 docs x 16", "fixed", 4, 16),
    ("raw text, BM25 top-4", "raw", 4, None),
    ("raw text, BM25 top-8", "raw", 8, None),
]


def _sync():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def ms(fn):
    _sync()
    t = time.perf_counter()
    out = fn()
    _sync()
    return out, 1000 * (time.perf_counter() - t)


def kv_bytes_per_position(model):
    c = model.model.config
    head_dim = getattr(c, "head_dim", None) or c.hidden_size // c.num_attention_heads
    return 2 * c.num_hidden_layers * c.num_key_value_heads * head_dim * 2        # K and V, bf16


@torch.no_grad()
def time_generation(model, x=None, ids=None, decode_tokens=16):
    """Prefill time, total time for exactly decode_tokens new tokens, and the input length in positions."""
    gen = dict(max_new_tokens=decode_tokens, min_new_tokens=decode_tokens, do_sample=False,
               pad_token_id=model.tokenizer.pad_token_id, eos_token_id=model.tokenizer.eos_token_id)
    if x is not None:
        mask = torch.ones(x.shape[:2], dtype=torch.long, device=x.device)
        _, t_pre = ms(lambda: model.model(inputs_embeds=x, attention_mask=mask, use_cache=True))
        _, t_all = ms(lambda: model.model.generate(inputs_embeds=x, attention_mask=mask, **gen))
        return t_pre, t_all, x.shape[1]
    mask = torch.ones_like(ids)
    with model.model.disable_adapter():
        _, t_pre = ms(lambda: model.model(input_ids=ids, attention_mask=mask, use_cache=True))
        _, t_all = ms(lambda: model.model.generate(input_ids=ids, attention_mask=mask, **gen))
    return t_pre, t_all, ids.shape[1]


def accuracy(run_dir, docs, total):
    folder = "results" if docs == 4 else f"results_k{docs}"
    p = os.path.join(run_dir, folder, "eval.json")
    if not os.path.exists(p):
        return None
    r = read_json(p).get("qa", {}).get("results", {}).get(f"uniform@{total}")
    return None if r is None else r["F1"]["mean"]


def main(args):
    set_seed(0)
    device = get_device()
    if device != "cuda" and not args.tiny:
        raise SystemExit("the latency benchmark needs a GPU")
    nested_run = args.nested_run or f"runs/qwen/{args.dataset}/r2_nested_M32_all_e6__learned_s42"
    fixed_run = args.fixed_run or f"runs/qwen/{args.dataset}/r2_fixed_M16_e6_s42"
    records = read_json(os.path.join(args.data_dir, f"{args.dataset}_eval.json"))
    records = [r for r in records if len(r["paragraphs"]) >= 8][: args.n + args.warmup]
    models = {}
    for key, run in (("nested", nested_run), ("fixed", fixed_run)):
        m, meta = load_from_checkpoint(os.path.join(run, "e2e"), device=device, tiny=args.tiny)
        m.model.eval()
        models[key] = (m, meta)
    kvb = kv_bytes_per_position(models["nested"][0])
    times = {name: {"prefill": [], "total": [], "positions": []} for name, *_ in SETTINGS}
    step = {"query": [], "scoring": [], "compress": []}
    with precision_context("none" if args.tiny else "bf16", device)():
        for n, rec in enumerate(tqdm(records, desc=f"latency ({args.dataset})")):
            record = n >= args.warmup
            order = bm25_rank(rec["question"], rec["paragraphs"])
            mems = {}
            for key, (m, meta) in models.items():
                m.use("compressor")
                cands, t_c = ms(lambda: [m.compress(p, "compressor")[0] for p in rec["paragraphs"]])
                q, t_q = ms(lambda: m.compress(rec["question"], "query_reasoner", is_query=True)[0])
                _, t_s = ms(lambda: m.score(q, cands, meta.get("r_score", min(16, m.max_mem))))
                mems[key] = [cands[i] for i in order]
                if record and key == "nested":
                    step["compress"].append(t_c / len(rec["paragraphs"]))
                    step["query"].append(t_q)
                    step["scoring"].append(t_s)
            instr = E2E_INSTRUCTION.format(q=rec["question"])
            for name, kind, docs, per_doc in SETTINGS:
                if kind == "raw":
                    m = models["nested"][0]
                    pre, _ = m._chat_parts(RAW_PROMPT.format(ctx=" ".join(rec["paragraphs"][i] for i in order[:docs]),
                                                             q=rec["question"]))
                    t_pre, t_all, pos = time_generation(m, ids=m.ids(pre), decode_tokens=args.decode_tokens)
                else:
                    m = models[kind][0]
                    m.use("generator")
                    x = m._build_inputs(instr, [c[:per_doc] for c in mems[kind][:docs]])
                    t_pre, t_all, pos = time_generation(m, x=x, decode_tokens=args.decode_tokens)
                if record:
                    times[name]["prefill"].append(t_pre)
                    times[name]["total"].append(t_all)
                    times[name]["positions"].append(pos)
    rows = []
    for name, kind, docs, per_doc in SETTINGS:
        t = times[name]
        pre, tot = statistics.median(t["prefill"]), statistics.median(t["total"])
        pos = statistics.mean(t["positions"])
        total = None if per_doc is None else docs * per_doc
        run = nested_run if kind == "nested" else (fixed_run if kind == "fixed" else None)
        rows.append({"setting": name, "memory_vectors": total, "input_positions": pos,
                     "prefill_ms": pre, "decode_ms_per_token": (tot - pre) / args.decode_tokens,
                     "total_ms": tot, "kv_cache_kb": kvb * (pos + args.decode_tokens) / 1024,
                     "F1": accuracy(run, docs, total) if run else None})
    vec_bytes = models["nested"][1].get("hidden_size", models["nested"][0].hidden_size) * 2
    offline = {"compress_ms_per_passage": statistics.median(step["compress"]),
               "query_ms": statistics.median(step["query"]), "scoring_ms": statistics.median(step["scoring"]),
               "index_kb_per_passage_nested": 32 * vec_bytes / 1024,
               "index_kb_per_passage_fixed_rates_4_8_16_32": (4 + 8 + 16 + 32) * vec_bytes / 1024}
    out = {"dataset": args.dataset, "n_questions": args.n, "decode_tokens": args.decode_tokens,
           "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu", "nested_run": nested_run, "fixed_run": fixed_run,
           "rows": rows, "offline": offline}
    write_json(out, os.path.join(args.runs_dir, f"latency_{args.dataset}.json"))
    L = [f"# Latency and memory, {args.dataset} ({out['gpu']}, batch size 1, median over {args.n} questions)\n",
         f"Decoding forced to {args.decode_tokens} tokens. F1 from the runs' own evaluation (uniform split).\n",
         "| Setting | Memory vectors | Input positions | Prefill (ms) | Decode (ms/token) | Total (ms) | KV cache (KB) | F1 |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        f1 = "-" if r["F1"] is None else f"{r['F1']:.1f}"
        L.append(f"| {r['setting']} | {r['memory_vectors'] or '-'} | {r['input_positions']:.0f} | {r['prefill_ms']:.1f} | "
                 f"{r['decode_ms_per_token']:.2f} | {r['total_ms']:.0f} | {r['kv_cache_kb']:.0f} | {f1} |")
    o = offline
    L += ["", f"Offline: compressing one passage {o['compress_ms_per_passage']:.1f} ms; encoding a question "
              f"{o['query_ms']:.1f} ms; scoring the candidates {o['scoring_ms']:.2f} ms.",
          f"Index per passage: nested model {o['index_kb_per_passage_nested']:.0f} KB (32 vectors, serves every "
          f"budget) vs one fixed-rate model per rate (4, 8, 16, 32 vectors) "
          f"{o['index_kb_per_passage_fixed_rates_4_8_16_32']:.0f} KB plus four trained compressors."]
    with open(os.path.join(args.runs_dir, f"latency_{args.dataset}.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", required=True)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--runs_dir", default="runs")
    p.add_argument("--nested_run", default=None)
    p.add_argument("--fixed_run", default=None)
    p.add_argument("--n", type=int, default=100)
    p.add_argument("--warmup", type=int, default=5)
    p.add_argument("--decode_tokens", type=int, default=16)
    p.add_argument("--tiny", action="store_true", help="tiny random models on CPU (pipeline test only)")
    main(p.parse_args())
