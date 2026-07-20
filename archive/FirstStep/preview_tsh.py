import pandas as pd
import random

# Define the tashbeeh keywords
start_with_demoy_tokens = ["كأن", "فكأن", "وكأن", "فكأن"]
start_with_tokens = ["بمثل", "فمثل", "ومثل", "كال", "فكال", "وكال"]
all_word_tokens = ["كما", "كأنما", "وكما", "فكما", "وكأنما", "فكأنما"]
verb_tokens = ["حسب", "خال"]
verb_tokens2 = ["شبه", "ظن"]

# Combine all into a single list
tashbeeh_keywords = (
    start_with_demoy_tokens +
    start_with_tokens +
    all_word_tokens +
    verb_tokens +
    verb_tokens2
)

# Load the output CSV
df = pd.read_csv("output.csv")

# Prepare the list of samples
samples = []

# Drop rows with empty poems
df = df[df["النص"].notna() & df["النص"].str.strip().astype(bool)]

# Loop over each poem and check for the presence of any tashbeeh word
for _, row in df.iterrows():
    poem = row["النص"]
    for keyword in tashbeeh_keywords:
        if keyword in poem:
            samples.append({
                "tashbeeh_word": keyword,
                "poem": poem,
                "poem_without_tashbeeh": poem.replace(keyword, "")
            })

# Convert to DataFrame
samples_df = pd.DataFrame(samples)

# Group by tashbeeh word and sample up to 10 poems for each
final_samples = (
    samples_df
    .drop_duplicates(subset=["tashbeeh_word", "poem"])  # Ensure uniqueness
    .groupby("tashbeeh_word", group_keys=False)
    .apply(lambda g: g.sample(n=min(10, len(g)), random_state=42))
)

# Save to Excel with Arabic character support
final_samples.to_excel("tashbeeh_samples.xlsx", index=False)

print("✅ Saved up to 10 poems per tashbeeh word to tashbeeh_samples.xlsx")
