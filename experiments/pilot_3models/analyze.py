"""Combine raw model outputs into comparison tables: per-model results,
run-to-run consistency, cross-model agreement, and precision/recall/F1
against Dr. Ali Hussein's ground truth.
"""
import json
from config import RAW_DIR, RESULTS_DIR, ELEMENT_ORDER
from parsing import parse_response, parse_response_single_element
from ground_truth import load_ground_truth, N_VERSES


def load_all_runs(out_dir=None):
    """Returns {provider: [{run_index, verses, parse_errors, meta}, ...]}"""
    out_dir = out_dir or RESULTS_DIR
    raw_dir = out_dir / "raw"
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    by_provider = {}
    for rec in manifest:
        raw_text = (raw_dir / f"{rec['provider']}_run{rec['run_index']}.txt").read_text(encoding="utf-8")
        parsed = parse_response(raw_text) if not rec.get("error") else {"verses": {}, "parse_errors": [f"API error: {rec['error']}"], "n_verses_parsed": 0}
        by_provider.setdefault(rec["provider"], []).append({"run_index": rec["run_index"], "meta": rec, **parsed})
    return by_provider


def load_all_runs_single_element(out_dir, element: str):
    """Like load_all_runs, but for a decomposed single-element run directory
    (parsed with parse_response_single_element instead of parse_response)."""
    raw_dir = out_dir / "raw"
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    by_provider = {}
    for rec in manifest:
        raw_text = (raw_dir / f"{rec['provider']}_run{rec['run_index']}.txt").read_text(encoding="utf-8")
        parsed = parse_response_single_element(raw_text, element) if not rec.get("error") else {"verses": {}, "parse_errors": [f"API error: {rec['error']}"], "n_verses_parsed": 0}
        by_provider.setdefault(rec["provider"], []).append({"run_index": rec["run_index"], "meta": rec, **parsed})
    return by_provider


def per_verse_majority(runs: list, element: str, verse_no: int):
    """Majority vote across the runs of ONE provider for one verse+element. Returns bool|None."""
    votes = []
    for run in runs:
        v = run["verses"].get(verse_no)
        if v is None:
            continue
        exists = v[element]["exists"]
        if exists is not None:
            votes.append(exists)
    if not votes:
        return None
    return sum(votes) > len(votes) / 2


def run_consistency(runs: list, n_verses: int = N_VERSES) -> dict:
    """For each element, fraction of verses where all runs of this provider agree."""
    out = {}
    for element in ELEMENT_ORDER:
        agree, total = 0, 0
        for verse_no in range(1, n_verses + 1):
            values = []
            for run in runs:
                v = run["verses"].get(verse_no)
                if v is not None and v[element]["exists"] is not None:
                    values.append(v[element]["exists"])
            if len(values) < 2:
                continue
            total += 1
            if len(set(values)) == 1:
                agree += 1
        out[element] = {"agree": agree, "total": total, "rate": (agree / total) if total else None}
    return out


def prf1(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def score_vs_ground_truth(by_provider: dict, gt: dict, n_verses: int = N_VERSES) -> dict:
    """Per-provider, per-element P/R/F1 using majority vote across that provider's runs."""
    out = {}
    for provider, runs in by_provider.items():
        out[provider] = {}
        for element in ELEMENT_ORDER:
            tp = fp = fn = tn = 0
            for verse_no in range(1, n_verses + 1):
                pred = per_verse_majority(runs, element, verse_no)
                truth = gt[verse_no][element]
                if pred is None:
                    continue  # unparseable prediction for this verse, excluded from scoring
                if pred and truth:
                    tp += 1
                elif pred and not truth:
                    fp += 1
                elif not pred and truth:
                    fn += 1
                else:
                    tn += 1
            out[provider][element] = prf1(tp, fp, fn)
            out[provider][element]["tn"] = tn
    return out


def cross_model_agreement(by_provider: dict, n_verses: int = N_VERSES) -> dict:
    """For each verse+element, does the majority vote agree across all 3 providers?"""
    providers = list(by_provider.keys())
    out = {}
    for element in ELEMENT_ORDER:
        all_agree, any_data = 0, 0
        rows = []
        for verse_no in range(1, n_verses + 1):
            votes = {}
            for provider in providers:
                votes[provider] = per_verse_majority(by_provider[provider], element, verse_no)
            present_votes = [v for v in votes.values() if v is not None]
            if not present_votes:
                continue
            any_data += 1
            agree = len(set(present_votes)) == 1
            all_agree += int(agree)
            rows.append({"verse": verse_no, "votes": votes, "all_agree": agree})
        out[element] = {"rows": rows, "all_agree_count": all_agree, "total": any_data}
    return out


def build_comparison_table(by_provider: dict, n_verses: int = N_VERSES) -> list:
    """One row per verse, with each provider's majority-vote appearance text per element."""
    providers = list(by_provider.keys())
    table = []
    for verse_no in range(1, n_verses + 1):
        row = {"verse": verse_no}
        for element in ELEMENT_ORDER:
            for provider in providers:
                runs = by_provider[provider]
                exists = per_verse_majority(runs, element, verse_no)
                appearance = None
                for run in runs:
                    v = run["verses"].get(verse_no)
                    if v and v[element]["exists"]:
                        appearance = v[element]["appearance"]
                        break
                row[(element, provider)] = {"exists": exists, "appearance": appearance}
        table.append(row)
    return table


if __name__ == "__main__":
    by_provider = load_all_runs()
    gt = load_ground_truth()
    scores = score_vs_ground_truth(by_provider, gt)
    print(json.dumps(scores, indent=2, ensure_ascii=False))
