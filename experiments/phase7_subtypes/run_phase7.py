"""Step 3: the real, resumable run for Phase 7's 2 approved subtypes
(استعارة قديمة, كناية عن صفة) x {zero-shot, few-shot} x 3 models, on the
UNCHANGED eval_pool_25.json pool (25 poems, 327 verse-units; user chose
Option (a) -- see docs/phase4/SESSION_LOG.md 2026-10-29).

One call per (subtype, condition, poem, verse, provider) cell. Models:
anthropic/openai via pilot_3models.providers (call_anthropic/call_openai,
unchanged, frozen harness), google via phase3_subelements.providers_fixed
.call_google_fixed (per the task's own "Gemini via providers_fixed"
instruction -- correctly bills hidden thinking tokens, unlike the plain
pilot_3models.providers.call_google).

Stop conditions (declared, task's own gate):
  - any 429/quota/credit error -> stop immediately, no retry.
  - a SINGLE provider's error streak reaches 5 IN A ROW, counted PER
    PROVIDER and reset only by THAT PROVIDER's own next success --
    NOT a shared/global counter that other providers' successes can
    reset. This is a deliberate fix of the exact bug already found and
    documented in docs/phase4/E1_V2_ERAS_FEWSHOT.md (the old global
    counter never fired during a real 167-cell anthropic credit outage
    because interleaved openai/google successes kept resetting it).
  - cumulative real spend (from logged usage, not estimated) exceeds the
    hard cap passed via --max-additional-usd.

Resumable: a cell already present in run_manifest.json with no error is
skipped on a later invocation (same convention phase4_e1_v2/runner.py
already uses), unless --force.

Usage:
    python run_phase7.py                                  # dry listing only
    python run_phase7.py --confirm --max-additional-usd 15
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase7_config import CONFIG_DIR, EVAL_POOL_25_PATH, PHASE3_DIR, RESULTS_DIR, ROOT  # noqa: E402
from census import load_poem_json  # noqa: E402
from subtype_prompts import build_messages  # noqa: E402
from fewshot_prompts import build_messages_fewshot  # noqa: E402
from providers_fixed import call_google_fixed  # noqa: E402

PILOT_DIR = ROOT / "experiments" / "pilot_3models"
sys.path.insert(0, str(PILOT_DIR))
from providers import call_anthropic, call_openai  # noqa: E402
from config import MODELS  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

APPROVED_SUBTYPES = ["استعارة قديمة", "كناية عن صفة"]
CONDITIONS = ["zero", "few"]
PROVIDER_ORDER = ["anthropic", "openai", "google"]
TEMPERATURE = 0.0
QUOTA_ERROR_MARKERS = ("429", "RESOURCE_EXHAUSTED", "quota", "credit balance")
CONSECUTIVE_ERROR_LIMIT = 5
PROGRESS_EVERY = 200

CALLERS = {"anthropic": call_anthropic, "openai": call_openai, "google": call_google_fixed}


def call_cost(provider: str, usage: dict) -> float:
    spec = MODELS[provider]
    in_tok = (usage or {}).get("input_tokens") or 0
    out_tok = (usage or {}).get("output_tokens") or 0
    return (in_tok / 1e6) * spec["price_in"] + (out_tok / 1e6) * spec["price_out"]


def spend_so_far(manifest: list) -> dict:
    spend = {p: 0.0 for p in PROVIDER_ORDER}
    for r in manifest:
        if r.get("error") is None:
            spend[r["provider"]] += call_cost(r["provider"], r.get("usage"))
    spend["_total"] = sum(spend.values())
    return spend


def is_quota_error(msg: str) -> bool:
    return any(m in msg for m in QUOTA_ERROR_MARKERS)


def cell_key(record: dict) -> tuple:
    return (record["subtype"], record["condition"], record["poem_id"], record["verse_no"], record["provider"])


def build_system_messages(sets_doc: dict) -> dict:
    """{(subtype, condition): system_message}. Verse-independent, built once."""
    out = {}
    for subtype in APPROVED_SUBTYPES:
        examples = sets_doc["sets"][subtype]["examples"]
        extra = [{"verse_text": ex["text"], "span": ex["annotations"][0]["span"],
                   "explanation": ex["annotations"][0]["analysis"]} for ex in examples]
        out[(subtype, "zero")] = build_messages(subtype, "placeholder")[0]
        out[(subtype, "few")] = build_messages_fewshot(subtype, "placeholder", extra)[0]
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-additional-usd", type=float, default=None)
    parser.add_argument("--limit-poems", type=int, default=None,
                         help="Smoke-test only: cap the pool to the first N poems (by poem_id).")
    parser.add_argument("--limit-verses-per-poem", type=int, default=None,
                         help="Smoke-test only: cap verses to the first N per poem.")
    args = parser.parse_args()

    pool_doc = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
    poems = sorted(pool_doc["poems"], key=lambda p: int(p["poem_id"]))
    if args.limit_poems:
        poems = poems[: args.limit_poems]
    sets_doc = json.loads((CONFIG_DIR / "phase7_example_sets.json").read_text(encoding="utf-8"))
    system_messages = build_system_messages(sets_doc)

    raw_dir = RESULTS_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = RESULTS_DIR / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    done = {cell_key(r) for r in manifest if r.get("error") is None} if not args.force else set()

    baseline_spend = spend_so_far(manifest)["_total"]
    effective_cap = (baseline_spend + args.max_additional_usd) if args.max_additional_usd is not None else None
    if effective_cap is None:
        print("No --max-additional-usd given: refusing to set an unbounded cap.")
        if args.confirm:
            return
    print(f"Baseline spend already in manifest: ${baseline_spend:.4f}. "
          f"Effective cap for this invocation: ${effective_cap if effective_cap is not None else 'UNBOUNDED'}")

    poem_cache = {p["poem_id"]: load_poem_json(p["poem_id"]) for p in poems}
    plan = []
    for poem in poems:
        pid = poem["poem_id"]
        pj = poem_cache[pid]
        verses_by_no = {v["verse_index"]: v["text"] for v in pj["verses"]}
        n_verses_this_poem = pj["verse_count"]
        if args.limit_verses_per_poem:
            n_verses_this_poem = min(n_verses_this_poem, args.limit_verses_per_poem)
        for verse_no in range(1, n_verses_this_poem + 1):
            for subtype in APPROVED_SUBTYPES:
                for condition in CONDITIONS:
                    for provider in PROVIDER_ORDER:
                        key = (subtype, condition, pid, verse_no, provider)
                        if key in done:
                            continue
                        plan.append((subtype, condition, pid, verse_no, verses_by_no[verse_no], provider))

    print(f"Planned calls: {len(plan)} (2 subtypes x 2 conditions x 3 models x 327 verses = 3924 total; "
          f"already_done={len(done)})")

    if not args.confirm:
        print("--dry-run / no --confirm: not making any API calls.")
        return

    error_streak = {p: 0 for p in PROVIDER_ORDER}  # PER-PROVIDER, reset only by that provider's own success
    calls_made = 0

    for subtype, condition, pid, verse_no, verse_text, provider in plan:
        system_message = system_messages[(subtype, condition)]
        user_message = build_messages(subtype, verse_text)[1]
        caller = CALLERS[provider]
        spec = MODELS[provider]

        print(f"[{subtype}][{condition}][{pid}][v{verse_no}][{provider}] model={spec['model_id']} ...")
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = caller(system_message, user_message, TEMPERATURE)
            error = None
            error_streak[provider] = 0
        except Exception as e:
            result = {"raw_text": "", "model_id": spec["model_id"], "usage": {}}
            error = f"{type(e).__name__}: {e}"
            print(f"  ERROR [{provider}]: {error}")
            manifest = save_record(manifest, subtype, condition, pid, verse_no, provider, result, error,
                                    started, None, raw_dir, manifest_path, spec)
            if is_quota_error(error):
                print("  QUOTA/429/CREDIT ERROR -- stopping immediately, no retry.")
                print_summary(manifest, subtype, condition, "STOPPED: quota/429/credit error")
                return
            error_streak[provider] += 1
            if error_streak[provider] >= CONSECUTIVE_ERROR_LIMIT:
                print(f"  {provider}: {CONSECUTIVE_ERROR_LIMIT} consecutive errors (per-provider counter, "
                      f"regardless of interleaving) -- stopping.")
                print_summary(manifest, subtype, condition, f"STOPPED: {provider} hit {CONSECUTIVE_ERROR_LIMIT} consecutive errors")
                return
            continue  # do not count a failed call toward spend/cap check below

        finished = datetime.now(timezone.utc).isoformat()
        manifest = save_record(manifest, subtype, condition, pid, verse_no, provider, result, error,
                                started, finished, raw_dir, manifest_path, spec)
        calls_made += 1

        spend = spend_so_far(manifest)
        if effective_cap is not None and spend["_total"] > effective_cap:
            print(f"\n*** HARD COST CAP EXCEEDED: ${spend['_total']:.4f} > ${effective_cap:.4f} *** STOPPING.")
            print_summary(manifest, subtype, condition, "STOPPED: hard cost cap exceeded")
            return

        if calls_made % PROGRESS_EVERY == 0:
            print(f"\n--- PROGRESS: {calls_made} calls this invocation ({len(manifest)} manifest records) ---")
            print(f"    spend: anthropic=${spend['anthropic']:.4f} openai=${spend['openai']:.4f} "
                  f"google=${spend['google']:.4f} TOTAL=${spend['_total']:.4f} (cap "
                  f"{'$' + format(effective_cap, '.2f') if effective_cap is not None else 'UNBOUNDED'})")
            print(f"    error streaks: {error_streak}\n")

    print_summary(manifest, None, None, "DONE: plan exhausted")


def save_record(manifest, subtype, condition, poem_id, verse_no, provider, result, error, started,
                 finished, raw_dir, manifest_path, spec):
    stem = f"{subtype}_{condition}_{poem_id}_v{verse_no}_{provider}".replace(" ", "_").replace("/", "_")
    (raw_dir / f"{stem}.txt").write_text(result["raw_text"], encoding="utf-8")
    record = {
        "subtype": subtype, "condition": condition, "poem_id": poem_id, "verse_no": verse_no,
        "provider": provider, "display_name": MODELS[provider]["display"], "model_id": result["model_id"],
        "temperature": TEMPERATURE, "started_at_utc": started, "finished_at_utc": finished,
        "usage": result["usage"], "error": error, "raw_text_file": f"raw/{stem}.txt",
    }
    manifest = [r for r in manifest if cell_key(r) != cell_key(record)]
    manifest.append(record)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def print_summary(manifest, last_subtype, last_condition, headline):
    spend = spend_so_far(manifest)
    print(f"\n{'=' * 70}\n{headline}\n{'=' * 70}")
    print(f"Total manifest records: {len(manifest)}")
    print(f"Spend: anthropic=${spend['anthropic']:.4f} openai=${spend['openai']:.4f} "
          f"google=${spend['google']:.4f} TOTAL=${spend['_total']:.4f}")
    print("\nCoverage per (subtype, condition, model) -- target 327 ok each:")
    for subtype in APPROVED_SUBTYPES:
        for condition in CONDITIONS:
            for provider in PROVIDER_ORDER:
                ok = sum(1 for r in manifest if r["subtype"] == subtype and r["condition"] == condition
                         and r["provider"] == provider and r.get("error") is None)
                err = sum(1 for r in manifest if r["subtype"] == subtype and r["condition"] == condition
                          and r["provider"] == provider and r.get("error") is not None)
                flag = "" if ok == 327 else "  <-- INCOMPLETE"
                print(f"  {subtype} / {condition} / {provider}: {ok} ok, {err} error{flag}")


if __name__ == "__main__":
    main()
