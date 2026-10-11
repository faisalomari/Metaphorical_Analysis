"""E1 v2 same-poet (abu_nuwas vs other) analysis. NO API calls -- reads
results/phase4_e1_v2/analysis_report.json (already computed, per-poem TP/FP/FN
counts included) plus experiments/phase4_e1_v2/{gt_v2,e1v2_config} for GT
density and the eval pool's poem metadata. Computes the gain-over-Z bootstrap
CIs per group (abu_nuwas/other) and the difference-of-gains CI, which the
existing analysis_report.json does not contain (it only has pairwise CIs over
the FULL pool, not within-group CIs or gain-over-Z specifically).
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E1V2_DIR = ROOT / "experiments" / "phase4_e1_v2"
sys.path.insert(0, str(E1V2_DIR))
from e1v2_config import E1V1_DIR, SET_NAMES  # noqa: E402
from gt_v2 import gt_spans_for_subtype  # noqa: E402

sys.path.insert(0, str(E1V1_DIR))
from ali_poems_io import load_poem_json  # noqa: E402

sys.path.insert(0, str(ROOT / "experiments" / "pilot_3models"))
from analyze import prf1  # noqa: E402

MODELS = ["anthropic", "openai", "google"]
CRITERIA = ["strict", "token"]

REPORT = json.loads((ROOT / "results" / "phase4_e1_v2" / "analysis_report.json").read_text(encoding="utf-8"))
POOL = json.loads((E1V2_DIR / "config" / "eval_pool_25.json").read_text(encoding="utf-8"))["poems"]

GROUPS = {
    "abu_nuwas": [p["poem_id"] for p in POOL if p["tag"] == "abu_nuwas"],
    "other": [p["poem_id"] for p in POOL if p["tag"] == "other"],
}
VERSE_COUNT = {p["poem_id"]: p["verse_count"] for p in POOL}
POET_NAME = {p["poem_id"]: p["poet_name"] for p in POOL}


def poem_f1_from_counts(c):
    return prf1(c["tp"], c["fp"], c["fn"])["f1"]


def pool_f1(per_poem, poem_ids):
    tp = sum(per_poem[p]["tp"] for p in poem_ids)
    fp = sum(per_poem[p]["fp"] for p in poem_ids)
    fn = sum(per_poem[p]["fn"] for p in poem_ids)
    return prf1(tp, fp, fn)["f1"], tp, fp, fn


def bootstrap_gain_ci(per_poem_set, per_poem_z, poem_ids, n_iter=2000, seed=0):
    """Bootstrap 95% CI for F1(set) - F1(Z), resampling poems WITHIN poem_ids only."""
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_iter):
        sample = [rng.choice(poem_ids) for _ in poem_ids]
        f1_set, *_ = pool_f1(per_poem_set, sample)
        f1_z, *_ = pool_f1(per_poem_z, sample)
        diffs.append(f1_set - f1_z)
    diffs.sort()
    lo = diffs[int(0.025 * n_iter)]
    hi = diffs[int(0.975 * n_iter) - 1]
    point = pool_f1(per_poem_set, poem_ids)[0] - pool_f1(per_poem_z, poem_ids)[0]
    return point, lo, hi


def bootstrap_diffofgains_ci(per_poem_set, per_poem_z, ids_a, ids_b, n_iter=2000, seed=0):
    """CI for (gain_a - gain_b) where gain_g = F1(set, group g) - F1(Z, group g).
    Resample poems within each group independently each iteration."""
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_iter):
        sample_a = [rng.choice(ids_a) for _ in ids_a]
        sample_b = [rng.choice(ids_b) for _ in ids_b]
        gain_a = pool_f1(per_poem_set, sample_a)[0] - pool_f1(per_poem_z, sample_a)[0]
        gain_b = pool_f1(per_poem_set, sample_b)[0] - pool_f1(per_poem_z, sample_b)[0]
        diffs.append(gain_a - gain_b)
    diffs.sort()
    lo = diffs[int(0.025 * n_iter)]
    hi = diffs[int(0.975 * n_iter) - 1]
    gain_a_point = pool_f1(per_poem_set, ids_a)[0] - pool_f1(per_poem_z, ids_a)[0]
    gain_b_point = pool_f1(per_poem_set, ids_b)[0] - pool_f1(per_poem_z, ids_b)[0]
    return gain_a_point - gain_b_point, lo, hi


def main():
    out = {}

    # --- Section 2: confound check -- verse counts, GT density per group, F1 at Z ---
    gt_density = {}
    for p in POOL:
        pj = load_poem_json(int(p["poem_id"]))
        gt = gt_spans_for_subtype(pj)
        n_pos_verses = sum(1 for v in gt.values() if v)
        n_pos_spans = sum(len(v) for v in gt.values())
        gt_density[p["poem_id"]] = {
            "verse_count": p["verse_count"],
            "n_gt_positive_verses": n_pos_verses,
            "n_gt_spans": n_pos_spans,
            "density_spans_per_verse": n_pos_spans / p["verse_count"],
        }
    out["gt_density_per_poem"] = gt_density

    group_density = {}
    for g, ids in GROUPS.items():
        total_verses = sum(VERSE_COUNT[i] for i in ids)
        total_spans = sum(gt_density[i]["n_gt_spans"] for i in ids)
        group_density[g] = {
            "n_poems": len(ids),
            "total_verses": total_verses,
            "total_gt_spans": total_spans,
            "density_spans_per_verse": total_spans / total_verses,
        }
    out["group_density"] = group_density

    # --- Section 3: gain over Z per group per model, criterion A/B/C, with CI ---
    gains = {}
    for model in MODELS:
        gains[model] = {}
        for criterion in CRITERIA:
            per_set = REPORT[model][criterion]["per_set"]
            per_poem_z = per_set["Z"]["per_poem"]
            gains[model][criterion] = {}
            for s in ["A", "B", "C"]:
                per_poem_s = per_set[s]["per_poem"]
                row = {}
                for g, ids in GROUPS.items():
                    point, lo, hi = bootstrap_gain_ci(per_poem_s, per_poem_z, ids)
                    row[g] = {"point": point, "ci_95": [lo, hi]}
                diff_point, diff_lo, diff_hi = bootstrap_diffofgains_ci(
                    per_poem_s, per_poem_z, GROUPS["abu_nuwas"], GROUPS["other"])
                row["diff_abu_minus_other"] = {"point": diff_point, "ci_95": [diff_lo, diff_hi]}
                gains[model][criterion][s] = row
    out["gain_over_z"] = gains

    # --- Section 4: per-poem table for abu_nuwas poems, F1 per set/model/criterion ---
    per_poem_table = {}
    for poem_id in GROUPS["abu_nuwas"]:
        per_poem_table[poem_id] = {"poet_name": POET_NAME[poem_id], "verse_count": VERSE_COUNT[poem_id]}
        for model in MODELS:
            per_poem_table[poem_id][model] = {}
            for criterion in CRITERIA:
                per_poem_table[poem_id][model][criterion] = {}
                for s in SET_NAMES:
                    c = REPORT[model][criterion]["per_set"][s]["per_poem"][poem_id]
                    per_poem_table[poem_id][model][criterion][s] = {
                        "tp": c["tp"], "fp": c["fp"], "fn": c["fn"], "f1": poem_f1_from_counts(c)}
    out["per_poem_abu_nuwas"] = per_poem_table

    (ROOT / "results" / "phase4_e1_v2" / "samepoet_analysis.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote results/phase4_e1_v2/samepoet_analysis.json")

    # Print key tables for review
    print("\n=== Group density ===")
    for g, d in group_density.items():
        print(f"  {g}: n_poems={d['n_poems']} total_verses={d['total_verses']} "
              f"total_gt_spans={d['total_gt_spans']} density={d['density_spans_per_verse']:.4f}")

    print("\n=== F1 at Z per group (strict/token) ===")
    for model in MODELS:
        for criterion in CRITERIA:
            z = REPORT[model][criterion]["per_set"]["Z"]
            print(f"  {model}/{criterion}: abu_nuwas F1={z['abu_nuwas']['f1']:.3f} "
                  f"(tp={z['abu_nuwas']['tp']},fp={z['abu_nuwas']['fp']},fn={z['abu_nuwas']['fn']})  "
                  f"other F1={z['other']['f1']:.3f} "
                  f"(tp={z['other']['tp']},fp={z['other']['fp']},fn={z['other']['fn']})")

    print("\n=== Gain over Z (point [95% CI]) ===")
    for model in MODELS:
        for criterion in CRITERIA:
            for s in ["A", "B", "C"]:
                row = gains[model][criterion][s]
                an = row["abu_nuwas"]
                ot = row["other"]
                df = row["diff_abu_minus_other"]
                sig = "SIG" if (df["ci_95"][0] > 0 or df["ci_95"][1] < 0) else "ns"
                print(f"  {model}/{criterion}/{s}: abu_nuwas={an['point']:+.4f} [{an['ci_95'][0]:+.4f},{an['ci_95'][1]:+.4f}]  "
                      f"other={ot['point']:+.4f} [{ot['ci_95'][0]:+.4f},{ot['ci_95'][1]:+.4f}]  "
                      f"diff={df['point']:+.4f} [{df['ci_95'][0]:+.4f},{df['ci_95'][1]:+.4f}] ({sig})")


if __name__ == "__main__":
    main()
