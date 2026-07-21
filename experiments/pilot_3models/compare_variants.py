"""Score baseline + all prompt variants on DEV (Imru2 + Nabigha, pooled),
using the span-level harness, and print a side-by-side comparison focused on
Trope and Kenning (the targeted failure modes).
"""
from pathlib import Path
from config import DEV_POEMS, ELEMENT_ORDER, RESULTS_DIR, POEMS
from analyze import load_all_runs, prf1
from ground_truth import load_ground_truth_spans
from span_scoring import score_span_level

VARIANTS_DIR = RESULTS_DIR / "dev_variants"

BASELINE_DIRS = {
    "Imru2": RESULTS_DIR,
    "Nabigha": RESULTS_DIR / "dev_nabigha_baseline",
}


def pooled_score(variant_key: str, criterion: str, threshold: float = 0.5) -> dict:
    """Pools TP/FP/FN/TN across both DEV poems, per provider per element."""
    pooled = {}
    for poem_key in DEV_POEMS:
        if variant_key == "baseline":
            out_dir = BASELINE_DIRS[poem_key]
        else:
            out_dir = VARIANTS_DIR / variant_key / poem_key
        by_provider = load_all_runs(out_dir)
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        scores = score_span_level(by_provider, gt_spans, n_verses, criterion, threshold)
        for provider in scores:
            pooled.setdefault(provider, {el: {"tp": 0, "fp": 0, "fn": 0} for el in ELEMENT_ORDER})
            for el in ELEMENT_ORDER:
                for k in ("tp", "fp", "fn"):
                    pooled[provider][el][k] += scores[provider][el][k]
    out = {}
    for provider, els in pooled.items():
        out[provider] = {el: prf1(v["tp"], v["fp"], v["fn"]) for el, v in els.items()}
    return out


def main():
    results = {}
    for variant_key in ["baseline", "v1_boundary", "v2_marker_independence", "v3_multi_figure", "v4_combined"]:
        results[variant_key] = {
            "strict": pooled_score(variant_key, "strict"),
            "token": pooled_score(variant_key, "token"),
        }

    providers = list(results["baseline"]["strict"].keys())
    for element in ["Trope", "Kenning", "Simile", "Antonymy"]:
        print(f"\n=== {element} (pooled DEV: Imru2+Nabigha) ===")
        print(f"{'Variant':<25} {'Model':<10} {'Strict F1':>10} {'Strict P/R':>12} {'Token F1':>9} {'Token P/R':>12}")
        for variant_key in results:
            for provider in providers:
                s = results[variant_key]["strict"][provider][element]
                t = results[variant_key]["token"][provider][element]
                print(f"{variant_key:<25} {provider:<10} {s['f1']:>10.3f} "
                      f"{s['precision']:.2f}/{s['recall']:.2f}     {t['f1']:>9.3f} {t['precision']:.2f}/{t['recall']:.2f}")
    return results


if __name__ == "__main__":
    main()
