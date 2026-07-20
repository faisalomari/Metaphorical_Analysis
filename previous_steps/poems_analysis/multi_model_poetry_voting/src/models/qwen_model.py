from __future__ import annotations

from openai import OpenAI

from src.models.base_model import BaseModel


class QwenModel(BaseModel):
    LABELING_RESPONSE_FORMAT = {
        "type": "json_schema",
        "json_schema": {
            "name": "poetry_rhetoric_label",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "enum": ["yes", "no"]},
                    "span": {"type": "string"},
                    "confidence_band": {
                        "type": "string",
                        "enum": ["very_low", "low", "medium", "high", "very_high"],
                    },
                    "reasoning": {"type": "string"},
                },
                "required": ["label", "span", "confidence_band", "reasoning"],
                "additionalProperties": False,
            },
        },
    }

    def __init__(self, model_name: str, api_key: str, base_url: str) -> None:
        super().__init__(provider="qwen", model_name=model_name, api_key=api_key)
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            response_format=self.LABELING_RESPONSE_FORMAT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def explain_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()
