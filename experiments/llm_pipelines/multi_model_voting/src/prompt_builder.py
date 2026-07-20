from __future__ import annotations

from pathlib import Path


BANDED_CONFIDENCE_PROVIDERS = {"gemini", "command_a", "aya", "qwen"}


def load_element_definition(element: str, elements_dir: Path) -> str:
    element_path = elements_dir / f"{element}.txt"
    if not element_path.exists():
        raise FileNotFoundError(f"Element definition file not found: {element_path}")
    return element_path.read_text(encoding="utf-8").strip()


def load_system_prompt(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_labeling_user_prompt(
    verse: str,
    element: str,
    definition: str,
    provider: str | None = None,
) -> str:
    if provider in BANDED_CONFIDENCE_PROVIDERS:
        return f"""
Task:
Determine whether the following Arabic verse contains the rhetorical element:
**{element}**

Definition:
{definition}

Rules (VERY IMPORTANT):
- Output MUST be valid JSON
- Output ONLY JSON
- NO explanations outside JSON
- NO markdown
- NO comments
- Judge ONLY the requested rhetorical element
- Use label "yes" if the element is present, otherwise "no"
- If label is "no", span MUST be an empty string
- Use confidence_band from this exact set only:
  "very_low", "low", "medium", "high", "very_high"
- Reasoning must be short

JSON schema (exact keys):
{{
  "label": "yes" or "no",
  "span": "exact words from the verse" or "",
  "confidence_band": "very_low" or "low" or "medium" or "high" or "very_high",
  "reasoning": "very short explanation"
}}

Verse:
{verse}
""".strip()

    return f"""
Task:
Determine whether the following Arabic verse contains the rhetorical element:
**{element}**

Definition:
{definition}

Rules (VERY IMPORTANT):
- Output MUST be valid JSON
- Output ONLY JSON
- NO explanations outside JSON
- NO markdown
- NO comments
- Judge ONLY the requested rhetorical element
- Use label "yes" if the element is present, otherwise "no"
- If label is "no", span MUST be an empty string
- Confidence MUST be a number from 0 to 1
- Reasoning must be short

JSON schema (exact keys):
{{
  "label": "yes" or "no",
  "span": "exact words from the verse" or "",
  "confidence": 0.0,
  "reasoning": "very short explanation"
}}

Verse:
{verse}
""".strip()


def build_explanation_user_prompt(
    verse: str,
    element: str,
    definition: str,
    selected_label: str,
    selected_span: str,
) -> str:
    return f"""
المطلوب:
اكتب شرحًا عربيًا موجزًا ومفيدًا أكاديميًا عن وجود عنصر البلاغة المطلوب في البيت التالي.

العنصر البلاغي:
{element}

التعريف المرجعي:
{definition}

البيت:
{verse}

الحكم النهائي:
{selected_label}

الموضع المختار:
{selected_span if selected_span else "لا يوجد"}

التعليمات:
- أعد نصًا عربيًا فقط
- لا تستخدم تعدادًا نقطيًا
- إن كان الحكم "no" فاشرح باختصار سبب غياب العنصر
- إن كان الحكم "yes" ففسر كيف يدل الموضع المختار على هذا العنصر
""".strip()
