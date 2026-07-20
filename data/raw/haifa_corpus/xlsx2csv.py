# convert_excels_to_csv.py
from pathlib import Path
import re
import sys

import pandas as pd


def safe_name(s: str) -> str:
    """Make a filename-safe string (keeps Arabic letters)."""
    s = str(s).strip()
    s = re.sub(r'[\\/:*?"<>|]+', "_", s)   # Windows-illegal chars
    s = re.sub(r"\s+", " ", s)
    return s[:150] if len(s) > 150 else s


def convert_folder(input_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_exts = {".xlsx", ".xlsm", ".xltx", ".xltm"}  # modern Excel
    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in excel_exts]

    if not files:
        print(f"No Excel files found in: {input_dir}")
        return

    for xls_path in sorted(files):
        try:
            # Read all sheets
            sheets = pd.read_excel(xls_path, sheet_name=None, engine="openpyxl")
        except Exception as e:
            print(f"[SKIP] Failed reading {xls_path.name}: {e}")
            continue

        base = safe_name(xls_path.stem)

        for sheet_name, df in sheets.items():
            # Keep Arabic and avoid Excel turning things into NaN strings
            df = df.copy()

            out_name = f"{base}__{safe_name(sheet_name)}.csv"
            out_path = output_dir / out_name

            try:
                # utf-8-sig helps Excel display Arabic correctly when opening CSV
                df.to_csv(out_path, index=False, encoding="utf-8-sig")
                print(f"[OK] {xls_path.name} / {sheet_name} -> {out_path.name}")
            except Exception as e:
                print(f"[SKIP] Failed writing {out_name}: {e}")


def main():
    # Usage:
    #   python convert_excels_to_csv.py "C:\path\to\excel_folder" "C:\path\to\csv_folder"
    if len(sys.argv) < 3:
        print("Usage: python convert_excels_to_csv.py <input_excel_folder> <output_csv_folder>")
        sys.exit(1)

    input_dir = Path(sys.argv[1]).expanduser().resolve()
    output_dir = Path(sys.argv[2]).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Input folder does not exist or is not a folder: {input_dir}")
        sys.exit(1)

    convert_folder(input_dir, output_dir)


if __name__ == "__main__":
    main()
