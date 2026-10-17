"""Step 2: TEST-only evaluation. For each target, compares Phase 5's best
model/config against the 2 selected Phase 6 configs (results/phase6_stronger_
ft/selected_configs.json): verse-level TP/FP/FN/P/R/F1 (primary, val-tuned
threshold), AUC-ROC + average precision (threshold-free), mean+-std over
seeds, bootstrap 95% CI over poems (same method as Phase 5's own analyze.py /
analysis/section2_variance.py). Also pulls in the E1 v2 LLM numbers for
استعارة فعل (medium) from docs/phase4/E1_V2_RESULTS.md / docs/phase5/
LOCAL_FT_RESULTS.md section 8, already summarized there -- hardcoded here with
their source cited, not re-scraped."""
import json
import statistics as stats

from sklearn.metrics import average_precision_score, roc_auc_score

import phase6_config as config
from analysis_common import BASELINE_CONFIG_NAME, all_seeds_cell, bootstrap_ci_over_poems, pool_predictions
from metrics_utils import prf

# docs/phase5/LOCAL_FT_RESULTS.md section 8 / docs/phase4/E1_V2_RESULTS.md (استعارة فعل / medium only,
# verse-level criterion, identical 25-poem/327-verse S3 test pool)
LLM_EVIDENCE_MEDIUM = {
    "best_single_llm": {"model": "Claude Sonnet 4.6, set A", "f1": 0.576},
    "llm_ensemble": {"model": "3-model ensemble, set A", "f1": 0.568},
    "llm_zero_shot_range": {"f1_low": 0.377, "f1_high": 0.549, "note": "set Z, 3 models"},
}


def summarize_cell(target_level: str, model_key: str, config_name: str, split_name: str) -> dict:
    runs = all_seeds_cell(target_level, model_key, config_name, split_name)
    if not runs:
        return None
    f1s = [r["test_metrics"]["f1"] for r in runs]
    labels, probs, preds = pool_predictions(runs)
    ci = bootstrap_ci_over_poems(runs)
    auc = roc_auc_score(labels, probs) if len(set(labels)) > 1 else float("nan")
    ap = average_precision_score(labels, probs) if len(set(labels)) > 1 else float("nan")
    pooled = prf(labels, preds)
    return {
        "model_key": model_key, "config_name": config_name, "split": split_name,
        "n_seeds": len(runs), "f1_mean": stats.mean(f1s), "f1_std": stats.pstdev(f1s) if len(f1s) > 1 else 0.0,
        "tp": pooled["tp"], "fp": pooled["fp"], "fn": pooled["fn"], "tn": pooled["tn"],
        "precision": pooled["precision"], "recall": pooled["recall"],
        "auc_roc": auc, "avg_precision": ap,
        "bootstrap_ci": ci,
        "test_pos_mean": stats.mean(r["test_metrics"]["tp"] + r["test_metrics"]["fn"] for r in runs),
    }


def build_table(split_name: str, target_levels: list, selected: dict) -> list:
    rows = []
    for target_level in target_levels:
        p5_model = config.PHASE5_BEST_MODEL[target_level]
        cands = selected.get(target_level, [])
        baseline_already_selected = any(
            c["model_key"] == p5_model and c["config_name"] == BASELINE_CONFIG_NAME for c in cands)
        if not baseline_already_selected:
            baseline = summarize_cell(target_level, p5_model, BASELINE_CONFIG_NAME, split_name)
            if baseline:
                rows.append({"target_level": target_level, "label": "phase5_baseline", **baseline})
        for cand in cands:
            cell = summarize_cell(target_level, cand["model_key"], cand["config_name"], split_name)
            if cell:
                rows.append({"target_level": target_level, "label": cand["label"], **cell})
    return rows


def render_markdown(rows: list, split_name: str) -> str:
    lines = [f"### {split_name}\n",
             "| Target | Config | n_seeds | F1 mean+-std | P | R | TP/FP/FN | AUC-ROC | AP | "
             "bootstrap 95% CI | test_pos (mean) | flag |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        flag = "**n<30**" if r["test_pos_mean"] < 30 else ""
        ci = r["bootstrap_ci"]
        ci_str = f"[{ci['ci_low']:.3f},{ci['ci_high']:.3f}]" if ci else "n/a"
        lines.append(
            f"| {r['target_level']} | {r['label']} ({r['model_key']}/{r['config_name']}) | {r['n_seeds']} | "
            f"{r['f1_mean']:.3f}+-{r['f1_std']:.3f} | {r['precision']:.3f} | {r['recall']:.3f} | "
            f"{r['tp']}/{r['fp']}/{r['fn']} | {r['auc_roc']:.3f} | {r['avg_precision']:.3f} | {ci_str} | "
            f"{r['test_pos_mean']:.0f} | {flag} |")
    return "\n".join(lines)


def main():
    selected = json.loads((config.RESULTS_DIR / "selected_configs.json").read_text(encoding="utf-8"))

    rows_s2 = build_table("S2", config.TARGET_LEVELS, selected)
    rows_s3 = build_table("S3", ["medium"], selected)

    out_md = ["## Step 2 evaluation -- TEST only\n", render_markdown(rows_s2, "S2 (primary split)"), ""]
    out_md.append(render_markdown(rows_s3, "S3 (استعارة فعل only, fixed 25-poem/327-verse TEST pool)"))
    out_md.append("\n### S3 vs LLM evidence (same test pool, docs/phase5/LOCAL_FT_RESULTS.md section 8)\n")
    out_md.append("| Source | F1 |")
    out_md.append("|---|---|")
    out_md.append(f"| Best single LLM ({LLM_EVIDENCE_MEDIUM['best_single_llm']['model']}) | "
                   f"{LLM_EVIDENCE_MEDIUM['best_single_llm']['f1']:.3f} |")
    out_md.append(f"| LLM ensemble ({LLM_EVIDENCE_MEDIUM['llm_ensemble']['model']}) | "
                   f"{LLM_EVIDENCE_MEDIUM['llm_ensemble']['f1']:.3f} |")
    out_md.append(f"| LLM zero-shot range | {LLM_EVIDENCE_MEDIUM['llm_zero_shot_range']['f1_low']:.3f}-"
                   f"{LLM_EVIDENCE_MEDIUM['llm_zero_shot_range']['f1_high']:.3f} |")
    for r in rows_s3:
        out_md.append(f"| Phase 6 {r['label']} ({r['model_key']}) | {r['f1_mean']:.3f}+-{r['f1_std']:.3f} |")

    md_text = "\n".join(out_md)
    out_path_md = config.RESULTS_DIR / "step2_evaluation.md"
    out_path_md.write_text(md_text, encoding="utf-8")
    out_path_json = config.RESULTS_DIR / "step2_evaluation.json"
    out_path_json.write_text(json.dumps({"S2": rows_s2, "S3": rows_s3}, ensure_ascii=False, indent=2,
                                         default=str), encoding="utf-8")
    print(md_text)
    print(f"\nwrote {out_path_md} and {out_path_json}")


if __name__ == "__main__":
    main()
