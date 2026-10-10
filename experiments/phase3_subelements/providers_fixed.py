"""Fixes a real cost-tracking bug found in this session: Phase 1's shared
`providers.call_google` (experiments/pilot_3models/providers.py) only reads
`usage.candidates_token_count` as "output_tokens". Gemini 3.5 Flash bills a
SEPARATE `thoughts_token_count` (internal "thinking" tokens) at the same
output rate, and that field is silently dropped - so every cost estimate this
project has printed for Gemini calls under-counts real spend. This is why the
previous phase3 full run computed $0.96 but the user's actual AI Studio
balance dropped by ~28 NIS (~$7.5-8).

Not fixed in pilot_3models/providers.py itself - that file is Phase 1's frozen
harness (must reproduce its exact frozen numbers per REPRODUCIBILITY.md).
This is a local, Phase-3-only replacement, same pattern Phase 2 uses for
things it needs to change (import Phase 1, override only what's new).

Also sets thinking_level="minimal" (Gemini 3.5 Flash's low-cost setting -
"as close as possible to a zero budget for thinking", per Google's docs) since
a yes/no-plus-one-sentence-reasoning classification task doesn't need deep
internal reasoning, and every thinking token is billed at the $9/MTok output
rate regardless of how simple the task is.
"""
import os

from phase3_config import MODELS, MODEL_KEY


def call_google_fixed(system_message: str, user_message: str, temperature: float = 0.0) -> dict:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model_id = MODELS[MODEL_KEY]["model_id"]
    resp = client.models.generate_content(
        model=model_id,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_message,
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_level="minimal"),
        ),
    )
    text = resp.text or ""
    usage = resp.usage_metadata
    candidates_tok = (usage.candidates_token_count if usage else None) or 0
    thoughts_tok = (getattr(usage, "thoughts_token_count", None) if usage else None) or 0
    return {
        "raw_text": text,
        "model_id": model_id,
        "usage": {
            "input_tokens": usage.prompt_token_count if usage else None,
            # billed output = visible answer + hidden thinking tokens, both at price_out
            "output_tokens": candidates_tok + thoughts_tok,
            "candidates_tokens": candidates_tok,
            "thoughts_tokens": thoughts_tok,
        },
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    r = call_google_fixed("You are a helpful assistant.", "Say only the word: test")
    print(r)
