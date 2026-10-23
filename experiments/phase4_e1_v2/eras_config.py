"""Constants + the note-quality filter for the supervisor-requested
poet-era few-shot experiment (M1/M2/E1/E2/H1/H2) on top of E1 v2's existing
Z/A/B/C(/D/D2) and F5/F10 (multipoet) sets.

Does not edit phase4_e1 (v1), phase3_subelements, pilot_3models, or any
existing E1 v2 file -- additive only, same convention Set D/D2 and F5/F10
already used.

Design (declared before any selection is run, per CLAUDE.md rule 2/6):
  - Same subtype focus as every other E1/E1v2/multipoet set: استعارة فعل
    (e1v2_config.SUBTYPE_FOCUS), same Phase 3 subtype prompt/schema.
  - Six sets, each exactly 2 example verses from 2 DIFFERENT poets, built
    with multipoet_prompt_builder.build_system_message_n(extra_examples)
    (N=2) -- the identical scaffold A/B/C/D/D2 already use (verified by
    unit_checks_eras.py to byte-match the A/B/C header+Example-1 block).
  - Poet-era bands are defined relative to docs/phase4/ERAS_ANALYTICS.md's
    own axis (data/ali_poems/poet_dates.csv death_year_ce), computed by
    eras_analytics.py -- this module only RE-EXPORTS the band thresholds
    (computed once, persisted to config/eras_axis.json by
    eras_analytics.build_axis_stats(), then read back here) so the
    selection step and the analytics step can never disagree about where
    the median/midpoint/extremes actually are.
  - M1, M2: both examples from poets in the MIDDLE BAND (within
    MIDDLE_BAND_HALF_WIDTH_YEARS of the weighted-by-verses median death
    year).
  - E1, E2: each = one example from an EARLIEST-extreme poet + one from a
    LATEST-extreme poet (bottom/top EXTREME_PCT of the dated axis by death
    year). E1 and E2 use 4 distinct poets between them (2 earliest + 2
    latest, no poet reused).
  - H1 = both examples from the middle of the FIRST HALF of the axis
    (poets below the overall median, drawn from near the first-half's own
    median). H2 = both from the middle of the SECOND HALF (above the
    overall median, near the second-half's own median).
  - No poet is reused across the six groups (12 distinct poets total).
  - Selection seed: MULTIPOET_EXAMPLE_SEED value (42) reused for
    continuity, but a SEPARATE random.seed() call made by eras_examples.py
    (its own draw, not multipoet's or v1's RNG stream) -- only used to
    break ties when a band/poet has >1 eligible candidate verse.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = Path(__file__).resolve().parent / "config"
RESULTS_DIR = ROOT / "results" / "phase4_e1_v2"
DOCS_DIR = ROOT / "docs" / "phase4"

POET_DATES_PATH = ROOT / "data" / "ali_poems" / "poet_dates.csv"

ERAS_AXIS_PATH = CONFIG_DIR / "eras_axis.json"          # written by eras_analytics.py
ERAS_EXAMPLE_SETS_PATH = CONFIG_DIR / "eras_example_sets.json"  # written by eras_examples.py
ERAS_NOTE_FILTER_REPORT_PATH = CONFIG_DIR / "eras_note_filter_report.json"

ERAS_SET_NAMES = ["M1", "M2", "E1", "E2", "H1", "H2"]

ERAS_EXAMPLE_SEED = 42  # separate random.seed() call, tie-break only (see module docstring)

# Band definitions for Part 1 (eras_analytics.py, full 36-poet corpus axis).
MIDDLE_BAND_HALF_WIDTH_YEARS = 75  # "middle band" = within +-75 years of the weighted median
EXTREME_PCT = 0.15                 # "extremes" = earliest/latest 15% of the dated axis, by years

# Part 2 (eras_examples.py) reuses EXTREME_PCT (now applied by RANK over the
# much smaller selection-eligible population -- see that module's docstring
# for why) and adds SELECTION_MIDDLE_N: the middle_band pool size, set to
# exactly enough for M1+M2 (2 examples each).
SELECTION_MIDDLE_N = 4

# Reliable-date confidence levels accepted for example-poet SELECTION (Part 2).
# Part 1's analytics axis itself includes every poet with ANY non-blank
# death_year_ce (high/medium/low, flagged as such) -- see ERAS_ANALYTICS.md
# for which poets lack a date entirely. Selection is stricter: only
# high/medium confidence poets are eligible to supply an example verse.
SELECTION_CONFIDENCE_LEVELS = {"high", "medium"}

# Poem exclusions for eras example-verse candidates (Part 2's selection
# rules, as given): never draw from a Phase 1 frozen poem, the 3 Abu Nuwas
# v1 example-source poems, any F5/F10 example-source poem, or any poem in
# eval_pool_25.json (the 327-verse-unit pool M1..H2 will themselves be
# EVALUATED on -- eval pool stays eval_pool_25.json, unchanged, per the task).
from e1v2_config import ALREADY_USED_POEM_IDS, EXAMPLE_POEM_IDS, NO_TEXT_POEM_ID  # noqa: E402

F5_F10_EXAMPLE_POEM_IDS = {
    "6574", "5661", "27110", "7891", "4480",       # F5
    "34779", "29516", "7408", "3331", "2187",      # +F10
}

QURAN_POET_NAME = "القرآن الكريم"  # not an individual poet -- excluded from era selection entirely


# ---------------------------------------------------------------------------
# Note-quality filter ("genuine metaphor analysis" vs. question-marked /
# lexical-gloss-only), declared + calibrated against the actual corpus
# before being applied (see SESSION_LOG.md for the calibration samples).
# ---------------------------------------------------------------------------
_ARABIC_DIACRITICS_RE = re.compile(r"[ً-ْٰـ]")
_COLON_GLOSS_RE = re.compile(r"^[^:：]{1,30}[:：]")  # "word(s): short definition" at the start
_REASONING_KEYWORDS = ["ستعار", "مجاز", "كناية", "شبه", "تشبيه", "تشابه", "كأن"]


def _strip_diacritics(s: str) -> str:
    return _ARABIC_DIACRITICS_RE.sub("", s)


def note_quality(note: str) -> tuple:
    """Returns (is_genuine: bool, reason: str). Rule, applied in order:
    1. A note containing a question mark (Arabic ؟ or ASCII ?) is EXCLUDED
       -- it marks the annotator's own uncertainty, not a confident analysis.
    2. A note containing any of _REASONING_KEYWORDS (diacritic-insensitive
       substring match: stems covering استعار/مستعار/استعارة, مجاز, كناية,
       شبه/تشبيه/تشابه, كأن) is KEPT regardless of length/shape -- it
       names the metaphor mechanism explicitly.
    3. Otherwise, a note with <=3 whitespace-separated tokens, OR one
       matching a leading "word(s): definition" colon-gloss pattern, is
       EXCLUDED as lexical-gloss-only (a bare dictionary definition or a
       one-word classificatory tag, not an analysis connecting source and
       target of the metaphor).
    4. Anything else (longer, non-colon-gloss-shaped, no keyword) is KEPT
       by default -- an interpretive paraphrase of the verse's meaning,
       even without an explicit rhetorical-terminology keyword, still
       counts as a genuine analysis note for this filter's purpose.
    Calibrated against the full candidate pool (858 notes): question_mark
    removes 203, colon_gloss removes 66, too_short removes 68 (337 total
    removed), keyword keeps 418, default_keep keeps 103 (521 total kept).
    """
    note = note.strip()
    if "؟" in note or "?" in note:
        return False, "question_mark"
    norm = _strip_diacritics(note)
    if any(k in norm for k in _REASONING_KEYWORDS):
        return True, "keyword"
    if len(note.split()) <= 3:
        return False, "too_short"
    if _COLON_GLOSS_RE.match(note):
        return False, "colon_gloss"
    return True, "default_keep"
