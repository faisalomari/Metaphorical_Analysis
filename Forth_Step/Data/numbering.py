# File: number_poetry_lines.py
# Adds 1) 2) 3) ... to the beginning of each non-empty line in a TXT file.

from pathlib import Path

INPUT_FILE = "Jareer/poetry.txt"
OUTPUT_FILE = INPUT_FILE

def main():
    in_path = Path(INPUT_FILE)
    out_path = Path(OUTPUT_FILE)

    lines = in_path.read_text(encoding="utf-8").splitlines()

    numbered = []
    n = 1
    for line in lines:
        raw = line.rstrip("\n")
        if raw.strip() == "":
            numbered.append("")  # keep blank lines as-is
            continue

        # If the line is already numbered like "12) ..." skip renumbering
        # Comment this block out if you ALWAYS want to renumber everything.
        if raw.lstrip().split(maxsplit=1)[0].endswith(")") and raw.lstrip().split(maxsplit=1)[0][:-1].isdigit():
            numbered.append(raw)
            continue

        numbered.append(f'{n}) "{raw.strip()}"')
        n += 1

    out_path.write_text("\n".join(numbered) + "\n", encoding="utf-8")
    print(f"Wrote: {out_path.resolve()}")

if __name__ == "__main__":
    main()
