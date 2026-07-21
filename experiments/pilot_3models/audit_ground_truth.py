"""Audit positive instance counts per element across ALL annotated poems in
data/ground_truth/ali_ana/original/*.xlsx (not just the pilot's one poem).

Reports both: row-level instance counts (a verse can have >1 instance of the
same element) and unique-verse counts (how many distinct verses contain at
least one instance), per poem and combined.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GT_DIR = ROOT / "data" / "ground_truth" / "ali_ana" / "original"

SUBSTRING_MAP = {
    "Trope": ["مجاز", "استعارة"],
    "Simile": ["تشبيه"],
    "Kenning": ["كناية"],
    "Antonymy": ["طباق"],
}
ELEMENT_ORDER = ["Trope", "Simile", "Kenning", "Antonymy"]

POEM_FILES = {
    "Imru1 (امرؤ القيس 1)": "امرؤ القيس 1.xlsx",
    "Imru2 (امرؤ القيس 8)": "امرؤ القيس 8.xlsx",
    "Nabigha (النابغة الذبياني)": "النابغة الذبياني.xlsx",
    "Jarir (جرير)": "جرير.xlsx",
    "Abu Tammam (ابو تمام)": "ابو تمام.xlsx",
}


def audit_poem(path: Path) -> dict:
    df = pd.read_excel(path)
    instance_counts = {name: 0 for name in ELEMENT_ORDER}
    verse_sets = {name: set() for name in ELEMENT_ORDER}
    for _, row in df.iterrows():
        labels = " ".join(str(row.get(c, "")) for c in ["العنصر البلاغي المستعمل", "العنصر البلاغي الثانوي"])
        verse_no = row.get("البيت")
        for name, substrings in SUBSTRING_MAP.items():
            if any(s in labels for s in substrings):
                instance_counts[name] += 1
                verse_sets[name].add(verse_no)
    return {
        "total_rows": len(df),
        "instance_counts": instance_counts,
        "unique_verse_counts": {name: len(v) for name, v in verse_sets.items()},
    }


def main():
    results = {}
    for label, filename in POEM_FILES.items():
        path = GT_DIR / filename
        if not path.exists():
            print(f"MISSING: {path}")
            continue
        results[label] = audit_poem(path)

    print(f"{'Poem':<30} {'Rows':>6} | " + " | ".join(f"{e:>9}" for e in ELEMENT_ORDER))
    print("-" * 100)
    totals = {name: 0 for name in ELEMENT_ORDER}
    total_unique = {name: 0 for name in ELEMENT_ORDER}
    for label, r in results.items():
        row_str = " | ".join(f"{r['instance_counts'][e]:>9}" for e in ELEMENT_ORDER)
        print(f"{label:<30} {r['total_rows']:>6} | {row_str}")
        for e in ELEMENT_ORDER:
            totals[e] += r["instance_counts"][e]
            total_unique[e] += r["unique_verse_counts"][e]

    print("-" * 100)
    print(f"{'TOTAL (instances, all poems)':<30} {'':>6} | " + " | ".join(f"{totals[e]:>9}" for e in ELEMENT_ORDER))
    print(f"{'TOTAL (unique verses, all poems)':<30} {'':>6} | " + " | ".join(f"{total_unique[e]:>9}" for e in ELEMENT_ORDER))


if __name__ == "__main__":
    main()
