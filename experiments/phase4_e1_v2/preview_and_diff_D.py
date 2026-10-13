"""Step 1 for Set D (NO API calls).

1. Regenerates system messages for Z/A/B/C via prompt_builder.build_system_message
   and byte-diffs them against the already-committed config/prompt_preview_{Z,A,B,C}.txt
   -- proves adding D/D2 did not change A/B/C/Z's prompts.
2. Writes config/prompt_preview_D.txt (and _D2.txt with --include-d2).
3. Prints unified diffs of D vs A, D vs B, D vs C (only the Example 2/3 lines should differ).
4. Reports the note-completeness confound: how many of the 2 fewshot examples in each of
   A/B/C/D (and D2) carry a non-empty analysis note on every one of their spans.
"""
import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import CONFIG_DIR, SET_NAMES  # noqa: E402
from prompt_builder import build_system_message, load_v1_example_sets, _examples_for_set  # noqa: E402


def verify_unchanged() -> bool:
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


def note_completeness(set_name: str, v1_sets: dict) -> tuple:
    """(n_examples_with_full_notes, n_examples) for a set's 2 fewshot examples --
    'full notes' means every span annotation on that example verse has a non-empty
    'analysis' field."""
    ex2_raw, ex3_raw = _examples_for_set(set_name, v1_sets)
    examples = [ex2_raw, ex3_raw]
    full = sum(1 for e in examples if all(a.get("analysis", "") for a in e["annotations"]))
    return full, len(examples)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-d2", action="store_true")
    args = parser.parse_args()

    print("=" * 78)
    print("Verifying Z/A/B/C previews are unchanged by adding D (and D2)")
    print("=" * 78)
    ok = verify_unchanged()
    if not ok:
        print("\n*** STOP: A/B/C/Z previews changed. Do not proceed. ***")
        return
    print("\nAll 4 existing previews (Z/A/B/C) regenerate byte-identical. Safe to add D.\n")

    sets_to_build = ["D"] + (["D2"] if args.include_d2 else [])
    for name in sets_to_build:
        text = build_system_message(name)
        out_path = CONFIG_DIR / f"prompt_preview_{name}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"Wrote {out_path}")

    print("\n" + "=" * 78)
    print("DIFFS: set D vs A, B, C (system message)")
    print("=" * 78)
    d_text = build_system_message("D")
    d_lines = d_text.splitlines(keepends=True)
    for other in ["A", "B", "C"]:
        other_lines = build_system_message(other).splitlines(keepends=True)
        print(f"\n--- D vs {other} ---")
        diff = list(difflib.unified_diff(other_lines, d_lines, fromfile=other, tofile="D"))
        print("".join(diff) if diff else "(no diff -- unexpected, D should differ in examples)")

    if args.include_d2:
        print("\n" + "=" * 78)
        print("DIFFS: set D2 vs D, A, B, C (system message)")
        print("=" * 78)
        d2_lines = build_system_message("D2").splitlines(keepends=True)
        for other in ["D", "A", "B", "C"]:
            other_lines = build_system_message(other).splitlines(keepends=True)
            print(f"\n--- D2 vs {other} ---")
            diff = list(difflib.unified_diff(other_lines, d2_lines, fromfile=other, tofile="D2"))
            print("".join(diff) if diff else "(no diff)")

    print("\n" + "=" * 78)
    print("CONFOUND CHECK: analysis-note completeness per set's 2 fewshot examples")
    print("=" * 78)
    v1_sets = load_v1_example_sets()
    for name in ["A", "B", "C", "D"] + (["D2"] if args.include_d2 else []):
        full, total = note_completeness(name, v1_sets)
        print(f"  Set {name}: {full}/{total} examples have a non-empty analysis note on every span"
              + ("" if full == total else "  <-- at least one example has an unannotated span"))


if __name__ == "__main__":
    main()
