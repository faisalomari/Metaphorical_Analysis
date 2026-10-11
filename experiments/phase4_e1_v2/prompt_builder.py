"""Builds the system/user message pair for sets Z/A/B/C, all on top of
experiments/phase3_subelements's subtype-level prompt (not pilot_3models's
old whole-poem prompt — that is the whole point of the v2 rebuild).

- Set Z: subtype_prompts.SYSTEM_TEMPLATE unmodified (1 example only — the
  original definition example from subtype_defs). The zero-extra-examples
  baseline.
- Sets A/B/C: fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT, with Example 1 = the
  same original definition example, and Example 2/3 = the 2 example verses
  from phase4_e1 (v1)'s config/example_sets.json for that set (same 3 sets,
  same seed=42 draw — reused unchanged, not redrawn).

Per set, only Example 2/3 differ between A/B/C — everything else (scaffold,
Example 1, ANALYSIS_INSTRUCTIONS) is byte-identical across the 3 sets.

User message (all 4 sets): subtype_prompts.ANALYSIS_INSTRUCTIONS filled with
ONE verse's text (one call = one verse-unit, not a whole poem).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_EXAMPLE_SETS_PATH, PHASE3_DIR, SUBTYPE_FOCUS  # noqa: E402

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))
from subtype_defs import SUBTYPE_DEFS  # noqa: E402
from subtype_prompts import SYSTEM_TEMPLATE, ANALYSIS_INSTRUCTIONS  # noqa: E402
from fewshot_prompts import SYSTEM_TEMPLATE_FEWSHOT  # noqa: E402


def load_v1_example_sets() -> dict:
    return json.loads(E1V1_EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))


def _format_example_verse(example: dict) -> dict:
    """v1's example_sets.json example -> {"verse_text", "note"} for one
    fewshot slot. An example verse may carry >1 annotation span (e.g. set B's
    verse 4 has 3) — joined into one note, since fewshot_prompts.
    SYSTEM_TEMPLATE_FEWSHOT has exactly one note slot per example verse."""
    parts = []
    for a in example["annotations"]:
        span = a.get("span", "")
        note = a.get("analysis", "")
        piece = f"the sub-element appears at «{span}»" if span else "the sub-element is present in this verse"
        if note:
            piece += f" — {note}"
        parts.append(piece)
    return {"verse_text": example["text"], "note": "; ".join(parts) if parts else "the sub-element is present in this verse"}


def build_system_message(set_name: str) -> str:
    d = SUBTYPE_DEFS[SUBTYPE_FOCUS]
    if set_name == "Z":
        return SYSTEM_TEMPLATE.format(
            parent=d["parent"], name=SUBTYPE_FOCUS, definition_ar=d["definition_ar"], example=d["example"],
        )
    v1_sets = load_v1_example_sets()
    ex2, ex3 = (_format_example_verse(e) for e in v1_sets[set_name]["examples"])
    return SYSTEM_TEMPLATE_FEWSHOT.format(
        parent=d["parent"], name=SUBTYPE_FOCUS, definition_ar=d["definition_ar"], example=d["example"],
        ex2_verse=ex2["verse_text"], ex2_note=ex2["note"],
        ex3_verse=ex3["verse_text"], ex3_note=ex3["note"],
    )


def build_user_message(verse_text: str) -> str:
    return ANALYSIS_INSTRUCTIONS.format(verse=verse_text)


def build_messages(set_name: str, verse_text: str) -> tuple:
    return build_system_message(set_name), build_user_message(verse_text)


if __name__ == "__main__":
    import difflib

    for name in ["Z", "A", "B", "C"]:
        print(f"\n{'=' * 70}\nSET {name} — full rendered system message\n{'=' * 70}")
        print(build_system_message(name))

    print(f"\n{'=' * 70}\nDIFF A vs B (system message)\n{'=' * 70}")
    a_lines = build_system_message("A").splitlines(keepends=True)
    b_lines = build_system_message("B").splitlines(keepends=True)
    print("".join(difflib.unified_diff(a_lines, b_lines, fromfile="A", tofile="B")))

    print(f"\n{'=' * 70}\nDIFF A vs C (system message)\n{'=' * 70}")
    c_lines = build_system_message("C").splitlines(keepends=True)
    print("".join(difflib.unified_diff(a_lines, c_lines, fromfile="A", tofile="C")))
