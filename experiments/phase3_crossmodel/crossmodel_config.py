"""Phase 3 cross-model config. Reuses Phase 1's model registry and Phase 3's
subtype/ground-truth machinery unchanged (imported, never copied) - adds only
what this phase needs: the new output dir and which models to run beyond the
existing Gemini data.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
PHASE3_DIR = ROOT / "experiments" / "phase3_subelements"
sys.path.insert(0, str(PILOT_DIR))
sys.path.insert(0, str(PHASE3_DIR))

from config import MODELS  # noqa: E402  (Phase 1, reused unchanged)
from phase3_config import BY_SUBTYPE_DIR, POEMS  # noqa: E402  (Phase 3, reused unchanged)
from subtype_defs import SUBTYPE_DEFS  # noqa: E402

RESULTS_DIR = ROOT / "results" / "phase3_crossmodel"
RAW_DIR = RESULTS_DIR / "raw"
PHASE3_RAW_DIR = ROOT / "results" / "phase3_subelements" / "raw"

N_RUNS = 2
TEMPERATURE = 0.0

# Already have Gemini (phase3_subelements). These are the "other models
# already used in the project" to run the same task on, per pilot_3models/
# config.py (MODELS) and phase2_chatlike/phase2_config.py (adds Fable 5).
# Fable 5 (claude-fable-5, $10/$50 per MTok) is excluded here, same as the
# original Phase 3 decision (results/phase3_subelements/MEETING_SUMMARY.md
# S5) - at this task's volume (570 rows x 2 runs) Fable 5 alone would exceed
# the $10 auto-proceed gate (see cost_estimate.md). Re-add with a fresh,
# separately-approved cost estimate if ever wanted.
CROSSMODEL_KEYS = ["anthropic", "openai"]

ALREADY_DONE_KEY = "google"  # Gemini 3.5 Flash - existing phase3_subelements data, re-scored not re-run
