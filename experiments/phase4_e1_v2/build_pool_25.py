"""Persists the 25-poem cheaper-variant pool (5 abu_nuwas + 20 other, seed=43)
to experiments/phase4_e1_v2/config/eval_pool_25.json, with poem ids logged.

Previously this pool only existed transiently (built on the fly inside
dryrun_v2.py / runner.py --pool cheap via e1v2_config.build_cheap_variant_pool).
This script writes it to disk once so the exact pool used by a real run is
fixed and auditable, matching how v1's eval_pool.json already works for the
50-poem pool. Reuses build_candidate_pool() (experiments/phase4_e1/build_pool.py,
unchanged) and build_cheap_variant_pool() (e1v2_config.py, unchanged) -- no
new sampling logic. No API calls.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import (  # noqa: E402
    CHEAP_VARIANT_ABU_NUWAS_N, CHEAP_VARIANT_OTHER_N, CHEAP_VARIANT_SEED,
    CONFIG_DIR, E1V1_DIR, build_cheap_variant_pool,
)

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from build_pool import build_candidate_pool  # noqa: E402

EVAL_POOL_25_PATH = CONFIG_DIR / "eval_pool_25.json"


def main():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    candidate_pool = build_candidate_pool()
    pool_25 = build_cheap_variant_pool(candidate_pool)

    n_abu_nuwas = sum(1 for p in pool_25 if p["tag"] == "abu_nuwas")
    n_other = len(pool_25) - n_abu_nuwas
    poem_ids = [p["poem_id"] for p in pool_25]

    doc = {
        "candidate_pool_size": len(candidate_pool),
        "seed": CHEAP_VARIANT_SEED,
        "pool_size": len(pool_25),
        "pool_verses": sum(p["verse_count"] for p in pool_25),
        "abu_nuwas_n": n_abu_nuwas,
        "other_n": n_other,
        "abu_nuwas_n_requested": CHEAP_VARIANT_ABU_NUWAS_N,
        "other_n_requested": CHEAP_VARIANT_OTHER_N,
        "poem_ids": poem_ids,
        "poems": pool_25,
    }
    EVAL_POOL_25_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Candidate pool: {len(candidate_pool)} poems")
    print(f"25-poem pool (seed={CHEAP_VARIANT_SEED}): {len(pool_25)} poems, {doc['pool_verses']} verses "
          f"({n_abu_nuwas} abu_nuwas, {n_other} other)")
    print(f"Poem ids: {poem_ids}")
    print(f"Wrote {EVAL_POOL_25_PATH}")


if __name__ == "__main__":
    main()
