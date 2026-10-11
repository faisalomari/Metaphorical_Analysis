"""E1 v2 analysis driver -- NO API calls. Reads run_manifest.json + raw/*.txt
only. Computes, per model x set x criterion (verse-level-exists, span-level-
strict, span-level-token-overlap), overall + abu_nuwas/other TP/FP/FN/P/R/F1,
pairwise bootstrap 95% CIs over poems across all 6 set-pairs, and per-poem
diff-sign counts. Writes the full numeric report to
results/phase4_e1_v2/analysis_report.json and prints the key summary tables
used to write docs/phase4/E1_V2_RESULTS.md.

criterion="verse" is a supplementary diagnostic only (CLAUDE.md rule 4 warns
plain verse-level exists/not-exists alone produces artifacts) -- strict and
token-overlap remain the primary span-level metrics, reported alongside it,
never replaced by it.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import before scoring_v2, which
# inserts experiments/phase4_e1 onto sys.path[0] -- that dir has its own
# runner.py with no spend_so_far, so importing after it would shadow this one)
from scoring_v2 import analyze  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

MODELS_ORDER = ["anthropic", "openai", "google"]
CRITERIA_ORDER = ["verse", "strict", "token"]
SET_NAMES = ["Z", "A", "B", "C"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini", "google": "Gemini (served: gemini-3.6-flash)"}


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    n_total = len(manifest)
    n_err = sum(1 for r in manifest if r.get("error"))
    spend = spend_so_far(manifest)

    report = analyze(out_dir=RESULTS_DIR, pool=pool, criteria=tuple(CRITERIA_ORDER), models=tuple(MODELS_ORDER))

    (RESULTS_DIR / "analysis_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Manifest: {n_total} records, {n_err} errors.")
    print(f"Actual spend: anthropic=${spend['anthropic']:.4f} openai=${spend['openai']:.4f} "
          f"google=${spend['google']:.4f} TOTAL=${spend['_total']:.4f}")
    print(f"Pool: {len(pool)} poems, {sum(p['verse_count'] for p in pool)} verses "
          f"({sum(1 for p in pool if p['tag']=='abu_nuwas')} abu_nuwas, "
          f"{sum(1 for p in pool if p['tag']=='other')} other)")

    for provider in MODELS_ORDER:
        print(f"\n{'=' * 78}\n{DISPLAY[provider]} ({provider})\n{'=' * 78}")
        for criterion in CRITERIA_ORDER:
            print(f"\n-- criterion: {criterion} --")
            per_set = report[provider][criterion]["per_set"]
            for s in SET_NAMES:
                for split in ("overall", "abu_nuwas", "other"):
                    c = per_set[s][split]
                    print(f"  set {s} / {split:9s}: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d}  "
                          f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
            print("  pairwise bootstrap 95% CI (F1_i - F1_j), per-poem diff signs:")
            for pair, ci in report[provider][criterion]["pairwise_bootstrap_ci"].items():
                diffs = report[provider][criterion]["per_poem_diff_signs"][pair]
                lo, hi = ci["ci_95"]
                sig = "SIG" if (lo > 0 or hi < 0) else "ns"
                print(f"    {pair}: point={ci['point']:+.4f} CI95=[{lo:+.4f}, {hi:+.4f}] ({sig})  "
                      f"per-poem: {diffs['a_greater']}>{diffs['b_greater']} tied={diffs['tied']}")

    print(f"\n{'=' * 78}\nDone. Full report written to {RESULTS_DIR / 'analysis_report.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
