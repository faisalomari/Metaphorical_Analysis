"""Few-shot (3-shot) follow-up to run_subtype_check.py, for the 13 subtypes
with enough ground-truth volume (n>=10) to hold out 2 examples as extra
few-shot demonstrations and still have a meaningful test set left (n-2>=8).
The other 12 subtypes are too small to spare examples without gutting their
test set - see the conversation for the full n-per-subtype table - and are
left as one-shot-only (already run, in raw/<subtype>_all.jsonl).

The 2 held-out examples per subtype are the FIRST 2 rows in that subtype's
ground-truth file order (deterministic, not cherry-picked for being "easy").
They are excluded from this run's test set. IMPORTANT for the one-shot vs
few-shot comparison: those same 2 rows must also be excluded when recomputing
one-shot's numbers for the comparison table (build_fewshot_comparison.py does
this) - otherwise the two conditions aren't tested on the same rows.

Usage:
    python run_fewshot_check.py --dry-run
    python run_fewshot_check.py --workers 10
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))

from phase3_config import MODELS, MODEL_KEY, N_RUNS, TEMPERATURE, RESULTS_DIR, ROOT  # noqa: E402
from run_subtype_check import (  # noqa: E402
    load_subtype_rows, get_verse_block, parse_verse_nos, slugify, _parse_response,
)
from fewshot_prompts import build_messages_fewshot  # noqa: E402
from providers_fixed import call_google_fixed  # noqa: E402

load_dotenv(ROOT / ".env")

# n>=10 threshold, see module docstring
ELIGIBLE_SUBTYPES = [
    "كناية فنية", "تشبيه قصير", "استعارة قديمة", "مجاز مرسل", "كناية عن فعل",
    "استعارة تمثيلية", "تشبيه مطول", "كناية لغوية", "طباق إيجاب", "مجاز عقلي",
    "كناية عن موصوف", "كناية عن صفة", "استعارة فعل",
]
N_HOLDOUT = 2


def resolve_row(row):
    verse_nos = parse_verse_nos(row["verse_no"])
    verse_text = get_verse_block(row["poem_key"], verse_nos)
    return {**row, "verse_text": verse_text}


def split_holdout_and_test(subtype_key: str):
    rows = load_subtype_rows(subtype_key, "all")
    resolved = [resolve_row(r) for r in rows]
    holdout, test = resolved[:N_HOLDOUT], resolved[N_HOLDOUT:]
    return holdout, test


def _do_call(caller, subtype_key, row, extra_examples, run_idx):
    system, user = build_messages_fewshot(subtype_key, row["verse_text"], extra_examples)
    result = caller(system, user, TEMPERATURE)
    parsed = _parse_response(result["raw_text"])
    record = {"subtype": subtype_key, "run_idx": run_idx, **row, **parsed, "model_id": result["model_id"]}
    return record, result["usage"].get("input_tokens") or 0, result["usage"].get("output_tokens") or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    model_spec = MODELS[MODEL_KEY]
    out_dir = RESULTS_DIR / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    per_subtype_n = {}
    holdouts_by_subtype = {}
    for subtype_key in ELIGIBLE_SUBTYPES:
        holdout, test = split_holdout_and_test(subtype_key)
        holdouts_by_subtype[subtype_key] = holdout
        per_subtype_n[subtype_key] = len(test)
        print(f"=== {subtype_key}: {len(test)} test rows (held out {len(holdout)} for few-shot) ===")
        if args.dry_run:
            print(f"  held-out verses: {[h['verse_no'] for h in holdout]}")
            continue
        for row in test:
            for run_idx in range(N_RUNS):
                tasks.append((subtype_key, row, run_idx))

    if args.dry_run:
        total_test = sum(per_subtype_n.values())
        print(f"\n{total_test} test rows total -> {total_test * N_RUNS} calls planned (N_RUNS={N_RUNS})")
        return

    print(f"\ndispatching {len(tasks)} calls across {args.workers} workers...", flush=True)

    caller = call_google_fixed
    total_in_tok = total_out_tok = 0
    n_done = n_errors = 0
    records_by_subtype = {k: [] for k in per_subtype_n}
    progress_step = max(1, len(tasks) // 50)
    bar = tqdm(total=len(tasks), desc="phase3 fewshot", unit="call")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(_do_call, caller, subtype_key, row, holdouts_by_subtype[subtype_key], run_idx): subtype_key
            for subtype_key, row, run_idx in tasks
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
            if n_done % progress_step == 0 or n_done == len(tasks):
                print(f"PROGRESS {n_done + n_errors}/{len(tasks)} ({100*(n_done+n_errors)/len(tasks):.0f}%) - {n_errors} errors", flush=True)
    bar.close()

    summary_rows = []
    for subtype_key, records in records_by_subtype.items():
        if not records:
            continue
        out_path = out_dir / f"{slugify(subtype_key)}_fewshot.jsonl"
        n_yes = [0] * N_RUNS
        with open(out_path, "w", encoding="utf-8") as f:
            for rec in sorted(records, key=lambda r: (r["row_id"], r["run_idx"])):
                if rec.get("exists") is True:
                    n_yes[rec["run_idx"]] += 1
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        n_rows = per_subtype_n[subtype_key]
        summary_rows.append({"subtype": subtype_key, "n_rows": n_rows, **{f"n_yes_run{i+1}": n_yes[i] for i in range(N_RUNS)}})
        print(f"  {subtype_key}: {[f'run{i+1}={n_yes[i]}/{n_rows}' for i in range(N_RUNS)]}")

    price_in = model_spec["price_in"] / 1_000_000
    price_out = model_spec["price_out"] / 1_000_000
    cost = total_in_tok * price_in + total_out_tok * price_out

    print(f"\ntotal API calls: {n_done} ok, {n_errors} failed")
    print(f"total tokens: in={total_in_tok} out={total_out_tok}")
    print(f"estimated cost ({model_spec['display']}): ${cost:.4f}")

    summary_path = RESULTS_DIR / "summary_fewshot.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "model": model_spec["display"], "total_calls": n_done, "total_errors": n_errors,
            "total_in_tok": total_in_tok, "total_out_tok": total_out_tok, "cost_usd": cost,
            "subtypes": summary_rows,
            "holdout_examples": {k: [h["verse_no"] for h in v] for k, v in holdouts_by_subtype.items()},
        }, f, ensure_ascii=False, indent=1)
    print(f"summary written to {summary_path}")


if __name__ == "__main__":
    main()
