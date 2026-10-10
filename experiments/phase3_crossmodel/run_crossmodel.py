"""Runs the existing Phase 3 sub-element check (identical prompts, identical
570 ground-truth rows across 25 subtypes, identical N_RUNS=2/temperature=0.0)
on additional models already used elsewhere in this project - NOT Gemini
(already done in experiments/phase3_subelements/), NOT Fable 5 (excluded for
cost, see results/phase3_crossmodel/cost_estimate.md).

Deliberately thin: every piece of logic (verse lookup, response parsing,
message building) is imported from experiments/phase3_subelements/ unchanged
- this script only swaps which model/caller is used and where output lands,
per CLAUDE.md's "reuse Phase 1 modules, only add what's new" convention
(applied one level down: reuse Phase 3's modules for a Phase-3-shaped task).

Writes results/phase3_crossmodel/raw/<slug>_all.jsonl per subtype per model
(one "_all" file per (model, subtype), same record shape run_subtype_check.py
uses, so score_crossmodel.py's loader works unchanged on either model's data).

Usage:
    python run_crossmodel.py --dry-run                       # verify counts, no API calls
    python run_crossmodel.py --models anthropic               # one model
    python run_crossmodel.py --models anthropic openai         # both (default)
    python run_crossmodel.py --models anthropic --subtypes "طباق إيجاب"
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crossmodel_config import (  # noqa: E402
    ROOT, PILOT_DIR, PHASE3_DIR, RAW_DIR, MODELS, SUBTYPE_DEFS,
    N_RUNS, TEMPERATURE, CROSSMODEL_KEYS,
)

sys.path.insert(0, str(PHASE3_DIR))
from run_subtype_check import (  # noqa: E402  (Phase 3, reused unchanged)
    load_subtype_rows, parse_verse_nos, get_verse_block, slugify,
)
from subtype_prompts import build_messages  # noqa: E402

sys.path.insert(0, str(PILOT_DIR))
from providers import CALLERS  # noqa: E402  (Phase 1, reused unchanged - no cost-tracking bug for anthropic/openai)

load_dotenv(ROOT / ".env")

FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _parse_response(raw_text: str) -> dict:
    cleaned = FENCE_RE.sub("", raw_text.strip()).strip()
    try:
        obj = json.loads(cleaned)
        return {
            "exists": obj.get("exists"), "appearance": obj.get("appearance"),
            "reasoning": obj.get("reasoning"), "parse_error": False,
        }
    except json.JSONDecodeError:
        return {"exists": None, "appearance": None, "reasoning": None, "parse_error": True, "raw": cleaned[:300]}


def _do_call(caller, subtype_key, row, verse_text, run_idx):
    system, user = build_messages(subtype_key, verse_text)
    result = caller(system, user, TEMPERATURE)
    parsed = _parse_response(result["raw_text"])
    record = {
        "subtype": subtype_key, "run_idx": run_idx, **row,
        "verse_text": verse_text, **parsed, "model_id": result["model_id"],
    }
    return record, result["usage"].get("input_tokens") or 0, result["usage"].get("output_tokens") or 0


def run_for_model(model_key: str, subtypes: list, dry_run: bool, workers: int, max_cost: float = None, chunk_size: int = 50):
    model_spec = MODELS[model_key]
    caller = CALLERS[model_key]
    out_dir = RAW_DIR / model_key
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = []  # (subtype_key, row, verse_text, run_idx)
    per_subtype_n = {}
    for subtype_key in subtypes:
        try:
            rows = load_subtype_rows(subtype_key, "all")
        except FileNotFoundError:
            print(f"  ! no subtype file for {subtype_key!r}, skipping")
            continue
        if not rows:
            print(f"  - {subtype_key}: 0 rows, skipping")
            continue
        resolved = []
        for row in rows:
            try:
                verse_nos = parse_verse_nos(row["verse_no"])
                verse_text = get_verse_block(row["poem_key"], verse_nos)
            except Exception as e:
                print(f"  ! verse lookup failed for {subtype_key} row #{row['row_id']}: {e}")
                continue
            resolved.append((row, verse_text))
        per_subtype_n[subtype_key] = len(resolved)
        print(f"=== {subtype_key}: {len(resolved)} rows ===")
        if dry_run:
            continue
        for row, verse_text in resolved:
            for run_idx in range(N_RUNS):
                tasks.append((subtype_key, row, verse_text, run_idx))

    if dry_run:
        total_planned = sum(per_subtype_n.values()) * N_RUNS
        print(f"\n[{model_key}] {sum(per_subtype_n.values())} rows -> {total_planned} calls planned (N_RUNS={N_RUNS})")
        return

    print(f"\n[{model_key}] dispatching {len(tasks)} calls across {workers} workers, "
          f"in chunks of {chunk_size}" + (f", hard cap ${max_cost:.2f}" if max_cost else "") + "...", flush=True)

    price_in = MODELS[model_key]["price_in"] / 1_000_000
    price_out = MODELS[model_key]["price_out"] / 1_000_000

    total_in_tok = total_out_tok = 0
    n_done = n_errors = 0
    records_by_subtype = {k: [] for k in per_subtype_n}
    bar = tqdm(total=len(tasks), desc=f"crossmodel {model_key}", unit="call")
    aborted_for_cost = False

    for chunk_start in range(0, len(tasks), chunk_size):
        chunk = tasks[chunk_start:chunk_start + chunk_size]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_do_call, caller, subtype_key, row, verse_text, run_idx): subtype_key
                for subtype_key, row, verse_text, run_idx in chunk
            }
            for fut in as_completed(futures):
                subtype_key = futures[fut]
                try:
                    record, in_tok, out_tok = fut.result()
                except Exception as e:
                    n_errors += 1
                    print(f"  ! call failed for {subtype_key}: {e}", flush=True)
                    bar.update(1)
                    continue
                records_by_subtype[subtype_key].append(record)
                total_in_tok += in_tok
                total_out_tok += out_tok
                n_done += 1
                bar.update(1)

        running_cost = total_in_tok * price_in + total_out_tok * price_out
        if max_cost is not None and running_cost >= max_cost:
            bar.close()
            print(f"\n[{model_key}] ABORTING: running cost ${running_cost:.4f} reached cap ${max_cost:.2f} "
                  f"after {n_done + n_errors}/{len(tasks)} calls. Writing partial results.", flush=True)
            aborted_for_cost = True
            break
    else:
        bar.close()

    summary_rows = []
    for subtype_key, records in records_by_subtype.items():
        if not records:
            continue
        out_path = out_dir / f"{slugify(subtype_key)}_all.jsonl"
        n_yes = [0] * N_RUNS
        with open(out_path, "w", encoding="utf-8") as f:
            for rec in sorted(records, key=lambda r: (r["row_id"], r["run_idx"])):
                if rec.get("exists") is True:
                    n_yes[rec["run_idx"]] += 1
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n_rows = per_subtype_n[subtype_key]
        summary_rows.append({"subtype": subtype_key, "n_rows": n_rows,
                              **{f"n_yes_run{i+1}": n_yes[i] for i in range(N_RUNS)}})
        print(f"  {subtype_key}: {[f'run{i+1}={n_yes[i]}/{n_rows}' for i in range(N_RUNS)]}")

    price_in = model_spec["price_in"] / 1_000_000
    price_out = model_spec["price_out"] / 1_000_000
    cost = total_in_tok * price_in + total_out_tok * price_out

    print(f"\n[{model_key}] total API calls: {n_done} ok, {n_errors} failed")
    print(f"[{model_key}] total tokens: in={total_in_tok} out={total_out_tok}")
    print(f"[{model_key}] estimated cost ({model_spec['display']}): ${cost:.4f}")

    summary_path = RAW_DIR.parent / f"summary_{model_key}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_key": model_key, "model": model_spec["display"],
            "total_calls": n_done, "total_errors": n_errors,
            "total_in_tok": total_in_tok, "total_out_tok": total_out_tok,
            "cost_usd": cost, "aborted_for_cost_cap": aborted_for_cost,
            "planned_calls": len(tasks), "subtypes": summary_rows,
        }, f, ensure_ascii=False, indent=1)
    print(f"[{model_key}] summary written to {summary_path}")
    return {"n_done": n_done, "n_errors": n_errors, "cost": cost}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=CROSSMODEL_KEYS, choices=list(MODELS.keys()))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--subtypes", nargs="*", default=None)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-cost", type=float, default=None, help="hard USD cap; stops dispatching new chunks once reached")
    ap.add_argument("--chunk-size", type=int, default=50)
    args = ap.parse_args()

    subtypes = args.subtypes or list(SUBTYPE_DEFS.keys())
    totals = {}
    for model_key in args.models:
        totals[model_key] = run_for_model(model_key, subtypes, args.dry_run, args.workers,
                                           max_cost=args.max_cost, chunk_size=args.chunk_size)

    if not args.dry_run:
        grand_cost = sum(t["cost"] for t in totals.values() if t)
        print(f"\n=== GRAND TOTAL across {list(totals.keys())}: ${grand_cost:.4f} ===")


if __name__ == "__main__":
    main()
