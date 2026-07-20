import pandas as pd

# === CONFIG ===
INPUT_CSV = "elemnts_from_poetries.csv"
OUTPUT_TXT = "training_elements.txt"


def main():
    # Load CSV
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")

    # Open output text file
    with open(OUTPUT_TXT, "w", encoding="utf-8-sig") as f:

        for i, row in df.iterrows():
            portion_num = i + 1

            # Extract fields
            arabic_name = row["العنصر البلاغي"]
            english_name = row["rhetorical element"]
            arabic_expl = row["شرح"]
            english_expl = row["explaination"]

            example1 = row["مثال امرؤ القيس 1"]
            example2 = row["مثال امرؤ القيس 8"]
            example3 = row["مثال النابغة الذبياني"]
            example4 = row["مثال جرير"]
            example5 = row["مثال أبو تمام"]

            # Write portion
            f.write(f"portion{portion_num}:\n")
            f.write('""""\n')
            f.write(f"اسم العنصر البلاغي: {arabic_name}\n")
            f.write(f"rhetorical element name: {english_name}\n")
            f.write(f"شرح العنصر البلاغي: {arabic_expl}\n")
            f.write(f"explaination: {english_expl}\n")
            f.write(f"مثال1: {example1}\n")
            f.write(f"مثال2: {example2}\n")
            f.write(f"مثال3: {example3}\n")
            f.write(f"مثال4: {example4}\n")
            f.write(f"مثال5: {example5}\n")
            f.write('""""\n\n')

    print("DONE! File created:", OUTPUT_TXT)

if __name__ == "__main__":
    main()
