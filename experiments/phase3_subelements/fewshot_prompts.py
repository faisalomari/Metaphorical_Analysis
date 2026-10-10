"""Few-shot (3-shot) prompt builder: same structure as subtype_prompts.py,
but the SUB-ELEMENT block carries the original 1 example PLUS 2 more, drawn
from that subtype's own ground truth and held out of the test set (see
run_fewshot_check.py - ELIGIBLE_SUBTYPES / pick_fewshot_examples).
"""
from subtype_defs import SUBTYPE_DEFS

SYSTEM_TEMPLATE_FEWSHOT = """You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
SUB-ELEMENT DEFINITION (REFERENCE)
================================
Below is EXACTLY ONE rhetorical sub-element (a specific branch of a broader
Arabic rhetorical element). Learn it deeply using ONLY the definition and
the 3 examples given here. Do NOT use outside knowledge, and do NOT confuse
it with sibling sub-elements under the same parent element. You will apply
this definition to ONE verse given in the user's message.

--------------------------------
SUB-ELEMENT
--------------------------------
Parent element: {parent}
Arabic name: {name}
Definition (Arabic): {definition_ar}

Example 1: {example}

Example 2 (from the annotated corpus - verse: {ex2_verse}): {ex2_note}

Example 3 (from the annotated corpus - verse: {ex3_verse}): {ex3_note}
"""

# unchanged from subtype_prompts.ANALYSIS_INSTRUCTIONS
from subtype_prompts import ANALYSIS_INSTRUCTIONS


def _format_extra_example(row, span, explanation):
    note = f"the sub-element appears at «{span}»" if span else "the sub-element is present in this verse"
    if explanation:
        note += f" — {explanation}"
    return note


def build_messages_fewshot(subtype_key: str, verse_text: str, extra_examples: list) -> tuple:
    """extra_examples: list of 2 dicts, each {"verse_text", "span", "explanation"}."""
    d = SUBTYPE_DEFS[subtype_key]
    ex2, ex3 = extra_examples
    system = SYSTEM_TEMPLATE_FEWSHOT.format(
        parent=d["parent"], name=subtype_key, definition_ar=d["definition_ar"], example=d["example"],
        ex2_verse=ex2["verse_text"], ex2_note=_format_extra_example(ex2, ex2["span"], ex2["explanation"]),
        ex3_verse=ex3["verse_text"], ex3_note=_format_extra_example(ex3, ex3["span"], ex3["explanation"]),
    )
    user = ANALYSIS_INSTRUCTIONS.format(verse=verse_text)
    return system, user
