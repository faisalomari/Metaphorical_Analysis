"""Step 4 (NO API calls): score F5/F10 on the new 50-poem multipoet pool,
compare against each other and (on the 9-poem overlap only) against the
existing Z/A/B/C/D (on eval_pool_25.json), and compute the F5/F10 ensemble.

Reuses scoring_v2.score_set / bootstrap_ci_pairwise / per_poem_diff_signs
and ensemble_v2's cache/scoring helpers UNCHANGED -- this script only wires
them to the new pool/sets, same convention as analyze_D.py / verse_analysis.py
did for Set D.

IMPORTANT CAVEAT (stated here and carried into the written report): F5/F10
ran on a DIFFERENT 50-poem pool than Z/A/B/C/D (which ran on
eval_pool_25.json). Only 9 of the 25 pool_25 poems are also in F5/F10's
pool, so any F5/F10-vs-Z/A/B/C/D comparison below is restricted to that
9-poem intersection (scoring_v2.bootstrap_ci_pairwise already does this
intersection automatically via set(per_poem_a) & set(per_poem_b)) and is
explicitly flagged as thin/indicative. F5's own and F10's own numbers
(not compared to Z/A/B/C/D) use the FULL 50-poem / 1000-verse pool.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, PILOT_DIR, RESULTS_DIR  # noqa: E402
from multipoet_config import EVAL_POOL_50_MULTIPOET_PATH  # noqa: E402
from runner import spend_so_far  # noqa: E402 (import order: see analyze_v2.py's own note)
from scoring_v2 import bootstrap_ci_pairwise, per_poem_diff_signs  # noqa: E402
from ensemble_v2 import (  # noqa: E402
    agreement_for_set, build_parsed_cache, score_set_ensemble, score_set_single_model,
)
# NOTE: uses ensemble_v2.score_set_single_model (cache-based) throughout, NOT
# scoring_v2.score_set directly -- score_set's load_verse_result re-reads and
# re-parses the ENTIRE run_manifest.json from disk on every single verse
# lookup, which is fine called a handful of times (as analyze_D.py/
# verse_analysis.py do, against a smaller manifest) but became a multi-minute
# bottleneck here against the now-much-larger manifest (12k+ records) called
# thousands of times across 2 sets x 3 providers x 3 criteria x 1000 verses.
# Building ONE cache up front and reusing it is the same fix ensemble_v2.py's
# own docstring already describes for its own single-model rescoring need.

if str(PILOT_DIR) not in sys.path:
    sys.path.insert(0, str(PILOT_DIR))
from analyze import prf1  # noqa: E402

MODELS_ORDER = ["anthropic", "openai", "google"]
CRITERIA_ORDER = ["verse", "strict", "token"]
MULTIPOET_SETS = ["F5", "F10"]
BASELINE_SETS = ["Z", "A", "B", "C", "D"]
DISPLAY = {"anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
           "google": "Gemini (served: gemini-3.6-flash)"}


def _totals(per_poem: dict, poem_ids) -> dict:
    tp = sum(per_poem[p]["tp"] for p in poem_ids)
    fp = sum(per_poem[p]["fp"] for p in poem_ids)
    fn = sum(per_poem[p]["fn"] for p in poem_ids)
    return {"tp": tp, "fp": fp, "fn": fn, **prf1(tp, fp, fn)}


def load_baseline_reports():
    """{criterion: {set_name: {provider: per_set_dict}}} for Z/A/B/C/D,
    read from the already-frozen analysis_report*.json files (not recomputed)."""
    zabc_strict_token = json.loads((RESULTS_DIR / "analysis_report.json").read_text(encoding="utf-8"))
    d_strict_token = json.loads((RESULTS_DIR / "analysis_report_D.json").read_text(encoding="utf-8"))
    verse = json.loads((RESULTS_DIR / "analysis_report_verse.json").read_text(encoding="utf-8"))

    out = {c: {s: {} for s in BASELINE_SETS} for c in CRITERIA_ORDER}
    for provider in MODELS_ORDER:
        for criterion in ("strict", "token"):
            for s in ("Z", "A", "B", "C"):
                out[criterion][s][provider] = zabc_strict_token[provider][criterion]["per_set"][s]
            out[criterion]["D"][provider] = d_strict_token[provider][criterion]["per_set"]["D"]
        out["verse"]["Z"][provider] = {"per_poem": verse[provider]["per_set"]["Z"]["per_poem"]}
        out["verse"]["A"][provider] = {"per_poem": verse[provider]["per_set"]["A"]["per_poem"]}
        out["verse"]["B"][provider] = {"per_poem": verse[provider]["per_set"]["B"]["per_poem"]}
        out["verse"]["C"][provider] = {"per_poem": verse[provider]["per_set"]["C"]["per_poem"]}
        out["verse"]["D"][provider] = {"per_poem": verse[provider]["per_set"]["D"]["per_poem"]}
    return out


def main():
    multipoet_pool = json.loads(EVAL_POOL_50_MULTIPOET_PATH.read_text(encoding="utf-8"))["poems"]
    pool_25 = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    multipoet_ids = {p["poem_id"] for p in multipoet_pool}
    pool_25_ids = {p["poem_id"] for p in pool_25}
    overlap_ids = sorted(multipoet_ids & pool_25_ids, key=int)
    print(f"Multipoet pool: {len(multipoet_pool)} poems. pool_25: {len(pool_25)} poems. "
          f"Overlap: {len(overlap_ids)} poems: {overlap_ids}")

    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    mp_manifest = [r for r in manifest if r["set_name"] in MULTIPOET_SETS]
    spend = spend_so_far([r for r in manifest if r["set_name"] in MULTIPOET_SETS])
    print(f"F5/F10 manifest records: {len(mp_manifest)}. Real cost: openai=${spend['openai']:.4f} "
          f"google=${spend['google']:.4f} anthropic=${spend['anthropic']:.4f} TOTAL=${spend['_total']:.4f}")

    baseline = load_baseline_reports()
    cache = build_parsed_cache(mp_manifest, RESULTS_DIR)

    report = {"primary_pool": {}, "vs_baseline_9poem_overlap": {}, "ensemble": {}}

    # ---- 1. F5/F10 primary numbers on their own full 50-poem pool ----
    for provider in MODELS_ORDER:
        report["primary_pool"][provider] = {}
        for criterion in CRITERIA_ORDER:
            per_set = {s: score_set_single_model(cache, multipoet_pool, s, provider, criterion) for s in MULTIPOET_SETS}
            pair = bootstrap_ci_pairwise(per_set["F5"]["per_poem"], per_set["F10"]["per_poem"])
            diffs = per_poem_diff_signs(per_set["F5"]["per_poem"], per_set["F10"]["per_poem"])
            report["primary_pool"][provider][criterion] = {
                "per_set": per_set, "F5_vs_F10": {"bootstrap_ci": pair, "diff_signs": diffs},
            }

    print("\n" + "=" * 78)
    print("PRIMARY: F5 vs F10 on their own full 50-poem / 1000-verse pool")
    print("=" * 78)
    for provider in MODELS_ORDER:
        print(f"\n-- {DISPLAY[provider]} --")
        for criterion in CRITERIA_ORDER:
            block = report["primary_pool"][provider][criterion]
            for s in MULTIPOET_SETS:
                for split in ("overall", "abu_nuwas", "other"):
                    c = block["per_set"][s][split]
                    print(f"  [{criterion:6s}] set {s:3s}/{split:9s}: TP={c['tp']:4d} FP={c['fp']:4d} "
                          f"FN={c['fn']:4d} P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}")
            ci = block["F5_vs_F10"]["bootstrap_ci"]
            dsign = block["F5_vs_F10"]["diff_signs"]
            sig = "SIG" if (ci["ci_95"][0] > 0 or ci["ci_95"][1] < 0) else "ns"
            print(f"  [{criterion:6s}] F5-F10: point={ci['point']:+.4f} "
                  f"CI95=[{ci['ci_95'][0]:+.4f},{ci['ci_95'][1]:+.4f}] ({sig})  "
                  f"per-poem: F5>F10={dsign['a_greater']} F10>F5={dsign['b_greater']} tied={dsign['tied']}")

    # ---- 2. F5/F10 vs Z/A/B/C/D on the 9-poem overlap only ----
    print("\n" + "=" * 78)
    print(f"SECONDARY (THIN, n={len(overlap_ids)} poems): F5/F10 vs Z/A/B/C/D on the pool-25 overlap")
    print("=" * 78)
    for provider in MODELS_ORDER:
        report["vs_baseline_9poem_overlap"][provider] = {}
        for criterion in CRITERIA_ORDER:
            mp_per_set = {s: score_set_single_model(cache, multipoet_pool, s, provider, criterion)["per_poem"]
                          for s in MULTIPOET_SETS}
            base_per_set = {s: baseline[criterion][s][provider]["per_poem"] for s in BASELINE_SETS}
            all_per_set = {**mp_per_set, **base_per_set}
            overlap_totals = {s: _totals(all_per_set[s], overlap_ids) for s in all_per_set}
            pairwise = {}
            for probe in MULTIPOET_SETS:
                for base in BASELINE_SETS:
                    ci = bootstrap_ci_pairwise(all_per_set[probe], all_per_set[base])
                    # scoring_v2.bootstrap_ci_pairwise's own "point" is computed from
                    # score_total(), which sums over EVERY poem_id in each input dict --
                    # correct when both sides share one pool (its only prior use case),
                    # but WRONG here: F5/F10's per_poem dict spans the full 50-poem pool
                    # while Z/A/B/C/D's spans pool_25, so that point would silently mix
                    # in poems outside the 9-poem overlap. The CI bounds themselves ARE
                    # correct (the function's resampling already restricts to
                    # set(per_poem_a) & set(per_poem_b)) -- only "point" is overridden
                    # here, with the SAME overlap-restricted F1 difference the resampling
                    # is actually drawn from (overlap_totals, computed above).
                    ci["point"] = overlap_totals[probe]["f1"] - overlap_totals[base]["f1"]
                    pairwise[f"{probe}-{base}"] = ci
            report["vs_baseline_9poem_overlap"][provider][criterion] = {
                "overlap_totals": overlap_totals, "pairwise_bootstrap_ci": pairwise,
            }
            print(f"\n-- {DISPLAY[provider]} / {criterion} (9-poem overlap totals) --")
            for s in MULTIPOET_SETS + BASELINE_SETS:
                t = overlap_totals[s]
                print(f"  set {s:3s}: TP={t['tp']:3d} FP={t['fp']:3d} FN={t['fn']:3d} "
                      f"P={t['precision']:.3f} R={t['recall']:.3f} F1={t['f1']:.3f}")
            print("  gain over Z (bootstrap CI over the FULL pools each set actually ran on, "
                  "poems intersected automatically to the overlap):")
            for probe in MULTIPOET_SETS:
                ci = pairwise[f"{probe}-Z"]
                sig = "SIG" if (ci["ci_95"][0] > 0 or ci["ci_95"][1] < 0) else "ns"
                print(f"    {probe}-Z: point={ci['point']:+.4f} CI95=[{ci['ci_95'][0]:+.4f},"
                      f"{ci['ci_95'][1]:+.4f}] ({sig})")

    # ---- 3. Ensemble for F5/F10 on the full new pool ----
    print("\n" + "=" * 78)
    print("ENSEMBLE (2-of-3 majority vote) for F5/F10 on the full new 50-poem pool")
    print("=" * 78)
    for s in MULTIPOET_SETS:
        report["ensemble"][s] = {"agreement": agreement_for_set(cache, multipoet_pool, s), "criteria": {}}
        print(f"\nSet {s} agreement buckets (overall):")
        for k in ("3", "2", "1", "0"):
            b = report["ensemble"][s]["agreement"]["overall"][k]
            print(f"  {k}/3 votes: n={b['n']:4d}  GT-positive-rate={b['gt_positive_rate']:.3f}  "
                  f"accuracy-vs-GT={b['accuracy']:.3f}")
        for criterion in CRITERIA_ORDER:
            ens = score_set_ensemble(cache, multipoet_pool, s, criterion)
            singles = {m: score_set_single_model(cache, multipoet_pool, s, m, criterion) for m in MODELS_ORDER}
            f1s = {m: singles[m]["overall"]["f1"] for m in MODELS_ORDER}
            best_model = max(f1s, key=f1s.get)
            report["ensemble"][s]["criteria"][criterion] = {
                "ensemble_overall": ens["overall"], "singles_overall": {m: singles[m]["overall"] for m in MODELS_ORDER},
                "best_model": best_model, "best_f1": f1s[best_model], "avg_f1": sum(f1s.values()) / 3,
            }
            c = ens["overall"]
            print(f"  [{criterion}] ensemble: TP={c['tp']:4d} FP={c['fp']:4d} FN={c['fn']:4d} "
                  f"P={c['precision']:.3f} R={c['recall']:.3f} F1={c['f1']:.3f}  |  "
                  f"best single={best_model} F1={f1s[best_model]:.3f}  avg single F1={sum(f1s.values())/3:.3f}")

    out_path = RESULTS_DIR / "analysis_report_multipoet.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{'=' * 78}\nDone. Full report written to {out_path}\n{'=' * 78}")


if __name__ == "__main__":
    main()
