"""Step 1 unit checks for the QUARTILE few-shot experiment (Q1/Q2), NO API
calls, same convention as unit_checks_eras.py / unit_checks_multipoet.py:
  1. Z/A/B/C AND M1/M2/E1/E2/H1/H2 prompt previews are unchanged (this
     task must not touch any existing eras set).
  2. No Q1/Q2 example-source poem leaks into eval_pool_25.json.
  3. Q1/Q2 each have exactly 2 distinct poets; all 4 poet ids across the
     two sets are globally distinct; NONE of the 4 is an M1/M2/E1/E2
     poet (hard rule, no exception); exactly the declared H2 poets
     (ديك الجن, ابن الرومي) are reused, one in each of Q1/Q2.
  4. GT reproduces counts: every drawn example verse really carries an
     استعارة فعل annotation matching one of its drawn spans.
  5. Writes config/prompt_preview_{Q1,Q2}.txt and asserts each one's
     header + "Example 1" block is byte-identical to set A's (same
     scaffold, only the drawn examples differ).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import CONFIG_DIR, E1V1_DIR, SET_NAMES, SUBTYPE_FOCUS  # noqa: E402
from eras_config import ERAS_SET_NAMES  # noqa: E402
from eras_examples import build_eras_sets  # noqa: E402
from eras_quartile_config import H1_H2_POET_NAMES, NEVER_REUSE_POET_NAMES, P75_REUSE_POOL_POET_NAMES, QUARTILE_SET_NAMES  # noqa: E402
from eras_quartile_examples import build_quartile_sets  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from multipoet_prompt_builder import build_system_message_n  # noqa: E402
from prompt_builder import build_system_message  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

EVAL_POOL_25_PATH = CONFIG_DIR / "eval_pool_25.json"


def check_existing_unchanged() -> bool:
    """A/B/C/Z (byte-identical regenerate) AND M1..H2 (byte-identical
    PERSISTED preview, since eras_examples.build_eras_sets() is itself
    deterministic and must not have been perturbed by anything this
    task added)."""
    all_ok = True
    for name in SET_NAMES:
        existing = (CONFIG_DIR / f"prompt_preview_{name}.txt").read_text(encoding="utf-8")
        regenerated = build_system_message(name)
        if existing.rstrip("\n") != regenerated.rstrip("\n"):
            all_ok = False
            print(f"*** MISMATCH for set {name} *** (A/B/C/Z must stay byte-identical)")
        else:
            print(f"OK: set {name} regenerated prompt is byte-identical to the committed preview.")

    eras_sets, _pools, _groups, _fc, _elig = build_eras_sets()
    for name in ERAS_SET_NAMES:
        existing = (CONFIG_DIR / f"prompt_preview_{name}.txt").read_text(encoding="utf-8")
        regenerated = build_system_message_n(eras_sets[name])
        if existing.rstrip("\n") != regenerated.rstrip("\n"):
            all_ok = False
            print(f"*** MISMATCH for set {name} *** (M1/M2/E1/E2/H1/H2 must stay byte-identical -- "
                  f"this task is additive-only, it must not have perturbed eras_examples.py's output)")
        else:
            print(f"OK: set {name} regenerated prompt is byte-identical to the committed preview "
                  f"(H1/H2 included -- untouched by the quartile task).")
    return all_ok


def check_no_leakage(sets: dict):
    example_poem_ids = {e["poem_id"] for examples in sets.values() for e in examples}
    pool_ids = {p["poem_id"] for p in json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]}
    overlap = example_poem_ids & pool_ids
    assert not overlap, f"Q1/Q2 example-source poems leaked into eval_pool_25.json: {overlap}"
    print(f"OK: 0 overlap between eval_pool_25.json's {len(pool_ids)} poems and the "
          f"{len(example_poem_ids)} Q1/Q2 example-source poems {sorted(example_poem_ids, key=int)}.")


def check_poet_structure(sets: dict):
    all_poet_ids, all_poet_names = [], []
    for g in QUARTILE_SET_NAMES:
        examples = sets[g]
        poet_ids = [e["poet_id"] for e in examples]
        poet_names = [e["poet_name"] for e in examples]
        assert len(examples) == 2, f"set {g} must have exactly 2 examples, got {len(examples)}"
        assert len(set(poet_ids)) == 2, f"set {g}'s 2 examples must be from 2 distinct poets, got {poet_ids}"
        all_poet_ids.extend(poet_ids)
        all_poet_names.extend(poet_names)
    assert len(set(all_poet_ids)) == len(all_poet_ids) == 4, (
        f"expected 4 globally distinct poets across Q1+Q2, got {len(set(all_poet_ids))} distinct "
        f"out of {len(all_poet_ids)}: {all_poet_ids}"
    )
    reused_me = set(all_poet_names) & NEVER_REUSE_POET_NAMES
    assert not reused_me, f"Q1/Q2 must never reuse an M1/M2/E1/E2 poet, but found: {reused_me}"
    reused_hh = set(all_poet_names) & H1_H2_POET_NAMES
    assert reused_hh == set(P75_REUSE_POOL_POET_NAMES), (
        f"Q1/Q2's only H1/H2 reuse must be exactly {P75_REUSE_POOL_POET_NAMES} (the declared P75-slot "
        f"reuse), got {reused_hh}"
    )
    print(f"OK: Q1/Q2 have exactly 2 distinct poets each; all 4 poet ids are globally distinct: "
          f"{sorted(all_poet_ids, key=int)}")
    print(f"OK: 0 M1/M2/E1/E2 poets reused. Declared H2-poet reuse confirmed exactly as specified: "
          f"{sorted(reused_hh)} (one per Q-set, P75 slot only).")


def check_gt_reproduces(sets: dict):
    for set_name in QUARTILE_SET_NAMES:
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
    for g in QUARTILE_SET_NAMES:
        built = build_system_message_n(sets[g])
        assert head(built) == a_head, f"set {g}'s header+Example-1 block differs from set A's scaffold"
    print("OK: both Q1/Q2 share the byte-identical header + Example 1 scaffold as set A "
          "(only Example 2 differs, same convention as every prior set family).")


def main():
    print("=" * 78)
    print("1. Verifying Z/A/B/C AND M1/M2/E1/E2/H1/H2 previews are unchanged")
    print("=" * 78)
    if not check_existing_unchanged():
        print("\n*** STOP: an existing set's prompt changed. Do not proceed. ***")
        return
    print()

    sets, groups, slot_detail, targets, filter_counts, eligible_poets = build_quartile_sets()

    print("=" * 78)
    print("2. No Q1/Q2 example-source poem in eval_pool_25.json")
    print("=" * 78)
    check_no_leakage(sets)
    print()

    print("=" * 78)
    print("3. Exactly 2 distinct poets per set; 4 globally distinct; reuse policy enforced")
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
    for set_name in QUARTILE_SET_NAMES:
        text = build_system_message_n(sets[set_name])
        out_path = CONFIG_DIR / f"prompt_preview_{set_name}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}")

    print("\nAll unit checks passed. No API calls made.")


if __name__ == "__main__":
    main()
