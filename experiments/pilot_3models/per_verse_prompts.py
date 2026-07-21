"""Per-verse granularity experiment (PROJECT_STATE.md §3g, NEW).

Mode A: v4_combined system prompt unchanged; user message = ONE verse, with
the analysis instructions minimally adapted for single-verse phrasing (same
JSON schema, one object returned instead of JSONL).

Mode B: reuses §3f's decomposed single-element system messages AND analysis
instructions UNCHANGED (build_system_message_decomposed /
ANALYSIS_INSTRUCTIONS_SINGLE_TEMPLATE) - only the user message's poem text is
replaced with a single verse.
"""
from config import POEMS, ACTIVE_POEM
from decompose_prompts import ANALYSIS_INSTRUCTIONS_SINGLE_TEMPLATE, ELEMENT_AR

ANALYSIS_INSTRUCTIONS_MODE_A = """================================
ANALYSIS PHASE (OUTPUT REQUIRED)
================================
Analyze the SINGLE verse below for the existence of ONLY the 4 elements above.

Return ONE JSON object only, for this verse.
No text before or after.

Schema (MUST MATCH EXACTLY):
{
  "no": <integer>,
  "مجاز_exists": <true|false>,
  "مجاز_appearance": <string|null>,
  "تشبيه_exists": <true|false>,
  "تشبيه_appearance": <string|null>,
  "كناية_exists": <true|false>,
  "كناية_appearance": <string|null>,
  "طباق_exists": <true|false>,
  "طباق_appearance": <string|null>
}

Rules:
- If *_exists is false -> *_appearance MUST be null
- If *_exists is true -> *_appearance MUST be a literal substring from the verse
- If ambiguous -> use TOKENS[i:j] (0-based whitespace tokens)
- Be conservative: if unsure -> exists=false
- Do NOT explain
- Do NOT add fields
- Do NOT use markdown

--------------------------------
VERSE
--------------------------------
"""


def get_verses(poem_key: str = ACTIVE_POEM) -> list:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    return [ln for ln in poem_text.split("\n") if ln.strip()]


def build_user_message_mode_a(verse_line: str) -> str:
    return ANALYSIS_INSTRUCTIONS_MODE_A + "\n" + verse_line + "\n"


def build_user_message_mode_b(element: str, verse_line: str) -> str:
    instructions = ANALYSIS_INSTRUCTIONS_SINGLE_TEMPLATE.format(ar=ELEMENT_AR[element])
    return instructions + "\n" + verse_line + "\n"


if __name__ == "__main__":
    verses = get_verses("Imru2")
    print(f"{len(verses)} verses")
    print("--- mode A example (verse 5) ---")
    print(build_user_message_mode_a(verses[4]))
    print("--- mode B example (Kenning, verse 5) ---")
    print(build_user_message_mode_b("Kenning", verses[4]))
