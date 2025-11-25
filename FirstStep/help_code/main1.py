import pandas as pd
import re

class WordAnalyzer:
    @staticmethod
    def remove_Diacritics(word):
        """Remove Arabic diacritics from a word."""
        return re.sub(r'[\u064B-\u0652]', '', word)  # Arabic diacritic range

    @staticmethod
    def clean_word(word):
        """Remove diacritics and non-alphabetic characters."""
        return ''.join([char for char in WordAnalyzer.remove_Diacritics(word) if char.isalpha() or char.isspace()])

def identification_tashbeeh_by_line(line):
    """Identify simile markers in a line of poetry."""
    start_with_tokens = {"بمثل", "فمثل", "ومثل", "كال", "فكال", "وكال"}
    start_with_demoy_tokens = {"كأن", "فكأن", "وكأن"}
    all_word_tokens = {"كما", "كأنما", "وكما", "فكما", "وكأنما", "فكأنما"}
    
    words = line.split()
    identified_words = []

    for word in words:
        clean_word = WordAnalyzer.clean_word(word)

        # Check if word is a known simile marker
        if clean_word in all_word_tokens:
            identified_words.append(clean_word)
            continue
        
        # Check if word starts with specific simile markers
        for token in start_with_tokens | start_with_demoy_tokens:
            if clean_word.startswith(token):
                identified_words.append(clean_word)
                break  # Avoid duplicate detection
    
    return ' '.join(identified_words)  # Return identified words as space-separated string

def process_csv(file_path):
    """Process the input CSV and extract simile markers."""
    df = pd.read_csv(file_path)
    df['Identified Words'] = df['النص'].apply(identification_tashbeeh_by_line)
    
    output_file = "processed_output.csv"
    df.to_csv(output_file, index=False)
    print(f"Processing completed. Output saved to {output_file}")

# Example usage
process_csv("Andalus2.csv")
