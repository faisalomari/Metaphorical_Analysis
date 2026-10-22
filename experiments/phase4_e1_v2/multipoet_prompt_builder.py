"""Generalizes prompt_builder.py's fewshot template from exactly 2 extra
examples (Sets A/B/C) to N extra examples (Sets F5/F10/F5b), same scaffold,
same per-example line format ("Example i (from the annotated corpus -
verse: ...): ..."), Example 1 unchanged (the original single definition
example from subtype_defs). Does NOT edit prompt_builder.py, fewshot_prompts.py,
or subtype_prompts.py -- those stay byte-identical (verified by
preview_and_diff_multipoet.py, same convention as Set D's
preview_and_diff_D.py). Reuses prompt_builder._format_example_verse
unchanged for per-example note formatting.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import PHASE3_DIR, SUBTYPE_FOCUS  # noqa: E402
from prompt_builder import _format_example_verse  # noqa: E402

if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))
from subtype_defs import SUBTYPE_DEFS  # noqa: E402
from subtype_prompts import ANALYSIS_INSTRUCTIONS  # noqa: E402

HEADER_TEMPLATE = """You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
SUB-ELEMENT DEFINITION (REFERENCE)
================================
Below is EXACTLY ONE rhetorical sub-element (a specific branch of a broader
Arabic rhetorical element). Learn it deeply using ONLY the definition and
the {n_total} examples given here. Do NOT use outside knowledge, and do NOT confuse
it with sibling sub-elements under the same parent element. You will apply
this definition to ONE verse given in the user's message.

--------------------------------
SUB-ELEMENT
--------------------------------
Parent element: {parent}
Arabic name: {name}
Definition (Arabic): {definition_ar}

Example 1: {example}
"""


def build_system_message_n(extra_examples: list) -> str:
    """extra_examples: list of v1-style example dicts (each with "text" and
    "annotations", as produced by multipoet_examples.draw_examples / the
    v1 example_sets.json shape) -- Example 2, 3, ..., len(extra_examples)+1,
    in the given order (the SAME order they were drawn in, never re-sorted)."""
    d = SUBTYPE_DEFS[SUBTYPE_FOCUS]
    n_total = len(extra_examples) + 1
    parts = [HEADER_TEMPLATE.format(
        n_total=n_total, parent=d["parent"], name=SUBTYPE_FOCUS,
        definition_ar=d["definition_ar"], example=d["example"],
    )]
    for i, ex_raw in enumerate(extra_examples, start=2):
        ex = _format_example_verse({"text": ex_raw["text"], "annotations": ex_raw["annotations"]})
        parts.append(f"\nExample {i} (from the annotated corpus - verse: {ex['verse_text']}): {ex['note']}\n")
    return "".join(parts)


def build_user_message(verse_text: str) -> str:
    return ANALYSIS_INSTRUCTIONS.format(verse=verse_text)


def build_messages_n(extra_examples: list, verse_text: str) -> tuple:
    return build_system_message_n(extra_examples), build_user_message(verse_text)


if __name__ == "__main__":
    import json
    from multipoet_config import MULTIPOET_EXAMPLE_SETS_PATH

    doc = json.loads(MULTIPOET_EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))
    for set_name in ["F5", "F10"]:
        print(f"\n{'=' * 70}\nSET {set_name} — full rendered system message\n{'=' * 70}")
        msg = build_system_message_n(doc["sets"][set_name])
        print(msg)
