import pandas as pd

# 1. Load the CSV file
# We use 'utf-8-sig' encoding which is best for reading Arabic CSVs created in Excel
input_file = 'Analyzed_Poetry_Master.csv'
output_file = 'abu_tammam_Poem_2.csv'

try:
    df = pd.read_csv(input_file, encoding='utf-8-sig')
except UnicodeDecodeError:
    # Fallback if the file uses a different encoding
    df = pd.read_csv(input_file, encoding='utf-8')

# 2. Filter for the specific Poet and Poem Title
# We use .strip() on the column names just in case there are hidden spaces
condition = (df['Poet'] == "أبو تمّام") & (df['Poem Title'] ==  "القصيدة رقم 2، ءِ، الكامل")
filtered_df = df[condition]

# 3. Save to a new CSV
if not filtered_df.empty:
    filtered_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"Success! Extracted {len(filtered_df)} rows to '{output_file}'")
else:
    print("No matching rows found. Please check the spelling in your CSV.")