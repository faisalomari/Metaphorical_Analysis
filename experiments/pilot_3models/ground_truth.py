"""Load Prof. Ali Hussein's manual ground-truth annotations and map the
53-element classical taxonomy down to this pilot's 4 target elements.

Mapping (substring match against primary + secondary element columns):
  - "مجاز" or "استعارة" (metaphor is a subtype of trope; conflated per the
    same convention used in SecondStep's f_score_prompt.txt)      -> Trope
  - "تشبيه"                                                        -> Simile
  - "كناية"                                                        -> Kenning
  - "طباق"                                                         -> Antonymy
Any other label (مبالغة, اشتقاق, رد الأعجاز على الصدور, تجريد, ...) is not
evidence for any of the 4 target elements.
"""
import pandas as pd
from config import POEMS, ELEMENT_ORDER, ACTIVE_POEM

SUBSTRING_MAP = {
    "Trope": ["مجاز", "استعارة"],
    "Simile": ["تشبيه"],
    "Kenning": ["كناية"],
    "Antonymy": ["طباق"],
}


def load_ground_truth_spans(poem_key: str = ACTIVE_POEM) -> dict:
    """Returns {verse_no: {element: [{"span": str, "primary": str, "secondary": str}, ...]}}.

    Verses with no annotation row at all are initialized with empty lists for
    every element: Dr. Hussein's annotation scheme logs every rhetorical
    instance found, so a verse absent from the sheet is treated as containing
    none of the 4 target elements (not as "no ground truth available").
    Exact-duplicate (span, element) rows (double-tagged subtype variants of
    the same phrase) are deduplicated so they don't inflate instance counts.
    """
    poem = POEMS[poem_key]
    n_verses = poem["n_verses"]
    df = pd.read_excel(poem["ground_truth_path"])
    gt = {no: {name: [] for name in ELEMENT_ORDER} for no in range(1, n_verses + 1)}
    seen = set()

    for _, row in df.iterrows():
        verse_no = row["البيت"]
        if not isinstance(verse_no, (int, float)) or pd.isna(verse_no):
            continue
        verse_no = int(verse_no)
        if not (1 <= verse_no <= n_verses):
            continue  # out-of-range / malformed verse references (e.g. verse ranges) are skipped

        primary = str(row.get("العنصر البلاغي المستعمل", "") or "")
        secondary = str(row.get("العنصر البلاغي الثانوي", "") or "")
        span = row.get("التعبير البلاغي")
        span = str(span) if pd.notna(span) else ""
        labels = f"{primary} {secondary}"

        for name, substrings in SUBSTRING_MAP.items():
            if any(s in labels for s in substrings):
                key = (verse_no, name, span.strip())
                if key in seen:
                    continue
                seen.add(key)
                gt[verse_no][name].append({"span": span, "primary": primary, "secondary": secondary})
    return gt


def load_ground_truth(poem_key: str = ACTIVE_POEM) -> dict:
    """Returns {verse_no: {element: bool}} — the coarse exists/not-exists view,
    kept for backward compatibility with the original verse-level scoring."""
    spans = load_ground_truth_spans(poem_key)
    return {no: {el: len(spans[no][el]) > 0 for el in ELEMENT_ORDER} for no in spans}


# Backward-compat constant used by analyze.py / build_report.py for the active poem.
N_VERSES = POEMS[ACTIVE_POEM]["n_verses"]


if __name__ == "__main__":
    gt = load_ground_truth_spans()
    for no in sorted(gt):
        for el in ELEMENT_ORDER:
            if gt[no][el]:
                print(no, el, [s["span"] for s in gt[no][el]])
