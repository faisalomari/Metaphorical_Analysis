"""Design-choice combination primitives for the GPT-Z + Claude-FS (+/- Gemini)
question. NO API calls. Builds on ensemble_v2.py's cache-based scorer
(build_parsed_cache keyed by (set_name, poem_id, verse_no, provider)) instead
of re-reading run_manifest.json/raw/*.txt per lookup.

New here (does not exist in ensemble_v2.py, which hardcodes all 3 voters on
the SAME set_name):
  - score_poem_two_voter: 2-voter OR/AND combination, each voter an
    independent (set_name, provider) pair -- lets "GPT on Z" and "Claude on
    set B" be combined even though they never ran under the same set_name.
  - score_poem_three_voter_majority: the same 2-of-3 majority rule
    ensemble_v2.score_poem_ensemble already uses, generalized to 3 arbitrary
    (set_name, provider) voters instead of 3 providers under one shared
    set_name (needed for "GPT-Z + Claude-FS + Gemini-FS" style designs).

Declared span-rule for the 2-voter case (stated up front, same discipline as
ensemble_v2.py's own declared limitation):
  - OR-exists verses: among whichever voter(s) said exists=True, each
    independently runs best_match() against the verse's GT spans. If AT
    LEAST ONE voter's match is non-null, that counts as 1 TP (remaining GT
    spans at that verse are FN) -- a union rule, consistent with "OR" being
    about either voter being enough to trigger a positive. If neither
    voter's "yes" match lands on a real span, it's 1 FP + FN per GT span.
  - AND-exists verses: both voters said exists=True (by definition of
    "combined" at the verse level); the span is counted a TP only if BOTH
    voters' match indices agree on the SAME GT span index -- an
    intersection rule, consistent with "AND" meaning both must agree.
  LIMITATION: the AND span rule inherits the same under-counting the
  ensemble's 3-voter rule has (two voters that each correctly spot a
  DIFFERENT real span in a multi-span verse do not get credit) -- stated
  here, not hidden, same as ensemble_v2.py's own §0 limitation note.
"""
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))  # experiments/phase4_e1_v2
from e1v2_config import PILOT_DIR  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from span_matching import best_match  # noqa: E402


def _exists(cache, voter, poem_id, verse_no):
    v = cache[(voter[0], poem_id, verse_no, voter[1])]["exists"]
    return bool(v) if v is not None else False


def _appearance(cache, voter, poem_id, verse_no):
    return cache[(voter[0], poem_id, verse_no, voter[1])]["appearance"] or ""


def score_poem_two_voter(cache, voter_a, voter_b, poem_id, n_verses, gt_spans, criterion, rule):
    """voter_a / voter_b: (set_name, provider). rule: 'or' or 'and'."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        a_yes = _exists(cache, voter_a, poem_id, verse_no)
        b_yes = _exists(cache, voter_b, poem_id, verse_no)
        combined = (a_yes or b_yes) if rule == "or" else (a_yes and b_yes)
        gt_texts = gt_spans[verse_no]
        if criterion == "verse":
            if combined and gt_texts:
                tp += 1
            elif combined and not gt_texts:
                fp += 1
            elif not combined and gt_texts:
                fn += 1
            continue
        if not combined:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        matches = []
        if a_yes:
            matches.append(best_match(_appearance(cache, voter_a, poem_id, verse_no), gt_texts, criterion))
        if b_yes:
            matches.append(best_match(_appearance(cache, voter_b, poem_id, verse_no), gt_texts, criterion))
        if rule == "or":
            found = [m for m in matches if m is not None]
            if found:
                tp += 1
                fn += len(gt_texts) - 1
            else:
                fp += 1
                fn += len(gt_texts)
        else:  # and -- both voters are exists=True here by construction (combined True)
            if len(matches) == 2 and matches[0] is not None and matches[0] == matches[1]:
                tp += 1
                fn += len(gt_texts) - 1
            else:
                fp += 1
                fn += len(gt_texts)
    return {"tp": tp, "fp": fp, "fn": fn}


def score_poem_three_voter_majority(cache, voter_specs, poem_id, n_verses, gt_spans, criterion):
    """voter_specs: list of 3 (set_name, provider) pairs. Same 2-of-3 /
    span-agreement-of->=2 rule as ensemble_v2.score_poem_ensemble, generalized
    to voters that need not share a set_name."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        parsed = [cache[(sn, poem_id, verse_no, pv)] for sn, pv in voter_specs]
        votes = sum(1 for p in parsed if p["exists"] is True)
        ensemble_exists = votes >= 2
        gt_texts = gt_spans[verse_no]
        if criterion == "verse":
            if ensemble_exists and gt_texts:
                tp += 1
            elif ensemble_exists and not gt_texts:
                fp += 1
            elif not ensemble_exists and gt_texts:
                fn += 1
            continue
        if not ensemble_exists:
            fn += len(gt_texts)
            continue
        if not gt_texts:
            fp += 1
            continue
        match_idxs = []
        for p in parsed:
            if p["exists"] is True:
                idx = best_match(p["appearance"] or "", gt_texts, criterion)
                if idx is not None:
                    match_idxs.append(idx)
        counts = Counter(match_idxs)
        _, freq = counts.most_common(1)[0] if counts else (None, 0)
        if freq >= 2:
            tp += 1
            fn += len(gt_texts) - 1
        else:
            fp += 1
            fn += len(gt_texts)
    return {"tp": tp, "fp": fp, "fn": fn}


def agreement_matrix(cache, pool, gt_cache, voter_a, voter_b):
    """Buckets: both / a_only / b_only / none, over every verse-unit in
    `pool`. accuracy = GT-positive rate for predicted-positive buckets
    (both/a_only/b_only, matching the OR-exists convention), 1-GT-positive
    rate for the predicted-negative bucket (none)."""
    buckets = {"both": {"n": 0, "gt_pos": 0}, "a_only": {"n": 0, "gt_pos": 0},
               "b_only": {"n": 0, "gt_pos": 0}, "none": {"n": 0, "gt_pos": 0}}
    for poem in pool:
        poem_id = poem["poem_id"]
        gt_spans = gt_cache[poem_id]["gt"]
        n_verses = gt_cache[poem_id]["n_verses"]
        for verse_no in range(1, n_verses + 1):
            a_yes = _exists(cache, voter_a, poem_id, verse_no)
            b_yes = _exists(cache, voter_b, poem_id, verse_no)
            bucket = "both" if (a_yes and b_yes) else "a_only" if a_yes else "b_only" if b_yes else "none"
            gt_pos = bool(gt_spans[verse_no])
            buckets[bucket]["n"] += 1
            if gt_pos:
                buckets[bucket]["gt_pos"] += 1
    out = {}
    for k, v in buckets.items():
        n, gt_pos = v["n"], v["gt_pos"]
        rate = (gt_pos / n) if n else None
        predicted_positive = k != "none"
        acc = None
        if n:
            acc = rate if predicted_positive else (1 - rate)
        out[k] = {"n": n, "gt_positive_rate": rate, "accuracy": acc}
    return out
