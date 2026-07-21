"""Prompt variants targeting the confirmed failure modes from the DEV error
analysis (Imru2 + Nabigha): Trope<->Kenning boundary confusion, simile-marker
anchoring on Trope spans, and multi-figure verses. Each variant only changes
the SYSTEM message (element definitions + added rules); the analysis
instructions/schema and the poem/user message are unchanged, for a clean
ablation.
"""
from config import ELEMENT_ORDER, ELEMENT_FILES, ELEMENTS_DIR
from prompts import SYSTEM_HEADER

RULE_1_BOUNDARY = """
--------------------------------
ADDITIONAL RULE: Trope vs. Kenning boundary
--------------------------------
Kenning (كناية): the literal meaning remains a POSSIBLE, plausible reading -
the speaker could mean it literally, even if the phrasing is unusual. The
figurative meaning is implied ALONGSIDE the literal one, not instead of it.

Trope (مجاز): the literal meaning is IMPOSSIBLE or clearly rejected by
context - only the figurative sense works. This includes a VERB whose action
is applied non-literally (e.g. a day "fading away" as if dying, an emotion
"seizing/enslaving" someone as if physically) - not only noun-based figures.

Worked contrast (same verse, two different verdicts):
  "تَسْتَبِيكَ" ("captivates you") -> Trope: a verb describing physical capture/
  slavery applied to a feeling; the literal act of enslaving cannot be meant.
  "بِواضِحٍ" ("radiant/bright [smile]") in the same verse -> Kenning: it could
  still literally describe brightness, while indirectly conveying beauty.
"""

RULE_2_MARKER_INDEPENDENCE = """
--------------------------------
ADDITIONAL RULE: evaluate each element on its own evidence
--------------------------------
The presence of an explicit comparison particle (كأن، كما، ك، مثل) is
evidence for SIMILE specifically - it is NOT evidence for Trope, and it does
NOT mean you have finished checking the verse. A verse containing an
explicit simile may ALSO separately contain a different word or verb used
figuratively (Trope) or indirectly (Kenning) elsewhere in the same verse.
Do not let a simile-particle phrase satisfy your check for a different
element. Re-read the verse independently for each of the 4 elements' own
definition and evidence before deciding exists=false.
"""

RULE_3_MULTI_FIGURE = """
--------------------------------
ADDITIONAL RULE: verses can contain multiple elements
--------------------------------
A single verse can contain more than one of these 4 elements at the same
time, and can contain more than one instance of the SAME element. Check ALL
4 elements independently for every verse, regardless of what you already
found for other elements in that verse.
"""

VARIANTS = {
    "baseline": [],
    "v1_boundary": [RULE_1_BOUNDARY],
    "v2_marker_independence": [RULE_2_MARKER_INDEPENDENCE],
    "v3_multi_figure": [RULE_3_MULTI_FIGURE],
    "v4_combined": [RULE_1_BOUNDARY, RULE_2_MARKER_INDEPENDENCE, RULE_3_MULTI_FIGURE],
    "v1_v2": [RULE_1_BOUNDARY, RULE_2_MARKER_INDEPENDENCE],
    "v1_v3": [RULE_1_BOUNDARY, RULE_3_MULTI_FIGURE],
}


def build_system_message_variant(variant_key: str) -> str:
    chunks = [SYSTEM_HEADER]
    for name in ELEMENT_ORDER:
        text = (ELEMENTS_DIR / ELEMENT_FILES[name]).read_text(encoding="utf-8").strip()
        chunks.append(text)
    chunks.extend(RULE.strip() for RULE in VARIANTS[variant_key])
    return "\n\n".join(chunks).rstrip() + "\n"


if __name__ == "__main__":
    for key in VARIANTS:
        msg = build_system_message_variant(key)
        print(f"=== {key} ({len(msg)} chars) ===")
