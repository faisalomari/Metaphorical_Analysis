import pandas as pd

# File paths
input_file = "Andalus.xlsx"  # Replace with your .xlsx file path
output_file = "Andalus.csv"  # Replace with your desired .csv file path

# Load the Excel file, ensuring "البيت" is read as a string
df = pd.read_excel(input_file, dtype={"البيت": str})

# Save to CSV
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"Converted file saved as {output_file}")
