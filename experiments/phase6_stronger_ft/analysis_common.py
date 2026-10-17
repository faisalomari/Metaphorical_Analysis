"""Shared loaders for Phase 6 analysis/selection scripts. Phase 5's raw/*.json
files (format `{target}__{model_key}__{split}__seed{N}.json`, config implicitly
"baseline" = verse-alone + bce_pos_weight + constant schedule) and Phase 6's
own raw/*.json (format `{target}__{model_key}__{config_name}__{split}__seed
{N}.json`) are both readable through one `load_cell()` call, so every
downstream script can treat "Phase 5 baseline" as just another config cell
instead of a special case."""
import json
import random
from pathlib import Path

import phase6_config as config

PHASE5_RAW_DIR = config.PHASE6_DIR.parents[1] / "results" / "phase5_local_ft" / "raw"
PHASE6_RAW_DIR = config.RAW_RESULTS_DIR

BASELINE_CONFIG_NAME = "ctx0_bce_pos_weight_constant"  # Phase 5's recipe, under Phase 6's naming scheme


def load_cell(target_level: str, model_key: str, config_name: str, split_name: str, seed: int):
    """config_name=BASELINE_CONFIG_NAME + a Phase-5-native model_key (camelbert_ca/
    arabert_v2/marbert) resolves to the existing Phase 5 raw file (no retrain).
    Anything else resolves to a Phase 6 raw file."""
    if config_name == BASELINE_CONFIG_NAME and model_key in ("camelbert_ca", "arabert_v2", "marbert"):
        path = PHASE5_RAW_DIR / f"{target_level}__{model_key}__{split_name}__seed{seed}.json"
    else:
        path = PHASE6_RAW_DIR / f"{target_level}__{model_key}__{config_name}__{split_name}__seed{seed}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def all_seeds_cell(target_level: str, model_key: str, config_name: str, split_name: str, seeds=None):
    seeds = seeds if seeds is not None else config.SEEDS
    runs = [load_cell(target_level, model_key, config_name, split_name, s) for s in seeds]
    return [r for r in runs if r is not None]


def bootstrap_ci_over_poems(runs: list, n_boot: int = 2000, seed: int = 0):
    """Same method/params as Phase 5's own analyze.py / analysis/section2_variance.py."""
    from metrics_utils import prf
    by_poem = {}
    for run in runs:
        for p in run["predictions"]:
            by_poem.setdefault(p["poem_id"], []).append((p["label"], p["pred"]))
    poem_ids = list(by_poem)
    if not poem_ids:
        return None
    rng = random.Random(seed)
    f1s = []
    for _ in range(n_boot):
        sample = rng.choices(poem_ids, k=len(poem_ids))
        y_true, y_pred = [], []
        for pid in sample:
            for lab, pred in by_poem[pid]:
                y_true.append(lab)
                y_pred.append(pred)
        f1s.append(prf(y_true, y_pred)["f1"])
    f1s.sort()
    point = prf([lab for pid in poem_ids for lab, _ in by_poem[pid]],
                [pred for pid in poem_ids for _, pred in by_poem[pid]])["f1"]
    return {"point": point, "ci_low": f1s[int(0.025 * n_boot)], "ci_high": f1s[int(0.975 * n_boot) - 1],
            "n_boot": n_boot, "n_poems": len(poem_ids)}


def pool_predictions(runs: list):
    labels, probs, preds = [], [], []
    for r in runs:
        for p in r["predictions"]:
            labels.append(p["label"])
            probs.append(p["prob"])
            preds.append(p["pred"])
    return labels, probs, preds
