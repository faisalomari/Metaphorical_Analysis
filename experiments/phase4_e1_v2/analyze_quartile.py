"""Step 3 (NO API calls): scores the two quartile sets (Q1/Q2) on
eval_pool_25.json -- the SAME pool every other E1 v2 set already ran on.

Computes, per model x criterion (verse PRIMARY, strict/token secondary):
  - overall/abu_nuwas/other TP/FP/FN/P/R/F1 for Q1 and Q2
    (ensemble_v2's cache-based scorer, reused unchanged).
  - POOLED Q = Q1+Q2 (per-poem TP/FP/FN summed across the two constituent
    sets -- same convention as analyze_eras.py's M/E/H pooling).
  - bootstrap 95% CI (per-poem resampling, n_iter=2000 seed=0) for:
    Q1 vs Q2 (within-pair noise), pooled Q vs pooled M, vs pooled E,
    vs pooled H (declared explicitly as the "same-half variant, not the
    requested quartile design" per CLAUDE.md-style terminology note),
    pooled Q vs Z, and pooled Q vs each of A/B/D2.
  - 3-model majority-vote ensemble for Q1 and Q2 (ensemble_v2's
    cache-based scorer is generic over set_name -- no edits needed).
  - per-poem diff signs for every pair above.

Also verifies (printed, not just asserted) which Gemini model_id was
actually served across the WHOLE manifest (not just Q1/Q2) -- the task
asked this be checked because analyze_eras.py's DISPLAY dict labels
google as "served: gemini-3.6-flash", which this check shows is wrong
(every google record, Q1/Q2 included, logs model_id="gemini-3.5-flash").
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from eras_quartile_config import QUARTILE_SET_NAMES  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import-order note: see analyze_v2.py/analyze_eras.py --
# must precede gt_v2/scoring_v2, which insert phase4_e1 (v1) onto sys.path and would
# otherwise shadow this runner.py with v1's own, which has no spend_so_far)
from scoring_v2 import bootstrap_ci_pairwise, per_poem_diff_signs  # noqa: E402
from ensemble_v2 import (  # noqa: E402
    build_parsed_cache, score_set_single_model, score_set_ensemble, verify_single_model_cache_scorer,
)

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

MODELS_ORDER = ["anthropic", "openai", "google"]
CRITERIA_ORDER = ["verse", "strict", "token"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini", "google": "Gemini"}

EXISTING_BASELINES = ["Z", "A", "B", "D2"]
# "H" here means H1+H2 pooled -- the pre-existing "same-half variant, not the requested
# design" set, explicitly distinguished from Q (the actual quartile design) per the task.
EXISTING_POOLED_GROUPS = ["M", "E", "H"]


def pool_per_poem(per_set_a: dict, per_set_b: dict) -> dict:
    out = {}
    for poem_id in per_set_a:
        a, b = per_set_a[poem_id], per_set_b[poem_id]
        out[poem_id] = {"tp": a["tp"] + b["tp"], "fp": a["fp"] + b["fp"], "fn": a["fn"] + b["fn"],
                         "tag": a["tag"]}
    return out


def pool_counts(per_poem: dict) -> dict:
    def agg(tag=None):
        tp = sum(c["tp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fp = sum(c["fp"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        fn = sum(c["fn"] for c in per_poem.values() if tag is None or c["tag"] == tag)
        return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}
    return {"per_poem": per_poem, "overall": agg(), "abu_nuwas": agg("abu_nuwas"), "other": agg("other")}


def check_served_gemini_model(manifest: list) -> str:
    counts = Counter(r["model_id"] for r in manifest if r["provider"] == "google")
    print(f"Gemini model_id actually served, ALL manifest google records ({sum(counts.values())} total): "
          f"{dict(counts)}")
    q_counts = Counter(r["model_id"] for r in manifest
                        if r["provider"] == "google" and r["set_name"] in QUARTILE_SET_NAMES)
    print(f"Gemini model_id actually served, Q1/Q2 only ({sum(q_counts.values())} total): {dict(q_counts)}")
    assert len(counts) == 1, f"multiple Gemini model_ids served across the manifest: {counts}"
    served = next(iter(counts))
    print(f"CONCLUSION: every google-provider call in this project (Q1/Q2 included) was served by "
          f"{served!r} -- NOT gemini-3.6-flash. analyze_eras.py's DISPLAY dict label "
          f"\"Gemini (served: gemini-3.6-flash)\" is incorrect; this script's DISPLAY uses the plain "
          f"name and states the real served model_id here instead.")
    return served


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    spend = spend_so_far(manifest)
    q_records = [r for r in manifest if r["set_name"] in QUARTILE_SET_NAMES]
    n_q_ok = sum(1 for r in q_records if r.get("error") is None)
    print(f"Manifest: {len(manifest)} total records. Quartile (Q1/Q2) records: "
          f"{len(q_records)} ({n_q_ok} ok, {len(q_records) - n_q_ok} error). "
          f"Cumulative spend: ${spend['_total']:.4f}")
    for s in QUARTILE_SET_NAMES:
        for p in MODELS_ORDER:
            n = sum(1 for r in q_records if r["set_name"] == s and r["provider"] == p
                    and r.get("error") is None)
            assert n == 327, f"set {s} / {p}: expected 327 ok cells, got {n}"
    print(f"OK: both {len(QUARTILE_SET_NAMES)} sets x {len(MODELS_ORDER)} models confirmed at 327/327 ok cells.")

    served_gemini_model = check_served_gemini_model(manifest)

    cache = build_parsed_cache(manifest, RESULTS_DIR)
    verify_single_model_cache_scorer(cache, pool)

    report = {"served_gemini_model_id": served_gemini_model, "models": {}, "pooled_q": {}, "ensemble": {}}

    for provider in MODELS_ORDER:
        report["models"][provider] = {}
        for criterion in CRITERIA_ORDER:
            per_set = {s: score_set_single_model(cache, pool, s, provider, criterion) for s in QUARTILE_SET_NAMES}
            baseline_sets = {b: score_set_single_model(cache, pool, b, provider, criterion)
                              for b in EXISTING_BASELINES}
            pooled_existing = {}
            for label, (a, b) in {"M": ("M1", "M2"), "E": ("E1", "E2"), "H": ("H1", "H2")}.items():
                pa = score_set_single_model(cache, pool, a, provider, criterion)
                pb = score_set_single_model(cache, pool, b, provider, criterion)
                pooled_existing[label] = pool_counts(pool_per_poem(pa["per_poem"], pb["per_poem"]))

            pooled_q_per_poem = pool_per_poem(per_set["Q1"]["per_poem"], per_set["Q2"]["per_poem"])
            pooled_q = pool_counts(pooled_q_per_poem)

            pairwise, diffs = {}, {}
            pairwise["Q1-Q2"] = bootstrap_ci_pairwise(per_set["Q1"]["per_poem"], per_set["Q2"]["per_poem"])
            diffs["Q1-Q2"] = per_poem_diff_signs(per_set["Q1"]["per_poem"], per_set["Q2"]["per_poem"])
            for label in EXISTING_POOLED_GROUPS:
                key = f"Q-{label}"
                pairwise[key] = bootstrap_ci_pairwise(pooled_q_per_poem, pooled_existing[label]["per_poem"])
                diffs[key] = per_poem_diff_signs(pooled_q_per_poem, pooled_existing[label]["per_poem"])
            for b in EXISTING_BASELINES:
                key = f"Q-{b}"
                pairwise[key] = bootstrap_ci_pairwise(pooled_q_per_poem, baseline_sets[b]["per_poem"])
                diffs[key] = per_poem_diff_signs(pooled_q_per_poem, baseline_sets[b]["per_poem"])

            report["models"][provider][criterion] = {
                "per_set": per_set,
                "pooled_q": {k: v for k, v in pooled_q.items() if k != "per_poem"},
                "pooled_existing": {g: {k: v for k, v in c.items() if k != "per_poem"}
                                     for g, c in pooled_existing.items()},
                "pairwise_bootstrap_ci": pairwise, "per_poem_diff_signs": diffs,
            }

    for criterion in CRITERIA_ORDER:
        report["ensemble"][criterion] = {}
        for s in QUARTILE_SET_NAMES:
            ens = score_set_ensemble(cache, pool, s, criterion)
            singles = {m: score_set_single_model(cache, pool, s, m, criterion) for m in MODELS_ORDER}
            f1s = {m: singles[m]["overall"]["f1"] for m in MODELS_ORDER}
            best_model = max(f1s, key=f1s.get)
            report["ensemble"][criterion][s] = {
                "ensemble": {k: v for k, v in ens.items() if k != "per_poem"},
                "best_single": {"model": best_model, "f1": f1s[best_model]},
                "avg_single_f1": sum(f1s.values()) / 3,
                "all_single_f1": f1s,
            }

    (RESULTS_DIR / "analysis_report_quartile.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- printed summary ----
    for provider in MODELS_ORDER:
        print(f"\n{'=' * 78}\n{DISPLAY[provider]} ({provider})\n{'=' * 78}")
        for criterion in CRITERIA_ORDER:
            print(f"\n-- criterion: {criterion} --")
            per_set = report["models"][provider][criterion]["per_set"]
            for s in QUARTILE_SET_NAMES:
                c = per_set[s]["overall"]
                print(f"  set {s:3s} / overall: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d}  "
                      f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
            pq = report["models"][provider][criterion]["pooled_q"]["overall"]
            print(f"  POOLED Q (Q1+Q2): TP={pq['tp']:4d} FP={pq['fp']:4d} FN={pq['fn']:4d} "
                  f"P={pq['precision']:.3f} R={pq['recall']:.3f} F1={pq['f1']:.3f}")
            for label, c in report["models"][provider][criterion]["pooled_existing"].items():
                o = c["overall"]
                print(f"    (reference) pooled {label}: TP={o['tp']:4d} FP={o['fp']:4d} FN={o['fn']:4d} "
                      f"P={o['precision']:.3f} R={o['recall']:.3f} F1={o['f1']:.3f}")
            print("  bootstrap 95% CI (F1_i - F1_j), per-poem diff signs (i>j/j>i/tied):")
            for pair, ci in report["models"][provider][criterion]["pairwise_bootstrap_ci"].items():
                d = report["models"][provider][criterion]["per_poem_diff_signs"][pair]
                sig = "SIG" if not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1]) else "ns"
                print(f"    {pair}: F1={ci['point']:+.4f} CI95=[{ci['ci_95'][0]:+.4f},{ci['ci_95'][1]:+.4f}] "
                      f"({sig})  signs={d['a_greater']}/{d['b_greater']}/{d['tied']}")

    print(f"\n{'=' * 78}\nENSEMBLE (2-of-3 majority vote), verse-primary\n{'=' * 78}")
    for s in QUARTILE_SET_NAMES:
        e = report["ensemble"]["verse"][s]
        print(f"  set {s}: ensemble F1={e['ensemble']['overall']['f1']:.3f}  "
              f"best single={e['best_single']['model']} F1={e['best_single']['f1']:.3f}  "
              f"avg single F1={e['avg_single_f1']:.3f}")

    print(f"\n{'=' * 78}\nDone. Full report written to {RESULTS_DIR / 'analysis_report_quartile.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
