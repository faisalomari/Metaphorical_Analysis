"""Build the blind re-annotation sample: a stratified random sample of verses
across all 5 poems, proportional to each poem's verse count.

Why proportional allocation, and why n=80 (see agreement_protocol.md §3 for
the full reasoning): per-element verse-level prevalence across the real,
already-collected ground truth (computed once, printed by this script, and
reproduced in agreement_protocol.md) is high enough for every element
(19.6%-62.5%) that a plain proportional sample - no element-based
oversampling needed - gives a non-degenerate 2x2 table (>=10 in both the
positive and negative cell) for all 4 elements at n=80. Fixed seed for
reproducibility; this script contains no invented numbers, only counts
computed from `experiments/pilot_3models/ground_truth.py`.

Output: writing/paper_plan/iaa/sheets/sample_manifest.csv
  columns: poem, verse_no (no verse text, no labels - that's generated
  separately and kept blind; this manifest is the sampling record).
"""
import csv
import random

from common import IAA_DIR, config, load_ground_truth_for_poem

SEED = 42
SAMPLE_SIZE = 80


def prevalence_report():
    total_verses = 0
    el_counts = {el: 0 for el in config.ELEMENT_ORDER}
    for poem in config.POEMS:
        gt = load_ground_truth_for_poem(poem)
        n = config.POEMS[poem]["n_verses"]
        total_verses += n
        for v in range(1, n + 1):
            for el in config.ELEMENT_ORDER:
                if gt.get(v, {}).get(el):
                    el_counts[el] += 1
    print(f"Ground-truth verse-level prevalence across all {total_verses} verses (5 poems):")
    for el in config.ELEMENT_ORDER:
        c = el_counts[el]
        print(f"  {el}: {c} verses ({c / total_verses:.1%})")
    return total_verses, el_counts


def build_sample():
    rng = random.Random(SEED)
    rows = []
    for poem_key, info in config.POEMS.items():
        n_verses = info["n_verses"]
        quota = round(SAMPLE_SIZE * n_verses / sum(p["n_verses"] for p in config.POEMS.values()))
        quota = max(1, min(quota, n_verses))
        chosen = sorted(rng.sample(range(1, n_verses + 1), quota))
        for v in chosen:
            rows.append({"poem": poem_key, "verse_no": v})
    return rows


def expected_positives(rows):
    """Sanity-check the chosen sample's own prevalence per element (not a new
    invented number - counted directly from the same ground truth used to draw
    the sample)."""
    counts = {el: 0 for el in config.ELEMENT_ORDER}
    by_poem_gt = {poem: load_ground_truth_for_poem(poem) for poem in config.POEMS}
    for row in rows:
        gt = by_poem_gt[row["poem"]].get(row["verse_no"], {})
        for el in config.ELEMENT_ORDER:
            if gt.get(el):
                counts[el] += 1
    return counts


def main():
    total_verses, el_counts = prevalence_report()
    rows = build_sample()
    print(f"\nDrew {len(rows)} verses (seed={SEED}), proportional by poem:")
    by_poem = {}
    for row in rows:
        by_poem[row["poem"]] = by_poem.get(row["poem"], 0) + 1
    for poem, n in by_poem.items():
        print(f"  {poem}: {n} of {config.POEMS[poem]['n_verses']}")

    positives = expected_positives(rows)
    print(f"\nExpected positive-verse counts WITHIN the drawn sample (sanity check, n={len(rows)}):")
    for el in config.ELEMENT_ORDER:
        print(f"  {el}: {positives[el]}")

    out_path = IAA_DIR / "sheets" / "sample_manifest.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["poem", "verse_no"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
