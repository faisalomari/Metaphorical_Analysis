"""DRY RUN cost estimate for Claude Opus 5.5 on set A only -- NO API calls.

Unlike dryrun_v2.py (which estimates input tokens with a tiktoken approximation
and output tokens from Phase 3's logged average), this script prices the Opus-
on-set-A run from REAL already-logged usage: the 327 Claude-Sonnet-4.6-on-set-A
manifest cells (same prompts Opus will see -- set A's prompt construction does
not depend on provider, see prompt_builder.build_messages) give a real average
input/output token count per call, which is a much tighter anchor than a token-
count approximation for a model that hasn't been called yet.

Per CLAUDE.md rule 5: cost estimate printed here, no API call anywhere in this
script. Awaiting explicit "go" before running runner.py --confirm.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EXTRA_MODEL_PRICING, EVAL_POOL_25_PATH, RESULTS_DIR  # noqa: E402

OUTPUT_INFLATION_SCENARIO = 1.30  # +30% output-length scenario (Opus 5.5's adaptive
                                   # thinking / different default effort vs. Sonnet 4.6
                                   # means its real output length is not guaranteed to
                                   # match Sonnet's).


def main():
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))

    set_a_sonnet = [r for r in manifest
                     if r["set_name"] == "A" and r["provider"] == "anthropic" and r.get("error") is None]
    n_calls = len(set_a_sonnet)
    expected_calls = pool["pool_verses"]

    print(f"Set A pool: {pool['pool_size']} poems, {expected_calls} verse-units.")
    print(f"Claude-Sonnet-4.6-on-set-A manifest cells found: {n_calls} "
          f"(expected {expected_calls}): {'OK' if n_calls == expected_calls else '*** MISMATCH ***'}")
    assert n_calls == expected_calls, "set A manifest is not complete for anthropic -- check before costing"

    avg_in = sum(r["usage"]["input_tokens"] for r in set_a_sonnet) / n_calls
    avg_out = sum(r["usage"]["output_tokens"] for r in set_a_sonnet) / n_calls
    print(f"Real average input tokens/call (Sonnet, set A): {avg_in:.2f}")
    print(f"Real average output tokens/call (Sonnet, set A): {avg_out:.2f}")

    spec = EXTRA_MODEL_PRICING["anthropic_opus"]
    print(f"\nOpus 5.5 pricing: model_id={spec['model_id']!r}  "
          f"${spec['price_in']:.2f}/MTok in, ${spec['price_out']:.2f}/MTok out")

    base_cost = expected_calls * (avg_in / 1e6 * spec["price_in"] + avg_out / 1e6 * spec["price_out"])
    inflated_out = avg_out * OUTPUT_INFLATION_SCENARIO
    high_cost = expected_calls * (avg_in / 1e6 * spec["price_in"] + inflated_out / 1e6 * spec["price_out"])

    print(f"\nPlanned calls (anthropic_opus x set A x {expected_calls} verse-units): {expected_calls}")
    print(f"Base cost estimate (real Sonnet-set-A avg tokens, Opus 5.5 pricing): ${base_cost:,.4f}")
    print(f"+{int((OUTPUT_INFLATION_SCENARIO - 1) * 100)}% output-length scenario "
          f"(avg_out={inflated_out:.2f}): ${high_cost:,.4f}")
    print(f"\nTask's own expectation band: ~$2.40-$3.00 -- "
          f"{'within band' if 2.40 <= base_cost <= 3.00 else 'OUTSIDE band, re-check'}.")

    print(f"\n{'=' * 70}\nSTOP\n{'=' * 70}")
    print("No API call has been made anywhere in this task. Awaiting explicit go-ahead before "
          "running: python runner.py --confirm --sets A --models anthropic_opus "
          "--max-additional-usd 5")


if __name__ == "__main__":
    main()
