from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd

from config import REQUIRED_POEM_COLUMNS
from src.schemas import VerseRecord


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_api_key(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing key file: {path}")
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"Key file is empty: {path}")
    return key


def load_poem_csv(path: Path, limit: int | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig")
    missing = [column for column in REQUIRED_POEM_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(
            f"Input CSV is missing required columns: {', '.join(missing)}"
        )

    df = df.head(limit).copy() if limit is not None else df.copy()
    df["Sadr"] = df["Sadr"].fillna("")
    df["Ajuz"] = df["Ajuz"].fillna("")
    df["combined_verse"] = (df["Sadr"].astype(str) + " " + df["Ajuz"].astype(str)).str.strip()
    df["verse_index"] = range(1, len(df) + 1)
    return df


def dataframe_to_verse_records(df: pd.DataFrame) -> list[VerseRecord]:
    records: list[VerseRecord] = []
    for row in df.to_dict(orient="records"):
        records.append(
            VerseRecord(
                verse_index=int(row["verse_index"]),
                combined_verse=str(row["combined_verse"]),
                original_row=row,
            )
        )
    return records


def append_jsonl(path: Path, payload: dict) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def save_csv(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
