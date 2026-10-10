"""Runners for Config A (pure model effect: v4_combined unchanged, on Fable
5) and Config B (pure terminology effect: v4_combined + terminology
correction, on Sonnet 4.6). Whole-poem, same shape as Phase 1's
run_pilot.run() - one call per (poem, run) - so the manifest/raw-file format
is byte-compatible with the existing analyze.load_all_runs() /
span_scoring.score_span_level() harness, unmodified.

Usage:
    python run_config_ab.py --config a
    python run_config_ab.py --config b
    python run_config_ab.py --config a --poems Imru2   # single poem
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))

from phase2_config import ROOT, SEC3I_POEMS, MODELS as P2_MODELS, N_RUNS as P1_N_RUNS, TEMPERATURE  # noqa: E402
from prompts import build_user_message  # noqa: E402  (Phase 1, unchanged)
from prompt_variants import build_system_message_variant  # noqa: E402
from prompt_config_b import build_config_b_system_message  # noqa: E402
from providers import call_anthropic  # noqa: E402  (Phase 1, unchanged - Config B / Sonnet)
from providers_v2 import call_fable5  # noqa: E402  (Config A)

load_dotenv(ROOT / ".env")

RESULTS_DIR = ROOT / "results" / "phase2_chatlike"


def _call_fable5_adapter(system_message, user_message, temperature=None):
    # run()'s call signature is (system, user, temperature) for every
    # provider; Fable 5 takes no temperature, so it's just dropped here.
    return call_fable5(system_message, user_message, effort="medium")


CONFIGS = {
    "a": {
        "provider_key": "anthropic_fable5",
        "caller": _call_fable5_adapter,
        "system_message": lambda: build_system_message_variant("v4_combined"),
        "out_subdir": "config_a",
    },
    "b": {
        "provider_key": "anthropic",
        "caller": call_anthropic,
        "system_message": build_config_b_system_message,
        "out_subdir": "config_b",
    },
}


def run_one_poem(config_key: str, poem_key: str, n_runs: int = P1_N_RUNS):
    cfg = CONFIGS[config_key]
    spec = P2_MODELS[cfg["provider_key"]]
    system_message = cfg["system_message"]()
    user_message = build_user_message(poem_key)
    out_dir = RESULTS_DIR / cfg["out_subdir"] / poem_key
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    provider = cfg["provider_key"]

    for run_idx in range(1, n_runs + 1):
        print(f"[Config {config_key.upper()}][{poem_key}] run {run_idx}/{n_runs} (model={spec['model_id']}) ...", flush=True)
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = cfg["caller"](system_message, user_message, TEMPERATURE)
            error = result.get("error")
        except Exception as e:
            result = {"raw_text": "", "model_id": spec["model_id"], "usage": {}}
            error = f"{type(e).__name__}: {e}"
        finished = datetime.now(timezone.utc).isoformat()
        out_stem = f"{provider}_run{run_idx}"
        (raw_dir / f"{out_stem}.txt").write_text(result["raw_text"], encoding="utf-8")

        record = {
            "poem_key": poem_key,
            "provider": provider,
            "display_name": spec["display"],
            "model_id": result.get("model_id", spec["model_id"]),
            "run_index": run_idx,
            "temperature": TEMPERATURE if provider == "anthropic" else None,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "usage": result.get("usage", {}),
            "error": error,
            "raw_text_file": f"raw/{out_stem}.txt",
        }
        manifest = [r for r in manifest if not (r["provider"] == provider and r["run_index"] == run_idx)]
        manifest.append(record)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        u = result.get("usage", {})
        print(f"  -> in={u.get('input_tokens')} out={u.get('output_tokens')} error={error}", flush=True)

    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", choices=["a", "b"], required=True)
    parser.add_argument("--poems", nargs="*", default=SEC3I_POEMS)
    parser.add_argument("--runs", type=int, default=P1_N_RUNS)
    args = parser.parse_args()
    for poem in args.poems:
        run_one_poem(args.config, poem, n_runs=args.runs)


if __name__ == "__main__":
    main()
