"""Step 4 figure: per-target F1 bar chart, Phase 5 baseline vs the 2 selected
Phase 6 configs vs the cheap ensemble (where available). Reads results/
phase6_stronger_ft/{selected_configs,step2_evaluation,step3_ensemble}.json
(must be run after evaluate.py and ensemble.py). Same simple matplotlib/Agg
convention as docs/phase5/figs/section4_learning_curve.png."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import phase6_config as config


def main():
    rows = json.loads((config.RESULTS_DIR / "step2_evaluation.json").read_text(encoding="utf-8"))["S2"]
    ensemble = json.loads((config.RESULTS_DIR / "step3_ensemble.json").read_text(encoding="utf-8"))

    by_target = {}
    for r in rows:
        by_target.setdefault(r["target_level"], []).append(r)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    targets = config.TARGET_LEVELS
    width = 0.2
    color_by_label = {
        "phase5_baseline": "#888888", "L1_context": "#4C72B0", "L2a_focal": "#DD8452",
        "L2b_cosine_llrd": "#937860", "L3_qwen2p5_3b": "#8172B2", "L3_arabert_large": "#C44E52",
        "ensemble": "#55A868",
    }
    labels_seen = []
    for i, target_level in enumerate(targets):
        cells = by_target.get(target_level, [])
        for j, cell in enumerate(cells[:3]):
            x = i + (j - 1) * width
            label = cell["label"]
            ax.bar(x, cell["f1_mean"], width=width, yerr=cell["f1_std"], capsize=3,
                   color=color_by_label.get(label, "#333333"),
                   label=label if label not in labels_seen else None)
            labels_seen.append(label)
        ens = ensemble.get(target_level)
        if ens and ens.get("status") == "ok":
            x = i + 2 * width
            ax.bar(x, ens["test_metrics"]["f1"], width=width, color=color_by_label["ensemble"],
                   label="ensemble" if "ensemble" not in labels_seen else None)
            labels_seen.append("ensemble")

    ax.set_xticks(range(len(targets)))
    ax.set_xticklabels(targets)
    ax.set_ylabel("Test F1 (S2)")
    ax.set_title("Phase 6: Phase 5 baseline vs selected configs vs ensemble, per target")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()

    out_path = config.FIGS_DIR / "phase6_f1_comparison.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
