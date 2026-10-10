"""Config C runner - two-stage, per-verse, Fable 5 (stage 1, free-form
Arabic analysis) + GPT-5.4-mini (stage 2, extraction into the strict JSONL
schema). Aggregates each (run) into ONE manifest record + ONE JSONL raw
file, matching run_per_verse.py's convention exactly, so the unmodified
Phase 1 harness (analyze.load_all_runs, span_scoring.score_span_level)
scores it without changes. Stage 1's full free-form analysis text is
additionally saved per verse (stage1_analysis.json) - not read by the
scoring pipeline, but needed for the verse-specific qualitative check
(PROJECT_STATE.md Phase 2 sec3i, point 3).

Scope for this run: Imru2 only (per the approved cost estimate). Do NOT
extend to Nabigha without a fresh confirmation - see PROJECT_STATE.md.

Usage:
    python run_config_c.py --poem Imru2 --runs 2
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))

from phase2_config import ROOT, N_RUNS as P1_N_RUNS  # noqa: E402
from per_verse_prompts import get_verses  # noqa: E402
from prompt_config_c import (  # noqa: E402
    STAGE1_SYSTEM_MESSAGE, build_stage1_user_message,
    STAGE2_SYSTEM_MESSAGE, build_stage2_user_message,
)
from providers_v2 import call_fable5  # noqa: E402
from providers import call_openai  # noqa: E402  (Phase 1, unchanged - stage 2 extractor)

load_dotenv(ROOT / ".env")

RESULTS_DIR = ROOT / "results" / "phase2_chatlike"
CONFIG_C_DIR = RESULTS_DIR / "config_c"
FENCE_RE = re.compile(r"^```(?:json|jsonl)?\s*|\s*```$", re.MULTILINE)


def _normalize_json_line(raw_text: str) -> str:
    cleaned = FENCE_RE.sub("", raw_text.strip()).strip()
    try:
        obj = json.loads(cleaned)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        return " ".join(cleaned.split())


def run_config_c(poem_key: str = "Imru2", n_runs: int = P1_N_RUNS, effort: str = "medium"):
    verses = get_verses(poem_key)
    out_dir = CONFIG_C_DIR / poem_key
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    provider = "config_c"

    for run_idx in range(1, n_runs + 1):
        print(f"[Config C][{poem_key}] run {run_idx}/{n_runs} ({len(verses)} verses x 2 stages) ...", flush=True)
        started = datetime.now(timezone.utc).isoformat()
        lines = []
        stage1_analyses = []  # [{verse_no, verse_text, analysis, stage1_usage, stage1_error}, ...]
        total_in_s1 = total_out_s1 = 0
        total_in_s2 = total_out_s2 = 0
        errors = []

        for verse_no, verse_line in enumerate(verses, start=1):
            # ---- Stage 1: free-form Arabic analysis on Fable 5 ----
            s1_user = build_stage1_user_message(poem_key, verse_line)
            try:
                s1 = call_fable5(STAGE1_SYSTEM_MESSAGE, s1_user, effort=effort)
                s1_error = s1.get("error")
                s1_text = s1["raw_text"]
                s1_usage = s1.get("usage") or {}
            except Exception as e:
                s1_error = f"{type(e).__name__}: {e}"
                s1_text = ""
                s1_usage = {}
            total_in_s1 += s1_usage.get("input_tokens") or 0
            total_out_s1 += s1_usage.get("output_tokens") or 0
            if s1_error:
                errors.append(f"verse {verse_no} stage1: {s1_error}")

            stage1_analyses.append({
                "verse_no": verse_no, "verse_text": verse_line,
                "analysis": s1_text, "usage": s1_usage, "error": s1_error,
            })

            # ---- Stage 2: extraction into strict schema on GPT-5.4-mini ----
            if s1_text:
                s2_user = build_stage2_user_message(verse_no, verse_line, s1_text)
                try:
                    s2 = call_openai(STAGE2_SYSTEM_MESSAGE, s2_user, 0.0)
                    s2_error = None
                    s2_text = s2["raw_text"]
                    s2_usage = s2.get("usage") or {}
                except Exception as e:
                    s2_error = f"{type(e).__name__}: {e}"
                    s2_text = ""
                    s2_usage = {}
            else:
                # stage 1 produced nothing (refusal/error) - stage 2 has no
                # input; emit an explicit exists=false line so the verse
                # stays present in the JSONL (excluded from scoring only via
                # its own missing content, not via a whole-run discard).
                s2_error = "skipped: empty stage1 output"
                s2_text = ""
                s2_usage = {}

            total_in_s2 += s2_usage.get("input_tokens") or 0
            total_out_s2 += s2_usage.get("output_tokens") or 0
            if s2_error:
                errors.append(f"verse {verse_no} stage2: {s2_error}")

            if s2_text:
                lines.append(_normalize_json_line(s2_text))
            else:
                lines.append(json.dumps({"no": verse_no}, ensure_ascii=False))

            print(f"  verse {verse_no}/{len(verses)}: s1 in={s1_usage.get('input_tokens')} out={s1_usage.get('output_tokens')} "
                  f"| s2 in={s2_usage.get('input_tokens')} out={s2_usage.get('output_tokens')}", flush=True)

        finished = datetime.now(timezone.utc).isoformat()
        out_stem = f"{provider}_run{run_idx}"
        (raw_dir / f"{out_stem}.txt").write_text("\n".join(lines), encoding="utf-8")
        (out_dir / f"stage1_analysis_run{run_idx}.json").write_text(
            json.dumps(stage1_analyses, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        record = {
            "poem_key": poem_key,
            "provider": provider,
            "display_name": "Config C (Fable 5 stage1 + GPT-5.4-mini stage2)",
            "model_id": "claude-fable-5+gpt-5.4-mini",
            "run_index": run_idx,
            "effort": effort,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "usage": {
                "stage1_input_tokens": total_in_s1, "stage1_output_tokens": total_out_s1,
                "stage2_input_tokens": total_in_s2, "stage2_output_tokens": total_out_s2,
                "input_tokens": total_in_s1 + total_in_s2, "output_tokens": total_out_s1 + total_out_s2,
            },
            # error stays None for partial per-verse failures - see
            # run_per_verse.py's docstring / PROJECT_STATE.md §6.8 for why.
            "error": None,
            "verse_errors": errors,
            "raw_text_file": f"raw/{out_stem}.txt",
            "stage1_analysis_file": f"stage1_analysis_run{run_idx}.json",
            "n_calls": len(verses) * 2,
        }
        manifest = [r for r in manifest if not (r["provider"] == provider and r["run_index"] == run_idx)]
        manifest.append(record)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> stage1 in={total_in_s1} out={total_out_s1} | stage2 in={total_in_s2} out={total_out_s2} | errors={len(errors)}", flush=True)

    print(f"Done -> {out_dir}")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--poem", default="Imru2")
    parser.add_argument("--runs", type=int, default=P1_N_RUNS)
    parser.add_argument("--effort", default="medium")
    args = parser.parse_args()
    run_config_c(poem_key=args.poem, n_runs=args.runs, effort=args.effort)


if __name__ == "__main__":
    main()
