"""Part 1, Step 2 (NO API calls): poet-death-year analytics over the full
ali_poems corpus (52 poets, data/ali_poems/manifest.csv +
data/ali_poems/poems/*.json), joined against data/ali_poems/poet_dates.csv
(Step 1's output). Every number below is computed programmatically from
those two sources -- nothing hand-typed.

Axis population: every poet with a non-blank death_year_ce in
poet_dates.csv (any confidence/approximate flag -- poets with NO date at
all are listed separately and excluded from every year-indexed stat, since
they cannot be placed on a time axis; this is what CLAUDE.md-style "mark
poets without reliable dates" means here).

Declared definitions (see eras_config.py for the two tunable constants):
  - PRIMARY MEDIAN = the VERSE-WEIGHTED median death year: build a
    multiset where poet P contributes verses(P) (excluding poem 28601,
    per the task's explicit instruction -- that poem has verse_count=0
    and no text anyway) copies of death_year_ce(P), then take the median
    of that multiset. This is the one used for every band/half/extreme
    classification below (chosen over the poems-weighted or plain
    per-poet median because every other metric in this project is
    verse-primary -- CLAUDE.md rule 4 / the 2026-10-14 verse-primary
    decision). Poems-weighted and plain per-poet median/mean are also
    reported, for comparison, but are NOT used for classification.
  - MIDPOINT = (min + max) / 2 of the axis population's death_year_ce --
    a property of the axis's range, not of its distribution (distinct
    from the median).
  - FIRST HALF = axis poets with death_year_ce < PRIMARY MEDIAN.
    SECOND HALF = axis poets with death_year_ce >= PRIMARY MEDIAN.
  - MIDDLE BAND = axis poets with |death_year_ce - PRIMARY MEDIAN| <=
    MIDDLE_BAND_HALF_WIDTH_YEARS (eras_config.py, currently 75 years).
  - EXTREMES = earliest/latest EXTREME_PCT (eras_config.py, currently 0.15)
    of the axis population BY POET COUNT, sorted by death_year_ce: the
    earliest-extreme threshold year is the death_year_ce at rank
    ceil(EXTREME_PCT * N) (1-indexed, ascending); every poet at or before
    that year is "earliest extreme" (ties at the boundary year are ALL
    included, so the extreme group can be slightly larger than the exact
    percentage -- declared here, not hidden). Symmetric for "latest".
  - FIRST/SECOND-HALF MEDIAN (for H1/H2's "middle of that half"): the
    same verse-weighted-median procedure, restricted to FIRST HALF (resp.
    SECOND HALF) poets only.
"""
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_DIR, NO_TEXT_POEM_ID, SUBTYPE_FOCUS  # noqa: E402
from eras_config import ERAS_AXIS_PATH, MIDDLE_BAND_HALF_WIDTH_YEARS, EXTREME_PCT, POET_DATES_PATH  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_manifest, load_poem_json  # noqa: E402

BIN_SIZE_YEARS = 100


def load_poet_dates() -> dict:
    """{poet_id: {poet_name, site_period, death_year_ce (int|None),
    death_year_ah (int|None), approximate (bool), confidence (str),
    source_url, note}}"""
    out = {}
    with open(POET_DATES_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ce = row["death_year_ce"].strip()
            ah = row["death_year_ah"].strip()
            out[row["poet_id"]] = {
                "poet_name": row["poet_name"],
                "site_period": row["site_period"],
                "death_year_ce": int(ce) if ce else None,
                "death_year_ah": int(ah) if ah else None,
                "approximate": row["approximate"].strip().lower() == "yes",
                "confidence": row["confidence"].strip().lower(),
                "source_url": row["source_url"],
                "note": row["note"],
            }
    return out


def build_poet_corpus_stats() -> dict:
    """{poet_id: {poet_name, period, n_poems, n_verses (excl. poem 28601),
    n_positive_verses (استعارة فعل GT-positive verses, excl. poem 28601),
    poem_ids}} -- purely from manifest.csv + poems/*.json, no dates."""
    rows = load_manifest()
    stats = defaultdict(lambda: {"poet_name": None, "period": None, "n_poems": 0,
                                  "n_verses": 0, "n_positive_verses": 0, "poem_ids": []})
    for r in rows:
        pid = r["poet_id"]
        s = stats[pid]
        s["poet_name"] = r["poet_name"]
        s["period"] = r["period"] or ""
        s["n_poems"] += 1
        s["poem_ids"].append(r["poem_id"])
        if r["poem_id"] == NO_TEXT_POEM_ID:
            continue  # excluded from verse counts (task instruction; also verse_count=0 anyway)
        pj = load_poem_json(r["poem_id"])
        s["n_verses"] += pj["verse_count"]
        gt = gt_spans_for_subtype(pj, SUBTYPE_FOCUS)
        s["n_positive_verses"] += sum(1 for spans in gt.values() if spans)
    return dict(stats)


def _weighted_median(pairs: list) -> float:
    """pairs: [(value, weight), ...] with integer weights. Median of the
    multiset formed by repeating each value `weight` times."""
    expanded = []
    for value, weight in pairs:
        expanded.extend([value] * int(weight))
    return statistics.median(expanded)


def build_axis_stats() -> dict:
    poet_dates = load_poet_dates()
    corpus = build_poet_corpus_stats()

    dated, undated = [], []
    for pid, c in corpus.items():
        d = poet_dates.get(pid)
        if d is None or d["death_year_ce"] is None:
            undated.append({"poet_id": pid, **c, "date_info": d})
            continue
        dated.append({"poet_id": pid, **c, "date_info": d})

    dated.sort(key=lambda p: p["date_info"]["death_year_ce"])
    years = [p["date_info"]["death_year_ce"] for p in dated]
    n = len(dated)

    median_by_poems = _weighted_median([(p["date_info"]["death_year_ce"], p["n_poems"]) for p in dated])
    median_by_verses = _weighted_median([(p["date_info"]["death_year_ce"], max(p["n_verses"], 1)) for p in dated])
    mean_by_poems = sum(p["date_info"]["death_year_ce"] * p["n_poems"] for p in dated) / sum(p["n_poems"] for p in dated)
    total_verses = sum(p["n_verses"] for p in dated)
    mean_by_verses = (sum(p["date_info"]["death_year_ce"] * p["n_verses"] for p in dated) / total_verses
                       if total_verses else float("nan"))
    plain_median = statistics.median(years)
    plain_mean = statistics.mean(years)
    midpoint = (min(years) + max(years)) / 2.0

    PRIMARY_MEDIAN = median_by_verses  # see module docstring

    first_half = [p for p in dated if p["date_info"]["death_year_ce"] < PRIMARY_MEDIAN]
    second_half = [p for p in dated if p["date_info"]["death_year_ce"] >= PRIMARY_MEDIAN]
    middle_band = [p for p in dated
                   if abs(p["date_info"]["death_year_ce"] - PRIMARY_MEDIAN) <= MIDDLE_BAND_HALF_WIDTH_YEARS]

    n_extreme = max(1, math.ceil(n * EXTREME_PCT)) if n else 0
    earliest_threshold_year = dated[n_extreme - 1]["date_info"]["death_year_ce"] if n else None
    latest_threshold_year = dated[n - n_extreme]["date_info"]["death_year_ce"] if n else None
    earliest_extreme = [p for p in dated if p["date_info"]["death_year_ce"] <= earliest_threshold_year]
    latest_extreme = [p for p in dated if p["date_info"]["death_year_ce"] >= latest_threshold_year]

    def half_median(half_list):
        return _weighted_median([(p["date_info"]["death_year_ce"], max(p["n_verses"], 1)) for p in half_list])

    first_half_median = half_median(first_half) if first_half else None
    second_half_median = half_median(second_half) if second_half else None

    def bin_of(year):
        start = (year // BIN_SIZE_YEARS) * BIN_SIZE_YEARS
        return f"{start}-{start + BIN_SIZE_YEARS - 1}"

    bins = defaultdict(lambda: {"n_poets": 0, "n_poems": 0, "n_verses": 0, "n_positive_verses": 0})
    for p in dated:
        b = bins[bin_of(p["date_info"]["death_year_ce"])]
        b["n_poets"] += 1
        b["n_poems"] += p["n_poems"]
        b["n_verses"] += p["n_verses"]
        b["n_positive_verses"] += p["n_positive_verses"]

    by_era = defaultdict(lambda: {"n_poets": 0, "n_poems": 0, "n_verses": 0, "n_positive_verses": 0,
                                   "n_poets_dated": 0})
    for pid, c in corpus.items():
        e = by_era[c["period"] or "(blank)"]
        e["n_poets"] += 1
        e["n_poems"] += c["n_poems"]
        e["n_verses"] += c["n_verses"]
        e["n_positive_verses"] += c["n_positive_verses"]
        if pid in poet_dates and poet_dates[pid]["death_year_ce"] is not None:
            e["n_poets_dated"] += 1

    cumulative = []
    cum_poems = cum_verses = 0
    for i, p in enumerate(dated):
        cum_poems += p["n_poems"]
        cum_verses += p["n_verses"]
        cumulative.append({
            "poet_id": p["poet_id"], "poet_name": p["poet_name"],
            "death_year_ce": p["date_info"]["death_year_ce"],
            "cum_poets": i + 1, "cum_poems": cum_poems, "cum_verses": cum_verses,
        })

    per_poet = []
    for pid, p in sorted(corpus.items(), key=lambda kv: kv[1]["poet_name"]):
        d = poet_dates.get(pid, {})
        per_poet.append({
            "poet_id": pid, "poet_name": p["poet_name"], "period": p["period"],
            "n_poems": p["n_poems"], "n_verses": p["n_verses"], "n_positive_verses": p["n_positive_verses"],
            "death_year_ce": d.get("death_year_ce"), "death_year_ah": d.get("death_year_ah"),
            "approximate": d.get("approximate"), "confidence": d.get("confidence"),
            "has_reliable_date": d.get("death_year_ce") is not None,
        })

    def tag_set(lst):
        return sorted(p["poet_id"] for p in lst)

    result = {
        "n_poets_total": len(corpus),
        "n_poets_dated": n,
        "n_poets_undated": len(undated),
        "undated_poets": [{"poet_id": p["poet_id"], "poet_name": p["poet_name"],
                            "note": (p["date_info"] or {}).get("note", "no poet_dates.csv row")} for p in undated],
        "median_by_poems": median_by_poems, "median_by_verses": median_by_verses,
        "mean_by_poems": mean_by_poems, "mean_by_verses": mean_by_verses,
        "plain_median": plain_median, "plain_mean": plain_mean,
        "primary_median": PRIMARY_MEDIAN,
        "midpoint": midpoint, "min_year": min(years) if years else None, "max_year": max(years) if years else None,
        "middle_band_half_width_years": MIDDLE_BAND_HALF_WIDTH_YEARS,
        "extreme_pct": EXTREME_PCT,
        "earliest_threshold_year": earliest_threshold_year, "latest_threshold_year": latest_threshold_year,
        "first_half_median": first_half_median, "second_half_median": second_half_median,
        "counts": {
            "first_half": {"n_poets": len(first_half), "n_poems": sum(p["n_poems"] for p in first_half),
                           "n_verses": sum(p["n_verses"] for p in first_half)},
            "second_half": {"n_poets": len(second_half), "n_poems": sum(p["n_poems"] for p in second_half),
                            "n_verses": sum(p["n_verses"] for p in second_half)},
            "middle_band": {"n_poets": len(middle_band), "n_poems": sum(p["n_poems"] for p in middle_band),
                            "n_verses": sum(p["n_verses"] for p in middle_band)},
            "earliest_extreme": {"n_poets": len(earliest_extreme), "n_poems": sum(p["n_poems"] for p in earliest_extreme),
                                 "n_verses": sum(p["n_verses"] for p in earliest_extreme)},
            "latest_extreme": {"n_poets": len(latest_extreme), "n_poems": sum(p["n_poems"] for p in latest_extreme),
                               "n_verses": sum(p["n_verses"] for p in latest_extreme)},
        },
        "band_poet_ids": {
            "first_half": tag_set(first_half), "second_half": tag_set(second_half),
            "middle_band": tag_set(middle_band), "earliest_extreme": tag_set(earliest_extreme),
            "latest_extreme": tag_set(latest_extreme),
        },
        "bins": dict(sorted(bins.items(), key=lambda kv: int(kv[0].split("-")[0]))),
        "by_era": dict(by_era),
        "cumulative": cumulative,
        "per_poet": per_poet,
    }
    return result


def main():
    stats = build_axis_stats()
    ERAS_AXIS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ERAS_AXIS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {ERAS_AXIS_PATH}")
    print(f"Poets: {stats['n_poets_total']} total, {stats['n_poets_dated']} dated, {stats['n_poets_undated']} undated")
    print(f"Median (by verses, PRIMARY): {stats['median_by_verses']:.1f}  "
          f"(by poems: {stats['median_by_poems']:.1f}, plain per-poet: {stats['plain_median']:.1f})")
    print(f"Mean (by verses): {stats['mean_by_verses']:.1f}  (by poems: {stats['mean_by_poems']:.1f}, "
          f"plain per-poet: {stats['plain_mean']:.1f})")
    print(f"Midpoint of axis: {stats['midpoint']:.1f}  (range {stats['min_year']}-{stats['max_year']})")
    print(f"Middle band (+-{stats['middle_band_half_width_years']}y): {stats['counts']['middle_band']}")
    print(f"First half (<{stats['primary_median']:.1f}): {stats['counts']['first_half']}  "
          f"(median {stats['first_half_median']:.1f})")
    print(f"Second half (>={stats['primary_median']:.1f}): {stats['counts']['second_half']}  "
          f"(median {stats['second_half_median']:.1f})")
    print(f"Earliest extreme (<= {stats['earliest_threshold_year']}): {stats['counts']['earliest_extreme']}")
    print(f"Latest extreme (>= {stats['latest_threshold_year']}): {stats['counts']['latest_extreme']}")
    if stats["undated_poets"]:
        print("Undated poets (excluded from every year-indexed stat above):")
        for p in stats["undated_poets"]:
            print(f"  {p['poet_name']} ({p['poet_id']}): {p['note']}")


if __name__ == "__main__":
    main()
