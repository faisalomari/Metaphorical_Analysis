"""Verse-criterion analysis (NO API calls), per the user's 2026-10-14 methodological
decision: VERSE is now the PRIMARY metric for conclusions (strict/token stay secondary).
CLAUDE.md rule 4 still flags plain verse-level exists/not-exists as a supplementary
diagnostic prone to rewarding exists=true regardless of span correctness -- this script
and its callers note that explicitly; CLAUDE.md itself is not edited.

Reuses scoring_v2.score_set's existing criterion="verse" branch unchanged. Does not
touch results/phase4_e1_v2/analysis_report.json or analysis_report_D.json (those stay as
the strict/token-primary, Z/A/B/C(/D/D2) reports they already are); writes a new
analysis_report_verse.json instead.

Adds its own bootstrap-CI helper (bootstrap_pair) that -- unlike scoring_v2.
bootstrap_ci_pairwise, which only returns the F1 diff -- resamples poems once and reports
F1, precision, and recall diffs together from the SAME resample draw (same seed=0,
n_iter=2000, with-replacement-over-poems method as the existing code), so "report
precision and recall separately" doesn't require a second, differently-seeded bootstrap.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import-order note: see analyze_v2.py)
from scoring_v2 import score_set  # noqa: E402

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

MODELS_ORDER = ["anthropic", "openai", "google"]
SETS = ["Z", "A", "B", "C", "D", "D2"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
           "google": "Gemini (served: gemini-3.6-flash)"}

# Reference verse-level overall F1 for Z/A/B/C, as given by the user (from
# E1_V2_RESULTS.md's existing verse table) -- checked below, not assumed.
REFERENCE_ZABC_F1 = {
    "anthropic": {"Z": 0.377, "A": 0.576, "B": 0.547, "C": 0.416},
    "openai": {"Z": 0.549, "A": 0.541, "B": 0.513, "C": 0.437},
    "google": {"Z": 0.393, "A": 0.511, "B": 0.510, "C": 0.481},
}

PAIRS = [
    ("Z", "A"), ("Z", "B"), ("Z", "C"), ("Z", "D"), ("Z", "D2"),
    ("A", "B"), ("A", "C"), ("B", "C"),
    ("D", "C"), ("D", "A"), ("D", "B"),
    ("D2", "C"), ("D2", "B"),
]


def _totals(per_poem: dict, poem_ids=None) -> dict:
    ids = poem_ids if poem_ids is not None else per_poem.keys()
    tp = sum(per_poem[p]["tp"] for p in ids)
    fp = sum(per_poem[p]["fp"] for p in ids)
    fn = sum(per_poem[p]["fn"] for p in ids)
    return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}


def bootstrap_pair(per_poem_a: dict, per_poem_b: dict, n_iter: int = 2000, seed: int = 0) -> dict:
    poem_ids = sorted(set(per_poem_a) & set(per_poem_b))
    rng = random.Random(seed)
    d_f1, d_p, d_r = [], [], []
    for _ in range(n_iter):
        sample = [rng.choice(poem_ids) for _ in poem_ids]
        a = _totals(per_poem_a, sample)
        b = _totals(per_poem_b, sample)
        d_f1.append(a["f1"] - b["f1"])
        d_p.append(a["precision"] - b["precision"])
        d_r.append(a["recall"] - b["recall"])

    def ci95(diffs):
        diffs = sorted(diffs)
        n = len(diffs)
        return diffs[int(0.025 * n)], diffs[int(0.975 * n) - 1]

    tot_a, tot_b = _totals(per_poem_a), _totals(per_poem_b)
    out = {}
    for name, diffs, key in [("f1", d_f1, "f1"), ("precision", d_p, "precision"), ("recall", d_r, "recall")]:
        lo, hi = ci95(diffs)
        point = tot_a[key] - tot_b[key]
        out[name] = {"point": point, "ci_95": [lo, hi], "sig": bool(lo > 0 or hi < 0)}
    return out


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    spend = spend_so_far(manifest)

    report = {}
    for provider in MODELS_ORDER:
        per_set = {s: score_set(RESULTS_DIR, s, provider, pool, "verse") for s in SETS}
        pairwise = {f"{a}-{b}": bootstrap_pair(per_set[a]["per_poem"], per_set[b]["per_poem"])
                    for a, b in PAIRS}
        report[provider] = {"per_set": per_set, "pairwise_bootstrap_ci": pairwise}

    (RESULTS_DIR / "analysis_report_verse.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Manifest: {len(manifest)} records. Cumulative spend: ${spend['_total']:.4f}")
    print("\n" + "=" * 78)
    print("REFERENCE CHECK: verse-level overall F1 for Z/A/B/C vs. user-supplied numbers")
    print("=" * 78)
    all_match = True
    for provider in MODELS_ORDER:
        for s in ["Z", "A", "B", "C"]:
            computed = report[provider]["per_set"][s]["overall"]["f1"]
            ref = REFERENCE_ZABC_F1[provider][s]
            match = abs(computed - ref) < 0.0005
            all_match &= match
            flag = "OK" if match else "*** MISMATCH ***"
            print(f"  {provider:10s} set {s}: computed={computed:.3f} reference={ref:.3f}  {flag}")
    print(f"\nALL MATCH: {all_match}")

    for provider in MODELS_ORDER:
        print(f"\n{'=' * 78}\n{DISPLAY[provider]} ({provider}) -- criterion: verse\n{'=' * 78}")
        per_set = report[provider]["per_set"]
        for s in SETS:
            for split in ("overall", "abu_nuwas", "other"):
                c = per_set[s][split]
                print(f"  set {s:3s} / {split:9s}: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d}  "
                      f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
        print("  bootstrap 95% CI (overall, F1/precision/recall, probe - baseline):")
        for pair, metrics in report[provider]["pairwise_bootstrap_ci"].items():
            f1, p, r = metrics["f1"], metrics["precision"], metrics["recall"]
            print(f"    {pair}: "
                  f"F1={f1['point']:+.4f} CI95=[{f1['ci_95'][0]:+.4f},{f1['ci_95'][1]:+.4f}] "
                  f"({'SIG' if f1['sig'] else 'ns'})  "
                  f"P={p['point']:+.4f} CI95=[{p['ci_95'][0]:+.4f},{p['ci_95'][1]:+.4f}] "
                  f"({'SIG' if p['sig'] else 'ns'})  "
                  f"R={r['point']:+.4f} CI95=[{r['ci_95'][0]:+.4f},{r['ci_95'][1]:+.4f}] "
                  f"({'SIG' if r['sig'] else 'ns'})")

    print(f"\n{'=' * 78}\nDone. Full report written to {RESULTS_DIR / 'analysis_report_verse.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
