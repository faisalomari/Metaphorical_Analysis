"""DRY RUN cost estimate for E1 v2 — NO API calls.

Real input-token count (tiktoken `cl100k_base`, an approximation — no local
tokenizer exists for gpt-5.4-mini/gemini-3.5-flash(3.6-flash) in this
environment, same caveat phase4_e1/dryrun.py already flagged) for every
distinct (set, poem, verse) prompt. Output tokens estimated from Phase 3's
real logged average, 106.2 tokens/decision (FULL_COST_MODEL.md §2:
results/phase3_crossmodel/summary_openai.json, 121,119 output tokens /
1,140 calls — includes the mandatory 1-3-sentence Arabic reasoning field),
applied uniformly (not scaled by input size, since Phase 3's own real data
shows output length here is governed by the fixed decision+reasoning shape,
not by input length).

Also answers the Gemini model-id question: config.py / providers.py /
providers_fixed.py all request model_id="gemini-3.5-flash" (pilot_3models.
config.MODELS), but the real E1 v1 run's 429 quota error body (E1_RESULTS.md,
SESSION_LOG.md 2026-10-10 Step 2) reported the quota wall under
'generativelanguage.googleapis.com/generate_content_free_tier_requests ...
for model gemini-3.6-flash' — i.e. Google's backend served the request under
gemini-3.6-flash's identity, not 3.5-flash's. FULL_COST_MODEL.md §0.1
independently confirmed gemini-3.5-flash is absent from Google's current
official pricing/models pages. Conclusion: 'gemini-3.5-flash' is the string
this project's code sends, but 'gemini-3.6-flash' is the model actually
served/billed — gemini-3.6-flash's pricing applies, not legacy 3.5-flash's.
A web search this session (ai.google.dev cached copies disagree) found two
conflicting current rates for gemini-3.6-flash: $0.75/$3.75 per MTok (intro
pricing through 2026-12-31, several sources) vs $1.50/$7.50 (one cached copy
+ one aggregator). Both are reported below as ESTIMATE_LOW / ESTIMATE_HIGH;
this project's own config.py $1.50/$9.00 figure is shown too for continuity
with every prior Phase 4 cost doc, but is the LEAST likely of the three to
be the real current rate for the model actually being billed.
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import (  # noqa: E402
    ALL_MODELS, CHEAP_VARIANT_ABU_NUWAS_N, CHEAP_VARIANT_OTHER_N, E1V1_DIR,
    E1V1_EVAL_POOL_PATH, PILOT_DIR, RUN_MODELS, SET_NAMES,
    build_cheap_variant_pool,
)
from prompt_builder import build_messages  # noqa: E402

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402
from build_pool import build_candidate_pool  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from config import MODELS  # noqa: E402

ENCODING_NAME = "cl100k_base"
_enc = tiktoken.get_encoding(ENCODING_NAME)

PHASE3_AVG_OUTPUT_TOKENS_PER_DECISION = 106.2  # real logged GPT-5.4-mini avg, FULL_COST_MODEL.md §2

# Gemini pricing scenarios, per MTok (in, out) — see module docstring.
GEMINI_PRICE_SCENARIOS = {
    "project config.py (gemini-3.5-flash, legacy/estimate)": (1.50, 9.00),
    "gemini-3.6-flash ESTIMATE_LOW (intro pricing thru 2026-12-31)": (0.75, 3.75),
    "gemini-3.6-flash ESTIMATE_HIGH (one cached page / one aggregator)": (1.50, 7.50),
}


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def build_cell_input_tokens(pool: list) -> dict:
    """Returns {(set_name, poem_id, verse_no): input_tokens} for every real
    verse-unit prompt this design would send."""
    system_tokens = {s: count_tokens(build_messages(s, "placeholder")[0]) for s in SET_NAMES}
    out = {}
    for poem in pool:
        pj = load_poem_json(poem["poem_id"])
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for verse_no, verse_text in verses_by_no.items():
            user_tokens = count_tokens(build_messages("Z", verse_text)[1])  # user template identical across sets
            for set_name in SET_NAMES:
                out[(set_name, poem["poem_id"], verse_no)] = system_tokens[set_name] + user_tokens
    return out


def cost_table(label: str, pool: list, cell_tokens: dict):
    n_poems = len(pool)
    n_verses = sum(p["verse_count"] for p in pool)
    n_cells_per_set = len(cell_tokens) // len(SET_NAMES)
    total_calls_per_model = len(cell_tokens)  # n_verses * len(SET_NAMES)

    print(f"\n{'=' * 78}\n{label}\n{'=' * 78}")
    print(f"Poems: {n_poems}  Verses (verse-units): {n_verses}  Sets: {SET_NAMES}")
    print(f"Calls per model = verse-units x sets = {n_verses} x {len(SET_NAMES)} = {total_calls_per_model}")
    print(f"Calls, confirmed pair ({' + '.join(RUN_MODELS)}) = {total_calls_per_model} x 2 = "
          f"{total_calls_per_model * 2}")

    total_input_tokens = sum(cell_tokens.values())
    total_output_tokens_est = total_calls_per_model * PHASE3_AVG_OUTPUT_TOKENS_PER_DECISION
    print(f"Total input tokens (1 model, all sets x all verse-units): {total_input_tokens:,.0f}")
    print(f"Total output tokens, estimated @ {PHASE3_AVG_OUTPUT_TOKENS_PER_DECISION}/decision "
          f"(1 model): {total_output_tokens_est:,.0f}")

    def cost_for_openai():
        spec = MODELS["openai"]
        return (total_input_tokens / 1e6) * spec["price_in"] + (total_output_tokens_est / 1e6) * spec["price_out"]

    def cost_for_google(price_in, price_out):
        return (total_input_tokens / 1e6) * price_in + (total_output_tokens_est / 1e6) * price_out

    def cost_for_anthropic():
        spec = MODELS["anthropic"]
        return (total_input_tokens / 1e6) * spec["price_in"] + (total_output_tokens_est / 1e6) * spec["price_out"]

    print(f"\n  GPT-5.4-mini               calls={total_calls_per_model:>6}  cost=${cost_for_openai():,.2f}")
    for scenario_name, (pin, pout) in GEMINI_PRICE_SCENARIOS.items():
        c = cost_for_google(pin, pout)
        print(f"  Gemini [{scenario_name}]\n"
              f"      ${pin}/${pout} per MTok   calls={total_calls_per_model:>6}  cost=${c:,.2f}")
    print(f"  Claude Sonnet 4.6 (costed, not run)  calls={total_calls_per_model:>6}  "
          f"cost=${cost_for_anthropic():,.2f}")

    gemini_mid = cost_for_google(*GEMINI_PRICE_SCENARIOS["gemini-3.6-flash ESTIMATE_LOW (intro pricing thru 2026-12-31)"])
    print(f"\n  CONFIRMED PAIR TOTAL (GPT-5.4-mini + Gemini @ 3.6-flash ESTIMATE_LOW): "
          f"${cost_for_openai() + gemini_mid:,.2f}")
    gemini_cfg = cost_for_google(*GEMINI_PRICE_SCENARIOS["project config.py (gemini-3.5-flash, legacy/estimate)"])
    print(f"  CONFIRMED PAIR TOTAL (GPT-5.4-mini + Gemini @ project config.py rate): "
          f"${cost_for_openai() + gemini_cfg:,.2f}")

    return {
        "n_poems": n_poems, "n_verses": n_verses, "calls_per_model": total_calls_per_model,
        "total_input_tokens": total_input_tokens, "total_output_tokens_est": total_output_tokens_est,
        "cost_openai": cost_for_openai(),
        "cost_google_cfg": gemini_cfg, "cost_google_est_low": gemini_mid,
    }


def main():
    full_pool = json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    print("Tokenizer: tiktoken `cl100k_base` (approximation — no offline tokenizer exists for "
          "gpt-5.4-mini or gemini-3.5-flash/3.6-flash in this environment).")

    full_tokens = build_cell_input_tokens(full_pool)
    full_result = cost_table("50-POEM EVAL POOL (unchanged from phase4_e1 v1, seed=43)", full_pool, full_tokens)

    candidate_pool = build_candidate_pool()
    cheap_pool = build_cheap_variant_pool(candidate_pool)
    cheap_tokens = build_cell_input_tokens(cheap_pool)
    cheap_result = cost_table(
        f"CHEAPER VARIANT: {CHEAP_VARIANT_ABU_NUWAS_N} abu_nuwas + {CHEAP_VARIANT_OTHER_N} other "
        f"= 25 poems (seed=43, drawn fresh from the same 158-poem candidate pool)",
        cheap_pool, cheap_tokens,
    )

    print(f"\n{'=' * 78}\nCOMPARISON WITH docs/phase4/FULL_COST_MODEL.md\n{'=' * 78}")
    print("FULL_COST_MODEL.md's D4a (23 subtypes, 1 call/poem, no reasoning) priced the FULL")
    print("23-subtype taxonomy at full-poem granularity: GPT-5.4-mini $36.38 (161 poems), Gemini")
    print("(config.py rate) $72.73 (161 poems) — i.e. ALL subtypes, not just one.")
    print("This design (E1 v2) prices only ONE subtype (استعارة فعل), 4 example-sets, at")
    print("per-VERSE granularity, over the SAME 50-poem pool D1/D2 would use (158/50-poem split):")
    print(f"  GPT-5.4-mini, 50-poem pool, 4 sets, 1 subtype: ${full_result['cost_openai']:,.2f} "
          f"(vs. D4a's $36.38 for 161 poems x 23 subtypes x all-verse-taxonomy calls — not directly")
    print("  comparable since D4a's output volume is ~23x larger per poem; this design's per-call")
    print("  output is Phase 3's single-decision 106.2 tokens, not D4a's ~49,000 tokens/poem.)")
    print(f"  Gemini (config.py legacy rate): ${full_result['cost_google_cfg']:,.2f}  |  "
          f"(3.6-flash ESTIMATE_LOW): ${full_result['cost_google_est_low']:,.2f}")

    print(f"\n{'=' * 78}\nSTOP\n{'=' * 78}")
    print("No API call has been made anywhere in this task. Awaiting explicit go-ahead before")
    print("running runner.py --confirm.")


if __name__ == "__main__":
    main()
