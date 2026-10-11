"""CALLERS for E1 v2's runner: thin re-export, no reimplementation.

- anthropic / openai: experiments/pilot_3models/providers.py, unchanged
  (call_anthropic already sets max_tokens=16000 explicitly).
- google: experiments/phase3_subelements/providers_fixed.py's
  call_google_fixed, NOT pilot_3models/providers.py's plain call_google.
  The plain version only reads usage.candidates_token_count as output
  tokens and silently drops Gemini's separate thoughts_token_count
  (internal thinking tokens, billed at the same output rate) -- the exact
  bug that caused a real past incident (computed cost $0.96, actual AI
  Studio balance drop ~$7.5-8, see providers_fixed.py's own docstring).
  call_google_fixed also sets thinking_level="minimal" to keep that
  hidden-token cost near zero.
"""
import sys
from pathlib import Path

PILOT_DIR = Path(__file__).resolve().parents[2] / "experiments" / "pilot_3models"
PHASE3_DIR = Path(__file__).resolve().parents[2] / "experiments" / "phase3_subelements"
if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

from providers import call_anthropic, call_openai  # noqa: E402
from providers_fixed import call_google_fixed  # noqa: E402

CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google_fixed,
}
