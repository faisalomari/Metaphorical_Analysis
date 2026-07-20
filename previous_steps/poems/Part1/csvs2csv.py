# merge_csvs_into_one.py
from pathlib import Path
import pandas as pd
import sys


def merge_csvs(input_csv_dir: Path, output_csv_path: Path) -> None:
    csv_files = sorted([p for p in input_csv_dir.glob("*.csv") if p.is_file()])

    if not csv_files:
        print(f"No CSV files found in: {input_csv_dir}")
        return

    dfs = []
    for p in csv_files:
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
        except UnicodeDecodeError:
            # fallback if a file wasn't saved with BOM
            df = pd.read_csv(p, encoding="utf-8")

        df["source_file"] = p.name

        # If file name is like: ExcelName__SheetName.csv
        if "__" in p.stem:
            df["source_sheet"] = p.stem.split("__", 1)[1]
        else:
            df["source_sheet"] = ""

        dfs.append(df)

        print(f"[OK] Loaded {p.name} -> {df.shape[0]} rows, {df.shape[1]} cols")

    merged = pd.concat(dfs, ignore_index=True, sort=False)

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

    print("\nDone.")
    print(f"Merged files: {len(csv_files)}")
    print(f"Final shape: {merged.shape}")
    print(f"Saved to: {output_csv_path}")


def main():
    # Usage:
    #   python merge_csvs_into_one.py "C:\path\to\csv_folder" "C:\path\to\output\all.csv"
    if len(sys.argv) < 3:
        print("Usage: python merge_csvs_into_one.py <input_csv_folder> <output_csv_path>")
        sys.exit(1)

    input_dir = Path(sys.argv[1]).expanduser().resolve()
    output_path = Path(sys.argv[2]).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input folder does not exist or is not a folder: {input_dir}")
        sys.exit(1)

    merge_csvs(input_dir, output_path)


if __name__ == "__main__":
    main()
