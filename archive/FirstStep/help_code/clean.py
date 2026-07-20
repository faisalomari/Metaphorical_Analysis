import pandas as pd
import re

# Arabic diacritics pattern
arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670\u06D6-\u06ED]')

# Optional additional characters to remove, e.g., "]"
def clean_text(text):
    text = re.sub(arabic_diacritics, '', text)
    text = text.replace("]", "").replace("[", "")  # optional cleanup
    return text.strip()

# Load dataset
df = pd.read_csv("merged_poems_dataset.csv")

# Clean text
df['النص'] = df['النص'].apply(clean_text)

# Save cleaned data
df.to_csv("merged_poems_dataset_cleaned.csv", index=False)

print("✅ Cleaned file saved as 'merged_poems_dataset_cleaned.csv'")
