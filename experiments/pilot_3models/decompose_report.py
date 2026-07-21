"""Per-element decomposition report (DEV only, supplementary — PROJECT_STATE.md
item 5a). Compares each decomposed single-element prompt against v4_combined,
both scored as 2-run majority, pooled across DEV (Imru2 + Nabigha).
"""
from config import DEV_POEMS, ELEMENT_ORDER, RESULTS_DIR, POEMS
from analyze import load_all_runs, load_all_runs_single_element, prf1
from ground_truth import load_ground_truth_spans
from span_scoring import majority_exists_and_appearance
from span_matching import best_match

VARIANTS_DIR = RESULTS_DIR / "dev_variants"


def run_consistency_single(runs: list, element: str, n_verses: int) -> dict:
    agree, total = 0, 0
    for verse_no in range(1, n_verses + 1):
        values = []
        for run in runs:
            v = run["verses"].get(verse_no)
            if v is not None and element in v and v[element]["exists"] is not None:
                values.append(v[element]["exists"])
        if len(values) < 2:
            continue
        total += 1
        if len(set(values)) == 1:
            agree += 1
    return {"agree": agree, "total": total, "rate": (agree / total) if total else None}


def pooled_counts_v4(criterion: str) -> dict:
    """v4_combined, 2-run majority, pooled DEV. Returns {provider: {el: {tp,fp,fn}}}."""
    pooled = {}
    for poem_key in DEV_POEMS:
        out_dir = VARIANTS_DIR / "v4_combined" / poem_key
        by_provider = load_all_runs(out_dir)
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        for provider, runs in by_provider.items():
            pooled.setdefault(provider, {el: {"tp": 0, "fp": 0, "fn": 0} for el in ELEMENT_ORDER})
            for element in ELEMENT_ORDER:
                for verse_no in range(1, n_verses + 1):
                    exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
                    gt_instances = gt_spans[verse_no][element]
                    gt_texts = [g["span"] for g in gt_instances]
                    if exists is None:
                        continue
                    if not exists:
                        pooled[provider][element]["fn"] += len(gt_texts)
                        continue
                    if not gt_texts:
                        pooled[provider][element]["fp"] += 1
                        continue
                    match_idx = best_match(appearance or "", gt_texts, criterion, 0.5)
                    if match_idx is None:
                        pooled[provider][element]["fp"] += 1
                        pooled[provider][element]["fn"] += len(gt_texts)
                    else:
                        pooled[provider][element]["tp"] += 1
                        pooled[provider][element]["fn"] += len(gt_texts) - 1
    return pooled


def pooled_counts_decomposed(element: str, criterion: str) -> dict:
    """decomposed_{element}, 2-run majority, pooled DEV. Returns {provider: {tp,fp,fn}}."""
    pooled = {}
    for poem_key in DEV_POEMS:
        out_dir = VARIANTS_DIR / f"decomposed_{element}" / poem_key
        by_provider = load_all_runs_single_element(out_dir, element)
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        for provider, runs in by_provider.items():
            pooled.setdefault(provider, {"tp": 0, "fp": 0, "fn": 0})
            for verse_no in range(1, n_verses + 1):
                exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
                gt_instances = gt_spans[verse_no][element]
                gt_texts = [g["span"] for g in gt_instances]
                if exists is None:
                    continue
                if not exists:
                    pooled[provider]["fn"] += len(gt_texts)
                    continue
                if not gt_texts:
                    pooled[provider]["fp"] += 1
                    continue
                match_idx = best_match(appearance or "", gt_texts, criterion, 0.5)
                if match_idx is None:
                    pooled[provider]["fp"] += 1
                    pooled[provider]["fn"] += len(gt_texts)
                else:
                    pooled[provider]["tp"] += 1
                    pooled[provider]["fn"] += len(gt_texts) - 1
    return pooled


def pooled_agreement_v4() -> dict:
    pooled = {}
    for poem_key in DEV_POEMS:
        out_dir = VARIANTS_DIR / "v4_combined" / poem_key
        by_provider = load_all_runs(out_dir)
        n_verses = POEMS[poem_key]["n_verses"]
        for provider, runs in by_provider.items():
            pooled.setdefault(provider, {el: {"agree": 0, "total": 0} for el in ELEMENT_ORDER})
            for element in ELEMENT_ORDER:
                cons = run_consistency_single(runs, element, n_verses)
                pooled[provider][element]["agree"] += cons["agree"]
                pooled[provider][element]["total"] += cons["total"]
    return pooled


def pooled_agreement_decomposed(element: str) -> dict:
    pooled = {}
    for poem_key in DEV_POEMS:
        out_dir = VARIANTS_DIR / f"decomposed_{element}" / poem_key
        by_provider = load_all_runs_single_element(out_dir, element)
        n_verses = POEMS[poem_key]["n_verses"]
        for provider, runs in by_provider.items():
            pooled.setdefault(provider, {"agree": 0, "total": 0})
            cons = run_consistency_single(runs, element, n_verses)
            pooled[provider]["agree"] += cons["agree"]
            pooled[provider]["total"] += cons["total"]
    return pooled


def main():
    print(f"\n{'#'*115}\n# Per-element decomposition vs v4_combined — DEV only (Imru2+Nabigha), 2-run majority both sides\n{'#'*115}")

    v4_strict = pooled_counts_v4("strict")
    v4_token = pooled_counts_v4("token")
    v4_agree = pooled_agreement_v4()

    for element in ELEMENT_ORDER:
        dec_strict = pooled_counts_decomposed(element, "strict")
        dec_token = pooled_counts_decomposed(element, "token")
        dec_agree = pooled_agreement_decomposed(element)

        print(f"\n=== {element} ===")
        print(f"{'Config':<14} {'Model':<10} {'TP':>4} {'FP':>4} {'FN':>4} {'F1(strict)':>11} {'P/R(strict)':>13}  |  "
              f"{'TP':>4} {'FP':>4} {'FN':>4} {'F1(token)':>10} {'P/R(token)':>12}  |  {'Agree':>12}")
        for provider in v4_strict:
            vs, vt = v4_strict[provider][element], v4_token[provider][element]
            ds, dt = dec_strict[provider], dec_token[provider]
            vs_s, vt_s = prf1(vs["tp"], vs["fp"], vs["fn"]), prf1(vt["tp"], vt["fp"], vt["fn"])
            ds_s, dt_s = prf1(ds["tp"], ds["fp"], ds["fn"]), prf1(dt["tp"], dt["fp"], dt["fn"])
            va, da = v4_agree[provider][element], dec_agree[provider]
            va_rate = f"{va['agree']}/{va['total']} ({va['agree']/va['total']*100:.0f}%)" if va['total'] else "n/a"
            da_rate = f"{da['agree']}/{da['total']} ({da['agree']/da['total']*100:.0f}%)" if da['total'] else "n/a"

            print(f"{'v4_combined':<14} {provider:<10} {vs['tp']:>4} {vs['fp']:>4} {vs['fn']:>4} {vs_s['f1']:>11.3f} "
                  f"{vs_s['precision']:.2f}/{vs_s['recall']:.2f}        |  "
                  f"{vt['tp']:>4} {vt['fp']:>4} {vt['fn']:>4} {vt_s['f1']:>10.3f} {vt_s['precision']:.2f}/{vt_s['recall']:.2f}       |  {va_rate:>12}")
            print(f"{'decomposed':<14} {provider:<10} {ds['tp']:>4} {ds['fp']:>4} {ds['fn']:>4} {ds_s['f1']:>11.3f} "
                  f"{ds_s['precision']:.2f}/{ds_s['recall']:.2f}        |  "
                  f"{dt['tp']:>4} {dt['fp']:>4} {dt['fn']:>4} {dt_s['f1']:>10.3f} {dt_s['precision']:.2f}/{dt_s['recall']:.2f}       |  {da_rate:>12}")


if __name__ == "__main__":
    main()
