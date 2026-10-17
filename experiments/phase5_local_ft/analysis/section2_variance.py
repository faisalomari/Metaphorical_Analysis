"""Section 2: variance. Bootstrap 95% CI over poems (test F1) per target x model
(S2, S3 where it exists), seed-to-seed std (from Section 1), and which
between-target differences are NOT statistically distinguishable (CI overlap).
Also a pooled-across-3-models-per-target CI (since the user's question is about
target difficulty, not one model), using S2 (primary split).
"""
import json
import random
import statistics as stats
from itertools import combinations

from common import ANALYSIS_OUT, LEVEL_ORDER, MODEL_KEYS, SEEDS, TARGETS_BY_LEVEL, load_run
from metrics_utils import prf

N_BOOT = 2000
BOOT_SEED = 0


def bootstrap_ci_over_poems(runs, n_boot=N_BOOT, seed=BOOT_SEED):
    by_poem = {}
    for run in runs:
        for p in run["predictions"]:
            by_poem.setdefault(p["poem_id"], []).append((p["label"], p["pred"]))
    poem_ids = list(by_poem)
    if not poem_ids:
        return None
    rng = random.Random(seed)
    f1s = []
    for _ in range(n_boot):
        sample = rng.choices(poem_ids, k=len(poem_ids))
        y_true, y_pred = [], []
        for pid in sample:
            for lab, pred in by_poem[pid]:
                y_true.append(lab)
                y_pred.append(pred)
        f1s.append(prf(y_true, y_pred)["f1"])
    f1s.sort()
    point = prf([lab for pid in poem_ids for lab, _ in by_poem[pid]],
                [pred for pid in poem_ids for _, pred in by_poem[pid]])["f1"]
    return {"point": point, "ci_low": f1s[int(0.025 * n_boot)], "ci_high": f1s[int(0.975 * n_boot) - 1],
            "n_boot": n_boot, "n_poems": len(poem_ids)}


def overlap(ci_a, ci_b):
    return not (ci_a["ci_high"] < ci_b["ci_low"] or ci_b["ci_high"] < ci_a["ci_low"])


def build():
    out = {"per_model": {}, "pooled_per_target": {}, "not_distinguishable_pairs": {}}
    md = ["## Section 2 — Variance: bootstrap 95% CI (over poems) and seed-to-seed std\n"]

    for split_name in ("S2", "S3"):
        levels = ["medium"] if split_name == "S3" else LEVEL_ORDER
        md.append(f"\n### {split_name} — per model\n")
        md.append("| Level | Model | point F1 (pooled 3 seeds) | 95% CI | n_poems (pooled, w/ repeats across seeds) | seed-to-seed F1 std |")
        md.append("|---|---|---|---|---|---|")
        out["per_model"][split_name] = {}
        for level in levels:
            out["per_model"][split_name][level] = {}
            for model_key in MODEL_KEYS:
                runs = [load_run(level, model_key, split_name, s) for s in SEEDS]
                runs = [r for r in runs if r is not None]
                if not runs:
                    continue
                ci = bootstrap_ci_over_poems(runs)
                seed_std = stats.pstdev([r["test_metrics"]["f1"] for r in runs]) if len(runs) > 1 else 0.0
                out["per_model"][split_name][level][model_key] = {**ci, "seed_std": seed_std}
                md.append(f"| {level} | {model_key} | {ci['point']:.3f} | [{ci['ci_low']:.3f},{ci['ci_high']:.3f}] | "
                          f"{ci['n_poems']} | {seed_std:.3f} |")

        # pooled across 3 models (micro-pool predictions from all models+seeds) per target
        md.append(f"\n### {split_name} — pooled across all 3 models (per-target overall picture)\n")
        md.append("| Level (subtype) | point F1 | 95% CI |")
        md.append("|---|---|---|")
        out["pooled_per_target"][split_name] = {}
        for level in levels:
            all_runs = []
            for model_key in MODEL_KEYS:
                all_runs += [r for r in (load_run(level, model_key, split_name, s) for s in SEEDS) if r is not None]
            if not all_runs:
                continue
            ci = bootstrap_ci_over_poems(all_runs)
            out["pooled_per_target"][split_name][level] = ci
            md.append(f"| {level} ({TARGETS_BY_LEVEL[level]['value']}) | {ci['point']:.3f} | "
                      f"[{ci['ci_low']:.3f},{ci['ci_high']:.3f}] |")

        # which between-target differences are NOT distinguishable (pooled CIs overlap), S2 only (has all 5)
        if split_name == "S2":
            md.append(f"\n### {split_name} — pairwise target comparisons: CI overlap = NOT statistically distinguishable\n")
            md.append("| Target A | Target B | A CI | B CI | Overlap? |")
            md.append("|---|---|---|---|---|")
            pairs_not_distinguishable = []
            for a, b in combinations(levels, 2):
                ci_a = out["pooled_per_target"][split_name].get(a)
                ci_b = out["pooled_per_target"][split_name].get(b)
                if not ci_a or not ci_b:
                    continue
                ov = overlap(ci_a, ci_b)
                if ov:
                    pairs_not_distinguishable.append((a, b))
                md.append(f"| {a} | {b} | [{ci_a['ci_low']:.3f},{ci_a['ci_high']:.3f}] | "
                          f"[{ci_b['ci_low']:.3f},{ci_b['ci_high']:.3f}] | {'YES -- overlap' if ov else 'no overlap'} |")
            out["not_distinguishable_pairs"][split_name] = pairs_not_distinguishable

    (ANALYSIS_OUT / "section2_variance.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_text = "\n".join(md)
    (ANALYSIS_OUT / "section2_variance.md").write_text(md_text, encoding="utf-8")
    print(md_text)


if __name__ == "__main__":
    build()
