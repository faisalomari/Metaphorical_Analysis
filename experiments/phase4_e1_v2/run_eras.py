"""Step 4 runner for the poet-era few-shot sets (M1/M2/E1/E2/H1/H2).

A STANDALONE runner (not a modification of runner.py), same reasoning as
run_multipoet.py: these sets need multipoet_prompt_builder.build_system_
message_n (N=2 examples, drawn by era rather than by period-diversity
round robin) instead of prompt_builder.build_messages's fixed Z/A/B/C/D/D2
call shape. UNLIKE run_multipoet.py, this reuses the SAME pool
(eval_pool_25.json) Z/A/B/C/D/D2 already ran on -- no separate pool, so no
9-poem-overlap caveat for the later analysis step. Reuses runner.py's
manifest/cost/resumability/hard-cap/quota-stop machinery unchanged
(spend_so_far, call_cost, cell_key, is_quota_error, _save, _print_summary).
Writes into the SAME results/phase4_e1_v2/run_manifest.json Z/A/B/C/D/D2/
F5/F10 already use (set_name values M1/M2/E1/E2/H1/H2 never collide with
an existing cell_key -- purely additive).

Usage:
    python run_eras.py                           # dry listing only
    python run_eras.py --confirm --max-additional-usd 20
    python run_eras.py --confirm --sets M1 M2 --max-additional-usd 20
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR, ROOT, TEMPERATURE  # noqa: E402
from eras_config import ERAS_SET_NAMES  # noqa: E402
from eras_examples import build_eras_sets  # noqa: E402
from multipoet_prompt_builder import build_system_message_n, build_user_message  # noqa: E402
from providers_v2 import CALLERS  # noqa: E402
from runner import (  # noqa: E402
    HARD_COST_CAP_USD, MODELS, PROGRESS_EVERY, _print_summary, _save, call_cost,
    cell_key, is_quota_error, spend_so_far,
)

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))

DEFAULT_MODELS = ["anthropic", "openai", "google"]
DEFAULT_SETS = list(ERAS_SET_NAMES)


def load_pool() -> list:
    return json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]


def load_example_sets() -> dict:
    """Rebuild from eras_examples (deterministic) rather than trusting a
    possibly-stale persisted file, then cross-check against the committed
    config/eras_example_sets.json -- stop if they ever disagree."""
    sets, _pools, _groups, _filter_counts, _eligible = build_eras_sets()
    persisted = json.loads(
        (Path(__file__).resolve().parent / "config" / "eras_example_sets.json").read_text(encoding="utf-8")
    )["sets"]
    for name in ERAS_SET_NAMES:
        live_ids = [(e["poem_id"], e["verse_no"]) for e in sets[name]]
        persisted_ids = [(e["poem_id"], e["verse_no"]) for e in persisted[name]]
        assert live_ids == persisted_ids, (
            f"set {name}: rebuilt example draw does not match the committed "
            f"config/eras_example_sets.json -- STOP, something changed upstream "
            f"(live={live_ids} persisted={persisted_ids})"
        )
    return sets


def run(sets=None, models=None, out_dir=None, force=False, dry_run=True, max_additional_usd=None):
    sets = sets or DEFAULT_SETS
    models = models or DEFAULT_MODELS
    pool = load_pool()
    example_sets = load_example_sets()
    out_dir = Path(out_dir) if out_dir else RESULTS_DIR
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    done = {cell_key(r) for r in manifest if r.get("error") is None} if not force else set()

    baseline_spend = spend_so_far(manifest)["_total"]
    effective_cap = (baseline_spend + max_additional_usd) if max_additional_usd is not None else HARD_COST_CAP_USD
    print(f"Baseline spend already in manifest: ${baseline_spend:.4f}. Effective cap for this "
          f"invocation: ${effective_cap:.4f}"
          + (f" (= baseline + ${max_additional_usd:.2f} extra)" if max_additional_usd is not None else ""))

    poem_cache = {}
    plan = []
    for poem in pool:
        poem_id = poem["poem_id"]
        if poem_id not in poem_cache:
            from ali_poems_io import load_poem_json  # local import, same sys.path convention
            poem_cache[poem_id] = load_poem_json(poem_id)
        pj = poem_cache[poem_id]
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        for set_name in sets:
            for verse_no in range(1, pj["verse_count"] + 1):
                for provider in models:
                    key = (set_name, poem_id, verse_no, provider)
                    if key in done:
                        continue
                    plan.append((set_name, poem, verse_no, verses_by_no[verse_no], provider))

    print(f"Planned calls: {len(plan)} (sets={sets}, models={models}, pool=eval_pool_25 "
          f"[{len(pool)} poems], already_done={len(done)})")

    if dry_run:
        print("--dry-run / no --confirm: not making any API calls. Run dryrun_eras.py for cost estimation.")
        return manifest

    system_messages = {s: build_system_message_n(example_sets[s]) for s in sets}
    consecutive_errors = 0
    error_counts = {"anthropic": 0, "openai": 0, "google": 0, "anthropic_opus": 0}
    calls_made_this_run = 0

    for set_name, poem, verse_no, verse_text, provider in plan:
        poem_id = poem["poem_id"]
        system_message = system_messages[set_name]
        user_message = build_user_message(verse_text)
        caller = CALLERS[provider]
        spec = MODELS[provider]

        print(f"[set {set_name}][{poem_id}][v{verse_no}][{provider}] model={spec['model_id']} ...")
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = caller(system_message, user_message, TEMPERATURE)
            error = None
            consecutive_errors = 0
        except Exception as e:
            result = {"raw_text": "", "model_id": spec["model_id"], "usage": {}}
            error = f"{type(e).__name__}: {e}"
            error_counts[provider] += 1
            print(f"  ERROR: {error}")
            if is_quota_error(error):
                print("  QUOTA/429 ERROR — stopping immediately per task instruction (no retry loop).")
                manifest = _save(manifest, poem, set_name, poem_id, verse_no, provider, run_result=result,
                                  error=error, started=started, raw_dir=raw_dir, manifest_path=manifest_path,
                                  spec=spec)
                _print_summary(manifest, error_counts, sets, models, "STOPPED: quota/429 error")
                return manifest
            consecutive_errors += 1
            if consecutive_errors >= 5:
                print("  5 consecutive errors — stopping per task instruction.")
                manifest = _save(manifest, poem, set_name, poem_id, verse_no, provider, run_result=result,
                                  error=error, started=started, raw_dir=raw_dir, manifest_path=manifest_path,
                                  spec=spec)
                _print_summary(manifest, error_counts, sets, models, "STOPPED: 5 consecutive errors")
                return manifest
        finished = datetime.now(timezone.utc).isoformat()
        manifest = _save(manifest, poem, set_name, poem_id, verse_no, provider, run_result=result,
                          error=error, started=started, finished=finished, raw_dir=raw_dir,
                          manifest_path=manifest_path, spec=spec)
        calls_made_this_run += 1

        spend = spend_so_far(manifest)
        if spend["_total"] > effective_cap:
            print(f"\n*** HARD COST CAP EXCEEDED: ${spend['_total']:.4f} > ${effective_cap:.4f} *** "
                  f"STOPPING IMMEDIATELY.")
            _print_summary(manifest, error_counts, sets, models, "STOPPED: hard cost cap exceeded")
            return manifest

        if calls_made_this_run % PROGRESS_EVERY == 0:
            print(f"\n--- PROGRESS: {calls_made_this_run} calls made this invocation "
                  f"({len(manifest)} total manifest records) ---")
            print(f"    spend so far: openai=${spend['openai']:.4f}  google=${spend['google']:.4f}  "
                  f"anthropic=${spend['anthropic']:.4f}  TOTAL=${spend['_total']:.4f} "
                  f"(cap ${effective_cap:.2f})")
            print(f"    errors so far: {error_counts}\n")

    _print_summary(manifest, error_counts, sets, models, "DONE: plan exhausted")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sets", nargs="+", default=None, choices=ERAS_SET_NAMES)
    parser.add_argument("--models", nargs="+", default=None,
                         choices=["anthropic", "openai", "google"])
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--confirm", action="store_true",
                         help="Required to actually spend money / make API calls.")
    parser.add_argument("--max-additional-usd", type=float, default=None)
    args = parser.parse_args()
    run(sets=args.sets, models=args.models, out_dir=args.out_dir, force=args.force,
        dry_run=not args.confirm, max_additional_usd=args.max_additional_usd)


if __name__ == "__main__":
    main()
