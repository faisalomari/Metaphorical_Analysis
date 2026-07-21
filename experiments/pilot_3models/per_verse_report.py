"""Per-verse granularity report (PROJECT_STATE.md §3g). Completes the 2x2
grid (whole-poem x all-4 / whole-poem x single-element / per-verse x all-4 /
per-verse x single-element), Imru2 ONLY (re-sliced from stored DEV results,
not pooled with Nabigha).
"""
import json
from config import ELEMENT_ORDER, RESULTS_DIR, POEMS, MODELS
from analyze import load_all_runs, load_all_runs_single_element, prf1, run_consistency
from ground_truth import load_ground_truth_spans
from span_scoring import score_span_level, majority_exists_and_appearance
from span_matching import best_match
from decompose_report import run_consistency_single

POEM_KEY = "Imru2"
N_VERSES = POEMS[POEM_KEY]["n_verses"]
VARIANTS_DIR = RESULTS_DIR / "dev_variants"
PER_VERSE_DIR = RESULTS_DIR / "per_verse"


def score_single_element_dir(out_dir, element, criterion):
    """Like decompose_report's pooled_counts_decomposed, but ONE poem only."""
    by_provider = load_all_runs_single_element(out_dir, element)
    gt_spans = load_ground_truth_spans(POEM_KEY)
    counts = {}
    for provider, runs in by_provider.items():
        tp = fp = fn = 0
        for verse_no in range(1, N_VERSES + 1):
            exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
            gt_texts = [g["span"] for g in gt_spans[verse_no][element]]
            if exists is None:
                continue
            if not exists:
                fn += len(gt_texts)
                continue
            if not gt_texts:
                fp += 1
                continue
            match_idx = best_match(appearance or "", gt_texts, criterion, 0.5)
            if match_idx is None:
                fp += 1
                fn += len(gt_texts)
            else:
                tp += 1
                fn += len(gt_texts) - 1
        counts[provider] = {"tp": tp, "fp": fp, "fn": fn}
    return counts, by_provider


def agreement_single_element_dir(out_dir, element):
    by_provider = load_all_runs_single_element(out_dir, element)
    out = {}
    for provider, runs in by_provider.items():
        out[provider] = run_consistency_single(runs, element, N_VERSES)
    return out


def cost_from_manifest(out_dir):
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    total = 0.0
    per_provider = {}
    for rec in manifest:
        provider = rec["provider"]
        spec = MODELS[provider]
        u = rec["usage"] or {}
        cost = (u.get("input_tokens") or 0) / 1e6 * spec["price_in"] + (u.get("output_tokens") or 0) / 1e6 * spec["price_out"]
        total += cost
        per_provider[provider] = per_provider.get(provider, 0.0) + cost
    return total, per_provider


def main():
    gt_spans = load_ground_truth_spans(POEM_KEY)
    gt_counts = {el: sum(len(gt_spans[no][el]) for no in gt_spans) for el in ELEMENT_ORDER}
    print(f"Imru2-only ground truth support (deduped): {gt_counts}")

    # --- Cell 1: whole-poem x all-4 (v4_combined, Imru2 only) ---
    v4_dir = VARIANTS_DIR / "v4_combined" / POEM_KEY
    v4_by_provider = load_all_runs(v4_dir)
    v4_strict = score_span_level(v4_by_provider, gt_spans, N_VERSES, "strict")
    v4_token = score_span_level(v4_by_provider, gt_spans, N_VERSES, "token")
    v4_agree = {p: run_consistency(runs, N_VERSES) for p, runs in v4_by_provider.items()}

    # --- Cell 3: per-verse x all-4 (mode A) ---
    a_dir = PER_VERSE_DIR / "mode_a" / POEM_KEY
    a_by_provider = load_all_runs(a_dir)
    a_strict = score_span_level(a_by_provider, gt_spans, N_VERSES, "strict")
    a_token = score_span_level(a_by_provider, gt_spans, N_VERSES, "token")
    a_agree = {p: run_consistency(runs, N_VERSES) for p, runs in a_by_provider.items()}
    a_cost_total, a_cost_provider = cost_from_manifest(a_dir)

    print(f"\nMode A total cost: ${a_cost_total:.3f}")

    print(f"\n{'='*130}")
    print("CELL 1 (whole-poem x all-4, v4_combined) vs CELL 3 (per-verse x all-4, mode A) -- Imru2 only")
    print(f"{'='*130}")
    header = (f"{'Element':<10} {'Model':<10} | {'whole TP/FP/FN':<16} {'whole F1(s)':>11} {'whole F1(t)':>11} {'whole agree':>12} | "
              f"{'verse TP/FP/FN':<16} {'verse F1(s)':>11} {'verse F1(t)':>11} {'verse agree':>12}")
    print(header)
    for element in ELEMENT_ORDER:
        for provider in v4_by_provider:
            vs, vt = v4_strict[provider][element], v4_token[provider][element]
            as_, at = a_strict[provider][element], a_token[provider][element]
            va = v4_agree[provider][element]
            aa = a_agree[provider][element]
            va_s = f"{va['agree']}/{va['total']}" if va['total'] else "n/a"
            aa_s = f"{aa['agree']}/{aa['total']}" if aa['total'] else "n/a"
            vs_counts = f"{vs['tp']}/{vs['fp']}/{vs['fn']}"
            as_counts = f"{as_['tp']}/{as_['fp']}/{as_['fn']}"
            print(f"{element:<10} {provider:<10} | {vs_counts:<16} {vs['f1']:>11.3f} {vt['f1']:>11.3f} {va_s:>12} | "
                  f"{as_counts:<16} {as_['f1']:>11.3f} {at['f1']:>11.3f} {aa_s:>12}")

    # --- Cell 2 & 4: single-element ---
    print(f"\n{'='*130}")
    print("CELL 2 (whole-poem x single-element, decomposed) vs CELL 4 (per-verse x single-element, mode B) -- Imru2 only")
    print(f"{'='*130}")
    b_cost_total = 0.0
    for element in ELEMENT_ORDER:
        dec_dir = VARIANTS_DIR / f"decomposed_{element}" / POEM_KEY
        b_dir = PER_VERSE_DIR / f"mode_b_{element}" / POEM_KEY
        if not b_dir.exists():
            print(f"\n=== {element}: mode B data not yet available, skipping ===")
            continue
        dec_counts, _ = score_single_element_dir(dec_dir, element, "strict")
        dec_counts_tok, _ = score_single_element_dir(dec_dir, element, "token")
        dec_agree = agreement_single_element_dir(dec_dir, element)
        b_counts, _ = score_single_element_dir(b_dir, element, "strict")
        b_counts_tok, _ = score_single_element_dir(b_dir, element, "token")
        b_agree = agreement_single_element_dir(b_dir, element)
        b_cost, _ = cost_from_manifest(b_dir)
        b_cost_total += b_cost

        print(f"\n=== {element} (mode B cost: ${b_cost:.3f}) ===")
        for provider in dec_counts:
            ds, dt = prf1(**dec_counts[provider]), prf1(**dec_counts_tok[provider])
            bs, bt = prf1(**b_counts[provider]), prf1(**b_counts_tok[provider])
            da, ba = dec_agree[provider], b_agree[provider]
            da_s = f"{da['agree']}/{da['total']}" if da['total'] else "n/a"
            ba_s = f"{ba['agree']}/{ba['total']}" if ba['total'] else "n/a"
            print(f"  {provider:<10} | whole TP/FP/FN {ds['tp']}/{ds['fp']}/{ds['fn']:<3} F1(s)={ds['f1']:.3f} F1(t)={dt['f1']:.3f} agree={da_s:>8} | "
                  f"verse TP/FP/FN {bs['tp']}/{bs['fp']}/{bs['fn']:<3} F1(s)={bs['f1']:.3f} F1(t)={bt['f1']:.3f} agree={ba_s:>8}")

    print(f"\nMode B total cost so far: ${b_cost_total:.3f}")
    print(f"\nGrand total new-call cost (A + B available so far): ${a_cost_total + b_cost_total:.3f}")


if __name__ == "__main__":
    main()
