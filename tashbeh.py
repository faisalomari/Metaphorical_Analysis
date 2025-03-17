#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

# =============================================================================
# A simple class for a word in a poem (like your Java wordInPoem)
# =============================================================================
class WordInPoem:
    def __init__(self, index, word):
        self.index = index
        self.word = word

    def __repr__(self):
        return f"({self.index}: {self.word})"


# =============================================================================
# The helper WordAnalyzer class
# (Note: The following implementation uses dummy analysis.
#  In your real system you would integrate with your Arabic morphology analyzer.)
# =============================================================================
class WordAnalyzer:
    @staticmethod
    def check_on(text_to_be_analyzed):
        """
        Simulate a morphological analysis of the word.
        Returns a list of dictionaries (or None if nothing is found).
        In a real implementation you would call your analyzer.
        """
        analysis = []
        if text_to_be_analyzed and text_to_be_analyzed.strip():
            # Dummy logic: if the word starts with "ك" then assume it is a verb;
            # otherwise treat it as a noun.
            typ = "فعل" if text_to_be_analyzed.startswith("ك") else "اسم"
            prefix = "#"  # default no prefix
            root = text_to_be_analyzed  # for demonstration, use the original word
            postag = "مجرور" if "م" in text_to_be_analyzed else ""
            entry = {
                "stem": WordAnalyzer.remove_diacritics(text_to_be_analyzed),
                "root": root,
                "type": typ,
                "prefix": prefix,
                "lemmePattern": "",
                "Suffix": "",
                "status": "",
                "1": "",
                "2": "",
                "postag": postag,
                "4": "",
                "5": "",
                "6": "",
                "7": ""
            }
            analysis.append(entry)
        return analysis if analysis else None

    @staticmethod
    def remove_diacritics(word):
        """
        Remove Arabic diacritics from the word.
        """
        diacritics = {"ْ", "ّ", "ُ", "ٌ", "َ", "ً", "ِ", "ٍ"}
        return "".join(ch for ch in word if ch not in diacritics)

    @staticmethod
    def remove_last_diac(word):
        """
        Remove the last character if it is a diacritic.
        """
        if word and word[-1] in {"ْ", "ّ", "ُ", "ٌ", "َ", "ً", "ِ", "ٍ"}:
            return word[:-1]
        return word

    @staticmethod
    def get_letters(word):
        """
        Return only the alphabetic letters (and spaces) from the word.
        """
        return "".join(ch if ch.isalpha() or ch.isspace() else "" for ch in word)


# =============================================================================
# The function that “identifies tashbeeh” in a given verse.
# It receives two lists of WordInPoem objects (first_part and second_part),
# merges them, and then applies several tests (similar to your Java code).
# =============================================================================
def identification_tashbeeh_by_line(first_part, second_part):
    # Define token arrays (exact strings as in your Java code)
    start_with_demoy_tokens = ["كأن", "فكأن", "وكأن", "فكأن"]
    print(start_with_demoy_tokens)
    start_with_tokens = ["بمثل", "فمثل", "ومثل", "كال", "فكال", "وكال"]
    all_word_tokens = ["كما", "كأنما", "وكما", "فكما", "وكأنما", "فكأنما"]
    verb_tokens = ["حسب", "خال"]
    verb_tokens2 = ["شبه", "ظن"]

    identification_tashbeeh = []  # To hold WordInPoem objects matching criteria

    # Combine the two parts (like firstPart.addAll(secondPart) in Java)
    all_words_in_line = first_part + second_part

    for entry_word in all_words_in_line:
        word = entry_word.word
        word_analysis1 = None

        # Try to get analysis for the word
        try:
            word_analysis1 = WordAnalyzer.check_on(word)
        except Exception as ex:
            word_analysis1 = None

        # If no analysis, try after removing diacritics
        if word_analysis1 is None:
            try:
                word_analysis1 = WordAnalyzer.check_on(WordAnalyzer.remove_diacritics(word))
            except Exception as ex:
                word_analysis1 = None

        flag1 = False
        if word_analysis1 is not None and len(word_analysis1) > 0:
            for entry in word_analysis1:
                # Print the type for debugging (you can remove or comment out this line)
                print(entry.get("type", "") + "**************************************")
                # If the word’s letters contain "مثل" and its type includes "فعل"
                if "مثل" in WordAnalyzer.get_letters(word) and "فعل" in entry.get("type", ""):
                    flag1 = True
                    print(entry.get("type", ""))
                # Check if the word (without diacritics) starts with any token from start_with_tokens,
                # and the entry’s prefix is not "#"
                for demword in start_with_tokens:
                    if WordAnalyzer.remove_diacritics(word).startswith(demword) and entry.get("prefix", "") != "#":
                        identification_tashbeeh.append(entry_word)
                        break  # exit inner loop
            if flag1:
                break  # exit word loop if flag1 is true
            else:
                # If the letters contain "مثل" but not "مثلث", add the word and stop processing further.
                if "مثل" in WordAnalyzer.get_letters(word) and "مثلث" not in WordAnalyzer.get_letters(word):
                    identification_tashbeeh.append(entry_word)
                    break

        # Try another analysis using the original check
        word_analysis = None
        try:
            word_analysis = WordAnalyzer.check_on(word)
        except Exception as ex:
            word_analysis = None

        flag = False
        if word_analysis is not None and len(word_analysis) > 0:
            for demword in start_with_demoy_tokens:
                print(demword)  # Debug print
                for entry in word_analysis:
                    typ = entry.get("type", "")
                    prefix = entry.get("prefix", "")
                    # Check conditions similar to your Java conditions
                    if ("حرف ناسخ" in typ) or (("حرف الجر" in prefix) and ("ال:التعريف" in prefix)) or \
                       (prefix == "كَ: حرف التشبيه" and "فعل" not in typ):
                        if WordAnalyzer.remove_diacritics(word).startswith(demword):
                            identification_tashbeeh.append(entry_word)
                            flag = True
                            break
                if flag:
                    break

        # Check for words that match exactly one of the tokens in all_word_tokens.
        for demword in all_word_tokens:
            if WordAnalyzer.remove_diacritics(word) == demword:
                identification_tashbeeh.append(entry_word)
                break

        # Check using verb_tokens (first set)
        if word_analysis is not None and len(word_analysis) > 0:
            for entry in word_analysis:
                for demword in verb_tokens:
                    if "فعل" in entry.get("type", ""):
                        root = entry.get("root", "")
                        is_demoy = False
                        if demword != "خال":
                            if demword == "حسب" and root == demword:
                                is_demoy = True
                            if demword in WordAnalyzer.remove_diacritics(word) and root == demword:
                                is_demoy = True
                        else:
                            if demword in WordAnalyzer.remove_diacritics(word) and (root == "خلل" or root == "خيل"):
                                is_demoy = True
                        if is_demoy:
                            identification_tashbeeh.append(entry_word)
                            break

        # Check using verb_tokens2 (second set)
        for demword in verb_tokens2:
            if word_analysis is not None and len(word_analysis) > 0:
                for entry in word_analysis:
                    if "فعل" in entry.get("type", ""):
                        root = entry.get("root", "")
                        is_demoy = False
                        if demword in WordAnalyzer.remove_diacritics(word) and root == demword:
                            is_demoy = True
                        if is_demoy:
                            identification_tashbeeh.append(entry_word)
                            break

        # A final check if the word length is > 1:
        if len(word) > 1:
            try:
                word_analysis = WordAnalyzer.check_on(word)
            except Exception as ex:
                word_analysis = None
            isval = True
            pre = "#"
            if word_analysis is not None and len(word_analysis) > 0:
                for entry in word_analysis:
                    prefix = entry.get("prefix", "")
                    postag = entry.get("postag", "")
                    if (prefix == "كَ: حرف التشبيه" or prefix == "كَ: حرف الجر") and \
                       (WordAnalyzer.remove_diacritics(word).startswith("كريم") or ("مجرور" not in postag)):
                        isval = False
                    if prefix == "كَ: حرف التشبيه" or prefix == "كَ: حرف الجر":
                        pre = prefix
                if isval and (pre == "كَ: حرف التشبيه" or pre == "كَ: حرف الجر"):
                    identification_tashbeeh.append(entry_word)

    print()
    print("Demoy is done!")
    return identification_tashbeeh


# =============================================================================
# Process the input CSV file and write the output to another CSV file.
# The input CSV is assumed to have a header with the column "البيت" (the verse).
# For each row, we process the verse, then output the original verse along with
# the identified Tashbeeh words (joined as a string).
# =============================================================================
def process_csv(input_file, output_file):
    output_rows = []
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            # Use the "البيت" column from your CSV
            line_text = row.get("النص", "")
            if not line_text.strip():
                continue  # skip empty lines

            # Split the verse into words (you may refine tokenization if needed)
            words = line_text.split()
            word_objects = [WordInPoem(index=i, word=w) for i, w in enumerate(words)]
            mid = len(word_objects) // 2
            first_part = word_objects[:mid]
            second_part = word_objects[mid:]
            tashbeeh_words = identification_tashbeeh_by_line(first_part, second_part)

            # Prepare the output row.
            output_row = {
                "النص": line_text,
                "TashbeehWords": " ".join([w.word for w in tashbeeh_words])
            }
            output_rows.append(output_row)

    # Write the output rows to the CSV file.
    with open(output_file, "w", newline='', encoding='utf-8') as out_csv:
        fieldnames = ["النص", "TashbeehWords"]
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"Output saved to {output_file}")


# =============================================================================
# Main program: process the input CSV and save the output to a new CSV file.
# =============================================================================
if __name__ == "__main__":
    input_csv_file = "Andalus2.csv"
    output_csv_file = "output.csv"
    process_csv(input_csv_file, output_csv_file)
