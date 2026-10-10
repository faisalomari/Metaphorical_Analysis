"""Resumable E1 runner: for each (example set, poem, provider, run_index)
cell, call the provider once (whole-poem call, same shape as
pilot_3models.run_pilot) and save raw output + a per-cell manifest record.

Usage:
    python runner.py --dry-run             # see dryrun.py instead for real cost estimate
    python runner.py                       # REAL API CALLS - requires --confirm
    python runner.py --confirm --sets A    # run only set A (e.g. for the repeat)
    python runner.py --confirm --repeat-set-a

Resumability: a cell already present in run_manifest.json (same set, poem_id,
provider, run_index) is skipped unless --force is passed, following
pilot_3models/run_per_verse.py's "replace on explicit retry, otherwise skip"
convention.

Per CLAUDE.md rule 5, this script refuses to make any API call unless
--confirm is passed explicitly on the command line (the dry-run cost gate
lives in dryrun.py and must be run, and the user's go-ahead given, first).
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_config import (  # noqa: E402
    EVAL_POOL_PATH, EXAMPLE_SETS_PATH, PILOT_DIR, REPEAT_SET_A, RESULTS_DIR,
    ROOT, RUN_MODELS, SET_NAMES, TEMPERATURE,
)
from ali_poems_io import build_poem_text, load_poem_json  # noqa: E402
from fewshot_examples import build_system_message_e1  # noqa: E402

from dotenv import load_dotenv  # noqa: E402
load_dotenv(ROOT / ".env")

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from prompts import ANALYSIS_INSTRUCTIONS  # noqa: E402
from providers import CALLERS  # noqa: E402
from config import MODELS  # noqa: E402


def load_eval_pool() -> list:
    return json.loads(EVAL_POOL_PATH.read_text(encoding="utf-8"))["poems"]


def load_example_sets() -> dict:
    return json.loads(EXAMPLE_SETS_PATH.read_text(encoding="utf-8"))


def build_user_message(poem_json: dict) -> str:
    return ANALYSIS_INSTRUCTIONS + "\n" + build_poem_text(poem_json) + "\n"


def cell_key(record: dict) -> tuple:
    return (record["set_name"], record["poem_id"], record["provider"], record["run_index"])


def run(sets=None, models=None, n_runs_override=None, repeat_set_a=None,
        out_dir=None, force=False, dry_run=True):
    sets = sets or SET_NAMES
    models = models or RUN_MODELS
    repeat_set_a = REPEAT_SET_A if repeat_set_a is None else repeat_set_a
    out_dir = Path(out_dir) if out_dir else RESULTS_DIR
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    example_sets = load_example_sets()
    pool = load_eval_pool()

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    done = {cell_key(r) for r in manifest if r.get("error") is None} if not force else set()

    plan = []
    for set_name in sets:
        run_indices = [1]
        if set_name == "A" and repeat_set_a:
            run_indices = [1, 2]
        n_runs = n_runs_override or len(run_indices)
        run_indices = run_indices[:n_runs] if n_runs_override else run_indices
        for poem in pool:
            for provider in models:
                for run_idx in run_indices:
                    key = (set_name, poem["poem_id"], provider, run_idx)
                    if key in done:
                        continue
                    plan.append((set_name, poem, provider, run_idx))

    print(f"Planned calls: {len(plan)} (sets={sets}, models={models}, "
          f"repeat_set_a={repeat_set_a}, pool_size={len(pool)}, already_done={len(done)})")

    if dry_run:
        print("--dry-run / no --confirm: not making any API calls. "
              "Run dryrun.py for cost estimation.")
        return manifest

    system_messages = {s: build_system_message_e1(example_sets[s]) for s in sets}
    poem_texts = {}  # cache per poem_id

    for set_name, poem, provider, run_idx in plan:
        poem_id = poem["poem_id"]
        if poem_id not in poem_texts:
            pj = load_poem_json(poem_id)
            poem_texts[poem_id] = (pj, build_user_message(pj))
        pj, user_message = poem_texts[poem_id]
        system_message = system_messages[set_name]
        caller = CALLERS[provider]
        spec = MODELS[provider]

        print(f"[set {set_name}][{poem_id}][{provider}] run {run_idx} (model={spec['model_id']}) ...")
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = caller(system_message, user_message, TEMPERATURE)
            error = None
        except Exception as e:
            result = {"raw_text": "", "model_id": spec["model_id"], "usage": {}}
            error = f"{type(e).__name__}: {e}"
            print(f"  ERROR: {error}")
        finished = datetime.now(timezone.utc).isoformat()

        out_stem = f"{set_name}_{poem_id}_{provider}_run{run_idx}"
        (raw_dir / f"{out_stem}.txt").write_text(result["raw_text"], encoding="utf-8")

        record = {
            "set_name": set_name,
            "poem_id": poem_id,
            "poem_tag": poem["tag"],
            "provider": provider,
            "display_name": spec["display"],
            "model_id": result["model_id"],
            "run_index": run_idx,
            "temperature": TEMPERATURE,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "usage": result["usage"],
            "error": error,
            "raw_text_file": f"raw/{out_stem}.txt",
        }
        manifest = [r for r in manifest if cell_key(r) != cell_key(record)]
        manifest.append(record)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nDone. {len(manifest)} records in manifest: {manifest_path}")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sets", nargs="+", default=None, choices=SET_NAMES)
    parser.add_argument("--models", nargs="+", default=None, choices=["anthropic", "openai", "google"])
    parser.add_argument("--repeat-set-a", action="store_true", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--confirm", action="store_true",
                         help="Required to actually spend money / make API calls.")
    args = parser.parse_args()
    run(sets=args.sets, models=args.models, repeat_set_a=args.repeat_set_a,
        out_dir=args.out_dir, force=args.force, dry_run=not args.confirm)


if __name__ == "__main__":
    main()
