"""Per-element decomposition experiment (PROJECT_STATE.md item 5a, DEV only).

Splits v4_combined into 4 single-element prompts: each keeps only that
element's definition and only the v4 rule content that's actually about that
element, rewritten so it doesn't require the model to also classify the
element it used to be contrasted against. The output schema is reduced to
that element's 2 fields. Wording is otherwise identical to v4_combined.

Adaptation notes (see module docstring in prompt_variants.py for the original
rules):
  - RULE_1_BOUNDARY (Trope vs Kenning) is inherently comparative. Kept for
    Trope-only and Kenning-only, each rewritten as a one-directional
    "don't mark X if <the other element's condition> holds" rule plus a
    counter-example, so it's usable without the other element's full
    definition block. Not applicable to Simile/Antonymy -> dropped there.
  - RULE_2_MARKER_INDEPENDENCE (simile particle isn't evidence for Trope) is
    kept, adapted, for Trope-only and Kenning-only (both were the targets of
    that rule). Dropped for Simile (the rule was never about Simile itself)
    and Antonymy (unrelated).
  - RULE_3_MULTI_FIGURE ("check all 4 elements independently") is structurally
    moot under decomposition: each call already isolates one element, so
    there's nothing left to independently re-check. Dropped for all 4.
"""
from config import ELEMENT_ORDER, ELEMENT_AR, ELEMENT_FILES, ELEMENTS_DIR, POEMS, ACTIVE_POEM

SYSTEM_HEADER_SINGLE = """You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
ELEMENT DEFINITION (REFERENCE)
================================
Below is EXACTLY 1 rhetorical element. Learn it deeply using ONLY the
definition and examples provided here. Do NOT use outside knowledge. Build
your internal detection rules from these examples. You will apply this
definition to the poem given in the user's message.

--------------------------------
ELEMENT_BLOCK
--------------------------------
"""

TROPE_BOUNDARY_SINGLE = """
--------------------------------
ADDITIONAL RULE: Trope vs. a merely indirect expression
--------------------------------
Trope (مجاز) requires that the literal meaning is IMPOSSIBLE or clearly
rejected by context - only the figurative sense works. This includes a VERB
whose action is applied non-literally (e.g. a day "fading away" as if dying,
an emotion "seizing/enslaving" someone as if physically), not only
noun-based figures.

Do NOT mark something as Trope if the literal reading remains a plausible,
possible meaning alongside the figurative one - that is a different, more
indirect figure of speech, out of scope here, and NOT Trope. Only mark Trope
when the literal sense is rejected.

Worked example: "تَسْتَبِيكَ" ("captivates you") -> Trope: a verb describing
physical capture/slavery applied to a feeling; the literal act of enslaving
cannot be meant.
Counter-example (NOT Trope): "بِواضِحٍ" ("radiant/bright [smile]") in the same
verse - it could still literally describe brightness while indirectly
conveying beauty. Do not mark this kind of case as Trope.
"""

TROPE_MARKER_INDEPENDENCE_SINGLE = """
--------------------------------
ADDITIONAL RULE: evaluate Trope on its own evidence
--------------------------------
The presence of an explicit comparison particle (كأن، كما، ك، مثل) is
evidence for a different figure (simile), NOT for Trope. Do not let a
simile-particle phrase by itself satisfy your check for Trope. Re-read the
verse independently using ONLY Trope's own definition and evidence above
before deciding exists=false.
"""

KENNING_BOUNDARY_SINGLE = """
--------------------------------
ADDITIONAL RULE: Kenning vs. a stronger figurative substitution
--------------------------------
Kenning (كناية) requires that the literal meaning remains a POSSIBLE,
plausible reading - the speaker could mean it literally, even if the
phrasing is unusual. The figurative meaning is implied ALONGSIDE the literal
one, not instead of it.

Do NOT mark something as Kenning if the literal meaning is IMPOSSIBLE or
clearly rejected by context - that is a different, stronger figure of
speech, out of scope here, and NOT Kenning. Only mark Kenning when the
literal sense remains plausible.

Worked example: "بِواضِحٍ" ("radiant/bright [smile]") -> Kenning: it could
still literally describe brightness, while indirectly conveying beauty.
Counter-example (NOT Kenning): "تَسْتَبِيكَ" ("captivates you") in the same
verse - a verb describing physical capture/slavery applied to a feeling; the
literal act of enslaving cannot be meant, so this is NOT Kenning.
"""

KENNING_MARKER_INDEPENDENCE_SINGLE = """
--------------------------------
ADDITIONAL RULE: evaluate Kenning on its own evidence
--------------------------------
The presence of an explicit comparison particle (كأن، كما، ك، مثل) is
evidence for a different figure (simile), NOT for Kenning. Do not let a
simile-particle phrase by itself satisfy your check for Kenning. Re-read the
verse independently using ONLY Kenning's own definition and evidence above
before deciding exists=false.
"""

SINGLE_ELEMENT_RULES = {
    "Trope": [TROPE_BOUNDARY_SINGLE, TROPE_MARKER_INDEPENDENCE_SINGLE],
    "Kenning": [KENNING_BOUNDARY_SINGLE, KENNING_MARKER_INDEPENDENCE_SINGLE],
    "Simile": [],
    "Antonymy": [],
}

ANALYSIS_INSTRUCTIONS_SINGLE_TEMPLATE = """================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze each verse INDIVIDUALLY for the existence of ONLY the 1 element above.

Return JSONL ONLY.
One JSON object per verse.
No text before or after.

Schema (MUST MATCH EXACTLY):
{{
  "no": <integer>,
  "{ar}_exists": <true|false>,
  "{ar}_appearance": <string|null>
}}

Rules:
- If *_exists is false -> *_appearance MUST be null
- If *_exists is true -> *_appearance MUST be a literal substring from the verse
- If ambiguous -> use TOKENS[i:j] (0-based whitespace tokens)
- Be conservative: if unsure -> exists=false
- Do NOT explain
- Do NOT add fields
- Do NOT merge verses
- Do NOT use markdown

--------------------------------
VERSES_BLOCK
--------------------------------
"""


def build_system_message_decomposed(element: str) -> str:
    text = (ELEMENTS_DIR / ELEMENT_FILES[element]).read_text(encoding="utf-8").strip()
    chunks = [SYSTEM_HEADER_SINGLE, text]
    chunks.extend(rule.strip() for rule in SINGLE_ELEMENT_RULES[element])
    return "\n\n".join(chunks).rstrip() + "\n"


def build_user_message_decomposed(element: str, poem_key: str = ACTIVE_POEM) -> str:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    ar = ELEMENT_AR[element]
    instructions = ANALYSIS_INSTRUCTIONS_SINGLE_TEMPLATE.format(ar=ar)
    return instructions + "\n" + poem_text + "\n"


if __name__ == "__main__":
    for element in ELEMENT_ORDER:
        msg = build_system_message_decomposed(element)
        print(f"=== {element} system message ({len(msg)} chars) ===")
        print(msg)
        print()
