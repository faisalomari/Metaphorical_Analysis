from __future__ import annotations

import os
from pathlib import Path
from typing import List

from openai import OpenAI

# ---------- CONFIG ----------
KEY_FILE = "key.txt"

POEM_NAME = "Jareer"
DATA_PATH = "../Data"
POETRY_PATH = os.path.join(DATA_PATH, POEM_NAME, "poetry.txt")
OUTPUT_JSONL_FILE = os.path.join(DATA_PATH, POEM_NAME, "Analysation2.jsonl")

# Keep ONLY the “instructional” parts here (NO poetry.txt)
PROMPT_PARTS: List[str] = [
    "prompt_intro.txt",
    "../Elements/Trope.txt",
    "../Elements/Simile.txt",
    "../Elements/Kenning.txt",
    "../Elements/Antonymy.txt",
    "prompt_analysis.txt",
]

MODEL = "gpt-5.2"
# ----------------------------


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_api_key(base_dir: Path) -> str:
    key_path = base_dir / KEY_FILE
    if not key_path.exists():
        raise FileNotFoundError(f"Missing key file: {key_path.resolve()}")

    key = read_text(key_path).strip()

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


def load_verses(poetry_file: Path) -> List[str]:
    """
    Assumption: poetry.txt contains one verse per line.
    Blank lines are ignored.
    """
    raw = read_text(poetry_file)
    verses = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not verses:
        raise ValueError(f"No verses found in: {poetry_file.resolve()}")
    return verses


def strip_code_fences(s: str) -> str:
    """
    If the model wraps output in ```...``` fences, remove them.
    """
    s = s.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        # drop first fence line
        lines = lines[1:]
        # drop last fence line if it is a fence
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    return s


def extract_jsonl_lines(model_text: str) -> List[str]:
    """
    Normalize model output to JSONL lines.
    - Removes code fences
    - Keeps non-empty lines
    """
    cleaned = strip_code_fences(model_text or "")
    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    return lines


def main() -> None:
    base_dir = Path(".").resolve()

    # 1) API key
    api_key = read_api_key(base_dir)

    # 2) Build the reusable prompt template (instructions + element definitions)
    prompt_template = merge_prompt_parts(base_dir, PROMPT_PARTS)

    # 3) Load verses
    poetry_file = (base_dir / POETRY_PATH).resolve()
    verses = load_verses(poetry_file)

    # 4) Prepare output file (overwrite each run; change to append-only if you prefer)
    out_path = (base_dir / OUTPUT_JSONL_FILE).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("", encoding="utf-8")  # reset file at start

    # 5) Call API one verse per request; append each result to JSONL
    client = OpenAI(api_key=api_key)

    for i, verse in enumerate(verses, start=1):
        # IMPORTANT: give the model the verse number explicitly,
        # so it can output {"no": i, ...} correctly.
        input_text = (
            prompt_template
            + "\n\n"
            + f"VERSE_NO: {i}\n"
            + f"VERSE_TEXT: {verse}\n"
        )

        resp = client.responses.create(
            model=MODEL,
            input=input_text,
        )

        lines = extract_jsonl_lines(resp.output_text or "")

        # Append lines to JSONL (ideally 1 line per verse)
        with out_path.open("a", encoding="utf-8") as f:
            for ln in lines:
                f.write(ln + "\n")

        print(f"[OK] Verse {i}/{len(verses)} -> appended {len(lines)} line(s)")

    print(f"[OK] Finished. Saved JSONL -> {out_path}")


if __name__ == "__main__":
    main()
