"""Minimal Arabic diacritics stripping for the val-only with/without-diacritics
ablation (task Step 1 instruction). No shared active-code helper exists in this
project for this (only `archive/FirstStep/tashbeh.py`'s `remove_diacritics`,
an archived, not-imported module) -- this reuses that exact same 8-character
diacritic set rather than inventing a different one."""

DIACRITICS = {"ِ", "َ", "ُ", "ْ", "ّ", "ً", "ٌ", "ٍ"}
# kasra, fatha, damma, sukun, shadda, tanween fath/damm/kasr


def strip_diacritics(text: str) -> str:
    return "".join(ch for ch in text if ch not in DIACRITICS)
