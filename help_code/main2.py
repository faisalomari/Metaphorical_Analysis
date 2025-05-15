import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# Load Arabic NLP Model (Hugging Face)
MODEL_NAME = "CAMeL-Lab/bert-base-arabic-camelbert-mix-ner"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

# Create NLP Pipeline
nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, grouped_entities=True)

# Simile Markers
SIMILE_MARKERS = {"كأن", "فكأن", "وكأن", "كما", "مثل", "يشبه", "يشابه"}

def extract_simile(sentence):
    """Extract simile components (marker, smiled noun, similed object)."""
    entities = nlp_pipeline(sentence)
    
    simile_marker = None
    smiled_noun = None
    similed_object = None

    words = sentence.split()
    
    for i, word in enumerate(words):
        clean_word = word.strip("،.!؟")
        
        if clean_word in SIMILE_MARKERS:
            simile_marker = clean_word  # Identify the simile marker
            
            # Try to extract smiled noun (before the marker) & similed object (after the marker)
            if i > 0:
                smiled_noun = words[i-1]  # Previous word as smiled noun
            if i + 1 < len(words):
                similed_object = words[i+1]  # Next word as similed object
            break  # Stop after first simile marker

    return simile_marker, smiled_noun, similed_object

def process_csv(file_path):
    """Process CSV file to extract similes."""
    df = pd.read_csv(file_path)
    
    markers = []
    smiled_nouns = []
    similed_objects = []

    for _, row in df.iterrows():
        marker, smiled_noun, similed_object = extract_simile(row['النص'])
        
        markers.append(marker)
        smiled_nouns.append(smiled_noun)
        similed_objects.append(similed_object)

    df['Simile Marker'] = markers
    df['Smiled Noun'] = smiled_nouns
    df['Similed Object'] = similed_objects
    
    output_file = "simile_extraction_output.csv"
    df.to_csv(output_file, index=False)
    print(f"Processing completed. Output saved to {output_file}")

# Example usage
process_csv("Andalus2.csv")
