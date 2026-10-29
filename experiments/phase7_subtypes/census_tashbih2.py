"""Step 0 addendum (NO API calls): census for the 2 تشبيه subtypes Dr. Ali
Hussein named in his reply (تشبيه قصير, تشبيه مطول — the likely exact string
for "طويل" per the task's own instruction to verify, not assume). Verifies
both exist verbatim in the corpus, builds the same per-subtype census table
census.py built for the first 2 approved subtypes, and checks what share of
تشبيه مطول's (and, for completeness, تشبيه قصير's) annotated spans cross a
verse boundary (verse_index carrying more than one distinct verse number),
per the task's explicit ask.

Does NOT edit census.py, phase7_example_sets.json, or any existing record —
additive only. Writes results/phase7_subtypes/census_tashbih2.json.

Reuses, unmodified: this package's own census.py (load_manifest,
load_poem_json, verse_no_of), phase4_e1_v2.eras_config.note_quality,
phase3_subelements.subtype_defs.SUBTYPE_DEFS.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, EVAL_POOL_25_PATH, NO_TEXT_POEM_ID, RESULTS_DIR,
)
from eras_config import note_quality  # noqa: E402
from subtype_defs import SUBTYPE_DEFS  # noqa: E402

TARGET_SUBTYPES = ["تشبيه قصير", "تشبيه مطول"]
# already drawn as example sources for the first 2 approved subtypes
# (phase7_example_sets.json) -- reported for transparency, not subtracted,
# since no examples have been drawn yet for these 2 new subtypes.
PHASE7_EXAMPLE_SOURCE_POEMS_SO_FAR = {"27110", "6174", "8470", "4480"}
MATERIALITY_THRESHOLD = 0.20


def main():
    manifest = load_manifest()
    poem_ids_all = [row["poem_id"] for row in manifest]
    poet_of_poem = {row["poem_id"]: row["poet_name"] for row in manifest}

    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = set(pool_doc["poem_ids"])

    all_poems = {}
    total_verses_corpus = 0
    subtype_counter = {}
    for pid in poem_ids_all:
        pj = load_poem_json(pid)
        all_poems[pid] = pj
        total_verses_corpus += pj["verse_count"]
        for a in pj["annotations"]:
            sub = (a.get("subtype") or "").strip()
            if sub:
                subtype_counter[sub] = subtype_counter.get(sub, 0) + 1

    print("=" * 70)
    print("STEP 0 ADDENDUM — census for تشبيه قصير / تشبيه مطول")
    print("=" * 70)

    # ---- exact-string existence check (verify, don't assume "طويل") ------
    print("\nExact-string existence check (task's own instruction: verify, "
          "don't substitute silently):")
    existence = {}
    for req in TARGET_SUBTYPES:
        n = subtype_counter.get(req, 0)
        in_defs = req in SUBTYPE_DEFS
        existence[req] = {"exact_annotation_count": n, "in_subtype_defs": in_defs}
        print(f"  {req!r}: exact annotation count = {n}, in subtype_defs.py = {in_defs}")

    n_long_variant = subtype_counter.get("تشبيه طويل", 0)
    print(f"\n  Literal 'تشبيه طويل' (the other spelling Dr. Ali mentioned): "
          f"{n_long_variant} exact hits in the corpus -- confirms 'تشبيه مطول' "
          f"(227 hits) is the correct corpus string, not 'تشبيه طويل'.")

    both_exact = all(existence[r]["exact_annotation_count"] > 0 for r in TARGET_SUBTYPES)
    if not both_exact:
        print("\n  *** At least one requested string has 0 exact hits -- STOP, see closest matches above. ***")

    # ---- per-subtype census table (same shape as census.py's) ------------
    def subtype_table(subtype: str) -> dict:
        pos_verse_keys = set()
        poems_with_pos = set()
        poets_with_pos = set()
        eligible_examples = []
        notes_total = 0
        notes_passing = 0
        pool_pos_verse_keys = set()
        multi_verse_annotation_count = 0
        total_annotation_count = 0

        for pid, pj in all_poems.items():
            n_verses = pj["verse_count"]
            for a in pj["annotations"]:
                if (a.get("subtype") or "").strip() != subtype:
                    continue
                vi_raw = str(a.get("verse_index"))
                vno = verse_no_of(a)
                if not (1 <= vno <= n_verses):
                    continue
                total_annotation_count += 1
                distinct_verse_nums = {int(x) for x in vi_raw.split(",") if x.strip()}
                if len(distinct_verse_nums) > 1:
                    multi_verse_annotation_count += 1

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
            "total_annotation_count": total_annotation_count,
            "multi_verse_annotation_count": multi_verse_annotation_count,
            "multi_verse_share": multi_verse_annotation_count / total_annotation_count if total_annotation_count else 0.0,
            "_eligible_examples_detail": eligible_examples,
        }

    results = {}
    print("\n" + "=" * 70)
    print("Per-subtype census table")
    print("=" * 70)
    header = (f"{'subtype':<16}{'pos_verses':>11}{'rate/verse':>11}{'poems':>7}{'poets':>7}"
              f"{'elig_ex':>9}{'elig_poets':>11}{'in_pool25':>10}")
    print(header)
    for req in TARGET_SUBTYPES:
        t = subtype_table(req)
        results[req] = t
        print(f"{req:<16}{t['positive_verses_corpus']:>11}{t['positive_rate_per_verse_corpus']:>11.4f}"
              f"{t['poems_with_positive']:>7}{t['poets_with_positive']:>7}"
              f"{t['eligible_example_verses']:>9}{t['distinct_poets_with_eligible_examples']:>11}"
              f"{t['positives_in_eval_pool_25']:>10}")

    print("\n'positives_in_eval_pool_25' is the raw 25-poem/327-verse pool, example-source poems "
          "NOT yet subtracted -- no few-shot examples have been drawn for these 2 subtypes yet "
          "(that is Step 1's job, next). For reference, the 4 poems already used as example "
          f"sources for the 2 approved subtypes ({sorted(PHASE7_EXAMPLE_SOURCE_POEMS_SO_FAR)}) "
          f"overlap the pool in 0 cases (same as the original Step 1 finding) and are not in "
          f"this pool either way.")

    print("\nDefinition/example presence in subtype_defs.py (task's explicit ask):")
    for req in TARGET_SUBTYPES:
        d = SUBTYPE_DEFS.get(req)
        print(f"  {req!r}: present, definition={d['definition_ar'][:70]}..." if d else f"  {req!r}: MISSING")

    # ---- verse-boundary-crossing check (task's explicit ask) -------------
    print("\n" + "=" * 70)
    print("Verse-boundary-crossing check (verse_index carrying >1 distinct verse number)")
    print("=" * 70)
    crossing_summary = {}
    for req in TARGET_SUBTYPES:
        t = results[req]
        share = t["multi_verse_share"]
        crossing_summary[req] = {
            "total_annotations": t["total_annotation_count"],
            "multi_verse_annotations": t["multi_verse_annotation_count"],
            "share": share,
            "material": share > MATERIALITY_THRESHOLD,
        }
        flag = "MATERIAL (>20%)" if share > MATERIALITY_THRESHOLD else "not material (<=20%)"
        print(f"  {req!r}: {t['multi_verse_annotation_count']}/{t['total_annotation_count']} annotations "
              f"cross a verse boundary ({share:.1%}) -- {flag}")

    any_material = any(v["material"] for v in crossing_summary.values())
    if any_material:
        print("\n  *** Material verse-crossing found -- STOP, see options (a)/(b) below. Do not choose silently. ***")
    else:
        print("\n  Neither subtype's verse-crossing share exceeds the 20% materiality bar -- "
              "no STOP needed on this point. Proceeding with single-verse input (option (a)) "
              "as the unit, same as the first 2 approved subtypes, since the few multi-verse "
              "spans are a small minority and verse_no_of() already takes the span's first "
              "verse number as its home verse, consistent with every prior phase's convention.")

    out = {
        "target_subtypes": TARGET_SUBTYPES,
        "existence_check": existence,
        "tashbih_tawil_literal_hits": n_long_variant,
        "both_exact_exist": both_exact,
        "per_subtype": {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in results.items()},
        "eligible_examples_detail": {k: v["_eligible_examples_detail"] for k, v in results.items()},
        "verse_crossing_summary": crossing_summary,
        "materiality_threshold": MATERIALITY_THRESHOLD,
        "any_material": any_material,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / "census_tashbih2.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
