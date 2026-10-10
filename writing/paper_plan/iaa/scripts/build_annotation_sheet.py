"""Build the blind re-annotation workbook from `sheets/sample_manifest.csv`.

Blind by construction: this script never reads model predictions or Dr.
Hussein's original ground-truth labels into the output sheet - only verse
text (from the poem files) and the element definitions (from
`data/elements/*.txt`), both of which are not themselves labels. The empty
label columns are for the annotator to fill in from scratch.

Output: writing/paper_plan/iaa/sheets/blind_reannotation_sample.xlsx
  - Sheet "Annotation": one row per sampled verse, empty label columns.
  - Sheet "Element Definitions": the 4 definitions + worked examples,
    reference material only, Dr. Hussein himself co-defined these so this is
    not new information, just a reminder for a second annotator / after a
    time gap.
  - Sheet "Instructions (EN)" / "تعليمات (عربي)": short in-sheet pointer to
    the standalone one-page instruction sheet (instructions.docx).
"""
import csv

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from common import ELEMENT_LABELS, IAA_DIR, POEM_AR_SHORT, config, load_poem_verses

YES_NO = ["نعم / Yes", "لا / No"]

HEADER_FILL = PatternFill(start_color="1F4E5F", end_color="1F4E5F", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)


def read_sample_manifest():
    path = IAA_DIR / "sheets" / "sample_manifest.csv"
    with path.open(encoding="utf-8") as f:
        return [{"poem": row["poem"], "verse_no": int(row["verse_no"])} for row in csv.DictReader(f)]


def build_annotation_sheet(wb, rows):
    ws = wb.active
    ws.title = "Annotation"
    ws.sheet_view.rightToLeft = True

    fixed_headers = ["#", "القصيدة / Poem", "رقم البيت / Verse No.", "نص البيت / Verse Text"]
    el_headers = []
    for el in config.ELEMENT_ORDER:
        ar, en = ELEMENT_LABELS[el]["ar"], ELEMENT_LABELS[el]["en"]
        el_headers += [f"{ar} ({en}) - موجود؟", f"{ar} ({en}) - الموضع (span)"]
    headers = fixed_headers + el_headers + ["ملاحظات / Notes"]

    for col, text in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col, value=text)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"

    verses_by_poem = {poem: load_poem_verses(poem) for poem in config.POEMS}

    r = 2
    for i, row in enumerate(rows, start=1):
        poem, no = row["poem"], row["verse_no"]
        text = verses_by_poem[poem].get(no, "")
        ws.cell(row=r, column=1, value=i)
        ws.cell(row=r, column=2, value=POEM_AR_SHORT[poem])
        ws.cell(row=r, column=3, value=no)
        vc = ws.cell(row=r, column=4, value=text)
        vc.alignment = Alignment(horizontal="right", wrap_text=True)
        r += 1

    n_data_rows = len(rows)
    dv = DataValidation(type="list", formula1=f'"{YES_NO[0]},{YES_NO[1]}"', allow_blank=True)
    ws.add_data_validation(dv)
    for ei in range(len(config.ELEMENT_ORDER)):
        exists_col = 5 + ei * 2
        dv.add(f"{ws.cell(row=2, column=exists_col).coordinate}:{ws.cell(row=1 + n_data_rows, column=exists_col).coordinate}")

    widths = {1: 4, 2: 22, 3: 10, 4: 55}
    for ei in range(len(config.ELEMENT_ORDER)):
        widths[5 + ei * 2] = 16
        widths[6 + ei * 2] = 30
    widths[len(headers)] = 25
    for col, w in widths.items():
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = w
    for r_ in range(2, 2 + n_data_rows):
        ws.row_dimensions[r_].height = 32


def build_definitions_sheet(wb):
    ws = wb.create_sheet("Element Definitions")
    ws.sheet_view.rightToLeft = True
    headers = ["Element (Arabic)", "Element (English, corrected)", "Arabic definition", "English definition", "Worked examples (from data/elements/*.txt)"]
    for col, text in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col, value=text)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    from common import ROOT

    r = 2
    for el in config.ELEMENT_ORDER:
        raw = (ROOT / "data" / "elements" / config.ELEMENT_FILES[el]).read_text(encoding="utf-8")
        lines = raw.splitlines()
        ar_def = next((l.split(":", 1)[1].strip() for l in lines if l.startswith("Arabic explanation:")), "")
        en_def = next((l.split(":", 1)[1].strip() for l in lines if l.startswith("English explanation:")), "")
        ex_start = next((i for i, l in enumerate(lines) if l.strip() == "Examples:"), None)
        examples = "\n".join(lines[ex_start + 1:]) if ex_start is not None else ""

        ws.cell(row=r, column=1, value=ELEMENT_LABELS[el]["ar"]).alignment = Alignment(horizontal="right")
        ws.cell(row=r, column=2, value=ELEMENT_LABELS[el]["en"])
        ws.cell(row=r, column=3, value=ar_def).alignment = Alignment(horizontal="right", wrap_text=True)
        ws.cell(row=r, column=4, value=en_def).alignment = Alignment(wrap_text=True)
        ws.cell(row=r, column=5, value=examples).alignment = Alignment(horizontal="right", wrap_text=True)
        ws.row_dimensions[r].height = 110
        r += 1

    widths = {1: 14, 2: 20, 3: 50, 4: 50, 5: 45}
    for col, w in widths.items():
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = w


def build_pointer_sheet(wb):
    ws = wb.create_sheet("Instructions")
    ws.sheet_view.rightToLeft = True
    msg_ar = (
        "الرجاء قراءة ورقة التعليمات المستقلة (instructions.docx) قبل البدء بالتبويب "
        "\"Annotation\". هذا الملف لا يحتوي على أي تسميات من النموذج أو من التصنيف الأصلي - "
        "كل خلية فارغة يجب تعبئتها من جديد بالاعتماد على نص البيت وتعريفات العناصر فقط."
    )
    msg_en = (
        "Please read the standalone instruction sheet (instructions.docx) before starting "
        "the 'Annotation' tab. This file contains no model predictions and no original "
        "ground-truth labels - every empty cell should be filled in fresh, based only on "
        "the verse text and the element definitions tab."
    )
    ws.cell(row=1, column=1, value=msg_ar).alignment = Alignment(horizontal="right", wrap_text=True)
    ws.cell(row=3, column=1, value=msg_en).alignment = Alignment(horizontal="left", wrap_text=True)
    ws.column_dimensions["A"].width = 100
    ws.row_dimensions[1].height = 60
    ws.row_dimensions[3].height = 60


def main():
    rows = read_sample_manifest()
    wb = Workbook()
    build_annotation_sheet(wb, rows)
    build_definitions_sheet(wb)
    build_pointer_sheet(wb)
    out_path = IAA_DIR / "sheets" / "blind_reannotation_sample.xlsx"
    wb.save(out_path)
    print(f"Wrote {out_path} ({len(rows)} verses)")


if __name__ == "__main__":
    main()
