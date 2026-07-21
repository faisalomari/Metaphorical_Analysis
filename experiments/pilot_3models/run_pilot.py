"""Run the 3-model pilot: same poem, same prompt, all 3 providers, N runs each.

Usage:
    python run_pilot.py                        # ACTIVE_POEM from config, N_RUNS from config
    python run_pilot.py --poem Nabigha --runs 1

Requires OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY in the environment
(loaded from a .env file at the repo root via python-dotenv). Never hardcode
keys in this file.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import MODELS, N_RUNS, TEMPERATURE, RESULTS_DIR, ROOT, ACTIVE_POEM
from prompts import build_system_message, build_user_message
from providers import CALLERS

load_dotenv(ROOT / ".env")


def run(poem_key: str = ACTIVE_POEM, n_runs: int = N_RUNS, out_dir=None,
        system_message=None, user_message=None, temperature: float = TEMPERATURE,
        run_indices=None):
    """run_indices, if given, overrides range(1, n_runs+1) — e.g. [2] to add a
    2nd run to a directory that already has run1 data, without re-running or
    overwriting run1. The manifest is extended (not replaced) when the out_dir
    already has one, so existing runs' records are preserved."""
    out_dir = Path(out_dir) if out_dir else RESULTS_DIR
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    system_message = system_message if system_message is not None else build_system_message()
    user_message = user_message if user_message is not None else build_user_message(poem_key)
    run_indices = run_indices if run_indices is not None else list(range(1, n_runs + 1))

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    for provider, spec in MODELS.items():
        caller = CALLERS[provider]
        for run_idx in run_indices:
            print(f"[{poem_key}][{provider}] run {run_idx}/{n_runs} (model={spec['model_id']}) ...")
            started = datetime.now(timezone.utc).isoformat()
            try:
                result = caller(system_message, user_message, temperature)
                error = None
            except Exception as e:
                result = {"raw_text": "", "model_id": spec["model_id"], "usage": {}}
                error = f"{type(e).__name__}: {e}"
                print(f"  ERROR: {error}")

            finished = datetime.now(timezone.utc).isoformat()
            out_stem = f"{provider}_run{run_idx}"
            (raw_dir / f"{out_stem}.txt").write_text(result["raw_text"], encoding="utf-8")

            record = {
                "poem_key": poem_key,
                "provider": provider,
                "display_name": spec["display"],
                "model_id": result["model_id"],
                "run_index": run_idx,
                "temperature": temperature,
                "started_at_utc": started,
                "finished_at_utc": finished,
                "usage": result["usage"],
                "error": error,
                "raw_text_file": f"raw/{out_stem}.txt",
            }
            (raw_dir / f"{out_stem}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            manifest.append(record)

    (out_dir / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nDone. {len(manifest)} calls made. Manifest: {out_dir / 'run_manifest.json'}")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--poem", default=ACTIVE_POEM)
    parser.add_argument("--runs", type=int, default=N_RUNS)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    run(poem_key=args.poem, n_runs=args.runs, out_dir=args.out_dir)


if __name__ == "__main__":
    main()
