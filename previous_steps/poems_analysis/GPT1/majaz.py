import pandas as pd
import json
from tqdm import tqdm
from openai import OpenAI

# ===============================
# CONFIG
# ===============================
CSV_PATH = "abu_tammam_Poem_2.csv"
OUTPUT_PATH = "majaz_predictions.jsonl"
MODEL_NAME = "gpt-4.1-mini"   # or gpt-4.1 / gpt-4o-mini / gpt-5 if available

# ===============================
# LOAD API KEY
# ===============================
with open("key.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)

# ===============================
# EXPLANATION BLOCK (REUSABLE)
# ===============================
TROPE_EXPLANATION = """
Arabic name: مجاز
English name: Trope

Arabic explanation:
المجاز هو استخدام اللفظ في غير معناه الأصلي لعلاقة بين المعنيين
مع وجود قرينة تمنع إرادة المعنى الحقيقي.

English explanation:
A trope (figurative expression) uses a word in a non-literal sense
based on an associative relationship, with a contextual clue that
blocks the literal meaning.
"""

# ===============================
# PROMPT BUILDER
# ===============================
def build_prompt(verse: str) -> str:
    return f"""
You are a STRICT JSON generator.

Task:
Determine whether the following Arabic verse contains **MAJAZ (Trope)**.

Definition:
- مجاز: استعمال اللفظ في غير معناه الحقيقي لعلاقة مع قرينة مانعة من إرادة المعنى الحقيقي.

Rules (VERY IMPORTANT):
- Output MUST be valid JSON
- Output ONLY JSON
- NO explanations outside JSON
- NO markdown
- NO comments
- If no majaz → label=0 and span="NONE"

JSON schema (exact):
{{
  "label": 0 or 1,
  "span": "exact words from the verse" or "NONE",
  "reasoning": "very short explanation"
}}

Verse:
{verse}
"""


import re

def safe_json_load(text):
    if not text or not isinstance(text, str):
        raise ValueError("Empty response")

    # Remove markdown code fences if present
    text = re.sub(r"^```json\s*", "", text.strip())
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(CSV_PATH)

# Combine Sadr + Ajuz into one verse
df["verse"] = df["Sadr"].fillna("") + " " + df["Ajuz"].fillna("")

# ===============================
# RUN INFERENCE
# ===============================
with open(OUTPUT_PATH, "w", encoding="utf-8") as fout:
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        verse = row["verse"].strip()
        if not verse:
            continue

        prompt = build_prompt(verse)

        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )

            raw = response.choices[0].message.content

            parsed = safe_json_load(raw)

            output = {
                "poet": row["Poet"],
                "poem_title": row["Poem Title"],
                "verse": verse,
                "label": parsed["label"],
                "span": parsed["span"],
                "reasoning": parsed["reasoning"],
                "raw_model_output": raw  # keep for auditing
            }

            fout.write(json.dumps(output, ensure_ascii=False) + "\n")

        except Exception as e:
            fout.write(json.dumps({
                "verse": verse,
                "error": str(e),
                "raw_model_output": raw if "raw" in locals() else None
            }, ensure_ascii=False) + "\n")
