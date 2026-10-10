"""Build the 50-poem eval pool for E1 (docs/phase4/COST_PLAN.md §2.2).

Candidate pool = all 167 manifest poems minus: the no-text poem (28601), the
5 frozen Phase 1 poems (already_used_in_project), and the 3 Abu Nuwas
example-source poems (fewshot_examples.py). Each poem is tagged "abu_nuwas"
or "other". A 50-poem subsample is drawn with random.seed(43) (a different
seed from the example draw, per the design, so the two randomizations don't
interact).

Writes experiments/phase4_e1/config/eval_pool.json and
experiments/phase4_e1/config/example_sets.json. No API calls.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_config import (  # noqa: E402
    ALREADY_USED_POEM_IDS, CONFIG_DIR, EVAL_POOL_PATH, EVAL_POOL_SIZE,
    EXAMPLE_POEM_IDS, EXAMPLE_SETS_PATH, NO_TEXT_POEM_ID, POET_NAME, POOL_SEED,
)
from ali_poems_io import load_manifest  # noqa: E402
from fewshot_examples import build_example_sets  # noqa: E402


def build_candidate_pool() -> list:
    rows = load_manifest()
    excluded = {NO_TEXT_POEM_ID} | ALREADY_USED_POEM_IDS | set(EXAMPLE_POEM_IDS)
    pool = []
    for r in rows:
        if r["poem_id"] in excluded:
            continue
        pool.append({
            "poem_id": r["poem_id"],
            "poet_name": r["poet_name"],
            "title": r["title"],
            "verse_count": int(r["verse_count"]),
            "tag": "abu_nuwas" if r["poet_name"] == POET_NAME else "other",
        })
    return pool


def build_eval_subsample(candidate_pool: list, size: int, seed: int) -> list:
    random.seed(seed)
    return sorted(random.sample(candidate_pool, size), key=lambda p: int(p["poem_id"]))


def main():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    candidate_pool = build_candidate_pool()
    eval_pool_full = candidate_pool  # the full cross-poet pool (158 poems)
    eval_pool_50 = build_eval_subsample(candidate_pool, EVAL_POOL_SIZE, POOL_SEED)

    n_abu_nuwas_full = sum(1 for p in eval_pool_full if p["tag"] == "abu_nuwas")
    n_abu_nuwas_50 = sum(1 for p in eval_pool_50 if p["tag"] == "abu_nuwas")

    pool_doc = {
        "candidate_pool_size": len(candidate_pool),
        "candidate_pool_verses": sum(p["verse_count"] for p in candidate_pool),
        "candidate_pool_abu_nuwas": n_abu_nuwas_full,
        "pool_seed": POOL_SEED,
        "eval_pool_size": len(eval_pool_50),
        "eval_pool_verses": sum(p["verse_count"] for p in eval_pool_50),
        "eval_pool_abu_nuwas": n_abu_nuwas_50,
        "eval_pool_other": len(eval_pool_50) - n_abu_nuwas_50,
        "poems": eval_pool_50,
    }
    EVAL_POOL_PATH.write_text(json.dumps(pool_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    example_sets = build_example_sets()
    EXAMPLE_SETS_PATH.write_text(json.dumps(example_sets, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Candidate pool: {len(candidate_pool)} poems, {pool_doc['candidate_pool_verses']} verses "
          f"({n_abu_nuwas_full} Abu Nuwas, {len(candidate_pool) - n_abu_nuwas_full} other)")
    print(f"Eval pool (seed={POOL_SEED}): {len(eval_pool_50)} poems, {pool_doc['eval_pool_verses']} verses "
          f"({n_abu_nuwas_50} abu_nuwas tag, {pool_doc['eval_pool_other']} other tag)")
    print(f"Wrote {EVAL_POOL_PATH}")
    print(f"Wrote {EXAMPLE_SETS_PATH}")


if __name__ == "__main__":
    main()
