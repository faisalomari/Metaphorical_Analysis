"""Shared helpers for the IAA scripts. Read-only with respect to the rest of
the repo: imports `experiments/pilot_3models` modules (config, ground_truth,
span_matching) rather than duplicating their logic, and never writes outside
`writing/paper_plan/iaa/`.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
IAA_DIR = ROOT / "writing" / "paper_plan" / "iaa"

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))

import config  # noqa: E402  (pilot_3models module, path injected above)
import ground_truth  # noqa: E402

VERSE_LINE_RE = re.compile(r'^\s*(\d+)\)\s*"+(.*?)"+\s*$')


def load_poem_verses(poem_key: str) -> dict:
    """Returns {verse_no: verse_text} for a poem, parsed from its poetry.txt.

    Handles both the single-quote convention (most poems) and Imru1's
    doubled-quote convention (see PROJECT_STATE.md Phase 1 §3i note) by
    stripping any run of trailing/leading double-quote characters.
    """
    path = config.POEMS[poem_key]["poetry_path"]
    verses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        m = VERSE_LINE_RE.match(line)
        if not m:
            continue
        verses[int(m.group(1))] = m.group(2).strip()
    return verses


def load_ground_truth_for_poem(poem_key: str) -> dict:
    """Returns {verse_no: {element: [span, ...]}} - just the span strings,
    dropping the subtype dict wrapper from ground_truth.load_ground_truth_spans."""
    raw = ground_truth.load_ground_truth_spans(poem_key)
    out = {}
    for no, by_el in raw.items():
        out[no] = {el: [item["span"] for item in by_el[el] if item["span"]] for el in config.ELEMENT_ORDER}
    return out


POEM_AR_SHORT = {
    "Imru1": "امرؤ القيس - قصيدة 1",
    "Imru2": "امرؤ القيس - قصيدة 8",
    "Nabigha": "النابغة الذبياني",
    "Jarir": "جرير",
    "Abu_Tammam": "أبو تمام",
}

# Corrected terminology (GLOSSARY.md) for all new writing produced by this task.
# Arabic term stays primary (Dr. Hussein reads Arabic natively); English is the
# corrected post-2026-07-23 name, with the old Phase-1 name noted once in the
# instruction sheet only, to avoid any ambiguity for readers who only know the
# superseded English terms.
ELEMENT_LABELS = {
    "Trope": {"ar": "مجاز", "en": "Trope"},
    "Simile": {"ar": "تشبيه", "en": "Simile"},
    "Kenning": {"ar": "كناية", "en": "Periphrasis"},
    "Antonymy": {"ar": "طباق", "en": "Antithesis"},
}
