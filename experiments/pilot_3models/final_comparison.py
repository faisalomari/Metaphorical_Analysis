"""Full comparison: baseline + all variants, raw TP/FP/FN + P/R/F1 per
element per model (pooled across DEV), plus v1_boundary run-to-run
consistency now that a genuine 2nd run exists.
"""
from config import DEV_POEMS, ELEMENT_ORDER, RESULTS_DIR, POEMS
from analyze import load_all_runs, prf1, run_consistency
from ground_truth import load_ground_truth_spans
from span_scoring import score_span_level

VARIANTS_DIR = RESULTS_DIR / "dev_variants"
BASELINE_DIRS = {"Imru2": RESULTS_DIR, "Nabigha": RESULTS_DIR / "dev_nabigha_baseline"}

ALL_VARIANTS = ["baseline", "v1_boundary", "v2_marker_independence", "v3_multi_figure",
                "v1_v2", "v1_v3", "v4_combined"]


def pooled_counts(variant_key: str, criterion: str, threshold: float = 0.5, run1_only: bool = True) -> dict:
    """run1_only=True restricts every variant (including v1_boundary, which now
    has 2 runs) to its first run only, so all variants are compared on the same
    1-run basis. Set False to use v1_boundary's real 2-run majority instead."""
    pooled = {}
    for poem_key in DEV_POEMS:
        out_dir = BASELINE_DIRS[poem_key] if variant_key == "baseline" else VARIANTS_DIR / variant_key / poem_key
        by_provider = load_all_runs(out_dir)
        if run1_only:
            by_provider = {p: [r for r in runs if r["run_index"] == 1] for p, runs in by_provider.items()}
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        scores = score_span_level(by_provider, gt_spans, n_verses, criterion, threshold)
        for provider in scores:
            pooled.setdefault(provider, {el: {"tp": 0, "fp": 0, "fn": 0} for el in ELEMENT_ORDER})
            for el in ELEMENT_ORDER:
                for k in ("tp", "fp", "fn"):
                    pooled[provider][el][k] += scores[provider][el][k]
    return pooled


def print_raw_counts_report():
    for element in ["Trope", "Kenning"]:
        print(f"\n{'='*100}\n{element} (pooled DEV, span-level STRICT criterion)\n{'='*100}")
        print(f"{'Variant':<25} {'Model':<10} {'TP':>4} {'FP':>4} {'FN':>4} {'Precision':>10} {'Recall':>8} {'F1':>7}")
        for variant_key in ALL_VARIANTS:
            counts = pooled_counts(variant_key, "strict")
            for provider in counts:
                c = counts[provider][element]
                s = prf1(c["tp"], c["fp"], c["fn"])
                print(f"{variant_key:<25} {provider:<10} {c['tp']:>4} {c['fp']:>4} {c['fn']:>4} "
                      f"{s['precision']:>10.3f} {s['recall']:>8.3f} {s['f1']:>7.3f}")


def print_v1_robustness_check():
    print(f"\n{'='*100}\nv1_boundary: run1-only vs 2-run-majority (does the headline number hold up?)\n{'='*100}")
    print(f"{'Element':<10} {'Model':<10} {'Run1-only F1':>13} {'2-run-majority F1':>18}")
    run1 = pooled_counts("v1_boundary", "strict", run1_only=True)
    both = pooled_counts("v1_boundary", "strict", run1_only=False)
    for element in ["Trope", "Kenning"]:
        for provider in run1:
            f1_1 = prf1(**{k: run1[provider][element][k] for k in ("tp", "fp", "fn")})["f1"]
            f1_2 = prf1(**{k: both[provider][element][k] for k in ("tp", "fp", "fn")})["f1"]
            print(f"{element:<10} {provider:<10} {f1_1:>13.3f} {f1_2:>18.3f}")


def print_v1_consistency():
    print(f"\n{'='*100}\nv1_boundary run-to-run consistency (2 real runs now)\n{'='*100}")
    for poem_key in DEV_POEMS:
        out_dir = VARIANTS_DIR / "v1_boundary" / poem_key
        by_provider = load_all_runs(out_dir)
        n_verses = POEMS[poem_key]["n_verses"]
        print(f"\n--- {poem_key} ({n_verses} verses) ---")
        for provider, runs in by_provider.items():
            cons = run_consistency(runs, n_verses)
            row = " | ".join(f"{el}: {cons[el]['agree']}/{cons[el]['total']}" for el in ELEMENT_ORDER)
            print(f"  {provider:<10} {row}")


if __name__ == "__main__":
    print_raw_counts_report()
    print_v1_robustness_check()
    print_v1_consistency()
