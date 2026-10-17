"""Step 1 selection: after run_l1l2_ablation.py (seed0) and run_l3_bigger_models.py
(seed0) have both produced cells, pick the top-2 configs per target by VAL F1
(best_val_f1 from the seed0 run -- never TEST, to avoid test-informed model
selection) among: Phase 5 baseline, the 3 single-lever L1/L2 cells, and the 3
L3 bigger-model cells. Writes results/phase6_stronger_ft/selected_configs.json,
consumed by run_final_grid.py (3-seed S2 + S3 promotion)."""
import json

import phase6_config as config
from analysis_common import BASELINE_CONFIG_NAME, load_cell

L1L2_CELLS = [
    ("ctx1_bce_pos_weight_constant", "L1_context"),
    ("ctx0_focal_constant", "L2a_focal"),
    ("ctx0_bce_pos_weight_cosine_llrd", "L2b_cosine_llrd"),
]


def candidates_for_target(target_level: str) -> list:
    """Returns [{"model_key","config_name","label","best_val_f1","test_f1"}]."""
    out = []
    p5_model = config.PHASE5_BEST_MODEL[target_level]
    base = load_cell(target_level, p5_model, BASELINE_CONFIG_NAME, "S2", 0)
    if base:
        out.append({"model_key": p5_model, "config_name": BASELINE_CONFIG_NAME, "label": "phase5_baseline",
                     "best_val_f1": base["best_val_f1"], "test_f1": base["test_metrics"]["f1"]})
    for config_name, label in L1L2_CELLS:
        cell = load_cell(target_level, p5_model, config_name, "S2", 0)
        if cell:
            out.append({"model_key": p5_model, "config_name": config_name, "label": label,
                         "best_val_f1": cell["best_val_f1"], "test_f1": cell["test_metrics"]["f1"]})
    for model_key in config.BIG_MODELS:
        # L3 cells use whatever recipe run_l3_bigger_models.py was invoked with; try the
        # two most likely tags (baseline recipe, and the winning L1/L2 recipe if re-run).
        for config_name, label in [("ctx0_bce_pos_weight_qlora", f"L3_{model_key}"),
                                    ("ctx0_bce_pos_weight_constant", f"L3_{model_key}")]:
            cell = load_cell(target_level, model_key, config_name, "S2", 0)
            if cell:
                out.append({"model_key": model_key, "config_name": config_name, "label": label,
                             "best_val_f1": cell["best_val_f1"], "test_f1": cell["test_metrics"]["f1"]})
                break
    return out


def main():
    selected = {}
    for target_level in config.TARGET_LEVELS:
        cands = candidates_for_target(target_level)
        if not cands:
            print(f"[{target_level}] NO candidates found yet -- run the sweeps first")
            continue
        cands.sort(key=lambda c: c["best_val_f1"], reverse=True)
        top2 = cands[:2]
        selected[target_level] = top2
        print(f"\n[{target_level}] candidates by VAL F1:")
        for c in cands:
            marker = "  <= SELECTED" if c in top2 else ""
            print(f"  {c['label']:28s} model={c['model_key']:15s} val_f1={c['best_val_f1']:.4f} "
                  f"test_f1={c['test_f1']:.4f}{marker}")

    out_path = config.RESULTS_DIR / "selected_configs.json"
    out_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
