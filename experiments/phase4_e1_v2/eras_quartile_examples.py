"""Part 2 (NO API calls): build the two QUARTILE few-shot example sets
Q1/Q2 -- each exactly 2 example verses from 2 DIFFERENT poets, target
استعارة فعل, same scaffold as A/B/C/D/D2/F5/F10/M1..H2
(multipoet_prompt_builder.build_system_message_n with N=2).

Reuses eras_examples.build_eligible_poets/draw_examples UNCHANGED (same
exclusion set: NO_TEXT_POEM_ID, ALREADY_USED_POEM_IDS, v1 EXAMPLE_POEM_IDS,
F5/F10 example poems, eval_pool_25.json's 25 poems) -- this module only
adds the quartile-specific slot assignment (P25 slot / P75 slot) on top
of that shared eligible-poet pool. See eras_quartile_config.py's module
docstring for the full user-decision trail (axis choice, reuse policy,
the P25-confidence-fallback deviation).

Slot assignment (declared, printed by main()):
  - P75 slot: H2's own two poets (ديك الجن, ابن الرومي -- eras_quartile_
    config.P75_REUSE_POOL_POET_NAMES), sorted by distance to the P75
    target, nearest first. This is the ONLY reuse of an existing set's
    poet anywhere in Q1/Q2, and it is reuse of H2 specifically (declared
    "Q shares its P75-slot poets with H2" -- any Q-vs-H comparison in the
    analysis step is confounded by this, flagged again there).
  - P25 slot: poets never used by ANY existing set (not M1/M2/E1/E2, not
    H1/H2), ranked by (confidence tier, distance) -- high/medium
    confidence preferred over low regardless of raw distance, ties
    broken by distance. Declared fallback: if fewer than 2 high/medium
    candidates exist (true for this corpus -- only 1, جميل بن معمر), the
    pool widens to also include "low" confidence as a second priority
    tier (QUARTILE_P25_CONFIDENCE_FALLBACK), never silently.
  - Pairing: Q1 = (nearest P25 candidate, nearest P75 candidate), Q2 =
    (2nd-nearest P25 candidate, 2nd-nearest P75 candidate) -- each Q-set
    gets one P25-slot poet + one P75-slot poet, matching every other
    eras set's "2 examples from 2 different poets" shape.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eras_config import ERAS_AXIS_PATH, ERAS_EXAMPLE_SEED  # noqa: E402
from eras_examples import build_eligible_poets, draw_examples  # noqa: E402
from eras_quartile_config import (  # noqa: E402
    H1_H2_POET_NAMES, NEVER_REUSE_POET_NAMES, P75_REUSE_POOL_POET_NAMES,
    QUARTILE_CONFIDENCE_LEVELS, QUARTILE_P25_CONFIDENCE_FALLBACK, QUARTILE_SET_NAMES,
    compute_targets,
)

CONFIG_DIR = Path(__file__).resolve().parent / "config"
QUARTILE_EXAMPLE_SETS_PATH = CONFIG_DIR / "quartile_example_sets.json"
QUARTILE_TARGETS_PATH = CONFIG_DIR / "quartile_targets.json"


def _dated_candidates(eligible_poets: dict, axis: dict) -> list:
    """[(poet_id, poet_name, death_year_ce, confidence, n_candidate_verses), ...]
    for every poet in eligible_poets (ANY confidence) that has a death
    year -- same shape eras_examples._selection_eligible_dated_poets uses,
    but NOT pre-filtered to high/medium here (the P25-fallback tier needs
    "low" too; filtering happens in pick_p25_candidates/pick_p75_candidates
    below, not here)."""
    per_poet_by_id = {p["poet_id"]: p for p in axis["per_poet"]}
    out = []
    for name, info in eligible_poets.items():
        pid = info["poet_id"]
        p = per_poet_by_id.get(pid)
        if not p or p["death_year_ce"] is None:
            continue
        out.append((pid, name, p["death_year_ce"], (p["confidence"] or "").lower(), len(info["verses"])))
    return out


def pick_p75_candidates(dated: list, target: float) -> list:
    """H2's own two poets, nearest-to-target first. Declared reuse --
    see module docstring."""
    pool = [c for c in dated if c[1] in P75_REUSE_POOL_POET_NAMES]
    pool.sort(key=lambda c: abs(c[2] - target))
    assert len(pool) == len(P75_REUSE_POOL_POET_NAMES), (
        f"expected {P75_REUSE_POOL_POET_NAMES} in the eligible pool, got {[c[1] for c in pool]}"
    )
    return pool


def pick_p25_candidates(dated: list, target: float, other_target: float, n: int = 2) -> list:
    """Poets never used by M1/M2/E1/E2 or H1/H2, ranked by
    (confidence tier, distance) -- high/medium preferred over low
    regardless of raw distance, ties broken by distance. See module
    docstring for the declared fallback-to-low-confidence deviation.
    A candidate must be strictly closer to `target` (P25) than to
    `other_target` (P75) to even enter the pool -- without this, a
    medium-confidence poet who actually belongs near the OTHER quartile
    (e.g. محمد بن هاشم الخالدي, 996 CE, 347y from P25 but only 151y from
    P75) would wrongly outrank a much closer low-confidence P25 poet
    purely on confidence tier; this filter was added after catching
    exactly that bug in this script's first run (see SESSION_LOG.md)."""
    unused = [c for c in dated if c[1] not in NEVER_REUSE_POET_NAMES and c[1] not in H1_H2_POET_NAMES]
    near = [c for c in unused if abs(c[2] - target) <= abs(c[2] - other_target)]
    tier1 = [c for c in near if c[3] in QUARTILE_CONFIDENCE_LEVELS]
    tier2 = [c for c in near if c[3] in QUARTILE_P25_CONFIDENCE_FALLBACK]
    tier1.sort(key=lambda c: abs(c[2] - target))
    tier2.sort(key=lambda c: abs(c[2] - target))
    ranked = tier1 + tier2
    assert len(ranked) >= n, f"P25 slot: need {n} candidates, only {len(ranked)} available: {ranked}"
    return ranked[:n]


def build_quartile_sets() -> tuple:
    filter_counts = {}
    from collections import defaultdict
    filter_counts = defaultdict(int)
    eligible_poets = build_eligible_poets(filter_counts)
    axis = json.loads(ERAS_AXIS_PATH.read_text(encoding="utf-8"))
    targets = compute_targets()

    dated = _dated_candidates(eligible_poets, axis)
    p75_cands = pick_p75_candidates(dated, targets["p75_target"])
    p25_cands = pick_p25_candidates(dated, targets["p25_target"], targets["p75_target"])

    groups = {
        "Q1": [p25_cands[0][0], p75_cands[0][0]],
        "Q2": [p25_cands[1][0], p75_cands[1][0]],
    }
    slot_detail = {
        "Q1": {"p25": {"poet_id": p25_cands[0][0], "poet_name": p25_cands[0][1],
                        "death_year_ce": p25_cands[0][2], "confidence": p25_cands[0][3],
                        "distance_to_target": abs(p25_cands[0][2] - targets["p25_target"])},
               "p75": {"poet_id": p75_cands[0][0], "poet_name": p75_cands[0][1],
                        "death_year_ce": p75_cands[0][2], "confidence": p75_cands[0][3],
                        "distance_to_target": abs(p75_cands[0][2] - targets["p75_target"]),
                        "reused_from": "H2"}},
        "Q2": {"p25": {"poet_id": p25_cands[1][0], "poet_name": p25_cands[1][1],
                        "death_year_ce": p25_cands[1][2], "confidence": p25_cands[1][3],
                        "distance_to_target": abs(p25_cands[1][2] - targets["p25_target"])},
               "p75": {"poet_id": p75_cands[1][0], "poet_name": p75_cands[1][1],
                        "death_year_ce": p75_cands[1][2], "confidence": p75_cands[1][3],
                        "distance_to_target": abs(p75_cands[1][2] - targets["p75_target"]),
                        "reused_from": "H2"}},
    }

    assert groups["Q1"][0] != groups["Q1"][1] and groups["Q2"][0] != groups["Q2"][1]
    assert set(groups["Q1"]).isdisjoint(set(groups["Q2"])), "Q1 and Q2 must use different poets from each other"

    flat_order = groups["Q1"] + groups["Q2"]
    random.seed(ERAS_EXAMPLE_SEED)  # separate call, own RNG stream -- see module docstring
    drawn_by_id = draw_examples(eligible_poets, flat_order)

    sets = {g: [drawn_by_id[pid] for pid in groups[g]] for g in groups}
    return sets, groups, slot_detail, targets, dict(filter_counts), eligible_poets


def main():
    sets, groups, slot_detail, targets, filter_counts, eligible_poets = build_quartile_sets()

    print("=" * 78)
    print("Target points")
    print("=" * 78)
    print(f"Range axis (REJECTED per the >100y STOP, kept for reference): "
          f"P25={targets['range_axis']['p25']:.2f}  P75={targets['range_axis']['p75']:.2f}")
    print(f"Verse-weighted-quantile axis (CHOSEN): "
          f"P25={targets['verse_weighted_quantile_axis']['p25']:.2f}  "
          f"P75={targets['verse_weighted_quantile_axis']['p75']:.2f}")

    for g in QUARTILE_SET_NAMES:
        print(f"\n{'=' * 78}\nSET {g}\n{'=' * 78}")
        for slot in ("p25", "p75"):
            d = slot_detail[g][slot]
            reuse_note = f" [REUSED from {d['reused_from']}]" if "reused_from" in d else ""
            print(f"  {slot.upper()} slot: {d['poet_name']} (poet_id={d['poet_id']}, "
                  f"death={d['death_year_ce']}, confidence={d['confidence']}, "
                  f"distance={d['distance_to_target']:.2f}){reuse_note}")
        for e in sets[g]:
            print(f"    drawn: poem {e['poem_id']} ({e['poem_name']}) v{e['verse_no']}: {e['text']}")
            for a in e["annotations"]:
                print(f"      span={a['span']!r}  analysis={a['analysis']!r}")

    used = set(groups["Q1"]) | set(groups["Q2"])
    print(f"\nOK: {len(used)} distinct poets across Q1+Q2 (expected 4).")
    assert len(used) == 4

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    QUARTILE_EXAMPLE_SETS_PATH.write_text(
        json.dumps({"seed": 42, "sets": sets, "slot_detail": slot_detail}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\nWrote {QUARTILE_EXAMPLE_SETS_PATH}")
    QUARTILE_TARGETS_PATH.write_text(json.dumps(targets, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {QUARTILE_TARGETS_PATH}")


if __name__ == "__main__":
    main()
