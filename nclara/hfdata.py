"""Load one split of a Hugging Face dataset as a list of plain dicts, robust to `datasets` version mismatches.

Why: the dataset metadata (both on the Hub and in caches written by datasets>=4) uses the column type name "List".
datasets 2.x does not know it; its lookup falls back to typing.List and crashes with
"TypeError: must be called with a dataclass type or instance". That metadata is only needed to rebuild column types,
which plain Python dicts do not need, so on failure we read the data files directly with pyarrow:

  1. datasets.load_dataset (normal path; works when versions match)
  2. the cached Arrow files in ~/.cache/huggingface/datasets (no network)
  3. the dataset's parquet files from the Hub (needs internet)
"""
import glob
import os


def _cache_roots():
    roots = [os.environ.get("HF_DATASETS_CACHE")]
    hf_home = os.environ.get("HF_HOME")
    if hf_home:
        roots.append(os.path.join(hf_home, "datasets"))
    roots.append(os.path.expanduser("~/.cache/huggingface/datasets"))
    return [r for r in roots if r and os.path.isdir(r)]


def _read_arrow(files):
    import pyarrow as pa
    tables = []
    for f in sorted(files):
        with pa.memory_map(f) as src:
            try:
                tables.append(pa.ipc.open_stream(src).read_all())      # what datasets writes
            except pa.ArrowInvalid:
                tables.append(pa.ipc.open_file(src).read_all())
    return pa.concat_tables(tables).to_pylist()


def _from_arrow_cache(path, name, split):
    namespace = path.split("/")[0].lower()
    config = name or "default"
    for root in _cache_roots():
        for ds_dir in glob.glob(os.path.join(root, f"{namespace}___*")):
            cfg = os.path.join(ds_dir, config)
            if not os.path.isdir(cfg):
                continue
            versions = sorted(glob.glob(os.path.join(cfg, "*", "*")), key=os.path.getmtime, reverse=True)
            for v in versions:                                   # newest cached build first
                # datasets names them <builder>-<split>.arrow or <builder>-<split>-00000-of-00003.arrow
                files = glob.glob(os.path.join(v, f"*-{split}.arrow")) + \
                    glob.glob(os.path.join(v, f"*-{split}-*-of-*.arrow"))
                if files:
                    return _read_arrow(files), v
    return None, None


def _from_hub_parquet(path, name, split):
    import pyarrow.parquet as pq
    from huggingface_hub import snapshot_download
    local = snapshot_download(path, repo_type="dataset", allow_patterns=["*.parquet"])
    files = [f for f in glob.glob(os.path.join(local, "**", "*.parquet"), recursive=True)
             if os.path.basename(f).startswith(split) or f"/{split}/" in f or f"{split}-" in os.path.basename(f)]
    if name:
        in_config = [f for f in files if f"{os.sep}{name}{os.sep}" in f]
        files = in_config or files
    if not files:
        return None, None
    import pyarrow as pa
    return pa.concat_tables([pq.read_table(f) for f in sorted(files)]).to_pylist(), os.path.dirname(files[0])


def load_split(path, name, split, verbose=True):
    """Rows of one split as a list of dicts (same structure as a Hugging Face Dataset's rows)."""
    errors = []
    try:
        from datasets import load_dataset
        ds = load_dataset(path, name, split=split) if name else load_dataset(path, split=split)
        return [ds[i] for i in range(len(ds))]
    except Exception as e:
        errors.append(f"datasets.load_dataset: {type(e).__name__}: {str(e)[:120]}")
    try:
        rows, where = _from_arrow_cache(path, name, split)
        if rows is not None:
            if verbose:
                print(f"[data] loaded {path} ({name or 'default'}, {split}) from the cached Arrow files in {where} "
                      f"({len(rows)} rows); the datasets library could not parse its metadata")
            return rows
        errors.append("Arrow cache: no cached files for this config/split")
    except Exception as e:
        errors.append(f"Arrow cache: {type(e).__name__}: {str(e)[:120]}")
    if os.environ.get("HF_HUB_OFFLINE") != "1":
        try:
            rows, where = _from_hub_parquet(path, name, split)
            if rows is not None:
                if verbose:
                    print(f"[data] loaded {path} ({name or 'default'}, {split}) from the Hub's parquet files ({len(rows)} rows)")
                return rows
            errors.append("Hub parquet: no matching parquet files")
        except Exception as e:
            errors.append(f"Hub parquet: {type(e).__name__}: {str(e)[:120]}")
    raise RuntimeError(f"could not load {path} ({name or 'default'}, {split}):\n  " + "\n  ".join(errors))
