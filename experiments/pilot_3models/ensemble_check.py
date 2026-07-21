"""Compute majority-vote-across-models (ensemble) F1 per element, reusing the
pilot's already-collected 3-model x 2-run outputs. No new API calls.

For each verse+element: take each model's own majority vote across its 2
runs (already computed by analyze.per_verse_majority), then majority-vote
those 3 per-model verdicts (2-of-3) against ground truth.
"""
from config import ELEMENT_ORDER, N_RUNS
from analyze import load_all_runs, per_verse_majority, prf1
from ground_truth import load_ground_truth, N_VERSES


def ensemble_vote(by_provider: dict, element: str, verse_no: int):
    votes = []
    for provider, runs in by_provider.items():
        v = per_verse_majority(runs, element, verse_no)
        if v is not None:
            votes.append(v)
    if not votes:
        return None
    return sum(votes) > len(votes) / 2


def main():
    by_provider = load_all_runs()
    gt = load_ground_truth()

    print(f"{'Element':<10} {'Precision':>10} {'Recall':>8} {'F1':>6} {'TP':>4} {'FP':>4} {'FN':>4} {'TN':>4}")
    print("-" * 60)
    ensemble_scores = {}
    for element in ELEMENT_ORDER:
        tp = fp = fn = tn = 0
        for verse_no in range(1, N_VERSES + 1):
            pred = ensemble_vote(by_provider, element, verse_no)
            truth = gt[verse_no][element]
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
        ensemble_scores[element] = s
        print(f"{element:<10} {s['precision']:>10.3f} {s['recall']:>8.3f} {s['f1']:>6.3f} "
              f"{s['tp']:>4} {s['fp']:>4} {s['fn']:>4} {s['tn']:>4}")
    return ensemble_scores


if __name__ == "__main__":
    main()
