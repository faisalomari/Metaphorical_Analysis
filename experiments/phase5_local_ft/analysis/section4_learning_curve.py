"""Section 4: data-size hypothesis. NEW local-only training runs (no API
calls): learning curve for "easy" (استعارة تمثيلية) and "medium"
(استعارة فعل) targets, training on 10/25/50/100% of each S2 seed's TRAIN
poems (val/test held fixed, unchanged from that seed's real S2 split), 3
seeds, MARBERT only (the model that won 4/5 targets in the main S2 grid).
Does not edit experiments/phase5_local_ft/train.py -- duplicates its core
loop here (imports its dataset/model helpers) so the frozen Phase 5 code and
results stay untouched. Outputs go to results/phase5_local_ft/analysis/raw_lc/
and results/phase5_local_ft/analysis/section4_*.
"""
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from common import ANALYSIS_OUT, FIGS_DIR, PHASE5_DIR, load_run, split_poem_ids

sys.path.insert(0, str(PHASE5_DIR))
import phase5_config as config  # noqa: E402
from dataset import build_examples  # noqa: E402
from metrics_utils import best_threshold, prf  # noqa: E402
from train import VerseDataset, predict_probs, set_seed  # noqa: E402

RAW_LC_DIR = ANALYSIS_OUT / "raw_lc"
RAW_LC_DIR.mkdir(parents=True, exist_ok=True)

FRACTIONS = [0.10, 0.25, 0.50, 1.00]
TARGET_LEVELS = ["easy", "medium"]
MODEL_KEY = "marbert"
SPLIT_NAME = "S2"
MAX_EPOCHS_LC = 15  # same as main grid; early stopping still applies


def subset_train_ids(all_train_ids, frac, seed):
    """Nested prefixes: shuffle once per seed, take a growing prefix as frac grows,
    so 10% subset of 25% subset of 50% subset of 100% (reduces run-to-run draw noise
    when comparing fractions for the same seed)."""
    rng = random.Random(seed * 1000 + 7)
    order = list(all_train_ids)
    rng.shuffle(order)
    k = max(1, round(frac * len(order)))
    return order[:k]


def run_one(target_level, target_value, frac, seed, force=False):
    out_path = RAW_LC_DIR / f"{target_level}__{MODEL_KEY}__frac{int(frac*100)}__seed{seed}.json"
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing.get("complete"):
            return existing

    ids = split_poem_ids(SPLIT_NAME, seed)
    train_ids = subset_train_ids(ids["train"], frac, seed)
    val_ids = ids["val"]
    test_ids = ids["test"]

    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_ex = build_examples(train_ids, target_value)
    val_ex = build_examples(val_ids, target_value)
    test_ex = build_examples(test_ids, target_value)

    train_pos = sum(e["label"] for e in train_ex)
    train_neg = len(train_ex) - train_pos
    pos_weight_value = (train_neg / train_pos) if train_pos else 1.0

    model_name = config.MODELS[MODEL_KEY]
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_ds = VerseDataset(train_ex, tokenizer, config.MAX_LEN)
    val_ds = VerseDataset(val_ex, tokenizer, config.MAX_LEN)
    test_ds = VerseDataset(test_ex, tokenizer, config.MAX_LEN)

    train_loader = DataLoader(train_ds, batch_size=config.BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=0)

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.LR, weight_decay=config.WEIGHT_DECAY)
    scaler = torch.amp.GradScaler("cuda")
    pos_weight_t = torch.tensor([pos_weight_value], device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight_t)

    val_labels = [e["label"] for e in val_ex]
    test_labels = [e["label"] for e in test_ex]

    best_val_f1 = -1.0
    best_state = None
    best_epoch = -1
    epochs_no_improve = 0
    epoch_log = []
    t_start = time.time()

    for epoch in range(1, MAX_EPOCHS_LC + 1):
        model.train()
        running_loss = 0.0
        for input_ids, attention_mask, labels in train_loader:
            input_ids, attention_mask, labels = input_ids.to(device), attention_mask.to(device), labels.to(device)
            optimizer.zero_grad()
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(input_ids=input_ids, attention_mask=attention_mask).logits.squeeze(-1)
                loss = loss_fn(logits.float(), labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            running_loss += loss.item() * len(labels)

        val_probs = predict_probs(model, val_loader, device)
        val_best = best_threshold(val_labels, val_probs, config.THRESHOLD_GRID)
        epoch_log.append({"epoch": epoch, "train_loss": running_loss / max(1, len(train_ex)),
                           "val_f1": val_best["f1"], "val_threshold": val_best["threshold"]})
        if val_best["f1"] > best_val_f1:
            best_val_f1 = val_best["f1"]
            best_epoch = epoch
            best_state = {k: v.detach().clone().cpu() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= config.EARLY_STOP_PATIENCE:
                break

    total_train_seconds = time.time() - t_start
    model.load_state_dict(best_state)
    model.to(device)

    val_probs = predict_probs(model, val_loader, device)
    val_best = best_threshold(val_labels, val_probs, config.THRESHOLD_GRID)
    threshold = val_best["threshold"]

    test_probs = predict_probs(model, test_loader, device)
    test_pred = [1 if p >= threshold else 0 for p in test_probs]
    test_metrics = prf(test_labels, test_pred)
    auc = roc_auc_score(test_labels, test_probs) if len(set(test_labels)) > 1 else float("nan")

    result = {
        "target_level": target_level, "target_value": target_value, "model_key": MODEL_KEY,
        "split": SPLIT_NAME, "seed": seed, "frac": frac,
        "train_size": len(train_ex), "train_pos": train_pos,
        "val_size": len(val_ex), "val_pos": sum(val_labels),
        "test_size": len(test_ex), "test_pos": sum(test_labels),
        "best_epoch": best_epoch, "best_val_f1": best_val_f1, "threshold": threshold,
        "total_train_seconds": round(total_train_seconds, 1),
        "epoch_log": epoch_log, "test_metrics": test_metrics, "auc_roc_test": auc,
        "complete": True,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[lc] {out_path.stem}: train_pos={train_pos} f1={test_metrics['f1']:.3f} auc={auc:.3f} "
          f"({total_train_seconds:.1f}s)")
    del model, best_state
    torch.cuda.empty_cache()
    return result


def power_fit(xs, ys):
    """F1 = a * x^b (saturating-ish for b<1), fit in log-space via least squares on
    log(y) = log(a) + b*log(x); returns (a,b,r2). Falls back to None if any y<=0."""
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    mask = ys > 1e-6
    if mask.sum() < 3:
        return None
    logx = np.log(xs[mask])
    logy = np.log(ys[mask])
    b, loga = np.polyfit(logx, logy, 1)
    a = np.exp(loga)
    pred = a * xs[mask] ** b
    ss_res = np.sum((ys[mask] - pred) ** 2)
    ss_tot = np.sum((ys[mask] - ys[mask].mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"a": float(a), "b": float(b), "r2": float(r2)}


def saturating_fit(xs, ys):
    """F1 = c * (1 - exp(-x/tau)), nonlinear least squares."""
    def model(x, c, tau):
        return c * (1 - np.exp(-x / tau))
    xs = np.array(xs, dtype=float)
    ys = np.array(ys, dtype=float)
    try:
        popt, _ = curve_fit(model, xs, ys, p0=[max(ys.max(), 0.1), max(xs.mean(), 1.0)], maxfev=5000)
        pred = model(xs, *popt)
        ss_res = np.sum((ys - pred) ** 2)
        ss_tot = np.sum((ys - ys.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return {"c": float(popt[0]), "tau": float(popt[1]), "r2": float(r2)}
    except Exception as e:
        return {"error": str(e)}


def build():
    from common import TARGETS_BY_LEVEL
    seeds = [0, 1, 2]

    lc_results = {lvl: {} for lvl in TARGET_LEVELS}
    for level in TARGET_LEVELS:
        target_value = TARGETS_BY_LEVEL[level]["value"]
        for frac in FRACTIONS:
            for seed in seeds:
                r = run_one(level, target_value, frac, seed)
                lc_results[level].setdefault(frac, []).append(r)

    # ---- cross-target (5 targets, full data, MARBERT S2) F1/AUC vs positive train verses ----
    from common import LEVEL_ORDER
    import statistics as stats
    cross = {}
    for level in LEVEL_ORDER:
        runs = [load_run(level, MODEL_KEY, "S2", s) for s in seeds]
        runs = [r for r in runs if r is not None]
        if not runs:
            continue
        f1s = [r["test_metrics"]["f1"] for r in runs]
        pos = [r["train_pos"] for r in runs]
        aucs = []
        for r in runs:
            labs = [p["label"] for p in r["predictions"]]
            probs = [p["prob"] for p in r["predictions"]]
            aucs.append(roc_auc_score(labs, probs) if len(set(labs)) > 1 else float("nan"))
        cross[level] = {"train_pos_mean": stats.mean(pos), "f1_mean": stats.mean(f1s),
                        "auc_mean": stats.mean(aucs)}

    # Pearson on the 5 cross-target points (as Phase 5 already reported) + power-law fit
    xs5 = [cross[l]["train_pos_mean"] for l in LEVEL_ORDER if l in cross]
    ys5_f1 = [cross[l]["f1_mean"] for l in LEVEL_ORDER if l in cross]
    ys5_auc = [cross[l]["auc_mean"] for l in LEVEL_ORDER if l in cross]
    pear_f1 = pearsonr(xs5, ys5_f1)
    pear_auc = pearsonr(xs5, ys5_auc)
    fit5_f1 = power_fit(xs5, ys5_f1)
    fit5_auc = power_fit(xs5, ys5_auc)

    # Within-target learning-curve fits (more points per target, same model/target held fixed
    # -- a cleaner test of the data-size hypothesis than the 5-point cross-target correlation)
    lc_fits = {}
    for level in TARGET_LEVELS:
        xs, ys_f1, ys_auc = [], [], []
        for frac in FRACTIONS:
            for r in lc_results[level][frac]:
                xs.append(r["train_pos"])
                ys_f1.append(r["test_metrics"]["f1"])
                ys_auc.append(r["auc_roc_test"])
        lc_fits[level] = {
            "power_fit_f1": power_fit(xs, ys_f1), "saturating_fit_f1": saturating_fit(xs, ys_f1),
            "power_fit_auc": power_fit(xs, ys_auc), "saturating_fit_auc": saturating_fit(xs, ys_auc),
            "pearson_f1": list(pearsonr(xs, ys_f1)), "n_points": len(xs),
        }

    summary = {
        "cross_target_5pt": cross,
        "cross_target_pearson_f1": list(pear_f1), "cross_target_pearson_auc": list(pear_auc),
        "cross_target_power_fit_f1": fit5_f1, "cross_target_power_fit_auc": fit5_auc,
        "learning_curve_fits": lc_fits,
        "fractions": FRACTIONS, "target_levels": TARGET_LEVELS, "model": MODEL_KEY, "split": SPLIT_NAME,
    }
    (ANALYSIS_OUT / "section4_learning_curve.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # ---- plot ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    colors = {"easy": "#d62728", "medium": "#1f77b4"}
    for level in TARGET_LEVELS:
        xs = [stats.mean(r["train_pos"] for r in lc_results[level][frac]) for frac in FRACTIONS]
        ys_f1 = [stats.mean(r["test_metrics"]["f1"] for r in lc_results[level][frac]) for frac in FRACTIONS]
        ys_auc = [stats.mean(r["auc_roc_test"] for r in lc_results[level][frac]) for frac in FRACTIONS]
        axes[0].plot(xs, ys_f1, "o-", color=colors[level], label=f"{level} (learning curve)")
        axes[1].plot(xs, ys_auc, "o-", color=colors[level], label=f"{level} (learning curve)")

    for level in LEVEL_ORDER:
        if level not in cross:
            continue
        marker = "D"
        axes[0].scatter([cross[level]["train_pos_mean"]], [cross[level]["f1_mean"]],
                        marker=marker, s=90, color="black", zorder=5)
        axes[0].annotate(level, (cross[level]["train_pos_mean"], cross[level]["f1_mean"]),
                         fontsize=8, xytext=(4, 4), textcoords="offset points")
        axes[1].scatter([cross[level]["train_pos_mean"]], [cross[level]["auc_mean"]],
                        marker=marker, s=90, color="black", zorder=5)
        axes[1].annotate(level, (cross[level]["train_pos_mean"], cross[level]["auc_mean"]),
                         fontsize=8, xytext=(4, 4), textcoords="offset points")

    for ax, ylabel in zip(axes, ["Test F1", "Test AUC-ROC"]):
        ax.set_xscale("log")
        ax.set_xlabel("positive training verses (log scale)")
        ax.set_ylabel(ylabel)
        ax.axhline(0.5 if ylabel == "Test AUC-ROC" else 0, color="gray", lw=0.7, ls="--")
        ax.legend(fontsize=8)
        ax.set_title(ylabel + " vs. positive training verses\n(lines=learning curve, MARBERT; "
                     "diamonds=all 5 targets at full data)")
    fig.tight_layout()
    fig_path = FIGS_DIR / "section4_learning_curve.png"
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)
    print(f"Figure saved: {fig_path}")

    md = ["## Section 4 — Data-size hypothesis\n"]
    md.append(f"Cross-target (5 targets, MARBERT, S2, full data): Pearson r(F1, positives)={pear_f1[0]:.3f} "
              f"(p={pear_f1[1]:.3f}), r(AUC, positives)={pear_auc[0]:.3f} (p={pear_auc[1]:.3f}).")
    md.append(f"Power-law fit F1 = a*x^b on the 5 points: {fit5_f1}")
    md.append(f"Power-law fit AUC = a*x^b on the 5 points: {fit5_auc}\n")
    for level in TARGET_LEVELS:
        md.append(f"**{level} learning curve** (n={lc_fits[level]['n_points']} runs: 4 fractions x 3 seeds):")
        md.append(f"- power-law fit F1: {lc_fits[level]['power_fit_f1']}")
        md.append(f"- saturating fit F1 = c*(1-exp(-x/tau)): {lc_fits[level]['saturating_fit_f1']}")
        md.append(f"- Pearson r (within-target, F1 vs positives): {lc_fits[level]['pearson_f1']}")
    (ANALYSIS_OUT / "section4_learning_curve.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    build()
