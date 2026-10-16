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
- anthropic_opus: Claude Opus 5.5, set-A-only task (2026-10-16). Cannot
  reuse pilot_3models.providers.call_anthropic unmodified -- it hardcodes
  MODELS["anthropic"]["model_id"] (Claude Sonnet 4.6) from the frozen
  Phase 1 config, which must not be edited (CLAUDE.md). call_anthropic_opus
  below is a new, separate function with the identical SDK call shape
  (max_tokens=16000, temperature passed through, same return dict shape),
  targeting e1v2_config.EXTRA_MODEL_PRICING["anthropic_opus"]["model_id"]
  instead.
"""
import os
import sys
from pathlib import Path

PILOT_DIR = Path(__file__).resolve().parents[2] / "experiments" / "pilot_3models"
PHASE3_DIR = Path(__file__).resolve().parents[2] / "experiments" / "phase3_subelements"
if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
if str(PHASE3_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE3_DIR))

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EXTRA_MODEL_PRICING  # noqa: E402
from providers import call_anthropic, call_openai  # noqa: E402
from providers_fixed import call_google_fixed  # noqa: E402


def call_anthropic_opus(system_message: str, user_message: str, temperature: float = 0.0) -> dict:
    """`temperature` is accepted (same call signature as every other CALLERS entry,
    which runner.py invokes positionally as caller(system, user, TEMPERATURE)) but
    NOT forwarded to the API: Anthropic's Opus 5.5 migration guide
    (platform.claude.com/docs/en/models/opus-5-5/migration-guide) states that
    Claude Opus 4.7 and later, including Opus 5.5, reject temperature/top_p/top_k
    at any non-default value with a 400 error -- confirmed directly here too (the
    first live attempt with temperature=0.0 failed with exactly that 400:
    "`temperature` is deprecated for this model", 5 consecutive errors, $0 spent,
    stopped automatically by the runner's own error-cap logic before this fix)."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model_id = EXTRA_MODEL_PRICING["anthropic_opus"]["model_id"]
    resp = client.messages.create(
        model=model_id,
        max_tokens=16000,
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return {
        "raw_text": text,
        "model_id": model_id,
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }


CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google_fixed,
    "anthropic_opus": call_anthropic_opus,
}
