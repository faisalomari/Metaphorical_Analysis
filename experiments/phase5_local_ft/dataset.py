"""Builds verse-level (poem_id, verse_no, text, label) example lists for one
target, from a saved split file (experiments/phase5_local_ft/splits/*.json)."""
import json

from data_io import ALI_POEMS_DIR, load_poem, label_for_target, verse_texts


def _poem_path(poem_id: str):
    matches = list(ALI_POEMS_DIR.glob(f"{poem_id}_*.json"))
    if not matches:
        raise FileNotFoundError(f"no poem json for poem_id={poem_id}")
    return matches[0]


def load_split(split_path) -> dict:
    with open(split_path, encoding="utf-8") as f:
        return json.load(f)


def build_examples(poem_ids: list, target_value: str) -> list:
    """Returns [{"poem_id","verse_no","text","label"}, ...] over every verse
    of every given poem (not just positives) -- the verse-level binary
    classification framing from the task instructions."""
    examples = []
    for pid in poem_ids:
        poem = load_poem(_poem_path(pid))
        texts = verse_texts(poem)
        labels = label_for_target(poem, {"kind": "subtype", "value": target_value})
        for verse_no, text in texts.items():
            examples.append({"poem_id": pid, "verse_no": verse_no, "text": text, "label": labels[verse_no]})
    return examples
