"""Span-aware scoring: an instance is correct only if the predicted
appearance-span overlaps a ground-truth span for that verse+element.
Multi-figure verses (multiple ground-truth instances of the same element in
one verse) are handled by matching the single model-predicted span against
whichever ground-truth instance it best matches; any remaining unmatched
ground-truth instances count as additional false negatives.

Reports both a strict-overlap criterion and a token-overlap-threshold
criterion, plus the original verse-level (exists/not-exists only) score for
direct old-vs-new comparison.
"""
from config import ELEMENT_ORDER, POEMS
from analyze import prf1
from ground_truth import load_ground_truth_spans, load_ground_truth
from span_matching import best_match


def majority_exists_and_appearance(runs: list, element: str, verse_no: int):
    """Majority-vote exists across runs; appearance = the predicted span from
    a run whose vote matches the majority (first found), or None."""
    votes = []
    for run in runs:
        v = run["verses"].get(verse_no)
        if v is not None and v[element]["exists"] is not None:
            votes.append(v[element]["exists"])
    if not votes:
        return None, None
    majority = sum(votes) > len(votes) / 2
    if not majority:
        return False, None
    for run in runs:
        v = run["verses"].get(verse_no)
        if v is not None and v[element]["exists"] is True:
            return True, v[element]["appearance"]
    return True, None


def score_span_level(by_provider: dict, gt_spans: dict, n_verses: int, criterion: str, threshold: float = 0.5) -> dict:
    out = {}
    for provider, runs in by_provider.items():
        out[provider] = {}
        for element in ELEMENT_ORDER:
            tp = fp = fn = tn = 0
            for verse_no in range(1, n_verses + 1):
                exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
                gt_instances = gt_spans[verse_no][element]
                gt_texts = [g["span"] for g in gt_instances]

                if exists is None:
                    continue  # unparseable, excluded
                if not exists:
                    fn += len(gt_texts)
                    if not gt_texts:
                        tn += 1
                    continue
                # exists == True
                if not gt_texts:
                    fp += 1
                    continue
                match_idx = best_match(appearance or "", gt_texts, criterion, threshold)
                if match_idx is None:
                    fp += 1
                    fn += len(gt_texts)
                else:
                    tp += 1
                    fn += len(gt_texts) - 1
            s = prf1(tp, fp, fn)
            s["tn"] = tn
            out[provider][element] = s
    return out


def score_verse_level(by_provider: dict, gt_bool: dict, n_verses: int) -> dict:
    """The ORIGINAL (Step-1-pilot) scoring: verse+element boolean only, no span check."""
    from analyze import per_verse_majority
    out = {}
    for provider, runs in by_provider.items():
        out[provider] = {}
        for element in ELEMENT_ORDER:
            tp = fp = fn = tn = 0
            for verse_no in range(1, n_verses + 1):
                pred = per_verse_majority(runs, element, verse_no)
                truth = gt_bool[verse_no][element]
                if pred is None:
                    continue
                if pred and truth:
                    tp += 1
                elif pred and not truth:
                    fp += 1
                elif not pred and truth:
                    fn += 1
                else:
                    tn += 1
            s = prf1(tp, fp, fn)
            s["tn"] = tn
            out[provider][element] = s
    return out


def print_side_by_side(old, strict, token, by_provider):
    print(f"{'Element':<10} {'Model':<20} {'OLD F1':>8} {'STRICT F1':>10} {'TOKEN F1':>9}   "
          f"{'OLD P/R':>12} {'STRICT P/R':>12} {'TOKEN P/R':>12}")
    print("-" * 110)
    for element in ELEMENT_ORDER:
        for provider in by_provider:
            o, s, t = old[provider][element], strict[provider][element], token[provider][element]
            print(f"{element:<10} {provider:<20} {o['f1']:>8.3f} {s['f1']:>10.3f} {t['f1']:>9.3f}   "
                  f"{o['precision']:.2f}/{o['recall']:.2f}      {s['precision']:.2f}/{s['recall']:.2f}      "
                  f"{t['precision']:.2f}/{t['recall']:.2f}")


if __name__ == "__main__":
    from analyze import load_all_runs
    poem_key = "Imru2"
    by_provider = load_all_runs()
    gt_spans = load_ground_truth_spans(poem_key)
    gt_bool = load_ground_truth(poem_key)
    n_verses = POEMS[poem_key]["n_verses"]

    old = score_verse_level(by_provider, gt_bool, n_verses)
    strict = score_span_level(by_provider, gt_spans, n_verses, "strict")
    token = score_span_level(by_provider, gt_spans, n_verses, "token", threshold=0.5)
    print_side_by_side(old, strict, token, by_provider)
