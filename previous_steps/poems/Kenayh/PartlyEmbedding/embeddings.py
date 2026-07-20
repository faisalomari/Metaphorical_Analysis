# embed_majaz_dataset.py
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List

import pandas as pd
from openai import OpenAI


# -----------------------------
# Helpers
# -----------------------------
def read_key(key_path: Path) -> str:
    key = key_path.read_text(encoding="utf-8").strip()
    if not key:
        raise ValueError(f"key.txt is empty: {key_path}")
    return key


def choose_text_column(df: pd.DataFrame) -> str:
    """
    Prefer the actual verse text column. In your sample, 'التعبير البلاغي' looks like the verse fragment.
    If you prefer 'البيت' or a combination, change here.
    """
    candidates = ["التعبير البلاغي", "البيت"]
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"None of {candidates} found in columns: {list(df.columns)}")


def embed_texts(client: OpenAI,
                texts: List[str],
                model: str = "text-embedding-3-large",
                batch_size: int = 128,
                max_retries: int = 5,
                sleep_base: float = 1.5) -> List[List[float]]:
    """
    Calls embeddings endpoint in batches. Returns list of vectors aligned with `texts`.
    """
    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # Retry loop for transient errors / rate limits
        for attempt in range(max_retries):
            try:
                resp = client.embeddings.create(
                    model=model,
                    input=batch
                )
                # Ensure ordering by index
                data_sorted = sorted(resp.data, key=lambda x: x.index)
                vectors.extend([d.embedding for d in data_sorted])
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait = sleep_base * (2 ** attempt)
                print(f"[WARN] Embedding batch {i//batch_size} failed ({e}). Retrying in {wait:.1f}s...")
                time.sleep(wait)

    if len(vectors) != len(texts):
        raise RuntimeError(f"Embedding count mismatch: got {len(vectors)} vectors for {len(texts)} texts")

    return vectors


def main():
    # =========================
    # 🔒 HARDCODED PATHS (EDIT)
    # =========================
    KEY_TXT = Path(r"key.txt")

    MAJAZ_CSV = Path(r"kenayh_only.csv")
    NON_MAJAZ_CSV = Path(r"non_kenayh_random_same_size.csv")

    OUT_DIR = Path(r"embeddings_out")
    OUT_PARQUET = OUT_DIR / "dataset_with_embeddings.parquet"
    OUT_CSV = OUT_DIR / "dataset_with_embeddings.csv"

    # Embedding settings
    MODEL = "text-embedding-3-large"
    BATCH_SIZE = 128

    # -----------------------------
    # Load
    # -----------------------------
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not KEY_TXT.exists():
        raise FileNotFoundError(f"Missing key.txt at: {KEY_TXT}")
    if not MAJAZ_CSV.exists():
        raise FileNotFoundError(f"Missing majaz csv at: {MAJAZ_CSV}")
    if not NON_MAJAZ_CSV.exists():
        raise FileNotFoundError(f"Missing non-majaz csv at: {NON_MAJAZ_CSV}")

    api_key = read_key(KEY_TXT)
    client = OpenAI(api_key=api_key)

    df_majaz = pd.read_csv(MAJAZ_CSV, encoding="utf-8-sig")
    df_non = pd.read_csv(NON_MAJAZ_CSV, encoding="utf-8-sig")

    df_majaz = df_majaz.copy()
    df_non = df_non.copy()
    df_majaz["label_majaz"] = 1
    df_non["label_majaz"] = 0

    df = pd.concat([df_majaz, df_non], ignore_index=True)

    # Pick text column
    text_col = choose_text_column(df)
    df["text_for_embedding"] = df[text_col].fillna("").astype(str).str.strip()

    # Drop empty texts (cannot embed empty)
    before = len(df)
    df = df[df["text_for_embedding"].str.len() > 0].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"[INFO] Dropped {dropped} rows with empty text.")

    # -----------------------------
    # Embed
    # -----------------------------
    texts = df["text_for_embedding"].tolist()
    print(f"[INFO] Embedding {len(texts)} rows using {MODEL} ...")

    vectors = embed_texts(
        client=client,
        texts=texts,
        model=MODEL,
        batch_size=BATCH_SIZE
    )

    df["embedding"] = vectors
    df["embedding_model"] = MODEL

    # -----------------------------
    # Save
    # -----------------------------
    # Parquet keeps list<float> nicely (recommended)
    df.to_parquet(OUT_PARQUET, index=False)

    # CSV: store embedding as JSON string (large file but portable)
    df_csv = df.copy()
    df_csv["embedding"] = df_csv["embedding"].apply(lambda v: json.dumps(v, ensure_ascii=False))
    df_csv.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("[DONE]")
    print(f"Saved parquet: {OUT_PARQUET}")
    print(f"Saved csv:     {OUT_CSV}")
    print(f"Final shape:   {df.shape}")
    print(f"Text column:   {text_col}")


if __name__ == "__main__":
    main()
