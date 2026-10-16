"""Scores Claude Opus 5.5 on set A only -- NO API calls, reads run_manifest.json +
raw/*.txt. Verse-level is PRIMARY (CLAUDE.md rule 4 / the user's 2026-10-14 decision,
same convention as verse_analysis.py); strict/token-overlap are secondary.

Compares Opus against Claude Sonnet 4.6, GPT-5.4-mini, Gemini, and the majority-vote
ensemble, all on set A: F1/precision/recall bootstrap 95% CIs over poems (reusing
verse_analysis.bootstrap_pair unchanged -- same seed=0, n_iter=2000, with-replacement-
over-poems method as every other Phase 4 comparison in this repo).

Set A is one of the few-shot sets (2 extra example verses beyond the Z baseline).
Opus was NOT run on Z/B/C/D/D2, so no gain-over-Z (or any other-set comparison) can be
computed for Opus -- only the 4-way same-set comparison on A, stated explicitly in the
written report.

Writes results/phase4_e1_v2/analysis_report_opus_a.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1v2_config import EVAL_POOL_25_PATH, RESULTS_DIR  # noqa: E402
from verse_analysis import bootstrap_pair  # noqa: E402
from ensemble_v2 import build_parsed_cache, score_set_ensemble, score_set_single_model  # noqa: E402

CRITERIA = ["verse", "strict", "token"]
SINGLE_MODELS = ["anthropic", "openai", "google"]
DISPLAY = {
    "anthropic": "Claude Sonnet 4.6", "openai": "GPT-5.4-mini",
    "google": "Gemini (served: gemini-3.6-flash)", "ensemble": "Majority-vote ensemble (2-of-3)",
    "anthropic_opus": "Claude Opus 5.5",
}


def main():
    pool = json.loads(EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poems"]
    manifest = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
    cache = build_parsed_cache(manifest, RESULTS_DIR)

    opus_ok = [r for r in manifest if r["set_name"] == "A" and r["provider"] == "anthropic_opus"
               and r.get("error") is None]
    opus_err = [r for r in manifest if r["set_name"] == "A" and r["provider"] == "anthropic_opus"
                and r.get("error") is not None]
    print(f"Opus/set A manifest cells: {len(opus_ok)} ok, {len(opus_err)} error "
          f"(expected {sum(p['verse_count'] for p in pool)} ok).")

    report = {"set": "A", "provider": "anthropic_opus", "n_cells_ok": len(opus_ok),
              "n_cells_error": len(opus_err), "criteria": {}}

    for criterion in CRITERIA:
        opus = score_set_single_model(cache, pool, "A", "anthropic_opus", criterion)
        per_model = {}
        pairwise = {}
        for m in SINGLE_MODELS:
            per_model[m] = score_set_single_model(cache, pool, "A", m, criterion)
            pairwise[m] = bootstrap_pair(opus["per_poem"], per_model[m]["per_poem"])
        ensemble = score_set_ensemble(cache, pool, "A", criterion)
        pairwise["ensemble"] = bootstrap_pair(opus["per_poem"], ensemble["per_poem"])

        report["criteria"][criterion] = {
            "opus": {k: v for k, v in opus.items() if k != "per_poem"},
            "single_models": {m: {k: v for k, v in per_model[m].items() if k != "per_poem"}
                               for m in SINGLE_MODELS},
            "ensemble": {k: v for k, v in ensemble.items() if k != "per_poem"},
            "pairwise_vs_opus": pairwise,  # point = F1/P/R(opus) - F1/P/R(other); positive = opus wins
        }

    (RESULTS_DIR / "analysis_report_opus_a.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'=' * 78}\nClaude Opus 5.5 on set A -- verse (PRIMARY), strict/token (secondary)\n{'=' * 78}")
    for criterion in CRITERIA:
        c = report["criteria"][criterion]
        print(f"\n--- criterion: {criterion} ---")
        for split in ("overall", "abu_nuwas", "other"):
            o = c["opus"][split]
            print(f"  Opus 5.5 / {split:9s}: TP={o['tp']:4d} FP={o['fp']:4d} FN={o['fn']:4d}  "
                  f"P={o['precision']:.3f} R={o['recall']:.3f} F1={o['f1']:.3f}")
        print("  Opus vs. each model/ensemble (F1_opus - F1_other), bootstrap 95% CI over poems:")
        for m in SINGLE_MODELS + ["ensemble"]:
            f1 = c["pairwise_vs_opus"][m]["f1"]
            p = c["pairwise_vs_opus"][m]["precision"]
            r = c["pairwise_vs_opus"][m]["recall"]
            other_f1 = (c["single_models"][m]["overall"]["f1"] if m in SINGLE_MODELS
                        else c["ensemble"]["overall"]["f1"])
            print(f"    vs {DISPLAY[m]:32s} (F1={other_f1:.3f}): "
                  f"ΔF1={f1['point']:+.4f} CI95=[{f1['ci_95'][0]:+.4f},{f1['ci_95'][1]:+.4f}] "
                  f"({'SIG' if f1['sig'] else 'ns'})  "
                  f"ΔP={p['point']:+.4f} ({'SIG' if p['sig'] else 'ns'})  "
                  f"ΔR={r['point']:+.4f} ({'SIG' if r['sig'] else 'ns'})")

    print(f"\n{'=' * 78}\nNOTE: Set A is one of the few-shot sets (Z + 2 extra example verses). Opus "
          f"5.5 was run ONLY on set A -- no Z/B/C/D/D2 results exist for it, so no gain-over-Z (or "
          f"any other cross-set comparison) can be computed for Opus.\n{'=' * 78}")
    print(f"\nWrote {RESULTS_DIR / 'analysis_report_opus_a.json'}")


if __name__ == "__main__":
    main()
