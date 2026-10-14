"""Same-poet (abu_nuwas vs other) gain-over-Z analysis, VERSE criterion -- per
the user's 2026-10-14 decision that verse is now the PRIMARY metric. NO API
calls. Reuses samepoet_analysis.py's bootstrap_gain_ci/bootstrap_diffofgains_ci
unchanged; the only difference is the per-poem counts come from
scoring_v2.score_set(criterion="verse") instead of the strict/token-only
analysis_report.json (which has no verse data).

CLAUDE.md rule 4 still flags plain verse-level exists/not-exists as a
supplementary diagnostic -- noted in the written-up doc, not here.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E1V2_DIR = ROOT / "experiments" / "phase4_e1_v2"
sys.path.insert(0, str(E1V2_DIR))
from e1v2_config import EVAL_POOL_25_PATH, RESULTS_DIR  # noqa: E402
from scoring_v2 import score_set  # noqa: E402
from samepoet_analysis import (  # noqa: E402
    GROUPS, bootstrap_gain_ci, bootstrap_diffofgains_ci,
)

MODELS = ["anthropic", "openai", "google"]
POOL = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]


def main():
    per_set_per_model = {m: {s: score_set(RESULTS_DIR, s, m, POOL, "verse") for s in ["Z", "A", "B", "C"]}
                          for m in MODELS}

    out = {}
    for model in MODELS:
        out[model] = {}
        per_poem_z = per_set_per_model[model]["Z"]["per_poem"]
        for s in ["A", "B", "C"]:
            per_poem_s = per_set_per_model[model][s]["per_poem"]
            row = {}
            for g, ids in GROUPS.items():
                point, lo, hi = bootstrap_gain_ci(per_poem_s, per_poem_z, ids)
                row[g] = {"point": point, "ci_95": [lo, hi]}
            diff_point, diff_lo, diff_hi = bootstrap_diffofgains_ci(
                per_poem_s, per_poem_z, GROUPS["abu_nuwas"], GROUPS["other"])
            row["diff_abu_minus_other"] = {"point": diff_point, "ci_95": [diff_lo, diff_hi]}
            out[model][s] = row

    (RESULTS_DIR / "samepoet_verse.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote results/phase4_e1_v2/samepoet_verse.json\n")

    print("=== F1 at Z per group (verse) ===")
    for model in MODELS:
        z = per_set_per_model[model]["Z"]
        print(f"  {model}: abu_nuwas F1={z['abu_nuwas']['f1']:.3f} "
              f"(tp={z['abu_nuwas']['tp']},fp={z['abu_nuwas']['fp']},fn={z['abu_nuwas']['fn']})  "
              f"other F1={z['other']['f1']:.3f} "
              f"(tp={z['other']['tp']},fp={z['other']['fp']},fn={z['other']['fn']})")

    print("\n=== Gain over Z, verse criterion (point [95% CI]) ===")
    for model in MODELS:
        for s in ["A", "B", "C"]:
            row = out[model][s]
            an, ot, df = row["abu_nuwas"], row["other"], row["diff_abu_minus_other"]
            sig = "SIG" if (df["ci_95"][0] > 0 or df["ci_95"][1] < 0) else "ns"
            print(f"  {model}/{s}: abu_nuwas={an['point']:+.4f} [{an['ci_95'][0]:+.4f},{an['ci_95'][1]:+.4f}]  "
                  f"other={ot['point']:+.4f} [{ot['ci_95'][0]:+.4f},{ot['ci_95'][1]:+.4f}]  "
                  f"diff={df['point']:+.4f} [{df['ci_95'][0]:+.4f},{df['ci_95'][1]:+.4f}] ({sig})")


if __name__ == "__main__":
    main()
