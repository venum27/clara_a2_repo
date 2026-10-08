"""Readiness check for Flair 2 (run via ./scripts/00_setup_check.sh).

Checks Python packages, GPUs, both backbones (actually loaded; downloaded first if missing), the data synthesiser's
files, and both datasets (actually loaded). Prints PASS/FAIL per item with what to do, and writes setup_report.txt.
"""
import glob
import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup_report.txt")
lines, results = [], []


def out(s=""):
    print(s, flush=True)
    lines.append(str(s))


def check(name, ok, detail, fix=None):
    results.append((name, ok))
    out(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")
    if not ok and fix:
        out(f"       -> {fix}")


def version_ok(mod, minimum):
    from packaging.version import Version
    v = getattr(mod, "__version__", "0").split("+")[0]
    return Version(v) >= Version(minimum), v


out(f"Flair 2 setup check, {time.strftime('%Y-%m-%d %H:%M')} | python {sys.version.split()[0]} ({sys.executable})")
out(f"downloads allowed: {os.environ.get('HF_HUB_OFFLINE', '0') != '1'}")

# ------------------------------------------------------------------------------------------ packages
out("\n== packages")
for name, minimum in [("torch", "2.1"), ("transformers", "4.43"), ("peft", "0.12"), ("accelerate", "0.30"),
                      ("datasets", "2.16"), ("huggingface_hub", "0.23"), ("tokenizers", "0.19"),
                      ("numpy", "1.24"), ("tqdm", "4.0")]:
    try:
        mod = __import__(name)
        ok, v = version_ok(mod, minimum)
        check(name, ok, f"{v} (need >= {minimum})", "python3 -m pip install --user " + name)
    except Exception as e:
        check(name, False, f"not importable ({type(e).__name__})", "python3 -m pip install --user " + name)
try:
    import rank_bm25  # noqa: F401
    check("rank_bm25", True, "installed")
except Exception:
    check("rank_bm25", False, "missing", "needed for the BM25 baseline")

# ------------------------------------------------------------------------------------------ GPUs
out("\n== GPUs")
try:
    import torch
    ok = torch.cuda.is_available()
    check("CUDA", ok, f"torch {torch.__version__} built for CUDA {torch.version.cuda}; available: {ok}")
    if ok:
        for i in range(torch.cuda.device_count()):
            f, t = torch.cuda.mem_get_info(i)
            out(f"       GPU {i}: {torch.cuda.get_device_name(i)}, {f / 2**30:.1f} of {t / 2**30:.1f} GiB free, "
                f"bf16 {torch.cuda.is_bf16_supported()}")
except Exception as e:
    check("CUDA", False, f"{type(e).__name__}: {e}")

# ------------------------------------------------------------------------------------------ backbones
out("\n== backbones (loaded for real, on CPU; downloaded first if missing)")
from nclara.modeling import BACKBONE_MODELS, resolve_model  # noqa: E402

DOWNLOAD_HINT = ("the model could not be loaded or downloaded; check the internet login, then run this check "
                 "again (it downloads missing models automatically)")
for bb in ("qwen", "t5"):
    src = resolve_model(bb)
    try:
        from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(src)
        cls = AutoModelForSeq2SeqLM if bb == "t5" else AutoModelForCausalLM
        model = cls.from_pretrained(src)
        n = sum(p.numel() for p in model.parameters())
        ids = tok("Paris is the capital of France.", return_tensors="pt").input_ids
        check(f"backbone {bb}", True, f"{src} | {n / 1e6:.0f}M parameters | tokenizer {type(tok).__name__} "
                                      f"({ids.shape[1]} tokens for a test sentence)")
        del model
    except Exception as e:
        check(f"backbone {bb}", False, f"{src}: {type(e).__name__}: {str(e)[:200]}",
              DOWNLOAD_HINT)

# ------------------------------------------------------------------------------------------ synthesiser
out("\n== data synthesiser (files checked, not loaded)")
synth = os.environ.get("SYNTH", "Qwen/Qwen2.5-14B-Instruct")
try:
    from huggingface_hub import snapshot_download
    path = synth if os.path.isdir(synth) else snapshot_download(synth, local_files_only=True)
    idx = glob.glob(os.path.join(path, "*.safetensors.index.json"))
    if idx:
        shards = sorted(set(json.load(open(idx[0]))["weight_map"].values()))
        absent = [s for s in shards if not os.path.exists(os.path.join(path, s))]
    else:
        shards = glob.glob(os.path.join(path, "*.safetensors"))
        absent = [] if shards else ["model.safetensors"]
    has_tok = any(os.path.exists(os.path.join(path, f)) for f in ("tokenizer.json", "vocab.json"))
    size = sum(os.path.getsize(os.path.join(path, s)) for s in shards if os.path.exists(os.path.join(path, s)))
    check(f"synthesiser {synth}", not absent and has_tok,
          f"{len(shards) - len(absent)}/{len(shards)} weight files, {size / 2**30:.1f} GiB, tokenizer: {has_tok}",
          f"incomplete download; step 1 completes it automatically, or choose another model with SYNTH=...")
except Exception as e:
    check(f"synthesiser {synth}", False, f"not downloaded yet ({type(e).__name__})",
          "it downloads automatically in step 1, or set SYNTH to one of the cached models listed below")
hub = os.path.join(os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface")), "hub")
cached = sorted(d.replace("models--", "").replace("--", "/") for d in os.listdir(hub) if d.startswith("models--")) \
    if os.path.isdir(hub) else []
out(f"       cached models: {', '.join(cached) if cached else '(none)'}")

# ------------------------------------------------------------------------------------------ datasets
out("\n== datasets (loaded; downloaded first if missing)")
from prepare_data import HF_DATASET_ID, flatten_context  # noqa: E402

for name, spec in HF_DATASET_ID.items():
    try:
        from nclara.hfdata import load_split
        ds = load_split(spec["path"], spec["name"], "validation")
        titles, paragraphs, gold = flatten_context(ds[0])
        check(f"dataset {name}", len(ds) > 1000 and len(gold) > 0,
              f"{spec['path']} ({spec['name'] or 'default'}) validation: {len(ds)} questions; first one has "
              f"{len(paragraphs)} paragraphs, {len(gold)} gold")
    except Exception as e:
        check(f"dataset {name}", False, f"{type(e).__name__}: {str(e)[:200]}",
              "could not be loaded; check the internet login and run this check again")

# ------------------------------------------------------------------------------------------ disk
out("\n== disk")
free = shutil.disk_usage(os.path.expanduser("~")).free / 2**30
check("disk space", free > 20, f"{free:.0f} GiB free in home (runs need a few GiB)")

# ------------------------------------------------------------------------------------------ summary
failed = [n for n, ok in results if not ok]
out("\n" + "=" * 60)
out("ALL CHECKS PASSED -- next: ./scripts/01_prepare_data.sh" if not failed
    else f"{len(failed)} check(s) failed: {', '.join(failed)}")
out("=" * 60)
open(REPORT, "w").write("\n".join(lines) + "\n")
print(f"report saved to {REPORT}")
