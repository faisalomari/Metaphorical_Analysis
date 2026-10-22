"""Step 1 (NO API calls): find eligible poets/poems/verses and build the
F5 / F10 / (optional) F5b multi-poet few-shot example sets.

Eligibility rule (declared in multipoet_config.py's docstring, applied here):
  a poem is a candidate example SOURCE for poet P's draw iff it is not
  NO_TEXT_POEM_ID / ALREADY_USED_POEM_IDS (Phase 1 frozen poems) / the 3 old
  Abu-Nuwas-only EXAMPLE_POEM_IDS (v1's own A/B/C sources) -- and, ONLY when
  P == "أبو نواس", also not one of the original eval_pool.json's 10
  abu_nuwas poems (OLD_EVAL_POOL_ABU_NUWAS_IDS).
  A VERSE is eligible iff it carries >=1 annotation with
  subtype == "استعارة فعل" (exact match) AND a non-empty "analysis" field.
  A poet is eligible iff >=1 of their candidate poems has >=1 eligible verse.

Poet-selection order: deterministic period-diversity round robin (poets
within a period ordered by poet_id, periods visited in PERIOD_ORDER below,
cycling until enough poets are collected) -- NOT randomized. F5 = first 5 of
this order, F10 = first 10 (so F5 is a strict prefix of F10), F5b (optional)
= next 5. The PER-POET VERSE draw is the only randomized step: one
random.seed(42) call, then one random.sample(eligible_verses_for_poet, 1)
per poet IN SELECTION ORDER -- so F5's 5 draws are byte-identical whether or
not F10/F5b are ever built (sequential RNG consumption, never reseeded
mid-draw).
"""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, E1V1_DIR, EXAMPLE_POEM_IDS, NO_TEXT_POEM_ID, SUBTYPE_FOCUS,
)
from multipoet_config import (  # noqa: E402
    CONFIG_DIR, F10_N, F5B_N, F5_N, MULTIPOET_EXAMPLE_SEED, MULTIPOET_EXAMPLE_SETS_PATH,
    MULTIPOET_SET_NAMES, OLD_EVAL_POOL_ABU_NUWAS_IDS,
)

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_manifest, load_poem_json  # noqa: E402

ABU_NUWAS_NAME = "أبو نواس"

# Chronological-ish priority order for round-robin diversity; any period seen
# in the data but not listed here falls after these, alphabetically, then ""
# (unknown/blank) last of all.
PERIOD_ORDER = [
    "العصر الجاهلي", "مخضرم", "مخضرم الدولتين", "العصر الأموي", "العصر العباسي",
]

EXCLUDED_ALWAYS = {NO_TEXT_POEM_ID} | set(ALREADY_USED_POEM_IDS) | set(EXAMPLE_POEM_IDS)


def _verse_no(verse_index_field) -> int:
    return int(str(verse_index_field).split(",")[0])


def find_eligible_verses_for_poem(poem_json: dict) -> dict:
    """{verse_no: [{"span": str, "analysis": str}, ...]} for every verse with
    >=1 SUBTYPE_FOCUS annotation carrying a non-empty analysis note."""
    n_verses = poem_json["verse_count"]
    out = defaultdict(list)
    for a in poem_json["annotations"]:
        if a.get("subtype") != SUBTYPE_FOCUS:
            continue
        note = (a.get("analysis") or "").strip()
        if not note:
            continue
        vn = _verse_no(a["verse_index"])
        if not (1 <= vn <= n_verses):
            continue
        out[vn].append({"span": (a.get("span_text") or "").strip(), "analysis": note})
    return dict(out)


def build_eligible_poets() -> dict:
    """Returns {poet_name: {"period": str, "verses": [(poem_id, poem_name, verse_no,
    verse_text, annotations), ...]}} -- eligible verses pooled across ALL of that
    poet's candidate poems (per-poet exclusion rule applied per poet identity)."""
    rows = load_manifest()
    by_poet_period = Counter()
    poets = defaultdict(lambda: {"period": None, "poet_id": None, "verses": []})

    for r in rows:
        poem_id = r["poem_id"]
        poet_name = r["poet_name"]
        if poem_id in EXCLUDED_ALWAYS:
            continue
        if poet_name == ABU_NUWAS_NAME and poem_id in OLD_EVAL_POOL_ABU_NUWAS_IDS:
            continue
        try:
            pj = load_poem_json(poem_id)
        except FileNotFoundError:
            continue
        elig = find_eligible_verses_for_poem(pj)
        if not elig:
            continue
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for vn, annots in elig.items():
            poets[poet_name]["verses"].append((poem_id, pj["poem_name"], vn, verses_by_no[vn], annots))
        poets[poet_name]["period"] = r["period"] or ""
        poets[poet_name]["poet_id"] = r["poet_id"]
        by_poet_period[poet_name] += 1

    return dict(poets)


def _period_sort_key(period: str) -> tuple:
    if period in PERIOD_ORDER:
        return (0, PERIOD_ORDER.index(period))
    if period:
        return (1, period)
    return (2, "")


def select_poet_order(eligible_poets: dict, n_needed: int) -> list:
    """Deterministic period-diversity round robin. Returns an ordered list of
    poet_name, length min(n_needed, len(eligible_poets))."""
    by_period = defaultdict(list)
    for name, info in eligible_poets.items():
        by_period[info["period"]].append((int(info["poet_id"]) if info["poet_id"] else 0, name))
    for period in by_period:
        by_period[period].sort()
    periods_order = sorted(by_period.keys(), key=_period_sort_key)
    queues = {p: [name for _, name in by_period[p]] for p in periods_order}

    order = []
    while len(order) < n_needed and any(queues.values()):
        for p in periods_order:
            if queues[p]:
                order.append(queues[p].pop(0))
                if len(order) == n_needed:
                    break
    return order


def draw_examples(eligible_poets: dict, poet_order: list) -> list:
    """One random.seed(42) call, then one draw per poet IN poet_order --
    sequential RNG consumption, so a prefix of poet_order always gets the
    same draws regardless of how many poets are drawn after it."""
    random.seed(MULTIPOET_EXAMPLE_SEED)
    drawn = []
    for name in poet_order:
        candidates = eligible_poets[name]["verses"]
        poem_id, poem_name, verse_no, verse_text, annots = random.sample(candidates, 1)[0]
        drawn.append({
            "poet_name": name,
            "period": eligible_poets[name]["period"],
            "poet_id": eligible_poets[name]["poet_id"],
            "poem_id": poem_id,
            "poem_name": poem_name,
            "verse_no": verse_no,
            "text": verse_text,
            "n_candidate_verses_for_poet": len(candidates),
            "annotations": [{"span": a["span"], "analysis": a["analysis"]} for a in annots],
        })
    return drawn


def build_multipoet_sets(include_f5b: bool = False) -> dict:
    eligible_poets = build_eligible_poets()
    n_needed = (F10_N + F5B_N) if include_f5b else F10_N
    poet_order = select_poet_order(eligible_poets, n_needed)
    drawn = draw_examples(eligible_poets, poet_order)

    sets = {
        "F5": drawn[:F5_N],
        "F10": drawn[:F10_N],
    }
    if include_f5b:
        sets["F5b"] = drawn[F10_N:F10_N + F5B_N]
    return sets, eligible_poets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-f5b", action="store_true")
    args = parser.parse_args()

    eligible_poets = build_eligible_poets()
    periods = Counter(info["period"] for info in eligible_poets.values())
    print(f"Eligible poets (>=1 poem with an {SUBTYPE_FOCUS} verse carrying a non-empty "
          f"analysis note, respecting exclusions): {len(eligible_poets)}")
    print(f"Periods represented: {dict(periods)}")
    for name, info in sorted(eligible_poets.items(), key=lambda kv: (_period_sort_key(kv[1]["period"]), kv[0])):
        print(f"  {name:30s} period={info['period']:20s} eligible_verses={len(info['verses'])}")

    sets, _ = build_multipoet_sets(include_f5b=args.include_f5b)

    for set_name, examples in sets.items():
        print(f"\n{'=' * 78}\nSET {set_name} ({len(examples)} examples, {len(set(e['poet_name'] for e in examples))} distinct poets)\n{'=' * 78}")
        for e in examples:
            print(f"  poet={e['poet_name']!r} period={e['period']!r} poem_id={e['poem_id']} "
                  f"({e['poem_name']!r}) verse_no={e['verse_no']} "
                  f"n_candidates_for_poet={e['n_candidate_verses_for_poet']}")
            print(f"    text: {e['text']}")
            for a in e["annotations"]:
                print(f"    span={a['span']!r} analysis={a['analysis']!r}")

    assert set(e["poet_name"] for e in sets["F5"]) <= set(e["poet_name"] for e in sets["F10"]), \
        "F5's poets must be a subset of F10's poets"
    assert len(set(e["poet_name"] for e in sets["F10"])) == len(sets["F10"]), "F10 must have distinct poets"
    if "F5b" in sets:
        assert not (set(e["poet_name"] for e in sets["F5b"]) & set(e["poet_name"] for e in sets["F10"])), \
            "F5b's poets must be disjoint from F10's poets"
    print(f"\nOK: F5 poets subset of F10 poets; F10 poets all distinct"
          + ("; F5b poets disjoint from F10" if "F5b" in sets else "") + ".")

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MULTIPOET_EXAMPLE_SETS_PATH.write_text(
        json.dumps({"seed": MULTIPOET_EXAMPLE_SEED, "sets": sets}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {MULTIPOET_EXAMPLE_SETS_PATH}")


if __name__ == "__main__":
    main()
