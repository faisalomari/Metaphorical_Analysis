from __future__ import annotations

from google import genai
from google.genai import types

from src.models.base_model import BaseModel


class GeminiModel(BaseModel):
    LABELING_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "label": {
                "type": "string",
                "enum": ["yes", "no"],
                "description": "Whether the requested rhetorical element is present.",
            },
            "span": {
                "type": "string",
                "description": "Exact words from the verse if the element is present, otherwise an empty string.",
            },
            "confidence_band": {
                "type": "string",
                "enum": ["very_low", "low", "medium", "high", "very_high"],
                "description": "Ordinal confidence bucket for the judgment.",
            },
            "reasoning": {
                "type": "string",
                "description": "Short explanation for the judgment.",
            },
        },
        "required": ["label", "span", "confidence_band", "reasoning"],
    }

    def __init__(self, model_name: str, api_key: str) -> None:
        super().__init__(provider="gemini", model_name=model_name, api_key=api_key)
        self.client = genai.Client(api_key=api_key)

    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                response_mime_type="application/json",
                response_json_schema=self.LABELING_RESPONSE_SCHEMA,
            ),
        )
        return (response.text or "").strip()

    def explain_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
        return (response.text or "").strip()
