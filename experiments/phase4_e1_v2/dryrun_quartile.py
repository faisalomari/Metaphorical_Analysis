"""Step 1 (NO API calls): cost estimate for the two quartile sets (Q1/Q2),
each 2 examples, on eval_pool_25.json (the SAME 327-verse-unit, 25-poem
pool every other E1 v2 set already ran on). Same method as
dryrun_eras.py/dryrun_multipoet.py (reused, not reimplemented differently):
REAL tiktoken cl100k_base input-token counts for the actual built prompts
x the pool's real verses, combined with REAL average output-tokens/call
per provider computed directly from the completed run_manifest.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR  # noqa: E402
from eras_quartile_config import QUARTILE_SET_NAMES  # noqa: E402
from eras_quartile_examples import build_quartile_sets  # noqa: E402
from multipoet_prompt_builder import build_system_message_n, build_user_message  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from config import MODELS  # noqa: E402

from dryrun_eras import build_cell_input_tokens, price_block  # noqa: E402  (reused unchanged)
from dryrun_multipoet import real_avg_output_tokens_per_call  # noqa: E402


def main():
    sets, groups, slot_detail, targets, filter_counts, eligible_poets = build_quartile_sets()
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    n_verses = sum(p["verse_count"] for p in pool)

    print("=" * 78)
    print("Real average output tokens/call per provider (from completed run_manifest.json, "
          "pooled across every existing set -- confirms output length ~input-independent)")
    print("=" * 78)
    out_stats = real_avg_output_tokens_per_call()
    for p, s in out_stats.items():
        print(f"  {p:28s}: n={s['n']:5d}  mean={s['mean']:6.1f}  min={s['min']:4d}  max={s['max']:4d}  "
              f"stdev={s['stdev']:5.2f}")

    print(f"\neval_pool_25.json: {len(pool)} poems, {n_verses} verse-units (same pool as every "
          f"existing set)")

    grand_total_worst = 0.0
    grand_total_cfg = 0.0
    for set_name in QUARTILE_SET_NAMES:
        extra_examples = sets[set_name]
        system_message = build_system_message_n(extra_examples)
        total_input_tokens = build_cell_input_tokens(pool, system_message)
        result = price_block(
            f"SET {set_name} (2 examples, poets {[e['poet_name'] for e in extra_examples]}) "
            f"x {n_verses} verse-units x 3 models x 1 run",
            total_input_tokens, n_verses, out_stats,
        )
        grand_total_worst += result["total_worst"]
        grand_total_cfg += result["total_cfg"]

    print(f"\n{'=' * 78}\nGRAND TOTAL: {' + '.join(QUARTILE_SET_NAMES)} "
          f"(2 sets x {n_verses} verse-units x 3 models)\n{'=' * 78}")
    print(f"  Worst-case Gemini pricing:   ${grand_total_worst:,.4f}")
    print(f"  config.py Gemini pricing:    ${grand_total_cfg:,.4f}")

    print(f"\n{'=' * 78}\nSTOP -- no API call has been made. Awaiting explicit \"go\" + a hard cap "
          f"(--max-additional-usd on run_quartile.py) before running --confirm.\n{'=' * 78}")


if __name__ == "__main__":
    main()
