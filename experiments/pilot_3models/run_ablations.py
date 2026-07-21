"""Run the v1+v2 / v1+v3 ablations, plus a genuine 2nd run of v1_boundary
(for real run-to-run consistency data, since the earlier "0.433 vs 0.454" was
strict-vs-token on a single run, not two runs)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DEV_POEMS, RESULTS_DIR
from prompts import build_user_message
from prompt_variants import build_system_message_variant
from run_pilot import run

VARIANTS_DIR = RESULTS_DIR / "dev_variants"


def main():
    # New ablations: 1 run each
    for variant_key in ["v1_v2", "v1_v3"]:
        sm = build_system_message_variant(variant_key)
        for poem_key in DEV_POEMS:
            um = build_user_message(poem_key)
            out_dir = VARIANTS_DIR / variant_key / poem_key
            run(poem_key=poem_key, n_runs=1, out_dir=out_dir, system_message=sm, user_message=um)

    # v1_boundary run 2 (added into the existing run1 dir/manifest so
    # analyze.load_all_runs picks up both runs together)
    sm = build_system_message_variant("v1_boundary")
    for poem_key in DEV_POEMS:
        um = build_user_message(poem_key)
        out_dir = VARIANTS_DIR / "v1_boundary" / poem_key
        # run_index=2 alongside the existing run_index=1
        import json
        from datetime import datetime, timezone
        from config import MODELS
        from providers import CALLERS

        raw_dir = out_dir / "raw"
        manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
        for provider, spec in MODELS.items():
            print(f"[{poem_key}][{provider}] v1_boundary run 2/2 (consistency check) ...")
            started = datetime.now(timezone.utc).isoformat()
            result = CALLERS[provider](sm, um, 0.0)
            finished = datetime.now(timezone.utc).isoformat()
            out_stem = f"{provider}_run2"
            (raw_dir / f"{out_stem}.txt").write_text(result["raw_text"], encoding="utf-8")
            record = {
                "poem_key": poem_key, "provider": provider, "display_name": spec["display"],
                "model_id": result["model_id"], "run_index": 2, "temperature": 0.0,
                "started_at_utc": started, "finished_at_utc": finished,
                "usage": result["usage"], "error": None, "raw_text_file": f"raw/{out_stem}.txt",
            }
            (raw_dir / f"{out_stem}.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
            manifest.append(record)
        (out_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
