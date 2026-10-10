"""Load poems + ground truth directly from data/ali_poems/poems/*.json
(the Dr. Ali Hussein corpus scrape), reusing experiments/pilot_3models's own
element-mapping convention (SUBSTRING_MAP) for consistency with every frozen
Phase 1-3 number, rather than reimplementing the mapping differently.
"""
import csv
import json
import sys
from pathlib import Path

from e1_config import ALI_MANIFEST_PATH, ALI_POEMS_JSON_DIR, PILOT_DIR

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))

from ground_truth import SUBSTRING_MAP  # noqa: E402
from config import ELEMENT_ORDER  # noqa: E402


def load_manifest() -> list:
    with open(ALI_MANIFEST_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_poem_json(poem_id) -> dict:
    poem_id = str(poem_id)
    matches = list(ALI_POEMS_JSON_DIR.glob(f"{poem_id}_*.json"))
    if not matches:
        raise FileNotFoundError(f"no poem json for poem_id={poem_id}")
    return json.loads(matches[0].read_text(encoding="utf-8"))


def build_poem_text(poem_json: dict) -> str:
    """Verse-numbered plain text, same shape as archive/Forth_Step/Data/*/poetry.txt
    (one verse per line, sadr<tab-width spaces>ajuz), ordered by verse_index."""
    verses = sorted(poem_json["verses"], key=lambda v: v["verse_index"])
    return "\n".join(v["text"] for v in verses).strip() + "\n"


def load_ali_gt_spans(poem_json: dict) -> dict:
    """Returns {verse_no: {element: [{"span": str, "subtype": str}, ...]}},
    same output shape as pilot_3models.ground_truth.load_ground_truth_spans.

    An annotation's verse number is the first entry of its comma-separated
    verse_index field (the verse the span's first word belongs to) — matches
    how this project's own scraper-validation (SESSION_LOG.md 2026-10-10T04:35)
    reconciled exact per-poem annotation counts against the frozen xlsx ground
    truth via the same convention (colomn / verse_index first token).
    """
    n_verses = poem_json["verse_count"]
    gt = {no: {name: [] for name in ELEMENT_ORDER} for no in range(1, n_verses + 1)}
    seen = set()
    for a in poem_json["annotations"]:
        verse_no = int(str(a["verse_index"]).split(",")[0])
        if not (1 <= verse_no <= n_verses):
            continue
        labels = f"{a.get('element', '')} {a.get('subtype', '')}"
        span = (a.get("span_text") or "").strip()
        for name, substrings in SUBSTRING_MAP.items():
            if any(s in labels for s in substrings):
                key = (verse_no, name, span)
                if key in seen:
                    continue
                seen.add(key)
                gt[verse_no][name].append({
                    "span": span,
                    "primary": a.get("element", ""),
                    "subtype": a.get("subtype", ""),
                })
    return gt


if __name__ == "__main__":
    pj = load_poem_json(16251)
    print(build_poem_text(pj))
    gt = load_ali_gt_spans(pj)
    for no in sorted(gt):
        for el in ELEMENT_ORDER:
            if gt[no][el]:
                print(no, el, [s["span"] for s in gt[no][el]])
