"""Build the 3 few-shot example sets (A/B/C) for the مجاز/استعارة فعل
example-sensitivity pilot (E1).

Reproduces docs/phase4/COST_PLAN.md §2.1 exactly from source data (not
transcribed by hand): for each of the 3 fixed Abu Nuwas source poems, list
the distinct verse numbers carrying an استعارة فعل annotation (exact subtype
match), then draw 2 with random.sample under one random.seed(42) applied
once, sets drawn in order A -> B -> C.

Does not touch experiments/pilot_3models/prompts.py's logic — this module
only appends a new few-shot block on top of its existing build_system_message()
output, following the same bare-numbered-verse format used in
data/elements/*.txt (see prompts.py SYSTEM_HEADER / ELEMENT_1 template),
extended with the span + Dr. Hussein's own analysis note for each example
(COST_PLAN's instruction: "verse text and annotation").
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_config import EXAMPLE_POEM_IDS, EXAMPLE_SEED, SET_NAMES, SUBTYPE_FOCUS, PILOT_DIR  # noqa: E402
from ali_poems_io import load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from prompts import build_system_message as pilot_build_system_message  # noqa: E402


def _verses_with_subtype(poem_json: dict, subtype: str) -> list:
    vs = set()
    for a in poem_json["annotations"]:
        if a.get("subtype") == subtype:
            vs.add(int(str(a["verse_index"]).split(",")[0]))
    return sorted(vs)


def _spans_for_verse(poem_json: dict, verse_no: int, subtype: str) -> list:
    out = []
    for a in poem_json["annotations"]:
        if a.get("subtype") != subtype:
            continue
        if int(str(a["verse_index"]).split(",")[0]) != verse_no:
            continue
        out.append({"span": (a.get("span_text") or "").strip(), "analysis": (a.get("analysis") or "").strip()})
    return out


def build_example_sets() -> dict:
    """Returns {set_name: {"source_poem_id", "source_poem_name", "candidate_verses",
    "chosen_verses": [verse_no, ...], "examples": [{"verse_no", "text", "annotations": [...]}]}}."""
    random.seed(EXAMPLE_SEED)
    sets = {}
    for set_name, poem_id in zip(SET_NAMES, EXAMPLE_POEM_IDS):
        pj = load_poem_json(poem_id)
        candidates = _verses_with_subtype(pj, SUBTYPE_FOCUS)
        chosen = sorted(random.sample(candidates, 2))
        verses_by_no = {v["verse_index"]: v for v in pj["verses"]}
        examples = [
            {
                "verse_no": vn,
                "text": verses_by_no[vn]["text"],
                "annotations": _spans_for_verse(pj, vn, SUBTYPE_FOCUS),
            }
            for vn in chosen
        ]
        sets[set_name] = {
            "source_poem_id": poem_id,
            "source_poem_name": pj["poem_name"],
            "candidate_verses": candidates,
            "chosen_verses": chosen,
            "examples": examples,
        }
    return sets


FEWSHOT_HEADER = """--------------------------------
FEW-SHOT EXAMPLES (مجاز / استعارة فعل)
--------------------------------
Additional worked examples of ONLY the استعارة فعل (verbal metaphor) subtype
of مجاز (Trope), beyond the element definitions above. Each example gives the
full verse and the annotated span(s) within it.
"""


def build_fewshot_block(example_set: dict) -> str:
    lines = [FEWSHOT_HEADER]
    for i, ex in enumerate(example_set["examples"], start=1):
        lines.append(f"{i}) {ex['text']}")
        for a in ex["annotations"]:
            note = f" ({a['analysis']})" if a["analysis"] else ""
            lines.append(f"   span: {a['span']}{note}")
    return "\n".join(lines) + "\n"


def build_system_message_e1(example_set: dict) -> str:
    """pilot_3models's existing (frozen) system message, unmodified, plus this
    set's few-shot block appended at the end."""
    base = pilot_build_system_message()
    return base.rstrip() + "\n\n" + build_fewshot_block(example_set)


if __name__ == "__main__":
    sets = build_example_sets()
    for name in SET_NAMES:
        s = sets[name]
        print(f"=== Set {name} (poem {s['source_poem_id']} {s['source_poem_name']}) ===")
        print(f"candidates with {SUBTYPE_FOCUS}: {s['candidate_verses']} -> chosen {s['chosen_verses']}")
        for ex in s["examples"]:
            print(f"  v{ex['verse_no']}: {ex['text']}")
            for a in ex["annotations"]:
                print(f"    span={a['span']!r} analysis={a['analysis']!r}")
        print()
