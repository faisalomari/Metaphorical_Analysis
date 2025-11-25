import os
import pandas as pd
import glob
from tqdm import tqdm

folder = "csv_outputs"
output_folder = "txt_outputs"
os.makedirs(output_folder, exist_ok=True)

def find_column(columns, options):
    for opt in options:
        if opt in columns:
            return opt
    return None


# Detect files
files = glob.glob(os.path.join(folder, "*.csv"))
poetry_groups = {}

for f in files:
    base = os.path.basename(f)
    name, _ = os.path.splitext(base)

    if "_يدوي" in name:
        poetry = name.replace("_يدوي", "")
        ftype = "يدوي"
    elif "_آلي" in name or "_الي" in name:
        poetry = name.replace("_آلي", "").replace("_الي", "")
        ftype = "آلي"
    else:
        continue

    poetry_groups.setdefault(poetry, {})[ftype] = f


# ============================
# MAIN PROCESSING
# ============================
for poetry, group in tqdm(poetry_groups.items(), desc="Processing poems"):

    if "يدوي" not in group or "آلي" not in group:
        print(f"Skipping {poetry} – missing files")
        continue

    df_auto = pd.read_csv(group["آلي"], encoding="utf-8-sig")
    df_manual = pd.read_csv(group["يدوي"], encoding="utf-8-sig")

    # Detect columns
    auto_col_verse = find_column(df_auto.columns, ["رقم البيت", "البيت", "رقم_البيت"])
    auto_col_exp   = find_column(df_auto.columns, ["التعبير البلاغي", "التعبير_البلاغي"])
    auto_col_elem  = find_column(df_auto.columns,
                                ["العنصر البلاغي", "العنصر البلاغي المستعمل", "العنصر_البلاغي"])

    man_col_verse = find_column(df_manual.columns, ["رقم البيت", "البيت", "رقم_البيت"])
    man_col_exp   = find_column(df_manual.columns, ["التعبير البلاغي", "التعبير_البلاغي"])
    man_col_elem  = find_column(df_manual.columns,
                               ["العنصر البلاغي", "العنصر البلاغي المستعمل", "العنصر_البلاغي"])

    # Convert to int
    df_auto[auto_col_verse] = pd.to_numeric(df_auto[auto_col_verse], errors="coerce").fillna(-1).astype(int)
    df_manual[man_col_verse] = pd.to_numeric(df_manual[man_col_verse], errors="coerce").fillna(-1).astype(int)

    max_verse = max(df_auto[auto_col_verse].max(), df_manual[man_col_verse].max())

    # Fast grouping by verse
    auto_grouped = df_auto.groupby(auto_col_verse)
    manual_grouped = df_manual.groupby(man_col_verse)

    # Output file
    out_path = os.path.join(output_folder, f"{poetry}.txt")
    with open(out_path, "w", encoding="utf-8") as txt:

        portion_num = 1

        for start in tqdm(range(1, max_verse + 1, 5), desc=f"{poetry} portions", leave=False):
            end = start + 4

            txt.write(f"portion_{portion_num}:\n")
            txt.write("\"\"\"\n")

            for verse in range(start, end + 1):

                auto_rows = auto_grouped.get_group(verse) if verse in auto_grouped.groups else None
                man_rows  = manual_grouped.get_group(verse) if verse in manual_grouped.groups else None

                if auto_rows is None and man_rows is None:
                    continue

                # === Automatic (combine all elements into list) ===
                if auto_rows is not None:
                    elements = [str(r[auto_col_elem]) for _, r in auto_rows.iterrows()]
                    combined = ", ".join(elements)
                    txt.write(f"{verse} | آلي  | {combined}\n")

                # === Manual (combine all elements) ===
                if man_rows is not None:
                    elements = [str(r[man_col_elem]) for _, r in man_rows.iterrows()]
                    combined = ", ".join(elements)
                    txt.write(f"{verse} | يدوي | {combined}\n")

                txt.write("\n")

            txt.write("\"\"\"\n\n")
            portion_num += 1

    print(f"Saved: {out_path}")

print("\nAll TXT files created successfully!")
