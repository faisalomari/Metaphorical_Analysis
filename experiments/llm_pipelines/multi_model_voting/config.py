from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "prompts"
ELEMENTS_DIR = ROOT_DIR / "elements"
KEYS_DIR = ROOT_DIR / "keys"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "outputs"

SUPPORTED_ELEMENTS = {"Trope", "Similie", "Kenning", "Antonymy"}
SUPPORTED_MODELS = {"gpt", "claude", "gemini", "command_a", "aya", "qwen"}

DEFAULT_MODEL_NAMES = {
    "gpt": "gpt-5.2",
    "claude": "claude-sonnet-4-6",
    "gemini": "gemini-2.5-pro",
    "command_a": "command-a-03-2025",
    "aya": "c4ai-aya-expanse-32b",
    "qwen": "qwen3-max",
}

CLAUDE_MODEL_FALLBACKS = [
    "claude-sonnet-4-6",
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-0",
    "claude-3-7-sonnet-latest",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
]

KEY_FILES = {
    "gpt": KEYS_DIR / "openai_key.txt",
    "claude": KEYS_DIR / "claude_key.txt",
    "gemini": KEYS_DIR / "gemini_key.txt",
    "command_a": KEYS_DIR / "cohere_key.txt",
    "aya": KEYS_DIR / "cohere_key.txt",
    "qwen": KEYS_DIR / "qwen_key.txt",
}

QWEN_BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

RAW_DIRNAME = "raw"
NORMALIZED_DIRNAME = "normalized"
FINAL_DIRNAME = "final"
LOGS_DIRNAME = "logs"

REQUIRED_POEM_COLUMNS = ("Sadr", "Ajuz")
