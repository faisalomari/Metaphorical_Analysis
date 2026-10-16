"""Step 4: evaluation on TEST only. Aggregates the 3-seed runs per
target x model x split into mean+-std F1 (+ raw TP/FP/FN), and a bootstrap
95% CI over poems (pooled across the 3 seeds' test predictions) for S2/S3.
No training, no API calls -- reads results/phase5_local_ft/raw/*.json only.
"""
import json
import random
import statistics as stats

import phase5_config as config
from metrics_utils import prf

N_BOOT = 2000
BOOT_SEED = 0

with open(config.CONFIG_DIR / "targets.json", encoding="utf-8") as f:
    TARGETS = json.load(f)["targets"]
TARGET_LEVELS = [t["level"] for t in TARGETS]


def load_run(target_level, model_key, split_name, seed):
    path = config.RAW_RESULTS_DIR / f"{target_level}__{model_key}__{split_name}__seed{seed}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline(target_level, split_name, seed):
    path = config.RAW_RESULTS_DIR / f"baselines__{target_level}__{split_name}__seed{seed}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def bootstrap_ci_over_poems(runs: list, n_boot=N_BOOT, seed=BOOT_SEED):
    """runs: list of per-seed result dicts (each with "predictions": [{poem_id,label,pred},...]).
    Pools predictions across all given seeds, resamples POEM IDS with replacement
    (same method/params as the project's existing verse_analysis.bootstrap_pair:
    seed=0, 2000 iters, resample-over-poems), recomputing pooled F1 each draw."""
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
    lo = f1s[int(0.025 * n_boot)]
    hi = f1s[int(0.975 * n_boot) - 1]
    return {"ci_low": lo, "ci_high": hi, "n_boot": n_boot}


def aggregate_cell(target_level, model_key, split_name, seeds=config.SEEDS):
    runs = [load_run(target_level, model_key, split_name, s) for s in seeds]
    runs = [r for r in runs if r is not None]
    if not runs:
        return None
    f1s = [r["test_metrics"]["f1"] for r in runs]
    ps = [r["test_metrics"]["precision"] for r in runs]
    rs = [r["test_metrics"]["recall"] for r in runs]
    tp = sum(r["test_metrics"]["tp"] for r in runs)
    fp = sum(r["test_metrics"]["fp"] for r in runs)
    fn = sum(r["test_metrics"]["fn"] for r in runs)
    cell = {
        "target_level": target_level, "model": model_key, "split": split_name, "n_seeds": len(runs),
        "f1_mean": stats.mean(f1s), "f1_std": stats.pstdev(f1s) if len(f1s) > 1 else 0.0,
        "precision_mean": stats.mean(ps), "recall_mean": stats.mean(rs),
        "tp_sum": tp, "fp_sum": fp, "fn_sum": fn,
        "f1_per_seed": f1s,
    }
    if split_name in ("S2", "S3"):
        boot = bootstrap_ci_over_poems(runs)
        cell["bootstrap_ci"] = boot
    return cell


def print_full_table():
    print(f"{'level':<10}{'model':<14}{'split':<5}{'F1 mean+-std':<18}{'P':<7}{'R':<7}{'TP/FP/FN':<14}{'boot CI'}")
    for split_name in ["S1", "S2", "S3"]:
        levels = ["medium"] if split_name == "S3" else TARGET_LEVELS
        for level in levels:
            for model_key in config.MODELS:
                cell = aggregate_cell(level, model_key, split_name)
                if cell is None:
                    continue
                ci = cell.get("bootstrap_ci")
                ci_str = f"[{ci['ci_low']:.3f},{ci['ci_high']:.3f}]" if ci else "-"
                print(f"{level:<10}{model_key:<14}{split_name:<5}"
                      f"{cell['f1_mean']:.3f}+-{cell['f1_std']:.3f}   "
                      f"{cell['precision_mean']:.3f}  {cell['recall_mean']:.3f}  "
                      f"{cell['tp_sum']}/{cell['fp_sum']}/{cell['fn_sum']:<8}{ci_str}")


if __name__ == "__main__":
    print_full_table()
