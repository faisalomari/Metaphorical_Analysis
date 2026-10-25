"""Constants + target-point computation for the supervisor-requested
QUARTILE few-shot experiment (Q1/Q2) on top of E1 v2's existing
Z/A/B/C(/D/D2), F5/F10 (multipoet), and M1/M2/E1/E2/H1/H2 (eras) sets.

Does not edit eras_config.py, eras_examples.py, phase4_e1 (v1),
phase3_subelements, pilot_3models, or any existing E1 v2 file --
additive only, same convention every prior set family (D/D2, F5/F10,
eras) already used.

Design (user's words, see docs/phase4/SESSION_LOG.md's 2026-10-25 "Quartile
few-shot task" entries for the full decision trail): "timeline from 0 to
1000; take one poem from 250 and one from 750" -- i.e. each new set = one
example near the death-year axis's 25th percentile (P25) + one near its
75th percentile (P75), named Q1 and Q2 (different poets from each other).
H1/H2 ("middle of each half") stay exactly as they are and are NOT the
requested quartile design -- see GLOSSARY-style note in
docs/phase4/E1_V2_ERAS_FEWSHOT.md once it is updated.

**STOP-condition finding, declared** (SESSION_LOG.md 2026-10-25): the
range-axis definition (min + 0.25/0.75*(max-min) = 730.75 / 1104.25 CE)
put the nearest eligible poet to P75 at 108.25 years away, over the
task's 100-year guard. Per explicit user instruction, this was presented
to the user (not chosen silently) as two options: (a) range-axis points
with the nearest available poets, (b) the verse-weighted-quantile
alternative. **User chose (b)**: P25/P75 of verse-weighted death years
(the same weighting convention ERAS_ANALYTICS.md's PRIMARY median uses),
giving P25=649.0, P75=845.0 CE -- much closer available poets for the
P75 slot in particular.

**User's additional declared decisions** (SESSION_LOG.md, same entry):
  - Reuse of H1/H2 poets is allowed for the P75 SLOT ONLY (not P25),
    declared and printed wherever it happens. M1/M2/E1/E2 poets are
    NEVER reused for Q1/Q2, no exception.
  - Q1 and Q2 must use 2 distinct poets each, no poet shared between
    Q1 and Q2 (same "different poets from each other" rule every prior
    pair of sets -- M1/M2, E1/E2, H1/H2 -- already followed).
  - P75 slot: prefer H2's own two poets split across Q1/Q2 (ديك الجن,
    ابن الرومي -- H2's pair, nearest-to-P75 available poets of any kind
    once the pure range-axis option was rejected), one per Q-set.
  - P25 slot: prefer poets NEVER used by any existing set. Only ONE such
    poet exists at the standing SELECTION_CONFIDENCE_LEVELS (high/medium)
    restriction near P25 (جميل بن معمر, see eras_quartile_examples.py) --
    a second, declared DEVIATION for this slot only: confidence is
    widened to also accept "low" (QUARTILE_P25_CONFIDENCE_LEVELS below),
    the same kind of declared, printed deviation eras_examples.py already
    used once (its rank-based band fix) rather than a silent widening.

Target-point computation re-derives both axis definitions directly from
config/eras_axis.json's persisted per-poet death-year/verse-count table
(the same source eras_analytics.py / ERAS_ANALYTICS.md already built) --
nothing here re-runs eras_analytics.py or touches its output file.
"""
import math
import statistics
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eras_config import ERAS_AXIS_PATH  # noqa: E402

QUARTILE_SET_NAMES = ["Q1", "Q2"]

QUARTILE_LOW_PCT, QUARTILE_HIGH_PCT = 0.25, 0.75

# User's decision: verse-weighted-quantile axis (option "b"), not the plain
# range axis (option "a") -- see module docstring.
QUARTILE_AXIS_CHOICE = "verse_weighted_quantile"

# P75-slot reuse pool: H2's own two poets (the nearest-to-P75 poets of any
# kind once the plain range axis was rejected). P25 never reuses H1/H2 or
# M1/M2/E1/E2.
P75_REUSE_POOL_POET_NAMES = ["ديك الجن", "ابن الرومي"]

# Never-reuse set for BOTH slots: every poet already used by M1/M2/E1/E2.
NEVER_REUSE_POET_NAMES = {
    "الكميت بن زيد الأسدي", "أبو دلامة", "أبو نواس", "أبو تمّام",
    "طرفة بن العبد ", "الصنوبري", "قطري بن الفجاءة المازني", "أبو فراس الحمداني",
}

# H1/H2 poets as a group (for the P25 slot, which must NOT reuse any of
# them -- only the P75 slot may, and only from P75_REUSE_POOL_POET_NAMES).
H1_H2_POET_NAMES = {"الفرزدق", "جرير بن عطيّة", "ديك الجن", "ابن الرومي"}

# Standing eligibility confidence levels (same as eras_config.SELECTION_
# CONFIDENCE_LEVELS) for the P75 slot and as the FIRST-PRIORITY tier for
# the P25 slot.
QUARTILE_CONFIDENCE_LEVELS = {"high", "medium"}

# Declared deviation (see module docstring): the P25 slot widens to also
# accept "low" confidence, but ONLY as a second-priority tier -- a
# high/medium candidate, if one exists, is always preferred over a low
# one, regardless of raw distance.
QUARTILE_P25_CONFIDENCE_FALLBACK = {"low"}


def _weighted_percentile(pairs: list, q: float) -> float:
    """Same expand-and-index method as eras_analytics._weighted_median,
    generalized to an arbitrary quantile q via linear interpolation
    (matches statistics.median's behavior at q=0.5 on an even-length
    list). pairs: [(value, integer weight), ...]."""
    expanded = []
    for value, weight in pairs:
        expanded.extend([value] * int(weight))
    expanded.sort()
    n = len(expanded)
    if n == 1:
        return float(expanded[0])
    idx = q * (n - 1)
    lo, hi = math.floor(idx), math.ceil(idx)
    if lo == hi:
        return float(expanded[int(idx)])
    frac = idx - lo
    return expanded[lo] + (expanded[hi] - expanded[lo]) * frac


def compute_targets() -> dict:
    """Re-derives both axis definitions from config/eras_axis.json's
    persisted per-poet table (dated poets only, same population
    ERAS_ANALYTICS.md's median/midpoint use). Returns both so the report
    can show the rejected option (a) alongside the chosen option (b)."""
    import json
    axis = json.loads(ERAS_AXIS_PATH.read_text(encoding="utf-8"))
    min_year, max_year = axis["min_year"], axis["max_year"]
    rng = max_year - min_year

    p25_range = min_year + QUARTILE_LOW_PCT * rng
    p75_range = min_year + QUARTILE_HIGH_PCT * rng

    dated = [p for p in axis["per_poet"] if p["death_year_ce"] is not None]
    pairs = [(p["death_year_ce"], max(p["n_verses"], 1)) for p in dated]
    p25_vw = _weighted_percentile(pairs, QUARTILE_LOW_PCT)
    p75_vw = _weighted_percentile(pairs, QUARTILE_HIGH_PCT)

    # Sanity check: q=0.5 on this same multiset must reproduce the
    # already-frozen primary median (784.0) -- confirms this module's
    # independent re-implementation agrees with eras_analytics.py's.
    median_check = _weighted_percentile(pairs, 0.5)
    assert abs(median_check - axis["median_by_verses"]) < 1e-9, (
        f"weighted-percentile re-derivation disagrees with eras_axis.json's "
        f"persisted median_by_verses ({median_check} vs {axis['median_by_verses']})"
    )

    return {
        "min_year": min_year, "max_year": max_year,
        "range_axis": {"p25": p25_range, "p75": p75_range},
        "verse_weighted_quantile_axis": {"p25": p25_vw, "p75": p75_vw},
        "chosen_axis": QUARTILE_AXIS_CHOICE,
        "p25_target": p25_vw if QUARTILE_AXIS_CHOICE == "verse_weighted_quantile" else p25_range,
        "p75_target": p75_vw if QUARTILE_AXIS_CHOICE == "verse_weighted_quantile" else p75_range,
    }
