from __future__ import annotations

from openai import OpenAI

from src.models.base_model import BaseModel


class OpenAIModel(BaseModel):
    def __init__(self, model_name: str, api_key: str) -> None:
        super().__init__(provider="gpt", model_name=model_name, api_key=api_key)
        self.client = OpenAI(api_key=api_key)

    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            response_format={"type": "json_object"},
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
