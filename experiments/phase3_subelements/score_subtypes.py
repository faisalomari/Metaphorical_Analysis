"""Computes the honest per-subtype metrics available from this experiment's
design, using the project's 2-run majority convention (analyze.py
per_verse_majority: with exactly 2 runs, majority=True only if BOTH runs say
True - a tie/split counts as False).

IMPORTANT LIMITATION (read before trusting any number here): every row fed
into run_subtype_check.py is a ground-truth POSITIVE for its own subtype -
we only ever asked "is subtype X present in a line Dr. Hussein already
tagged as subtype X?". We never asked the model about a line that is NOT
tagged with subtype X. That means:
  - TP and FN ARE honestly measured (majority=True -> TP, majority=False -> FN)
  - Recall = TP / (TP + FN) IS honestly measured
  - FP and TN are UNDEFINED by this design - there is no negative sample to
    compute them from. Precision and F1 CANNOT be computed from this data;
    reporting them as 0 or 1 would be fabricated, not measured.
This script reports TP/FN/Recall only, and explicitly marks FP/TN/Precision/F1
as not-available rather than guessing.
"""
import json
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

from phase3_config import RESULTS_DIR
from subtype_defs import SUBTYPE_DEFS

RAW_DIR = RESULTS_DIR / "raw"


def majority(votes):
    """Matches analyze.py per_verse_majority exactly: with N_RUNS=2, a split
    (1 true, 1 false) counts as False, not as a coin flip."""
    votes = [v for v in votes if v is not None]
    if not votes:
        return None
    return sum(votes) > len(votes) / 2


def load_rows_for_subtype(subtype_key: str, slug: str):
    """Merges the _dev and _test jsonl for one subtype into {(poem_key, row_id): [exists_run1, exists_run2]}.

    NOTE: the ground truth's '#' column is only unique WITHIN one poem's own
    sheet (every poem file restarts at #1) - keying by row_id alone silently
    collapses rows from different poems that happen to share a '#' value.
    Must key by (poem_key, row_id)."""
    by_row = {}
    for split in ("dev", "test"):
        path = RAW_DIR / f"{slug}_{split}.jsonl"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                key = (rec["poem_key"], rec["row_id"])
                by_row.setdefault(key, {})[rec["run_idx"]] = rec.get("exists")
    return by_row


def slugify(name: str) -> str:
    import re
    s = re.sub(r'[\\/:*?"<>|]', "", name)
    return s.replace(" ", "_")


def main():
    results = []
    for subtype_key in SUBTYPE_DEFS:
        slug = slugify(subtype_key)
        by_row = load_rows_for_subtype(subtype_key, slug)
        if not by_row:
            continue
        tp = fn = parse_err = 0
        for (poem_key, row_id), runs in by_row.items():
            votes = [runs.get(0), runs.get(1)]
            m = majority(votes)
            if m is None:
                parse_err += 1
                continue
            if m:
                tp += 1
            else:
                fn += 1
        n = tp + fn
        recall = round(tp / n, 3) if n else None
        results.append({
            "subtype": subtype_key,
            "parent": SUBTYPE_DEFS[subtype_key]["parent"],
            "n": n, "TP": tp, "FN": fn, "parse_errors_excluded": parse_err,
            "recall_2run_majority": recall,
        })

    results.sort(key=lambda r: -r["n"])

    print(f"{'subtype':40s} {'n':>4s} {'TP':>4s} {'FN':>4s} {'recall':>7s}")
    for r in results:
        print(f"{r['subtype']:40s} {r['n']:4d} {r['TP']:4d} {r['FN']:4d} {r['recall_2run_majority']:7.3f}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "recall_by_subtype"
    ws.sheet_view.rightToLeft = True
    ws.append(["العنصر_الفرعي", "العنصر_الرئيسي", "n (=TP+FN)", "TP", "FN", "Recall (2-run majority)",
               "FP", "TN", "Precision", "F1"])
    for r in results:
        ws.append([r["subtype"], r["parent"], r["n"], r["TP"], r["FN"], r["recall_2run_majority"],
                   "غير متاح", "غير متاح", "غير متاح", "غير متاح"])
    for i in range(1, 11):
        ws.column_dimensions[get_column_letter(i)].width = 22

    note = wb.create_sheet("ملاحظة_منهجية")
    note.sheet_view.rightToLeft = True
    note.append(["كل سطر في هذه التجربة كان مثالًا موجبًا معروفًا مسبقًا لفرعه (Dr. Hussein tagged it as this subtype)."])
    note.append(["لذلك TP و FN و Recall مقاسة بصدق فعليًا."])
    note.append(["أما FP و TN و Precision و F1: غير قابلة للحساب من هذه التجربة، لأننا لم نسأل الموديل مطلقًا عن سطر لا يحمل هذا الفرع."])
    note.append(["لحسابها فعليًا نحتاج عينة سلبية (أسطر غير معلَّمة بهذا الفرع) لكل فرع، وهذا استدعاء إضافي جديد يحتاج تقدير تكلفة وموافقة مسبقة."])
    note.column_dimensions["A"].width = 110

    out_path = RESULTS_DIR / "recall_by_subtype.xlsx"
    wb.save(out_path)
    print(f"\nwritten to {out_path}")


if __name__ == "__main__":
    main()
