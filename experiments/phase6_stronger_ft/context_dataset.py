"""L1 (context) lever: builds verse-level examples whose TEXT includes the
previous and next verse, marked with separators, instead of Phase 5's
verse-alone text. Labels are unchanged (still the target verse's own label --
only the model's input context changes, not what it is being asked to
classify). Reuses Phase 5's data_io.py (poem loading, label_for_target)
unmodified; only the text-building step is new."""
import json
from pathlib import Path

import phase6_config as config
from data_io import ALI_POEMS_DIR, load_poem, label_for_target, verse_texts
from dataset import load_split  # noqa: F401  (Phase 5's split loader, reused unchanged)

PREV_TAG = "[PREV]"
TARGET_TAG = "[VERSE]"
NEXT_TAG = "[NEXT]"


def _poem_path(poem_id: str) -> Path:
    matches = list(ALI_POEMS_DIR.glob(f"{poem_id}_*.json"))
    if not matches:
        raise FileNotFoundError(f"no poem json for poem_id={poem_id}")
    return matches[0]


def _windowed_text(texts: dict, verse_no: int, n_verses: int) -> str:
    prev_text = texts.get(verse_no - 1, "") if verse_no - 1 >= 1 else ""
    next_text = texts.get(verse_no + 1, "") if verse_no + 1 <= n_verses else ""
    parts = []
    if prev_text:
        parts.append(f"{PREV_TAG} {prev_text}")
    parts.append(f"{TARGET_TAG} {texts[verse_no]}")
    if next_text:
        parts.append(f"{NEXT_TAG} {next_text}")
    return " ".join(parts)


def build_examples(poem_ids: list, target_value: str, use_context: bool) -> list:
    """Same return shape as Phase 5's dataset.build_examples; `use_context=True`
    replaces each verse's bare text with prev+target+next (verse's own label
    unchanged). `use_context=False` reproduces Phase 5's verse-alone text
    exactly (kept here, not re-imported, so this module is a single source of
    truth for what Phase 6's ablation actually varies)."""
    examples = []
    for pid in poem_ids:
        poem = load_poem(_poem_path(pid))
        texts = verse_texts(poem)
        n_verses = poem["verse_count"]
        labels = label_for_target(poem, {"kind": "subtype", "value": target_value})
        for verse_no, text in texts.items():
            final_text = _windowed_text(texts, verse_no, n_verses) if use_context else text
            examples.append({"poem_id": pid, "verse_no": verse_no, "text": final_text,
                              "label": labels[verse_no]})
    return examples


if __name__ == "__main__":
    # Quick token-length p99 report for the context-window variant (Step 1 "L1"
    # instruction: "Report token length p99 and cost"). Uses the 3 Phase 5
    # tokenizers (same ones whose p99 set Phase 5's MAX_LEN=32 for verse-alone).
    from transformers import AutoTokenizer
    from data_io import list_poem_files

    all_poem_ids = sorted({f.name.split("_", 1)[0] for f in list_poem_files()})
    lengths_by_tok = {}
    for key, model_name in config.ENCODER_MODELS.items():
        tok = AutoTokenizer.from_pretrained(model_name)
        lens = []
        for pid in all_poem_ids:
            poem = load_poem(_poem_path(pid))
            texts = verse_texts(poem)
            n_verses = poem["verse_count"]
            for verse_no in texts:
                t = _windowed_text(texts, verse_no, n_verses)
                lens.append(len(tok(t)["input_ids"]))
        lens.sort()
        p99 = lens[int(0.99 * (len(lens) - 1))]
        p95 = lens[int(0.95 * (len(lens) - 1))]
        lengths_by_tok[key] = {"p50": lens[len(lens) // 2], "p95": p95, "p99": p99, "max": lens[-1], "n": len(lens)}
        print(f"{key} ({model_name}): n={len(lens)} p50={lens[len(lens)//2]} p95={p95} p99={p99} max={lens[-1]}")

    out_path = config.RESULTS_DIR / "l1_context_token_lengths.json"
    out_path.write_text(json.dumps(lengths_by_tok, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
