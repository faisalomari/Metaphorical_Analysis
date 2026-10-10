"""DRY RUN cost estimate for E1 — NO API calls.

Computes exact input-token counts for every (set, poem) prompt this pilot
would actually send (not an average/extrapolation), using tiktoken's
`cl100k_base` encoding as the closest available LOCAL estimate for all three
providers (none of OpenAI/Anthropic/Google ship an offline tokenizer for
gpt-5.4-mini / claude-sonnet-4-6 / gemini-3.5-flash in this environment;
counting via Anthropic's or Google's real tokenizer would itself require a
network call to their API, which this dry run must not make). Real token
counts WILL differ slightly per-provider at run time and must be
re-confirmed against actual `usage` fields in the first real response per
CLAUDE.md rule 5 — this estimate is for the go/no-go decision only.

Output tokens are not directly computable offline (depend on the model's
actual response length) — estimated via each provider's own historical
output/input ratio from Phase 1's pooled run_manifest.json data
(docs/phase4/INFO_REPORT.md §4), applied to this call's real input-token
count.

Reports cost for ALL 3 models (anthropic/openai/google), even though the
confirmed E1 run only uses google+openai, since the user asked to see all 3
costed. Compares the headline cell to COST_PLAN.md's prior $7.36 estimate
(50 poems, 3 sets, GPT+Gemini, 2 runs).
"""
import json
import sys
from pathlib import Path

import tiktoken

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_config import (  # noqa: E402
    ALL_MODELS, EVAL_POOL_PATH, EXAMPLE_SETS_PATH, N_RUNS, PILOT_DIR,
    REPEAT_SET_A, RUN_MODELS, SET_NAMES,
)
from ali_poems_io import build_poem_text, load_poem_json  # noqa: E402
from fewshot_examples import build_system_message_e1  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from prompts import ANALYSIS_INSTRUCTIONS  # noqa: E402
from config import MODELS  # noqa: E402

ENCODING_NAME = "cl100k_base"
_enc = tiktoken.get_encoding(ENCODING_NAME)

# Phase 1 pooled historical output/input token ratio per provider
# (INFO_REPORT.md §4: "Across all 5 poems (pooled): anthropic avg ~6,227 in /
# 4,518 out; openai avg ~4,290 in / 2,854 out; google avg ~4,185 in / 3,771
# out"). Used only to estimate this call's output tokens from its real input
# token count (output length isn't computable offline).
HISTORICAL_OUT_IN_RATIO = {
    "anthropic": 4518 / 6227,
    "openai": 2854 / 4290,
    "google": 3771 / 4185,
}

COST_PLAN_PRIOR_ESTIMATE_USD = 7.36  # 50 poems, 3 sets, GPT+Gemini, 2 runs


def count_tokens(text: str) -> int:
    return len(_enc.encode(text))


def build_prompts():
    """Returns {(set_name, poem_id): (system_message, user_message)}."""
    example_sets = json.loads(EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))
    pool = json.loads(EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    system_messages = {s: build_system_message_e1(example_sets[s]) for s in SET_NAMES}
    prompts = {}
    for poem in pool:
        pj = load_poem_json(poem["poem_id"])
        user_message = ANALYSIS_INSTRUCTIONS + "\n" + build_poem_text(pj) + "\n"
        for set_name in SET_NAMES:
            prompts[(set_name, poem["poem_id"])] = (system_messages[set_name], user_message)
    return prompts


def main():
    prompts = build_prompts()
    n_poems = len({pid for (_, pid) in prompts})

    input_tokens_per_cell = {}
    for (set_name, poem_id), (system_message, user_message) in prompts.items():
        input_tokens_per_cell[(set_name, poem_id)] = count_tokens(system_message) + count_tokens(user_message)

    total_input_tokens = sum(input_tokens_per_cell.values())
    n_cells = len(input_tokens_per_cell)  # = n_sets * n_poems, 1 call per (set, poem, model, run)

    print(f"Tokenizer: tiktoken `{ENCODING_NAME}` (closest local estimate for all 3 providers; "
          f"no offline tokenizer exists for claude-sonnet-4-6 or gemini-3.5-flash in this "
          f"environment, and counting via their real APIs would itself be a network call).")
    print(f"Eval pool: {n_poems} poems. Sets: {SET_NAMES}. "
          f"Distinct (set, poem) prompts: {n_cells}.")
    print(f"Total input tokens (all sets x all poems, 1x): {total_input_tokens:,}\n")

    def cost_for(models, n_runs, repeat_set_a):
        calls = 0
        total_cost = 0.0
        per_model = {}
        for provider in models:
            spec = MODELS[provider]
            ratio = HISTORICAL_OUT_IN_RATIO[provider]
            p_calls = 0
            p_cost = 0.0
            for (set_name, poem_id), in_tok in input_tokens_per_cell.items():
                runs = n_runs
                if set_name == "A" and repeat_set_a:
                    runs += 1
                out_tok_est = in_tok * ratio
                cost_per_call = (in_tok / 1e6) * spec["price_in"] + (out_tok_est / 1e6) * spec["price_out"]
                p_calls += runs
                p_cost += cost_per_call * runs
            per_model[provider] = {"calls": p_calls, "cost": p_cost,
                                    "model_id": spec["model_id"], "display": spec["display"]}
            calls += p_calls
            total_cost += p_cost
        return calls, total_cost, per_model

    print("=" * 70)
    print("COST TABLE — all 3 models, with and without the optional set-A repeat")
    print("=" * 70)
    for repeat in (False, True):
        label = "WITH set-A repeat" if repeat else "WITHOUT set-A repeat (default)"
        print(f"\n--- {label} ---")
        for provider in ALL_MODELS:
            calls, cost, per_model = cost_for([provider], N_RUNS, repeat)
            m = per_model[provider]
            print(f"  {m['display']:<22} ({m['model_id']:<20}) calls={m['calls']:>4}  cost=${m['cost']:.2f}")
        calls, cost, per_model = cost_for(RUN_MODELS, N_RUNS, repeat)
        print(f"  {'TOTAL (confirmed pair: ' + ' + '.join(RUN_MODELS) + ')':<45} calls={calls:>4}  cost=${cost:.2f}")
        if repeat is False:
            vs_prior = cost / COST_PLAN_PRIOR_ESTIMATE_USD * 100
            print(f"  (COST_PLAN.md's prior 50-poem/3-set/2-model/2-run estimate was "
                  f"${COST_PLAN_PRIOR_ESTIMATE_USD:.2f}; this design is half the runs "
                  f"(1 vs 2) -> {vs_prior:.0f}% of that figure is expected, not 100%)")

    print("\n" + "=" * 70)
    print("Design recap")
    print("=" * 70)
    print(f"Sets: {SET_NAMES} | Models for the real run (confirmed): {RUN_MODELS} | "
          f"N_RUNS per cell: {N_RUNS} | optional set-A repeat: {REPEAT_SET_A} (off by default)")
    print("\nSTOP: no API call has been made. Awaiting explicit go-ahead before running runner.py --confirm.")


if __name__ == "__main__":
    main()
