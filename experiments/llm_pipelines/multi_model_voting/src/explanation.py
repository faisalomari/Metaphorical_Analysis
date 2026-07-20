from __future__ import annotations

from src.schemas import ModelResult


def attach_explanation(result: ModelResult, explanation: str) -> ModelResult:
    result.explanation = explanation.strip()
    return result
