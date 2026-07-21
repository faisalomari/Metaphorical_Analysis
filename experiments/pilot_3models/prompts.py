from config import ELEMENT_ORDER, ELEMENT_FILES, ELEMENTS_DIR, POEMS, ACTIVE_POEM

SYSTEM_HEADER = """You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
ELEMENT DEFINITIONS (REFERENCE)
================================
Below are EXACTLY 4 rhetorical elements. Learn them deeply using ONLY the
definitions and examples provided here. Do NOT use outside knowledge. Build
your internal detection rules from these examples. You will apply these
definitions to the poem given in the user's message.

--------------------------------
ELEMENTS_BLOCK
--------------------------------
"""

ANALYSIS_INSTRUCTIONS = """================================
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
- Do NOT merge verses
- Do NOT use markdown

--------------------------------
VERSES_BLOCK
--------------------------------
"""


def build_system_message() -> str:
    chunks = [SYSTEM_HEADER]
    for name in ELEMENT_ORDER:
        text = (ELEMENTS_DIR / ELEMENT_FILES[name]).read_text(encoding="utf-8").strip()
        chunks.append(text)
    return "\n\n".join(chunks).rstrip() + "\n"


def build_user_message(poem_key: str = ACTIVE_POEM) -> str:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    return ANALYSIS_INSTRUCTIONS + "\n" + poem_text + "\n"


if __name__ == "__main__":
    print(build_system_message())
    print(build_user_message())
