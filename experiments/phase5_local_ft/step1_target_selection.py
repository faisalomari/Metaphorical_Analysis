"""Step 1 (task instructions): choose 5 targets FROM DATA, not by guess.

1. Count positive verses + poems-containing for every subtype (exact string)
   and the 4 parent elements, across data/ali_poems/poems/*.json (excl. 28601).
2. Keep candidates with >=150 positive verses (lower the threshold if <5 qualify).
3. Among candidates, take the highest verse counts.
4. Rank difficulty from existing LLM results (Phase 1 frozen F1, Phase 3
   per-subtype recall incl. crossmodel, E1 v2 verse-F1 for استعارة فعل) and
   assign 5 levels (very easy/easy/medium/hard/very hard), one target each,
   forcing استعارة فعل in as the medium reference.

No training, no API calls. Prints the full table + the final 5-target table.
"""
import json
from collections import Counter

from data_io import PARENT_AR, PARENT_ORDER, list_poem_files, load_poem, positive_verses_by_parent, positive_verses_by_subtype

OUT_PATH_STATS = "config/subtype_verse_stats.json"
MIN_POSITIVE_VERSES = 150


def collect_stats():
    poem_files = list_poem_files()
    subtype_verses = Counter()
    subtype_poems = Counter()
    parent_verses = Counter()
    parent_poems = Counter()
    total_verses = 0
    n_poems = 0
    for f in poem_files:
        poem = load_poem(f)
        n_poems += 1
        total_verses += poem["verse_count"]
        by_subtype = positive_verses_by_subtype(poem)
        for subtype, verses in by_subtype.items():
            if verses:
                subtype_verses[subtype] += len(verses)
                subtype_poems[subtype] += 1
        by_parent = positive_verses_by_parent(poem)
        for parent, verses in by_parent.items():
            if verses:
                parent_verses[parent] += len(verses)
                parent_poems[parent] += 1
    return {
        "n_poems": n_poems,
        "total_verses": total_verses,
        "subtype_verses": dict(subtype_verses),
        "subtype_poems": dict(subtype_poems),
        "parent_verses": dict(parent_verses),
        "parent_poems": dict(parent_poems),
    }


def print_table(stats):
    print(f"\n=== Corpus: {stats['n_poems']} poems (excl. 28601), {stats['total_verses']} verses ===\n")

    print("--- 4 parent elements ---")
    print(f"{'Parent':<12}{'Arabic':<10}{'pos_verses':<12}{'poems_with':<10}")
    for name in PARENT_ORDER:
        v = stats["parent_verses"].get(name, 0)
        p = stats["parent_poems"].get(name, 0)
        print(f"{name:<12}{PARENT_AR[name]:<10}{v:<12}{p:<10}")

    print("\n--- Every subtype (exact string), sorted by positive verse count desc ---")
    print(f"{'subtype':<45}{'pos_verses':<12}{'poems_with':<10}")
    rows = sorted(stats["subtype_verses"].items(), key=lambda kv: -kv[1])
    for subtype, v in rows:
        p = stats["subtype_poems"].get(subtype, 0)
        print(f"{subtype:<45}{v:<12}{p:<10}")
    return rows


def pick_candidates(rows, min_pos=MIN_POSITIVE_VERSES):
    candidates = [(s, v) for s, v in rows if v >= min_pos]
    if len(candidates) < 5:
        print(f"\n[threshold] fewer than 5 subtypes qualify at >={min_pos} positive verses "
              f"({len(candidates)} qualify) -- lowering threshold")
        sorted_rows = sorted(rows, key=lambda kv: -kv[1])
        candidates = sorted_rows[:max(5, len(candidates))]
        new_min = candidates[-1][1] if candidates else 0
        print(f"[threshold] lowered to >={new_min} positive verses to get >=5 candidates")
    else:
        print(f"\n[threshold] {len(candidates)} subtypes qualify at >={min_pos} positive verses")
    return candidates


if __name__ == "__main__":
    stats = collect_stats()
    with open(OUT_PATH_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    rows = print_table(stats)
    candidates = pick_candidates(rows)
    print("\n--- Candidates (subtype, pos_verses), highest verse counts first ---")
    for s, v in sorted(candidates, key=lambda kv: -kv[1]):
        print(f"{s:<45}{v}")
