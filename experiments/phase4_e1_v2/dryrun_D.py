"""Step 2 for Set D (NO API calls): cost estimate for running set D (and
optionally D2) using the REAL average cost/call per provider computed from the
already-completed E1 v2 manifest (results/phase4_e1_v2/run_manifest.json,
3,924 real calls, 0 errors) -- not a tiktoken estimate, since real logged
usage already exists for this exact harness/pool/model triple.

Set D (and D2) run on the same 25-poem pool (config/eval_pool_25.json, 327
verse-units) and the same 3 providers as Z/A/B/C, so "327 calls per model"
is exact, not approximate -- only the per-call cost is an average (real
per-set averages differ slightly by prompt length, but D/D2's fewshot-example
token overhead is the same order as A/B/C's, so the overall Z/A/B/C average
is the right real-data anchor, flagged as such below).

Does not touch run_manifest.json, does not call any provider API.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from runner import spend_so_far, call_cost  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))


def real_avg_cost_per_call() -> dict:
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    spend = spend_so_far(manifest)
    counts = {"anthropic": 0, "openai": 0, "google": 0}
    for r in manifest:
        if r.get("error") is None:
            counts[r["provider"]] += 1
    return {p: spend[p] / counts[p] for p in counts}, counts, spend


def main():
    avg_cost, counts, spend = real_avg_cost_per_call()
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    n_verses = sum(p["verse_count"] for p in pool)

    print("=" * 78)
    print("REAL per-call averages, from results/phase4_e1_v2/run_manifest.json "
          f"({sum(counts.values())} calls, sets Z/A/B/C, 0 errors)")
    print("=" * 78)
    for p in ("anthropic", "openai", "google"):
        print(f"  {p:10s}: {counts[p]} calls, total=${spend[p]:.4f}, avg/call=${avg_cost[p]:.6f}")
    print(f"  TOTAL (already spent, Z/A/B/C): ${spend['_total']:.4f}")

    print(f"\n25-poem pool (config/eval_pool_25.json): {len(pool)} poems, {n_verses} verse-units "
          "-- same pool Set D/D2 will use.")

    def project(n_sets: int) -> dict:
        calls_per_model = n_verses * n_sets
        cost = {p: avg_cost[p] * calls_per_model for p in avg_cost}
        return calls_per_model, cost

    print("\n" + "=" * 78)
    print("OPTION 1: Set D only (3 models x 327 verse-units x 1 set)")
    print("=" * 78)
    calls, cost = project(1)
    for p in ("anthropic", "openai", "google"):
        print(f"  {p:10s}: {calls} calls  -> ${cost[p]:.4f}")
    print(f"  TOTAL for Set D: ${sum(cost.values()):.4f}")
    print(f"  New grand total (Z/A/B/C + D): ${spend['_total'] + sum(cost.values()):.4f}")

    print("\n" + "=" * 78)
    print("OPTION 2: Set D + Set D2 (3 models x 327 verse-units x 2 sets)")
    print("=" * 78)
    calls2, cost2 = project(2)
    for p in ("anthropic", "openai", "google"):
        print(f"  {p:10s}: {calls2} calls  -> ${cost2[p]:.4f}")
    print(f"  TOTAL for D+D2: ${sum(cost2.values()):.4f}")
    print(f"  New grand total (Z/A/B/C + D + D2): ${spend['_total'] + sum(cost2.values()):.4f}")

    print("\n" + "=" * 78)
    print("STOP -- no API call has been made. Awaiting explicit \"go\" + a hard cap "
          "(--max-additional-usd on runner.py) before running --confirm --sets D [D2].")
    print("=" * 78)


if __name__ == "__main__":
    main()
