"""CLaRa with nested (Matryoshka) memory tokens, for a decoder-only (Qwen2.5) and an encoder-decoder (FLAN-T5) backbone.

One base LLM carries three LoRA adapters that share its representation space:
  compressor      passage + memory tokens -> memory vectors (the compressed document)
  query_reasoner  question + query memory tokens -> query vectors used for retrieval
  generator       question + selected memory vectors -> answer

Nesting: the compressor always produces `max_mem` memory vectors, and every prefix M[:m] is trained to be a
usable compression on its own (nested SCP). One stored index therefore serves every compression rate.

IMPORTANT (bug fixed relative to the A1 code): PEFT's `set_adapter()` marks only the active adapter as
trainable. In a CLaRa step several adapters are used in one forward pass (compressor, then generator), so after
switching to the generator the compressor's LoRA weights have requires_grad=False when backward() runs and they
silently receive no gradient. `use()` below switches adapters and then restores our own trainable set.
"""
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model
from transformers.modeling_outputs import BaseModelOutput

from .utils import clean_prediction, read_json, write_json

BACKBONE_MODELS = {"qwen": "Qwen/Qwen2.5-0.5B-Instruct", "t5": "google/flan-t5-base"}
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_model(backbone):
    """Where to load a backbone from, in order: $QWEN_MODEL / $T5_MODEL, a copy in <project>/models/<name>
    (optional local copy), else the Hugging Face id (loaded from the cache, downloaded if missing)."""
    env = os.environ.get(f"{backbone.upper()}_MODEL")
    if env:
        return env
    local = os.path.join(PROJECT_DIR, "models", BACKBONE_MODELS[backbone].split("/")[-1])
    return local if os.path.isfile(os.path.join(local, "config.json")) else BACKBONE_MODELS[backbone]
ADAPTERS = ("compressor", "generator", "query_reasoner")
MEMORY_PLACEHOLDER = "<<<MEMORY>>>"


class NestedCLaRa(nn.Module):
    lora_targets = None
    task_type = None
    is_encoder_decoder = False

    def __init__(self, base_model, tokenizer, backbone, model_name, max_mem=32, lora_r=16,
                 max_doc_tokens=256, max_query_tokens=64, max_target_tokens=96, device="cpu",
                 rescale_memory=False):
        super().__init__()
        self.rescale_memory = rescale_memory
        self.backbone, self.model_name = backbone, model_name
        self.tokenizer = tokenizer
        self.max_mem, self.lora_r = max_mem, lora_r
        self.max_doc_tokens, self.max_query_tokens = max_doc_tokens, max_query_tokens
        self.max_target_tokens = max_target_tokens
        self.device = device
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        self.hidden_size = base_model.config.hidden_size if hasattr(base_model.config, "hidden_size") \
            else base_model.config.d_model
        cfg = LoraConfig(r=lora_r, lora_alpha=2 * lora_r, lora_dropout=0.05,
                         target_modules=self.lora_targets, task_type=self.task_type)
        self.model = get_peft_model(base_model, cfg, adapter_name="compressor")
        self.model.add_adapter("generator", cfg)
        self.model.add_adapter("query_reasoner", cfg)

        # Learnable memory-token input embeddings: identical for every passage (blank slots); their OUTPUT
        # hidden states after the compressor forward pass are the compressed document.
        self.mem_doc = nn.Parameter(0.02 * torch.randn(max_mem, self.hidden_size))
        self.mem_query = nn.Parameter(self.mem_doc.detach().clone())
        self.to(device)

        # Typical norm of a real token embedding; used to optionally rescale memory vectors (decoder-only only)
        with torch.no_grad():
            self.embed_norm = self.model.get_input_embeddings().weight.norm(dim=-1).mean().item()
        self._lora = [(n, p) for n, p in self.model.named_parameters() if "lora_" in n]
        self._trainable = set()
        self.set_trainable([])

    # ------------------------------------------------------------------ adapters & trainability
    def set_trainable(self, adapters, mem_doc=False, mem_query=False):
        """Freeze everything, then unfreeze the LoRA weights of `adapters` and the chosen memory embeddings."""
        for p in self.model.parameters():
            p.requires_grad_(False)
        self._trainable = {n for n, _ in self._lora if any(f".{a}." in n for a in adapters)}
        for n, p in self._lora:
            p.requires_grad_(n in self._trainable)
        self.mem_doc.requires_grad_(mem_doc)
        self.mem_query.requires_grad_(mem_query)

    def use(self, adapter):
        """Activate `adapter` for the next forward pass WITHOUT changing which weights are trainable."""
        self.model.set_adapter(adapter)
        for n, p in self._lora:
            p.requires_grad_(n in self._trainable)

    def trainable_parameters(self):
        return [p for p in self.parameters() if p.requires_grad]

    def copy_adapter(self, src, dst):
        params = dict(self._lora)
        copied = 0
        with torch.no_grad():
            for n, p in self._lora:
                if f".{src}." in n:
                    target = n.replace(f".{src}.", f".{dst}.")
                    if target in params:
                        params[target].copy_(p)
                        copied += 1
        return copied

    def lora_snapshot(self):
        return {n: p.detach().float().cpu().clone() for n, p in self._lora}

    def delta_report(self, before):
        """Per adapter: how many LoRA tensors changed since `before`, and the mean |delta|.
        (Compare against a snapshot of the SAME model; comparing against a freshly initialised model, as the
        A1 check did, mostly measures the difference between two random initialisations.)"""
        after = self.lora_snapshot()
        report = {}
        for a in ADAPTERS:
            keys = [k for k in after if f".{a}." in k]
            changed = sum(not torch.equal(before[k], after[k]) for k in keys)
            total_abs = sum((after[k] - before[k]).abs().sum().item() for k in keys)
            numel = sum(after[k].numel() for k in keys)
            nonzero_B = sum(after[k].abs().sum().item() > 0 for k in keys if "lora_B" in k)
            n_B = sum("lora_B" in k for k in keys)
            report[a] = {"tensors": len(keys), "changed": changed,
                         "mean_abs_delta": total_abs / max(numel, 1),
                         "lora_B_nonzero": f"{nonzero_B}/{n_B}"}
        return report

    def param_counts(self):
        base = self.model.get_base_model()
        total_base = sum(p.numel() for n, p in base.named_parameters() if "lora_" not in n)
        per_adapter = {a: sum(p.numel() for n, p in self._lora if f".{a}." in n) for a in ADAPTERS}
        return {"backbone": self.backbone, "model_name": self.model_name,
                "architecture": "encoder-decoder" if self.is_encoder_decoder else "decoder-only",
                "base_params": total_base, "lora_params_per_adapter": per_adapter,
                "memory_embedding_params": self.mem_doc.numel() + self.mem_query.numel(),
                "hidden_size": self.hidden_size, "max_mem": self.max_mem, "lora_r": self.lora_r}

    # ------------------------------------------------------------------ tokenisation helpers
    def ids(self, text, max_len=None, add_special_tokens=False):
        enc = self.tokenizer(text, add_special_tokens=add_special_tokens, truncation=max_len is not None,
                             max_length=max_len, return_tensors="pt")
        return enc.input_ids.to(self.device)

    def embed(self, ids):
        return self.model.get_input_embeddings()(ids)

    def n_tokens(self, text):
        return len(self.tokenizer(text, add_special_tokens=False).input_ids)

    # ------------------------------------------------------------------ retrieval (shared)
    @staticmethod
    def score(query_mem, cand_mems, r):
        """Cosine similarity between the flattened first-r query vectors and first-r document vectors."""
        q = F.normalize(query_mem[:r].flatten(), dim=0)
        C = torch.stack([F.normalize(c[:r].flatten(), dim=0) for c in cand_mems])
        return C @ q

    @staticmethod
    def st_topk(scores, k, tau=0.5):
        """Straight-through top-k without replacement. Forward: hard one-hot rows (k x D).
        Backward: gradient of the per-slot softmax(scores / tau)."""
        D = scores.shape[0]
        taken = torch.zeros(D, device=scores.device)
        hard = torch.zeros(k, D, device=scores.device)
        soft = []
        for j in range(k):
            logits = scores / tau + torch.log(1 - taken + 1e-9)
            p = F.softmax(logits, dim=0)
            soft.append(p)
            idx = int(torch.argmax(p.detach()))
            hard[j, idx] = 1.0
            taken = taken + hard[j]
        soft = torch.stack(soft)
        return hard + (soft - soft.detach())

    @staticmethod
    def gather_slots(Z, cand_mems, budgets):
        """Slot j = the memory prefix of the document selected by row j of Z, truncated to budgets[j].
        Multiplying by Z keeps the straight-through gradient path to the retrieval scores."""
        slots = []
        for j, b in enumerate(budgets):
            stack = torch.stack([c[:b] for c in cand_mems])            # (D, b, H)
            slots.append(torch.einsum("d,dbh->bh", Z[j], stack))
        return slots

    # ------------------------------------------------------------------ save / load
    def meta(self):
        return {"backbone": self.backbone, "model_name": self.model_name, "max_mem": self.max_mem,
                "lora_r": self.lora_r, "max_doc_tokens": self.max_doc_tokens,
                "max_query_tokens": self.max_query_tokens, "max_target_tokens": self.max_target_tokens,
                "rescale_memory": self.rescale_memory}

    def save(self, out_dir, extra_meta=None):
        os.makedirs(out_dir, exist_ok=True)
        torch.save({n: p.detach().cpu() for n, p in self._lora}, os.path.join(out_dir, "lora_state.pt"))
        torch.save({"mem_doc": self.mem_doc.detach().cpu(), "mem_query": self.mem_query.detach().cpu()},
                   os.path.join(out_dir, "mem_embeddings.pt"))
        write_json({**self.meta(), **(extra_meta or {})}, os.path.join(out_dir, "meta.json"))

    def load_state(self, in_dir):
        state = torch.load(os.path.join(in_dir, "lora_state.pt"), map_location=self.device)
        own = dict(self._lora)
        missing = [n for n in own if n not in state]
        with torch.no_grad():
            for n, t in state.items():
                if n in own:
                    own[n].copy_(t.to(self.device))
            mem = torch.load(os.path.join(in_dir, "mem_embeddings.pt"), map_location=self.device)
            self.mem_doc.copy_(mem["mem_doc"].to(self.device))
            self.mem_query.copy_(mem["mem_query"].to(self.device))
        if missing:
            raise RuntimeError(f"{len(missing)} LoRA tensors missing from checkpoint {in_dir}")

    # ------------------------------------------------------------------ backbone-specific API
    def compress(self, text, adapter="compressor", is_query=False):
        raise NotImplementedError

    def gen_loss(self, instruction, slots, target):
        raise NotImplementedError

    def generate(self, instruction, slots, max_new_tokens=24):
        raise NotImplementedError

    def generate_raw(self, prompt, max_new_tokens=24):
        raise NotImplementedError


# ====================================================================== decoder-only: Qwen2.5
class QwenCLaRa(NestedCLaRa):
    lora_targets = ["q_proj", "k_proj", "v_proj", "o_proj"]
    task_type = "CAUSAL_LM"

    def _decoder(self):
        return self.model.get_base_model().model          # transformer body, no LM head

    def _lm_head(self):
        return self.model.get_base_model().lm_head

    def _chat_parts(self, user_text):
        """Split the chat-formatted prompt around the placeholder where memory vectors are inserted."""
        if getattr(self.tokenizer, "chat_template", None):
            s = self.tokenizer.apply_chat_template([{"role": "user", "content": user_text}],
                                                   tokenize=False, add_generation_prompt=True)
        else:
            s = f"User: {user_text}\nAssistant:"
        if MEMORY_PLACEHOLDER in s:
            pre, post = s.split(MEMORY_PLACEHOLDER)
            return pre, post
        return s, ""

    def compress(self, text, adapter="compressor", is_query=False):
        """Input: [passage tokens][m_1 .. m_max]. Output: final hidden states at the memory positions.
        Causal attention means m_i only sees the passage and m_<i, so M[:m] is identical whether or not the
        later memory tokens exist -- the property that makes slicing a stored index valid."""
        ids = self.ids(text, self.max_query_tokens if is_query else self.max_doc_tokens)
        tok = self.embed(ids)
        mem = (self.mem_query if is_query else self.mem_doc).unsqueeze(0)
        x = torch.cat([tok, mem], dim=1)
        self.use(adapter)
        h = self._decoder()(inputs_embeds=x,
                            attention_mask=torch.ones(x.shape[:2], dtype=torch.long, device=self.device)
                            ).last_hidden_state[0]
        T = tok.shape[1]
        return h[T:], h[:T]

    def _build_inputs(self, instruction, slots):
        pre, post = self._chat_parts(f"{instruction}\n{MEMORY_PLACEHOLDER}")
        parts = [self.embed(self.ids(pre))]
        for i, s in enumerate(slots):
            parts.append(self.embed(self.ids(f"{chr(10) if i else ''}[Document {i + 1}] ")))
            if self.rescale_memory:
                # Memory vectors are final-layer (post-norm) states, far larger than input embeddings; in a pre-norm
                # decoder they then dominate their residual stream so later layers barely update them.
                s = s * (self.embed_norm / (s.norm(dim=-1, keepdim=True) + 1e-6))
            parts.append(s.unsqueeze(0))
        if post:
            parts.append(self.embed(self.ids(post)))
        return torch.cat(parts, dim=1)

    def gen_loss(self, instruction, slots, target):
        self.use("generator")
        x = self._build_inputs(instruction, slots)
        tgt = self.tokenizer(target, add_special_tokens=False).input_ids[: self.max_target_tokens - 1]
        tgt = torch.tensor([tgt + [self.tokenizer.eos_token_id]], device=self.device)
        inp = torch.cat([x, self.embed(tgt)], dim=1)
        h = self._decoder()(inputs_embeds=inp,
                            attention_mask=torch.ones(inp.shape[:2], dtype=torch.long, device=self.device)
                            ).last_hidden_state
        L, A = x.shape[1], tgt.shape[1]
        logits = self._lm_head()(h[:, L - 1: L - 1 + A])   # only the positions that predict the target
        return F.cross_entropy(logits.reshape(-1, logits.shape[-1]).float(), tgt.reshape(-1))

    @torch.no_grad()
    def generate(self, instruction, slots, max_new_tokens=24):
        self.use("generator")
        x = self._build_inputs(instruction, slots)
        out = self.model.generate(inputs_embeds=x,
                                  attention_mask=torch.ones(x.shape[:2], dtype=torch.long, device=self.device),
                                  max_new_tokens=max_new_tokens, do_sample=False,
                                  pad_token_id=self.tokenizer.pad_token_id,
                                  eos_token_id=self.tokenizer.eos_token_id)
        return clean_prediction(self.tokenizer.decode(out[0], skip_special_tokens=True))

    @torch.no_grad()
    def generate_raw(self, prompt, max_new_tokens=24):
        """Plain base model (all adapters disabled) reading raw text -- the uncompressed baseline."""
        pre, _ = self._chat_parts(prompt)
        ids = self.ids(pre)
        with self.model.disable_adapter():
            out = self.model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                                      max_new_tokens=max_new_tokens, do_sample=False,
                                      pad_token_id=self.tokenizer.pad_token_id,
                                      eos_token_id=self.tokenizer.eos_token_id)
        return clean_prediction(self.tokenizer.decode(out[0][ids.shape[1]:], skip_special_tokens=True)), ids.shape[1]


# ====================================================================== encoder-decoder: FLAN-T5
class T5CLaRa(NestedCLaRa):
    lora_targets = ["q", "k", "v", "o"]
    task_type = "SEQ_2_SEQ_LM"
    is_encoder_decoder = True

    def __init__(self, *args, causal_memory=True, **kwargs):
        super().__init__(*args, **kwargs)
        # T5's encoder is bidirectional. With causal_memory, memory token i attends to the passage and to memory
        # tokens <= i, and the passage does not attend to memory tokens, so prefixes are independent of later
        # tokens exactly as in the decoder-only case. Mask formats differ across transformers versions, so we
        # probe for one that actually produces this behaviour.
        self.mask_format = self._probe_mask_format() if causal_memory else None
        if causal_memory and self.mask_format is None:
            print("[T5CLaRa] WARNING: no causal memory mask format worked with this transformers version; "
                  "using bidirectional attention. Nesting still works because the full memory set is always "
                  "computed and then sliced, but prefixes are no longer independent of later tokens.")

    def _encoder(self):
        return self.model.get_base_model().get_encoder()

    def _mask(self, T, n, fmt):
        L = T + n
        allowed = torch.zeros(L, L, dtype=torch.bool, device=self.device)
        allowed[:, :T] = True
        allowed[T:, T:] = torch.tril(torch.ones(n, n, dtype=torch.bool, device=self.device))
        if fmt == "4d_bool":
            return allowed[None, None]
        if fmt == "3d_float":
            return allowed[None].float()
        if fmt == "4d_additive":
            return torch.where(allowed, 0.0, torch.finfo(torch.float32).min)[None, None]
        raise ValueError(fmt)

    @torch.no_grad()
    def _probe_mask_format(self):
        T, n, H = 5, 6, self.hidden_size
        x = torch.randn(1, T + n, H, device=self.device)
        x2 = x.clone()
        x2[:, T + 3:] += 3.0                       # perturb memory tokens 4..6
        was_training = self.model.training
        self.model.eval()
        self.model.set_adapter("compressor")
        try:
            for fmt in ("4d_bool", "3d_float", "4d_additive"):
                try:
                    h1 = self._encoder()(inputs_embeds=x, attention_mask=self._mask(T, n, fmt)).last_hidden_state
                    h2 = self._encoder()(inputs_embeds=x2, attention_mask=self._mask(T, n, fmt)).last_hidden_state
                    if torch.allclose(h1[:, :T + 3], h2[:, :T + 3], atol=1e-4) and \
                            not torch.allclose(h1[:, T + 3:], h2[:, T + 3:], atol=1e-4):
                        return fmt
                except Exception:
                    continue
            return None
        finally:
            self.model.train(was_training)

    def compress(self, text, adapter="compressor", is_query=False):
        ids = self.ids(text, self.max_query_tokens if is_query else self.max_doc_tokens)
        tok = self.embed(ids)
        mem = (self.mem_query if is_query else self.mem_doc).unsqueeze(0)
        x = torch.cat([tok, mem], dim=1)
        T, n = tok.shape[1], mem.shape[1]
        mask = self._mask(T, n, self.mask_format) if self.mask_format else \
            torch.ones(x.shape[:2], dtype=torch.long, device=self.device)
        self.use(adapter)
        h = self._encoder()(inputs_embeds=x, attention_mask=mask).last_hidden_state[0]
        return h[T:], h[:T]

    def _encoder_outputs(self, instruction, slots):
        """Decoder cross-attends over [generator-encoded instruction ; memory vectors of each slot]."""
        self.use("generator")
        ids = self.ids(instruction, max_len=self.max_query_tokens * 2)
        ih = self._encoder()(inputs_embeds=self.embed(ids),
                             attention_mask=torch.ones_like(ids)).last_hidden_state
        comb = torch.cat([ih] + [s.unsqueeze(0) for s in slots], dim=1)
        mask = torch.ones(comb.shape[:2], dtype=torch.long, device=self.device)
        return BaseModelOutput(last_hidden_state=comb), mask

    def gen_loss(self, instruction, slots, target):
        enc, mask = self._encoder_outputs(instruction, slots)
        labels = self.ids(target, max_len=self.max_target_tokens, add_special_tokens=True)
        return self.model(encoder_outputs=enc, attention_mask=mask, labels=labels).loss

    @torch.no_grad()
    def generate(self, instruction, slots, max_new_tokens=24):
        enc, mask = self._encoder_outputs(instruction, slots)
        out = self.model.generate(encoder_outputs=enc, attention_mask=mask,
                                  max_new_tokens=max_new_tokens, do_sample=False)
        return clean_prediction(self.tokenizer.decode(out[0], skip_special_tokens=True))

    @torch.no_grad()
    def generate_raw(self, prompt, max_new_tokens=24):
        ids = self.ids(prompt, max_len=512, add_special_tokens=True)
        with self.model.disable_adapter():
            out = self.model.generate(input_ids=ids, attention_mask=torch.ones_like(ids),
                                      max_new_tokens=max_new_tokens, do_sample=False)
        return clean_prediction(self.tokenizer.decode(out[0], skip_special_tokens=True)), ids.shape[1]


# ====================================================================== factory
def load_model(backbone, max_mem=32, lora_r=16, model_name=None, device="cpu", tiny=False, **kwargs):
    if tiny:
        from .tiny import build_tiny_backbone
        base, tok, model_name = build_tiny_backbone(backbone)
    else:
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
        model_name = model_name or resolve_model(backbone)
        tok = AutoTokenizer.from_pretrained(model_name)
        cls = AutoModelForSeq2SeqLM if backbone == "t5" else AutoModelForCausalLM
        base = cls.from_pretrained(model_name, torch_dtype=torch.float32)
    model_cls = T5CLaRa if backbone == "t5" else QwenCLaRa
    return model_cls(base, tok, backbone=backbone, model_name=model_name, max_mem=max_mem,
                     lora_r=lora_r, device=device, **kwargs)


def load_from_checkpoint(ckpt_dir, device="cpu", tiny=False):
    meta = read_json(os.path.join(ckpt_dir, "meta.json"))
    model = load_model(meta["backbone"], max_mem=meta["max_mem"], lora_r=meta["lora_r"],
                       model_name=None if tiny else meta["model_name"], device=device, tiny=tiny,
                       max_doc_tokens=meta.get("max_doc_tokens", 256),
                       max_query_tokens=meta.get("max_query_tokens", 64),
                       max_target_tokens=meta.get("max_target_tokens", 96),
                       rescale_memory=meta.get("rescale_memory", False))
    model.load_state(ckpt_dir)
    return model, meta
