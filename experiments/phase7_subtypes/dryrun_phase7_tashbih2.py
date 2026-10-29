"""Step 2 addendum (NO API calls): cost dry-run for the 2 new تشبيه subtypes
(تشبيه قصير, تشبيه مطول) x {zero-shot, few-shot} x 3 models, each over its
own unchanged 25-poem/327-verse pool (see phase7_example_sets_tashbih2.json
-- 0 poems removed for either subtype). Same method as dryrun_phase7.py
(real tiktoken input tokens, Phase-3-calibrated 120 output tokens/call) --
reused unchanged, not reinvented.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_poem_json  # noqa: E402
from phase7_config import CONFIG_DIR, EVAL_POOL_25_PATH, RESULTS_DIR  # noqa: E402
from subtype_prompts import ANALYSIS_INSTRUCTIONS  # noqa: E402

ENC = tiktoken.get_encoding("cl100k_base")
OUTPUT_TOKENS_PER_CALL = 120

MODEL_PRICING = {
    "anthropic": {"model_id": "claude-sonnet-4-6", "display": "Claude Sonnet 4.6", "price_in": 3.00, "price_out": 15.00},
    "openai": {"model_id": "gpt-5.4-mini", "display": "GPT-5.4 mini", "price_in": 0.75, "price_out": 4.50},
    "google": {"model_id": "gemini-3.5-flash", "display": "Gemini 3.5 Flash", "price_in": 1.50, "price_out": 9.00},
}


def n_tok(text: str) -> int:
    return len(ENC.encode(text))


def main():
    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    sets_doc = json.loads((CONFIG_DIR / "phase7_example_sets_tashbih2.json").read_text(encoding="utf-8"))
    subtypes = sets_doc["target_subtypes"]

    per_subtype_results = {}
    grand_total = 0.0
    per_model_total = {k: 0.0 for k in MODEL_PRICING}
    per_subtype_total = {s: 0.0 for s in subtypes}

    for subtype in subtypes:
        final_pool = sets_doc["per_subtype_final_pool"][subtype]
        pool_poem_ids = final_pool["final_eval_pool_poem_ids"]

        user_tokens = []
        for pid in pool_poem_ids:
            pj = load_poem_json(pid)
            for v in pj["verses"]:
                msg = ANALYSIS_INSTRUCTIONS.format(verse=v["text"])
                user_tokens.append(n_tok(msg))
        n_verses = len(user_tokens)
        total_user_tokens = sum(user_tokens)
        print(f"\n{subtype}: pool {len(pool_poem_ids)} poems, {n_verses} verse-units, "
              f"avg user tokens={total_user_tokens/n_verses:.1f}")

        subtype_calls = n_verses * 2 * len(MODEL_PRICING)
        subtype_cost = 0.0
        for cond, cond_key in [("zero", "zero_shot_system_tokens"), ("few", "few_shot_system_tokens")]:
            sys_tok = sets_doc["sets"][subtype][cond_key]
            total_in_tokens = n_verses * sys_tok + total_user_tokens
            total_out_tokens = n_verses * OUTPUT_TOKENS_PER_CALL
            for model_key, m in MODEL_PRICING.items():
                cost = (total_in_tokens * m["price_in"] + total_out_tokens * m["price_out"]) / 1e6
                grand_total += cost
                subtype_cost += cost
                per_model_total[model_key] += cost
                print(f"  {cond:5s} {model_key:10s}: in={total_in_tokens/n_verses:.1f} tok/call, "
                      f"out={OUTPUT_TOKENS_PER_CALL} tok/call, cost=${cost:.4f}")
        per_subtype_total[subtype] = subtype_cost
        per_subtype_results[subtype] = {"n_verses": n_verses, "calls": subtype_calls, "cost_usd": round(subtype_cost, 4)}

    total_calls = sum(v["calls"] for v in per_subtype_results.values())
    print(f"\nTotal calls (2 new subtypes): {total_calls}")
    print("Per-model total:")
    for k, v in per_model_total.items():
        print(f"  {MODEL_PRICING[k]['display']}: ${v:.4f}")
    print(f"\nGRAND TOTAL (2 new تشبيه subtypes, primary token-based estimate): ${grand_total:.2f}")

    # combined with the already-estimated first-2-subtypes cost (dryrun_cost.json, $9.70) for a
    # full 4-subtype picture
    orig = json.loads((RESULTS_DIR / "dryrun_cost.json").read_text(encoding="utf-8"))
    combined_total = grand_total + orig["grand_total_primary_usd"]
    print(f"\nCombined 4-subtype total (original $‌{orig['grand_total_primary_usd']:.2f} + "
          f"new ${grand_total:.2f}): ${combined_total:.2f}")

    out = {
        "subtypes": subtypes,
        "total_calls": total_calls,
        "per_subtype": per_subtype_results,
        "per_model_total_usd": {k: round(v, 4) for k, v in per_model_total.items()},
        "grand_total_primary_usd": round(grand_total, 4),
        "combined_4subtype_total_usd": round(combined_total, 4),
        "model_pricing": MODEL_PRICING,
    }
    out_path = RESULTS_DIR / "dryrun_cost_tashbih2.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
