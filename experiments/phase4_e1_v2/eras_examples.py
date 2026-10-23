"""Part 2 (NO API calls): build the six poet-era few-shot example sets
M1/M2/E1/E2/H1/H2 -- each exactly 2 example verses from 2 DIFFERENT poets,
target استعارة فعل, same scaffold as A/B/C/D/D2/F5/F10
(multipoet_prompt_builder.build_system_message_n with N=2).

Depends on eras_analytics.build_axis_stats()'s persisted
config/eras_axis.json (poet death-year bands) and eras_config.py's
note-quality filter + poem/poet exclusions. See eras_config.py's module
docstring for the full band-definition writeup and this module's
docstring below for the group-by-group selection procedure.

Eligibility rule (declared before any selection is made, seed=42):
  A poem is a candidate example SOURCE iff it is not NO_TEXT_POEM_ID,
  not one of the 5 Phase-1-frozen ALREADY_USED_POEM_IDS, not one of the
  3 Abu-Nuwas-only v1 EXAMPLE_POEM_IDS, not one of the 10 F5/F10 example
  poems (F5_F10_EXAMPLE_POEM_IDS), and not one of eval_pool_25.json's 25
  poems (the pool M1..H2 are themselves evaluated on -- eval_pool_25.json
  stays unchanged).
  A VERSE is eligible iff it carries >=1 annotation with subtype ==
  "استعارة فعل" (exact match) whose "analysis" note passes
  eras_config.note_quality() (a genuine metaphor analysis, not a
  question-marked guess or a bare lexical gloss).
  A poet is eligible iff: (a) they are not "القرآن الكريم" (not an
  individual poet); (b) >=1 of their candidate poems has >=1 eligible
  verse; (c) their poet_dates.csv confidence is high/medium (reliable
  date, eras_config.SELECTION_CONFIDENCE_LEVELS).

Band computation -- IMPORTANT DEVIATION, declared here and in
SESSION_LOG.md: Part 1's ERAS_ANALYTICS.md bands (eras_analytics.py,
config/eras_axis.json) are computed over the FULL 36-poet dated corpus
axis, as specified, to describe the corpus. But the population actually
AVAILABLE to supply an example verse here is much smaller (confidence
high/medium AND a surviving candidate verse after the standard
phase4_e1_v2 exclusions and the note_quality filter) -- only 14 poets, as
it turns out, and several of Part 1's full-axis extreme-dated poets
(النابغة الذبياني، الأعشى ميمون، امرؤ القيس, among others) have ZERO
usable candidate verses in this corpus (their استعارة فعل annotations
carry empty analysis notes), so Part 1's year-threshold bands, applied
naively to this 14-poet pool, leave some roles (notably earliest_extreme
and h1_pool) competing for the SAME 2-3 poets and the greedy group-by-
group draw provably fails (verified by running it: ValueError, pool
exhausted). Fix: Part 2 computes its own bands by RANK within the
14-poet selection-eligible population (sorted by death_year_ce), which
partitions it into disjoint, non-competing candidate pools by
construction:
  - N = len(selection-eligible population) (14 in this run).
  - k_extreme = max(2, ceil(EXTREME_PCT * N)) -- same EXTREME_PCT (0.15)
    as Part 1's "15%" rule, now applied by rank over this smaller
    population. earliest_extreme = the first k_extreme poets (ranks);
    latest_extreme = the last k_extreme.
  - middle_band = SELECTION_MIDDLE_N (4, exactly enough for M1+M2's 2+2)
    poets whose RANK is closest to the population's center rank,
    ties broken toward the earlier (smaller-year) poet -- excludes any
    poet already claimed by earliest_extreme/latest_extreme.
  - first_half = ranks below the center; second_half = ranks at/above
    the center (an even rank split -- equivalent to a median split).
  - h1_pool = first_half MINUS (earliest_extreme union middle_band) --
    "the middle of the first half" once the extreme and overall-middle
    roles have already claimed their share.
  - h2_pool = second_half MINUS (latest_extreme union middle_band).
  For this run's 14-poet population these 5 pools come out pairwise
  disjoint (0 overlap), so no fallback/widening was needed beyond this
  rank-based redefinition itself -- verified programmatically in main().

Group-by-group selection (fixed processing order M1, M2, E1, E2, H1, H2;
a GLOBAL used-poet set carries across all six groups, so all 12 poet
slots end up distinct -- "no poet repeated across the six groups"):
  - M1, M2: candidates = middle_band (poet_id ascending for determinism
    among ties; here, rank order). M1 takes the first 2 not yet used,
    M2 the next 2.
  - E1, E2: candidates = earliest_extreme and latest_extreme separately
    (rank order). E1 = (first unused earliest, first unused latest),
    E2 = (next unused earliest, next unused latest).
  - H1: candidates = h1_pool, rank order; H1 takes the first 2 unused.
  - H2: candidates = h2_pool, rank order; H2 takes the first 2 unused.
  Each poet contributes exactly 1 verse to the set they're drawn into:
  one random.seed(ERAS_EXAMPLE_SEED) call (separate from every other
  module's RNG stream), then one random.sample(eligible_verses, 1) per
  poet IN THE GLOBAL SELECTION ORDER above (sequential consumption,
  matching multipoet_examples.py's own convention) -- so a group's draw
  never depends on what is drawn after it.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, E1V1_DIR, EVAL_POOL_25_PATH, EXAMPLE_POEM_IDS, NO_TEXT_POEM_ID, SUBTYPE_FOCUS,
)
from eras_config import (  # noqa: E402
    ERAS_AXIS_PATH, ERAS_EXAMPLE_SEED, ERAS_EXAMPLE_SETS_PATH, ERAS_NOTE_FILTER_REPORT_PATH,
    EXTREME_PCT, F5_F10_EXAMPLE_POEM_IDS, QURAN_POET_NAME, SELECTION_CONFIDENCE_LEVELS, SELECTION_MIDDLE_N,
    note_quality,
)

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_manifest, load_poem_json  # noqa: E402


def _verse_no(verse_index_field) -> int:
    return int(str(verse_index_field).split(",")[0])


def _excluded_poem_ids() -> set:
    pool25 = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool25_ids = {p["poem_id"] for p in pool25["poems"]}
    return ({NO_TEXT_POEM_ID} | set(ALREADY_USED_POEM_IDS) | set(EXAMPLE_POEM_IDS)
            | set(F5_F10_EXAMPLE_POEM_IDS) | pool25_ids)


def find_eligible_verses_for_poem(poem_json: dict, filter_counts: dict) -> dict:
    """{verse_no: [{"span", "analysis"}, ...]} -- only annotations whose
    note passes note_quality(); filter_counts accumulates reason tallies
    across the whole corpus scan (for the printed filter report)."""
    n_verses = poem_json["verse_count"]
    out = defaultdict(list)
    for a in poem_json["annotations"]:
        if a.get("subtype") != SUBTYPE_FOCUS:
            continue
        note = (a.get("analysis") or "").strip()
        if not note:
            filter_counts["empty_note"] += 1
            continue
        ok, reason = note_quality(note)
        filter_counts["kept:" + reason if ok else reason] += 1
        if not ok:
            continue
        vn = _verse_no(a["verse_index"])
        if not (1 <= vn <= n_verses):
            continue
        out[vn].append({"span": (a.get("span_text") or "").strip(), "analysis": note})
    return dict(out)


def build_eligible_poets(filter_counts: dict) -> dict:
    """{poet_name: {"poet_id", "period", "verses": [(poem_id, poem_name,
    verse_no, verse_text, annots), ...]}} -- same shape as
    multipoet_examples.build_eligible_poets, but with the eras-specific
    exclusion set (F5/F10 + eval_pool_25, on top of the standard
    NO_TEXT/ALREADY_USED/EXAMPLE_POEM_IDS) and the note_quality filter
    applied to every candidate annotation."""
    excluded = _excluded_poem_ids()
    rows = load_manifest()
    poets = defaultdict(lambda: {"period": None, "poet_id": None, "verses": []})
    for r in rows:
        poem_id = r["poem_id"]
        poet_name = r["poet_name"]
        if poet_name == QURAN_POET_NAME:
            continue
        if poem_id in excluded:
            continue
        try:
            pj = load_poem_json(poem_id)
        except FileNotFoundError:
            continue
        elig = find_eligible_verses_for_poem(pj, filter_counts)
        if not elig:
            continue
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for vn, annots in elig.items():
            poets[poet_name]["verses"].append((poem_id, pj["poem_name"], vn, verses_by_no[vn], annots))
        poets[poet_name]["period"] = r["period"] or ""
        poets[poet_name]["poet_id"] = r["poet_id"]
    return dict(poets)


def _confidence_ok(poet_id: str, per_poet_by_id: dict) -> bool:
    p = per_poet_by_id.get(poet_id)
    return bool(p and p["has_reliable_date"] and (p["confidence"] or "").lower() in SELECTION_CONFIDENCE_LEVELS)


def _selection_eligible_dated_poets(eligible_poets: dict, axis: dict) -> list:
    """[(poet_id, death_year_ce, poet_name), ...] sorted ascending by
    death_year_ce -- the population actually available to draw an example
    FROM: dated, confidence high/medium (eras_config.SELECTION_CONFIDENCE_
    LEVELS), and has >=1 genuine candidate verse after exclusions."""
    per_poet_by_id = {p["poet_id"]: p for p in axis["per_poet"]}
    name_to_id = {name: info["poet_id"] for name, info in eligible_poets.items()}
    eligible_ids = {pid for pid in name_to_id.values() if _confidence_ok(pid, per_poet_by_id)}
    out = [(pid, per_poet_by_id[pid]["death_year_ce"], per_poet_by_id[pid]["poet_name"])
           for pid in eligible_ids
           if per_poet_by_id.get(pid) and per_poet_by_id[pid]["death_year_ce"] is not None]
    out.sort(key=lambda t: (t[1], int(t[0])))
    return out


def build_group_pools(eligible_poets: dict, axis: dict) -> dict:
    """Returns {group_label: [poet_id, ...]} (rank order; duplicates never
    occur within one band) for the 5 underlying, pairwise-disjoint-by-
    construction pools this module draws from: middle_band,
    earliest_extreme, latest_extreme, h1_pool (first-half-middle),
    h2_pool (second-half-middle). See module docstring's "Band
    computation" section for the full rank-based rationale."""
    import math
    dated = _selection_eligible_dated_poets(eligible_poets, axis)
    n = len(dated)
    ids_by_rank = [pid for pid, _year, _name in dated]

    k_extreme = max(2, math.ceil(n * EXTREME_PCT)) if n else 0
    earliest_idx = set(range(0, k_extreme))
    latest_idx = set(range(n - k_extreme, n))

    center = (n - 1) / 2.0
    remaining_idx = [i for i in range(n) if i not in earliest_idx and i not in latest_idx]
    remaining_idx.sort(key=lambda i: (abs(i - center), i))
    middle_idx = set(remaining_idx[:SELECTION_MIDDLE_N])

    half_cut = n // 2  # ranks < half_cut = first half; >= half_cut = second half
    first_half_idx = set(range(0, half_cut))
    second_half_idx = set(range(half_cut, n))
    h1_idx = first_half_idx - earliest_idx - middle_idx
    h2_idx = second_half_idx - latest_idx - middle_idx

    def by_idx(idx_set):
        return [ids_by_rank[i] for i in sorted(idx_set)]

    pools = {
        "middle_band": by_idx(middle_idx), "earliest_extreme": by_idx(earliest_idx),
        "latest_extreme": by_idx(latest_idx), "h1_pool": by_idx(h1_idx), "h2_pool": by_idx(h2_idx),
    }
    all_listed = [pid for pool in pools.values() for pid in pool]
    assert len(set(all_listed)) == len(all_listed), (
        f"rank-based pools are not pairwise disjoint: {pools}"
    )
    return pools


def select_group_poets(pools: dict) -> dict:
    """Fixed processing order M1,M2,E1,E2,H1,H2; a global used-poet set
    carries across groups so all 12 slots end up distinct poet_ids.
    Returns {group_name: [poet_id, poet_id]}."""
    used = set()

    def take(pool, n):
        chosen = [pid for pid in pool if pid not in used][:n]
        if len(chosen) < n:
            raise ValueError(f"pool exhausted: needed {n}, pool={pool}, already used={used}")
        used.update(chosen)
        return chosen

    groups = {}
    groups["M1"] = take(pools["middle_band"], 2)
    groups["M2"] = take(pools["middle_band"], 2)
    e1_early = take(pools["earliest_extreme"], 1)
    e1_late = take(pools["latest_extreme"], 1)
    groups["E1"] = e1_early + e1_late
    e2_early = take(pools["earliest_extreme"], 1)
    e2_late = take(pools["latest_extreme"], 1)
    groups["E2"] = e2_early + e2_late
    groups["H1"] = take(pools["h1_pool"], 2)
    groups["H2"] = take(pools["h2_pool"], 2)
    return groups


def draw_examples(eligible_poets: dict, selection_order_poet_ids: list) -> dict:
    """One random.seed(ERAS_EXAMPLE_SEED) call, then one
    random.sample(eligible_verses_for_poet, 1) per poet IN
    selection_order_poet_ids -- sequential RNG consumption, never
    reseeded mid-draw (same convention as multipoet_examples.py)."""
    id_to_name = {info["poet_id"]: name for name, info in eligible_poets.items()}
    random.seed(ERAS_EXAMPLE_SEED)
    drawn = {}
    for poet_id in selection_order_poet_ids:
        name = id_to_name[poet_id]
        candidates = eligible_poets[name]["verses"]
        poem_id, poem_name, verse_no, verse_text, annots = random.sample(candidates, 1)[0]
        drawn[poet_id] = {
            "poet_name": name, "period": eligible_poets[name]["period"], "poet_id": poet_id,
            "poem_id": poem_id, "poem_name": poem_name, "verse_no": verse_no, "text": verse_text,
            "n_candidate_verses_for_poet": len(candidates),
            "annotations": [{"span": a["span"], "analysis": a["analysis"]} for a in annots],
        }
    return drawn


def build_eras_sets() -> tuple:
    filter_counts = defaultdict(int)
    eligible_poets = build_eligible_poets(filter_counts)
    axis = json.loads(ERAS_AXIS_PATH.read_text(encoding="utf-8"))
    pools = build_group_pools(eligible_poets, axis)
    groups = select_group_poets(pools)

    flat_order = []
    for g in ("M1", "M2", "E1", "E2", "H1", "H2"):
        flat_order.extend(groups[g])
    drawn_by_id = draw_examples(eligible_poets, flat_order)

    sets = {g: [drawn_by_id[pid] for pid in groups[g]] for g in groups}
    return sets, pools, groups, dict(filter_counts), eligible_poets


def main():
    sets, pools, groups, filter_counts, eligible_poets = build_eras_sets()

    print("Note-quality filter report (over every استعارة فعل annotation with a non-empty note, "
          "within the eras-eligible candidate pool):")
    for k, v in sorted(filter_counts.items()):
        print(f"  {k}: {v}")

    print("\nPool sizes (eligible, confidence-ok poets per band):")
    for name, pool in pools.items():
        print(f"  {name}: {len(pool)} poets -> {pool}")

    print(f"\nTotal eligible poets (any band, pre-restriction): {len(eligible_poets)}")

    used_all = set()
    for g in ("M1", "M2", "E1", "E2", "H1", "H2"):
        print(f"\n{'=' * 78}\nSET {g}\n{'=' * 78}")
        for pid in groups[g]:
            assert pid not in used_all, f"poet {pid} reused across groups"
            used_all.add(pid)
        for pid in groups[g]:
            print(f"  poet_id={pid}")
    print(f"\nOK: {len(used_all)} distinct poets across all six groups (expected 12).")

    ERAS_EXAMPLE_SETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ERAS_EXAMPLE_SETS_PATH.write_text(
        json.dumps({"seed": ERAS_EXAMPLE_SEED, "sets": sets}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {ERAS_EXAMPLE_SETS_PATH}")

    ERAS_NOTE_FILTER_REPORT_PATH.write_text(json.dumps(filter_counts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {ERAS_NOTE_FILTER_REPORT_PATH}")


if __name__ == "__main__":
    main()
