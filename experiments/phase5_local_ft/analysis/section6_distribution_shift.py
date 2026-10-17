"""Section 6: distribution shift. Per-target F1 by poet and by period on S2
test (MARBERT, pooled 3 seeds), train/test poet overlap per split/seed, and
whether positives for the 5 targets are concentrated in a few poets/poems
(corpus-wide, not split-dependent). No training, no API calls.
"""
import json
from collections import defaultdict

from common import ANALYSIS_OUT, LEVEL_ORDER, SEEDS, TARGETS_BY_LEVEL, get_poem, load_run, split_poem_ids
from data_io import list_poem_files, load_poem, positive_verses_by_subtype
from metrics_utils import prf

MODEL_KEY = "marbert"
SPLIT_NAME = "S2"
MIN_VERSES_FOR_POET_CELL = 15


def poet_and_period(poem_id):
    poem = get_poem(poem_id)
    return poem.get("poet_name"), poem.get("period")


def per_poet_period_f1(level):
    runs = [load_run(level, MODEL_KEY, SPLIT_NAME, s) for s in SEEDS]
    runs = [r for r in runs if r is not None]
    by_poet = defaultdict(list)
    by_period = defaultdict(list)
    for r in runs:
        for p in r["predictions"]:
            poet, period = poet_and_period(p["poem_id"])
            by_poet[poet].append((p["label"], p["pred"]))
            by_period[period].append((p["label"], p["pred"]))

    poet_rows = []
    for poet, items in by_poet.items():
        if len(items) < MIN_VERSES_FOR_POET_CELL:
            continue
        y_true = [a for a, _ in items]
        y_pred = [b for _, b in items]
        m = prf(y_true, y_pred)
        if m["tp"] + m["fn"] == 0:
            continue  # no positives for this poet in test -- F1 undefined/not meaningful
        poet_rows.append({"poet": poet, "n_verses": len(items), "n_pos": sum(y_true), **m})
    poet_rows.sort(key=lambda r: -r["n_pos"])

    period_rows = []
    for period, items in by_period.items():
        y_true = [a for a, _ in items]
        y_pred = [b for _, b in items]
        m = prf(y_true, y_pred)
        period_rows.append({"period": period, "n_verses": len(items), "n_pos": sum(y_true), **m})
    period_rows.sort(key=lambda r: -r["n_pos"])

    return poet_rows, period_rows


def poet_overlap():
    rows = []
    for split_name in ("S1", "S2", "S3"):
        for seed in SEEDS:
            ids = split_poem_ids(split_name, seed)
            train_poets = {poet_and_period(pid)[0] for pid in ids["train"]}
            test_poets_per_poem = [poet_and_period(pid)[0] for pid in ids["test"]]
            n_test = len(test_poets_per_poem)
            n_overlap = sum(1 for p in test_poets_per_poem if p in train_poets)
            rows.append({
                "split": split_name, "seed": seed,
                "n_test_poems": n_test, "n_test_poems_poet_in_train": n_overlap,
                "pct_test_poems_poet_in_train": n_overlap / n_test if n_test else None,
                "n_test_poems_poet_UNSEEN": n_test - n_overlap,
            })
    return rows


def concentration(level, top_k=5):
    target_value = TARGETS_BY_LEVEL[level]["value"]
    all_poems = [load_poem(f) for f in list_poem_files()]
    by_poet = defaultdict(int)
    by_poem = defaultdict(int)
    total = 0
    for poem in all_poems:
        pos = positive_verses_by_subtype(poem).get(target_value, set())
        n = len(pos)
        if n:
            by_poet[poem.get("poet_name")] += n
            by_poem[str(poem["poem_id"])] += n
            total += n
    top_poets = sorted(by_poet.items(), key=lambda kv: -kv[1])[:top_k]
    top_poems = sorted(by_poem.items(), key=lambda kv: -kv[1])[:top_k]
    top_poets_share = sum(c for _, c in top_poets) / total if total else None
    top_poems_share = sum(c for _, c in top_poems) / total if total else None
    return {
        "target": target_value, "total_positive_verses": total,
        "n_distinct_poets_with_positive": len(by_poet), "n_distinct_poems_with_positive": len(by_poem),
        f"top{top_k}_poets": top_poets, f"top{top_k}_poets_share_of_total": top_poets_share,
        f"top{top_k}_poems": top_poems, f"top{top_k}_poems_share_of_total": top_poems_share,
    }


def build():
    out = {"per_poet_period": {}, "poet_overlap": poet_overlap(), "concentration": {}}
    md = ["## Section 6 — Distribution shift\n"]

    md.append("### Train/test poet overlap (every split x seed)\n")
    md.append("| split | seed | n_test_poems | poet seen in train | poet UNSEEN in train | %% poet-in-train |")
    md.append("|---|---|---|---|---|---|")
    for row in out["poet_overlap"]:
        md.append(f"| {row['split']} | {row['seed']} | {row['n_test_poems']} | "
                  f"{row['n_test_poems_poet_in_train']} | {row['n_test_poems_poet_UNSEEN']} | "
                  f"{row['pct_test_poems_poet_in_train']*100:.1f}% |")

    md.append("\n### Per-target positive-verse concentration (corpus-wide, all 166 poems)\n")
    md.append("| Level (subtype) | total pos verses | distinct poets w/ positive | distinct poems w/ positive | "
              "top-5 poets' share | top-5 poems' share |")
    md.append("|---|---|---|---|---|---|")
    for level in LEVEL_ORDER:
        c = concentration(level)
        out["concentration"][level] = c
        md.append(f"| {level} ({c['target']}) | {c['total_positive_verses']} | {c['n_distinct_poets_with_positive']} | "
                  f"{c['n_distinct_poems_with_positive']} | {c['top5_poets_share_of_total']*100:.1f}% | "
                  f"{c['top5_poems_share_of_total']*100:.1f}% |")
    md.append("\nTop-5 poets by positive-verse count, per target:\n")
    for level in LEVEL_ORDER:
        c = out["concentration"][level]
        md.append(f"- **{level}**: {c['top5_poets']}")

    md.append("\n### Per-poet F1 on S2 test (MARBERT, pooled 3 seeds, poets with >=15 pooled test verses only)\n")
    md.append("### Per-period F1 on S2 test (MARBERT, pooled 3 seeds)\n")
    for level in LEVEL_ORDER:
        poet_rows, period_rows = per_poet_period_f1(level)
        out["per_poet_period"][level] = {"by_poet": poet_rows, "by_period": period_rows}
        md.append(f"\n**{level} ({TARGETS_BY_LEVEL[level]['value']})** -- by poet (>=15 pooled test verses, has >=1 positive):")
        md.append("| poet | n_verses | n_pos | TP | FP | FN | precision | recall | F1 |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for r in poet_rows:
            md.append(f"| {r['poet']} | {r['n_verses']} | {r['n_pos']} | {r['tp']} | {r['fp']} | {r['fn']} | "
                      f"{r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |")
        md.append(f"\n**{level}** -- by period:")
        md.append("| period | n_verses | n_pos | TP | FP | FN | precision | recall | F1 |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for r in period_rows:
            md.append(f"| {r['period']} | {r['n_verses']} | {r['n_pos']} | {r['tp']} | {r['fp']} | {r['fn']} | "
                      f"{r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |")

    (ANALYSIS_OUT / "section6_distribution_shift.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md_text = "\n".join(md)
    (ANALYSIS_OUT / "section6_distribution_shift.md").write_text(md_text, encoding="utf-8")
    print(md_text[:6000])


if __name__ == "__main__":
    build()
