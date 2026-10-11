"""Resumable E1 v2 runner: for each (set, poem, verse_no, provider) cell,
one API call (one verse-unit), schema {"exists","appearance","reasoning"}.

This differs from phase4_e1 (v1)'s runner.py in call shape: v1 = one call per
whole poem (JSONL, 4 elements); v2 = one call per verse (single JSON object,
1 subtype) — Phase 3's granularity, not Phase 1's. Call count is therefore
much larger; see dryrun_v2.py before running this for real.

Usage:
    python runner.py                  # dry listing only (no API calls)
    python runner.py --confirm        # REAL API CALLS - requires --confirm
    python runner.py --confirm --pool 25      # use the persisted 25-poem pool
                                               # (config/eval_pool_25.json, poem
                                               # ids logged there; built by
                                               # build_pool_25.py)
    python runner.py --confirm --pool cheap   # same 25-poem design, but
                                               # regenerated on the fly instead
                                               # of read from disk (legacy)
    python runner.py --confirm --sets Z A

Resumability: a cell already in run_manifest.json with no error is skipped
unless --force is passed (phase4_e1 (v1)'s own convention, reused).

Per CLAUDE.md rule 5: refuses any API call without --confirm. Stops
immediately (no retry loop) on a 429/quota error, per the explicit task
instruction, rather than retrying into the same wall v1 already hit.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import (  # noqa: E402
    E1V1_EVAL_POOL_PATH, E1V1_DIR, EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR,
    ROOT, RUN_MODELS, SET_NAMES, TEMPERATURE, build_cheap_variant_pool,
)
from prompt_builder import build_messages  # noqa: E402
from providers_v2 import CALLERS  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

if str(E1V1_DIR) not in sys.path:
    sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_manifest, load_poem_json  # noqa: E402
from build_pool import build_candidate_pool  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from config import MODELS  # noqa: E402

QUOTA_ERROR_MARKERS = ("429", "RESOURCE_EXHAUSTED", "quota")
HARD_COST_CAP_USD = 10.00
PROGRESS_EVERY = 500


def call_cost(provider: str, usage: dict) -> float:
    """Worst-case cost for one call, using config.py's MODELS pricing table
    (confirmed the highest of the 3 Gemini pricing scenarios considered in
    dryrun_v2.py, so this is the conservative/safe figure for a live hard-cap
    check, not an attempt to predict the real invoice exactly)."""
    spec = MODELS[provider]
    in_tok = (usage or {}).get("input_tokens") or 0
    out_tok = (usage or {}).get("output_tokens") or 0
    return (in_tok / 1e6) * spec["price_in"] + (out_tok / 1e6) * spec["price_out"]


def spend_so_far(manifest: list) -> dict:
    """{provider: cost} + "_total", computed from every error-free manifest
    record's real logged usage (not an estimate)."""
    spend = {p: 0.0 for p in ("anthropic", "openai", "google")}
    for r in manifest:
        if r.get("error") is None:
            spend[r["provider"]] += call_cost(r["provider"], r.get("usage"))
    spend["_total"] = sum(v for k, v in spend.items() if k != "_total")
    return spend


def load_pool(which: str) -> list:
    if which == "full":
        return json.loads(E1V1_EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]
    if which == "25":
        return json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    if which == "cheap":
        return build_cheap_variant_pool(build_candidate_pool())
    raise ValueError(which)


def cell_key(record: dict) -> tuple:
    return (record["set_name"], record["poem_id"], record["verse_no"], record["provider"])


def is_quota_error(msg: str) -> bool:
    return any(m in msg for m in QUOTA_ERROR_MARKERS)


def run(sets=None, models=None, pool_name="full", out_dir=None, force=False, dry_run=True,
        max_additional_usd=None):
    """max_additional_usd: if set, the hard cap for THIS invocation is (spend already in the
    manifest at start) + max_additional_usd, instead of the absolute HARD_COST_CAP_USD total --
    needed for a small top-up run after a prior invocation already spent close to (or at) the
    absolute cap."""
    sets = sets or SET_NAMES
    models = models or RUN_MODELS
    pool = load_pool(pool_name)
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

    print(f"Planned calls: {len(plan)} (sets={sets}, models={models}, pool={pool_name} "
          f"[{len(pool)} poems], already_done={len(done)})")

    if dry_run:
        print("--dry-run / no --confirm: not making any API calls. Run dryrun_v2.py for cost estimation.")
        return manifest

    system_messages = {s: build_messages(s, "placeholder")[0] for s in sets}  # system doesn't depend on verse
    consecutive_errors = 0
    error_counts = {"anthropic": 0, "openai": 0, "google": 0}
    calls_made_this_run = 0

    for set_name, poem, verse_no, verse_text, provider in plan:
        poem_id = poem["poem_id"]
        system_message = system_messages[set_name]
        user_message = build_messages(set_name, verse_text)[1]
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


def _print_summary(manifest, error_counts, sets, models, headline):
    spend = spend_so_far(manifest)
    print(f"\n{'=' * 70}\n{headline}\n{'=' * 70}")
    print(f"Total manifest records: {len(manifest)}")
    print(f"Spend per model: openai=${spend['openai']:.4f}  google=${spend['google']:.4f}  "
          f"anthropic=${spend['anthropic']:.4f}")
    print(f"TOTAL SPEND: ${spend['_total']:.4f}  (cap ${HARD_COST_CAP_USD:.2f})")
    print(f"Error counts this invocation: {error_counts}")
    for s in sets:
        for p in models:
            ok = sum(1 for r in manifest if r["set_name"] == s and r["provider"] == p and r.get("error") is None)
            err = sum(1 for r in manifest if r["set_name"] == s and r["provider"] == p and r.get("error") is not None)
            print(f"  set {s} / {p}: {ok} ok, {err} error")


def _save(manifest, poem, set_name, poem_id, verse_no, provider, run_result, error, started,
          raw_dir, manifest_path, spec, finished=None):
    out_stem = f"{set_name}_{poem_id}_v{verse_no}_{provider}"
    (raw_dir / f"{out_stem}.txt").write_text(run_result["raw_text"], encoding="utf-8")
    record = {
        "set_name": set_name,
        "poem_id": poem_id,
        "poem_tag": poem["tag"],
        "verse_no": verse_no,
        "provider": provider,
        "display_name": spec["display"],
        "model_id": run_result["model_id"],
        "temperature": TEMPERATURE,
        "started_at_utc": started,
        "finished_at_utc": finished,
        "usage": run_result["usage"],
        "error": error,
        "raw_text_file": f"raw/{out_stem}.txt",
    }
    manifest = [r for r in manifest if cell_key(r) != cell_key(record)]
    manifest.append(record)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sets", nargs="+", default=None, choices=SET_NAMES)
    parser.add_argument("--models", nargs="+", default=None, choices=["anthropic", "openai", "google"])
    parser.add_argument("--pool", default="full", choices=["full", "cheap", "25"])
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--confirm", action="store_true",
                         help="Required to actually spend money / make API calls.")
    parser.add_argument("--max-additional-usd", type=float, default=None,
                         help="Cap THIS invocation at (spend already in manifest) + this amount, "
                              "instead of the absolute HARD_COST_CAP_USD total. For a small top-up "
                              "run after a prior invocation already spent near/at the absolute cap.")
    args = parser.parse_args()
    run(sets=args.sets, models=args.models, pool_name=args.pool, out_dir=args.out_dir,
        force=args.force, dry_run=not args.confirm, max_additional_usd=args.max_additional_usd)


if __name__ == "__main__":
    main()
