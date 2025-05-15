import pandas as pd

# Load the CSV file
input_file = "Amaoy2.csv"  # Replace with your input CSV file path
output_file = "output.csv"  # Replace with your desired output file path

# Load the CSV data
df = pd.read_csv(input_file, encoding="utf-8")  # Ensure UTF-8 encoding when reading

# Define the words to filter (you can modify this list)
words_to_filter = ["كَأنَّ", "كَما", "كَأَنَّ"]  # Example words to filter

# Define a function to filter words from the poetry column
def filter_poetry(poetry):
    poetry = str(poetry)  # Convert to string to handle non-string values
    for word in words_to_filter:
        poetry = poetry.replace(word, "")
    return poetry

# Apply the function to the poetry column and create a new column
df["البيت بعد التصفية"] = df["البيت"].apply(filter_poetry)

# Save the updated DataFrame to a new CSV file
df.to_csv(output_file, index=False, encoding="utf-8-sig")  # Save with UTF-8 encoding

print(f"Filtered file saved as {output_file}")
