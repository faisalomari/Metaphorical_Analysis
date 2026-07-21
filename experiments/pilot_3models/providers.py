"""Thin, uniform wrappers around the three provider SDKs.

Each call_* function takes (system_message, user_message, temperature) and
returns a dict: {"raw_text": str, "model_id": str, "usage": {...}}.
No JSON-mode / structured-output enforcement is used anywhere here —
instruction-only JSON, matching Forth_Step's original methodology, for
comparability with the earlier GPT-5.2 pilot runs.
"""
import os
from config import MODELS


def call_anthropic(system_message: str, user_message: str, temperature: float = 0.0) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model_id = MODELS["anthropic"]["model_id"]
    resp = client.messages.create(
        model=model_id,
        max_tokens=16000,
        temperature=temperature,
        system=system_message,
        messages=[{"role": "user", "content": user_message}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    return {
        "raw_text": text,
        "model_id": model_id,
        "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
    }


def call_openai(system_message: str, user_message: str, temperature: float = 0.0) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model_id = MODELS["openai"]["model_id"]
    resp = client.chat.completions.create(
        model=model_id,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )
    text = resp.choices[0].message.content or ""
    usage = resp.usage
    return {
        "raw_text": text,
        "model_id": model_id,
        "usage": {"input_tokens": usage.prompt_tokens, "output_tokens": usage.completion_tokens},
    }


def call_google(system_message: str, user_message: str, temperature: float = 0.0) -> dict:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model_id = MODELS["google"]["model_id"]
    resp = client.models.generate_content(
        model=model_id,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_message,
            temperature=temperature,
        ),
    )
    text = resp.text or ""
    usage = resp.usage_metadata
    return {
        "raw_text": text,
        "model_id": model_id,
        "usage": {
            "input_tokens": usage.prompt_token_count if usage else None,
            "output_tokens": usage.candidates_token_count if usage else None,
        },
    }


CALLERS = {
    "anthropic": call_anthropic,
    "openai": call_openai,
    "google": call_google,
}
