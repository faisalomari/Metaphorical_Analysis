"""Generates the 4 result figures for the thesis writing chapters, pulling
every number live from the scoring harness (never hardcoded), saved as both
PDF and PNG to writing/figures/. Designed to be legible in grayscale: bars
use both distinct colors and distinct hatch patterns; markers use distinct
shapes in addition to color.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

import arabic_reshaper
from bidi.algorithm import get_display


def ar(text: str) -> str:
    """Reshape + bidi-reorder Arabic text for correct matplotlib rendering
    (matplotlib does not apply Arabic contextual letter-joining or RTL
    reordering on its own)."""
    return get_display(arabic_reshaper.reshape(text))

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ELEMENT_ORDER, MODELS, RESULTS_DIR, POEMS
from analyze import load_all_runs
from ground_truth import load_ground_truth_spans
from span_scoring import score_span_level
from test_report import pooled_counts, trope_subtype_breakdown  # noqa: F401 (breakdown reused via inline recompute below)
from per_verse_report import score_single_element_dir

FIG_DIR = Path(__file__).resolve().parents[2] / "writing" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

MODEL_ORDER = ["anthropic", "openai", "google"]
MODEL_LABEL = {p: MODELS[p]["display"] for p in MODEL_ORDER}
MODEL_COLOR = {"anthropic": "#4C4C4C", "openai": "#8C8C8C", "google": "#C4C4C4"}
MODEL_MARKER = {"anthropic": "o", "openai": "s", "google": "^"}
ELEMENT_LABEL = {"Trope": "Trope", "Simile": "Simile", "Kenning": "Kenning", "Antonymy": "Antonymy"}

plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "figure.dpi": 150,
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{name}.pdf")
    fig.savefig(FIG_DIR / f"{name}.png", dpi=200)
    plt.close(fig)
    print(f"wrote {name}.pdf / .png")


def fig1_baseline_vs_v4():
    strict_base = pooled_counts("baseline", "strict")
    strict_v4 = pooled_counts("v4_combined", "strict")

    fig, ax = plt.subplots(figsize=(9, 5))
    n_elements = len(ELEMENT_ORDER)
    group_width = 0.8
    bar_width = group_width / (len(MODEL_ORDER) * 2)
    x = range(n_elements)

    for mi, provider in enumerate(MODEL_ORDER):
        base_f1 = []
        v4_f1 = []
        for element in ELEMENT_ORDER:
            b = strict_base[provider][element]
            v = strict_v4[provider][element]
            bp = b["tp"] / (b["tp"] + b["fp"]) if (b["tp"] + b["fp"]) else 0
            br = b["tp"] / (b["tp"] + b["fn"]) if (b["tp"] + b["fn"]) else 0
            bf1 = 2 * bp * br / (bp + br) if (bp + br) else 0
            vp = v["tp"] / (v["tp"] + v["fp"]) if (v["tp"] + v["fp"]) else 0
            vr = v["tp"] / (v["tp"] + v["fn"]) if (v["tp"] + v["fn"]) else 0
            vf1 = 2 * vp * vr / (vp + vr) if (vp + vr) else 0
            base_f1.append(bf1)
            v4_f1.append(vf1)
        offset_base = (mi * 2) * bar_width - group_width / 2 + bar_width / 2
        offset_v4 = (mi * 2 + 1) * bar_width - group_width / 2 + bar_width / 2
        xs_base = [xi + offset_base for xi in x]
        xs_v4 = [xi + offset_v4 for xi in x]
        ax.bar(xs_base, base_f1, width=bar_width, color=MODEL_COLOR[provider],
               edgecolor="black", linewidth=0.5, label=f"{MODEL_LABEL[provider]} (baseline)")
        ax.bar(xs_v4, v4_f1, width=bar_width, color=MODEL_COLOR[provider],
               edgecolor="black", linewidth=0.5, hatch="///", label=f"{MODEL_LABEL[provider]} (v4_combined)")

    ax.set_xticks(list(x))
    ax.set_xticklabels([ELEMENT_LABEL[e] for e in ELEMENT_ORDER])
    ax.set_ylabel("F1 (strict criterion)")
    ax.set_title("Baseline vs. v4_combined, per element per model — frozen TEST, 2-run majority")
    ax.legend(fontsize=8, ncol=2, loc="upper right")
    ax.set_ylim(0, 0.85)
    return fig


def fig2_trope_subtypes():
    # recompute the pooled subtype miss-rate breakdown directly (same logic
    # as test_report.trope_subtype_breakdown, capturing values instead of printing)
    from config import TEST_POEMS
    from span_scoring import majority_exists_and_appearance
    from span_matching import strict_overlap
    from collections import Counter

    def breakdown(prompt_key):
        subtype_misses = Counter()
        subtype_totals = Counter()
        for poem_key in TEST_POEMS:
            out_dir = RESULTS_DIR / "test_final" / prompt_key / poem_key
            by_provider = load_all_runs(out_dir)
            gt = load_ground_truth_spans(poem_key)
            n_verses = POEMS[poem_key]["n_verses"]
            for verse_no in range(1, n_verses + 1):
                for inst in gt[verse_no]["Trope"]:
                    subtype = inst["secondary"] or inst["primary"]
                    subtype_totals[subtype] += 1
                    hit = False
                    for provider, runs in by_provider.items():
                        exists, appearance = majority_exists_and_appearance(runs, "Trope", verse_no)
                        if exists and strict_overlap(appearance or "", inst["span"]):
                            hit = True
                    if not hit:
                        subtype_misses[subtype] += 1
        return subtype_misses, subtype_totals

    base_miss, totals = breakdown("baseline")
    v4_miss, _ = breakdown("v4_combined")

    subtypes = [s for s, n in totals.most_common() if n >= 4]
    base_rate = [base_miss[s] / totals[s] * 100 for s in subtypes]
    v4_rate = [v4_miss[s] / totals[s] * 100 for s in subtypes]

    fig, ax = plt.subplots(figsize=(9, 5))
    y = range(len(subtypes))
    height = 0.35
    ax.barh([yi + height / 2 for yi in y], base_rate, height=height, color="#8C8C8C",
            edgecolor="black", linewidth=0.5, label="Baseline")
    ax.barh([yi - height / 2 for yi in y], v4_rate, height=height, color="#4C4C4C",
            edgecolor="black", linewidth=0.5, hatch="///", label="v4_combined")
    labels = [f"{ar(s)} (n={totals[s]})" for s in subtypes]
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("False-negative rate (% of ground-truth instances missed)")
    ax.set_title("Trope false-negative rate by ground-truth subtype, pooled TEST")
    ax.legend(loc="lower right")
    return fig


def fig3_kenning_grid():
    poem_key = "Imru2"
    n_verses = POEMS[poem_key]["n_verses"]
    gt_spans = load_ground_truth_spans(poem_key)

    v4_by_provider = load_all_runs(RESULTS_DIR / "dev_variants" / "v4_combined" / poem_key)
    a_by_provider = load_all_runs(RESULTS_DIR / "per_verse" / "mode_a" / poem_key)
    v4_strict = score_span_level(v4_by_provider, gt_spans, n_verses, "strict")
    a_strict = score_span_level(a_by_provider, gt_spans, n_verses, "strict")

    dec_dir = RESULTS_DIR / "dev_variants" / "decomposed_Kenning" / poem_key
    b_dir = RESULTS_DIR / "per_verse" / "mode_b_Kenning" / poem_key
    dec_counts, _ = score_single_element_dir(dec_dir, "Kenning", "strict")
    b_counts, _ = score_single_element_dir(b_dir, "Kenning", "strict")

    def f1_of(counts):
        tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
        p = tp / (tp + fp) if (tp + fp) else 0
        r = tp / (tp + fn) if (tp + fn) else 0
        return 2 * p * r / (p + r) if (p + r) else 0

    cells = ["Whole+All4\n(v4_combined)", "Whole+Single\n(decomposed)", "Verse+All4\n(Mode A)", "Verse+Single\n(Mode B)"]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(cells))
    width = 0.25
    for mi, provider in enumerate(MODEL_ORDER):
        vals = [
            v4_strict[provider]["Kenning"]["f1"],
            f1_of(dec_counts[provider]),
            a_strict[provider]["Kenning"]["f1"],
            f1_of(b_counts[provider]),
        ]
        offset = (mi - 1) * width
        xs = [xi + offset for xi in x]
        ax.bar(xs, vals, width=width, color=MODEL_COLOR[provider], edgecolor="black",
               linewidth=0.5, hatch=["", "//", "xx"][mi], label=MODEL_LABEL[provider])

    ax.set_xticks(list(x))
    ax.set_xticklabels(cells)
    ax.set_ylabel("Kenning F1 (strict criterion)")
    ax.set_title("Kenning across the granularity x decomposition grid — DEV (Imru2), 2-run majority")
    ax.legend()
    return fig


def fig4_precision_recall_scatter():
    strict_v4 = pooled_counts("v4_combined", "strict")
    fig, ax = plt.subplots(figsize=(7.5, 6.5))

    # manual per-(element,model) label offsets (dx, dy in points) to dodge
    # overlapping points/labels and the legend/annotation boxes
    offset_overrides = {
        ("Trope", "anthropic"): (8, -10),
        ("Simile", "openai"): (8, 8),
        ("Simile", "google"): (8, -10),
        ("Kenning", "google"): (-22, 6),
    }

    for provider in MODEL_ORDER:
        for element in ELEMENT_ORDER:
            c = strict_v4[provider][element]
            p = c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0
            r = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0
            ax.scatter(r, p, marker=MODEL_MARKER[provider], s=90,
                       color=MODEL_COLOR[provider], edgecolor="black", linewidth=0.6, zorder=3)
            dx, dy = offset_overrides.get((element, provider), (7, 5))
            ax.annotate(element[:2], (r, p), textcoords="offset points", xytext=(dx, dy), fontsize=8)

    ax.axhspan(0, 0.35, color="#ececec", zorder=0)
    ax.text(0.51, 0.02, "low precision (over-claiming: Antonymy)", fontsize=8, color="#555555",
            ha="center", va="bottom")
    ax.axvspan(0, 0.30, color="#f5f5f5", zorder=0)
    ax.text(0.15, 0.98, "low recall\n(under-detection:\nTrope, Kenning)", fontsize=8, color="#555555",
            ha="center", va="top")

    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker=MODEL_MARKER[p], color="w", markerfacecolor=MODEL_COLOR[p],
                       markeredgecolor="black", markersize=9, label=MODEL_LABEL[p]) for p in MODEL_ORDER]
    ax.legend(handles=handles, loc="lower right", fontsize=8, framealpha=0.95)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title("Precision vs. recall, v4_combined, all elements x models — frozen TEST")
    return fig


if __name__ == "__main__":
    save(fig1_baseline_vs_v4(), "f1_test_baseline_vs_v4")
    save(fig2_trope_subtypes(), "f2_trope_subtype_miss_rates")
    save(fig3_kenning_grid(), "f3_kenning_granularity_grid")
    save(fig4_precision_recall_scatter(), "f4_precision_recall_scatter")
