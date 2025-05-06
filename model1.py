import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from sklearn.metrics import accuracy_score

# Load the dataset
df = pd.read_csv("merged_poems_dataset_cleaned.csv")

# Split into train, validation, and test sets
train_df, temp_df = train_test_split(df, test_size=0.95, stratify=df['label'], random_state=42)
# df = temp_df
# train_df, temp_df = train_test_split(df, test_size=0.9, stratify=df['label'], random_state=42)
val_df, test_df = train_test_split(temp_df, test_size=0.98, stratify=temp_df['label'], random_state=42)

# Load tokenizer
model_name = "aubmindlab/bert-base-arabertv2"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Tokenization function
def tokenize_example(example):
    return tokenizer(example['النص'], truncation=True, padding="max_length")

# Convert to HuggingFace Datasets
train_ds = Dataset.from_pandas(train_df.reset_index(drop=True))
val_ds = Dataset.from_pandas(val_df.reset_index(drop=True))
test_ds = Dataset.from_pandas(test_df.reset_index(drop=True))

# Tokenize
train_ds = train_ds.map(tokenize_example, batched=True)
val_ds = val_ds.map(tokenize_example, batched=True)
test_ds = test_ds.map(tokenize_example, batched=True)

# Remove unused columns for training
train_ds = train_ds.remove_columns(['النص'])
val_ds = val_ds.remove_columns(['النص'])
test_ds = test_ds.remove_columns(['النص'])

# Load model
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = logits.argmax(axis=-1)
    acc = accuracy_score(labels, predictions)
    return {"accuracy": acc}

# Define training arguments
training_args = TrainingArguments(
    output_dir="./cls_model",
    evaluation_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    num_train_epochs=5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    logging_dir='./logs',
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    compute_metrics=compute_metrics
)

# Train
trainer.train()

# Evaluate on test set
results = trainer.evaluate(test_ds)
print("📊 Test Results:", results)
