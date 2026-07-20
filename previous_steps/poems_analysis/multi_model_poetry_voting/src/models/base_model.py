from __future__ import annotations

from abc import ABC, abstractmethod


class BaseModel(ABC):
    def __init__(self, provider: str, model_name: str, api_key: str) -> None:
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    def label_json(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        raise NotImplementedError

    @abstractmethod
    def explain_text(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        raise NotImplementedError
