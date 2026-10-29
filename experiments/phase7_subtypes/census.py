"""Step 0 data census (NO API calls): verifies the 3 requested subtype
strings exist verbatim in the full ali_poems corpus annotations, and builds
the per-subtype counts tables the task asked for, before any example-set
or cost work happens. Writes results/phase7_subtypes/census.json (machine-
readable) and prints the human-readable tables to stdout.

Reuses, unmodified: phase4_e1_v2.e1v2_config (poem exclusions),
phase4_e1_v2.eras_config.note_quality (note-quality filter),
phase3_subelements.subtype_defs.SUBTYPE_DEFS (definitions/examples).
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase7_config import (  # noqa: E402
    ALI_MANIFEST_PATH, ALI_POEMS_JSON_DIR, ALREADY_USED_POEM_IDS,
    EVAL_POOL_25_PATH, NO_TEXT_POEM_ID, REQUESTED_SUBTYPES, RESULTS_DIR,
)
from eras_config import note_quality  # noqa: E402
from subtype_defs import SUBTYPE_DEFS  # noqa: E402


def load_manifest() -> list:
    with open(ALI_MANIFEST_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_poem_json(poem_id: str) -> dict:
    matches = list(ALI_POEMS_JSON_DIR.glob(f"{poem_id}_*.json"))
    if not matches:
        raise FileNotFoundError(f"no poem json for poem_id={poem_id}")
    return json.loads(matches[0].read_text(encoding="utf-8"))


def verse_no_of(annotation: dict) -> int:
    return int(str(annotation["verse_index"]).split(",")[0])


def main():
    manifest = load_manifest()
    poem_ids_all = [row["poem_id"] for row in manifest]
    poet_of_poem = {row["poem_id"]: row["poet_name"] for row in manifest}

    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = set(pool_doc["poem_ids"])
    print(f"eval_pool_25.json: {len(pool_poem_ids)} poems, {pool_doc['pool_verses']} verse-units")

    all_poems = {}
    total_verses_corpus = 0
    subtype_counter = Counter()  # exact subtype string -> annotation count (all elements)
    for pid in poem_ids_all:
        pj = load_poem_json(pid)
        all_poems[pid] = pj
        total_verses_corpus += pj["verse_count"]
        for a in pj["annotations"]:
            sub = (a.get("subtype") or "").strip()
            if sub:
                subtype_counter[sub] += 1

    print(f"\nTotal poems in corpus: {len(poem_ids_all)}, total verses: {total_verses_corpus}")
    print(f"Total distinct subtype strings seen in annotations: {len(subtype_counter)}")

    # ---- Step 0a: exact-string existence check + closest matches ---------
    existence = {}
    for req in REQUESTED_SUBTYPES:
        exact_n = subtype_counter.get(req, 0)
        in_defs = req in SUBTYPE_DEFS
        existence[req] = {"exact_annotation_count": exact_n, "in_subtype_defs": in_defs}

    print("\n" + "=" * 70)
    print("STEP 0a — exact-string existence check")
    print("=" * 70)
    for req, info in existence.items():
        print(f"  {req!r}: exact annotation count = {info['exact_annotation_count']}, "
              f"in subtype_defs.py = {info['in_subtype_defs']}")

    # closest matches for any requested subtype with 0 exact hits: any
    # subtype string sharing a root keyword (تشبيه / بليغ / مؤكد / استعار /
    # قديم / كناي / صفة) with the requested string, excluding the requested
    # string itself.
    def keyword_roots(s: str) -> set:
        roots = []
        for kw in ["تشبيه", "بليغ", "مؤكد", "استعار", "قديم", "كناي", "صفة", "مرسل", "تمثيل"]:
            if kw in s:
                roots.append(kw)
        return set(roots)

    closest = {}
    for req in REQUESTED_SUBTYPES:
        if existence[req]["exact_annotation_count"] > 0:
            continue
        req_roots = keyword_roots(req)
        matches = []
        for sub, n in subtype_counter.items():
            if sub == req:
                continue
            if keyword_roots(sub) & req_roots:
                matches.append((sub, n))
        matches.sort(key=lambda t: -t[1])
        closest[req] = matches

    if closest:
        print("\nSTEP 0a — closest subtype strings for requested subtypes with 0 exact hits:")
        for req, matches in closest.items():
            print(f"  {req!r} -> 0 exact hits. Closest candidates (by shared keyword root):")
            for sub, n in matches:
                in_defs = sub in SUBTYPE_DEFS
                print(f"      {sub!r}: {n} annotations, in subtype_defs.py = {in_defs}")

    # full dump of every distinct subtype string containing "تشبيه" (for the
    # تشبيه بليغ / تشبيه مؤكد check specifically, task's explicit ask)
    print("\nAll distinct subtype strings containing 'تشبيه' (simile family), with counts:")
    tashbih_variants = sorted(
        [(s, n) for s, n in subtype_counter.items() if "تشبيه" in s], key=lambda t: -t[1]
    )
    for s, n in tashbih_variants:
        print(f"    {s!r}: {n}")

    print("\nAll distinct subtype strings containing 'استعار' (metaphor family), with counts:")
    for s, n in sorted([(s, n) for s, n in subtype_counter.items() if "استعار" in s], key=lambda t: -t[1]):
        print(f"    {s!r}: {n}")

    print("\nAll distinct subtype strings containing 'كناي' (periphrasis family), with counts:")
    for s, n in sorted([(s, n) for s, n in subtype_counter.items() if "كناي" in s], key=lambda t: -t[1]):
        print(f"    {s!r}: {n}")

    # ---- Step 0b/0c: per-subtype table -----------------------------------
    def subtype_table(subtype: str) -> dict:
        pos_verse_keys = set()  # (poem_id, verse_no)
        poems_with_pos = set()
        poets_with_pos = set()
        eligible_examples = []  # list of dicts
        notes_total = 0
        notes_passing = 0
        pool_pos_verse_keys = set()
        both_span_identity = []  # filled later for overlap check

        for pid, pj in all_poems.items():
            n_verses = pj["verse_count"]
            for a in pj["annotations"]:
                if (a.get("subtype") or "").strip() != subtype:
                    continue
                vno = verse_no_of(a)
                if not (1 <= vno <= n_verses):
                    continue
                pos_verse_keys.add((pid, vno))
                poems_with_pos.add(pid)
                poets_with_pos.add(poet_of_poem.get(pid, pj.get("poet_name")))
                if pid in pool_poem_ids:
                    pool_pos_verse_keys.add((pid, vno))

                note = (a.get("analysis") or "").strip()
                notes_total += 1
                is_genuine = False
                if note:
                    is_genuine, _reason = note_quality(note)
                if is_genuine:
                    notes_passing += 1
                    if pid not in ALREADY_USED_POEM_IDS and pid != NO_TEXT_POEM_ID:
                        eligible_examples.append({
                            "poem_id": pid, "poet_name": poet_of_poem.get(pid, pj.get("poet_name")),
                            "verse_no": vno, "span": (a.get("span_text") or "").strip(),
                            "note": note, "raw_key": a.get("raw_key"),
                        })

        eligible_poets = {e["poet_name"] for e in eligible_examples}
        return {
            "subtype": subtype,
            "positive_verses_corpus": len(pos_verse_keys),
            "positive_rate_per_verse_corpus": len(pos_verse_keys) / total_verses_corpus if total_verses_corpus else 0.0,
            "poems_with_positive": len(poems_with_pos),
            "poets_with_positive": len(poets_with_pos),
            "notes_total": notes_total,
            "notes_passing_quality_filter": notes_passing,
            "note_quality_rate": notes_passing / notes_total if notes_total else 0.0,
            "eligible_example_verses": len(eligible_examples),
            "distinct_poets_with_eligible_examples": len(eligible_poets),
            "positives_in_eval_pool_25": len(pool_pos_verse_keys),
            "_eligible_examples_detail": eligible_examples,
            "_positive_verse_keys": sorted(pos_verse_keys),
        }

    results = {}
    print("\n" + "=" * 70)
    print("STEP 0b — per-subtype census table")
    print("=" * 70)
    header = (f"{'subtype':<22}{'pos_verses':>11}{'rate/verse':>11}{'poems':>7}{'poets':>7}"
              f"{'elig_ex':>9}{'elig_poets':>11}{'in_pool25':>10}")
    print(header)
    for req in REQUESTED_SUBTYPES:
        t = subtype_table(req)
        results[req] = t
        print(f"{req:<22}{t['positive_verses_corpus']:>11}{t['positive_rate_per_verse_corpus']:>11.4f}"
              f"{t['poems_with_positive']:>7}{t['poets_with_positive']:>7}"
              f"{t['eligible_example_verses']:>9}{t['distinct_poets_with_eligible_examples']:>11}"
              f"{t['positives_in_eval_pool_25']:>10}")

    # ---- Step 0c: تشبيه بليغ vs تشبيه مؤكد specific comparison -----------
    print("\n" + "=" * 70)
    print("STEP 0c — تشبيه بليغ vs تشبيه مؤكد")
    print("=" * 70)
    c_subtypes = ["تشبيه بليغ", "تشبيه مؤكد"]
    c_results = {}
    for s in c_subtypes:
        t = subtype_table(s)
        c_results[s] = t
        in_defs = s in SUBTYPE_DEFS
        def_text = SUBTYPE_DEFS[s]["definition_ar"] + " " + SUBTYPE_DEFS[s]["example"] if in_defs else None
        def_len = len(def_text) if def_text else None
        print(f"\n  {s!r}: in subtype_defs.py = {in_defs}, def+example char length = {def_len}")
        print(f"    positive_verses_corpus={t['positive_verses_corpus']}, poems={t['poems_with_positive']}, "
              f"poets={t['poets_with_positive']}, rate/verse={t['positive_rate_per_verse_corpus']:.4f}")
        print(f"    note_quality_rate={t['note_quality_rate']:.3f} ({t['notes_passing_quality_filter']}/{t['notes_total']})")
        print(f"    eligible_example_verses={t['eligible_example_verses']}, "
              f"distinct_poets_with_eligible={t['distinct_poets_with_eligible_examples']}")
        print(f"    positives_in_eval_pool_25={t['positives_in_eval_pool_25']}")

    # overlap / confusability: verses carrying BOTH subtypes, and identical spans
    keys_a = set(c_results[c_subtypes[0]]["_positive_verse_keys"])
    keys_b = set(c_results[c_subtypes[1]]["_positive_verse_keys"])
    overlap_verses = keys_a & keys_b
    print(f"\n  Verses carrying BOTH {c_subtypes[0]!r} and {c_subtypes[1]!r}: {len(overlap_verses)}")
    if overlap_verses:
        # check identical-span overlap
        spans_a = defaultdict(set)
        spans_b = defaultdict(set)
        for pid, pj in all_poems.items():
            for a in pj["annotations"]:
                sub = (a.get("subtype") or "").strip()
                if sub not in c_subtypes:
                    continue
                vno = verse_no_of(a)
                span = (a.get("span_text") or "").strip()
                if sub == c_subtypes[0]:
                    spans_a[(pid, vno)].add(span)
                else:
                    spans_b[(pid, vno)].add(span)
        identical_span_verses = [k for k in overlap_verses if spans_a[k] & spans_b[k]]
        print(f"  Of those, verses where the span is IDENTICAL between the two subtypes: {len(identical_span_verses)}")

    results["_tashbih_balagh_vs_muakkad"] = {
        s: {k: v for k, v in c_results[s].items() if not k.startswith("_")} for s in c_subtypes
    }
    results["_tashbih_overlap_verses"] = len(overlap_verses)

    # strip heavy detail fields before writing JSON (keep a trimmed version)
    out = {}
    for k, v in results.items():
        if k.startswith("_"):
            out[k] = v
            continue
        out[k] = {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
        out[k]["_eligible_examples_detail"] = v["_eligible_examples_detail"]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "census.json"
    out_path.write_text(json.dumps({
        "total_poems": len(poem_ids_all),
        "total_verses_corpus": total_verses_corpus,
        "eval_pool_25_poems": len(pool_poem_ids),
        "eval_pool_25_verses": pool_doc["pool_verses"],
        "subtype_counter_all": dict(subtype_counter),
        "existence_check": existence,
        "closest_matches_for_zero_hit": closest,
        "tashbih_variants_all": tashbih_variants,
        "per_subtype": out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
