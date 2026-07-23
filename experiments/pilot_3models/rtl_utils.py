"""Shared RTL/bidi helpers for every .docx builder in this project.

Rules (see PROJECT_STATE.md / session record for the full spec):
- Arabic text is always stored in logical order; never reversed, never
  patched with manual bidi control characters. Direction is a paragraph
  property (<w:bidi/> in pPr) plus a run property (<w:rtl/> in rPr) -
  never a table-level bidiVisual flag unless explicitly requested.
- Each paragraph's direction is decided independently by whether its own
  text is majority-Arabic (heuristic: >50% of non-whitespace characters
  fall in the Arabic Unicode blocks). Latin-majority paragraphs stay LTR
  even if they embed an isolated Arabic word or two - Word's Unicode bidi
  algorithm handles that case correctly on its own; it is majority-Arabic
  paragraphs defaulting to LTR that actually breaks verse/phrase ordering.
"""
import re

from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ARABIC_RE = re.compile(
    "[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]"
)


def is_majority_arabic(text: str) -> bool:
    stripped = re.sub(r"\s", "", text or "")
    if not stripped:
        return False
    arabic_chars = len(ARABIC_RE.findall(stripped))
    return arabic_chars / len(stripped) > 0.5


def set_paragraph_rtl(paragraph, rtl: bool = True) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    existing = pPr.find(qn("w:bidi"))
    if rtl and existing is None:
        pPr.append(OxmlElement("w:bidi"))
    elif not rtl and existing is not None:
        pPr.remove(existing)


def set_run_rtl(run, rtl: bool = True) -> None:
    rPr = run._r.get_or_add_rPr()
    existing = rPr.find(qn("w:rtl"))
    if rtl and existing is None:
        rPr.append(OxmlElement("w:rtl"))
    elif not rtl and existing is not None:
        rPr.remove(existing)


def apply_paragraph_direction(paragraph, text: str = None) -> bool:
    """Inspect (or use the given override) text, set bidi/rtl on the
    paragraph and every one of its runs accordingly. Returns whether RTL
    was applied, so callers needing the per-paragraph decision can reuse
    it without recomputing."""
    if text is None:
        text = paragraph.text
    rtl = is_majority_arabic(text)
    set_paragraph_rtl(paragraph, rtl)
    for run in paragraph.runs:
        set_run_rtl(run, rtl)
    return rtl
