"""Step 1's <30-positives gate tripped for استعارة قديمة (15 positives in the
25-poem pool). This script computes OPTION (b) only -- what it would take to
extend the pool to >=30 positives for استعارة قديمة -- so the user can compare
it against OPTION (a) (keep 25 poems, mark استعارة قديمة indicative-only).
Does NOT modify phase7_example_sets.json or any existing config. No API calls.

Candidate pool for extension = all 167 manifest poems minus: NO_TEXT_POEM_ID,
the 5 Phase-1 frozen poems, the 25 poems already in eval_pool_25.json, and
the 4 example-source poems phase7_examples.py just drew. Declared seed
(EXTEND_SEED=100, a separate stream from the example-draw 42-series to avoid
any confusion between "picking examples" and "extending the eval pool") is
used to shuffle this candidate pool once, then poems are added in that fixed
shuffled order until استعارة قديمة's cumulative positive count reaches >=30
-- i.e. the SAME declared-seed-then-deterministic-order convention every
other sampling step in this project (phase4_e1_v2's build_pool_25.py,
eras_examples.py) already uses, not a bespoke one.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_manifest, load_poem_json, verse_no_of  # noqa: E402
from phase7_config import ALREADY_USED_POEM_IDS, NO_TEXT_POEM_ID, RESULTS_DIR  # noqa: E402

EXTEND_SEED = 100
TARGET_SUBTYPE = "استعارة قديمة"
OTHER_SUBTYPE = "كناية عن صفة"
TARGET_MIN = 30

# per-call cost means, read from docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md
# Part 3.2 / FULL_COST_MODEL_V2.md Sec 2 (hand-carried, not re-estimated here
# -- Step 2's own formal dry-run will compute Phase-7-specific real token
# counts; this is only enough precision to compare option (a) vs (b)).
PER_CALL_COST = {
    "zero": {"anthropic": 0.004957, "openai": 0.000846, "google": 0.001603},
    "few": {"anthropic": 0.005904, "openai": 0.001015, "google": 0.001889},
}


def main():
    manifest = load_manifest()
    poem_ids_all = [row["poem_id"] for row in manifest]

    phase7_sets_path = Path(__file__).resolve().parent / "config" / "phase7_example_sets.json"
    phase7_sets = json.loads(phase7_sets_path.read_text(encoding="utf-8"))
    pool_poem_ids = set(phase7_sets["eval_pool_25_poem_ids"])
    example_poem_ids = set(phase7_sets["example_source_poem_ids"])
    excluded = {NO_TEXT_POEM_ID} | ALREADY_USED_POEM_IDS | pool_poem_ids | example_poem_ids

    candidate_ids = [pid for pid in poem_ids_all if pid not in excluded]
    random.seed(EXTEND_SEED)
    shuffled = candidate_ids[:]
    random.shuffle(shuffled)

    current_target_positive = phase7_sets["pool_positive_counts"][TARGET_SUBTYPE]
    current_other_positive = phase7_sets["pool_positive_counts"][OTHER_SUBTYPE]
    current_verses = phase7_sets["final_eval_pool_verses"]

    added = []
    running_target = current_target_positive
    running_other = current_other_positive
    running_verses = current_verses
    for pid in shuffled:
        if running_target >= TARGET_MIN:
            break
        pj = load_poem_json(pid)
        n_verses = pj["verse_count"]
        target_pos = len({verse_no_of(a) for a in pj["annotations"]
                           if (a.get("subtype") or "").strip() == TARGET_SUBTYPE and 1 <= verse_no_of(a) <= n_verses})
        other_pos = len({verse_no_of(a) for a in pj["annotations"]
                          if (a.get("subtype") or "").strip() == OTHER_SUBTYPE and 1 <= verse_no_of(a) <= n_verses})
        added.append({"poem_id": pid, "poet_name": pj["poet_name"], "verse_count": n_verses,
                      f"{TARGET_SUBTYPE}_positives": target_pos, f"{OTHER_SUBTYPE}_positives": other_pos})
        running_target += target_pos
        running_other += other_pos
        running_verses += n_verses

    print(f"Candidate pool for extension: {len(candidate_ids)} poems (167 total - 1 no-text - 5 Phase1 "
          f"- {len(pool_poem_ids)} eval_pool_25 - {len(example_poem_ids)} example-source)")
    print(f"Declared seed: {EXTEND_SEED} (shuffle candidate pool once, add in that fixed order)")
    print(f"\nPoems added to reach >={TARGET_MIN} positives for {TARGET_SUBTYPE}:")
    for a in added:
        print(f"  poem {a['poem_id']} ({a['poet_name']}, {a['verse_count']} verses): "
              f"+{a[f'{TARGET_SUBTYPE}_positives']} {TARGET_SUBTYPE}, +{a[f'{OTHER_SUBTYPE}_positives']} {OTHER_SUBTYPE}")

    print(f"\nBefore: {current_target_positive} {TARGET_SUBTYPE} / {current_other_positive} {OTHER_SUBTYPE} "
          f"positives, {current_verses} verse-units, 25 poems")
    print(f"After:  {running_target} {TARGET_SUBTYPE} / {running_other} {OTHER_SUBTYPE} positives, "
          f"{running_verses} verse-units, {25 + len(added)} poems")

    extra_verses = running_verses - current_verses
    print(f"\nExtra verse-units added: {extra_verses}")
    print("Extra calls = extra_verses x 2 conditions x 3 models x 2 subtypes = "
          f"{extra_verses} x 2 x 3 x 2 = {extra_verses * 2 * 3 * 2}")

    print("\nExtra cost estimate (per-call means from FULL_COST_MODEL_V2.md Sec 2, same table used "
          "throughout this project -- Step 2 will recompute with Phase-7's real token counts):")
    total = 0.0
    for cond in ["zero", "few"]:
        for model, per_call in PER_CALL_COST[cond].items():
            c = extra_verses * 2 * per_call  # x2 subtypes
            total += c
            print(f"  {cond:5s} {model:10s}: {extra_verses} verses x 2 subtypes x ${per_call}/call = ${c:.4f}")
    print(f"  TOTAL extra cost estimate: ${total:.2f}")

    out = {
        "extend_seed": EXTEND_SEED, "target_subtype": TARGET_SUBTYPE, "target_min": TARGET_MIN,
        "added_poems": added, "before": {"target_positive": current_target_positive,
                                          "other_positive": current_other_positive, "verses": current_verses},
        "after": {"target_positive": running_target, "other_positive": running_other, "verses": running_verses},
        "extra_verses": extra_verses, "extra_calls": extra_verses * 2 * 3 * 2,
        "extra_cost_estimate_usd": round(total, 4),
    }
    out_path = RESULTS_DIR / "extend_pool_option.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
