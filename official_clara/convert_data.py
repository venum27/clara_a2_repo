"""Convert this project's data into the official CLaRa code's three training formats, so the official baseline is
trained on exactly the same questions and the same synthetic SCP data as our models.

  stage1   (compression pretraining)   {"data_type": "qa", "question": [...], "answers": [...], "docs": [passage]}
           QA records only by default: the released loader turns a paraphrase record's question into "" but a QA
           record's into a list, so a file mixing both crashes in datasets/pyarrow ("cannot mix list and non-list").
           The authors' example pretraining data is QA-only too. --paraphrase writes them anyway.
  stage1_2 (instruction tuning)        {"question": q, "docs": [k passages], "answer": a}
  stage2   (end-to-end)                {"question": q, "docs": [10 candidates], "answer": a, "pos_index": [gold]}

For stage 1_2 the official data pairs each question with retrieved passages; we use its gold passages plus the
highest-BM25 distractors, k passages in total. For stage 2 only questions with exactly --n_docs candidates are kept:
the official model reshapes a batch of questions to (batch, n_docs, ...), so a batch mixing questions with different
numbers of candidates crashes (a few HotpotQA questions have fewer than 10 paragraphs; 2Wiki always has 10).

    python3 official_clara/convert_data.py --datasets hotpotqa,2wiki --k 4
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nclara.utils import parse_str_list, read_json  # noqa: E402


def bm25_order(question, paragraphs):
    try:
        from rank_bm25 import BM25Okapi
        bm = BM25Okapi([p.lower().split() for p in paragraphs])
        scores = bm.get_scores(question.lower().split())
        return sorted(range(len(paragraphs)), key=lambda i: -scores[i])
    except ImportError:                                    # plain word overlap if rank_bm25 is missing
        q = set(question.lower().split())
        return sorted(range(len(paragraphs)), key=lambda i: -len(q & set(paragraphs[i].lower().split())))


def write_jsonl(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)


def main(args):
    for ds in parse_str_list(args.datasets):
        out = os.path.join(args.out_dir, ds)
        scp = [d for d in read_json(os.path.join(args.data_dir, f"{ds}_scp.json")) if d["split"] == "train"]
        stage1 = []
        for d in scp:
            qas = d.get("simple_qa", []) + d.get("complex_qa", [])
            if qas:
                stage1.append({"data_type": "qa", "question": [x["question"] for x in qas],
                               "answers": [x["answer"] for x in qas], "docs": [d["document"]]})
            if args.paraphrase and d.get("paraphrase"):
                stage1.append({"data_type": "paraphrase", "answers": [d["paraphrase"]], "docs": [d["document"]]})
        train = read_json(os.path.join(args.data_dir, f"{ds}_train.json"))
        stage12, stage2 = [], []
        for rec in train:
            paras = rec["paragraphs"]
            gold = [i for i in rec["gold_idx"] if i < len(paras)]
            rest = [i for i in bm25_order(rec["question"], paras) if i not in gold]
            chosen = (gold + rest)[: args.k]
            if len(chosen) == args.k:
                stage12.append({"question": rec["question"], "docs": [paras[i] for i in chosen],
                                "answer": rec["answer"]})
            if len(paras) == args.n_docs:
                stage2.append({"question": rec["question"], "docs": paras, "answer": rec["answer"],
                               "pos_index": gold})
        n1 = write_jsonl(stage1, os.path.join(out, "stage1_pretrain.jsonl"))
        n12 = write_jsonl(stage12, os.path.join(out, "stage1_2_instruction.jsonl"))
        n2 = write_jsonl(stage2, os.path.join(out, "stage2_end_to_end.jsonl"))
        dropped = len(train) - n2
        print(f"[{ds}] stage1 {n1} records ({sum(r['data_type'] == 'qa' for r in stage1)} QA, "
              f"{sum(r['data_type'] == 'paraphrase' for r in stage1)} paraphrase) | stage1_2 {n12} | stage2 {n2} "
              f"(dropped {dropped} with other than {args.n_docs} candidates) -> {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasets", default="hotpotqa,2wiki")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--out_dir", default="official_clara/data")
    p.add_argument("--k", type=int, default=4, help="documents per question (the official generation_top_k)")
    p.add_argument("--n_docs", type=int, default=10, help="stage 2: keep questions with exactly this many candidates")
    p.add_argument("--paraphrase", action="store_true",
                   help="also write paraphrase records (the released loader cannot mix them with QA records)")
    main(p.parse_args())
