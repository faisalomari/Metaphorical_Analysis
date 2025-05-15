import pandas as pd

# Load file with tashbeeh
df_with = pd.read_csv("data/with/merged_output2.csv")  # has 'النص' and maybe 'TashbeehWords'
df_with = df_with[['النص']]  # Keep only النص
df_with['label'] = 1

# Load file without tashbeeh
df_without = pd.read_csv("data/without/without2.csv")  # has 'التعبير البلاغي'
df_without = df_without.rename(columns={'التعبير البلاغي': 'النص'})  # Rename to match
df_without = df_without[['النص']]  # Keep only النص
df_without['label'] = 0

# Balance the dataset
min_len = min(len(df_with), len(df_without))
df_with_balanced = df_with.sample(n=min_len, random_state=42)
df_without_balanced = df_without.sample(n=min_len, random_state=42)

# Merge the balanced DataFrames
merged_df = pd.concat([df_with_balanced, df_without_balanced], ignore_index=True)

# Shuffle the dataset
merged_df = merged_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save to CSV
merged_df.to_csv("merged_poems_dataset.csv", index=False)

print(f"✅ Done! Saved balanced dataset with {min_len * 2} rows as 'merged_poems_dataset.csv'")
