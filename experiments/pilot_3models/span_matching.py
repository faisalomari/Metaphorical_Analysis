"""Span-level matching between a predicted appearance and ground-truth spans.

Two criteria, reported side by side per the task spec:
  - strict: after normalization, one span is a substring of the other
  - token: token-overlap coefficient (|intersection| / min(|pred|, |gt|)) >= threshold
"""
import re

# Arabic diacritics (tashkeel) unicode ranges, matching FirstStep/help_code/clean.py's convention.
ARABIC_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْٰۖ-ۭ]")
TOKEN_THRESHOLD = 0.5


def normalize(text) -> str:
    if not text:
        return ""
    text = ARABIC_DIACRITICS.sub("", str(text))
    text = text.replace("ـ", "")  # strip tatweel
    text = re.sub(r"\s+", " ", text).strip()
    # Strip quote-like wrapping punctuation - straight quotes (present since
    # Phase 1) plus Arabic guillemets « » (added Phase 2: Fable 5's Config C
    # extraction quotes spans with them; never appeared in any Phase 1 raw
    # output, so this is a no-op there, not a change to any frozen number).
    return text.strip("\"'«»")


# Single-letter conjunction/preposition clitics that attach directly to the next
# word with no space (و "and", ف "so/then") in Modern Standard/Classical Arabic.
# Stripped as an alternate token form so e.g. "وكأن" also matches bare "كأن" -
# without this, whole-word token-set overlap is fragile against attached prefixes
# in a way substring (strict) matching is not.
_CLITIC_PREFIXES = ("و", "ف")


def _prefix_variants(word: str) -> set:
    variants = {word}
    if len(word) > 3 and word[0] in _CLITIC_PREFIXES:
        variants.add(word[1:])
    return variants


def tokens(text) -> set:
    out = set()
    for word in normalize(text).split():
        out |= _prefix_variants(word)
    return out


def strict_overlap(pred: str, gt: str) -> bool:
    p, g = normalize(pred), normalize(gt)
    if not p or not g:
        return False
    return p in g or g in p


def token_overlap_ratio(pred: str, gt: str) -> float:
    pt, gt_ = tokens(pred), tokens(gt)
    if not pt or not gt_:
        return 0.0
    return len(pt & gt_) / min(len(pt), len(gt_))


def token_match(pred: str, gt: str, threshold: float = TOKEN_THRESHOLD) -> bool:
    return token_overlap_ratio(pred, gt) >= threshold


def best_match(pred: str, gt_spans: list, criterion: str, threshold: float = TOKEN_THRESHOLD):
    """Returns the index of the best-matching (unused) gt span, or None."""
    if criterion == "strict":
        for i, gt in enumerate(gt_spans):
            if strict_overlap(pred, gt):
                return i
        return None
    elif criterion == "token":
        best_i, best_ratio = None, 0.0
        for i, gt in enumerate(gt_spans):
            r = token_overlap_ratio(pred, gt)
            if r >= threshold and r > best_ratio:
                best_i, best_ratio = i, r
        return best_i
    raise ValueError(criterion)
