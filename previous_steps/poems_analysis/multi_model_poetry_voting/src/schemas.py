from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ModelResult:
    label: str = "no"
    span: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    raw_response: str = ""
    model_name: str = ""
    provider: str = ""
    status: str = "ok"
    error_message: str = ""
    attempt_count: int = 1
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerseRecord:
    verse_index: int
    combined_verse: str
    original_row: dict[str, Any] = field(default_factory=dict)


@dataclass
class VoteDecision:
    voted_label: str
    selected_provider: str
    selected_model_name: str
    selected_confidence: float
    final_span: str
    vote_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
