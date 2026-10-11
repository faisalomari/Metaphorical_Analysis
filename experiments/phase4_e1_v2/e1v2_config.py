"""Phase 4 E1 v2 (rebuild on the Phase 3 subtype-level prompt) constants.

E1 v1 (experiments/phase4_e1/) reused pilot_3models.prompts.build_system_message()
unmodified: old terminology ("Kenning"/"Antonymy") and TEST-poem-leaking element
examples (see docs/phase4/PROMPT_INVENTORY.md). v1's files/results are untouched;
this is a separate module that builds the same example-sensitivity question on
top of experiments/phase3_subelements's subtype-level prompt instead.

Reuses, unmodified, from phase4_e1 (v1):
  - config/eval_pool.json  (50 poems: 10 abu_nuwas + 40 other, seed=43)
  - config/example_sets.json (sets A/B/C, 2 examples each, seed=42)
Does not edit phase3_subelements/ or pilot_3models/ — only imports from them.
"""
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
PHASE3_DIR = ROOT / "experiments" / "phase3_subelements"
E1V1_DIR = ROOT / "experiments" / "phase4_e1"

ALI_POEMS_DIR = ROOT / "data" / "ali_poems"
ALI_MANIFEST_PATH = ALI_POEMS_DIR / "manifest.csv"
ALI_POEMS_JSON_DIR = ALI_POEMS_DIR / "poems"

CONFIG_DIR = Path(__file__).resolve().parent / "config"
RESULTS_DIR = ROOT / "results" / "phase4_e1_v2"

# v1's own config files, reused unchanged (same pool / same example sets).
E1V1_EVAL_POOL_PATH = E1V1_DIR / "config" / "eval_pool.json"
E1V1_EXAMPLE_SETS_PATH = E1V1_DIR / "config" / "example_sets.json"

# This module's own persisted 25-poem pool (build_pool_25.py writes this).
EVAL_POOL_25_PATH = CONFIG_DIR / "eval_pool_25.json"

POET_NAME = "أبو نواس"
SUBTYPE_FOCUS = "استعارة فعل"  # exact match against poem_json["annotations"][i]["subtype"]
PARENT_ELEMENT = "مجاز (Trope) — فرع الاستعارة"  # subtype_defs.SUBTYPE_DEFS[SUBTYPE_FOCUS]["parent"]

# Same exclusions as v1 (COST_PLAN.md §0/§2.1): poem with no verse text, the 5
# frozen Phase 1 poems, and the 3 Abu Nuwas example-source poems.
NO_TEXT_POEM_ID = "28601"
ALREADY_USED_POEM_IDS = {"2127", "2196", "3205", "3218", "10539"}
EXAMPLE_POEM_IDS = ["16251", "17234", "21337"]

SET_NAMES = ["Z", "A", "B", "C"]  # Z = zero-extra-examples baseline (Phase 3's original prompt)
FEWSHOT_SET_NAMES = ["A", "B", "C"]

RUN_MODELS = ["google", "openai"]
ALL_MODELS = ["anthropic", "openai", "google"]
N_RUNS = 1
REPEAT_SET_A = False

TEMPERATURE = 0.0

# Cheaper-variant subsample: 5 abu_nuwas + 20 other, drawn from the same
# candidate pool (158 poems) as v1's build_pool.py, same seed=43 (a separate
# random.sample call under the same seed value — NOT a subset of the 50-poem
# eval pool, so it is reproducible independently of it).
CHEAP_VARIANT_ABU_NUWAS_N = 5
CHEAP_VARIANT_OTHER_N = 20
CHEAP_VARIANT_SEED = 43


def build_cheap_variant_pool(candidate_pool: list) -> list:
    abu_nuwas_candidates = [p for p in candidate_pool if p["tag"] == "abu_nuwas"]
    other_candidates = [p for p in candidate_pool if p["tag"] == "other"]
    random.seed(CHEAP_VARIANT_SEED)
    picked = (random.sample(abu_nuwas_candidates, CHEAP_VARIANT_ABU_NUWAS_N)
              + random.sample(other_candidates, CHEAP_VARIANT_OTHER_N))
    return sorted(picked, key=lambda p: int(p["poem_id"]))
