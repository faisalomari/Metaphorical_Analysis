"""Phase 4 E1 (example-sensitivity pilot) constants.

Design frozen per docs/phase4/COST_PLAN.md and the user's E1 design decisions
(2026-10-10): poet=Abu Nuwas, element=مجاز (Trope), subtype focus=استعارة فعل,
3 example sets (A/B/C, seed=42), 50-poem eval pool (seed=43), 1 run per
set/model, optional set-A repeat (off by default).

Paths follow experiments/pilot_3models's sys.path-insertion convention (no
package __init__ required; each script inserts both this directory and the
pilot directory onto sys.path before importing bare module names).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"

ALI_POEMS_DIR = ROOT / "data" / "ali_poems"
ALI_MANIFEST_PATH = ALI_POEMS_DIR / "manifest.csv"
ALI_POEMS_JSON_DIR = ALI_POEMS_DIR / "poems"

CONFIG_DIR = Path(__file__).resolve().parent / "config"
RESULTS_DIR = ROOT / "results" / "phase4_e1"
EXAMPLE_SETS_PATH = CONFIG_DIR / "example_sets.json"
EVAL_POOL_PATH = CONFIG_DIR / "eval_pool.json"

POET_NAME = "أبو نواس"
ELEMENT = "Trope"          # this project's internal element key (prompts.py / span_scoring.py)
ELEMENT_AR = "مجاز"
SUBTYPE_FOCUS = "استعارة فعل"

# Exclusions (COST_PLAN.md §0 / §2.1): poem with no verse text, the 5 frozen
# Phase 1 poems (TEST stays spent, DEV stays DEV), and the 3 Abu Nuwas poems
# used as example sources (excluded from eval separately, see build_pool.py).
NO_TEXT_POEM_ID = "28601"
ALREADY_USED_POEM_IDS = {"2127", "2196", "3205", "3218", "10539"}  # Abu_Tammam, Imru2, Imru1, Nabigha, Jarir

EXAMPLE_POEM_IDS = ["16251", "17234", "21337"]  # sets A, B, C source poems, in order
EXAMPLE_SEED = 42
POOL_SEED = 43
EVAL_POOL_SIZE = 50

SET_NAMES = ["A", "B", "C"]
N_RUNS = 1          # one run per set per model (no second run) per the design
REPEAT_SET_A = False  # separate off-by-default flag: one optional repeat of set A only

# Two models confirmed by the user (2026-10-10, evidence: INFO_REPORT.md §1a/§1d
# Trope/استعارة فعل F1, §4 cost/call) for the actual E1 run.
RUN_MODELS = ["google", "openai"]
# All 3 models this project supports pricing for (config.py MODELS) — used for
# the dry-run cost comparison table at the user's request, not for the actual run.
ALL_MODELS = ["anthropic", "openai", "google"]

TEMPERATURE = 0.0
