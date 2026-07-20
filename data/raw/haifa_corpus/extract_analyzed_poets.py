import json

def get_poets_with_analyzed_poems(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("The source JSON file was not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding the JSON file.")
        return []

    analyzed_poets = []
    for entry in data:
        poet_name = entry.get("poet")
        poems = entry.get("poems", [])
        
        # Check if any poem is analyzed ("نعم")
        if any(poem.get("analyzed") == "نعم" for poem in poems):
            analyzed_poets.append(poet_name)

    return analyzed_poets

def save_to_txt(poet_list, output_file):
    if not poet_list:
        print("No poets found to save.")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        for poet in poet_list:
            f.write(f"{poet}\n")
    print(f"Successfully saved {len(poet_list)} poets to {output_file}")

# --- Execution ---
input_json = 'all_poets.json'      # Your input file
output_txt = 'analyzed_poets.txt'  # The file to be created

poets = get_poets_with_analyzed_poems(input_json)
save_to_txt(poets, output_txt)