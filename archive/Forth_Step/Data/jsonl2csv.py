# File: jsonl_to_csv_with_verses.py
# Reads:
#   1) analysis.jsonl  (your JSONL output)
#   2) poetry.txt      (numbered verses like: 1) "....")
# Writes:
#   output.csv         (no | verse | مجاز | تشبيه | كناية | طباق)
#
# Notes:
# - For each element column, we store the appearance substring (or TOKENS[i:j]) if exists, else empty.
# - Verse text is cleaned: removes surrounding " or "" if present.

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Dict, Any, List
import os

DIR = "Abu_tammam"
JSONL_FILE = os.path.join(DIR, "Analysation.jsonl")
POETRY_FILE = os.path.join(DIR, "poetry.txt")
OUTPUT_CSV = os.path.join(DIR, DIR + ".csv")

ELEMENTS = ["مجاز", "تشبيه", "كناية", "طباق"]


def clean_outer_quotes(s: str) -> str:
    """
    Remove surrounding quotes if the whole verse is wrapped with "..." or ""..."".
    Keeps internal quotes intact.
    """
    s = s.strip()

    # Remove surrounding double-double quotes first: ""..."" (common in some exports)
    if len(s) >= 4 and s.startswith('""') and s.endswith('""'):
        s = s[2:-2].strip()

    # Remove single surrounding double quotes: "..."
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        s = s[1:-1].strip()

    return s


def load_poetry(poetry_path: Path) -> Dict[int, str]:
    """
    Parses lines like:
      1) ""قَدكَ ... ؟!""
    Returns: {1: "قَدكَ ... ؟!", ...}
    """
    verses: Dict[int, str] = {}

    for line in poetry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r"^\s*(\d+)\)\s*(.*)\s*$", line)
        if not m:
            continue  # skip anything not matching N) ...

        no = int(m.group(1))
        verse_raw = m.group(2).strip()
        verse = clean_outer_quotes(verse_raw)
        verses[no] = verse

    return verses


def load_jsonl(jsonl_path: Path) -> Dict[int, Dict[str, Any]]:
    """
    Returns mapping: no -> full json object
    """
    results: Dict[int, Dict[str, Any]] = {}

    for line_no, line in enumerate(jsonl_path.read_text(encoding="utf-8").splitlines(), start=1):
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON on line {line_no} in {jsonl_path}: {e}") from e

        if "no" not in obj:
            continue
        results[int(obj["no"])] = obj

    return results


def main() -> None:
    jsonl_path = Path(JSONL_FILE)
    poetry_path = Path(POETRY_FILE)
    out_path = Path(OUTPUT_CSV)

    if not jsonl_path.exists():
        raise FileNotFoundError(f"Missing: {jsonl_path.resolve()}")
    if not poetry_path.exists():
        raise FileNotFoundError(f"Missing: {poetry_path.resolve()}")

    verses = load_poetry(poetry_path)
    analysis = load_jsonl(jsonl_path)

    # Build rows for all verse numbers present in poetry.txt (sorted)
    verse_numbers = sorted(verses.keys())

    headers = ["no", "verse"] + ELEMENTS

    rows: List[Dict[str, str]] = []
    for no in verse_numbers:
        row: Dict[str, str] = {"no": str(no), "verse": verses.get(no, "")}

        obj = analysis.get(no, {})
        for el in ELEMENTS:
            exists_key = f"{el}_exists"
            app_key = f"{el}_appearance"

            if obj.get(exists_key) is True:
                val = obj.get(app_key)
                row[el] = "" if val is None else str(val)
            else:
                row[el] = ""

        rows.append(row)

    # Write CSV
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote: {out_path.resolve()}")


if __name__ == "__main__":
    main()
