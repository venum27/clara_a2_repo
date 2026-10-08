"""Synthesise Salient Compressor Pretraining (SCP) data: simple QA, complex QA and a paraphrase per passage.

Changes from A1:
  * One instruction-tuned synthesiser (default Qwen2.5-14B-Instruct) writes the data for BOTH backbones. In A1
    FLAN-T5-base generated its own data and produced 0 verified QA pairs, so its compressor only ever saw
    paraphrase supervision. Sharing the data also makes the two backbones directly comparable.
  * Line-based output ("Q1: ... / A1: ...") instead of JSON, which small models follow far more reliably.
  * Complex (two-fact) questions, as in the paper, in addition to simple ones.
  * Every passage from the training questions' gold paragraphs is used (A1 used only the first gold paragraph),
    and 10% of passages are held out to measure compression quality per prefix length.
  * Greedy decoding, a fixed passage order and deterministic kernels, so re-running gives the same data.

    python synth_scp_data.py --datasets hotpotqa --synth_model Qwen/Qwen2.5-14B-Instruct
"""
import argparse
import os
import random
import re

# Deterministic cuBLAS kernels, so re-running synthesis reproduces the same data.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import torch  # noqa: E402
from tqdm import tqdm

from nclara.utils import get_device, parse_str_list, read_json, set_seed, write_json

SIMPLE_QA_PROMPT = """Read the document and write 3 short factual questions about it.
Each question must be answerable with a short phrase copied from the document, must make sense without seeing
the document, and must ask about a different fact.

Document:
{doc}

Use exactly this format:
Q1: <question>
A1: <answer>
Q2: <question>
A2: <answer>
Q3: <question>
A3: <answer>"""

COMPLEX_QA_PROMPT = """Read the document and write 1 question that can only be answered by combining TWO different
facts from the document. The answer must be a short phrase copied from the document, and the question must make
sense without seeing the document.

Document:
{doc}

Use exactly this format:
Q1: <question>
A1: <answer>"""

PARAPHRASE_PROMPT = """Paraphrase the document. Keep every fact, name, number and date, change the wording and the
sentence order, and do not add information.

Document:
{doc}

Paraphrase:"""


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datasets", default="hotpotqa,2wiki")
    p.add_argument("--data_dir", default="data")
    p.add_argument("--synth_model", default="Qwen/Qwen2.5-14B-Instruct")
    p.add_argument("--max_docs", type=int, default=800, help="cap on passages per dataset")
    p.add_argument("--include_distractors", action="store_true",
                   help="also synthesise data for distractor paragraphs (more SCP data, slower)")
    p.add_argument("--heldout_frac", type=float, default=0.1)
    p.add_argument("--batch_size", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tiny", action="store_true")
    return p


def clean(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def is_grounded(answer, doc):
    """Answer text (or >=80% of its content words) must appear in the passage (A1's check)."""
    a, d = clean(answer), clean(doc)
    if not a:
        return False
    if a in d:
        return True
    words = re.findall(r"[a-z0-9]+", a)
    doc_words = set(re.findall(r"[a-z0-9]+", d))
    return bool(words) and sum(w in doc_words for w in words if len(w) > 2) / len(words) >= 0.8


def parse_pairs(raw):
    qs = dict(re.findall(r"Q(\d+)\s*[:.]\s*(.+)", raw))
    ans = dict(re.findall(r"A(\d+)\s*[:.]\s*(.+)", raw))
    return [{"question": qs[i].strip(), "answer": ans[i].strip()} for i in sorted(qs) if i in ans]


def verify(pairs, doc):
    keep = []
    for p in pairs:
        q, a = p["question"], p["answer"]
        if not q.endswith("?") or len(a.split()) > 8 or clean(a) in clean(q) or not is_grounded(a, doc):
            continue
        keep.append(p)
    return keep


class Synthesiser:
    def __init__(self, model_name, device):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(model_name, padding_side="left")
        if device == "cuda":
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        else:
            dtype = torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype).to(device).eval()
        self.device = device

    @torch.no_grad()
    def __call__(self, prompts, max_new_tokens):
        texts = [self.tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False,
                                              add_generation_prompt=True) for p in prompts]
        enc = self.tok(texts, return_tensors="pt", padding=True).to(self.device)
        out = self.model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                                  pad_token_id=self.tok.pad_token_id or self.tok.eos_token_id)
        return [self.tok.decode(o[enc.input_ids.shape[1]:], skip_special_tokens=True).strip() for o in out]


def collect_passages(records, include_distractors, max_docs, seed):
    seen, docs = set(), []
    for rec in records:
        idx = range(len(rec["paragraphs"])) if include_distractors else rec["gold_idx"]
        for i in idx:
            d = rec["paragraphs"][i].strip()
            if len(d.split()) >= 15 and d not in seen:
                seen.add(d)
                docs.append(d)
    random.Random(seed).shuffle(docs)
    return docs[:max_docs]


def main(args):
    set_seed(args.seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    synth = None
    for name in parse_str_list(args.datasets):
        records = read_json(os.path.join(args.data_dir, f"{name}_train.json"))
        out_path = os.path.join(args.data_dir, f"{name}_scp.json")
        if args.tiny:
            from nclara.tiny import fake_synthetic
            write_json(fake_synthetic(records, args.heldout_frac, args.seed), out_path)
            print(f"[{name}] wrote toy SCP data -> {out_path}")
            continue
        if synth is None:
            synth = Synthesiser(args.synth_model, get_device())
        passages = collect_passages(records, args.include_distractors, args.max_docs, args.seed)
        rng = random.Random(args.seed)
        out, n_simple, n_complex = [], 0, 0
        for s in tqdm(range(0, len(passages), args.batch_size), desc=f"synth [{name}]"):
            batch = passages[s: s + args.batch_size]
            simple = synth([SIMPLE_QA_PROMPT.format(doc=d) for d in batch], 160)
            complex_ = synth([COMPLEX_QA_PROMPT.format(doc=d) for d in batch], 80)
            para = synth([PARAPHRASE_PROMPT.format(doc=d) for d in batch], 220)
            for d, r1, r2, r3 in zip(batch, simple, complex_, para):
                sq, cq = verify(parse_pairs(r1), d), verify(parse_pairs(r2), d)
                n_simple += len(sq)
                n_complex += len(cq)
                out.append({"doc_id": f"{name}_d{len(out)}", "document": d, "simple_qa": sq, "complex_qa": cq,
                            "paraphrase": r3, "split": "heldout" if rng.random() < args.heldout_frac else "train"})
        write_json(out, out_path)
        print(f"[{name}] {len(out)} passages | verified simple QA: {n_simple} | complex QA: {n_complex} "
              f"| heldout passages: {sum(o['split'] == 'heldout' for o in out)} -> {out_path}")


if __name__ == "__main__":
    main(build_parser().parse_args())
