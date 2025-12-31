from __future__ import annotations

import os
from pathlib import Path
from typing import List

from openai import OpenAI

# ---------- CONFIG ----------
KEY_FILE = "key.txt"
FINAL_PROMPT_FILE = "final_prompt.txt"

POEM_NAME = "Imru1"
DATA_PATH = "../Data"
POETRY_PATH = os.path.join(DATA_PATH,POEM_NAME,"poetry.txt")
OUTPUT_JSONL_FILE = os.path.join(DATA_PATH,POEM_NAME,"Analysation.jsonl")

PARTS_IN_ORDER: List[str] = [
    "prompt_intro.txt",
    "../Elements/Trope.txt",
    "../Elements/Simile.txt",
    "../Elements/Kenning.txt",
    "../Elements/Antonymy.txt",
    "prompt_analysis.txt",
    POETRY_PATH,
]

# MODEL = "gpt-5.2-pro-2025-12-11" #Very Expensive Model
MODEL = "gpt-5.2"
# ----------------------------


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_api_key(base_dir: Path) -> str:
    key_path = base_dir / KEY_FILE
    if not key_path.exists():
        raise FileNotFoundError(f"Missing key file: {key_path.resolve()}")

    key = read_text(key_path).strip()

    # Basic sanity checks
    if not key:
        raise ValueError("key.txt is empty.")
    if any(c.isspace() for c in key):
        raise ValueError("API key contains whitespace. Make sure key.txt has the key on one line only.")

    return key


def merge_prompt_parts(base_dir: Path, parts: List[str]) -> str:
    chunks: List[str] = []
    for filename in parts:
        p = base_dir / filename
        if not p.exists():
            raise FileNotFoundError(f"Missing required prompt part: {p.resolve()}")
        chunks.append(read_text(p).rstrip())
    return "\n\n".join(chunks).rstrip() + "\n"


def main() -> None:
    base_dir = Path(".").resolve()

    # 1) Load key from key.txt (server-side). Do NOT put keys in browser/client code. :contentReference[oaicite:1]{index=1}
    api_key = read_api_key(base_dir)

    # 2) Merge all txt parts into one final prompt file
    final_prompt = merge_prompt_parts(base_dir, PARTS_IN_ORDER)
    final_prompt_path = base_dir / FINAL_PROMPT_FILE
    final_prompt_path.write_text(final_prompt, encoding="utf-8")
    print(f"[OK] Wrote merged prompt -> {final_prompt_path}")

    # 3) Call API
    client = OpenAI(api_key=api_key)  # alternatively, you can export OPENAI_API_KEY env var :contentReference[oaicite:2]{index=2}
    resp = client.responses.create(
        model=MODEL,
        input=final_prompt,
    )

    # 4) Save output (expected JSONL per your prompt instructions)
    output_text = (resp.output_text or "").strip() + "\n"
    out_path = base_dir / OUTPUT_JSONL_FILE
    out_path.write_text(output_text, encoding="utf-8")
    print(f"[OK] Saved model output -> {out_path}")


if __name__ == "__main__":
    main()
