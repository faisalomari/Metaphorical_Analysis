"""Final, frozen TEST report: baseline vs v4_combined on Imru1+Jarir+Abu_Tammam.
2-run majority is primary; single-run numbers shown for transparency.
Also: run-agreement rates, antonymy pooled across all 3 TEST poems, and a
Trope false-negative breakdown by ground-truth subtype for v4_combined.
"""
from pathlib import Path
from collections import Counter

from config import TEST_POEMS, ELEMENT_ORDER, RESULTS_DIR, POEMS
from analyze import load_all_runs, prf1, run_consistency
from ground_truth import load_ground_truth_spans
from span_scoring import score_span_level, majority_exists_and_appearance
from span_matching import strict_overlap

TEST_DIR = RESULTS_DIR / "test_final"


def pooled_counts(prompt_key: str, criterion: str, run1_only: bool = False, threshold: float = 0.5) -> dict:
    pooled = {}
    for poem_key in TEST_POEMS:
        out_dir = TEST_DIR / prompt_key / poem_key
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


def print_main_report():
    for prompt_key in ["baseline", "v4_combined"]:
        print(f"\n{'#'*110}\n# {prompt_key.upper()} — TEST (pooled Imru1+Jarir+Abu_Tammam), 2-run majority (primary)\n{'#'*110}")
        strict_2run = pooled_counts(prompt_key, "strict", run1_only=False)
        token_2run = pooled_counts(prompt_key, "token", run1_only=False)
        for element in ELEMENT_ORDER:
            print(f"\n--- {element} ---")
            print(f"{'Model':<10} {'TP':>4} {'FP':>4} {'FN':>4} {'Precision':>10} {'Recall':>8} {'F1(strict)':>11}  |  "
                  f"{'TP':>4} {'FP':>4} {'FN':>4} {'Precision':>10} {'Recall':>8} {'F1(token)':>10}")
            for provider in strict_2run:
                cs = strict_2run[provider][element]
                ct = token_2run[provider][element]
                ss = prf1(cs["tp"], cs["fp"], cs["fn"])
                st = prf1(ct["tp"], ct["fp"], ct["fn"])
                print(f"{provider:<10} {cs['tp']:>4} {cs['fp']:>4} {cs['fn']:>4} {ss['precision']:>10.3f} {ss['recall']:>8.3f} {ss['f1']:>11.3f}  |  "
                      f"{ct['tp']:>4} {ct['fp']:>4} {ct['fn']:>4} {st['precision']:>10.3f} {st['recall']:>8.3f} {st['f1']:>10.3f}")


def print_run1_transparency():
    print(f"\n{'#'*110}\n# Single-run (run1-only) numbers, for transparency vs the 2-run-majority primary numbers above\n{'#'*110}")
    for prompt_key in ["baseline", "v4_combined"]:
        strict_1run = pooled_counts(prompt_key, "strict", run1_only=True)
        print(f"\n--- {prompt_key}, run1-only, strict criterion ---")
        for element in ["Trope", "Kenning"]:
            for provider in strict_1run:
                c = strict_1run[provider][element]
                s = prf1(c["tp"], c["fp"], c["fn"])
                print(f"  {element:<10} {provider:<10} F1={s['f1']:.3f} (P={s['precision']:.2f}/R={s['recall']:.2f})")


def print_run_agreement():
    print(f"\n{'#'*110}\n# Run-to-run agreement rates (decision-level, pooled TEST)\n{'#'*110}")
    for prompt_key in ["baseline", "v4_combined"]:
        pooled = {}
        for poem_key in TEST_POEMS:
            out_dir = TEST_DIR / prompt_key / poem_key
            by_provider = load_all_runs(out_dir)
            n_verses = POEMS[poem_key]["n_verses"]
            for provider, runs in by_provider.items():
                cons = run_consistency(runs, n_verses)
                pooled.setdefault(provider, {el: {"agree": 0, "total": 0} for el in ELEMENT_ORDER})
                for el in ELEMENT_ORDER:
                    pooled[provider][el]["agree"] += cons[el]["agree"]
                    pooled[provider][el]["total"] += cons[el]["total"]
        print(f"\n--- {prompt_key} ---")
        print(f"{'Model':<10} " + " ".join(f"{el:>16}" for el in ELEMENT_ORDER))
        for provider, els in pooled.items():
            row = " ".join(f"{els[el]['agree']}/{els[el]['total']} ({els[el]['agree']/els[el]['total']*100:.0f}%)".rjust(16)
                            for el in ELEMENT_ORDER)
            print(f"{provider:<10} {row}")


def trope_subtype_breakdown(prompt_key: str):
    print(f"\n{'#'*110}\n# Trope false-negative breakdown by ground-truth subtype — {prompt_key} (pooled across 3 models, TEST)\n{'#'*110}")
    subtype_misses = Counter()
    subtype_totals = Counter()
    for poem_key in TEST_POEMS:
        out_dir = TEST_DIR / prompt_key / poem_key
        by_provider = load_all_runs(out_dir)
        gt = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        for verse_no in range(1, n_verses + 1):
            for inst in gt[verse_no]["Trope"]:
                subtype = inst["secondary"] or inst["primary"]
                subtype_totals[subtype] += 1
                hit = False
                for provider, runs in by_provider.items():
                    exists, appearance = majority_exists_and_appearance(runs, "Trope", verse_no)
                    if exists and strict_overlap(appearance or "", inst["span"]):
                        hit = True
                if not hit:
                    subtype_misses[subtype] += 1
    for subtype, total in subtype_totals.most_common():
        missed = subtype_misses[subtype]
        print(f"  {subtype:<25} missed {missed}/{total} ({missed/total*100:.0f}%)")


if __name__ == "__main__":
    print_main_report()
    print_run1_transparency()
    print_run_agreement()
    trope_subtype_breakdown("baseline")
    trope_subtype_breakdown("v4_combined")
