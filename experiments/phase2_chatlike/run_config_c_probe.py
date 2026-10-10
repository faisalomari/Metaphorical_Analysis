"""Targeted recall probe (NOT a full-poem evaluation) - Nabigha, Config C
recipe (Stage 1 Fable 5 free-form analysis + Stage 2 GPT-5.4-mini
extraction, unchanged from run_config_c.py), run on a SPECIFIC verse list
only: the 9 verses containing a مجاز مرسل ground-truth instance, plus 2
contrast verses (other Trope subtypes). 2 runs each.

This is deliberately NOT scored through span_scoring.score_span_level -
that assumes every verse 1..n_verses was analyzed and would silently
compute misleading FN/precision numbers for the ~39 Nabigha verses never
sent to the model. Known-positive-verse recall only; no precision/F1 claim
is made anywhere in this script's output or the report built from it.
"""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))

from phase2_config import ROOT  # noqa: E402
from config import POEMS  # noqa: E402  (pilot_3models)
from ground_truth import load_ground_truth_spans  # noqa: E402
from prompt_config_c import (  # noqa: E402
    STAGE1_SYSTEM_MESSAGE, build_stage1_user_message,
    STAGE2_SYSTEM_MESSAGE, build_stage2_user_message,
)
from providers_v2 import call_fable5  # noqa: E402
from providers import call_openai  # noqa: E402
from span_matching import strict_overlap, token_match  # noqa: E402

load_dotenv(ROOT / ".env")

RESULTS_DIR = ROOT / "results" / "phase2_chatlike" / "config_c_probe" / "Nabigha"

MURSAL_VERSES = [4, 7, 8, 10, 14, 16, 30, 33, 47]
CONTRAST_VERSES = [2, 5]
ALL_VERSES = sorted(set(MURSAL_VERSES) | set(CONTRAST_VERSES))


def get_verse_line(poem_key: str, verse_no: int) -> str:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    lines = [ln for ln in poem_text.split("\n") if ln.strip()]
    return lines[verse_no - 1]


def run_probe(poem_key: str = "Nabigha", n_runs: int = 2, effort: str = "medium"):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = {}  # verse_no -> [ {run_index, stage1_analysis, stage2_extracted, usage...}, ... ]

    for verse_no in ALL_VERSES:
        verse_line = get_verse_line(poem_key, verse_no)
        results[verse_no] = []
        for run_idx in range(1, n_runs + 1):
            print(f"[Probe][{poem_key}] verse {verse_no} run {run_idx}/{n_runs} ...", flush=True)
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

            if s1_text:
                s2_user = build_stage2_user_message(verse_no, verse_line, s1_text)
                try:
                    s2 = call_openai(STAGE2_SYSTEM_MESSAGE, s2_user, 0.0)
                    s2_text = s2["raw_text"]
                    s2_usage = s2.get("usage") or {}
                    s2_error = None
                except Exception as e:
                    s2_text = ""
                    s2_usage = {}
                    s2_error = f"{type(e).__name__}: {e}"
            else:
                s2_text, s2_usage, s2_error = "", {}, "skipped: empty stage1 output"

            try:
                cleaned = s2_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.strip("`").strip()
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:].strip()
                extracted = json.loads(cleaned) if cleaned else None
            except json.JSONDecodeError:
                extracted = None

            print(f"  s1 in={s1_usage.get('input_tokens')} out={s1_usage.get('output_tokens')} "
                  f"| s2 in={s2_usage.get('input_tokens')} out={s2_usage.get('output_tokens')} "
                  f"| s1_err={s1_error} s2_err={s2_error}", flush=True)

            results[verse_no].append({
                "run_index": run_idx, "verse_text": verse_line,
                "stage1_analysis": s1_text, "stage1_usage": s1_usage, "stage1_error": s1_error,
                "stage2_raw": s2_text, "stage2_extracted": extracted, "stage2_usage": s2_usage, "stage2_error": s2_error,
            })

    out_path = RESULTS_DIR / "probe_results.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone -> {out_path}")
    return results


if __name__ == "__main__":
    run_probe()
