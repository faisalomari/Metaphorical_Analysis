"""Supervisor deliverable 2: an illustrative, NOT-scored variant of
v4_combined that adds a required one-sentence Arabic "reason" field per
positive decision. The ELEMENT DEFINITIONS system message is v4_combined,
completely unchanged (build_system_message_variant("v4_combined")) - only
the analysis-instructions schema (in the user message) is extended.
"""
from config import POEMS, ACTIVE_POEM

ANALYSIS_INSTRUCTIONS_WITH_REASON = """================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze each verse INDIVIDUALLY for the existence of ONLY the 4 elements above.

Return JSONL ONLY.
One JSON object per verse.
No text before or after.

Schema (MUST MATCH EXACTLY):
{
  "no": <integer>,
  "مجاز_exists": <true|false>,
  "مجاز_appearance": <string|null>,
  "مجاز_reason": <string|null>,
  "تشبيه_exists": <true|false>,
  "تشبيه_appearance": <string|null>,
  "تشبيه_reason": <string|null>,
  "كناية_exists": <true|false>,
  "كناية_appearance": <string|null>,
  "كناية_reason": <string|null>,
  "طباق_exists": <true|false>,
  "طباق_appearance": <string|null>,
  "طباق_reason": <string|null>
}

Rules:
- If *_exists is false -> *_appearance and *_reason MUST be null
- If *_exists is true -> *_appearance MUST be a literal substring from the verse
- If *_exists is true -> *_reason MUST be ONE sentence in Arabic explaining why this element applies here
- If ambiguous -> use TOKENS[i:j] (0-based whitespace tokens)
- Be conservative: if unsure -> exists=false
- Do NOT explain when exists=false (reason stays null)
- Do NOT add fields
- Do NOT merge verses
- Do NOT use markdown

--------------------------------
VERSES_BLOCK
--------------------------------
"""


def build_user_message_with_reason(poem_key: str = ACTIVE_POEM) -> str:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    return ANALYSIS_INSTRUCTIONS_WITH_REASON + "\n" + poem_text + "\n"


if __name__ == "__main__":
    print(build_user_message_with_reason("Imru2"))
