"""Step 1 unit checks for the poet-era few-shot experiment (NO API calls),
same convention as unit_checks_multipoet.py / preview_and_diff_D.py:
  1. A/B/C/Z prompt previews are unchanged.
  2. No eras example-source poem leaks into eval_pool_25.json (the pool
     M1..H2 are themselves evaluated on).
  3. Each of the six sets has exactly 2 distinct poets; all 12 poet ids
     across the six sets are globally distinct.
  4. GT reproduces counts: every drawn example verse really carries an
     استعارة فعل annotation matching one of its drawn spans (re-derived
     from the poem JSON directly, not just trusted from the draw step).
  5. Writes config/prompt_preview_{M1,M2,E1,E2,H1,H2}.txt and asserts each
     one's header + "Example 1" block is byte-identical to set A's (same
     scaffold, only the drawn examples differ).
"""
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import CONFIG_DIR, E1V1_DIR, SET_NAMES, SUBTYPE_FOCUS  # noqa: E402
from eras_config import ERAS_SET_NAMES  # noqa: E402
from eras_examples import build_eras_sets  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from multipoet_prompt_builder import build_system_message_n  # noqa: E402
from prompt_builder import build_system_message  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

EVAL_POOL_25_PATH = CONFIG_DIR / "eval_pool_25.json"


def check_zabc_unchanged() -> bool:
    all_ok = True
    for name in SET_NAMES:
        existing = (CONFIG_DIR / f"prompt_preview_{name}.txt").read_text(encoding="utf-8")
        regenerated = build_system_message(name)
        if existing.rstrip("\n") != regenerated.rstrip("\n"):
            all_ok = False
            print(f"*** MISMATCH for set {name} *** (A/B/C/Z must stay byte-identical)")
            diff = difflib.unified_diff(
                existing.splitlines(keepends=True), regenerated.splitlines(keepends=True),
                fromfile=f"existing_{name}", tofile=f"regenerated_{name}",
            )
            print("".join(diff))
        else:
            print(f"OK: set {name} regenerated prompt is byte-identical to the committed preview.")
    return all_ok


def check_no_leakage(sets: dict):
    example_poem_ids = {e["poem_id"] for examples in sets.values() for e in examples}
    pool_ids = {p["poem_id"] for p in json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]}
    overlap = example_poem_ids & pool_ids
    assert not overlap, f"eras example-source poems leaked into eval_pool_25.json: {overlap}"
    print(f"OK: 0 overlap between eval_pool_25.json's {len(pool_ids)} poems and the "
          f"{len(example_poem_ids)} eras example-source poems {sorted(example_poem_ids, key=int)}.")


def check_poet_structure(sets: dict):
    all_poet_ids = []
    for g in ERAS_SET_NAMES:
        examples = sets[g]
        poet_ids = [e["poet_id"] for e in examples]
        assert len(examples) == 2, f"set {g} must have exactly 2 examples, got {len(examples)}"
        assert len(set(poet_ids)) == 2, f"set {g}'s 2 examples must be from 2 distinct poets, got {poet_ids}"
        all_poet_ids.extend(poet_ids)
    assert len(set(all_poet_ids)) == len(all_poet_ids) == 12, (
        f"expected 12 globally distinct poets across all six groups, got {len(set(all_poet_ids))} "
        f"distinct out of {len(all_poet_ids)}: {all_poet_ids}"
    )
    print(f"OK: all six sets have exactly 2 distinct poets each; all 12 poet ids are globally distinct "
          f"across the six groups: {sorted(all_poet_ids, key=int)}")


def check_gt_reproduces(sets: dict):
    for set_name in ERAS_SET_NAMES:
        for e in sets[set_name]:
            pj = load_poem_json(e["poem_id"])
            gt = gt_spans_for_subtype(pj, SUBTYPE_FOCUS)
            spans_at_verse = gt[e["verse_no"]]
            assert spans_at_verse, (
                f"{set_name}: poem {e['poem_id']} verse {e['verse_no']} has no "
                f"{SUBTYPE_FOCUS} GT span -- draw step's eligibility check did not hold"
            )
            drawn_spans = {a["span"] for a in e["annotations"]}
            assert drawn_spans <= set(spans_at_verse) | {""}, (
                f"{set_name}: drawn annotation spans {drawn_spans} not found in "
                f"freshly-recomputed GT spans {spans_at_verse} for poem {e['poem_id']} v{e['verse_no']}"
            )
        print(f"OK: set {set_name}: all {len(sets[set_name])} drawn example verses independently "
              f"reconfirmed to carry a GT {SUBTYPE_FOCUS} span.")


def check_scaffold_matches_a(sets: dict):
    a_text = (CONFIG_DIR / "prompt_preview_A.txt").read_text(encoding="utf-8")

    def head(text):
        lines = text.splitlines()
        for i, l in enumerate(lines):
            if l.startswith("Example 2"):
                return lines[:i]
        return lines

    a_head = head(a_text)
    for g in ERAS_SET_NAMES:
        built = build_system_message_n(sets[g])
        assert head(built) == a_head, f"set {g}'s header+Example-1 block differs from set A's scaffold"
    print("OK: all six eras sets share the byte-identical header + Example 1 scaffold as set A "
          "(only Example 2/3 differ, same convention as A/B/C/D/D2/F5/F10).")


def main():
    print("=" * 78)
    print("1. Verifying Z/A/B/C previews are unchanged")
    print("=" * 78)
    if not check_zabc_unchanged():
        print("\n*** STOP: A/B/C/Z previews changed. Do not proceed. ***")
        return
    print()

    sets, pools, groups, filter_counts, eligible_poets = build_eras_sets()

    print("=" * 78)
    print("2. No eras example-source poem in eval_pool_25.json")
    print("=" * 78)
    check_no_leakage(sets)
    print()

    print("=" * 78)
    print("3. Exactly 2 distinct poets per set; 12 globally distinct poets")
    print("=" * 78)
    check_poet_structure(sets)
    print()

    print("=" * 78)
    print("4. GT reproduces counts for every drawn example")
    print("=" * 78)
    check_gt_reproduces(sets)
    print()

    print("=" * 78)
    print("5. Scaffold matches set A's header + Example 1; writing prompt previews")
    print("=" * 78)
    check_scaffold_matches_a(sets)
    for set_name in ERAS_SET_NAMES:
        text = build_system_message_n(sets[set_name])
        out_path = CONFIG_DIR / f"prompt_preview_{set_name}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}")

    print("\nAll unit checks passed. No API calls made.")


if __name__ == "__main__":
    main()
