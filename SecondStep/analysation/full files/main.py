import pandas as pd
import os

file_path = "full_poems.xlsx"

# Load Excel file
xls = pd.ExcelFile(file_path)

# Create output folder
output_folder = "csv_outputs"
os.makedirs(output_folder, exist_ok=True)

for sheet in xls.sheet_names:
    # Read each sheet
    df = pd.read_excel(file_path, sheet_name=sheet)
    
    # Create safe file name
    safe_sheet_name = sheet.replace("/", "_").replace("\\", "_")
    
    # Output path
    csv_path = os.path.join(output_folder, f"{safe_sheet_name}.csv")
    
    # Save with UTF-8-SIG for proper Arabic display
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    print(f"Saved: {csv_path}")

print("\nAll sheets saved as CSV successfully!")
