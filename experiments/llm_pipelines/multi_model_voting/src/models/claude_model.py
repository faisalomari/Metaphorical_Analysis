from __future__ import annotations

from anthropic import Anthropic

from src.models.base_model import BaseModel


class ClaudeModel(BaseModel):
    def __init__(
        self,
        model_name: str,
        api_key: str,
        fallback_model_names: list[str] | None = None,
    ) -> None:
        super().__init__(provider="claude", model_name=model_name, api_key=api_key)
        self.client = Anthropic(api_key=api_key)
        self.fallback_model_names = fallback_model_names or []

    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self._create_message(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        return self._flatten_text(response)

    def explain_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self._create_message(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        return self._flatten_text(response).strip()

    def _candidate_models(self) -> list[str]:
        candidates = [self.model_name, *self.fallback_model_names]
        seen: set[str] = set()
        ordered: list[str] = []
        for name in candidates:
            if name and name not in seen:
                seen.add(name)
                ordered.append(name)
        return ordered

    def _create_message(self, system_prompt: str, user_prompt: str, temperature: float):
        last_error: Exception | None = None
        for candidate in self._candidate_models():
            try:
                response = self.client.messages.create(
                    model=candidate,
                    temperature=temperature,
                    max_tokens=512,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                self.model_name = candidate
                return response
            except Exception as exc:
                last_error = exc
                if not self._is_model_not_found_error(exc):
                    raise
        if last_error is not None:
            raise last_error
        raise RuntimeError("No Claude model candidates available")

    @staticmethod
    def _flatten_text(response) -> str:
        chunks: list[str] = []
        for block in response.content:
            text = getattr(block, "text", "")
            if text:
                chunks.append(text)
        return "".join(chunks)

    @staticmethod
    def _is_model_not_found_error(exc: Exception) -> bool:
        message = str(exc).lower()
        return "not_found_error" in message or "model:" in message
