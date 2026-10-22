"""Step 1 (NO API calls), continued: build the 50-poem eval pool for the
multi-poet experiment = phase4_e1 (v1)'s existing eval_pool.json's 50 poems
MINUS any poem used as an F5/F10/(F5b) example source, replaced by "the next
poems from the same seed-43 stratified draw" (10 abu_nuwas + 40 other, kept
if at all possible).

Continuation method (verified empirically before writing this, see
SESSION_LOG.md): CPython's random.sample(population, k) under a fixed seed
has the property that sample(pop, k)[:j] == sample(pop, j) for the SAME seed
state and the SAME population list/order, for any j <= k -- i.e. asking for
MORE items from the same seeded draw reproduces the original prefix exactly
and gives a well-defined, deterministic "next" continuation. v1's
build_eval_subsample does:
    random.seed(43)
    picked = random.sample(abu_nuwas_candidates, 10) + random.sample(other_candidates, 40)
(ONE seed() call, two sequential sample() calls on the SAME RNG stream) --
reproduced exactly here as two independent reseeded draws so each stratum
can be extended on its own without disturbing the other:
  - abu_nuwas: random.seed(43); sample(abu_nuwas_candidates, len(abu_nuwas_candidates))
    (a fresh seed call -- matches v1's FIRST sample call exactly for its
    first 10 items).
  - other: random.seed(43); sample(abu_nuwas_candidates, 10) [replays v1's
    exact first call to reach the identical RNG state] ; THEN
    sample(other_candidates, len(other_candidates)) (matches v1's SECOND
    call exactly for its first 40 items).
Both extended lists are verified against the committed eval_pool.json below
before being used for any replacement.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_DIR, E1V1_EVAL_POOL_PATH  # noqa: E402
from multipoet_config import (  # noqa: E402
    EVAL_POOL_50_MULTIPOET_PATH, MULTIPOET_POOL_CONTINUATION_SEED,
)

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from build_pool import build_candidate_pool  # noqa: E402

SEED = MULTIPOET_POOL_CONTINUATION_SEED  # 43, must equal e1_config.POOL_SEED


def build_extended_strata():
    candidate_pool = build_candidate_pool()
    abu_nuwas_candidates = [p for p in candidate_pool if p["tag"] == "abu_nuwas"]
    other_candidates = [p for p in candidate_pool if p["tag"] == "other"]

    random.seed(SEED)
    abu_ext = random.sample(abu_nuwas_candidates, len(abu_nuwas_candidates))

    random.seed(SEED)
    random.sample(abu_nuwas_candidates, 10)  # replay v1's first call to reach its exact post-call state
    other_ext = random.sample(other_candidates, len(other_candidates))

    return candidate_pool, abu_ext, other_ext


def verify_reproduces_original(abu_ext, other_ext):
    original = json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    original_ids = {p["poem_id"] for p in original}
    reproduced_ids = {p["poem_id"] for p in (abu_ext[:10] + other_ext[:40])}
    assert reproduced_ids == original_ids, (
        f"continuation does not reproduce eval_pool.json's original 50: "
        f"missing={original_ids - reproduced_ids} extra={reproduced_ids - original_ids}"
    )
    print(f"OK: seed-43 continuation reproduces the exact original 50-poem eval_pool.json "
          f"(10 abu_nuwas + 40 other) as its prefix.")


def build_eval_pool_50_multipoet(example_poem_ids: set) -> dict:
    candidate_pool, abu_ext, other_ext = build_extended_strata()
    verify_reproduces_original(abu_ext, other_ext)

    original_abu = abu_ext[:10]
    original_other = other_ext[:40]

    kept_abu = [p for p in original_abu if p["poem_id"] not in example_poem_ids]
    kept_other = [p for p in original_other if p["poem_id"] not in example_poem_ids]
    n_removed_abu = len(original_abu) - len(kept_abu)
    n_removed_other = len(original_other) - len(kept_other)

    removed_ids = {p["poem_id"] for p in original_abu + original_other if p["poem_id"] in example_poem_ids}

    pool_ids_so_far = {p["poem_id"] for p in kept_abu + kept_other}

    def take_replacements(extended_list, start, n_needed):
        reps = []
        i = start
        while len(reps) < n_needed and i < len(extended_list):
            cand = extended_list[i]
            if (cand["poem_id"] not in pool_ids_so_far
                    and cand["poem_id"] not in example_poem_ids):
                reps.append(cand)
                pool_ids_so_far.add(cand["poem_id"])
            i += 1
        return reps, i

    abu_replacements, _ = take_replacements(abu_ext, 10, n_removed_abu)
    other_replacements, _ = take_replacements(other_ext, 40, n_removed_other)

    final_abu = kept_abu + abu_replacements
    final_other = kept_other + other_replacements
    final_pool = sorted(final_abu + final_other, key=lambda p: int(p["poem_id"]))

    composition_note = (
        f"{len(final_abu)} abu_nuwas + {len(final_other)} other "
        f"({'matches 10+40 target' if len(final_abu) == 10 and len(final_other) == 40 else 'DEVIATES from 10+40 target'})"
    )

    doc = {
        "base_pool": "experiments/phase4_e1/config/eval_pool.json (v1's 50-poem pool, seed=43)",
        "continuation_seed": SEED,
        "example_poem_ids_removed": sorted(removed_ids, key=int),
        "n_removed_abu_nuwas": n_removed_abu,
        "n_removed_other": n_removed_other,
        "n_replacement_abu_nuwas": len(abu_replacements),
        "n_replacement_other": len(other_replacements),
        "replacement_poem_ids_abu_nuwas": [p["poem_id"] for p in abu_replacements],
        "replacement_poem_ids_other": [p["poem_id"] for p in other_replacements],
        "composition_note": composition_note,
        "pool_size": len(final_pool),
        "pool_verses": sum(p["verse_count"] for p in final_pool),
        "pool_abu_nuwas": len(final_abu),
        "pool_other": len(final_other),
        "poems": final_pool,
    }
    return doc


def main():
    import argparse
    from multipoet_examples import build_multipoet_sets

    parser = argparse.ArgumentParser()
    parser.add_argument("--include-f5b", action="store_true")
    args = parser.parse_args()

    sets, _ = build_multipoet_sets(include_f5b=args.include_f5b)
    example_poem_ids = {e["poem_id"] for examples in sets.values() for e in examples}
    print(f"Example-source poem ids across {list(sets.keys())}: {sorted(example_poem_ids, key=int)}")

    doc = build_eval_pool_50_multipoet(example_poem_ids)

    original = json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    original_ids = {p["poem_id"] for p in original}
    new_ids = {p["poem_id"] for p in doc["poems"]}
    overlap_25 = None
    try:
        pool_25 = json.loads((Path(__file__).resolve().parent / "config" / "eval_pool_25.json")
                              .read_text(encoding="utf-8"))["poems"]
        pool_25_ids = {p["poem_id"] for p in pool_25}
        overlap_25 = len(pool_25_ids & new_ids)
    except FileNotFoundError:
        pass

    print(f"\nRemoved {len(doc['example_poem_ids_removed'])} poems used as example sources: "
          f"{doc['example_poem_ids_removed']}")
    print(f"Replacements: abu_nuwas={doc['replacement_poem_ids_abu_nuwas']} "
          f"other={doc['replacement_poem_ids_other']}")
    print(f"Final composition: {doc['composition_note']}")
    print(f"Final pool: {doc['pool_size']} poems, {doc['pool_verses']} verse-units")
    print(f"Overlap with old 50-poem pool (eval_pool.json): {len(original_ids & new_ids)}/{len(new_ids)}")
    if overlap_25 is not None:
        print(f"Overlap with the 25-poem pool (eval_pool_25.json), for comparison with Z/A/B/C/D: "
              f"{overlap_25}/{len(pool_25_ids)}")

    EVAL_POOL_50_MULTIPOET_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_POOL_50_MULTIPOET_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {EVAL_POOL_50_MULTIPOET_PATH}")


if __name__ == "__main__":
    main()
