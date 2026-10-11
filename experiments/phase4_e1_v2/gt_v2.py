"""Verse-level ground truth for exactly one subtype (exact string match on
poem_json["annotations"][i]["subtype"]), reusing phase4_e1 (v1)'s
ali_poems_io.load_poem_json/load_manifest unchanged (not reimplemented).

A verse-unit here is ONE verse (not a multi-verse annotation span) — matches
v1's own per-verse scoring convention (phase4_e1/scoring.py
majority_exists_and_appearance), so an annotation whose comma-separated
verse_index spans multiple verses is counted at its FIRST verse only, same
rule v1 already used and the scraper's own validation pass (SESSION_LOG.md
2026-10-10T04:35) confirmed reproduces the frozen xlsx row counts exactly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_DIR, SUBTYPE_FOCUS  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402


def verses_by_no(poem_json: dict) -> dict:
    return {v["verse_index"]: v["text"] for v in poem_json["verses"]}


def gt_spans_for_subtype(poem_json: dict, subtype: str = SUBTYPE_FOCUS) -> dict:
    """Returns {verse_no: [span_text, ...]} for every verse 1..n_verses
    (empty list = no GT-positive instance of this subtype at that verse)."""
    n_verses = poem_json["verse_count"]
    gt = {no: [] for no in range(1, n_verses + 1)}
    for a in poem_json["annotations"]:
        if a.get("subtype") != subtype:
            continue
        verse_no = int(str(a["verse_index"]).split(",")[0])
        if 1 <= verse_no <= n_verses:
            span = (a.get("span_text") or "").strip()
            gt[verse_no].append(span)
    return gt


if __name__ == "__main__":
    pj = load_poem_json(16251)
    gt = gt_spans_for_subtype(pj)
    vb = verses_by_no(pj)
    for no in sorted(gt):
        if gt[no]:
            print(no, vb[no], "->", gt[no])
