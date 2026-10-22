"""Constants for the supervisor-requested multi-poet few-shot experiment
(F5/F10/optional F5b) on top of E1 v2's existing Z/A/B/C(/D/D2) sets.

Does not edit phase4_e1 (v1), phase3_subelements, pilot_3models, or any
existing E1 v2 file -- additive only, same convention Set D/D2 already used
(see preview_and_diff_D.py / dryrun_D.py / analyze_D.py).

Design (declared before any selection is run, per CLAUDE.md rule 2/6):
  - Same subtype focus as every other E1/E1v2 set: استعارة فعل (SUBTYPE_FOCUS,
    e1v2_config.py), same Phase 3 subtype prompt/schema.
  - F5  = 5 example verses, each from a DIFFERENT poet.
  - F10 = 10 example verses, each from a DIFFERENT poet, F5's 5 poets INCLUDED
    (F5 is a strict prefix of F10's poet list) -- isolates "10 vs 5" from
    "which poets".
  - F5b (optional, --include-f5b, off by default) = 5 MORE examples from 5
    OTHER poets, disjoint from F10's 10 -- isolates "number of examples" from
    "choice of examples" (a different set of 5 poets should land close to F5
    if the effect is about count, not about which specific poets/verses).
  - Poet-selection seed: deterministic (period-diversity round robin, see
    multipoet_examples.py) -- NOT random; only the per-poet VERSE draw is
    randomized, under random.seed(MULTIPOET_EXAMPLE_SEED) = 42 (same seed
    value as v1's EXAMPLE_SEED, reused for continuity, but a SEPARATE
    random.seed() call -- this module's own draw, not v1's RNG stream).
  - Abu Nuwas may be one of the poets, but ONLY via a poem that is not one of
    the ORIGINAL 10 abu_nuwas eval_pool.json poems and not one of v1's own
    3 Abu Nuwas example-source poems (EXAMPLE_POEM_IDS) -- so the Abu Nuwas
    eval-pool slots and the original fewshot examples are never touched by
    this new draw. Every other poet's candidate poems may include an
    eval_pool poem; if chosen, that poem is removed from the new 50-poem
    pool and replaced (see multipoet_pool.py).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = Path(__file__).resolve().parent / "config"
RESULTS_DIR = ROOT / "results" / "phase4_e1_v2"

MULTIPOET_SET_NAMES = ["F5", "F10"]  # F5b appended at call sites when --include-f5b
F5_N = 5
F10_N = 10
F5B_N = 5

MULTIPOET_EXAMPLE_SEED = 42       # per-poet verse draw (separate random.seed() call)
MULTIPOET_POOL_CONTINUATION_SEED = 43  # must match e1_config.POOL_SEED exactly

# Old (v1) eval_pool_50's own Abu Nuwas poem ids -- Abu Nuwas example sources
# for F5/F10/F5b must avoid these (see module docstring) in addition to the
# standard NO_TEXT/ALREADY_USED/old-EXAMPLE_POEM_IDS exclusions every poet's
# candidates already respect.
OLD_EVAL_POOL_ABU_NUWAS_IDS = {
    "9028", "9078", "13658", "13666", "17233", "17373", "20449", "21047", "31126", "31384",
}

EVAL_POOL_50_MULTIPOET_PATH = CONFIG_DIR / "eval_pool_50_multipoet.json"
MULTIPOET_EXAMPLE_SETS_PATH = CONFIG_DIR / "multipoet_example_sets.json"
