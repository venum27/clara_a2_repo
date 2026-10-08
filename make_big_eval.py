"""A larger evaluation set: questions from the same validation split as before, excluding every question we trained
on or already evaluated (data/<dataset>_train.json and _eval.json). Writes data/<dataset>_evalbig.json.

The trained models are only evaluated again; nothing is retrained. With 300 questions a paired F1 difference has a
95% interval of about +-4 points; with 3,000 about +-1.3.

    python3 make_big_eval.py --datasets hotpotqa,2wiki --n 3000      # --n all: every remaining question
"""
import argparse
import os
import random

from nclara.hfdata import load_split
from nclara.utils import parse_str_list, read_json, write_json
from prepare_data import HF_DATASET_ID, build_records


def main(args):
    for ds in parse_str_list(args.datasets):
        out = os.path.join(args.data_dir, f"{ds}_{args.name}.json")
        if os.path.exists(out) and not args.force:
            print(f"[{ds}] {out} exists ({len(read_json(out))} questions); use --force to rebuild")
            continue
        used = {r["id"] for part in ("train", "eval") for r in read_json(os.path.join(args.data_dir, f"{ds}_{part}.json"))}
        spec = HF_DATASET_ID[ds]
        rows = load_split(spec["path"], spec["name"], "validation")
        ids = [i for i in range(len(rows)) if rows[i]["id"] not in used]
        random.Random(args.seed).shuffle(ids)
        recs = [r for r in build_records(rows, ids) if len(r["paragraphs"]) >= args.min_docs]
        if args.n != "all":
            recs = recs[: int(args.n)]
        assert not ({r["id"] for r in recs} & used), "overlap with training or evaluation questions"
        write_json(recs, out)
        print(f"[{ds}] {len(rows)} validation questions, {len(used)} already used -> {len(recs)} new evaluation "
              f"questions in {out} (none overlap)")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasets", default="hotpotqa,2wiki")
    p.add_argument("--n", default="3000", help="number of questions, or 'all'")
    p.add_argument("--name", default="evalbig")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--min_docs", type=int, default=4, help="the models read 4 documents")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--force", action="store_true")
    main(p.parse_args())
