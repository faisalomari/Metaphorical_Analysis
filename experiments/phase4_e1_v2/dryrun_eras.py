"""Step 3 (NO API calls): cost estimate for the six poet-era sets
(M1/M2/E1/E2/H1/H2), each 2 examples, on eval_pool_25.json (the SAME
327-verse-unit, 25-poem pool Z/A/B/C/D/D2 already ran on -- unlike F5/F10,
these sets need no separate pool, so their results will be directly
comparable to Z/A/B/D2 without any thin-overlap correction).

Same method as dryrun_multipoet.py (reused, not reimplemented differently):
REAL tiktoken cl100k_base input-token counts for the actual built prompts x
the pool's real verses, combined with REAL average output-tokens/call per
provider computed directly from the completed run_manifest.json.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR  # noqa: E402
from eras_config import ERAS_SET_NAMES  # noqa: E402
from eras_examples import build_eras_sets  # noqa: E402
from multipoet_prompt_builder import build_system_message_n, build_user_message  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from config import MODELS  # noqa: E402

from dryrun_multipoet import GEMINI_PRICE_SCENARIOS, PROVIDER_DISPLAY, real_avg_output_tokens_per_call  # noqa: E402

ENCODING_NAME = "cl100k_base"
_enc = tiktoken.get_encoding(ENCODING_NAME)


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def build_cell_input_tokens(pool: list, system_message: str) -> int:
    from ali_poems_io import load_poem_json  # noqa
    system_tokens = count_tokens(system_message)
    total = 0
    for poem in pool:
        pj = load_poem_json(poem["poem_id"])
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for verse_text in verses_by_no.values():
            total += system_tokens + count_tokens(build_user_message(verse_text))
    return total


def cost_for_tokens(total_input_tokens: int, n_calls: int, out_mean: float, price_in: float, price_out: float) -> float:
    return (total_input_tokens / 1e6) * price_in + (n_calls * out_mean / 1e6) * price_out


def price_block(label: str, total_input_tokens: int, n_calls: int, out_stats: dict) -> dict:
    print(f"\n{label}: {n_calls} calls, {total_input_tokens:,} input tokens total")
    costs = {}
    for provider in ("openai", "anthropic"):
        spec = MODELS[provider]
        c = cost_for_tokens(total_input_tokens, n_calls, out_stats[provider]["mean"], spec["price_in"], spec["price_out"])
        costs[provider] = c
        print(f"  {PROVIDER_DISPLAY[provider]:28s} (avg_out={out_stats[provider]['mean']:.1f} tok/call): ${c:,.4f}")
    costs["google"] = {}
    for scenario, (pin, pout) in GEMINI_PRICE_SCENARIOS.items():
        c = cost_for_tokens(total_input_tokens, n_calls, out_stats["google"]["mean"], pin, pout)
        costs["google"][scenario] = c
        print(f"  Gemini [{scenario}] (avg_out={out_stats['google']['mean']:.1f} tok/call): ${c:,.4f}")
    worst_google = max(costs["google"].values())
    total_worst = costs["openai"] + costs["anthropic"] + worst_google
    total_cfg = costs["openai"] + costs["anthropic"] + costs["google"]["config.py (gemini-3.5-flash, legacy)"]
    print(f"  TOTAL (3 models, worst-case Gemini): ${total_worst:,.4f}")
    print(f"  TOTAL (3 models, config.py Gemini rate): ${total_cfg:,.4f}")
    return {"costs": costs, "total_worst": total_worst, "total_cfg": total_cfg}


def main():
    sets, pools, groups, filter_counts, eligible_poets = build_eras_sets()
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    n_verses = sum(p["verse_count"] for p in pool)

    print("=" * 78)
    print("Real average output tokens/call per provider (from completed run_manifest.json, "
          "pooled across Z/A/B/C/D/D2 -- confirms output length ~input-independent)")
    print("=" * 78)
    out_stats = real_avg_output_tokens_per_call()
    for p, s in out_stats.items():
        print(f"  {PROVIDER_DISPLAY[p]:28s}: n={s['n']:5d}  mean={s['mean']:6.1f}  "
              f"min={s['min']:4d}  max={s['max']:4d}  stdev={s['stdev']:5.2f}")

    print(f"\neval_pool_25.json: {len(pool)} poems, {n_verses} verse-units (same pool as Z/A/B/C/D/D2)")

    grand_total_worst = 0.0
    grand_total_cfg = 0.0
    for set_name in ERAS_SET_NAMES:
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

    print(f"\n{'=' * 78}\nGRAND TOTAL: {' + '.join(ERAS_SET_NAMES)} (6 sets x {n_verses} verse-units x 3 models)\n{'=' * 78}")
    print(f"  Worst-case Gemini pricing:   ${grand_total_worst:,.4f}")
    print(f"  config.py Gemini pricing:    ${grand_total_cfg:,.4f}")

    print(f"\n{'=' * 78}\nSTOP -- no API call has been made. Awaiting explicit \"go\" + a hard cap "
          f"(--max-additional-usd on run_eras.py) before running --confirm.\n{'=' * 78}")


if __name__ == "__main__":
    main()
