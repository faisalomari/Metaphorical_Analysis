from __future__ import annotations

import json
import re
from typing import Any

from src.schemas import ModelResult

CONFIDENCE_BAND_TO_SCORE = {
    "very_low": 0.1,
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "very_high": 0.9,
}


def extract_json_object(text: str) -> str:
    stripped = (text or "").strip()
    stripped = re.sub(r"^```json\s*", "", stripped, flags=re.IGNORECASE)
    stripped = re.sub(r"^```\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in response")
    return stripped[start : end + 1]


def normalize_label(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return "yes" if float(value) >= 0.5 else "no"

    text = str(value or "").strip().lower()
    yes_values = {"yes", "1", "true", "present", "exists", "y"}
    no_values = {"no", "0", "false", "absent", "none", "n"}
    if text in yes_values:
        return "yes"
    if text in no_values:
        return "no"
    raise ValueError(f"Unsupported label value: {value}")


def normalize_confidence(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, str):
        cleaned = value.strip().replace("%", "")
        number = float(cleaned)
        if "%" in value or number > 1:
            number = number / 100.0
    else:
        number = float(value)
        if number > 1:
            number = number / 100.0
    if number < 0:
        number = 0.0
    if number > 1:
        number = 1.0
    return round(number, 4)


def normalize_confidence_band(value: Any) -> float:
    text = str(value or "").strip().lower()
    if text not in CONFIDENCE_BAND_TO_SCORE:
        raise ValueError(f"Unsupported confidence band: {value}")
    return CONFIDENCE_BAND_TO_SCORE[text]


def parse_model_response(
    raw_text: str,
    provider: str,
    model_name: str,
    attempt_count: int = 1,
) -> ModelResult:
    json_blob = extract_json_object(raw_text)
    data = json.loads(json_blob)

    label = normalize_label(data.get("label"))
    span = str(data.get("span") or "").strip()
    if data.get("confidence_band") not in (None, ""):
        confidence = normalize_confidence_band(data.get("confidence_band"))
    else:
        confidence = normalize_confidence(data.get("confidence"))
    reasoning = str(data.get("reasoning") or "").strip()

    if label == "no":
        span = ""

    return ModelResult(
        label=label,
        span=span,
        confidence=confidence,
        reasoning=reasoning,
        raw_response=raw_text,
        model_name=model_name,
        provider=provider,
        status="ok",
        attempt_count=attempt_count,
    )


def build_error_result(
    raw_text: str,
    provider: str,
    model_name: str,
    error_message: str,
    attempt_count: int = 1,
) -> ModelResult:
    return ModelResult(
        label="no",
        span="",
        confidence=0.0,
        reasoning="",
        raw_response=raw_text,
        model_name=model_name,
        provider=provider,
        status="error",
        error_message=error_message,
        attempt_count=attempt_count,
    )
