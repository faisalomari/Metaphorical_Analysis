"""Supervisor deliverable 1: detailed_results.docx - verse-by-verse, per
element, per model decisions vs ground truth, across all 5 poems (3 TEST +
2 DEV), using ONLY already-collected v4_combined data (the frozen/adopted
prompt, 2-run majority). No new API calls. Reuses the exact same scoring
primitives (majority_exists_and_appearance, best_match) that produce the
main report's numbers - this is a per-verse presentation layer over the
existing harness, not a new one.
"""
import re

from config import ELEMENT_ORDER, ELEMENT_AR, MODELS, RESULTS_DIR, POEMS
from analyze import load_all_runs
from ground_truth import load_ground_truth_spans
from span_scoring import majority_exists_and_appearance
from span_matching import best_match

POEM_DIRS = {
    "Imru1": RESULTS_DIR / "test_final" / "v4_combined" / "Imru1",
    "Jarir": RESULTS_DIR / "test_final" / "v4_combined" / "Jarir",
    "Abu_Tammam": RESULTS_DIR / "test_final" / "v4_combined" / "Abu_Tammam",
    "Imru2": RESULTS_DIR / "dev_variants" / "v4_combined" / "Imru2",
    "Nabigha": RESULTS_DIR / "dev_variants" / "v4_combined" / "Nabigha",
}
# TEST (frozen headline numbers) first, then DEV
POEM_ORDER = ["Imru1", "Jarir", "Abu_Tammam", "Imru2", "Nabigha"]
POEM_LABELS = {
    "Imru1": "Imru' al-Qais, Poem 1 (the Mu'allaqa) - TEST",
    "Jarir": "Jarir - TEST",
    "Abu_Tammam": "Abu Tammam - TEST",
    "Imru2": "Imru' al-Qais, Poem 8 - DEV",
    "Nabigha": "Al-Nabigha Al-Dhubyani - DEV",
}

VERSE_LINE_RE = re.compile(r'^\s*\d+\)\s*"*(.*?)"*\s*$')


def clean_verse_text(raw_line: str) -> str:
    m = VERSE_LINE_RE.match(raw_line)
    return m.group(1) if m else raw_line.strip()


def get_verse_texts(poem_key: str) -> dict:
    poem_text = POEMS[poem_key]["poetry_path"].read_text(encoding="utf-8").strip()
    lines = [ln for ln in poem_text.split("\n") if ln.strip()]
    return {i + 1: clean_verse_text(ln) for i, ln in enumerate(lines)}


def classify(runs, element, verse_no, gt_texts):
    """Reuses majority_exists_and_appearance + best_match (both already
    power the frozen scoring) to classify one verse+element+provider as
    TP/FP/FN/TN/NA for qualitative display."""
    exists, appearance = majority_exists_and_appearance(runs, element, verse_no)
    if exists is None:
        return {"verdict": "NA", "appearance": None}
    if not exists:
        return {"verdict": "FN" if gt_texts else "TN", "appearance": None}
    if not gt_texts:
        return {"verdict": "FP", "appearance": appearance}
    match_idx = best_match(appearance or "", gt_texts, "strict", 0.5)
    if match_idx is None:
        return {"verdict": "FP", "appearance": appearance}
    return {"verdict": "TP", "appearance": appearance}


VERDICT_COLOR = {"TP": (0x1A, 0x7A, 0x1A), "FP": (0xB0, 0x20, 0x20), "FN": (0xC0, 0x7A, 0x00)}
VERDICT_LABEL = {"TP": "TP (correct)", "FP": "FP (false alarm)", "FN": "FN (missed)", "TN": "-", "NA": "n/a"}


def fill_model_cell(cell, verdict_info):
    from docx.shared import RGBColor
    cell.text = ""
    p = cell.paragraphs[0]
    verdict = verdict_info["verdict"]
    if verdict in ("TN", "NA"):
        p.add_run(VERDICT_LABEL[verdict])
        return
    run = p.add_run(VERDICT_LABEL[verdict])
    run.bold = True
    run.font.color.rgb = RGBColor(*VERDICT_COLOR[verdict])
    if verdict_info.get("appearance"):
        p2 = cell.add_paragraph()
        r2 = p2.add_run(verdict_info["appearance"])
        r2.italic = True
        p2.alignment = 3  # WD_ALIGN_PARAGRAPH.RIGHT (Arabic reads better right-aligned)


def build_docx(out_path):
    import docx
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10)

    doc.add_heading("Detailed Verse-by-Verse Results — v4_combined, 2-Run Majority", level=1)
    doc.add_heading("Reading guide", level=2)
    guide = doc.add_paragraph()
    guide.add_run(
        "Every verdict in this document uses the v4_combined prompt (the thesis's adopted/frozen configuration) "
        "and 2-run majority vote — the same scoring primitives that produce the main report's numbers "
        "(analyze.majority_exists_and_appearance + span_matching.best_match, strict criterion), just shown "
        "per verse instead of aggregated. Poems are grouped TEST first (the frozen headline evaluation: "
        "Imru1, Jarir, Abu Tammam), then DEV (Imru2, Nabigha, used only for prompt tuning). Within each poem, "
        "results are grouped by element. Each model cell shows:"
    )
    for line in [
        "TP (correct) — the model's predicted span matched a real ground-truth instance",
        "FP (false alarm) — the model said this element exists but there is no matching ground-truth instance "
        "(or its span didn't match one that does exist)",
        "FN (missed) — ground truth has an instance here but the model said it doesn't exist",
        "– — both model and ground truth agree the element is absent (not colored; the uninteresting case)",
    ]:
        doc.add_paragraph(line, style="List Bullet")
    guide2 = doc.add_paragraph()
    guide2.add_run(
        "The italic text under a TP/FP verdict is the model's own predicted “appearance” span — the literal "
        "substring it pointed to as evidence. This is the only “why” available in the existing data; these "
        "runs were never asked to state a reason. A small illustrative sample with an actual stated reason "
        "per positive decision is in the separate document explanations_sample.docx (Imru2 only, DEV, "
        "explicitly NOT part of the frozen evaluation)."
    )

    for poem_key in POEM_ORDER:
        out_dir = POEM_DIRS[poem_key]
        by_provider = load_all_runs(out_dir)
        gt_spans = load_ground_truth_spans(poem_key)
        verse_texts = get_verse_texts(poem_key)
        n_verses = POEMS[poem_key]["n_verses"]

        doc.add_heading(f"{poem_key} — {POEM_LABELS[poem_key]}", level=1)

        for element in ELEMENT_ORDER:
            doc.add_heading(f"{element} ({ELEMENT_AR[element]})", level=2)
            providers = list(by_provider.keys())
            table = doc.add_table(rows=1, cols=3 + len(providers))
            table.style = "Light Grid Accent 1"
            hdr = table.rows[0].cells
            hdr[0].text = "#"
            hdr[1].text = "Verse"
            hdr[2].text = "Ground truth"
            for i, provider in enumerate(providers):
                hdr[3 + i].text = MODELS[provider]["display"]

            for verse_no in range(1, n_verses + 1):
                gt_texts = [g["span"] for g in gt_spans[verse_no][element]]
                row = table.add_row().cells
                row[0].text = str(verse_no)
                vt = row[1].paragraphs[0]
                vt.add_run(verse_texts.get(verse_no, ""))
                vt.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                gtp = row[2].paragraphs[0]
                gtp.add_run("; ".join(gt_texts) if gt_texts else "-")
                gtp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                for i, provider in enumerate(providers):
                    v = classify(by_provider[provider], element, verse_no, gt_texts)
                    fill_model_cell(row[3 + i], v)

    doc.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    build_docx(RESULTS_DIR / "detailed_results.docx")
