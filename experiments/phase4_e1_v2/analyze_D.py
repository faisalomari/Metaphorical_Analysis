"""Step 4 for Set D (NO API calls). Scores D and D2 next to the existing
Z/A/B/C, using scoring_v2.score_set (same strict/token-overlap span matcher,
same verse-level supplementary diagnostic) -- reused unchanged, not
reimplemented. Does not touch results/phase4_e1_v2/analysis_report.json
(that file stays Z/A/B/C-only, matching E1_V2_RESULTS.md); writes its own
results/phase4_e1_v2/analysis_report_D.json instead.

Computes, per model x criterion (verse/strict/token):
  - overall TP/FP/FN/P/R/F1 for Z, A, B, C, D, D2
  - bootstrap 95% CI (per-poem resampling) for D-vs-A, D-vs-B, D-vs-C, D-vs-Z,
    D2-vs-A, D2-vs-B, D2-vs-C, D2-vs-Z, and D-vs-D2
  - "gain over Z" = the D-vs-Z / D2-vs-Z point estimate + CI (same numbers,
    relabeled for direct readability)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import before scoring_v2, same
# shadowing reason as analyze_v2.py)
from scoring_v2 import score_set, bootstrap_ci_pairwise, per_poem_diff_signs  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

MODELS_ORDER = ["anthropic", "openai", "google"]
CRITERIA_ORDER = ["verse", "strict", "token"]
SETS = ["Z", "A", "B", "C", "D", "D2"]
BASELINES = ["A", "B", "C", "Z"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
           "google": "Gemini (served: gemini-3.6-flash)"}


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    n_total = len(manifest)
    n_err = sum(1 for r in manifest if r.get("error"))
    spend = spend_so_far(manifest)

    report = {}
    for provider in MODELS_ORDER:
        report[provider] = {}
        for criterion in CRITERIA_ORDER:
            per_set = {s: score_set(RESULTS_DIR, s, provider, pool, criterion) for s in SETS}
            pairwise = {}
            diffs = {}
            for probe in ["D", "D2"]:
                for base in BASELINES:
                    key = f"{probe}-{base}"
                    pairwise[key] = bootstrap_ci_pairwise(per_set[probe]["per_poem"], per_set[base]["per_poem"])
                    diffs[key] = per_poem_diff_signs(per_set[probe]["per_poem"], per_set[base]["per_poem"])
            pairwise["D-D2"] = bootstrap_ci_pairwise(per_set["D"]["per_poem"], per_set["D2"]["per_poem"])
            diffs["D-D2"] = per_poem_diff_signs(per_set["D"]["per_poem"], per_set["D2"]["per_poem"])
            report[provider][criterion] = {
                "per_set": per_set, "pairwise_bootstrap_ci": pairwise, "per_poem_diff_signs": diffs,
            }

    (RESULTS_DIR / "analysis_report_D.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Manifest: {n_total} records, {n_err} errors.")
    print(f"Actual cumulative spend (Z/A/B/C/D/D2): anthropic=${spend['anthropic']:.4f} "
          f"openai=${spend['openai']:.4f} google=${spend['google']:.4f} TOTAL=${spend['_total']:.4f}")

    for provider in MODELS_ORDER:
        print(f"\n{'=' * 78}\n{DISPLAY[provider]} ({provider})\n{'=' * 78}")
        for criterion in CRITERIA_ORDER:
            print(f"\n-- criterion: {criterion} --")
            per_set = report[provider][criterion]["per_set"]
            for s in SETS:
                c = per_set[s]["overall"]
                print(f"  set {s:3s} / overall: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d}  "
                      f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
            print("  bootstrap 95% CI (F1_probe - F1_baseline), per-poem diff signs:")
            for pair, ci in report[provider][criterion]["pairwise_bootstrap_ci"].items():
                diffs = report[provider][criterion]["per_poem_diff_signs"][pair]
                lo, hi = ci["ci_95"]
                sig = "SIG" if (lo > 0 or hi < 0) else "ns"
                print(f"    {pair}: point={ci['point']:+.4f} CI95=[{lo:+.4f}, {hi:+.4f}] ({sig})  "
                      f"per-poem: {diffs['a_greater']}>{diffs['b_greater']} tied={diffs['tied']}")

    print(f"\n{'=' * 78}\nDone. Full report written to {RESULTS_DIR / 'analysis_report_D.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
