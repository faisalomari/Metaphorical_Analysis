"""Step 3: cheap ensemble of the best 2-3 trained Phase 6 models per target --
average predicted probabilities (per poem_id+verse_no, matched across models),
threshold tuned on the AVERAGED VAL probabilities (never on test). Only models
that persisted val_predictions can be blended; Phase 5's own baseline cell
predates this field (train.py never saved val predictions) and is reported
standalone in evaluate.py instead, not silently dropped -- this script says so
explicitly per target when that happens."""
import json
import statistics as stats

from sklearn.metrics import average_precision_score, roc_auc_score

import phase6_config as config
from analysis_common import all_seeds_cell, bootstrap_ci_over_poems
from metrics_utils import best_threshold, prf


def _probs_by_key(runs: list, field: str) -> dict:
    """{(poem_id, verse_no): (label, prob)} averaged over this cell's seeds."""
    acc = {}
    for r in runs:
        for p in r[field]:
            key = (p["poem_id"], p["verse_no"])
            acc.setdefault(key, {"label": p["label"], "probs": []})["probs"].append(p["prob"])
    return {k: (v["label"], stats.mean(v["probs"])) for k, v in acc.items()}


def ensemble_for_target(target_level: str, candidates: list, split_name: str) -> dict:
    per_model = []
    for cand in candidates:
        runs = all_seeds_cell(target_level, cand["model_key"], cand["config_name"], split_name)
        runs = [r for r in runs if r.get("val_predictions")]
        if not runs:
            print(f"  [{target_level}] {cand['label']} has no val_predictions (Phase 5 baseline cell "
                  f"predates this field) -- excluded from the ensemble blend")
            continue
        per_model.append((cand, runs))

    if len(per_model) < 2:
        return {"target_level": target_level, "split": split_name, "status": "skipped",
                "reason": f"only {len(per_model)} model(s) with val_predictions available"}

    val_maps = [_probs_by_key(runs, "val_predictions") for _, runs in per_model]
    test_maps = [_probs_by_key(runs, "predictions") for _, runs in per_model]

    common_val_keys = set.intersection(*(set(m) for m in val_maps))
    common_test_keys = set.intersection(*(set(m) for m in test_maps))

    val_labels = [val_maps[0][k][0] for k in common_val_keys]
    val_probs_avg = [stats.mean(m[k][1] for m in val_maps) for k in common_val_keys]
    val_best = best_threshold(val_labels, val_probs_avg, config.THRESHOLD_GRID)
    threshold = val_best["threshold"]

    test_labels = [test_maps[0][k][0] for k in common_test_keys]
    test_probs_avg = [stats.mean(m[k][1] for m in test_maps) for k in common_test_keys]
    test_pred = [1 if p >= threshold else 0 for p in test_probs_avg]
    test_metrics = prf(test_labels, test_pred)
    auc = roc_auc_score(test_labels, test_probs_avg) if len(set(test_labels)) > 1 else float("nan")
    ap = average_precision_score(test_labels, test_probs_avg) if len(set(test_labels)) > 1 else float("nan")

    fake_runs = [{"predictions": [{"poem_id": k[0], "verse_no": k[1], "label": test_maps[0][k][0],
                                    "pred": (1 if stats.mean(m[k][1] for m in test_maps) >= threshold else 0)}
                                   for k in common_test_keys]}]
    ci = bootstrap_ci_over_poems(fake_runs)

    return {
        "target_level": target_level, "split": split_name, "status": "ok",
        "members": [c["label"] for c, _ in per_model],
        "threshold": threshold, "val_f1": val_best["f1"],
        "test_metrics": test_metrics, "auc_roc": auc, "avg_precision": ap, "bootstrap_ci": ci,
    }


def main():
    selected = json.loads((config.RESULTS_DIR / "selected_configs.json").read_text(encoding="utf-8"))
    out = {}
    lines = ["## Step 3 -- cheap ensemble (avg probs, threshold tuned on VAL) of the selected configs\n"]
    for target_level, cands in selected.items():
        res = ensemble_for_target(target_level, cands, "S2")
        out[target_level] = res
        if res["status"] == "ok":
            m = res["test_metrics"]
            ci = res["bootstrap_ci"]
            lines.append(f"- **{target_level}**: ensemble of {res['members']} -> F1={m['f1']:.3f} "
                          f"(TP={m['tp']} FP={m['fp']} FN={m['fn']}), AUC={res['auc_roc']:.3f}, "
                          f"AP={res['avg_precision']:.3f}, CI=[{ci['ci_low']:.3f},{ci['ci_high']:.3f}]"
                          if ci else f"- **{target_level}**: ensemble F1={m['f1']:.3f}")
        else:
            lines.append(f"- **{target_level}**: skipped ({res['reason']})")
        if target_level == "medium":
            res_s3 = ensemble_for_target(target_level, cands, "S3")
            out["medium_S3"] = res_s3
            if res_s3["status"] == "ok":
                m = res_s3["test_metrics"]
                lines.append(f"  - S3 (استعارة فعل fixed test pool): F1={m['f1']:.3f} "
                              f"(TP={m['tp']} FP={m['fp']} FN={m['fn']}), AUC={res_s3['auc_roc']:.3f}")

    md_text = "\n".join(lines)
    (config.RESULTS_DIR / "step3_ensemble.md").write_text(md_text, encoding="utf-8")
    (config.RESULTS_DIR / "step3_ensemble.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(md_text)


if __name__ == "__main__":
    main()
