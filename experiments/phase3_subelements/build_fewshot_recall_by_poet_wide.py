"""Simple wide table requested: rows = the 13 few-shot subtypes, columns =
one Recall value per poet (4 columns) + one Total Recall column. A second
sheet keeps the underlying n/TP/FN per cell for reference. No new API calls.
"""
import json

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from phase3_config import RESULTS_DIR
from subtype_defs import SUBTYPE_DEFS
from build_by_poet import parent_short, majority, PARENT_ORDER
from run_fewshot_check import ELIGIBLE_SUBTYPES, split_holdout_and_test
from build_fewshot_comparison import slugify

RAW_DIR = RESULTS_DIR / "raw"
POETS = ["امرؤ القيس", "النابغة الذبياني", "جرير بن عطيّة", "أبو تمّام"]


def subtype_sort_key(k):
    parent = parent_short(SUBTYPE_DEFS[k]["parent"])
    return (PARENT_ORDER.index(parent) if parent in PARENT_ORDER else 99,)


def main():
    per_subtype = {}
    for subtype_key in ELIGIBLE_SUBTYPES:
        slug = slugify(subtype_key)
        path = RAW_DIR / f"{slug}_fewshot.jsonl"
        by_row = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                key = (rec["poem_key"], rec["row_id"])
                by_row.setdefault(key, {"poet": rec["poet"]})[rec["run_idx"]] = rec.get("exists")
        agg = {}
        for key, runs in by_row.items():
            poet = runs["poet"]
            m = majority([runs.get(0), runs.get(1)])
            if m is None:
                continue
            slot = agg.setdefault(poet, [0, 0])
            slot[0 if m else 1] += 1
        per_subtype[subtype_key] = agg

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "recall_by_poet"
    ws.sheet_view.rightToLeft = True
    ws.append(
        ["الفرع", "العنصر_الرئيسي"]
        + [f"عدد الأمثلة التوضيحية - {p}" for p in POETS]
        + [f"Recall - {p}" for p in POETS]
        + ["Recall - الإجمالي"]
    )
    for c in ws[1]:
        c.font = Font(bold=True)

    ws2 = wb.create_sheet("تفاصيل_n_TP_FN")
    ws2.sheet_view.rightToLeft = True
    ws2.append(["الفرع"] + sum(([f"{p} n", f"{p} TP", f"{p} FN"] for p in POETS), []) + ["الإجمالي n", "الإجمالي TP", "الإجمالي FN"])
    for c in ws2[1]:
        c.font = Font(bold=True)

    for subtype_key in sorted(ELIGIBLE_SUBTYPES, key=subtype_sort_key):
        parent = parent_short(SUBTYPE_DEFS[subtype_key]["parent"])
        agg = per_subtype[subtype_key]

        holdout, _ = split_holdout_and_test(subtype_key)
        demo_counts = {}
        for h in holdout:
            demo_counts[h["poet"]] = demo_counts.get(h["poet"], 0) + 1

        row = [subtype_key, parent] + [demo_counts.get(poet, 0) or None for poet in POETS]
        detail_row = [subtype_key]
        total_tp = total_fn = 0
        for poet in POETS:
            tp, fn = agg.get(poet, [0, 0])
            n = tp + fn
            row.append(round(tp / n, 3) if n else None)
            detail_row += [n or None, tp or None, fn or None]
            total_tp += tp
            total_fn += fn
        n_total = total_tp + total_fn
        row.append(round(total_tp / n_total, 3) if n_total else None)
        detail_row += [n_total, total_tp, total_fn]
        ws.append(row)
        ws2.append(detail_row)

    for i in range(1, 12):
        ws.column_dimensions[get_column_letter(i)].width = 22
    ws.column_dimensions["A"].width = 34
    ws.freeze_panes = "C2"

    for i in range(1, 14):
        ws2.column_dimensions[get_column_letter(i)].width = 14
    ws2.column_dimensions["A"].width = 34

    out_path = RESULTS_DIR / "fewshot_recall_by_poet_wide.xlsx"
    wb.save(out_path)
    print(f"written to {out_path}")


if __name__ == "__main__":
    main()
