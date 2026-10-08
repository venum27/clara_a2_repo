"""Download HotpotQA (distractor) and 2WikiMultihopQA and write disjoint train / eval subsets.

Same source datasets and record schema as Assignment 1, with configurable sizes (A1's biggest risk was data
scale) and the question `type` kept so results can be broken down (e.g. bridge vs comparison).

    python prepare_data.py --datasets hotpotqa,2wiki --n_train 300 --n_eval 100
"""
import argparse
import os
import random

from nclara.utils import parse_str_list, write_json

HF_DATASET_ID = {
    "hotpotqa": dict(path="hotpotqa/hotpot_qa", name="distractor"),
    "2wiki": dict(path="framolfese/2WikiMultihopQA", name=None),
}


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasets", default="hotpotqa,2wiki")
    p.add_argument("--n_train", type=int, default=300)
    p.add_argument("--n_eval", type=int, default=100)
    p.add_argument("--split", default="validation",
                   help="HF split to sample from. A1 sampled disjoint train/eval ids from the validation split.")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--data_dir", default="data")
    p.add_argument("--tiny", action="store_true", help="write a toy dataset instead (CPU smoke test)")
    return p


def flatten_context(ex):
    titles, sents = ex["context"]["title"], ex["context"]["sentences"]
    paragraphs = [" ".join(s).strip() for s in sents]
    gold_titles = set(ex["supporting_facts"]["title"])
    return titles, paragraphs, [i for i, t in enumerate(titles) if t in gold_titles]


def build_records(ds, ids):
    out = []
    for i in ids:
        ex = ds[i]
        titles, paragraphs, gold_idx = flatten_context(ex)
        if not gold_idx or len(paragraphs) < 3:
            continue
        out.append({"id": ex["id"], "question": ex["question"], "answer": ex["answer"], "titles": titles,
                    "paragraphs": paragraphs, "gold_idx": gold_idx, "type": ex.get("type", "unknown")})
    return out


def main(args):
    os.makedirs(args.data_dir, exist_ok=True)
    for name in parse_str_list(args.datasets):
        train_path = os.path.join(args.data_dir, f"{name}_train.json")
        eval_path = os.path.join(args.data_dir, f"{name}_eval.json")
        if args.tiny:
            from nclara.tiny import make_fake_records
            write_json(make_fake_records(args.n_train, args.seed, "tr"), train_path)
            write_json(make_fake_records(args.n_eval, args.seed + 1, "ev"), eval_path)
            print(f"[{name}] wrote toy data ({args.n_train} train / {args.n_eval} eval)")
            continue
        from nclara.hfdata import load_split
        spec = HF_DATASET_ID[name]
        try:
            ds = load_split(spec["path"], spec["name"], args.split)
        except Exception as e:
            raise SystemExit(f"[{name}] {e}\nRun ./scripts/00_setup_check.sh for details.")
        ids = list(range(len(ds)))
        random.Random(args.seed).shuffle(ids)
        # over-sample a little because build_records drops examples without gold paragraphs
        train = build_records(ds, ids[: int(args.n_train * 1.1)])[: args.n_train]
        evals = build_records(ds, ids[int(args.n_train * 1.1): int(args.n_train * 1.1) + int(args.n_eval * 1.1)])
        evals = evals[: args.n_eval]
        write_json(train, train_path)
        write_json(evals, eval_path)
        print(f"[{name}] {len(train)} train / {len(evals)} eval -> {train_path}, {eval_path}")


if __name__ == "__main__":
    main(build_parser().parse_args())
