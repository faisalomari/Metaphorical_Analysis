# extract_majaz_and_random_non_majaz.py
from pathlib import Path
import pandas as pd
import sys


def extract_majaz_and_random_non_majaz(input_csv: Path,
                                       out_majaz_csv: Path,
                                       out_non_majaz_csv: Path,
                                       seed: int = 42) -> None:
    # Read with UTF-8 BOM (Excel-friendly), fallback to utf-8
    try:
        df = pd.read_csv(input_csv, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(input_csv, encoding="utf-8")

    col = "العنصر البلاغي المستعمل"
    if col not in df.columns:
        raise ValueError(
            f"Column '{col}' not found. Available columns: {list(df.columns)}"
        )

    s = df[col].fillna("").astype(str).str.strip()

    # Majaz rows (contains تشبيه)
    mask_majaz = s.str.contains("تشبيه", na=False)
    df_majaz = df.loc[mask_majaz].copy()

    # Non-majaz rows
    df_non = df.loc[~mask_majaz].copy()

    # Sample non-majaz with same size as majaz (or all if not enough)
    n = len(df_majaz)
    if n == 0:
        print("No rows matched 'تشبيه'. Nothing to extract.")
        return

    if len(df_non) >= n:
        df_non_sample = df_non.sample(n=n, random_state=seed)
    else:
        df_non_sample = df_non.copy()
        print(f"Warning: non-majaz rows ({len(df_non)}) < majaz rows ({n}). Exporting all non-majaz.")

    # Optional: reorder columns (keeps all columns)
    preferred_order = [
        "#", "البيت", "الشاعر", "القصيدة", "التعبير البلاغي",
        "العنصر البلاغي المستعمل", "العنصر البلاغي الثانوي",
        "الثيمة المستعملة", "الشرح", "عدل/احذف",
        "source_file", "source_sheet"
    ]

    def reorder_cols(d: pd.DataFrame) -> pd.DataFrame:
        existing_preferred = [c for c in preferred_order if c in d.columns]
        remaining = [c for c in d.columns if c not in existing_preferred]
        return d[existing_preferred + remaining]

    df_majaz = reorder_cols(df_majaz)
    df_non_sample = reorder_cols(df_non_sample)

    # Ensure output folders exist
    out_majaz_csv.parent.mkdir(parents=True, exist_ok=True)
    out_non_majaz_csv.parent.mkdir(parents=True, exist_ok=True)

    # Write
    df_majaz.to_csv(out_majaz_csv, index=False, encoding="utf-8-sig")
    df_non_sample.to_csv(out_non_majaz_csv, index=False, encoding="utf-8-sig")

    print(f"Input rows: {len(df)}")
    print(f"Majaz rows: {len(df_majaz)} -> {out_majaz_csv}")
    print(f"Random non-majaz rows: {len(df_non_sample)} (seed={seed}) -> {out_non_majaz_csv}")


def main():
    # =========================
    # 🔒 HARDCODED PATHS
    # =========================
    input_csv = Path(r"all.csv").expanduser().resolve()

    out_majaz_csv = Path(r"kenayh_only.csv").expanduser().resolve()
    out_non_majaz_csv = Path(r"non_kenayh_random_same_size.csv").expanduser().resolve()

    # Random seed (same seed => same sampled output)
    seed = 42

    if not input_csv.exists():
        print(f"Input file not found: {input_csv}")
        sys.exit(1)

    extract_majaz_and_random_non_majaz(input_csv, out_majaz_csv, out_non_majaz_csv, seed=seed)


if __name__ == "__main__":
    main()
