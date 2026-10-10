"""Phase 2 provider wrappers.

Config B (Sonnet 4.6) and Config C stage 2 (GPT-5.4-mini extractor) reuse
Phase 1's providers.call_anthropic / call_openai unchanged (temperature=0.0
is valid on both). Fable 5 (Config A, Config C stage 1) needs a distinct
wrapper because its request shape differs from every model Phase 1 ever
called:
  - no temperature/top_p/top_k (Fable 5 rejects them with a 400)
  - no `thinking` param at all - thinking is always on for Fable 5; passing
    anything (including {"type": "adaptive"}) is unnecessary, and
    {"type": "disabled"} is a 400
  - depth is controlled by output_config.effort instead
  - stop_reason can be "refusal" (safety classifier decline) - must check
    before reading .content, since content can be empty (pre-output decline)
    or partial (mid-stream decline)
  - server-side fallback to Opus 4.8 is opt-in via beta header + the
    `fallbacks` param; enabled by default here per the model's own guidance
    (a refusal with no fallback just stops, which would silently drop DEV
    verses from a 2-run majority)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))
from providers import call_anthropic, call_openai, call_google  # noqa: F401,E402  (reused unchanged for Config B / stage 2)

FABLE5_MODEL_ID = "claude-fable-5"
FALLBACK_MODEL_ID = "claude-opus-4-8"


def call_fable5(system_message: str, user_message: str, effort: str = "medium", max_tokens: int = 16000) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.beta.messages.create(
        model=FABLE5_MODEL_ID,
        max_tokens=max_tokens,
        betas=["server-side-fallback-2026-06-01"],
        fallbacks=[{"model": FALLBACK_MODEL_ID}],
        output_config={"effort": effort},
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )
    usage = {
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }
    if resp.stop_reason == "refusal":
        return {
            "raw_text": "",
            "model_id": resp.model,
            "usage": usage,
            "error": f"refusal: {getattr(resp, 'stop_details', None)}",
        }
    text = "".join(block.text for block in resp.content if block.type == "text")
    served_by_fallback = any(block.type == "fallback" for block in resp.content)
    return {
        "raw_text": text,
        "model_id": resp.model,
        "usage": usage,
        "error": None,
        "served_by_fallback": served_by_fallback,
    }
