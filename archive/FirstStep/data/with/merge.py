import pandas as pd
import os

# List of Excel files (as shown in your screenshot)
excel_files = [
    "abasy.xlsx",
    "amaoy.xlsx",
    "andalus.xlsx",
    "d_veterans.xlsx",
    "jahly.xlsx",
    "mamloky.xlsx",
    "unknown.xlsx",
    "veterans.xlsx"
]

# Output merged CSV file
merged_csv_file = "merged_output.csv"

# Create an empty list to store DataFrames
dfs = []

# Loop through each Excel file
for file in excel_files:
    # Convert Excel to DataFrame
    df = pd.read_excel(file, dtype={"البيت": str})
    
    # Optionally save individual CSVs (uncomment if needed)
    # csv_file = file.replace(".xlsx", ".csv")
    # df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    
    # Append to list
    dfs.append(df)

# Concatenate all DataFrames
merged_df = pd.concat(dfs, ignore_index=True)

# Save merged CSV
merged_df.to_csv(merged_csv_file, index=False, encoding="utf-8-sig")

print(f"All files merged and saved as {merged_csv_file}")
