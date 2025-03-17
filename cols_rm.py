#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

def remove_columns_from_csv(input_csv, output_csv, columns_to_remove):
    """
    Reads the input CSV file, removes the columns specified in columns_to_remove,
    and writes the filtered data to output_csv.
    """
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        # Determine the columns that will remain in the new CSV file.
        new_fieldnames = [col for col in reader.fieldnames if col not in columns_to_remove]

        with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()  # Write header to the output CSV.
            for row in reader:
                # Create a new row dictionary that only contains the desired columns.
                filtered_row = {col: row[col] for col in new_fieldnames}
                writer.writerow(filtered_row)
    print(f"Filtered CSV saved as '{output_csv}'.")


if __name__ == "__main__":
    # Set the input and output CSV file names.
    input_csv_file = "Andalus.csv"       # Replace with your input CSV filename.
    output_csv_file = "Andalus2.csv"  # The new CSV file with removed columns.

    # Specify which columns to remove.
    # For example, based on your sample CSV header:
    # "#,البيت,الشاعر,القصيدة,التعبير البلاغي,العنصر البلاغي المستعمل,العنصر البلاغي الثانوي"
    columns_to_remove = [
        "الشاعر",
        "القصيدة",
        "العنصر البلاغي المستعمل",
        "العنصر البلاغي الثانوي"
    ]

    remove_columns_from_csv(input_csv_file, output_csv_file, columns_to_remove)
