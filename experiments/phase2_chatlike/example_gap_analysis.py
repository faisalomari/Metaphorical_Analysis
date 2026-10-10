"""Task 3 (2026-07-26 session) - example-vs-test gap analysis.

Characterizes data/elements/*.txt's worked examples against the ground-truth
instance population (all 5 poems, with TEST called out separately since
that's where the miss rate lives): subtype coverage, marker explicitness,
span length, single- vs multi-figure verses. Zero new API calls - pure
analysis over already-existing files.

Method: every example line in data/elements/*.txt turns out to be a REAL verse
from one of this project's 5 annotated poems (not a synthetic/textbook
example) - so each example's true subtype/multi-figure context can be looked
up directly from Dr. Ali Hussein's ground truth, rather than judged by eye.
"""
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "pilot_3models"))

from config import POEMS, ELEMENTS_DIR, ELEMENT_FILES, TEST_POEMS, DEV_POEMS
from ground_truth import load_ground_truth_spans

ARABIC_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْٰۖ-ۭ]")
EXPLICIT_MARKERS = ["كأن", "كأنما", "كما", "مثل"]  # simile particles; also checked as Trope/Kenning false-marker signal


def normalize(text):
    if not text:
        return ""
    text = ARABIC_DIACRITICS.sub("", text)
    text = text.replace("ـ", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip("\"'«»")


def load_all_poem_verses():
    """Returns {poem_key: {verse_no: normalized_verse_text}}"""
    out = {}
    for poem_key, meta in POEMS.items():
        text = meta["poetry_path"].read_text(encoding="utf-8")
        verses = {}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(\d+)\)\s*(.*)$", line)
            if not m:
                continue
            no = int(m.group(1))
            verses[no] = normalize(m.group(2))
        out[poem_key] = verses
    return out


def find_example_source(example_text, all_verses):
    """Find which (poem, verse_no) an example line comes from, by normalized
    substring/equality match against every poem's verse text."""
    norm_example = normalize(example_text)
    for poem_key, verses in all_verses.items():
        for no, vtext in verses.items():
            if norm_example == vtext or norm_example in vtext or vtext in norm_example:
                return poem_key, no
    return None, None


def parse_examples_file(path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    examples = []
    in_examples = False
    for line in lines:
        if line.strip().startswith("Examples:"):
            in_examples = True
            continue
        if in_examples and line.strip():
            m = re.match(r"^\d+\)\s*(.*)$", line.strip())
            if m:
                examples.append(m.group(1).strip())
    return examples


def has_explicit_marker(verse_text):
    """Explicit simile-particle markers: standalone كأن/كأنما/كما/مثل, PLUS the
    attached kaf-of-comparison (ك+noun, e.g. كالمسك) - a single-letter clitic
    like و/ف's handling in span_matching.py, not a standalone token, so it
    needs its own word-level check rather than a plain substring match."""
    norm = normalize(verse_text)
    found = [m for m in EXPLICIT_MARKERS if re.search(rf"(^|\s){re.escape(m)}($|\s)", norm)]
    for word in norm.split():
        candidates = {word}
        if len(word) > 3 and word[0] in ("و", "ف"):
            candidates.add(word[1:])  # strip attached و/ف clitic before checking
        for w in candidates:
            if (w.startswith("كال") or w.startswith("كأ")) and w not in found:
                found.append(w)
    return found


def main():
    all_verses = load_all_poem_verses()
    gt_by_poem = {poem_key: load_ground_truth_spans(poem_key) for poem_key in POEMS}

    element_files = {"Trope": "Trope.txt", "Simile": "Simile.txt", "Kenning": "Kenning.txt", "Antonymy": "Antonymy.txt"}
    example_records = defaultdict(list)

    for element, fname in element_files.items():
        examples = parse_examples_file(ELEMENTS_DIR / fname)
        for i, ex in enumerate(examples, 1):
            poem_key, verse_no = find_example_source(ex, all_verses)
            record = {"element": element, "index": i, "text": ex, "poem": poem_key, "verse": verse_no}
            if poem_key:
                gt_verse = gt_by_poem[poem_key][verse_no]
                record["gt_all_elements"] = {el: [inst["span"] for inst in gt_verse[el]] for el in gt_verse}
                record["gt_subtypes_this_element"] = [inst["secondary"] or inst["primary"] for inst in gt_verse[element]]
                record["split"] = "TEST" if poem_key in TEST_POEMS else "DEV"
                total_instances = sum(len(v) for v in gt_verse.values())
                record["multi_figure"] = total_instances > 1
                record["n_total_gt_instances_in_verse"] = total_instances
            record["has_explicit_marker"] = has_explicit_marker(ex)
            record["word_count"] = len(normalize(ex).split())
            example_records[element].append(record)

    print("=== Example provenance ===")
    for element, records in example_records.items():
        print(f"\n{element}:")
        for r in records:
            print(f"  #{r['index']}: poem={r['poem']} v{r['verse']} split={r.get('split')} "
                  f"subtypes={r.get('gt_subtypes_this_element')} multi_figure={r.get('multi_figure')} "
                  f"markers={r['has_explicit_marker']} words={r['word_count']}")
            print(f"       all-element GT in this verse: {r.get('gt_all_elements')}")

    # --- Population comparison: subtype distribution in ALL Trope GT instances (TEST+DEV pooled) ---
    print("\n=== Trope subtype distribution: examples vs full ground truth (all 5 poems) ===")
    example_subtypes = Counter()
    for r in example_records["Trope"]:
        for st in r.get("gt_subtypes_this_element", []):
            example_subtypes[st] += 1

    gt_subtypes_all = Counter()
    gt_subtypes_test = Counter()
    for poem_key in POEMS:
        gt = gt_by_poem[poem_key]
        for no in gt:
            for inst in gt[no]["Trope"]:
                label = inst["secondary"] or inst["primary"]
                gt_subtypes_all[label] += 1
                if poem_key in TEST_POEMS:
                    gt_subtypes_test[label] += 1

    print("Example count by subtype:", dict(example_subtypes))
    print("Full-corpus GT count by subtype (all 5 poems):", dict(gt_subtypes_all))
    print("TEST-only GT count by subtype:", dict(gt_subtypes_test))

    # --- Multi-figure share: corpus-wide vs example verses, per element ---
    print("\n=== Multi-figure verse share: corpus vs examples, per element ===")
    for element in element_files:
        corpus_multi, corpus_total = 0, 0
        for poem_key in POEMS:
            gt = gt_by_poem[poem_key]
            for no in gt:
                if gt[no][element]:
                    corpus_total += 1
                    total_instances = sum(len(v) for v in gt[no].values())
                    if total_instances > 1:
                        corpus_multi += 1
        ex_multi = sum(1 for r in example_records[element] if r.get("multi_figure"))
        ex_total = sum(1 for r in example_records[element] if r.get("poem"))
        print(f"{element}: corpus multi-figure {corpus_multi}/{corpus_total} "
              f"({100*corpus_multi/corpus_total:.0f}%) vs examples {ex_multi}/{ex_total} "
              f"({100*ex_multi/ex_total:.0f}%)")

    # --- Span word-length: corpus-wide average vs example-verse matched-element spans ---
    print("\n=== Average GT span word-length: corpus vs example-verse spans, per element ===")
    for element in element_files:
        corpus_lengths = []
        for poem_key in POEMS:
            gt = gt_by_poem[poem_key]
            for no in gt:
                for inst in gt[no][element]:
                    corpus_lengths.append(len(normalize(inst["span"]).split()))
        example_lengths = []
        for r in example_records[element]:
            if not r.get("poem"):
                continue
            gt = gt_by_poem[r["poem"]][r["verse"]]
            for inst in gt[element]:
                example_lengths.append(len(normalize(inst["span"]).split()))
        corpus_avg = sum(corpus_lengths) / len(corpus_lengths) if corpus_lengths else 0
        example_avg = sum(example_lengths) / len(example_lengths) if example_lengths else 0
        print(f"{element}: corpus avg {corpus_avg:.1f} words (n={len(corpus_lengths)}) "
              f"vs example-verse spans avg {example_avg:.1f} words (n={len(example_lengths)})")

    import json
    with open(ROOT / "results" / "phase2_chatlike" / "example_gap_analysis_data.json", "w", encoding="utf-8") as f:
        json.dump({
            "examples": {el: recs for el, recs in example_records.items()},
            "gt_subtypes_all": dict(gt_subtypes_all),
            "gt_subtypes_test": dict(gt_subtypes_test),
            "example_subtypes": dict(example_subtypes),
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
