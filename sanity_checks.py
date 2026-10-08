"""Pre-flight checks. Run once per backbone before spending GPU time on training.

  1. A1 bug demo: switching adapters with plain PEFT set_adapter() leaves the compressor with NO gradient.
  2. Fixed: NestedCLaRa.use() -> compressor, generator and memory embeddings all receive gradients.
  3. Nesting: the first m memory vectors do not depend on later memory tokens (so a stored index can be sliced).
  4. Straight-through: the retrieval loss reaches the query reasoner's LoRA weights through top-k selection.
  5. Learned budgets: the budget head gets a training signal from the answer loss (REINFORCE over exact-total splits).

    python sanity_checks.py --backbone qwen          # downloads Qwen2.5-0.5B-Instruct
    python sanity_checks.py --backbone t5 --tiny     # tiny random model, CPU, seconds
"""
import argparse

import torch

from nclara.modeling import load_model
from nclara.utils import get_device, set_seed

DOC = "Christopher Nolan is a British-American filmmaker. He was born in London in 1970."
Q = "In which year was the director of Inception born?"


def lora_grads(model, adapter):
    ps = [p for n, p in model._lora if f".{adapter}." in n]
    return sum(p.grad is not None and p.grad.abs().sum().item() > 0 for p in ps), len(ps)


def check(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def main(args):
    set_seed(0)
    device = get_device()
    model = load_model(args.backbone, max_mem=16, device=device, tiny=args.tiny)
    model.model.train()
    results = []

    # 1) A1 pattern: temporarily replace use() with a plain PEFT set_adapter() call
    model.set_trainable(["compressor", "generator"], mem_doc=True)
    model.use = lambda adapter: model.model.set_adapter(adapter)     # instance attribute shadows the method
    M, _ = model.compress(DOC, "compressor")
    model.gen_loss("Question: " + Q, [M[:8]], "1970").backward()
    del model.use                                                    # back to the fixed class method
    g, n = lora_grads(model, "compressor")
    results.append(check("A1 pattern (plain set_adapter)", g == 0,
                         f"compressor LoRA tensors with gradient: {g}/{n} (0 reproduces the A1 bug)"))
    model.zero_grad(set_to_none=True)

    # 2) fixed switching
    model.set_trainable(["compressor", "generator"], mem_doc=True)
    M, doc_h = model.compress(DOC, "compressor")
    loss = model.gen_loss("Question: " + Q, [M[:8]], "1970") + 0.1 * torch.nn.functional.mse_loss(
        M[:8].mean(0), doc_h.mean(0).detach())
    loss.backward()
    gc, nc = lora_grads(model, "compressor")
    gg, ng = lora_grads(model, "generator")
    mem_ok = model.mem_doc.grad is not None and model.mem_doc.grad.abs().sum().item() > 0
    results.append(check("fixed adapter switching", gc > 0 and gg > 0 and mem_ok,
                         f"compressor {gc}/{nc}, generator {gg}/{ng} LoRA tensors with gradient; "
                         f"memory embeddings: {mem_ok}  (LoRA A-matrices get no gradient on the very first step "
                         f"because B starts at zero, and T5's compressor only uses the encoder)"))
    model.zero_grad(set_to_none=True)

    # 3) prefix independence
    model.model.eval()
    with torch.no_grad():
        M1, _ = model.compress(DOC)
        saved = model.mem_doc.detach().clone()
        model.mem_doc.data[8:] += 1.0
        M2, _ = model.compress(DOC)
        model.mem_doc.data.copy_(saved)
    same = torch.allclose(M1[:8], M2[:8], atol=1e-4)
    results.append(check("prefix independence", same,
                         "first 8 memory vectors unchanged when memory tokens 9-16 are perturbed"
                         + ("" if same else " -- T5 fell back to bidirectional attention (see warning above)")))

    # 4) straight-through gradient to the query reasoner
    model.model.train()
    model.copy_adapter("compressor", "query_reasoner")
    with torch.no_grad():
        model.mem_query.copy_(model.mem_doc)
        # give LoRA B matrices non-zero values so A-matrices also receive gradient in this one-step test
        for n, p in model._lora:
            if ".query_reasoner." in n and "lora_B" in n:
                p.normal_(0, 0.01)
    model.set_trainable(["query_reasoner", "generator"], mem_query=True)
    with torch.no_grad():
        cands = [model.compress(t)[0] for t in [DOC, "Paris is the capital of France.", "Inception is a 2010 film."]]
    q, _ = model.compress(Q, "query_reasoner", is_query=True)
    Z = model.st_topk(model.score(q, cands, 8), 2, 0.5)
    loss = model.gen_loss("Question: " + Q, model.gather_slots(Z, cands, [8, 4]), "1970")
    loss.backward()
    gq, nq = lora_grads(model, "query_reasoner")
    results.append(check("straight-through to query reasoner", gq > 0,
                         f"query_reasoner LoRA tensors with gradient: {gq}/{nq}"))

    # 5) budget head: 24 vectors over the 2 selected documents allows two splits, [8,16] and [16,8]. Evaluate both
    #    (deterministically, no dropout) and apply the leave-one-out REINFORCE update: the head must get gradient.
    from nclara.budget import BudgetHead, head_features
    model.model.eval()
    head = BudgetHead(model.hidden_size, [4, 8, 16], 2).to(device)
    chosen = Z.detach().argmax(dim=1).tolist()
    with torch.no_grad():
        q2, _ = model.compress(Q, "query_reasoner", is_query=True)
        scores2 = model.score(q2, cands, 8)
    logits = head(*head_features(q2, cands, chosen, scores2, 8, 4))
    dist, pats = head.split_distribution(logits, 24)
    splits = [[head.lengths[i] for i in p] for p in pats.tolist()]
    with torch.no_grad():
        Ls = torch.tensor([model.gen_loss("Question: " + Q, [cands[c][:bi] for c, bi in zip(chosen, sp)], "1970").item()
                           for sp in splits], device=device)
    adv = (Ls.sum() - Ls) / (len(Ls) - 1) - Ls
    (-(adv * dist.log_prob(torch.arange(len(splits), device=device))).mean()).backward()
    g = sum(p.grad is not None and p.grad.abs().sum().item() > 0 for p in head.parameters())
    n_p = len(list(head.parameters()))
    results.append(check("learned budget head", len(splits) == 2 and g > 0,
                         f"{g}/{n_p} head tensors received gradient; splits {splits} gave answer losses "
                         f"{[round(x, 3) for x in Ls.tolist()]}"))

    print(f"\n{sum(results)}/{len(results)} checks passed")
    return all(results)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--backbone", choices=["qwen", "t5"], required=True)
    p.add_argument("--tiny", action="store_true")
    return p


if __name__ == "__main__":
    main(build_parser().parse_args())
