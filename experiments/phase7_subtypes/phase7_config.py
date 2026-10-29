"""Phase 7 (3-model x {zero-shot,few-shot} x 3 subtypes) constants.

Additive-only, same convention every phase4_e1_v2 supplementary set has
already used: imports Phase 1/3/4 modules unchanged, adds nothing to them.
Does not edit experiments/phase3_subelements/, experiments/phase4_e1_v2/,
experiments/pilot_3models/, or any existing result/doc.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHASE3_DIR = ROOT / "experiments" / "phase3_subelements"
PHASE4_DIR = ROOT / "experiments" / "phase4_e1_v2"
PHASE4_E1_DIR = ROOT / "experiments" / "phase4_e1"

ALI_POEMS_DIR = ROOT / "data" / "ali_poems"
ALI_MANIFEST_PATH = ALI_POEMS_DIR / "manifest.csv"
ALI_POEMS_JSON_DIR = ALI_POEMS_DIR / "poems"

CONFIG_DIR = Path(__file__).resolve().parent / "config"
RESULTS_DIR = ROOT / "results" / "phase7_subtypes"
DOCS_DIR = ROOT / "docs" / "phase7"

EVAL_POOL_25_PATH = PHASE4_DIR / "config" / "eval_pool_25.json"

for p in (str(PHASE3_DIR), str(PHASE4_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Same exclusions as every phase4_e1_v2 set (e1v2_config.py): poem with no
# verse text, and the 5 frozen Phase 1 poems (never used as example sources
# for ANY set in this project).
NO_TEXT_POEM_ID = "28601"
ALREADY_USED_POEM_IDS = {"2127", "2196", "3205", "3218", "10539"}

# The task's 3 target subtypes, candidate exact-string set for each (the
# first entry is the literally-requested string; others are declared only
# if Step 0a's census finds the first one absent or needing a choice).
REQUESTED_SUBTYPES = ["تشبيه بليغ", "استعارة قديمة", "كناية عن صفة"]

MODELS = ["anthropic", "openai", "google"]
CONDITIONS = ["zero", "few"]
