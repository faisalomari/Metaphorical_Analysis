"""Analysis for the leave-one-out جرير كناية عن صفة probe
(run_leave_one_out_jarir.py). Produces:

  results/phase3_subelements/loo_jarir_kinaya_sifa.xlsx
    Sheet 1 "per_config": one row per of the 17 demo configs - which verse
      was used as the one-shot example, and the resulting recall (2-run
      majority) on the other 16 lines.
    Sheet 2 "raw_matrix": 17x16 matrix, one row per demo config, one column
      per test verse, cell = majority verdict (TP/FN) - to see whether
      specific test lines are consistently hard regardless of which example
      was shown, or whether it's demo-dependent.
    Sheet 3 "الملخص": overall stats - mean/min/max/stdev of recall across
      the 17 configs, i.e. how much recall swings just from changing which
      single example is shown.

No new API calls - pure aggregation of raw/loo_jarir_kinaya_sifa.jsonl.
"""
import json
import statistics

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

from phase3_config import RESULTS_DIR


def majority(votes):
    votes = [v for v in votes if v is not None]
    if not votes:
        return None
    return sum(votes) > len(votes) / 2


def main():
    path = RESULTS_DIR / "raw" / "loo_jarir_kinaya_sifa.jsonl"
    meta = json.load(open(RESULTS_DIR / "loo_jarir_meta.json", encoding="utf-8"))
    rows_meta = {r["row_id"]: r for r in meta["rows"]}

    # {config_idx: {test_row_id: {run_idx: exists}}}
    data = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            data.setdefault(rec["demo_config_idx"], {}).setdefault(rec["test_row_id"], {})[rec["run_idx"]] = rec.get("exists")

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "per_config"
    ws1.sheet_view.rightToLeft = True
    ws1.append(["config#", "demo_row_id", "demo_verse_no", "demo_span", "demo_explanation",
                "n_test", "TP", "FN", "Recall"])
    for c in ws1[1]:
        c.font = Font(bold=True)

    recalls = []
    for config_idx in sorted(data.keys()):
        demo_row_id = None
        # demo row id isn't in per-test records; recover from meta order (configs indexed 0..16 in row order)
        demo_row = meta["rows"][config_idx]
        tp = fn = 0
        for test_row_id, runs in data[config_idx].items():
            m = majority([runs.get(0), runs.get(1)])
            if m is True:
                tp += 1
            elif m is False:
                fn += 1
        n = tp + fn
        recall = round(tp / n, 3) if n else None
        if recall is not None:
            recalls.append(recall)
        ws1.append([config_idx + 1, demo_row["row_id"], demo_row["verse_no"], demo_row["span"],
                    demo_row["explanation"], n, tp, fn, recall])

    for i in range(1, 10):
        ws1.column_dimensions[get_column_letter(i)].width = 22
    ws1.column_dimensions["D"].width = 40
    ws1.column_dimensions["E"].width = 50

    # raw matrix: rows=config (demo used), cols=test verse, cell=TP/FN
    ws2 = wb.create_sheet("raw_matrix")
    ws2.sheet_view.rightToLeft = True
    all_test_row_ids = sorted({rid for cfg in data.values() for rid in cfg})
    ws2.append(["config \\ test_row_id"] + [f"#{rid} (v{rows_meta[rid]['verse_no']})" for rid in all_test_row_ids])
    for config_idx in sorted(data.keys()):
        demo_row = meta["rows"][config_idx]
        row_vals = [f"cfg{config_idx+1} (demo=#{demo_row['row_id']}, v{demo_row['verse_no']})"]
        for rid in all_test_row_ids:
            runs = data[config_idx].get(rid)
            if runs is None:
                row_vals.append("—")  # this was the demo line itself for this config
                continue
            m = majority([runs.get(0), runs.get(1)])
            row_vals.append("TP" if m is True else "FN" if m is False else "?")
        ws2.append(row_vals)
    ws2.column_dimensions["A"].width = 30
    for i in range(2, len(all_test_row_ids) + 2):
        ws2.column_dimensions[get_column_letter(i)].width = 12

    # per-test-line hit rate across all 16 configs where it WAS in the test set
    hit_rate_row = ["% TP across configs"]
    for rid in all_test_row_ids:
        outcomes = []
        for config_idx in sorted(data.keys()):
            runs = data[config_idx].get(rid)
            if runs is None:
                continue
            m = majority([runs.get(0), runs.get(1)])
            if m is not None:
                outcomes.append(1 if m else 0)
        hit_rate_row.append(round(100 * sum(outcomes) / len(outcomes), 1) if outcomes else None)
    ws2.append([])
    ws2.append(hit_rate_row)

    ws3 = wb.create_sheet("الملخص")
    ws3.sheet_view.rightToLeft = True
    ws3.append(["المقياس", "القيمة"])
    ws3.append(["عدد الإعدادات (configs)", len(recalls)])
    ws3.append(["متوسط Recall عبر الإعدادات", round(statistics.mean(recalls), 3)])
    ws3.append(["أعلى Recall", max(recalls)])
    ws3.append(["أدنى Recall", min(recalls)])
    ws3.append(["الفرق بين الأعلى والأدنى", round(max(recalls) - min(recalls), 3)])
    ws3.append(["الانحراف المعياري", round(statistics.stdev(recalls), 3)])
    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 16

    out_path = RESULTS_DIR / "loo_jarir_kinaya_sifa.xlsx"
    wb.save(out_path)
    print(f"written to {out_path}")
    print(f"recall range: {min(recalls)} - {max(recalls)}, mean={statistics.mean(recalls):.3f}, stdev={statistics.stdev(recalls):.3f}")


if __name__ == "__main__":
    main()
