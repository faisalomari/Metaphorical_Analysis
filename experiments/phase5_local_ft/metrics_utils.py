"""Shared TP/FP/FN/precision/recall/F1 (verse-level binary), per CLAUDE.md
rule 3: always report raw counts alongside precision/recall/F1."""


def prf(y_true: list, y_pred: list) -> dict:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tn = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": precision, "recall": recall, "f1": f1}


def best_threshold(y_true: list, probs: list, grid: list) -> dict:
    """Picks the threshold (from `grid`) maximizing F1 on (y_true, probs). VAL ONLY."""
    best = {"threshold": 0.5, "f1": -1.0}
    for thr in grid:
        y_pred = [1 if p >= thr else 0 for p in probs]
        m = prf(y_true, y_pred)
        if m["f1"] > best["f1"]:
            best = {"threshold": thr, **m}
    return best
