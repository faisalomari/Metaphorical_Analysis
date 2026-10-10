"""Builds the system/user message pair for a single (subtype, verse) check.

Follows the same conventions as Phase 1's decompose_prompts.py: system message
= element/subtype definition block only (no outside knowledge), user message
= single-verse analysis instructions with a small, strict JSON schema and a
conservative bias (exists=false when unsure) - the same bias direction used
throughout this project's prompting.
"""
from subtype_defs import SUBTYPE_DEFS

SYSTEM_TEMPLATE = """You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
SUB-ELEMENT DEFINITION (REFERENCE)
================================
Below is EXACTLY ONE rhetorical sub-element (a specific branch of a broader
Arabic rhetorical element). Learn it deeply using ONLY the definition and
example given here. Do NOT use outside knowledge, and do NOT confuse it with
sibling sub-elements under the same parent element. You will apply this
definition to ONE verse given in the user's message.

--------------------------------
SUB-ELEMENT
--------------------------------
Parent element: {parent}
Arabic name: {name}
Definition (Arabic): {definition_ar}
Example: {example}
"""

ANALYSIS_INSTRUCTIONS = """================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze the verse(s) below for the existence of ONLY the sub-element defined
above (not the broader parent element, not any other sub-element). Usually
there is one verse; occasionally there are two or more consecutive verses
because this specific rhetorical instance spans across them - treat them as
one unit and answer for the whole passage.

Return ONE JSON object only. No text before or after.

Schema (MUST MATCH EXACTLY):
{{
  "exists": <true|false>,
  "appearance": <string|null>,
  "reasoning": <string>
}}

Rules:
- If exists is false -> appearance MUST be null
- If exists is true -> appearance MUST be a literal substring from the text below
- reasoning is ALWAYS required (both when true and false): 1-3 sentences, in
  Arabic, explaining WHY the sub-element's definition does or does not match
  this text - reference the specific word(s)/phrase you based the decision on
- Be conservative: if unsure -> exists=false
- Do NOT add fields beyond the schema
- Do NOT use markdown

--------------------------------
VERSE(S)
--------------------------------
{verse}
"""


def build_messages(subtype_key: str, verse_text: str) -> tuple:
    d = SUBTYPE_DEFS[subtype_key]
    system = SYSTEM_TEMPLATE.format(
        parent=d["parent"], name=subtype_key, definition_ar=d["definition_ar"], example=d["example"],
    )
    user = ANALYSIS_INSTRUCTIONS.format(verse=verse_text)
    return system, user


if __name__ == "__main__":
    s, u = build_messages("كناية عن صفة", "طويل النجاد رفيع العماد كثير الرماد إذا ما شتا")
    print(s)
    print(u)
