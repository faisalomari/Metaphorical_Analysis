"""Phase 2 sec3i report: pooled DEV comparison (existing Sonnet+v4 vs Config
A vs Config B) and an Imru2-only comparison that adds Config C, plus the
verse-6 (Imru2) qualitative check for the motivating كناية/periphrasis
observation. Reuses Phase 1's analyze.load_all_runs / span_scoring.score_span_level
unmodified - this script only wires directories + provider filters together.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))

from config import ELEMENT_ORDER, POEMS  # noqa: E402
from analyze import load_all_runs, prf1  # noqa: E402
from ground_truth import load_ground_truth_spans  # noqa: E402
from span_scoring import score_span_level, majority_exists_and_appearance  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
P1_RESULTS = ROOT / "results" / "pilot_3models"
P2_RESULTS = ROOT / "results" / "phase2_chatlike"

EXISTING_DIRS = {
    "Imru2": P1_RESULTS / "dev_variants" / "v4_combined" / "Imru2",
    "Nabigha": P1_RESULTS / "dev_variants" / "v4_combined" / "Nabigha",
}
CONFIG_A_DIRS = {"Imru2": P2_RESULTS / "config_a" / "Imru2", "Nabigha": P2_RESULTS / "config_a" / "Nabigha"}
CONFIG_B_DIRS = {"Imru2": P2_RESULTS / "config_b" / "Imru2", "Nabigha": P2_RESULTS / "config_b" / "Nabigha"}
CONFIG_C_DIRS = {"Imru2": P2_RESULTS / "config_c" / "Imru2"}


def pooled_counts(dirs: dict, provider: str, criterion: str) -> dict:
    pooled = {el: {"tp": 0, "fp": 0, "fn": 0} for el in ELEMENT_ORDER}
    for poem_key, out_dir in dirs.items():
        by_provider = load_all_runs(out_dir)
        if provider not in by_provider:
            continue
        gt_spans = load_ground_truth_spans(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]
        scores = score_span_level({provider: by_provider[provider]}, gt_spans, n_verses, criterion)
        for el in ELEMENT_ORDER:
            for k in ("tp", "fp", "fn"):
                pooled[el][k] += scores[provider][el][k]
    return pooled


def print_table(title: str, columns: list):
    """columns: list of (label, dirs, provider)"""
    print(f"\n{'#'*130}\n# {title}\n{'#'*130}")
    for criterion in ["strict", "token"]:
        print(f"\n--- criterion={criterion} ---")
        header = f"{'Element':<10}" + "".join(f"{label:>34}" for label, _, _ in columns)
        print(header)
        computed = {label: pooled_counts(dirs, provider, criterion) for label, dirs, provider in columns}
        for el in ELEMENT_ORDER:
            row = f"{el:<10}"
            for label, _, _ in columns:
                c = computed[label][el]
                s = prf1(c["tp"], c["fp"], c["fn"])
                row += f"{c['tp']:>3}/{c['fp']:>3}/{c['fn']:>3} F1={s['f1']:.3f}".rjust(34)
            print(row)


def verse_check(verse_no: int = 6, poem_key: str = "Imru2"):
    print(f"\n{'#'*130}\n# Verse-specific check: {poem_key} verse {verse_no} (the motivating كناية/periphrasis observation)\n{'#'*130}")
    verse_line = [ln for ln in POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip().split("\n") if ln.strip()][verse_no - 1]
    print(f"\nVerse text: {verse_line}")

    gt = load_ground_truth_spans(poem_key)[verse_no]
    print("\nGround truth (Dr. Ali Hussein's annotation):")
    for el in ELEMENT_ORDER:
        insts = gt[el]
        if insts:
            print(f"  {el}: " + "; ".join(f"'{i['span']}' ({i['primary']}/{i['secondary']})" for i in insts))
        else:
            print(f"  {el}: (none)")

    checks = [
        ("Existing (Sonnet 4.6 + v4_combined, Phase 1 frozen)", EXISTING_DIRS, "anthropic"),
        ("Config A (Fable 5 + v4_combined unchanged)", CONFIG_A_DIRS, "anthropic_fable5"),
        ("Config B (Sonnet 4.6 + terminology-corrected v4)", CONFIG_B_DIRS, "anthropic"),
        ("Config C (Fable 5 stage1 + GPT-5.4-mini stage2)", CONFIG_C_DIRS, "config_c"),
    ]
    print()
    for label, dirs, provider in checks:
        out_dir = dirs.get(poem_key)
        if out_dir is None or not out_dir.exists():
            print(f"{label}: (no data for {poem_key})")
            continue
        by_provider = load_all_runs(out_dir)
        runs = by_provider.get(provider, [])
        print(f"\n{label}:")
        for el in ELEMENT_ORDER:
            exists, appearance = majority_exists_and_appearance(runs, el, verse_no)
            print(f"  {el}: exists={exists} appearance={appearance!r}")

    # Config C stage 1's full free-form analysis text for this verse, both runs
    print(f"\n--- Config C stage-1 full analysis text for verse {verse_no} (both runs) ---")
    for run_idx in (1, 2):
        p = CONFIG_C_DIRS["Imru2"] / f"stage1_analysis_run{run_idx}.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        rec = next((r for r in data if r["verse_no"] == verse_no), None)
        print(f"\n=== run {run_idx} ===")
        if rec:
            print(rec["analysis"])
        else:
            print("(no record)")


if __name__ == "__main__":
    print_table(
        "Pooled DEV (Imru2+Nabigha) — Existing (Sonnet+v4, frozen) vs Config A vs Config B",
        [
            ("Existing (Sonnet+v4)", EXISTING_DIRS, "anthropic"),
            ("Config A (Fable5+v4)", CONFIG_A_DIRS, "anthropic_fable5"),
            ("Config B (Sonnet+v4-term)", CONFIG_B_DIRS, "anthropic"),
        ],
    )
    print_table(
        "Imru2-only — Existing vs A vs B (re-sliced) vs Config C",
        [
            ("Existing (Sonnet+v4)", {"Imru2": EXISTING_DIRS["Imru2"]}, "anthropic"),
            ("Config A (Fable5+v4)", {"Imru2": CONFIG_A_DIRS["Imru2"]}, "anthropic_fable5"),
            ("Config B (Sonnet+v4-term)", {"Imru2": CONFIG_B_DIRS["Imru2"]}, "anthropic"),
            ("Config C (2-stage)", CONFIG_C_DIRS, "config_c"),
        ],
    )
    verse_check(6, "Imru2")
