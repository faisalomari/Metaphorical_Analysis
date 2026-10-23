"""Step 5 (NO API calls): scores the six poet-era sets (M1/M2/E1/E2/H1/H2)
on eval_pool_25.json -- the SAME pool Z/A/B/C/D/D2 already ran on, so every
comparison below is a clean, non-thin comparison (no 9-poem-overlap caveat
like F5/F10 needed).

Computes, per model x criterion (verse PRIMARY, strict/token secondary):
  - overall/abu_nuwas/other TP/FP/FN/P/R/F1 for each of M1,M2,E1,E2,H1,H2
    (scoring_v2.score_set, reused unchanged).
  - POOLED aggregates M=M1+M2, E=E1+E2, H=H1+H2 (per-poem TP/FP/FN summed
    across the two constituent sets -- declared explicitly: this evaluates
    "does drawing from this era-band help, regardless of which 2 specific
    poets were drawn," at the cost of effectively doubling each poem's
    verse-units for the pooled comparison only).
  - bootstrap 95% CI (per-poem resampling, scoring_v2.bootstrap_ci_pairwise,
    n_iter=2000 seed=0, same method as every other E1 v2 analysis) for:
    within-pair noise (M1-M2, E1-E2, H1-H2), pooled cross-category
    (M-E, M-H, E-H), each of the 6 sets vs Z, and each of the 6 sets vs
    the existing 2-example sets A/B/D2.
  - 3-model majority-vote ensemble for the 6 new sets, reusing
    ensemble_v2.py's cache-based scorer unchanged (score_set_single_model /
    score_set_ensemble are generic over set_name, no edits needed there).
  - per-poem diff signs (a_greater/b_greater/tied) for every pair above.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from eras_config import ERAS_SET_NAMES  # noqa: E402
from runner import spend_so_far  # noqa: E402  (import-order note: see analyze_v2.py --
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
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
           "google": "Gemini (served: gemini-3.6-flash)"}

EXISTING_BASELINES = ["Z", "A", "B", "D2"]
WITHIN_PAIR_NOISE = [("M1", "M2"), ("E1", "E2"), ("H1", "H2")]
POOLED_GROUPS = {"M": ("M1", "M2"), "E": ("E1", "E2"), "H": ("H1", "H2")}
POOLED_CROSS = [("M", "E"), ("M", "H"), ("E", "H")]


def pool_per_poem(per_set_a: dict, per_set_b: dict) -> dict:
    """Sum tp/fp/fn per poem across two sets' per_poem dicts (same poems,
    same tags -- eval_pool_25.json is shared)."""
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


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    spend = spend_so_far(manifest)
    eras_manifest_records = [r for r in manifest if r["set_name"] in ERAS_SET_NAMES]
    n_eras_ok = sum(1 for r in eras_manifest_records if r.get("error") is None)
    print(f"Manifest: {len(manifest)} total records. Eras (M1..H2) records: "
          f"{len(eras_manifest_records)} ({n_eras_ok} ok, "
          f"{len(eras_manifest_records) - n_eras_ok} error). Cumulative spend: ${spend['_total']:.4f}")
    for s in ERAS_SET_NAMES:
        for p in MODELS_ORDER:
            n = sum(1 for r in eras_manifest_records if r["set_name"] == s and r["provider"] == p
                    and r.get("error") is None)
            assert n == 327, f"set {s} / {p}: expected 327 ok cells, got {n}"
    print(f"OK: all {len(ERAS_SET_NAMES)} sets x {len(MODELS_ORDER)} models confirmed at 327/327 ok cells.")

    # Cache-based scoring (ensemble_v2's fix for scoring_v2.score_set's per-verse full-manifest
    # rescan, which is far too slow against this now-18k-record manifest -- same fix
    # analyze_multipoet.py already needed and documented in SESSION_LOG.md).
    cache = build_parsed_cache(manifest, RESULTS_DIR)
    verify_single_model_cache_scorer(cache, pool)

    report = {"models": {}, "pooled": {}, "ensemble": {}}

    for provider in MODELS_ORDER:
        report["models"][provider] = {}
        for criterion in CRITERIA_ORDER:
            per_set = {s: score_set_single_model(cache, pool, s, provider, criterion) for s in ERAS_SET_NAMES}
            baseline_sets = {}
            for b in EXISTING_BASELINES:
                baseline_sets[b] = score_set_single_model(cache, pool, b, provider, criterion)

            pairwise, diffs = {}, {}
            for a, b in WITHIN_PAIR_NOISE:
                key = f"{a}-{b}"
                pairwise[key] = bootstrap_ci_pairwise(per_set[a]["per_poem"], per_set[b]["per_poem"])
                diffs[key] = per_poem_diff_signs(per_set[a]["per_poem"], per_set[b]["per_poem"])
            for s in ERAS_SET_NAMES:
                for b in EXISTING_BASELINES:
                    key = f"{s}-{b}"
                    pairwise[key] = bootstrap_ci_pairwise(per_set[s]["per_poem"], baseline_sets[b]["per_poem"])
                    diffs[key] = per_poem_diff_signs(per_set[s]["per_poem"], baseline_sets[b]["per_poem"])

            report["models"][provider][criterion] = {
                "per_set": per_set, "pairwise_bootstrap_ci": pairwise, "per_poem_diff_signs": diffs,
            }

    for provider in MODELS_ORDER:
        for criterion in CRITERIA_ORDER:
            per_set = report["models"][provider][criterion]["per_set"]
            pooled_per_poem = {}
            pooled_counts = {}
            for label, (a, b) in POOLED_GROUPS.items():
                pp = pool_per_poem(per_set[a]["per_poem"], per_set[b]["per_poem"])
                pooled_per_poem[label] = pp
                pooled_counts[label] = pool_counts(pp)
            pooled_pairwise, pooled_diffs = {}, {}
            for a, b in POOLED_CROSS:
                key = f"{a}-{b}"
                pooled_pairwise[key] = bootstrap_ci_pairwise(pooled_per_poem[a], pooled_per_poem[b])
                pooled_diffs[key] = per_poem_diff_signs(pooled_per_poem[a], pooled_per_poem[b])
            report["pooled"].setdefault(provider, {})[criterion] = {
                "per_group": {k: {kk: vv for kk, vv in v.items() if kk != "per_poem"}
                              for k, v in pooled_counts.items()},
                "pairwise_bootstrap_ci": pooled_pairwise, "per_poem_diff_signs": pooled_diffs,
            }

    # 3-model majority-vote ensemble for the 6 eras sets (ensemble_v2's cache-based
    # scorer is generic over set_name -- no edits to that module needed; reuses the
    # same cache built above).
    for criterion in CRITERIA_ORDER:
        report["ensemble"][criterion] = {}
        for s in ERAS_SET_NAMES:
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

    (RESULTS_DIR / "analysis_report_eras.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- printed summary ----
    for provider in MODELS_ORDER:
        print(f"\n{'=' * 78}\n{DISPLAY[provider]} ({provider})\n{'=' * 78}")
        for criterion in CRITERIA_ORDER:
            print(f"\n-- criterion: {criterion} --")
            per_set = report["models"][provider][criterion]["per_set"]
            for s in ERAS_SET_NAMES:
                for split in ("overall", "abu_nuwas", "other"):
                    c = per_set[s][split]
                    print(f"  set {s:3s} / {split:9s}: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d}  "
                          f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
            print("  bootstrap 95% CI (F1_i - F1_j), per-poem diff signs (i>j/j>i/tied):")
            for pair, ci in report["models"][provider][criterion]["pairwise_bootstrap_ci"].items():
                d = report["models"][provider][criterion]["per_poem_diff_signs"][pair]
                sig = "SIG" if not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1]) else "ns"
                print(f"    {pair}: F1={ci['point']:+.4f} CI95=[{ci['ci_95'][0]:+.4f},{ci['ci_95'][1]:+.4f}] "
                      f"({sig})  signs={d['a_greater']}/{d['b_greater']}/{d['tied']}")
            print("  POOLED (M=M1+M2, E=E1+E2, H=H1+H2):")
            for label, c in report["pooled"][provider][criterion]["per_group"].items():
                o = c["overall"]
                print(f"    {label}: TP={o['tp']:4d} FP={o['fp']:4d} FN={o['fn']:4d} "
                      f"P={o['precision']:.3f} R={o['recall']:.3f} F1={o['f1']:.3f}")
            for pair, ci in report["pooled"][provider][criterion]["pairwise_bootstrap_ci"].items():
                d = report["pooled"][provider][criterion]["per_poem_diff_signs"][pair]
                sig = "SIG" if not (ci["ci_95"][0] <= 0 <= ci["ci_95"][1]) else "ns"
                print(f"    POOLED {pair}: F1={ci['point']:+.4f} "
                      f"CI95=[{ci['ci_95'][0]:+.4f},{ci['ci_95'][1]:+.4f}] ({sig})  "
                      f"signs={d['a_greater']}/{d['b_greater']}/{d['tied']}")

    print(f"\n{'=' * 78}\nENSEMBLE (2-of-3 majority vote), verse-primary\n{'=' * 78}")
    for s in ERAS_SET_NAMES:
        e = report["ensemble"]["verse"][s]
        print(f"  set {s}: ensemble F1={e['ensemble']['overall']['f1']:.3f}  "
              f"best single={e['best_single']['model']} F1={e['best_single']['f1']:.3f}  "
              f"avg single F1={e['avg_single_f1']:.3f}")

    print(f"\n{'=' * 78}\nDone. Full report written to {RESULTS_DIR / 'analysis_report_eras.json'}\n{'=' * 78}")


if __name__ == "__main__":
    main()
