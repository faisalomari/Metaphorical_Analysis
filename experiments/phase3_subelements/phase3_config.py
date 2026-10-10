"""Phase 3 (sub-rhetorical-element detection) config. Reuses Phase 1's poem
registry, DEV/TEST split, and model registry unchanged (imported, never
copied) - see PROJECT_STATE.md standing discipline: DEV first, TEST spent once.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
sys.path.insert(0, str(PILOT_DIR))

from config import POEMS, DEV_POEMS, TEST_POEMS, MODELS  # noqa: E402  (Phase 1, reused unchanged)

BY_SUBTYPE_DIR = ROOT / "data" / "ground_truth" / "by_subtype"
RESULTS_DIR = ROOT / "results" / "phase3_subelements"

# Chosen model for this phase (see conversation: Gemini 3.5 Flash was the best
# or near-best F1 on 3/4 elements in Phase 1 TEST, at half Claude Sonnet 4.6's
# price and with the highest run-to-run consistency; GPT-5.4-mini is cheaper
# but clearly weaker on Trope/Kenning/Antonymy; Fable 5 explicitly excluded by
# the user for cost - $10/$50 per MTok, 10x Gemini's input price).
MODEL_KEY = "google"
N_RUNS = 2
TEMPERATURE = 0.0
