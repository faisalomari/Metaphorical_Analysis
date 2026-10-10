"""Phase 2 (v2) config. Reuses Phase 1's poem registry, ground truth, element
order, and Sonnet 4.6 model entry unchanged (imported, never copied) - only
adds what Phase 2 needs on top: the Fable 5 model entry and the DEV-only
scope for the sec3i experiment. See PROJECT_STATE.md -> Phase 2 section.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PILOT_DIR = ROOT / "experiments" / "pilot_3models"
sys.path.insert(0, str(PILOT_DIR))

from config import (  # noqa: E402  (Phase 1 config, reused unchanged)
    ELEMENT_ORDER, ELEMENT_AR, ELEMENT_FILES, ELEMENTS_DIR,
    POEMS, DEV_POEMS, TEST_POEMS, N_RUNS, TEMPERATURE,
    MODELS as PHASE1_MODELS,
)

RESULTS_DIR = ROOT / "results" / "phase2_chatlike"

# DEV-only scope for sec3i - identical set to Phase 1's DEV, never TEST.
SEC3I_POEMS = DEV_POEMS  # ["Imru2", "Nabigha"]

# Model registry for Phase 2. Sonnet 4.6 entry is Phase 1's, imported
# unchanged (Config B runs on it). Fable 5 pricing verified 2026-07-23
# against the Anthropic API skill's cached model table ($10/$50 per MTok).
MODELS = dict(PHASE1_MODELS)
MODELS["anthropic_fable5"] = {
    "model_id": "claude-fable-5",
    "display": "Claude Fable 5",
    "price_in": 10.00,
    "price_out": 50.00,
}

# Cheap extraction model for Config C stage 2 (reuses Phase 1's GPT-5.4-mini
# entry - same pricing table, no separate lookup needed).
EXTRACTOR_MODEL_KEY = "openai"
