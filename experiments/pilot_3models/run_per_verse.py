"""Runner for the per-verse granularity experiment (PROJECT_STATE.md §3g).

Mode A: 1 call per verse, v4_combined content, all 4 elements per call.
Mode B: 1 call per verse per element, reusing §3f's decomposed prompts.

Each (provider, run_index) cell aggregates its N_VERSES individual API calls
into ONE manifest record + ONE raw JSONL-style text file (one compact JSON
object per line, in verse order) - matching run_pilot.run()'s output format
exactly, so the existing loaders (analyze.load_all_runs /
load_all_runs_single_element) and score_span_level() work completely
unchanged. Per-call usage/errors are additionally logged to
per_call_log.json in the same directory for cost auditing, but that file is
never read by the scoring pipeline.

Usage:
    python run_per_verse.py --mode a
    python run_per_verse.py --mode b
    python run_per_verse.py --mode b --elements Kenning Trope
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import MODELS, N_RUNS, TEMPERATURE, RESULTS_DIR, ROOT, ELEMENT_ORDER
from prompt_variants import build_system_message_variant
from decompose_prompts import build_system_message_decomposed
from per_verse_prompts import get_verses, build_user_message_mode_a, build_user_message_mode_b
from providers import CALLERS

load_dotenv(ROOT / ".env")

PER_VERSE_DIR = RESULTS_DIR / "per_verse"
FENCE_RE = re.compile(r"^```(?:json|jsonl)?\s*|\s*```$", re.MULTILINE)


def _normalize_json_line(raw_text: str) -> str:
    """Collapse one verse's response into a single JSONL-safe line: compact
    valid JSON, or (if malformed) collapse internal newlines so the parse
    failure stays confined to that one line instead of corrupting the
    concatenated file's line-based parsing for neighboring verses."""
    cleaned = FENCE_RE.sub("", raw_text.strip()).strip()
    try:
        obj = json.loads(cleaned)
        return json.dumps(obj, ensure_ascii=False)
    except json.JSONDecodeError:
        return " ".join(cleaned.split())


def _run_one_cell(poem_key, system_message, build_user_message_fn, out_dir, n_runs=N_RUNS, temperature=TEMPERATURE, providers=None):
    """providers, if given, restricts this call to a subset of MODELS keys -
    e.g. a retry of just the provider whose earlier attempt failed, without
    re-spending on providers that already succeeded. Retrying a
    (provider, run_index) cell REPLACES its existing manifest record instead
    of appending a duplicate, so a retry directory never ends up with two
    entries for the same cell (one dead, one live)."""
    verses = get_verses(poem_key)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = out_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    call_log_path = out_dir / "per_call_log.json"
    call_log = json.loads(call_log_path.read_text(encoding="utf-8")) if call_log_path.exists() else []

    active_models = {p: MODELS[p] for p in providers} if providers else MODELS
    for provider, spec in active_models.items():
        caller = CALLERS[provider]
        for run_idx in range(1, n_runs + 1):
            print(f"[{poem_key}][{provider}] run {run_idx}/{n_runs} per-verse ({len(verses)} calls) ...", flush=True)
            started = datetime.now(timezone.utc).isoformat()
            # drop any earlier call-log entries for this exact (provider, run_idx) cell
            # so a retry doesn't leave stale/duplicate per-verse entries alongside the fresh ones
            call_log = [c for c in call_log if not (c["provider"] == provider and c["run_index"] == run_idx)]
            lines = []
            total_in = total_out = 0
            errors = []
            for verse_no, verse_line in enumerate(verses, start=1):
                user_message = build_user_message_fn(verse_line)
                try:
                    result = caller(system_message, user_message, temperature)
                    line = _normalize_json_line(result["raw_text"])
                    usage = result["usage"] or {}
                    err = None
                except Exception as e:
                    line = ""
                    usage = {}
                    err = f"{type(e).__name__}: {e}"
                lines.append(line)
                total_in += usage.get("input_tokens") or 0
                total_out += usage.get("output_tokens") or 0
                if err:
                    errors.append(f"verse {verse_no}: {err}")
                call_log.append({
                    "poem_key": poem_key, "provider": provider, "run_index": run_idx,
                    "verse_no": verse_no, "usage": usage, "error": err,
                })
            finished = datetime.now(timezone.utc).isoformat()
            out_stem = f"{provider}_run{run_idx}"
            (raw_dir / f"{out_stem}.txt").write_text("\n".join(lines), encoding="utf-8")

            record = {
                "poem_key": poem_key,
                "provider": provider,
                "display_name": spec["display"],
                "model_id": spec["model_id"],
                "run_index": run_idx,
                "temperature": temperature,
                "started_at_utc": started,
                "finished_at_utc": finished,
                "usage": {"input_tokens": total_in, "output_tokens": total_out},
                # NOTE: "error" must stay None for a partially-successful cell -
                # analyze.py's load_all_runs()/load_all_runs_single_element()
                # treat any truthy "error" as "discard this entire run's data"
                # (correct for the original one-call-per-run design, where a
                # truthy error means raw_text is empty/garbage). Here raw_text
                # always contains genuine JSON lines for whichever verses
                # succeeded (failed verses are just blank lines, transparently
                # excluded per-verse by parse_response), so a per-verse failure
                # must never zero out the other N-1 verses' real data.
                "error": None,
                "verse_errors": errors,
                "raw_text_file": f"raw/{out_stem}.txt",
                "n_calls": len(verses),
            }
            # retrying an already-attempted (provider, run_idx) cell replaces its
            # manifest record rather than appending a duplicate
            manifest = [r for r in manifest if not (r["provider"] == provider and r["run_index"] == run_idx)]
            manifest.append(record)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            call_log_path.write_text(json.dumps(call_log, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  -> in={total_in} out={total_out} errors={len(errors)}", flush=True)

    print(f"Done -> {out_dir}")
    return manifest


def run_mode_a(poem_key="Imru2", n_runs=N_RUNS, providers=None):
    sm = build_system_message_variant("v4_combined")
    out_dir = PER_VERSE_DIR / "mode_a" / poem_key
    return _run_one_cell(poem_key, sm, build_user_message_mode_a, out_dir, n_runs=n_runs, providers=providers)


def run_mode_b(poem_key="Imru2", n_runs=N_RUNS, elements=None, providers=None):
    elements = elements or ELEMENT_ORDER
    results = {}
    for element in elements:
        sm = build_system_message_decomposed(element)
        out_dir = PER_VERSE_DIR / f"mode_b_{element}" / poem_key
        results[element] = _run_one_cell(
            poem_key, sm, lambda v, element=element: build_user_message_mode_b(element, v),
            out_dir, n_runs=n_runs, providers=providers,
        )
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["a", "b"], required=True)
    parser.add_argument("--poem", default="Imru2")
    parser.add_argument("--runs", type=int, default=N_RUNS)
    parser.add_argument("--elements", nargs="*", default=None, choices=ELEMENT_ORDER)
    parser.add_argument("--providers", nargs="*", default=None, choices=list(MODELS.keys()))
    args = parser.parse_args()
    if args.mode == "a":
        run_mode_a(poem_key=args.poem, n_runs=args.runs, providers=args.providers)
    else:
        run_mode_b(poem_key=args.poem, n_runs=args.runs, elements=args.elements, providers=args.providers)


if __name__ == "__main__":
    main()
