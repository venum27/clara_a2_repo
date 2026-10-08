"""Tiny randomly-initialised backbones + a toy multi-hop dataset, used only for CPU smoke tests (`--tiny`).

They let the whole pipeline (data -> SCP -> end-to-end -> evaluation) run in a few minutes without a GPU or any
downloads, so plumbing bugs are caught before spending Colab time. Numbers produced in tiny mode are meaningless.
"""
import random

N_PEOPLE, N_CITIES = 60, 20
_WORDS = (["where", "does", "live", "lives", "in", "is", "a", "friend", "of", "the", "was", "born", "and",
           "?", ".", ":", "[", "]", "answer", "question", "based", "on", "document", "using", "retrieved",
           "documents", "rewrite", "your", "own", "words", "paraphrase", "context", "only", "be", "brief",
           "who", "what", "year", "user", "assistant", "that", "person", "city", "home", "one", "which",
           "friends", "with", "resides", "town"]
          + [f"person{i}" for i in range(N_PEOPLE)] + [f"city{i}" for i in range(N_CITIES)]
          + [str(i) for i in range(10)] + [f"{y}" for y in range(1900, 2000)])


def build_tokenizer(for_t5=False):
    from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, processors
    from transformers import PreTrainedTokenizerFast
    specials = ["<pad>", "</s>", "<unk>", "<user>", "<assistant>"]
    vocab = {w: i for i, w in enumerate(specials + _WORDS)}
    tk = Tokenizer(models.WordLevel(vocab=vocab, unk_token="<unk>"))
    tk.normalizer = normalizers.Lowercase()
    tk.pre_tokenizer = pre_tokenizers.Sequence([pre_tokenizers.WhitespaceSplit(),
                                                pre_tokenizers.Punctuation()])
    if for_t5:
        tk.post_processor = processors.TemplateProcessing(single="$A </s>", special_tokens=[("</s>", 1)])
    tok = PreTrainedTokenizerFast(tokenizer_object=tk, pad_token="<pad>", eos_token="</s>", unk_token="<unk>")
    if not for_t5:
        tok.chat_template = ("{% for m in messages %}<user> {{ m['content'] }} {% endfor %}"
                             "{% if add_generation_prompt %}<assistant> {% endif %}")
    return tok


def build_tiny_backbone(backbone):
    import torch
    torch.manual_seed(0)
    if backbone == "t5":
        from transformers import T5Config, T5ForConditionalGeneration
        tok = build_tokenizer(for_t5=True)
        cfg = T5Config(vocab_size=len(tok), d_model=64, d_kv=16, d_ff=128, num_layers=2, num_decoder_layers=2,
                       num_heads=4, decoder_start_token_id=0, pad_token_id=0, eos_token_id=1)
        return T5ForConditionalGeneration(cfg), tok, "tiny-t5"
    from transformers import Qwen2Config, Qwen2ForCausalLM
    tok = build_tokenizer(for_t5=False)
    cfg = Qwen2Config(vocab_size=len(tok), hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=512,
                      tie_word_embeddings=True, pad_token_id=0, eos_token_id=1, bos_token_id=1)
    return Qwen2ForCausalLM(cfg), tok, "tiny-qwen"


def make_fake_records(n, seed, id_prefix):
    """Two-hop questions: 'where does the friend of person_a live ?' needs doc A (friendship) + doc B (city)."""
    rng = random.Random(seed)
    records = []
    for i in range(n):
        a, b = rng.sample(range(N_PEOPLE), 2)
        city = rng.randrange(N_CITIES)
        gold = [f"person{a} is a friend of person{b} . person{a} was born in {rng.randrange(1900, 2000)} .",
                f"person{b} lives in city{city} . person{b} was born in {rng.randrange(1900, 2000)} ."]
        distractors = []
        while len(distractors) < 8:
            p, c = rng.randrange(N_PEOPLE), rng.randrange(N_CITIES)
            if p in (a, b):
                continue
            distractors.append(f"person{p} lives in city{c} . person{p} was born in {rng.randrange(1900, 2000)} .")
        paragraphs = gold + distractors
        order = list(range(10))
        rng.shuffle(order)
        paragraphs = [paragraphs[j] for j in order]
        gold_idx = [order.index(0), order.index(1)]
        records.append({"id": f"{id_prefix}{i}", "question": f"where does the friend of person{a} live ?",
                        "answer": f"city{city}", "titles": [f"t{j}" for j in range(10)],
                        "paragraphs": paragraphs, "gold_idx": sorted(gold_idx), "type": "bridge"})
    return records


def fake_synthetic(records, heldout_frac=0.1, seed=0):
    """Stand-in for LLM-generated SCP data: template QA pairs and a reworded paraphrase per gold passage."""
    rng = random.Random(seed)
    docs, seen = [], set()
    for rec in records:
        for gi in rec["gold_idx"]:
            doc = rec["paragraphs"][gi]
            if doc in seen:
                continue
            seen.add(doc)
            w = doc.split()
            qa, complex_qa = [], []
            if "lives" in w:
                person, city, year = w[0], w[3], w[-2]
                qa.append({"question": f"where does {person} live ?", "answer": city})
                qa.append({"question": f"what year was {person} born ?", "answer": year})
                complex_qa.append({"question": f"which city is home to the person born in {year} ?", "answer": city})
                para = f"{city} is where {person} resides . {year} is the year {person} was born ."
            else:
                person, friend, year = w[0], w[5], w[-2]
                qa.append({"question": f"who is a friend of {person} ?", "answer": friend})
                qa.append({"question": f"what year was {person} born ?", "answer": year})
                complex_qa.append({"question": f"who is friends with the person born in {year} ?", "answer": friend})
                para = f"{friend} is friends with {person} . {person} was born in {year} ."
            docs.append({"doc_id": f"d{len(docs)}", "document": doc, "simple_qa": qa, "complex_qa": complex_qa,
                         "paraphrase": para, "split": "heldout" if rng.random() < heldout_frac else "train"})
    return docs
