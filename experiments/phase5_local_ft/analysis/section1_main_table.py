"""Section 1: exact-numbers table, per target x model x split, mean+-std over
seeds. Positives/negatives in train/val/test (verses AND poems), TP/FP/FN/TN,
precision/recall/F1, tuned threshold, best epoch. Baselines alongside. LLM
evidence (recall or F1, units kept explicit) from config/targets.json.
Flags cells where test positives < 30. No training, no API calls.
"""
import json
import statistics as stats

from common import (ANALYSIS_OUT, LEVEL_ORDER, MODEL_KEYS, SEEDS,
                     TARGETS_BY_LEVEL, load_baseline, load_run,
                     split_verse_poem_counts)


def fmt(x, nd=3):
    return f"{x:.{nd}f}"


def aggregate_model_cell(level, model_key, split_name):
    runs = [load_run(level, model_key, split_name, s) for s in SEEDS]
    runs = [r for r in runs if r is not None]
    if not runs:
        return None
    f1s = [r["test_metrics"]["f1"] for r in runs]
    ps = [r["test_metrics"]["precision"] for r in runs]
    rs = [r["test_metrics"]["recall"] for r in runs]
    thrs = [r["threshold"] for r in runs]
    epochs = [r["best_epoch"] for r in runs]
    tp = [r["test_metrics"]["tp"] for r in runs]
    fp = [r["test_metrics"]["fp"] for r in runs]
    fn = [r["test_metrics"]["fn"] for r in runs]
    tn = [r["test_metrics"]["tn"] for r in runs]
    return {
        "n_seeds": len(runs),
        "f1_mean": stats.mean(f1s), "f1_std": stats.pstdev(f1s) if len(f1s) > 1 else 0.0,
        "p_mean": stats.mean(ps), "p_std": stats.pstdev(ps) if len(ps) > 1 else 0.0,
        "r_mean": stats.mean(rs), "r_std": stats.pstdev(rs) if len(rs) > 1 else 0.0,
        "tp_mean": stats.mean(tp), "fp_mean": stats.mean(fp),
        "fn_mean": stats.mean(fn), "tn_mean": stats.mean(tn),
        "tp_sum": sum(tp), "fp_sum": sum(fp), "fn_sum": sum(fn), "tn_sum": sum(tn),
        "threshold_mean": stats.mean(thrs), "threshold_std": stats.pstdev(thrs) if len(thrs) > 1 else 0.0,
        "best_epoch_mean": stats.mean(epochs), "best_epoch_std": stats.pstdev(epochs) if len(epochs) > 1 else 0.0,
        "train_size": stats.mean(r["train_size"] for r in runs), "train_pos": stats.mean(r["train_pos"] for r in runs),
        "val_size": stats.mean(r["val_size"] for r in runs), "val_pos": stats.mean(r["val_pos"] for r in runs),
        "test_size": stats.mean(r["test_size"] for r in runs), "test_pos": stats.mean(r["test_pos"] for r in runs),
    }


def aggregate_baseline_cell(level, split_name):
    runs = [load_baseline(level, split_name, s) for s in SEEDS]
    runs = [r for r in runs if r is not None]
    if not runs:
        return None
    out = {}
    for key in ("majority", "always_positive", "tfidf_logreg"):
        if key == "tfidf_logreg":
            f1s = [r["tfidf_logreg"]["test"]["f1"] for r in runs]
            ps = [r["tfidf_logreg"]["test"]["precision"] for r in runs]
            rs = [r["tfidf_logreg"]["test"]["recall"] for r in runs]
            tp = [r["tfidf_logreg"]["test"]["tp"] for r in runs]
            fp = [r["tfidf_logreg"]["test"]["fp"] for r in runs]
            fn = [r["tfidf_logreg"]["test"]["fn"] for r in runs]
            tn = [r["tfidf_logreg"]["test"]["tn"] for r in runs]
        else:
            f1s = [r[key]["f1"] for r in runs]
            ps = [r[key]["precision"] for r in runs]
            rs = [r[key]["recall"] for r in runs]
            tp = [r[key]["tp"] for r in runs]
            fp = [r[key]["fp"] for r in runs]
            fn = [r[key]["fn"] for r in runs]
            tn = [r[key]["tn"] for r in runs]
        out[key] = {
            "f1_mean": stats.mean(f1s), "f1_std": stats.pstdev(f1s) if len(f1s) > 1 else 0.0,
            "p_mean": stats.mean(ps), "r_mean": stats.mean(rs),
            "tp_sum": sum(tp), "fp_sum": sum(fp), "fn_sum": sum(fn), "tn_sum": sum(tn),
        }
    return out


def llm_evidence_line(level):
    t = TARGETS_BY_LEVEL[level]
    ev = t["evidence"]
    parts = []
    if "e1_v2_verse_F1_best_single_model_setA" in ev:
        parts.append(f"LLM verse-F1 best-single={ev['e1_v2_verse_F1_best_single_model_setA']:.3f}, "
                      f"ensemble={ev['e1_v2_verse_F1_ensemble_setA']:.3f}, "
                      f"zero-shot range={ev['e1_v2_verse_F1_zero_shot_range']}")
    if "phase3_crossmodel_recall_strict" in ev:
        r = ev["phase3_crossmodel_recall_strict"]
        parts.append(f"LLM span-level strict RECALL (not F1): gemini={r.get('gemini')}, gpt={r.get('gpt')}, n={r.get('n')}")
    if "phase1_frozen_parent_F1_avg_3models" in ev:
        parts.append(f"Phase1 parent-level (not subtype) span-F1 avg 3 LLMs={ev['phase1_frozen_parent_F1_avg_3models']:.3f}")
    if "phase1_TEST_subtype_breakdown_pct_missed" in ev:
        m = ev["phase1_TEST_subtype_breakdown_pct_missed"]
        parts.append(f"Phase1 TEST subtype %%missed: baseline={m['baseline']}, v4={m['v4_combined']}, n={m['n']}")
    return " | ".join(parts)


def build():
    report = {"splits": {}}
    md_lines = []
    md_lines.append("## Section 1 — Exact numbers: F1/P/R/TP/FP/FN/TN per target x model x split\n")
    md_lines.append("Mean +/- population-std over 3 seeds unless noted. `test_pos` < 30 is flagged with **(thin, n<30)**.\n")
    md_lines.append("Note: S1/S2 reshuffle the WHOLE partition per seed (train/val/test all vary) -- "
                     "verse/poem counts below are the mean across the 3 seeds' own (different) splits. "
                     "S3 keeps TEST fixed across all 3 seeds (same 327-verse/25-poem pool every time).\n")

    for split_name in ("S1", "S2", "S3"):
        levels = ["medium"] if split_name == "S3" else LEVEL_ORDER
        md_lines.append(f"\n### Split {split_name}\n")
        header = ("| Level (subtype) | Model | train pos/neg verses (poems) | val pos/neg verses (poems) | "
                   "test pos/neg verses (poems) | TP/FP/FN/TN (sum over seeds) | Precision | Recall | F1 mean+-std | "
                   "threshold | best epoch |")
        sep = "|---|---|---|---|---|---|---|---|---|---|---|"
        md_lines.append(header)
        md_lines.append(sep)
        report["splits"][split_name] = {}
        for level in levels:
            target_value = TARGETS_BY_LEVEL[level]["value"]
            vp_cache = {}
            report["splits"][split_name][level] = {"models": {}, "baselines": {}, "llm": llm_evidence_line(level)}
            for model_key in MODEL_KEYS:
                cell = aggregate_model_cell(level, model_key, split_name)
                if cell is None:
                    continue
                report["splits"][split_name][level]["models"][model_key] = cell
                if target_value not in vp_cache:
                    per_seed = [split_verse_poem_counts(split_name, s, target_value) for s in SEEDS]
                    avg = {}
                    for part in ("train", "val", "test"):
                        avg[part] = {k: round(stats.mean(d[part][k] for d in per_seed), 1)
                                     for k in per_seed[0][part]}
                    avg["_per_seed"] = per_seed
                    vp_cache[target_value] = avg
                vp = vp_cache[target_value]
                thin = cell["test_pos"] < 30
                thin_mark = " **(thin, n<30)**" if thin else ""
                train_str = (f"{vp.get('train', {}).get('n_pos_verses', '?')}/"
                             f"{vp.get('train', {}).get('n_neg_verses', '?')} "
                             f"({vp.get('train', {}).get('n_pos_poems', '?')}/"
                             f"{vp.get('train', {}).get('n_poems', '?')} poems)")
                val_str = (f"{vp.get('val', {}).get('n_pos_verses', '?')}/"
                           f"{vp.get('val', {}).get('n_neg_verses', '?')} "
                           f"({vp.get('val', {}).get('n_pos_poems', '?')}/"
                           f"{vp.get('val', {}).get('n_poems', '?')} poems)")
                test_str = (f"{vp.get('test', {}).get('n_pos_verses', '?')}/"
                            f"{vp.get('test', {}).get('n_neg_verses', '?')} "
                            f"({vp.get('test', {}).get('n_pos_poems', '?')}/"
                            f"{vp.get('test', {}).get('n_poems', '?')} poems){thin_mark}")
                row = (f"| {level} ({target_value}) | {model_key} | {train_str} | {val_str} | {test_str} | "
                       f"{cell['tp_sum']}/{cell['fp_sum']}/{cell['fn_sum']}/{cell['tn_sum']} | "
                       f"{fmt(cell['p_mean'])} | {fmt(cell['r_mean'])} | "
                       f"{fmt(cell['f1_mean'])}+-{fmt(cell['f1_std'])} | "
                       f"{fmt(cell['threshold_mean'],2)}+-{fmt(cell['threshold_std'],2)} | "
                       f"{fmt(cell['best_epoch_mean'],1)}+-{fmt(cell['best_epoch_std'],1)} |")
                md_lines.append(row)

            baselines = aggregate_baseline_cell(level, split_name)
            if baselines:
                report["splits"][split_name][level]["baselines"] = baselines
                for key, label in (("majority", "baseline: majority"),
                                    ("always_positive", "baseline: always-positive"),
                                    ("tfidf_logreg", "baseline: TF-IDF+LR")):
                    b = baselines[key]
                    md_lines.append(f"| {level} | {label} | - | - | - | "
                                     f"{b['tp_sum']}/{b['fp_sum']}/{b['fn_sum']}/{b['tn_sum']} | "
                                     f"{fmt(b['p_mean'])} | {fmt(b['r_mean'])} | "
                                     f"{fmt(b['f1_mean'])}+-{fmt(b['f1_std'])} | - | - |")
            md_lines.append(f"| {level} | **LLM evidence** | {llm_evidence_line(level)} | | | | | | | | |")

    (ANALYSIS_OUT / "section1_main_table.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_text = "\n".join(md_lines)
    (ANALYSIS_OUT / "section1_main_table.md").write_text(md_text, encoding="utf-8")
    print(md_text[:3000])
    print(f"\n...written to {ANALYSIS_OUT / 'section1_main_table.md'}")


if __name__ == "__main__":
    build()
