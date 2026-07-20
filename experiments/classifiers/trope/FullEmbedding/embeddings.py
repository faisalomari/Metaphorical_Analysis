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

        for attempt in range(max_retries):
            try:
                resp = client.embeddings.create(
                    model=model,
                    input=batch
                )
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
    # 🔒 HARDCODED PATHS
    # =========================
    KEY_TXT = Path(r"key.txt")
    MAJAZ_CSV = Path(r"majaz_dataset.csv")
    NON_MAJAZ_CSV = Path(r"non_majaz_random_sample.csv")

    OUT_DIR = Path(r"embeddings_out")
    OUT_PARQUET = OUT_DIR / "dataset_with_embeddings.parquet"
    OUT_CSV = OUT_DIR / "dataset_with_embeddings.csv"

    MODEL = "text-embedding-3-large"
    BATCH_SIZE = 128

    # -----------------------------
    # Load
    # -----------------------------
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not KEY_TXT.exists():
        raise FileNotFoundError(f"Missing key.txt at: {KEY_TXT}")
    
    api_key = read_key(KEY_TXT)
    client = OpenAI(api_key=api_key)

    df_majaz = pd.read_csv(MAJAZ_CSV, encoding="utf-8-sig")
    df_non = pd.read_csv(NON_MAJAZ_CSV, encoding="utf-8-sig")

    df_majaz["label_majaz"] = 1
    df_non["label_majaz"] = 0

    df = pd.concat([df_majaz, df_non], ignore_index=True)

    # -----------------------------
    # NEW LOGIC: Conditional Text Selection
    # -----------------------------
    primary_col = "البيت_الكامل"
    fallback_col = "التعبير البلاغي"

    # Ensure columns exist before processing
    for col in [primary_col, fallback_col]:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing from CSV.")

    # 1. Clean up strings and treat whitespace-only as NaN
    df[primary_col] = df[primary_col].astype(str).str.strip().replace(['', 'nan', 'None'], pd.NA)
    df[fallback_col] = df[fallback_col].astype(str).str.strip().replace(['', 'nan', 'None'], pd.NA)

    # 2. Apply logic: Use primary_col, if NA use fallback_col
    df["text_for_embedding"] = df[primary_col].fillna(df[fallback_col])

    # Drop rows where BOTH were empty
    before = len(df)
    df = df[df["text_for_embedding"].notna()].reset_index(drop=True)
    dropped = before - len(df)
    if dropped:
        print(f"[INFO] Dropped {dropped} rows where both '{primary_col}' and '{fallback_col}' were empty.")

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
    df.to_parquet(OUT_PARQUET, index=False)

    df_csv = df.copy()
    df_csv["embedding"] = df_csv["embedding"].apply(lambda v: json.dumps(v, ensure_ascii=False))
    df_csv.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print("[DONE]")
    print(f"Final shape: {df.shape}")
    print(f"Logic used: Used '{primary_col}' with fallback to '{fallback_col}'")


if __name__ == "__main__":
    main()