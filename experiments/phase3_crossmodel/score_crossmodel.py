"""Span-level re-scoring for the Phase 3 subtype-recall data, shared across
every model (Gemini's existing phase3_subelements data, re-scored with no new
API calls; plus any new model run by run_crossmodel.py, same record schema).

WHY this exists instead of reusing phase3_subelements/score_subtypes.py as-is:
that script's recall is VERSE-LEVEL (exists=True/False only) - exactly the
scoring artifact CLAUDE.md's standing discipline (#4) warns about ("never
plain verse-level exists/not-exists"). Every row here is a single verse (or
small verse-block) that is a KNOWN ground-truth positive for its own subtype,
so "exists=True" alone does not prove the model found the right thing - it
could say yes for an unrelated reason. This module additionally checks the
model's "appearance" span against the ground truth's own annotated span
(the row's "span" field) using Phase 1's span_matching.best_match (strict
substring + token-overlap>=0.5), exactly as CLAUDE.md requires. A row only
counts as a true positive if BOTH (a) exists=True by 2-run majority AND
(b) appearance span-matches the ground-truth span under the given criterion.

WHAT THIS DOES NOT FIX: precision/F1 remain undefined by this experiment's
design (positive-only sampling, no negative examples were ever shown to any
model, for any subtype, by any run) - see MEETING_SUMMARY.md S4 and
phase3_subelements/score_subtypes.py's docstring. This module reports
TP/FN/Recall only, under two criteria (strict, token), plus the original
naive (verse-level, no span check) recall for direct before/after comparison.
Never computes or guesses precision/F1 - they are reported as not available.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crossmodel_config import PILOT_DIR  # noqa: E402

sys.path.insert(0, str(PILOT_DIR))
from span_matching import best_match  # noqa: E402

MIN_RELIABLE_N = 10  # below this, project precedent (MEETING_SUMMARY S2: "7
# subtypes with only 1 occurrence, too thin, excluded") treats a subtype's
# rate as unreliable; n<10 here is flagged, not excluded (unlike the original
# n=1 exclusion), since recall at n=2-9 is still informative directionally.


def majority(votes):
    """Matches analyze.py per_verse_majority / score_subtypes.py majority()
    exactly: with N_RUNS=2, a 1-1 split counts as False, not a coin flip."""
    votes = [v for v in votes if v is not None]
    if not votes:
        return None
    return sum(votes) > len(votes) / 2


def load_rows_for_subtype(raw_dir: Path, slug: str, splits=("all",)):
    """Merges every requested split's jsonl for one subtype into
    {(poem_key, row_id): {"runs": {run_idx: (exists, appearance)}, "span": gt_span}}.

    Keyed by (poem_key, row_id) - the ground truth's '#' column restarts at 1
    per poem, so row_id alone would silently collapse rows across poems
    (same bug class already documented in phase3_subelements/score_subtypes.py).

    Default splits=("all",) only: for every Gemini subtype, "<slug>_all.jsonl"
    is the final, reasoning-enabled, authoritative re-run (verified against
    final_summary.xlsx's n per subtype - matches exactly). "<slug>_dev.jsonl"
    / "<slug>_test.jsonl" are the STALE first-pass data (no reasoning field,
    superseded - see MEETING_SUMMARY.md S7 "first pass" vs "final re-run").
    Do not merge them in; that would risk stale data for subtypes where "all"
    and "dev"/"test" disagree. New crossmodel runs (run_crossmodel.py) only
    ever write "<slug>_all.jsonl" in the first place, so this is also the
    right default for those.
    """
    by_row = {}
    for split in splits:
        path = raw_dir / f"{slug}_{split}.jsonl"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                key = (rec["poem_key"], rec["row_id"])
                entry = by_row.setdefault(key, {"runs": {}, "span": rec.get("span")})
                entry["runs"][rec["run_idx"]] = (rec.get("exists"), rec.get("appearance"))
    return by_row


def score_subtype(by_row: dict) -> dict:
    """Returns counts for: naive (exists-only) recall, strict span-match
    recall, token span-match recall - plus parse-error and provider-error-like
    (no runs at all) exclusions."""
    tp_naive = fn_naive = 0
    tp_strict = fn_strict = 0
    tp_token = fn_token = 0
    excluded_no_vote = 0  # both runs unparseable/missing - can't vote at all

    for (poem_key, row_id), entry in by_row.items():
        runs = entry["runs"]
        votes = [runs.get(0, (None, None))[0], runs.get(1, (None, None))[0]]
        m = majority(votes)
        if m is None:
            excluded_no_vote += 1
            continue

        if not m:
            fn_naive += 1
            fn_strict += 1
            fn_token += 1
            continue

        tp_naive += 1
        # pick the appearance from a run whose vote matches the majority
        # (True), same convention as span_scoring.majority_exists_and_appearance
        appearance = None
        for run_idx in (0, 1):
            v = runs.get(run_idx)
            if v is not None and v[0] is True:
                appearance = v[1]
                break
        gt_span = entry["span"]
        gt_texts = [gt_span] if gt_span else []

        if best_match(appearance or "", gt_texts, "strict") is not None:
            tp_strict += 1
        else:
            fn_strict += 1  # said yes, but span doesn't match ground truth - conservative, not counted as a real find

        if best_match(appearance or "", gt_texts, "token", threshold=0.5) is not None:
            tp_token += 1
        else:
            fn_token += 1

    n = tp_naive + fn_naive
    return {
        "n": n,
        "tp_naive": tp_naive, "fn_naive": fn_naive,
        "recall_naive": round(tp_naive / n, 3) if n else None,
        "tp_strict": tp_strict, "fn_strict": fn_strict,
        "recall_strict": round(tp_strict / n, 3) if n else None,
        "tp_token": tp_token, "fn_token": fn_token,
        "recall_token": round(tp_token / n, 3) if n else None,
        "excluded_parse_errors": excluded_no_vote,
        "thin": n < MIN_RELIABLE_N,
    }


def score_all_subtypes(raw_dir: Path, subtype_defs: dict, splits=("all",)):
    import re

    def slugify(name: str) -> str:
        s = re.sub(r'[\\/:*?"<>|]', "", name)
        return s.replace(" ", "_")

    results = {}
    for subtype_key in subtype_defs:
        slug = slugify(subtype_key)
        by_row = load_rows_for_subtype(raw_dir, slug, splits)
        if not by_row:
            continue
        results[subtype_key] = score_subtype(by_row)
    return results


if __name__ == "__main__":
    from crossmodel_config import PHASE3_RAW_DIR
    from subtype_defs import SUBTYPE_DEFS

    results = score_all_subtypes(PHASE3_RAW_DIR, SUBTYPE_DEFS)
    print(f"{'subtype':40s} {'n':>4s} {'naive':>7s} {'strict':>7s} {'token':>7s}")
    for k, r in sorted(results.items(), key=lambda kv: -kv[1]["n"]):
        print(f"{k:40s} {r['n']:4d} {r['recall_naive'] or 0:7.3f} {r['recall_strict'] or 0:7.3f} {r['recall_token'] or 0:7.3f}")
