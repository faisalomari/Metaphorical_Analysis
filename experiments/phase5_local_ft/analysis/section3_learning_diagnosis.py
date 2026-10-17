"""Section 3: is the model learning at all? Per target (S2, pooled over 3
seeds x best model and all 3 models): train-loss / val-F1 curve summary,
prediction rate vs true rate on test, AUC-ROC + average precision (threshold-
free) on test, and F1 at the best POSSIBLE threshold on test (diagnostic only
-- never a valid reported result, since it peeks at test labels to choose a
threshold). No val loss was ever recorded by train.py (only val F1, via
best_threshold) -- that gap is stated explicitly rather than invented.
"""
import json
import statistics as stats

from common import ANALYSIS_OUT, LEVEL_ORDER, MODEL_KEYS, SEEDS, load_run
from metrics_utils import prf
from sklearn.metrics import average_precision_score, roc_auc_score

THRESHOLD_GRID = [round(0.05 + 0.01 * i, 2) for i in range(91)]


def best_threshold_f1_diagnostic(y_true, probs):
    best = {"threshold": 0.5, "f1": -1.0}
    for thr in THRESHOLD_GRID:
        y_pred = [1 if p >= thr else 0 for p in probs]
        m = prf(y_true, y_pred)
        if m["f1"] > best["f1"]:
            best = {"threshold": thr, **m}
    return best


def curve_summary(epoch_log):
    train_losses = [e["train_loss"] for e in epoch_log]
    val_f1s = [e["val_f1"] for e in epoch_log]
    n = len(epoch_log)
    return {
        "n_epochs_run": n,
        "train_loss_first": train_losses[0], "train_loss_last": train_losses[-1],
        "train_loss_monotonic_decrease": all(train_losses[i] >= train_losses[i + 1] for i in range(n - 1)),
        "val_f1_first": val_f1s[0], "val_f1_last": val_f1s[-1], "val_f1_max": max(val_f1s),
        "val_f1_argmax_epoch": epoch_log[val_f1s.index(max(val_f1s))]["epoch"],
        "val_f1_trend": "improves_then_plateaus_or_drops" if max(val_f1s) != val_f1s[-1] or n <= 2
                        else ("still_improving_at_stop" if val_f1s[-1] == max(val_f1s) and n == len(epoch_log) else "flat"),
    }


def build():
    out = {}
    md = ["## Section 3 — Is the model learning at all? (S2, per target x model)\n"]
    md.append("`val loss` was never recorded by `train.py` (only val F1, via best-threshold search) -- "
              "curve summaries below use train loss + val F1 only. `best-threshold F1` is a **diagnostic-only** "
              "number that picks the threshold maximizing F1 on the TEST set itself -- it is never a valid "
              "reported result, only a ceiling to compare the real (val-tuned) F1 against.\n")

    for level in LEVEL_ORDER:
        out[level] = {}
        md.append(f"\n### {level}\n")
        md.append("| Model | best_epoch (mean) | n_epochs_run (mean) | train_loss first->last | "
                   "val_f1 first->max->last | AUC-ROC (test) | AP (test) | real F1 (val-tuned) | "
                   "best-possible F1 (test-tuned, diagnostic) | pred_rate | true_rate |")
        md.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for model_key in MODEL_KEYS:
            runs = [load_run(level, model_key, "S2", s) for s in SEEDS]
            runs = [r for r in runs if r is not None]
            if not runs:
                continue
            curves = [curve_summary(r["epoch_log"]) for r in runs]
            best_epochs = [r["best_epoch"] for r in runs]
            n_epochs = [c["n_epochs_run"] for c in curves]
            tl_first = stats.mean(c["train_loss_first"] for c in curves)
            tl_last = stats.mean(c["train_loss_last"] for c in curves)
            vf_first = stats.mean(c["val_f1_first"] for c in curves)
            vf_max = stats.mean(c["val_f1_max"] for c in curves)
            vf_last = stats.mean(c["val_f1_last"] for c in curves)

            all_probs, all_labels, all_preds = [], [], []
            for r in runs:
                for p in r["predictions"]:
                    all_probs.append(p["prob"])
                    all_labels.append(p["label"])
                    all_preds.append(p["pred"])
            auc = roc_auc_score(all_labels, all_probs) if len(set(all_labels)) > 1 else float("nan")
            ap = average_precision_score(all_labels, all_probs) if len(set(all_labels)) > 1 else float("nan")
            real_f1 = prf(all_labels, all_preds)["f1"]
            diag = best_threshold_f1_diagnostic(all_labels, all_probs)
            pred_rate = sum(all_preds) / len(all_preds)
            true_rate = sum(all_labels) / len(all_labels)

            out[level][model_key] = {
                "best_epoch_mean": stats.mean(best_epochs), "n_epochs_run_mean": stats.mean(n_epochs),
                "train_loss_first": tl_first, "train_loss_last": tl_last,
                "val_f1_first": vf_first, "val_f1_max": vf_max, "val_f1_last": vf_last,
                "auc_roc_test": auc, "avg_precision_test": ap,
                "real_f1_test_pooled": real_f1,
                "best_possible_threshold_f1_diagnostic": diag["f1"],
                "best_possible_threshold_diagnostic": diag["threshold"],
                "pred_rate": pred_rate, "true_rate": true_rate,
            }
            md.append(f"| {model_key} | {stats.mean(best_epochs):.1f} | {stats.mean(n_epochs):.1f} | "
                      f"{tl_first:.3f}->{tl_last:.3f} | {vf_first:.3f}->{vf_max:.3f}->{vf_last:.3f} | "
                      f"{auc:.3f} | {ap:.3f} | {real_f1:.3f} | {diag['f1']:.3f} (thr={diag['threshold']}) | "
                      f"{pred_rate:.3f} | {true_rate:.3f} |")

    (ANALYSIS_OUT / "section3_learning_diagnosis.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_text = "\n".join(md)
    (ANALYSIS_OUT / "section3_learning_diagnosis.md").write_text(md_text, encoding="utf-8")
    print(md_text)


if __name__ == "__main__":
    build()
