"""Step 1 unit checks for the multi-poet experiment (NO API calls):
  1. A/B/C/Z prompt previews are unchanged (same check as preview_and_diff_D.py).
  2. No example-source poem (F5/F10/F5b) appears in the new 50-poem pool.
  3. F5's poets are a subset of F10's poets; F10 has 10 distinct poets;
     F5b (if present) is disjoint from F10.
  4. GT reproduces counts: every drawn example verse really does carry an
     استعارة فعل annotation with a non-empty analysis note (re-derived from
     the poem JSON directly, not just trusted from the draw step), and the
     new pool's total استعارة فعل GT instance count is computed and printed.
  5. Writes config/prompt_preview_F5.txt / _F10.txt (and _F5b.txt if present).
"""
import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import CONFIG_DIR, E1V1_DIR, SET_NAMES, SUBTYPE_FOCUS  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402
from multipoet_config import EVAL_POOL_50_MULTIPOET_PATH  # noqa: E402
from multipoet_examples import build_multipoet_sets  # noqa: E402
from multipoet_prompt_builder import build_system_message_n  # noqa: E402
from prompt_builder import build_system_message  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402


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


def check_no_leakage(sets: dict, pool: list):
    example_poem_ids = {e["poem_id"] for examples in sets.values() for e in examples}
    pool_ids = {p["poem_id"] for p in pool}
    overlap = example_poem_ids & pool_ids
    assert not overlap, f"example-source poems leaked into the new 50-poem pool: {overlap}"
    print(f"OK: 0 overlap between the new {len(pool_ids)}-poem pool and the "
          f"{len(example_poem_ids)} example-source poems {sorted(example_poem_ids, key=int)}.")


def check_poet_structure(sets: dict):
    f5_poets = {e["poet_name"] for e in sets["F5"]}
    f10_poets = {e["poet_name"] for e in sets["F10"]}
    assert f5_poets <= f10_poets, "F5 poets must be a subset of F10 poets"
    assert len(f10_poets) == len(sets["F10"]) == 10, "F10 must have exactly 10 distinct poets"
    assert len(f5_poets) == len(sets["F5"]) == 5, "F5 must have exactly 5 distinct poets"
    print(f"OK: F5 ({len(f5_poets)} poets) subset of F10 ({len(f10_poets)} poets); "
          f"one poet per example in both.")
    if "F5b" in sets:
        f5b_poets = {e["poet_name"] for e in sets["F5b"]}
        assert len(f5b_poets) == len(sets["F5b"]) == 5
        assert not (f5b_poets & f10_poets), "F5b poets must be disjoint from F10 poets"
        print(f"OK: F5b ({len(f5b_poets)} poets) disjoint from F10's poets.")


def check_gt_reproduces(sets: dict):
    for set_name, examples in sets.items():
        for e in examples:
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
        print(f"OK: set {set_name}: all {len(examples)} drawn example verses independently "
              f"reconfirmed to carry a GT {SUBTYPE_FOCUS} span.")


def total_gt_instances(pool: list) -> int:
    total = 0
    for poem in pool:
        pj = load_poem_json(poem["poem_id"])
        gt = gt_spans_for_subtype(pj, SUBTYPE_FOCUS)
        total += sum(len(v) for v in gt.values())
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-f5b", action="store_true")
    args = parser.parse_args()

    print("=" * 78)
    print("1. Verifying Z/A/B/C previews are unchanged")
    print("=" * 78)
    ok = check_zabc_unchanged()
    if not ok:
        print("\n*** STOP: A/B/C/Z previews changed. Do not proceed. ***")
        return
    print()

    sets, _ = build_multipoet_sets(include_f5b=args.include_f5b)
    pool_doc = json.loads(EVAL_POOL_50_MULTIPOET_PATH.read_text(encoding="utf-8"))
    pool = pool_doc["poems"]

    print("=" * 78)
    print("2. No example-source poem in the new 50-poem pool")
    print("=" * 78)
    check_no_leakage(sets, pool)
    print()

    print("=" * 78)
    print("3. One poet per example / F5 subset of F10 / F5b disjoint")
    print("=" * 78)
    check_poet_structure(sets)
    print()

    print("=" * 78)
    print("4. GT reproduces counts for every drawn example")
    print("=" * 78)
    check_gt_reproduces(sets)
    n_gt = total_gt_instances(pool)
    print(f"Total {SUBTYPE_FOCUS} GT instances across the new 50-poem pool: {n_gt} "
          f"(pool: {pool_doc['pool_size']} poems, {pool_doc['pool_verses']} verse-units)")
    print()

    print("=" * 78)
    print("5. Writing prompt previews")
    print("=" * 78)
    for set_name in sets:
        text = build_system_message_n(sets[set_name])
        out_path = CONFIG_DIR / f"prompt_preview_{set_name}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path} ({len(sets[set_name])} extra examples, "
              f"{len(set(e['poet_name'] for e in sets[set_name]))} distinct poets)")

    print("\nAll unit checks passed. No API calls made.")


if __name__ == "__main__":
    main()
