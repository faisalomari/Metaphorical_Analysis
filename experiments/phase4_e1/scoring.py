"""Span-level scoring for E1 (strict + token-overlap, CLAUDE.md rule 4),
reporting raw TP/FP/FN always (rule 3), split by abu_nuwas/other poem tag
and overall, with per-poem paired differences between sets and a bootstrap
CI over poems for each pairwise (F1_set1 - F1_set2).

Only scores the مجاز (Trope) element (this pilot's focus) — not the other 3
elements, since the few-shot block only targets استعارة فعل and the eval
pool's ground truth here is pulled from the Ali-corpus JSON, not the frozen
xlsx sheets.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_config import ELEMENT, EVAL_POOL_PATH, PILOT_DIR, RESULTS_DIR, SET_NAMES  # noqa: E402
from ali_poems_io import load_ali_gt_spans, load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402
from parsing import parse_response  # noqa: E402
from span_matching import best_match  # noqa: E402


def load_runs(out_dir: Path, set_name: str, poem_id: str, provider: str) -> list:
    """Returns parsed {verse_no: {element: {"exists":, "appearance":}}} per run,
    for every run_index found in the manifest for this (set, poem, provider)."""
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    runs = []
    for r in manifest:
        if (r["set_name"], r["poem_id"], r["provider"]) != (set_name, poem_id, provider):
            continue
        if r.get("error"):
            continue
        raw_text = (out_dir / r["raw_text_file"]).read_text(encoding="utf-8")
        parsed = parse_response(raw_text)
        runs.append({"run_index": r["run_index"], "verses": parsed["verses"]})
    return runs


def majority_exists_and_appearance(runs: list, element: str, verse_no: int):
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


def score_poem(runs: list, gt_spans: dict, n_verses: int, criterion: str, threshold: float = 0.5) -> dict:
    """TP/FP/FN for one poem, one element, pooled over its verses."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        exists, appearance = majority_exists_and_appearance(runs, ELEMENT, verse_no)
        gt_texts = [g["span"] for g in gt_spans[verse_no][ELEMENT]]
        if exists is None:
            continue
        if not exists:
            fn += len(gt_texts)
            continue
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
    return {"tp": tp, "fp": fp, "fn": fn}


def score_set(out_dir: Path, set_name: str, provider: str, pool: list, criterion: str) -> dict:
    """Per-poem TP/FP/FN for one (set, provider), plus pooled overall/abu_nuwas/other."""
    per_poem = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        pj = load_poem_json(poem_id)
        gt_spans = load_ali_gt_spans(pj)
        runs = load_runs(out_dir, set_name, poem_id, provider)
        counts = score_poem(runs, gt_spans, pj["verse_count"], criterion)
        counts["tag"] = poem["tag"]
        per_poem[poem_id] = counts

    def pool_counts(tag=None):
        tp = sum(c["tp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fp = sum(c["fp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fn = sum(c["fn"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}

    return {
        "per_poem": per_poem,
        "overall": pool_counts(),
        "abu_nuwas": pool_counts("abu_nuwas"),
        "other": pool_counts("other"),
    }


def poem_f1(counts: dict) -> float:
    return prf1(counts["tp"], counts["fp"], counts["fn"])["f1"]


def bootstrap_ci_pairwise(per_poem_a: dict, per_poem_b: dict, n_iter: int = 2000, seed: int = 0):
    """Bootstrap CI over poems for pooled F1_a - F1_b. Resamples the shared
    poem ids with replacement, recomputes pooled F1 for each set each draw."""
    poem_ids = sorted(set(per_poem_a) & set(per_poem_b))
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_iter):
        sample = [rng.choice(poem_ids) for _ in poem_ids]
        tp_a = sum(per_poem_a[p]["tp"] for p in sample)
        fp_a = sum(per_poem_a[p]["fp"] for p in sample)
        fn_a = sum(per_poem_a[p]["fn"] for p in sample)
        tp_b = sum(per_poem_b[p]["tp"] for p in sample)
        fp_b = sum(per_poem_b[p]["fp"] for p in sample)
        fn_b = sum(per_poem_b[p]["fn"] for p in sample)
        diffs.append(prf1(tp_a, fp_a, fn_a)["f1"] - prf1(tp_b, fp_b, fn_b)["f1"])
    diffs.sort()
    lo = diffs[int(0.025 * n_iter)]
    hi = diffs[int(0.975 * n_iter) - 1]
    return {"point": poem_f1(score_total(per_poem_a)) - poem_f1(score_total(per_poem_b)), "ci_95": [lo, hi]}


def score_total(per_poem: dict) -> dict:
    return {
        "tp": sum(c["tp"] for c in per_poem.values()),
        "fp": sum(c["fp"] for c in per_poem.values()),
        "fn": sum(c["fn"] for c in per_poem.values()),
    }


def analyze(out_dir=None, criteria=("strict", "token")):
    out_dir = Path(out_dir) if out_dir else RESULTS_DIR
    pool = json.loads(EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]

    report = {}
    for provider in ["google", "openai"]:
        report[provider] = {}
        for criterion in criteria:
            per_set = {s: score_set(out_dir, s, provider, pool, criterion) for s in SET_NAMES}
            pairwise = {}
            for i, s1 in enumerate(SET_NAMES):
                for s2 in SET_NAMES[i + 1:]:
                    pairwise[f"{s1}-{s2}"] = bootstrap_ci_pairwise(
                        per_set[s1]["per_poem"], per_set[s2]["per_poem"])
            report[provider][criterion] = {"per_set": per_set, "pairwise_bootstrap_ci": pairwise}
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    result = analyze(args.out_dir)
    print(json.dumps(
        {p: {c: {"overall": {s: result[p][c]["per_set"][s]["overall"] for s in SET_NAMES}}
             for c in result[p]} for p in result},
        ensure_ascii=False, indent=2))
