"""Per-poem breakdown (Phase 2 §6) — answers Tsvika's same-poet question.
Re-slices Phase 1's frozen TEST/DEV manifests by INDIVIDUAL poem instead of
the pooled-across-poems view used everywhere else in Phase 1 (§3a) and
Phase 2 (§3i). No new API calls; no change to any frozen pooled number —
this is a different aggregation of the exact same underlying data.

Baseline run counts are NOT uniform across poems (a pre-existing Phase 1
asymmetry, not introduced here): TEST poems and Imru2 have 2 baseline
runs; Nabigha's baseline has only 1 (see PROJECT_STATE.md §4). Flagged
explicitly wherever Nabigha's baseline numbers are shown.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))

from config import ELEMENT_ORDER, POEMS, MODELS  # noqa: E402
from analyze import load_all_runs, prf1  # noqa: E402
from ground_truth import load_ground_truth_spans  # noqa: E402
from span_scoring import score_span_level  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
P1 = ROOT / "results" / "pilot_3models"

POEM_DIRS = {
    # poem_key: {"baseline": dir_or_None, "v4_combined": dir, "is_dev": bool, "baseline_runs": int}
    "Imru1": {"baseline": P1 / "test_final" / "baseline" / "Imru1", "v4_combined": P1 / "test_final" / "v4_combined" / "Imru1", "is_dev": False, "baseline_runs": 2},
    "Jarir": {"baseline": P1 / "test_final" / "baseline" / "Jarir", "v4_combined": P1 / "test_final" / "v4_combined" / "Jarir", "is_dev": False, "baseline_runs": 2},
    "Abu_Tammam": {"baseline": P1 / "test_final" / "baseline" / "Abu_Tammam", "v4_combined": P1 / "test_final" / "v4_combined" / "Abu_Tammam", "is_dev": False, "baseline_runs": 2},
    "Imru2": {"baseline": P1, "v4_combined": P1 / "dev_variants" / "v4_combined" / "Imru2", "is_dev": True, "baseline_runs": 2},
    "Nabigha": {"baseline": P1 / "dev_nabigha_baseline", "v4_combined": P1 / "dev_variants" / "v4_combined" / "Nabigha", "is_dev": True, "baseline_runs": 1},
}

POET = {"Imru1": "Imru' al-Qais", "Imru2": "Imru' al-Qais", "Nabigha": "Al-Nabigha", "Jarir": "Jarir", "Abu_Tammam": "Abu Tammam"}


def poem_scores(poem_key: str, prompt_key: str, criterion: str = "strict"):
    out_dir = POEM_DIRS[poem_key][prompt_key]
    by_provider = load_all_runs(out_dir)
    gt_spans = load_ground_truth_spans(poem_key)
    n_verses = POEMS[poem_key]["n_verses"]
    return score_span_level(by_provider, gt_spans, n_verses, criterion)


def main():
    for criterion in ["strict", "token"]:
        print(f"\n{'='*140}\nCRITERION = {criterion}\n{'='*140}")
        for poem_key, meta in POEM_DIRS.items():
            dev_tag = " [DEV]" if meta["is_dev"] else " [TEST]"
            baseline_note = f" (baseline: {meta['baseline_runs']} run{'s' if meta['baseline_runs']>1 else ''})" if meta["baseline_runs"] != 2 else ""
            print(f"\n--- {poem_key}{dev_tag} — poet: {POET[poem_key]}{baseline_note} ---")
            b_scores = poem_scores(poem_key, "baseline", criterion)
            v4_scores = poem_scores(poem_key, "v4_combined", criterion)
            print(f"{'Element':<10} {'Model':<10} {'Baseline TP/FP/FN':<20} {'F1':>6}   {'v4 TP/FP/FN':<20} {'F1':>6}")
            for element in ELEMENT_ORDER:
                for provider in MODELS:
                    if provider not in b_scores or provider not in v4_scores:
                        continue
                    b = b_scores[provider][element]
                    v = v4_scores[provider][element]
                    bs = prf1(b["tp"], b["fp"], b["fn"])
                    vs = prf1(v["tp"], v["fp"], v["fn"])
                    print(f"{element:<10} {provider:<10} {b['tp']:>2}/{b['fp']:>2}/{b['fn']:>2}{'':<11} {bs['f1']:>6.3f}   "
                          f"{v['tp']:>2}/{v['fp']:>2}/{v['fn']:>2}{'':<11} {vs['f1']:>6.3f}")


if __name__ == "__main__":
    main()
