"""Shared loaders for the Phase 5 local-FT diagnosis analysis (docs/phase5/LOCAL_FT_DIAGNOSIS.md).
Read-only against experiments/phase5_local_ft and results/phase5_local_ft -- never edits
earlier phases' code or results. New outputs go under results/phase5_local_ft/analysis/.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE5_DIR = ROOT / "experiments" / "phase5_local_ft"
RESULTS_DIR = ROOT / "results" / "phase5_local_ft"
RAW_DIR = RESULTS_DIR / "raw"
ANALYSIS_OUT = RESULTS_DIR / "analysis"
ANALYSIS_OUT.mkdir(parents=True, exist_ok=True)
FIGS_DIR = ROOT / "docs" / "phase5" / "figs"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

for p in (str(PHASE5_DIR),):
    if p not in sys.path:
        sys.path.insert(0, p)

import phase5_config as config  # noqa: E402
from data_io import load_poem, ALI_POEMS_DIR, positive_verses_by_subtype  # noqa: E402

with open(PHASE5_DIR / "config" / "targets.json", encoding="utf-8") as f:
    _TARGETS_JSON = json.load(f)
TARGETS = _TARGETS_JSON["targets"]
TARGETS_BY_LEVEL = {t["level"]: t for t in TARGETS}
LEVEL_ORDER = ["very_easy", "easy", "medium", "hard", "very_hard"]
MODEL_KEYS = list(config.MODELS)
SEEDS = config.SEEDS


def load_run(target_level, model_key, split_name, seed):
    path = RAW_DIR / f"{target_level}__{model_key}__{split_name}__seed{seed}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline(target_level, split_name, seed):
    path = RAW_DIR / f"baselines__{target_level}__{split_name}__seed{seed}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


_POEM_CACHE = {}


def get_poem(poem_id: str) -> dict:
    if poem_id not in _POEM_CACHE:
        matches = list(ALI_POEMS_DIR.glob(f"{poem_id}_*.json"))
        if not matches:
            raise FileNotFoundError(poem_id)
        _POEM_CACHE[poem_id] = load_poem(matches[0])
    return _POEM_CACHE[poem_id]


def split_poem_ids(split_name, seed):
    path = PHASE5_DIR / "splits" / f"{split_name}_seed{seed}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def poems_with_positive(poem_ids, target_value):
    """Count of poems (out of poem_ids) with >=1 positive verse for this subtype."""
    n = 0
    for pid in poem_ids:
        poem = get_poem(pid)
        pos = positive_verses_by_subtype(poem).get(target_value, set())
        if pos:
            n += 1
    return n


def split_verse_poem_counts(split_name, seed, target_value):
    """Returns dict with per-split (train/val/test) verse and poem counts, pos and total."""
    ids = split_poem_ids(split_name, seed)
    out = {}
    for part in ("train", "val", "test"):
        pids = ids.get(part, [])
        n_poems = len(pids)
        n_verses = 0
        n_pos_verses = 0
        n_pos_poems = 0
        for pid in pids:
            poem = get_poem(pid)
            n_verses += poem["verse_count"]
            pos = positive_verses_by_subtype(poem).get(target_value, set())
            if pos:
                n_pos_poems += 1
            n_pos_verses += len(pos)
        out[part] = {
            "n_poems": n_poems, "n_pos_poems": n_pos_poems,
            "n_verses": n_verses, "n_pos_verses": n_pos_verses,
            "n_neg_verses": n_verses - n_pos_verses,
            "n_neg_poems": n_poems - n_pos_poems,
        }
    return out
