"""Builds docs/phase4/ALL_RESULTS.xlsx -- one workbook consolidating every
result shown in docs/phase4/E1_V2_REPORT.html, EXCLUDING Phase 5-6 (local
fine-tuning).

NO API calls. Does not edit any existing results/code file. Every number is
computed from the existing manifests/JSON via the project's own scorers --
never hand-typed -- with one declared exception: Phase 1's frozen Trope TEST
TP/FP/FN (PROJECT_STATE.md section 3a, prose not JSON), copied the same way
build_e1v2_report.py's PHASE1_TROPE_TEST already does, and verified against
PROJECT_STATE.md's own text before use (see verify_phase1_numbers below).

Reuses, unchanged: experiments/phase4_e1_v2/ensemble_v2.py (build_parsed_cache,
score_set_single_model, score_poem_single_model, gt_v2.gt_spans_for_subtype,
ali_poems_io.load_poem_json, pilot_3models.analyze.prf1) and
experiments/phase7_subtypes/score_phase7.py (load_manifests, build_cell_index)
for every TP/FP/FN pulled from a cache. Adds ONLY new generic k-of-n ensemble
combination scorers (score_set_combo_e1v2 / score_set_combo_p7) needed for the
"Top 3 models ENSEMBLE" rows, which no existing script computes -- declared in
their own docstrings below. All other combination numbers (2-of-3 majority,
GPT-Z OR/AND Claude-FS) reuse pre-computed results/phase4_e1_v2/
analysis_report_ensemble.json, results/phase4_e1_v2/design_choice/
analysis_report_design_choice.json, and results/phase7_subtypes/
analysis_report_phase7.json where available, cross-checked against a fresh
cache-based recomputation (see verify_* functions).

Primary metric throughout: VERSE-LEVEL ONLY (per this task's instruction).
CLAUDE.md rule 4 standing caveat (verse-level alone can reward exists=True
regardless of span correctness) is stated once, prominently, in the Notes
sheet and in every top-info block.

Run: python scripts/build_results_excel.py
Writes: docs/phase4/ALL_RESULTS.xlsx
"""
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "phase4_e1_v2"))
sys.path.insert(0, str(ROOT / "experiments" / "phase7_subtypes"))

import ensemble_v2 as ens2            # noqa: E402  (also wires e1v1/pilot dirs onto sys.path)
import e1v2_config                    # noqa: E402  (already cached by ensemble_v2's own import)
import score_phase7 as p7             # noqa: E402
from experiments.pilot_3models import config as pilot_config  # noqa: E402

DOCS_DIR = ROOT / "docs" / "phase4"
OUT_PATH = DOCS_DIR / "ALL_RESULTS.xlsx"
E1V2_DIR = ROOT / "experiments" / "phase4_e1_v2"
RESULTS_DIR = ens2.RESULTS_DIR                      # results/phase4_e1_v2
P7_RESULTS_DIR = p7.RESULTS_DIR                      # results/phase7_subtypes
PROJECT_STATE_PATH = ROOT / "PROJECT_STATE.md"
TOP5_BLOCKERS_PATH = ROOT / "writing" / "paper_plan" / "TOP_5_BLOCKERS.md"

PRICING = {**pilot_config.MODELS, **e1v2_config.EXTRA_MODEL_PRICING}
MODEL_SHORT = {"anthropic": "Claude", "openai": "GPT", "google": "Gemini", "anthropic_opus": "Opus 5.5"}
MODELS3 = ["anthropic", "openai", "google"]

VERSE_PRIMARY_NOTE = ("Verse = primary metric (user decision). CLAUDE.md rule 4 caveat: "
                       "verse-level alone can reward exists=True regardless of whether the "
                       "predicted span is actually correct -- see Notes sheet.")


# ---------------------------------------------------------------------------
# Generic k-of-n combination scorers (the one new piece of scoring math this
# script adds -- everything else reuses ensemble_v2.py / score_phase7.py
# functions unchanged). Verse-level only, per this task's instruction.
# ---------------------------------------------------------------------------

def score_poem_combo_e1v2(cache, cells, poem_id, n_verses, gt_spans, threshold):
    """cells: list of (set_name, provider) pairs. A verse is predicted
    positive iff >=`threshold` of those cells returned exists=True (a missing
    or unparseable cell is a non-vote, same convention ensemble_v2.py's own
    2-of-3 ensemble already uses)."""
    tp = fp = fn = 0
    for verse_no in range(1, n_verses + 1):
        votes = 0
        for set_name, provider in cells:
            parsed = cache.get((set_name, poem_id, verse_no, provider))
            if parsed is not None and parsed.get("exists") is True:
                votes += 1
        exists = votes >= threshold
        gt_texts = gt_spans[verse_no]
        if exists and gt_texts:
            tp += 1
        elif exists and not gt_texts:
            fp += 1
        elif not exists and gt_texts:
            fn += 1
    return tp, fp, fn


def score_set_combo_e1v2(cache, pool, cells, threshold):
    tp = fp = fn = 0
    for poem in pool:
        pid = poem["poem_id"]
        pj = ens2.load_poem_json(pid)
        gt = ens2.gt_spans_for_subtype(pj)
        t, f, n = score_poem_combo_e1v2(cache, cells, pid, pj["verse_count"], gt, threshold)
        tp += t
        fp += f
        fn += n
    return {"tp": tp, "fp": fp, "fn": fn, **ens2.prf1(tp, fp, fn)}


def score_poem_combo_p7(cell_index, subtype, cells, poem_id, gt_poem, threshold):
    """cells: list of (condition, provider) pairs, same voting rule as above."""
    tp = fp = fn = 0
    for verse_no in range(1, gt_poem["n_verses"] + 1):
        votes = 0
        for condition, provider in cells:
            parsed = cell_index.get((subtype, condition, poem_id, verse_no, provider))
            if parsed is not None and parsed.get("exists") is True:
                votes += 1
        exists = votes >= threshold
        gt_texts = gt_poem["by_verse"][verse_no]
        if exists and gt_texts:
            tp += 1
        elif exists and not gt_texts:
            fp += 1
        elif not exists and gt_texts:
            fn += 1
    return tp, fp, fn


def score_set_combo_p7(cell_index, subtype, pool_poem_ids, gt, cells, threshold):
    tp = fp = fn = 0
    for pid in pool_poem_ids:
        t, f, n = score_poem_combo_p7(cell_index, subtype, cells, pid, gt[pid], threshold)
        tp += t
        fp += f
        fn += n
    return {"tp": tp, "fp": fp, "fn": fn, **ens2.prf1(tp, fp, fn)}


def call_cost(provider, usage):
    spec = PRICING[provider]
    usage = usage or {}
    return (usage.get("input_tokens", 0) / 1e6) * spec["price_in"] + \
           (usage.get("output_tokens", 0) / 1e6) * spec["price_out"]


def is_ar(text) -> bool:
    text = str(text)
    ar = len(re.findall(r"[؀-ۿ]", text))
    total = len(re.findall(r"\S", text))
    return total > 0 and ar / total > 0.5


def pool_positive_count(pool):
    total = 0
    for poem in pool:
        pj = ens2.load_poem_json(poem["poem_id"])
        gt = ens2.gt_spans_for_subtype(pj)
        total += sum(1 for v in gt.values() if v)
    return total


# ---------------------------------------------------------------------------
# Shared data loads (E1 v2 family: core / eras / quartile / multipoet / opus
# all share one run_manifest.json + raw dir under results/phase4_e1_v2/).
# ---------------------------------------------------------------------------

print("Loading results/phase4_e1_v2/run_manifest.json and building parsed cache ...")
E1V2_MANIFEST = json.loads((RESULTS_DIR / "run_manifest.json").read_text(encoding="utf-8"))
E1V2_CACHE = ens2.build_parsed_cache(E1V2_MANIFEST, RESULTS_DIR)

_pool25_doc = json.loads(ens2.EVAL_POOL_25_PATH.read_text(encoding="utf-8"))
POOL25 = _pool25_doc["poems"]
POOL25_VERSES = _pool25_doc["pool_verses"]

_pool50_doc = json.loads((E1V2_DIR / "config" / "eval_pool_50_multipoet.json").read_text(encoding="utf-8"))
POOL50 = _pool50_doc["poems"]
POOL50_VERSES = _pool50_doc["pool_verses"]

ANALYSIS_ENSEMBLE = json.loads((RESULTS_DIR / "analysis_report_ensemble.json").read_text(encoding="utf-8"))
DESIGN_CHOICE = json.loads((RESULTS_DIR / "design_choice" / "analysis_report_design_choice.json").read_text(encoding="utf-8"))
ANALYSIS_OPUS_A = json.loads((RESULTS_DIR / "analysis_report_opus_a.json").read_text(encoding="utf-8"))

print("Loading results/phase7_subtypes manifests and building cell index ...")
P7_MANIFEST = p7.load_manifests()
P7_CELL_INDEX = p7.build_cell_index(P7_MANIFEST)
ANALYSIS_PHASE7 = json.loads((P7_RESULTS_DIR / "analysis_report_phase7.json").read_text(encoding="utf-8"))
P7_POOL_POEM_IDS = json.loads(p7.EVAL_POOL_25_PATH.read_text(encoding="utf-8"))["poem_ids"]

print(f"E1v2 cache: {len(E1V2_CACHE)} cells. Phase7 cell index: {len(P7_CELL_INDEX)} cells.")


def single_row(cache_overall_fn, pool, set_name, provider, extra_note=""):
    r = cache_overall_fn(pool, set_name, provider)
    return {"kind": "data", "label": f"{MODEL_SHORT[provider]} / {set_name}", "tp": r["tp"],
            "fp": r["fp"], "fn": r["fn"], "precision": r["precision"], "recall": r["recall"],
            "f1": r["f1"], "extra_note": extra_note, "group": "single"}


def e1v2_single(pool, set_name, provider):
    return ens2.score_set_single_model(E1V2_CACHE, pool, set_name, provider, "verse")["overall"]


def p7_single(subtype, condition, provider, gt, pool_poem_ids):
    return ANALYSIS_PHASE7["subtypes"][subtype]["by_model"][provider][condition]["verse"]


# ===========================================================================
# Excel writing helpers
# ===========================================================================

FONT_NAME = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
SECTION_FONT = Font(name=FONT_NAME, bold=True, italic=True)
MEAN_FILL = PatternFill("solid", fgColor="FFF2CC")
MEAN_FONT = Font(name=FONT_NAME, bold=True, italic=True)
BEST_FILL = PatternFill("solid", fgColor="C6EFCE")
NOTE_FONT = Font(name=FONT_NAME, italic=True, color="808080")
PLAIN_FONT = Font(name=FONT_NAME)
BOLD_FONT = Font(name=FONT_NAME, bold=True)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
NUM_FMT = "0.000"

COLS = ["Model/Condition", "TP", "FP", "FN", "TN", "P", "R", "F1", "Notes"]


def _set_cell(ws, r, c, value, font=None, fill=None, align=None, numfmt=None, border=True):
    cell = ws.cell(r, c, value)
    cell.font = font or PLAIN_FONT
    if fill:
        cell.fill = fill
    if align:
        cell.alignment = align
    elif isinstance(value, str) and is_ar(value):
        cell.alignment = Alignment(horizontal="right")
    if numfmt:
        cell.number_format = numfmt
    if border:
        cell.border = BORDER
    return cell


INFO_VALUE_LAST_COL = 9      # merge the value cell across B..I (the same width as the table below)
INFO_CHARS_PER_LINE = 118    # rough capacity of the merged B..I span at Arial 10, for row-height sizing


def write_info_block(ws, lines, start_row=1):
    r = start_row
    for label, value in lines:
        _set_cell(ws, r, 1, label, font=BOLD_FONT, border=False)
        ws.cell(r, 1).alignment = Alignment(vertical="top")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=INFO_VALUE_LAST_COL)
        cell = ws.cell(r, 2, value)
        cell.font = PLAIN_FONT
        horiz = "right" if is_ar(str(value)) else "left"
        cell.alignment = Alignment(horizontal=horiz, vertical="top", wrap_text=True)
        n_lines = max(1, -(-len(str(value)) // INFO_CHARS_PER_LINE))  # ceil division
        ws.row_dimensions[r].height = max(15, n_lines * 15)
        r += 1
    return r


def write_table(ws, rows, total_verse_units, header_row):
    for c, h in enumerate(COLS, start=1):
        _set_cell(ws, header_row, c, h, font=HEADER_FONT, fill=HEADER_FILL,
                  align=Alignment(horizontal="center"))
    r = header_row + 1
    row_excel_pos = {}
    group_rows = {}  # group -> list of (excel_row, f1_python_value)
    for i, row in enumerate(rows):
        row_excel_pos[i] = r
        kind = row["kind"]
        _set_cell(ws, r, 1, row["label"], font=MEAN_FONT if kind == "mean" else
                  (SECTION_FONT if kind == "section" else PLAIN_FONT))
        if kind == "section":
            for c in range(2, 10):
                _set_cell(ws, r, c, "", fill=SECTION_FILL)
            r += 1
            continue
        if kind == "note":
            _set_cell(ws, r, 2, "N/A")
            for c in range(3, 9):
                _set_cell(ws, r, c, "")
            _set_cell(ws, r, 9, row.get("extra_note", ""))
            r += 1
            continue
        if kind == "data":
            _set_cell(ws, r, 2, row["tp"])
            _set_cell(ws, r, 3, row["fp"])
            _set_cell(ws, r, 4, row["fn"])
            _set_cell(ws, r, 5, f"={total_verse_units}-B{r}-C{r}-D{r}")
            _set_cell(ws, r, 6, f"=IFERROR(B{r}/(B{r}+C{r}),0)", numfmt=NUM_FMT)
            _set_cell(ws, r, 7, f"=IFERROR(B{r}/(B{r}+D{r}),0)", numfmt=NUM_FMT)
            _set_cell(ws, r, 8, f"=IFERROR(2*F{r}*G{r}/(F{r}+G{r}),0)", numfmt=NUM_FMT)
            _set_cell(ws, r, 9, row.get("extra_note", ""))
            group_rows.setdefault(row.get("group", "default"), []).append((r, row["f1"]))
        elif kind == "mean":
            src = [row_excel_pos[j] for j in row["source_rows"]]
            tpc = ",".join(f"B{x}" for x in src)
            fpc = ",".join(f"C{x}" for x in src)
            fnc = ",".join(f"D{x}" for x in src)
            pc = ",".join(f"F{x}" for x in src)
            rc = ",".join(f"G{x}" for x in src)
            fc = ",".join(f"H{x}" for x in src)
            _set_cell(ws, r, 2, f"=AVERAGE({tpc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt="0.0")
            _set_cell(ws, r, 3, f"=AVERAGE({fpc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt="0.0")
            _set_cell(ws, r, 4, f"=AVERAGE({fnc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt="0.0")
            _set_cell(ws, r, 5, f"={total_verse_units}-B{r}-C{r}-D{r}", font=MEAN_FONT, fill=MEAN_FILL, numfmt="0.0")
            _set_cell(ws, r, 6, f"=AVERAGE({pc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt=NUM_FMT)
            _set_cell(ws, r, 7, f"=AVERAGE({rc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt=NUM_FMT)
            _set_cell(ws, r, 8, f"=AVERAGE({fc})", font=MEAN_FONT, fill=MEAN_FILL, numfmt=NUM_FMT)
            _set_cell(ws, r, 9, row.get("extra_note", ""), font=MEAN_FONT, fill=MEAN_FILL)
            _set_cell(ws, r, 1, row["label"], font=MEAN_FONT, fill=MEAN_FILL)
        r += 1
    # Highlight best F1 per group (data rows only)
    for group, items in group_rows.items():
        if not items:
            continue
        best_row = max(items, key=lambda x: x[1])[0]
        for c in range(1, 9):
            ws.cell(best_row, c).fill = BEST_FILL
    return r


def new_sheet(wb, name, info_lines, rows, total_verse_units, col_widths=None):
    ws = wb.create_sheet(title=name[:31])
    last_info_row = write_info_block(ws, info_lines)
    header_row = last_info_row + 1
    last_row = write_table(ws, rows, total_verse_units, header_row)
    widths = col_widths or [34, 7, 7, 7, 7, 8, 8, 8, 70]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return ws, header_row, last_row


# ===========================================================================
# Sheet 1 -- E1 v2 core, 25-poem pool, استعارة فعل (Z, A, B, C, D, D2)
# ===========================================================================

def build_sheet1():
    few_sets = ["A", "B", "C", "D", "D2"]
    rows = []
    summary_rows = []  # (label, f1) for Summary sheet, singles only
    per_model_recall = {}   # provider -> {'zero': r, 'few_mean': r}
    per_model_few_recall = {}  # provider -> {set: recall}

    rows.append({"kind": "section", "label": "Single models -- zero-shot (Z)"})
    for p in MODELS3:
        r = e1v2_single(POOL25, "Z", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / zero-shot (Z)", "tp": r["tp"],
                     "fp": r["fp"], "fn": r["fn"], "f1": r["f1"], "group": "singleZ", "extra_note": ""})
        per_model_recall[p] = {"zero": r["recall"]}
        summary_rows.append((f"{MODEL_SHORT[p]}/Z", r["f1"]))

    for p in MODELS3:
        rows.append({"kind": "section", "label": f"{MODEL_SHORT[p]} -- few-shot sets (A/B/C/D/D2)"})
        f1_idx = []
        f1_vals = []
        per_model_few_recall[p] = {}
        for s in few_sets:
            r = e1v2_single(POOL25, s, p)
            note = "Known outlier set (homogeneous-root) per DESIGN_CHOICE_GPTZ_CLAUDEFS.md Part 2" if s == "C" else ""
            rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot {s}", "tp": r["tp"],
                         "fp": r["fp"], "fn": r["fn"], "f1": r["f1"], "group": f"few_{p}", "extra_note": note})
            f1_idx.append(len(rows) - 1)
            f1_vals.append(r["f1"])
            per_model_few_recall[p][s] = r["recall"]
            summary_rows.append((f"{MODEL_SHORT[p]}/{s}", r["f1"]))
        rng = f"range F1 [{min(f1_vals):.3f}, {max(f1_vals):.3f}] (min={few_sets[f1_vals.index(min(f1_vals))]}, max={few_sets[f1_vals.index(max(f1_vals))]})"
        rows.append({"kind": "mean", "label": f"{MODEL_SHORT[p]} / few-shot MEAN over 5 sets",
                     "source_rows": f1_idx, "extra_note": f"Mean of per-set P/R/F1 (not pooled counts); {rng}."})
        per_model_recall[p]["few_mean"] = sum(per_model_few_recall[p].values()) / len(few_sets)

    # Ensemble (2-of-3), zero
    rows.append({"kind": "section", "label": "Ensemble (majority vote across Claude/GPT/Gemini)"})
    cellsZ = [("Z", p) for p in MODELS3]
    ez = score_set_combo_e1v2(E1V2_CACHE, POOL25, cellsZ, 2)
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / zero", "tp": ez["tp"], "fp": ez["fp"],
                 "fn": ez["fn"], "f1": ez["f1"], "group": "combo", "extra_note": ""})
    summary_rows.append(("ENSEMBLE(2of3)/zero", ez["f1"]))

    idxs = []
    for s in few_sets:
        cells = [(s, p) for p in MODELS3]
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, 2)
        rows.append({"kind": "data", "label": f"ENSEMBLE (2-of-3) / few [{s}]", "tp": e["tp"], "fp": e["fp"],
                     "fn": e["fn"], "f1": e["f1"], "group": "combo_ens_few", "extra_note": ""})
        idxs.append(len(rows) - 1)
        summary_rows.append((f"ENSEMBLE(2of3)/{s}", e["f1"]))
    rows.append({"kind": "mean", "label": "ENSEMBLE (2-of-3) / few MEAN over 5 sets", "source_rows": idxs,
                 "extra_note": "Mean of per-set P/R/F1."})

    # Top 3 by recall
    configs = []
    for p in MODELS3:
        configs.append({"label": f"{MODEL_SHORT[p]}-Z", "kind": "zero", "model": p, "recall": per_model_recall[p]["zero"]})
        configs.append({"label": f"{MODEL_SHORT[p]}-FS", "kind": "few", "model": p, "recall": per_model_recall[p]["few_mean"]})
    top3 = sorted(configs, key=lambda c: c["recall"], reverse=True)[:3]
    top3_labels = ", ".join(f"{c['label']} (R={c['recall']:.3f})" for c in top3)

    def cells_for_set(chosen, set_name):
        return [(("Z" if c["kind"] == "zero" else set_name), c["model"]) for c in chosen]

    rows.append({"kind": "section", "label": f"Top 3 by recall (chosen: {top3_labels})"})
    for thr, name in ((2, "Top 3 models ENSEMBLE (2-of-3)"), (1, "Top 3 models ENSEMBLE (1-of-3)")):
        idxs = []
        for s in few_sets:
            cells = cells_for_set(top3, s)
            e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, thr)
            rows.append({"kind": "data", "label": f"{name} [{s}]", "tp": e["tp"], "fp": e["fp"], "fn": e["fn"],
                         "f1": e["f1"], "group": f"combo_{name}", "extra_note": f"Chosen 3: {top3_labels}" if s == few_sets[0] else ""})
            idxs.append(len(rows) - 1)
            summary_rows.append((f"{name}/{s}", e["f1"]))
        rows.append({"kind": "mean", "label": f"{name} MEAN over 5 sets", "source_rows": idxs,
                     "extra_note": "1-of-3 = positive if ANY of the 3 chosen configs says true. "
                                    "Ranking by recall favors liberal configurations; the 1-of-3 OR "
                                    "typically trades precision for recall." if thr == 1 else ""})

    # Fixed, user-requested combo (not recall-selected): Gemini-FS + GPT-Z + Claude-FS, 1-of-3 (OR)
    rows.append({"kind": "section", "label": "Fixed combo (user-requested, not recall-selected)"})
    idxs = []
    for s in few_sets:
        cells = [(s, "google"), ("Z", "openai"), (s, "anthropic")]
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, 1)
        rows.append({"kind": "data", "label": f"Gemini-FS + GPT-Z + Claude-FS (1-of-3) [{s}]", "tp": e["tp"],
                     "fp": e["fp"], "fn": e["fn"], "f1": e["f1"], "group": "combo_fixed3",
                     "extra_note": ("Fixed combo: positive if ANY of Gemini few-shot, GPT zero-shot, "
                                    "Claude few-shot says true -- not the recall-selected Top 3 above."
                                    if s == few_sets[0] else "")})
        idxs.append(len(rows) - 1)
        summary_rows.append((f"Gemini-FS+GPT-Z+Claude-FS(1of3)/{s}", e["f1"]))
    rows.append({"kind": "mean", "label": "Gemini-FS + GPT-Z + Claude-FS (1-of-3) MEAN over 5 sets",
                 "source_rows": idxs, "extra_note": "Mean of per-set P/R/F1."})

    # GPT-Z OR/AND Claude-FS
    rows.append({"kind": "section", "label": "GPT-Z + Claude-FS combination"})
    for op, thr, name in (("or", 1, "GPT-Z OR Claude-FS"), ("and", 2, "GPT-Z AND Claude-FS")):
        idxs = []
        for s in few_sets:
            cells = [("Z", "openai"), (s, "anthropic")]
            e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, thr)
            rows.append({"kind": "data", "label": f"{name} [{s}]", "tp": e["tp"], "fp": e["fp"], "fn": e["fn"],
                         "f1": e["f1"], "group": f"combo_{name}", "extra_note": ""})
            idxs.append(len(rows) - 1)
            summary_rows.append((f"{name}/{s}", e["f1"]))
        rows.append({"kind": "mean", "label": f"{name} MEAN over 5 sets", "source_rows": idxs, "extra_note": ""})

    n_pos = pool_positive_count(POOL25)
    n_neg = POOL25_VERSES - n_pos
    all_records = [r for r in E1V2_MANIFEST if r["set_name"] in ("Z",) + tuple(few_sets)]
    cost = sum(call_cost(r["provider"], r.get("usage")) for r in all_records if r.get("error") is None)
    dates = sorted(r["started_at_utc"][:10] for r in all_records)
    gemini_ids = sorted({r["model_id"] for r in all_records if r["provider"] == "google"})
    info = [
        ("Experiment", "E1 v2 core -- example-sensitivity pilot"),
        ("Sub-element (Arabic)", "استعارة فعل"),
        ("Sub-element (English)", "verbal metaphor (subtype of استعارة/metaphor, umbrella مجاز/trope)"),
        ("Prompt version(s)", "Z (zero-shot), A/B/C/D/D2 (five few-shot example-set variants)"),
        ("Pool", "eval_pool_25.json -- 25 poems, seed=43"),
        ("Number of poems", len(POOL25)),
        ("Number of verse-units", POOL25_VERSES),
        ("Number of positive verses", n_pos),
        ("Number of negative verses", n_neg),
        ("Positive rate", round(n_pos / POOL25_VERSES, 4)),
        ("Calls per cell", POOL25_VERSES),
        ("Runs per cell", e1v2_config.N_RUNS),
        ("Models (provider: requested model_id)",
         f"anthropic: claude-sonnet-4-6; openai: gpt-5.4-mini; google: {', '.join(gemini_ids)} "
         f"(requested only -- no model_version logged in manifest; see Notes sheet re: 3.5 vs 3.6)"),
        ("Cost (this sheet's sets)", f"${cost:.4f}"),
        ("Run date(s)", f"{dates[0]} to {dates[-1]}" if dates else "n/a"),
        ("Metric note", VERSE_PRIMARY_NOTE),
    ]
    new_sheet(wb, "E1v2 Core", info, rows, POOL25_VERSES)
    return summary_rows, top3_labels


# ===========================================================================
# Sheet 2 -- Eras (M1,M2,E1,E2,H1,H2,Q1,Q2) -- same pool as core
# ===========================================================================

def build_sheet2():
    few_sets = ["M1", "M2", "E1", "E2", "H1", "H2", "Q1", "Q2"]
    rows = []
    summary_rows = []
    per_model_recall = {}
    per_model_few_recall = {}

    rows.append({"kind": "section", "label": "Single models -- zero-shot (Z, same pool as E1v2 core)"})
    for p in MODELS3:
        r = e1v2_single(POOL25, "Z", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / zero-shot (Z)", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "singleZ", "extra_note": ""})
        per_model_recall[p] = {"zero": r["recall"]}
        summary_rows.append((f"{MODEL_SHORT[p]}/Z", r["f1"]))

    for p in MODELS3:
        rows.append({"kind": "section", "label": f"{MODEL_SHORT[p]} -- era/quartile few-shot sets"})
        f1_idx = []
        f1_vals = []
        per_model_few_recall[p] = {}
        for s in few_sets:
            r = e1v2_single(POOL25, s, p)
            rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot {s}", "tp": r["tp"], "fp": r["fp"],
                         "fn": r["fn"], "f1": r["f1"], "group": f"few_{p}", "extra_note": ""})
            f1_idx.append(len(rows) - 1)
            f1_vals.append(r["f1"])
            per_model_few_recall[p][s] = r["recall"]
            summary_rows.append((f"{MODEL_SHORT[p]}/{s}", r["f1"]))
        rng = f"range F1 [{min(f1_vals):.3f}, {max(f1_vals):.3f}] (min={few_sets[f1_vals.index(min(f1_vals))]}, max={few_sets[f1_vals.index(max(f1_vals))]})"
        rows.append({"kind": "mean", "label": f"{MODEL_SHORT[p]} / few-shot MEAN over 8 sets",
                     "source_rows": f1_idx, "extra_note": f"Mean of per-set P/R/F1; {rng}."})
        per_model_recall[p]["few_mean"] = sum(per_model_few_recall[p].values()) / len(few_sets)

    rows.append({"kind": "section", "label": "Ensemble (majority vote across Claude/GPT/Gemini)"})
    cellsZ = [("Z", p) for p in MODELS3]
    ez = score_set_combo_e1v2(E1V2_CACHE, POOL25, cellsZ, 2)
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / zero", "tp": ez["tp"], "fp": ez["fp"], "fn": ez["fn"],
                 "f1": ez["f1"], "group": "combo", "extra_note": "Identical to E1v2 Core sheet's Z row (same pool/data)."})
    summary_rows.append(("ENSEMBLE(2of3)/zero", ez["f1"]))

    idxs = []
    for s in few_sets:
        cells = [(s, p) for p in MODELS3]
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, 2)
        rows.append({"kind": "data", "label": f"ENSEMBLE (2-of-3) / few [{s}]", "tp": e["tp"], "fp": e["fp"],
                     "fn": e["fn"], "f1": e["f1"], "group": "combo_ens_few", "extra_note": ""})
        idxs.append(len(rows) - 1)
        summary_rows.append((f"ENSEMBLE(2of3)/{s}", e["f1"]))
    rows.append({"kind": "mean", "label": "ENSEMBLE (2-of-3) / few MEAN over 8 sets", "source_rows": idxs,
                 "extra_note": "Mean of per-set P/R/F1."})

    configs = []
    for p in MODELS3:
        configs.append({"label": f"{MODEL_SHORT[p]}-Z", "kind": "zero", "model": p, "recall": per_model_recall[p]["zero"]})
        configs.append({"label": f"{MODEL_SHORT[p]}-FS", "kind": "few", "model": p, "recall": per_model_recall[p]["few_mean"]})
    top3 = sorted(configs, key=lambda c: c["recall"], reverse=True)[:3]
    top3_labels = ", ".join(f"{c['label']} (R={c['recall']:.3f})" for c in top3)

    def cells_for_set(chosen, set_name):
        return [(("Z" if c["kind"] == "zero" else set_name), c["model"]) for c in chosen]

    rows.append({"kind": "section", "label": f"Top 3 by recall (chosen: {top3_labels})"})
    for thr, name in ((2, "Top 3 models ENSEMBLE (2-of-3)"), (1, "Top 3 models ENSEMBLE (1-of-3)")):
        idxs = []
        for s in few_sets:
            cells = cells_for_set(top3, s)
            e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, thr)
            rows.append({"kind": "data", "label": f"{name} [{s}]", "tp": e["tp"], "fp": e["fp"], "fn": e["fn"],
                         "f1": e["f1"], "group": f"combo_{name}", "extra_note": f"Chosen 3: {top3_labels}" if s == few_sets[0] else ""})
            idxs.append(len(rows) - 1)
            summary_rows.append((f"{name}/{s}", e["f1"]))
        rows.append({"kind": "mean", "label": f"{name} MEAN over 8 sets", "source_rows": idxs,
                     "extra_note": "1-of-3 = positive if ANY of the 3 chosen configs says true." if thr == 1 else ""})

    rows.append({"kind": "section", "label": "Fixed combo (user-requested, not recall-selected)"})
    idxs = []
    for s in few_sets:
        cells = [(s, "google"), ("Z", "openai"), (s, "anthropic")]
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, 1)
        rows.append({"kind": "data", "label": f"Gemini-FS + GPT-Z + Claude-FS (1-of-3) [{s}]", "tp": e["tp"],
                     "fp": e["fp"], "fn": e["fn"], "f1": e["f1"], "group": "combo_fixed3",
                     "extra_note": ("Fixed combo: positive if ANY of Gemini few-shot, GPT zero-shot, "
                                    "Claude few-shot says true -- not the recall-selected Top 3 above."
                                    if s == few_sets[0] else "")})
        idxs.append(len(rows) - 1)
        summary_rows.append((f"Gemini-FS+GPT-Z+Claude-FS(1of3)/{s}", e["f1"]))
    rows.append({"kind": "mean", "label": "Gemini-FS + GPT-Z + Claude-FS (1-of-3) MEAN over 8 sets",
                 "source_rows": idxs, "extra_note": "Mean of per-set P/R/F1."})

    rows.append({"kind": "section", "label": "GPT-Z + Claude-FS combination"})
    for op, thr, name in (("or", 1, "GPT-Z OR Claude-FS"), ("and", 2, "GPT-Z AND Claude-FS")):
        idxs = []
        for s in few_sets:
            cells = [("Z", "openai"), (s, "anthropic")]
            e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells, thr)
            rows.append({"kind": "data", "label": f"{name} [{s}]", "tp": e["tp"], "fp": e["fp"], "fn": e["fn"],
                         "f1": e["f1"], "group": f"combo_{name}", "extra_note": ""})
            idxs.append(len(rows) - 1)
            summary_rows.append((f"{name}/{s}", e["f1"]))
        rows.append({"kind": "mean", "label": f"{name} MEAN over 8 sets", "source_rows": idxs, "extra_note": ""})

    n_pos = pool_positive_count(POOL25)
    n_neg = POOL25_VERSES - n_pos
    all_records = [r for r in E1V2_MANIFEST if r["set_name"] in ("Z",) + tuple(few_sets)]
    cost = sum(call_cost(r["provider"], r.get("usage")) for r in all_records if r.get("error") is None)
    dates = sorted(r["started_at_utc"][:10] for r in all_records)
    info = [
        ("Experiment", "Poet-era & quartile few-shot sensitivity (M1/M2/E1/E2/H1/H2 'same-half' labels as in "
                        "E1_V2_ERAS_FEWSHOT.md, plus Q1/Q2 quartile sets)"),
        ("Sub-element (Arabic)", "استعارة فعل"),
        ("Sub-element (English)", "verbal metaphor"),
        ("Prompt version(s)", "Z (reused from E1v2 core) + M1/M2/E1/E2/H1/H2/Q1/Q2 few-shot example-set variants"),
        ("Pool", "eval_pool_25.json -- SAME pool as E1v2 core (25 poems, seed=43)"),
        ("Number of poems", len(POOL25)),
        ("Number of verse-units", POOL25_VERSES),
        ("Number of positive verses", n_pos),
        ("Number of negative verses", n_neg),
        ("Positive rate", round(n_pos / POOL25_VERSES, 4)),
        ("Calls per cell", POOL25_VERSES),
        ("Runs per cell", e1v2_config.N_RUNS),
        ("Models", "anthropic: claude-sonnet-4-6; openai: gpt-5.4-mini; google: gemini-3.5-flash (requested; no model_version logged)"),
        ("Cost (this sheet's sets, excl. Z already counted on E1v2 Core)", f"${cost:.4f}"),
        ("Run date(s)", f"{dates[0]} to {dates[-1]}" if dates else "n/a"),
        ("Metric note", VERSE_PRIMARY_NOTE),
    ]
    new_sheet(wb, "Eras FewShot", info, rows, POOL25_VERSES)
    return summary_rows, top3_labels


# ===========================================================================
# Sheet 3 -- Multi-poet F5/F10, own 50-poem pool, Z not available
# ===========================================================================

def build_sheet3():
    rows = []
    summary_rows = []
    configs = []
    rows.append({"kind": "section", "label": "Single models -- F5 (5 examples, 5 poets)"})
    for p in MODELS3:
        r = e1v2_single(POOL50, "F5", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot F5", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "F5", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-F5", "set": "F5", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/F5", r["f1"]))
    rows.append({"kind": "section", "label": "Single models -- F10 (10 examples, F5's 5 poets included)"})
    for p in MODELS3:
        r = e1v2_single(POOL50, "F10", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot F10", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "F10", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-F10", "set": "F10", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/F10", r["f1"]))

    rows.append({"kind": "section", "label": "Adaptation note"})
    rows.append({"kind": "note", "label": "No MEAN(F5,F10) row -- see adaptation note",
                 "extra_note": "F5 and F10 are two DIFFERENT designs (5 vs 10 few-shot examples), not "
                                "replicate draws of the same condition -- unlike A/B/C/D/D2 on the core "
                                "sheet, averaging them would not estimate example-set robustness. Shown "
                                "as two separate rows per model instead, per this sheet's task-level "
                                "adaptation instruction."})
    rows.append({"kind": "note", "label": "GPT-Z OR/AND Claude-FS: N/A on this sheet",
                 "extra_note": "Zero-shot (Z) was never run on the 50-poem multi-poet pool -- "
                                "GPT-Z does not exist here."})
    rows.append({"kind": "note", "label": "Gemini-FS + GPT-Z + Claude-FS (1-of-3): N/A on this sheet",
                 "extra_note": "Same reason -- this fixed combo requires GPT-Z, which was never run "
                                "on the 50-poem multi-poet pool."})

    rows.append({"kind": "section", "label": "Ensemble (majority vote across Claude/GPT/Gemini), per set"})
    for s in ("F5", "F10"):
        cells = [(s, p) for p in MODELS3]
        e = score_set_combo_e1v2(E1V2_CACHE, POOL50, cells, 2)
        rows.append({"kind": "data", "label": f"ENSEMBLE (2-of-3) / few [{s}]", "tp": e["tp"], "fp": e["fp"],
                     "fn": e["fn"], "f1": e["f1"], "group": "combo_ens", "extra_note": ""})
        summary_rows.append((f"ENSEMBLE(2of3)/{s}", e["f1"]))

    top3 = sorted(configs, key=lambda c: c["recall"], reverse=True)[:3]
    top3_labels = ", ".join(f"{c['label']} (R={c['recall']:.3f})" for c in top3)
    cells_top3 = [(c["set"], c["model"]) for c in top3]
    rows.append({"kind": "section", "label": f"Top 3 by recall among the 6 (model x F5/F10) configs: {top3_labels}"})
    for thr, name in ((2, "Top 3 models ENSEMBLE (2-of-3)"), (1, "Top 3 models ENSEMBLE (1-of-3)")):
        e = score_set_combo_e1v2(E1V2_CACHE, POOL50, cells_top3, thr)
        rows.append({"kind": "data", "label": name, "tp": e["tp"], "fp": e["fp"], "fn": e["fn"], "f1": e["f1"],
                     "group": f"combo_{name}",
                     "extra_note": f"Chosen 3: {top3_labels}. Each chosen config already names its own "
                                   "exact set (F5 or F10), so no per-set/MEAN split is needed here "
                                   "(unlike the core/eras sheets)."})
        summary_rows.append((name, e["f1"]))

    n_pos = pool_positive_count(POOL50)
    n_neg = POOL50_VERSES - n_pos
    all_records = [r for r in E1V2_MANIFEST if r["set_name"] in ("F5", "F10")]
    cost = sum(call_cost(r["provider"], r.get("usage")) for r in all_records if r.get("error") is None)
    dates = sorted(r["started_at_utc"][:10] for r in all_records)
    info = [
        ("Experiment", "Multi-poet few-shot (F5 vs F10): does the NUMBER of few-shot examples matter?"),
        ("Sub-element (Arabic)", "استعارة فعل"),
        ("Sub-element (English)", "verbal metaphor"),
        ("Prompt version(s)", "F5 (5 examples, 5 different poets) / F10 (10 examples, 10 different poets, "
                               "F5's 5 poets included) -- zero-shot (Z) not run on this pool"),
        ("Pool", "eval_pool_50_multipoet.json -- DIFFERENT 50-poem pool (only partial overlap with eval_pool_25.json)"),
        ("Number of poems", len(POOL50)),
        ("Number of verse-units", POOL50_VERSES),
        ("Number of positive verses", n_pos),
        ("Number of negative verses", n_neg),
        ("Positive rate", round(n_pos / POOL50_VERSES, 4)),
        ("Calls per cell", POOL50_VERSES),
        ("Runs per cell", e1v2_config.N_RUNS),
        ("Models", "anthropic: claude-sonnet-4-6; openai: gpt-5.4-mini; google: gemini-3.5-flash (requested; no model_version logged)"),
        ("Cost (this sheet's sets)", f"${cost:.4f}"),
        ("Run date(s)", f"{dates[0]} to {dates[-1]}" if dates else "n/a"),
        ("Metric note", VERSE_PRIMARY_NOTE + " Different pool than every other E1v2 sheet -- "
                                              "do not compare F5/F10 F1 directly against Z/A/B/.../Q2."),
    ]
    new_sheet(wb, "Multipoet F5F10", info, rows, POOL50_VERSES)
    return summary_rows, top3_labels


# ===========================================================================
# Sheet 4 -- Opus 5.5, set A only
# ===========================================================================

def build_sheet4():
    rows = []
    summary_rows = []
    configs = []

    rows.append({"kind": "section", "label": "Single models -- zero-shot (Z, reused from E1v2 core)"})
    for p in MODELS3:
        r = e1v2_single(POOL25, "Z", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / zero-shot (Z)", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "Z", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-Z", "set": "Z", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/Z", r["f1"]))

    rows.append({"kind": "section", "label": "Single models -- few-shot (set A, reused from E1v2 core)"})
    for p in MODELS3:
        r = e1v2_single(POOL25, "A", p)
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot A", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "A", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-A", "set": "A", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/A", r["f1"]))

    r = ANALYSIS_OPUS_A["criteria"]["verse"]["opus"]["overall"]
    rows.append({"kind": "data", "label": "Opus 5.5 / few-shot A", "tp": r["tp"], "fp": r["fp"], "fn": r["fn"],
                 "f1": r["f1"], "group": "A", "extra_note": "Opus 5.5 ran on set A only -- no zero-shot condition."})
    configs.append({"label": "Opus-A", "set": "A", "model": "anthropic_opus", "recall": r["recall"]})
    summary_rows.append(("Opus/A", r["f1"]))

    rows.append({"kind": "section", "label": "Ensemble (majority vote), reused from E1v2 core / analysis_report_ensemble.json"})
    ez = score_set_combo_e1v2(E1V2_CACHE, POOL25, [("Z", p) for p in MODELS3], 2)
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / zero", "tp": ez["tp"], "fp": ez["fp"], "fn": ez["fn"],
                 "f1": ez["f1"], "group": "combo", "extra_note": "3 base models only (Claude/GPT/Gemini), Opus not included."})
    summary_rows.append(("ENSEMBLE(2of3)/zero", ez["f1"]))
    ea = ANALYSIS_OPUS_A["criteria"]["verse"]["ensemble"]["overall"]
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / few [A]", "tp": ea["tp"], "fp": ea["fp"], "fn": ea["fn"],
                 "f1": ea["f1"], "group": "combo", "extra_note": "3 base models only, Opus not included."})
    summary_rows.append(("ENSEMBLE(2of3)/A", ea["f1"]))

    top3 = sorted(configs, key=lambda c: c["recall"], reverse=True)[:3]
    top3_labels = ", ".join(f"{c['label']} (R={c['recall']:.3f})" for c in top3)
    cells_top3 = [(c["set"], c["model"]) for c in top3]
    rows.append({"kind": "section", "label": f"Top 3 by recall among the 7 configs (3xZ + 3xA + Opus-A): {top3_labels}"})
    for thr, name in ((2, "Top 3 models ENSEMBLE (2-of-3)"), (1, "Top 3 models ENSEMBLE (1-of-3)")):
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, cells_top3, thr)
        rows.append({"kind": "data", "label": name, "tp": e["tp"], "fp": e["fp"], "fn": e["fn"], "f1": e["f1"],
                     "group": f"combo_{name}", "extra_note": f"Chosen 3: {top3_labels}."})
        summary_rows.append((name, e["f1"]))

    rows.append({"kind": "section", "label": "Fixed combo (user-requested, not recall-selected)"})
    e = score_set_combo_e1v2(E1V2_CACHE, POOL25, [("A", "google"), ("Z", "openai"), ("A", "anthropic")], 1)
    rows.append({"kind": "data", "label": "Gemini-FS + GPT-Z + Claude-FS (1-of-3) [A]", "tp": e["tp"],
                 "fp": e["fp"], "fn": e["fn"], "f1": e["f1"], "group": "combo_fixed3",
                 "extra_note": "Fixed combo: positive if ANY of Gemini few-shot[A], GPT zero-shot, "
                                "Claude few-shot[A] says true -- not the recall-selected Top 3 above."})
    summary_rows.append(("Gemini-FS+GPT-Z+Claude-FS(1of3)/A", e["f1"]))

    rows.append({"kind": "section", "label": "GPT-Z + Claude-FS[A] combination"})
    for thr, name in ((1, "GPT-Z OR Claude-FS[A]"), (2, "GPT-Z AND Claude-FS[A]")):
        e = score_set_combo_e1v2(E1V2_CACHE, POOL25, [("Z", "openai"), ("A", "anthropic")], thr)
        rows.append({"kind": "data", "label": name, "tp": e["tp"], "fp": e["fp"], "fn": e["fn"], "f1": e["f1"],
                     "group": f"combo_{name}", "extra_note": ""})
        summary_rows.append((name, e["f1"]))

    n_pos = pool_positive_count(POOL25)
    n_neg = POOL25_VERSES - n_pos
    opus_records = [r for r in E1V2_MANIFEST if r["provider"] == "anthropic_opus"]
    cost = sum(call_cost(r["provider"], r.get("usage")) for r in opus_records if r.get("error") is None)
    dates = sorted(r["started_at_utc"][:10] for r in opus_records)
    info = [
        ("Experiment", "Claude Opus 5.5 vs the 3-model panel, set A only"),
        ("Sub-element (Arabic)", "استعارة فعل"),
        ("Sub-element (English)", "verbal metaphor"),
        ("Prompt version(s)", "Z (3 base models, reused) + A (3 base models + Opus 5.5, reused/new)"),
        ("Pool", "eval_pool_25.json -- SAME pool as E1v2 core"),
        ("Number of poems", len(POOL25)),
        ("Number of verse-units", POOL25_VERSES),
        ("Number of positive verses", n_pos),
        ("Number of negative verses", n_neg),
        ("Positive rate", round(n_pos / POOL25_VERSES, 4)),
        ("Calls per cell", POOL25_VERSES),
        ("Runs per cell", e1v2_config.N_RUNS),
        ("Models", "anthropic_opus: claude-opus-5-5 (set A only; no zero-shot run for Opus)"),
        ("Cost (Opus calls only; base-3-model cost already counted on E1v2 Core)", f"${cost:.4f}"),
        ("Run date(s)", f"{dates[0]} to {dates[-1]}" if dates else "n/a"),
        ("Metric note", VERSE_PRIMARY_NOTE),
    ]
    new_sheet(wb, "Opus5.5 SetA", info, rows, POOL25_VERSES)
    return summary_rows, top3_labels


# ===========================================================================
# Sheets 5-8 -- Phase 7 subtypes
# ===========================================================================

PHASE7_SUBTYPE_EN = {
    "استعارة قديمة": "archaic/lexicalized metaphor (subtype of استعارة/metaphor)",
    "كناية عن صفة": "periphrasis about an attribute/trait (subtype of كناية/periphrasis)",
    "تشبيه قصير": "short simile (subtype of تشبيه/simile)",
    "تشبيه مطول": "extended/elaborated simile (subtype of تشبيه/simile)",
}


def build_phase7_sheet(subtype, sheet_title):
    sub_report = ANALYSIS_PHASE7["subtypes"][subtype]
    indicative = subtype in ANALYSIS_PHASE7["indicative_only"]
    rows = []
    summary_rows = []
    configs = []

    gt = p7.build_ground_truth(subtype, P7_POOL_POEM_IDS)

    rows.append({"kind": "section", "label": "Single models -- zero-shot"})
    for p in MODELS3:
        r = sub_report["by_model"][p]["zero"]["verse"]
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / zero-shot", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "zero", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-Z", "cond": "zero", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/zero", r["f1"]))

    rows.append({"kind": "section", "label": "Single models -- few-shot (1 condition; no multi-set MEAN on this sheet)"})
    for p in MODELS3:
        r = sub_report["by_model"][p]["few"]["verse"]
        rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / few-shot", "tp": r["tp"], "fp": r["fp"],
                     "fn": r["fn"], "f1": r["f1"], "group": "few", "extra_note": ""})
        configs.append({"label": f"{MODEL_SHORT[p]}-FS", "cond": "few", "model": p, "recall": r["recall"]})
        summary_rows.append((f"{MODEL_SHORT[p]}/few", r["f1"]))
    rows.append({"kind": "note", "label": "No few-shot MEAN row on this sheet",
                 "extra_note": "Phase 7 ran exactly ONE few-shot condition per model for this subtype "
                                "(2 worked examples, fixed) -- there is no family of interchangeable "
                                "few-shot example sets to average, unlike the E1v2 Core/Eras sheets."})

    rows.append({"kind": "section", "label": "Ensemble (majority vote), reused from analysis_report_phase7.json"})
    ez = sub_report["ensemble"]["zero"]["verse"]
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / zero", "tp": ez["tp"], "fp": ez["fp"], "fn": ez["fn"],
                 "f1": ez["f1"], "group": "combo", "extra_note": ""})
    summary_rows.append(("ENSEMBLE(2of3)/zero", ez["f1"]))
    ef = sub_report["ensemble"]["few"]["verse"]
    rows.append({"kind": "data", "label": "ENSEMBLE (2-of-3) / few", "tp": ef["tp"], "fp": ef["fp"], "fn": ef["fn"],
                 "f1": ef["f1"], "group": "combo", "extra_note": ""})
    summary_rows.append(("ENSEMBLE(2of3)/few", ef["f1"]))

    top3 = sorted(configs, key=lambda c: c["recall"], reverse=True)[:3]
    top3_labels = ", ".join(f"{c['label']} (R={c['recall']:.3f})" for c in top3)
    cells_top3 = [(c["cond"], c["model"]) for c in top3]
    rows.append({"kind": "section", "label": f"Top 3 by recall among the 6 (model x zero/few) configs: {top3_labels}"})
    for thr, name in ((2, "Top 3 models ENSEMBLE (2-of-3)"), (1, "Top 3 models ENSEMBLE (1-of-3)")):
        e = score_set_combo_p7(P7_CELL_INDEX, subtype, P7_POOL_POEM_IDS, gt, cells_top3, thr)
        rows.append({"kind": "data", "label": name, "tp": e["tp"], "fp": e["fp"], "fn": e["fn"], "f1": e["f1"],
                     "group": f"combo_{name}", "extra_note": f"Chosen 3: {top3_labels}."})
        summary_rows.append((name, e["f1"]))

    rows.append({"kind": "section", "label": "Fixed combo (user-requested, not recall-selected)"})
    e = score_set_combo_p7(P7_CELL_INDEX, subtype, P7_POOL_POEM_IDS, gt,
                            [("few", "google"), ("zero", "openai"), ("few", "anthropic")], 1)
    rows.append({"kind": "data", "label": "Gemini-FS + GPT-Z + Claude-FS (1-of-3)", "tp": e["tp"], "fp": e["fp"],
                 "fn": e["fn"], "f1": e["f1"], "group": "combo_fixed3",
                 "extra_note": "Fixed combo: positive if ANY of Gemini few-shot, GPT zero-shot, "
                                "Claude few-shot says true -- not the recall-selected Top 3 above."})
    summary_rows.append(("Gemini-FS+GPT-Z+Claude-FS(1of3)", e["f1"]))

    rows.append({"kind": "section", "label": "GPT-Z + Claude-FS combination (reused from analysis_report_phase7.json)"})
    dc = sub_report["design_choice"]
    orr = dc["gptz_or_claudefs_verse"]
    rows.append({"kind": "data", "label": "GPT-Z OR Claude-FS", "tp": orr["tp"], "fp": orr["fp"], "fn": orr["fn"],
                 "f1": orr["f1"], "group": "combo_or", "extra_note": ""})
    summary_rows.append(("GPT-Z OR Claude-FS", orr["f1"]))
    andd = dc["gptz_and_claudefs_verse"]
    rows.append({"kind": "data", "label": "GPT-Z AND Claude-FS", "tp": andd["tp"], "fp": andd["fp"], "fn": andd["fn"],
                 "f1": andd["f1"], "group": "combo_and", "extra_note": ""})
    summary_rows.append(("GPT-Z AND Claude-FS", andd["f1"]))

    n_pos = sub_report["n_pool_positives"]
    n_neg = 327 - n_pos
    subtype_records = [r for r in P7_MANIFEST if r["subtype"] == subtype]
    cost = sum(call_cost(r["provider"], r.get("usage")) for r in subtype_records if r.get("error") is None)
    dates = sorted(r["started_at_utc"][:10] for r in subtype_records)
    indicative_note = (" -- INDICATIVE ONLY: pool positives < 30 (this project's own floor), "
                        "read every number here as 'what happened on this one 25-poem sample', "
                        "not a generalizable estimate.") if indicative else " -- above the n=30 pool-positive floor."
    info = [
        ("Experiment", f"Phase 7 subtype check -- {subtype}"),
        ("Sub-element (Arabic)", subtype),
        ("Sub-element (English)", PHASE7_SUBTYPE_EN[subtype]),
        ("Prompt version(s)", "zero-shot / few-shot (2 worked examples)"),
        ("Pool", "eval_pool_25.json -- SAME pool as E1v2 core (25 poems, 327 verse-units)"),
        ("Number of poems", 25),
        ("Number of verse-units", 327),
        ("Number of positive verses", n_pos),
        ("Number of negative verses", n_neg),
        ("Positive rate", round(n_pos / 327, 4)),
        ("Calls per cell", 327),
        ("Runs per cell", 1),
        ("Models", "anthropic: claude-sonnet-4-6; openai: gpt-5.4-mini; google: gemini-3.5-flash (requested; no model_version logged)"),
        ("Cost (this subtype)", f"${cost:.4f}"),
        ("Run date(s)", f"{dates[0]} to {dates[-1]}" if dates else "n/a"),
        ("Pool-positive floor status", f"n={n_pos}" + indicative_note),
        ("Metric note", VERSE_PRIMARY_NOTE),
    ]
    new_sheet(wb, sheet_title, info, rows, 327)
    return summary_rows, top3_labels


# ===========================================================================
# Sheet 9 -- Phase 1 frozen (5 poems, old prompt, Trope, strict-based)
# ===========================================================================

PHASE1_TROPE_TEST = {
    "baseline": {
        "anthropic": {"tp": 17, "fp": 3, "fn": 162},
        "openai": {"tp": 6, "fp": 1, "fn": 173},
        "google": {"tp": 34, "fp": 4, "fn": 145},
    },
    "v4_combined": {
        "anthropic": {"tp": 25, "fp": 3, "fn": 154},
        "openai": {"tp": 28, "fp": 16, "fn": 151},
        "google": {"tp": 45, "fp": 9, "fn": 134},
    },
}


def verify_phase1_numbers(project_state_md):
    tpfpfn_strings = {
        "baseline": {"anthropic": "17/3/162", "openai": "6/1/173", "google": "34/4/145"},
        "v4_combined": {"anthropic": "25/3/154", "openai": "28/16/151", "google": "45/9/134"},
    }
    f1_strings = {
        "baseline": {"anthropic": "0.171", "openai": "0.065", "google": "0.313"},
        "v4_combined": {"anthropic": "0.242", "openai": "0.251", "google": "0.386"},
    }
    for prompt_key, rows_ in tpfpfn_strings.items():
        for p, s in rows_.items():
            assert s in project_state_md, f"Phase 1 TP/FP/FN {s} ({prompt_key}/{p}) not found in PROJECT_STATE.md"
    for prompt_key, rows_ in f1_strings.items():
        for p, s in rows_.items():
            assert s in project_state_md, f"Phase 1 F1 {s} ({prompt_key}/{p}) not found in PROJECT_STATE.md"
            c = PHASE1_TROPE_TEST[prompt_key][p]
            got = ens2.prf1(c["tp"], c["fp"], c["fn"])["f1"]
            assert abs(got - float(s)) < 0.0005, (prompt_key, p, got, s)
    print("PASS: Phase 1 Trope TEST TP/FP/FN and F1 strings verified verbatim against PROJECT_STATE.md.")


def build_sheet9():
    project_state_md = PROJECT_STATE_PATH.read_text(encoding="utf-8")
    verify_phase1_numbers(project_state_md)
    rows = []
    summary_rows = []
    for prompt_key, label in (("baseline", "baseline prompt"), ("v4_combined", "v4_combined prompt")):
        rows.append({"kind": "section", "label": f"{label}"})
        for p in MODELS3:
            c = PHASE1_TROPE_TEST[prompt_key][p]
            f1 = ens2.prf1(c["tp"], c["fp"], c["fn"])["f1"]
            rows.append({"kind": "data", "label": f"{MODEL_SHORT[p]} / {prompt_key}", "tp": c["tp"], "fp": c["fp"],
                         "fn": c["fn"], "f1": f1, "group": prompt_key, "extra_note": ""})
            summary_rows.append((f"{MODEL_SHORT[p]}/{prompt_key}", f1))
    info = [
        ("Experiment", "Phase 1 FROZEN -- TEST run (span-level, strict criterion), NOT comparable to any "
                        "other sheet in this workbook"),
        ("Sub-element (Arabic)", "مجاز (Phase 1 terminology: 'Trope')"),
        ("Sub-element (English)", "Trope -- the FULL umbrella category (استعارة + تمثيل + مجاز مرسل pooled), "
                                   "not a single subtype like every other sheet here"),
        ("Prompt version(s)", "baseline vs v4_combined (whole-poem prompts, Phase 1 terminology/method -- "
                               "NOT the Phase 4/7 per-verse subtype prompt)"),
        ("Pool", "TEST poems: Imru1, Jarir, Abu_Tammam (3 poems, frozen, SPENT -- PROJECT_STATE.md section 2)"),
        ("Number of poems", 3),
        ("Number of verse-units", "n/a -- SPAN-level scoring (multi-instance per verse possible), not a "
                                   "per-verse binary classification like every other sheet; TN is not a "
                                   "meaningful concept here and is omitted (task: 'only the columns that exist')"),
        ("Number of positive (ground-truth) instances", 179),
        ("Metric", "Span-level, STRICT matching criterion, 2-run majority (PROJECT_STATE.md rule 2/4) "
                   "-- NOT verse-level. This is the one sheet in this workbook that is not verse-level."),
        ("Comparability warning", "Different prompt, different element scope (umbrella Trope vs a single "
                                   "subtype), different pool, different metric (span/strict vs verse) from "
                                   "every other sheet. Copied verbatim from PROJECT_STATE.md section 3a and "
                                   "verified against that file's text programmatically (see script). "
                                   "DO NOT compare these F1 values directly against any other sheet."),
        ("Source", "PROJECT_STATE.md section 3a (frozen 2026-07-21)"),
    ]
    new_sheet(wb, "Phase1 Frozen", info, rows, "n/a")
    return summary_rows


# ===========================================================================
# Sheet 10 -- Summary
# ===========================================================================

def build_summary(all_summaries, all_top3):
    ws = wb.create_sheet(title="Summary")
    headers = ["Experiment", "Best verse F1 (config)", "Worst verse F1 (config)", "Top-3 chosen (where applicable)"]
    for c, h in enumerate(headers, start=1):
        _set_cell(ws, 1, c, h, font=HEADER_FONT, fill=HEADER_FILL, align=Alignment(horizontal="center"))
    r = 2
    for name, rows_f1 in all_summaries:
        if not rows_f1:
            continue
        best = max(rows_f1, key=lambda x: x[1])
        worst = min(rows_f1, key=lambda x: x[1])
        _set_cell(ws, r, 1, name, font=BOLD_FONT)
        _set_cell(ws, r, 2, f"{best[1]:.3f} ({best[0]})")
        _set_cell(ws, r, 3, f"{worst[1]:.3f} ({worst[0]})")
        top3_text = all_top3.get(name, "")
        c4 = _set_cell(ws, r, 4, top3_text)
        c4.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = max(15, 15 * max(1, -(-len(top3_text) // 70)))
        r += 1
    widths = [26, 30, 30, 70]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return ws


# ===========================================================================
# Sheet 11 -- Notes
# ===========================================================================

def build_notes(git_commit):
    ws = wb.create_sheet(title="Notes")
    blockers_text = TOP5_BLOCKERS_PATH.read_text(encoding="utf-8") if TOP5_BLOCKERS_PATH.exists() else ""
    licensing_note = ("UNRESOLVED: " + blockers_text.splitlines()[1].strip()
                       if blockers_text else "writing/paper_plan/TOP_5_BLOCKERS.md not found")

    sections = [
        ("Scope", [
            "This workbook consolidates every result shown in docs/phase4/E1_V2_REPORT.html, "
            "EXCLUDING Phase 5-6 (local fine-tuning), per the user's explicit request.",
            "Verse-level metrics ONLY throughout (per the user's explicit decision for this workbook). "
            "CLAUDE.md's standing rule 4 (always score span-level too, strict + token-overlap) is "
            "deliberately NOT followed in this workbook -- verse-level alone can reward exists=True "
            "regardless of whether the predicted span is actually correct, which is why "
            "E1_V2_REPORT.html / DESIGN_CHOICE_GPTZ_CLAUDEFS.md / E1_V2_ENSEMBLE.md all report "
            "strict/token alongside verse. Use the HTML report or the underlying analysis_report*.json "
            "files directly if a strict/token comparison is needed.",
        ]),
        ("Definitions used throughout this workbook", [
            "ENSEMBLE (2-of-3): for each verse-unit, predicted positive iff >=2 of the 3 named models/"
            "configurations returned exists=True for that cell. A missing/unparseable cell is a non-vote "
            "(treated as False) -- same convention as experiments/phase4_e1_v2/ensemble_v2.py and "
            "experiments/phase7_subtypes/score_phase7.py's own ensemble rule.",
            "Top 3 models ENSEMBLE (2-of-3) / (1-of-3): among the 6 base configurations for that sheet "
            "(3 models x zero-shot/few-shot, few-shot = that model's MEAN recall over its own few-shot "
            "sets where more than one exists), the 3 with the HIGHEST verse-level RECALL are chosen -- "
            "NEVER by F1 or precision. 2-of-3 then requires 2 of those 3 chosen configurations to agree; "
            "1-of-3 (OR) requires only one. CAVEAT: ranking by recall systematically favors liberal "
            "(high-recall, lower-precision) configurations, so the 1-of-3 OR ensemble built from a "
            "recall-selected trio will typically show high recall and comparatively low precision -- "
            "this is expected given the selection rule, not a surprising result. The same MODEL can "
            "legitimately occupy 2 of the 3 chosen slots (e.g. both its zero-shot AND few-shot "
            "configuration rank in the top 3) -- the rule ranks the 6 CONFIGURATIONS, not 1-per-model; "
            "this happened on several sheets in this workbook (e.g. 'E1v2 Core' chose GPT-Z and GPT-FS "
            "together) and is shown explicitly in each sheet's 'Top 3 by recall (chosen: ...)' section header.",
            "GPT-Z OR Claude-FS / AND: the 2-voter combination of GPT-5.4-mini's zero-shot call with "
            "Claude Sonnet 4.6's few-shot call for the stated set. OR = positive if either says yes; "
            "AND = positive only if both agree. This is the project's own 'production candidate' "
            "combination, first analyzed in docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md.",
            "Gemini-FS + GPT-Z + Claude-FS (1-of-3): a FIXED 3-voter combination requested directly "
            "by the user (Gemini few-shot, GPT zero-shot, Claude few-shot), scored as 1-of-3 (OR -- "
            "positive if ANY of the 3 says true). This is NOT the recall-selected 'Top 3' above -- it "
            "is always this exact trio, on every sheet where all 3 inputs exist. Shown per few-shot "
            "set + MEAN on 'E1v2 Core' and 'Eras FewShot' (same convention as every other combo row); "
            "a single row on 'Opus5.5 SetA' (set A only) and each Phase 7 subtype sheet (1 few-shot "
            "condition only); N/A on 'Multipoet F5F10' (no zero-shot run on that pool, so GPT-Z does "
            "not exist there) and on 'Phase1 Frozen' (different metric entirely).",
            "MEAN (over sets) rows: the MEAN of each set's own already-computed Precision/Recall/F1 "
            "(not derived from averaged TP/FP/FN, which would be a different, nonlinear quantity for "
            "F1). TP/FP/FN shown on a MEAN row are plain means of the per-set counts, shown for "
            "reference only (hence non-integer) -- they are NOT used to (re)derive that row's P/R/F1. "
            "The 'never pick the best set' rule means every individual set's row is always shown "
            "alongside the MEAN, with the full min-max range stated in that row's Notes cell.",
            "TN (true negatives) = (total verse-units in that sheet's pool) - TP - FP - FN, as an "
            "Excel formula referencing the literal pool size stated in that sheet's own info block.",
            "P/R/F1 are always live Excel formulas computed from each row's own TP/FP/FN cells "
            "(=IFERROR(TP/(TP+FP),0) etc.) -- never hand-typed, per the task's instruction.",
        ]),
        ("Comparability warnings", [
            "The 'Phase1 Frozen' sheet is NOT comparable to any other sheet: different prompt (whole-poem "
            "baseline/v4_combined vs every other sheet's per-verse subtype prompt), different element "
            "scope (the full umbrella 'Trope'/مجاز category vs one narrow subtype), different pool "
            "(3 frozen TEST poems vs the 25/50-poem E1v2 pools), and a different metric (span-level "
            "strict, 2-run majority, vs this workbook's verse-level, 1-run convention everywhere else).",
            "'E1v2 Core' / 'Eras FewShot' / 'Opus5.5 SetA' share the SAME 25-poem/327-verse pool and the "
            "same zero-shot (Z) data -- numbers for 'Claude/Z', 'GPT/Z', 'Gemini/Z' and the 3-model "
            "ENSEMBLE/zero row are IDENTICAL across those three sheets by construction (same cache, "
            "same cells), not independently re-estimated.",
            "'Multipoet F5F10' uses a DIFFERENT 50-poem pool with only partial overlap (9/25 poems) "
            "against the other E1v2 sheets' 25-poem pool (per docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md) "
            "-- its F1 values must not be compared directly against Z/A/B/C/D/D2/M*/E*/H*/Q* rows.",
            "Phase 7 subtypes 'استعارة قديمة', 'تشبيه قصير', 'تشبيه مطول' are flagged INDICATIVE ONLY "
            "(pool positives n=15/13/25, all under this project's own n=30 floor) -- their numbers "
            "describe this one 25-poem sample, not a generalizable estimate. Only 'كناية عن صفة' (n=49) "
            "is above the floor.",
            "No bootstrap confidence intervals are shown anywhere in this workbook (the task asked for "
            "raw TP/FP/FN/P/R/F1 only) -- several of the differences visible here (e.g. between sets, "
            "or between single models and ensembles) do NOT clear a 95% CI in the source documents "
            "(docs/phase4/E1_V2_ENSEMBLE.md, DESIGN_CHOICE_GPTZ_CLAUDEFS.md, docs/phase7/SUBTYPES_RESULTS.md) "
            "-- consult those documents before treating any single-row difference here as a confirmed effect.",
        ]),
        ("One run, no noise baseline (everywhere in this workbook except Phase1 Frozen)", [
            "Every E1 v2 / Phase 7 number in this workbook is from EXACTLY 1 run per (set/condition, poem, "
            "verse, model) cell -- CLAUDE.md's standing rule 2 (>=2 runs, 2-run majority as the primary "
            "metric) was NOT followed for any of Phases 4 and 7. The project's own prior finding "
            "(PROJECT_STATE.md section 6.1: an apparent 8x Kenning/Periphrasis gain on one run halved on "
            "a second) is the explicit reason that rule exists -- treat every single-run number in this "
            "workbook, including every ensemble/Top-3/OR/AND combination built on top of those single "
            "runs, as provisional pending a second run, exactly as docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md "
            "Part 4 already states. Phase 1 Frozen (sheet 9) is the one exception: it IS 2-run majority.",
        ]),
        ("Licensing", [licensing_note]),
        ("Source files read to build this workbook", [
            "results/phase4_e1_v2/run_manifest.json, analysis_report_ensemble.json, analysis_report_opus_a.json, "
            "design_choice/analysis_report_design_choice.json, and raw/*.txt (via ensemble_v2.build_parsed_cache)",
            "results/phase7_subtypes/run_manifest.json, run_manifest_tashbih2.json, analysis_report_phase7.json, "
            "and raw/*.txt + raw_tashbih2/*.txt (via score_phase7.load_manifests/build_cell_index)",
            "experiments/phase4_e1_v2/config/eval_pool_25.json, eval_pool_50_multipoet.json",
            "experiments/phase4_e1_v2/{ensemble_v2,e1v2_config,gt_v2}.py, experiments/phase7_subtypes/score_phase7.py "
            "(all read-only, never modified), experiments/pilot_3models/{analyze,config}.py",
            "PROJECT_STATE.md section 3a (Phase 1 frozen numbers), GLOSSARY.md (terminology), "
            "writing/paper_plan/TOP_5_BLOCKERS.md (licensing caveat)",
            "docs/phase4/{E1_V2_ENSEMBLE,DESIGN_CHOICE_GPTZ_CLAUDEFS}.md, docs/phase7/SUBTYPES_RESULTS.md "
            "(cross-checked, not recomputed from, in verify_* below)",
        ]),
        ("Provenance", [
            f"Built by scripts/build_results_excel.py, git commit {git_commit}, generated "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}. No API calls were made to "
            "produce this workbook or any of its inputs.",
        ]),
    ]
    r = 1
    for title, paras in sections:
        _set_cell(ws, r, 1, title, font=Font(name=FONT_NAME, bold=True, size=13), border=False)
        r += 1
        for p_ in paras:
            _set_cell(ws, r, 1, p_, border=False)
            ws.cell(r, 1).alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = 45
            r += 1
        r += 1
    ws.column_dimensions["A"].width = 140
    return ws


# ===========================================================================
# Main
# ===========================================================================

wb = openpyxl.Workbook()
wb.remove(wb.active)

all_summaries = []
all_top3 = {}

print("Building Sheet 1 (E1v2 Core) ...")
s1, t1 = build_sheet1()
all_summaries.append(("E1v2 Core", s1))
all_top3["E1v2 Core"] = t1

print("Building Sheet 2 (Eras FewShot) ...")
s2, t2 = build_sheet2()
all_summaries.append(("Eras FewShot", s2))
all_top3["Eras FewShot"] = t2

print("Building Sheet 3 (Multipoet F5F10) ...")
s3, t3 = build_sheet3()
all_summaries.append(("Multipoet F5F10", s3))
all_top3["Multipoet F5F10"] = t3

print("Building Sheet 4 (Opus5.5 SetA) ...")
s4, t4 = build_sheet4()
all_summaries.append(("Opus5.5 SetA", s4))
all_top3["Opus5.5 SetA"] = t4

PHASE7_SHEETS = [
    ("استعارة قديمة", "P7 استعارة قديمة"),
    ("كناية عن صفة", "P7 كناية عن صفة"),
    ("تشبيه قصير", "P7 تشبيه قصير"),
    ("تشبيه مطول", "P7 تشبيه مطول"),
]
for subtype, title in PHASE7_SHEETS:
    print(f"Building Phase 7 sheet ({subtype}) ...")
    s, t = build_phase7_sheet(subtype, title)
    all_summaries.append((title, s))
    all_top3[title] = t

print("Building Sheet 9 (Phase1 Frozen) ...")
s9 = build_sheet9()
all_summaries.append(("Phase1 Frozen", s9))

print("Building Summary sheet ...")
build_summary(all_summaries, all_top3)

print("Building Notes sheet ...")
try:
    git_commit = __import__("subprocess").check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()
except Exception:
    git_commit = "unknown"
build_notes(git_commit)

DOCS_DIR.mkdir(parents=True, exist_ok=True)
wb.save(OUT_PATH)
print(f"\nWrote {OUT_PATH}")
print("Sheets:", wb.sheetnames)
