"""Step 2 (NO API calls): cost estimate for F5/F10 (+F5b, +Z add-on) on the
new 50-poem multipoet pool.

Unlike dryrun_D.py (which used a flat real avg-$/call anchor from the
Z/A/B/C manifest -- valid there because D/D2's prompts are the same LENGTH
class as A/B/C, only the 2 example verses differ), F5/F10's system prompts
are MUCH longer (6 / 11 worked examples vs A/B/C's 3) so a flat per-call
dollar average would understate their real input-token cost. This script
instead reuses dryrun_v2.py's own method: REAL tiktoken `cl100k_base` input
token counts for the actual F5/F10 prompts x the new pool's real verses,
combined with REAL average output-tokens/call per provider computed
directly from the completed run_manifest.json (schema-driven output length
is ~constant regardless of input length -- confirmed by this script's own
printed min/max/std, not just assumed).

Gemini is still priced under all 3 scenarios from dryrun_v2.py
(gemini-3.5-flash config.py rate / gemini-3.6-flash ESTIMATE_LOW / ESTIMATE_HIGH)
since the served-vs-requested model-id ambiguity documented there is
unchanged.
"""
import json
import statistics
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import E1V1_DIR, EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from multipoet_config import EVAL_POOL_50_MULTIPOET_PATH  # noqa: E402
from multipoet_examples import build_multipoet_sets  # noqa: E402
from multipoet_prompt_builder import build_system_message_n, build_user_message  # noqa: E402
from prompt_builder import build_system_message as build_system_message_z  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from config import MODELS  # noqa: E402

ENCODING_NAME = "cl100k_base"
_enc = tiktoken.get_encoding(ENCODING_NAME)

GEMINI_PRICE_SCENARIOS = {
    "config.py (gemini-3.5-flash, legacy)": (1.50, 9.00),
    "gemini-3.6-flash ESTIMATE_LOW": (0.75, 3.75),
    "gemini-3.6-flash ESTIMATE_HIGH": (1.50, 7.50),
}

PROVIDER_DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
                    "google": "Gemini (served: gemini-3.6-flash)"}


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def real_avg_output_tokens_per_call() -> dict:
    """Per provider: mean/min/max/stdev of usage.output_tokens across every
    error-free cell in the completed E1 v2 manifest (all sets Z/A/B/C/D/D2
    pooled -- output length is schema-driven, not input-length-driven)."""
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    by_provider = {"anthropic": [], "openai": [], "google": []}
    for r in manifest:
        if r.get("error") is None and r["provider"] in by_provider:
            out_tok = (r.get("usage") or {}).get("output_tokens")
            if out_tok:
                by_provider[r["provider"]].append(out_tok)
    stats = {}
    for p, vals in by_provider.items():
        stats[p] = {
            "n": len(vals), "mean": statistics.mean(vals), "min": min(vals), "max": max(vals),
            "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        }
    return stats


def build_cell_input_tokens(pool: list, system_message: str) -> int:
    """Total input tokens (system+user) over every verse-unit in pool, for
    ONE fixed system message (one set)."""
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
    total_best_cfg = costs["openai"] + costs["anthropic"] + costs["google"]["config.py (gemini-3.5-flash, legacy)"]
    print(f"  TOTAL (3 models, worst-case Gemini): ${total_worst:,.4f}")
    print(f"  TOTAL (3 models, config.py Gemini rate): ${total_best_cfg:,.4f}")
    return {"costs": costs, "total_worst": total_worst, "total_cfg": total_best_cfg}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-f5b", action="store_true")
    parser.add_argument("--include-z-addon", action="store_true", default=True)
    args = parser.parse_args()

    sets, _ = build_multipoet_sets(include_f5b=args.include_f5b)
    pool = json.loads(EVAL_POOL_50_MULTIPOET_PATH.read_text(encoding="utf-8"))["poems"]
    n_verses = sum(p["verse_count"] for p in pool)

    print("=" * 78)
    print(f"Real average output tokens/call per provider (from completed run_manifest.json, "
          f"pooled across sets Z/A/B/C/D/D2 -- confirms output length is ~input-independent)")
    print("=" * 78)
    out_stats = real_avg_output_tokens_per_call()
    for p, s in out_stats.items():
        print(f"  {PROVIDER_DISPLAY[p]:28s}: n={s['n']:5d}  mean={s['mean']:6.1f}  "
              f"min={s['min']:4d}  max={s['max']:4d}  stdev={s['stdev']:5.2f}")

    print(f"\nNew 50-poem multipoet pool: {len(pool)} poems, {n_verses} verse-units")

    grand_total_worst = 0.0
    grand_total_cfg = 0.0
    for set_name, extra_examples in sets.items():
        system_message = build_system_message_n(extra_examples)
        total_input_tokens = build_cell_input_tokens(pool, system_message)
        result = price_block(
            f"SET {set_name} ({len(extra_examples)} examples, "
            f"{len(set(e['poet_name'] for e in extra_examples))} poets) x {n_verses} verse-units x 3 models x 1 run",
            total_input_tokens, n_verses, out_stats,
        )
        grand_total_worst += result["total_worst"]
        grand_total_cfg += result["total_cfg"]

    z_addon_result = None
    if args.include_z_addon:
        pool_25 = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
        pool_25_ids = {p["poem_id"] for p in pool_25}
        new_for_z = [p for p in pool if p["poem_id"] not in pool_25_ids]
        n_verses_new_z = sum(p["verse_count"] for p in new_for_z)
        z_system = build_system_message_z("Z")
        z_input_tokens = build_cell_input_tokens(new_for_z, z_system)
        print(f"\n{'=' * 78}\nOPTIONAL ADD-ON: Set Z on the {len(new_for_z)} new-pool poems NOT already "
              f"covered by the existing Z run on eval_pool_25.json\n{'=' * 78}")
        print(f"(of the pool's 50 poems, {len(pool) - len(new_for_z)} already have Z data from the "
              f"25-poem run; {len(new_for_z)} do not)")
        z_addon_result = price_block(
            f"Z add-on ({len(new_for_z)} poems, {n_verses_new_z} verse-units) x 3 models x 1 run",
            z_input_tokens, n_verses_new_z, out_stats,
        )

    print(f"\n{'=' * 78}\nGRAND TOTAL: {'+'.join(sets.keys())}{' + Z add-on' if z_addon_result else ''}\n{'=' * 78}")
    print(f"  Worst-case Gemini pricing:   ${grand_total_worst + (z_addon_result['total_worst'] if z_addon_result else 0):,.4f}")
    print(f"  config.py Gemini pricing:    ${grand_total_cfg + (z_addon_result['total_cfg'] if z_addon_result else 0):,.4f}")
    print(f"  (Z add-on alone: worst=${z_addon_result['total_worst']:,.4f}  cfg=${z_addon_result['total_cfg']:,.4f})"
          if z_addon_result else "")

    print(f"\n{'=' * 78}\nSTOP -- no API call has been made. Awaiting explicit \"go\" + a hard cap "
          f"(--max-additional-usd on runner.py) before running --confirm.\n{'=' * 78}")


if __name__ == "__main__":
    main()
