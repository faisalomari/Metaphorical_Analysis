import pandas as pd
import os

# 1. Set the path to the folder containing your xlsx files
folder_path = 'Full_Poems'
output_file = 'merged_poets_data.csv'

all_dataframes = []

# 2. Loop through every file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".xlsx"):
        file_path = os.path.join(folder_path, filename)
        
        print(f"Processing: {filename}")
        
        # Read the excel file
        # We use try/except in case a file is corrupted or empty
        try:
            df = pd.read_excel(file_path)
            
            # Optional: Add a column to track which file the data came from
            df['source_file'] = filename 
            
            all_dataframes.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")

# 3. Merge all dataframes into one
if all_dataframes:
    merged_df = pd.concat(all_dataframes, ignore_index=True)

    # 4. Export to CSV with Arabic-friendly encoding
    # 'utf-8-sig' is the key for Arabic text to show correctly in Excel
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nSuccess! Merged file saved as: {output_file}")
else:
    print("No xlsx files found in the directory.")