"""Step 2 (NO API calls): cost dry-run for the 2 approved subtypes
(استعارة قديمة, كناية عن صفة) x {zero-shot, few-shot} x 3 models, on the
unchanged 25-poem/327-verse eval_pool_25.json (user chose Option (a):
keep the pool as-is, استعارة قديمة indicative-only -- see
docs/phase4/SESSION_LOG.md 2026-10-29). Also checks API-key presence
(readiness) WITHOUT calling any provider.

Input tokens are REAL, measured directly from the actual rendered system
+ user messages this run would send (tiktoken cl100k_base) -- not a
guess. Output tokens use the project's own calibrated figure for this
EXACT JSON schema (exists/appearance/reasoning): 120 tokens/call, the
real average measured from Phase 3 cross-model's own logged responses
(results/phase3_crossmodel/cost_estimate.md), reused here rather than
re-measured (same schema, same instructions, unchanged).
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census import load_poem_json, verse_no_of  # noqa: E402
from phase7_config import CONFIG_DIR, EVAL_POOL_25_PATH, RESULTS_DIR  # noqa: E402
from subtype_prompts import ANALYSIS_INSTRUCTIONS  # noqa: E402

ENC = tiktoken.get_encoding("cl100k_base")
OUTPUT_TOKENS_PER_CALL = 120  # Phase 3 cross-model's own measured average for this schema

MODEL_PRICING = {
    "anthropic": {"model_id": "claude-sonnet-4-6", "display": "Claude Sonnet 4.6", "price_in": 3.00, "price_out": 15.00},
    "openai": {"model_id": "gpt-5.4-mini", "display": "GPT-5.4 mini", "price_in": 0.75, "price_out": 4.50},
    "google": {"model_id": "gemini-3.5-flash", "display": "Gemini 3.5 Flash", "price_in": 1.50, "price_out": 9.00},
}

# FULL_COST_MODEL_V2.md Sec 2 per-call means (real spend, E1v2's استعارة فعل
# prompt family -- cross-check only, NOT the primary estimate for Phase 7's
# own, shorter, different-subtype prompts).
CROSSCHECK_PER_CALL = {
    "zero": {"anthropic": 0.004957, "openai": 0.000846, "google": 0.001603},
    "few": {"anthropic": 0.005904, "openai": 0.001015, "google": 0.001889},
}


def n_tok(text: str) -> int:
    return len(ENC.encode(text))


def check_api_keys() -> dict:
    from dotenv import load_dotenv
    import os
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    out = {}
    for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]:
        v = os.environ.get(k)
        out[k] = {"present": bool(v), "length": len(v) if v else 0}
    return out


def main():
    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    pool_poem_ids = pool_doc["poem_ids"]
    sets_doc = json.loads((CONFIG_DIR / "phase7_example_sets.json").read_text(encoding="utf-8"))

    # real per-verse user-message token counts over the unchanged 25-poem pool
    user_tokens = []
    for pid in pool_poem_ids:
        pj = load_poem_json(pid)
        for v in pj["verses"]:
            msg = ANALYSIS_INSTRUCTIONS.format(verse=v["text"])
            user_tokens.append(n_tok(msg))
    n_verses = len(user_tokens)
    total_user_tokens = sum(user_tokens)
    avg_user_tokens = total_user_tokens / n_verses
    print(f"Pool: {len(pool_poem_ids)} poems, {n_verses} verse-units (unchanged, Option (a))")
    print(f"Real user-message tokens: avg={avg_user_tokens:.1f}, min={min(user_tokens)}, max={max(user_tokens)}, total={total_user_tokens}")

    subtypes = list(sets_doc["sets"].keys())
    n_models = len(MODEL_PRICING)
    n_conditions = 2
    total_calls = n_verses * n_conditions * n_models * len(subtypes)
    print(f"\nCalls = verse_units({n_verses}) x conditions(2) x models(3) x subtypes({len(subtypes)}) = {total_calls}")

    print("\nServed model IDs this run will request (pilot_3models/config.py MODELS, unchanged):")
    for key, m in MODEL_PRICING.items():
        print(f"  {key}: {m['model_id']} ({m['display']}) -- price_in=${m['price_in']}/MTok, price_out=${m['price_out']}/MTok")
    print("  Gemini price/identity uncertainty (flagged, not resolved -- same caveat as "
          "docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md Sec 3.3): every prior E1v2 manifest record "
          "logs model_id='gemini-3.5-flash' as REQUESTED and consistently SERVED; a separate "
          "pre-run verification call once suggested 'gemini-3.6-flash' was actually served but "
          "that claim was never corroborated by any persisted manifest record and was walked "
          "back. Billing in this run will also include Gemini's hidden thinking tokens "
          "(providers_fixed.call_google_fixed, thinking_level='minimal') -- NOT separately "
          "estimated below since no real Phase-7 output exists yet to measure them from; this "
          "is a known one-sided underestimate risk for Gemini's column only, bounded by the "
          "cross-check row below.")

    grand_total = 0.0
    grand_total_crosscheck = 0.0
    print(f"\n{'subtype':<16}{'cond':<6}{'model':<10}{'in_tok/call':>12}{'out_tok/call':>13}{'cost':>12}{'crosscheck':>12}")
    per_model_total = {k: 0.0 for k in MODEL_PRICING}
    per_subtype_total = {s: 0.0 for s in subtypes}
    for subtype in subtypes:
        for cond, cond_key in [("zero", "zero_shot_system_tokens"), ("few", "few_shot_system_tokens")]:
            sys_tok = sets_doc["sets"][subtype][cond_key]
            total_in_tokens = n_verses * sys_tok + total_user_tokens
            avg_in_per_call = total_in_tokens / n_verses
            total_out_tokens = n_verses * OUTPUT_TOKENS_PER_CALL
            for model_key, m in MODEL_PRICING.items():
                cost = (total_in_tokens * m["price_in"] + total_out_tokens * m["price_out"]) / 1e6
                crosscheck = n_verses * CROSSCHECK_PER_CALL[cond][model_key]
                grand_total += cost
                grand_total_crosscheck += crosscheck
                per_model_total[model_key] += cost
                per_subtype_total[subtype] += cost
                print(f"{subtype:<16}{cond:<6}{model_key:<10}{avg_in_per_call:>12.1f}{OUTPUT_TOKENS_PER_CALL:>13}"
                      f"${cost:>10.4f}  ${crosscheck:>9.4f}")

    print(f"\nPer-model total (primary, token-based estimate):")
    for k, v in per_model_total.items():
        print(f"  {MODEL_PRICING[k]['display']}: ${v:.4f}")
    print(f"\nPer-subtype total (primary):")
    for s, v in per_subtype_total.items():
        print(f"  {s}: ${v:.4f}")
    print(f"\nGRAND TOTAL (primary, token-based, real measured input + Phase-3-calibrated output): ${grand_total:.2f}")
    print(f"GRAND TOTAL (cross-check, FULL_COST_MODEL_V2 per-call means -- different, longer "
          f"استعارة فعل prompts, directional only): ${grand_total_crosscheck:.2f}")

    keys = check_api_keys()
    print("\nAPI key readiness check (presence only, NO API call made):")
    for k, v in keys.items():
        print(f"  {k}: {'present' if v['present'] else 'MISSING'} (len={v['length']})")
    all_present = all(v["present"] for v in keys.values())
    print(f"  All 3 keys present: {all_present}")

    out = {
        "n_verses": n_verses, "n_subtypes": len(subtypes), "subtypes": subtypes,
        "total_calls": total_calls,
        "avg_user_tokens": avg_user_tokens, "total_user_tokens": total_user_tokens,
        "output_tokens_per_call": OUTPUT_TOKENS_PER_CALL,
        "model_pricing": MODEL_PRICING,
        "grand_total_primary_usd": round(grand_total, 4),
        "grand_total_crosscheck_usd": round(grand_total_crosscheck, 4),
        "per_model_total_usd": {k: round(v, 4) for k, v in per_model_total.items()},
        "per_subtype_total_usd": {k: round(v, 4) for k, v in per_subtype_total.items()},
        "api_keys_present": {k: v["present"] for k, v in keys.items()},
    }
    out_path = RESULTS_DIR / "dryrun_cost.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
