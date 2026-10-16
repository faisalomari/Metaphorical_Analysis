"""Shared data loading for Phase 5 (local fine-tuning). Reads directly from
data/ali_poems/poems/*.json (same corpus as phase4_e1_v2, the Dr. Ali Hussein
scrape) — a fresh, self-contained loader (phase4_e1*/pilot_3models are frozen,
not edited, per CLAUDE.md / task instructions), but reuses
pilot_3models.ground_truth.SUBSTRING_MAP unmodified for the 4-parent-element
mapping so Phase 5's "parent element" counts use the exact same Trope/Simile/
Kenning/Antonymy <-> مجاز+استعارة/تشبيه/كناية/طباق convention as every other
frozen number in this project, rather than inventing a second mapping.

A verse is "positive" for a subtype/element if >=1 annotation of that type
has its (comma-separated) verse_index's FIRST entry equal to that verse —
the same convention phase4_e1_v2/gt_v2.py and phase4_e1's ali_poems_io.py
already use and that the scraper's own validation pass confirmed reproduces
the frozen xlsx row counts exactly (SESSION_LOG.md 2026-10-10T04:35).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALI_POEMS_DIR = ROOT / "data" / "ali_poems" / "poems"
PILOT_DIR = ROOT / "experiments" / "pilot_3models"

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from ground_truth import SUBSTRING_MAP  # noqa: E402  (Trope/Simile/Kenning/Antonymy -> substrings)

PARENT_ORDER = ["Trope", "Simile", "Kenning", "Antonymy"]
PARENT_AR = {"Trope": "مجاز", "Simile": "تشبيه", "Kenning": "كناية", "Antonymy": "طباق"}

NO_TEXT_POEM_ID = "28601"  # zero word-level text on the source site (README.md) — always excluded


def list_poem_files(exclude=(NO_TEXT_POEM_ID,)):
    exclude = set(exclude)
    files = sorted(ALI_POEMS_DIR.glob("*.json"))
    return [f for f in files if f.name.split("_", 1)[0] not in exclude]


def load_poem(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_poems(exclude=(NO_TEXT_POEM_ID,)) -> list:
    return [load_poem(f) for f in list_poem_files(exclude=exclude)]


def verse_texts(poem: dict) -> dict:
    """{verse_no: text}"""
    return {v["verse_index"]: v["text"] for v in poem["verses"]}


def annotation_verse_no(a: dict, n_verses: int):
    """First verse index of a (possibly multi-verse-span) annotation, or None if out of range."""
    try:
        verse_no = int(str(a["verse_index"]).split(",")[0])
    except (ValueError, KeyError):
        return None
    if 1 <= verse_no <= n_verses:
        return verse_no
    return None


def positive_verses_by_subtype(poem: dict) -> dict:
    """{exact_subtype_string: set(verse_no)} for every subtype that appears in this poem."""
    n_verses = poem["verse_count"]
    out = {}
    for a in poem.get("annotations", []):
        subtype = a.get("subtype")
        if not subtype:
            continue
        verse_no = annotation_verse_no(a, n_verses)
        if verse_no is None:
            continue
        out.setdefault(subtype, set()).add(verse_no)
    return out


def positive_verses_by_parent(poem: dict) -> dict:
    """{parent_name (Trope/Simile/Kenning/Antonymy): set(verse_no)}, via SUBSTRING_MAP
    on "{element} {subtype}" — identical convention to pilot_3models/audit_ground_truth.py
    and phase4_e1's ali_poems_io.load_ali_gt_spans."""
    n_verses = poem["verse_count"]
    out = {name: set() for name in PARENT_ORDER}
    for a in poem.get("annotations", []):
        verse_no = annotation_verse_no(a, n_verses)
        if verse_no is None:
            continue
        labels = f"{a.get('element', '')} {a.get('subtype', '')}"
        for name, substrings in SUBSTRING_MAP.items():
            if any(s in labels for s in substrings):
                out[name].add(verse_no)
    return out


def label_for_target(poem: dict, target: dict) -> dict:
    """{verse_no: 0/1} for one target spec, over ALL verses 1..n (not just positives).
    target = {"kind": "subtype", "value": "استعارة فعل"} or {"kind": "parent", "value": "Trope"}."""
    n_verses = poem["verse_count"]
    if target["kind"] == "subtype":
        pos = positive_verses_by_subtype(poem).get(target["value"], set())
    elif target["kind"] == "parent":
        pos = positive_verses_by_parent(poem).get(target["value"], set())
    else:
        raise ValueError(f"unknown target kind: {target['kind']}")
    return {no: int(no in pos) for no in range(1, n_verses + 1)}
