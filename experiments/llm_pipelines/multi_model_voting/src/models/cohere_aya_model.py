from __future__ import annotations

import cohere

from src.models.base_model import BaseModel


class CohereAyaModel(BaseModel):
    def __init__(self, model_name: str, api_key: str) -> None:
        super().__init__(provider="aya", model_name=model_name, api_key=api_key)
        self.client = cohere.ClientV2(api_key=api_key)

    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat(
            model=self.model_name,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return self._flatten_text(response)

    def explain_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat(
            model=self.model_name,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return self._flatten_text(response).strip()

    @staticmethod
    def _flatten_text(response) -> str:
        chunks: list[str] = []
        message = getattr(response, "message", None)
        content = getattr(message, "content", []) if message is not None else []
        for block in content or []:
            text = getattr(block, "text", "")
            if text:
                chunks.append(text)
        return "".join(chunks)
