"""Span-level scoring for E1 v2 (strict + token-overlap, CLAUDE.md rule 4),
raw TP/FP/FN always (rule 3), pooled overall/abu_nuwas/other, per-poem, plus
a bootstrap 95% CI over poems for every pairwise (F1_set_i - F1_set_j)
across sets Z/A/B/C (CLAUDE.md rule 2's run-noise precedent).

Unlike phase3_subelements/score_subtypes.py (recall-only — every row fed to
that experiment was a known GT-positive, so FP/precision/F1 are undefined
there), this pilot asks the model about EVERY verse in the eval poems, so
precision/recall/F1 and raw TP/FP/FN are all well-defined here.

Scoring rule for one verse-unit, one (set, provider):
  - GT positive = subtype == "استعارة فعل" (exact match) at that verse (see
    gt_v2.gt_spans_for_subtype). A verse can have 0, 1, or more GT spans.
  - Model exists=False, or exists=True with no matching GT span -> contributes
    to FN for each unmatched GT span, and FP if the model said True with no
    GT at all or no match (same convention as phase4_e1 (v1) scoring.py
    score_poem, reused here, not reimplemented differently).
  - Match = span_matching.best_match(appearance, gt_spans, criterion),
    pilot_3models's own strict/token-overlap matcher (reused unchanged).
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_DIR, PILOT_DIR, RESULTS_DIR, SET_NAMES  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from parsing_v2 import parse_verse_response  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402
from span_matching import best_match  # noqa: E402


def load_verse_result(out_dir: Path, set_name: str, poem_id: str, verse_no: int, provider: str):
    """Reads one verse-unit cell from run_manifest.json + its raw-text file.
    Returns None if the cell isn't in the manifest or errored."""
    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    for r in manifest:
        if (r["set_name"], r["poem_id"], r["verse_no"], r["provider"]) == (set_name, poem_id, verse_no, provider):
            if r.get("error"):
                return None
            raw_text = (out_dir / r["raw_text_file"]).read_text(encoding="utf-8")
            return parse_verse_response(raw_text)
    return None


def score_poem(out_dir: Path, set_name: str, poem_id: str, provider: str, n_verses: int,
               gt_spans: dict, criterion: str) -> dict:
    """criterion: "strict"/"token" (span-level, CLAUDE.md rule 4's required primary metric) or
    "verse" (plain verse-level exists-vs-ground-truth, no span match at all -- CLAUDE.md rule 4
    explicitly warns this alone produces artifacts, so it is reported ONLY as a supplementary
    diagnostic alongside strict/token, never as a substitute for them)."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        parsed = load_verse_result(out_dir, set_name, poem_id, verse_no, provider)
        gt_texts = gt_spans[verse_no]
        if parsed is None or parsed["exists"] is None:
            continue  # no cell / parse error: excluded, not counted as FN or FP
        if criterion == "verse":
            if parsed["exists"] and gt_texts:
                tp += 1
            elif parsed["exists"] and not gt_texts:
                fp += 1
            elif not parsed["exists"] and gt_texts:
                fn += 1
            continue
        if not parsed["exists"]:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idx = best_match(parsed["appearance"] or "", gt_texts, criterion)
        if match_idx is None:
            fp += 1
            fn += len(gt_texts)
        else:
            tp += 1
            fn += len(gt_texts) - 1
    return {"tp": tp, "fp": fp, "fn": fn}


def score_set(out_dir: Path, set_name: str, provider: str, pool: list, criterion: str) -> dict:
    per_poem = {}
    for poem in pool:
        poem_id = poem["poem_id"]
        pj = load_poem_json(poem_id)
        gt_spans = gt_spans_for_subtype(pj)
        counts = score_poem(out_dir, set_name, poem_id, provider, pj["verse_count"], gt_spans, criterion)
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


def score_total(per_poem: dict) -> dict:
    return {
        "tp": sum(c["tp"] for c in per_poem.values()),
        "fp": sum(c["fp"] for c in per_poem.values()),
        "fn": sum(c["fn"] for c in per_poem.values()),
    }


def poem_f1(counts: dict) -> float:
    return prf1(counts["tp"], counts["fp"], counts["fn"])["f1"]


def bootstrap_ci_pairwise(per_poem_a: dict, per_poem_b: dict, n_iter: int = 2000, seed: int = 0) -> dict:
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
    point = poem_f1(score_total(per_poem_a)) - poem_f1(score_total(per_poem_b))
    return {"point": point, "ci_95": [lo, hi]}


def per_poem_diff_signs(per_poem_a: dict, per_poem_b: dict) -> dict:
    poem_ids = sorted(set(per_poem_a) & set(per_poem_b))
    a_gt = b_gt = tied = 0
    for p in poem_ids:
        fa, fb = poem_f1(per_poem_a[p]), poem_f1(per_poem_b[p])
        if fa > fb:
            a_gt += 1
        elif fb > fa:
            b_gt += 1
        else:
            tied += 1
    return {"a_greater": a_gt, "b_greater": b_gt, "tied": tied}


def analyze(out_dir=None, pool=None, criteria=("strict", "token"), models=("google", "openai")):
    out_dir = Path(out_dir) if out_dir else RESULTS_DIR
    report = {}
    for provider in models:
        report[provider] = {}
        for criterion in criteria:
            per_set = {s: score_set(out_dir, s, provider, pool, criterion) for s in SET_NAMES}
            pairwise = {}
            diffs = {}
            for i, s1 in enumerate(SET_NAMES):
                for s2 in SET_NAMES[i + 1:]:
                    pairwise[f"{s1}-{s2}"] = bootstrap_ci_pairwise(
                        per_set[s1]["per_poem"], per_set[s2]["per_poem"])
                    diffs[f"{s1}-{s2}"] = per_poem_diff_signs(per_set[s1]["per_poem"], per_set[s2]["per_poem"])
            report[provider][criterion] = {
                "per_set": per_set, "pairwise_bootstrap_ci": pairwise, "per_poem_diff_signs": diffs,
            }
    return report


if __name__ == "__main__":
    print("scoring_v2 module loaded OK (run unit_checks.py for a no-API local check).")
