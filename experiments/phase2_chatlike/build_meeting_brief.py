"""One-page meeting brief for Tsvika (Prof. Tsvi Kuflik), responding to his
Phase 1 feedback (PROJECT_STATE.md Phase 2 sec5). Uses the shared RTL
helpers (rtl_utils.py) per CLAUDE.md - no hand-rolled bidi handling.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pilot_3models"))
from rtl_utils import apply_paragraph_direction  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "phase2_chatlike" / "meeting_brief.docx"


def add_para(doc, text, size=9, bold=False, space_after=2):
    from docx.shared import Pt
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(0)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = bold
    apply_paragraph_direction(p, text)
    return p


def add_heading(doc, text, size=11):
    from docx.shared import Pt, RGBColor
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    apply_paragraph_direction(p, text)
    return p


def add_table(doc, rows, col_widths_in, font_size=8):
    from docx.shared import Inches, Pt
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid Accent 1"
    table.autofit = False
    for r_idx, row_vals in enumerate(rows):
        cells = table.rows[r_idx].cells
        for c_idx, val in enumerate(row_vals):
            cells[c_idx].width = Inches(col_widths_in[c_idx])
            cell_p = cells[c_idx].paragraphs[0]
            cell_p.paragraph_format.space_after = Pt(0)
            run = cell_p.add_run(val)
            run.font.size = Pt(font_size)
            run.bold = (r_idx == 0)
            apply_paragraph_direction(cell_p, val)
    return table


def build():
    import docx
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = docx.Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(9)
    section = doc.sections[0]
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

    title = doc.add_paragraph()
    title.paragraph_format.space_after = Pt(2)
    tr = title.add_run("Meeting Brief — Phase 2 Progress (2026-07-23)")
    tr.font.size = Pt(14)
    tr.bold = True
    tr.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)

    sub = doc.add_paragraph()
    sub.paragraph_format.space_after = Pt(4)
    sr = sub.add_run("For: Prof. Tsvi Kuflik  |  Responding to feedback on the Phase 1 report  |  Full detail: PROJECT_STATE.md, results/phase2_chatlike/report_3i.md")
    sr.font.size = Pt(8)
    sr.italic = True
    sr.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # --- 1. Phase 1 frozen results ---
    add_heading(doc, "1. Phase 1 — frozen results (recap)")
    add_para(doc, "• v4_combined (the adopted prompt) beats baseline on Trope, Simile, and Antonymy; Kenning barely moves (frozen TEST: 3 poems, 3 models, 2-run majority).")
    add_para(doc, "• Total cost across the whole pilot cycle: $8.29, 1,134 API calls — reproducible exactly (REPRODUCIBILITY.md).")
    add_para(doc, "• Two structural findings worth remembering: all 3 models miss the same instances (ensembling gains nothing), and all 3 over-claim Antonymy (precision as low as 0.26).")

    # --- 2. Same-poet question ---
    add_heading(doc, "2. Your same-poet question — answered")
    add_para(doc, 'You asked: "You have 2 poems by the same poet — perhaps when it\'s the same poet, success will be better?"', size=8)
    add_table(doc, [
        ["Poem", "Poet", "Split", "Macro-avg F1 (v4, strict)"],
        ["Abu_Tammam", "Abu Tammam", "TEST", "0.366  (highest)"],
        ["Imru2", "Imru' al-Qais", "DEV", "0.343"],
        ["Imru1", "Imru' al-Qais", "TEST", "0.302"],
        ["Nabigha", "Al-Nabigha", "DEV", "0.284"],
        ["Jarir", "Jarir", "TEST", "0.256  (lowest)"],
    ], col_widths_in=[1.2, 1.3, 0.8, 1.9], font_size=8)
    add_para(doc, "No clear same-poet effect: Imru' al-Qais's two poems sit in the middle of the range, not clustered at the top — a different poet (Abu Tammam) scores highest, another (Jarir) lowest. "
                  "Honest confound: Imru2 was DEV-tuned and Imru1 wasn't, yet their gap (0.04) is smaller than Abu_Tammam-vs-Jarir's (0.11) — so any DEV-tuning advantage isn't larger than ordinary poem-to-poem noise. "
                  "With only 2 poems for one poet and 1 each for three others, this is too thin to rule the hypothesis out — a fresh poem by an already-represented poet would settle it (see ask #2).", size=8)

    # --- 3. Error characteristics ---
    add_heading(doc, "3. Error characteristics (full 9-row table: results/phase2_chatlike/error_characteristics_summary.md)")
    add_table(doc, [
        ["Failure mode", "Element(s)", "Frequency"],
        ["مجاز مرسل (lexicalized metonymy) stays flat — no Phase 1 fix moves it", "Trope", "85% missed, baseline AND v4 alike (n=13, TEST)"],
        ["Trope↔Kenning boundary confusion (figurative verb vs. plausible-literal phrasing)", "Trope, Kenning", "motivated a dedicated prompt rule"],
        ["Antithesis over-claiming — FP > TP for every model", "Antonymy", "precision as low as 0.26 (n=43, TEST)"],
        ["Shared blind spots — ensembling across 3 models gains nothing", "Trope, Kenning", "ensemble F1 = best single model, exactly"],
        ["Run instability, concentrated in one model", "Kenning", "Gemini agreement drops to 77-89% vs. 91-100% elsewhere"],
        ["[Phase 2] Detection reachable, not reliably decided", "Kenning, Trope", "4/10 any-of-2-runs -> 1/10 under 2-run majority"],
    ], col_widths_in=[3.6, 1.0, 2.6], font_size=8)

    # --- 4. Phase 2 findings ---
    add_heading(doc, "4. Phase 2 findings (this cycle)")
    for line in [
        "Model effect alone (Fable 5, same prompt) lifts Trope and Kenning recall with NO precision cost — the cleanest result of the cycle.",
        "Terminology correction alone (kenning→periphrasis, antonymy→antithesis): small real gain for Trope, none for Kenning — a caveat for Phase 1's Trope numbers only.",
        "Full recipe (free-form reasoning + correct terms + named مجاز subtypes): the largest Kenning gain yet (F1 0.11→0.32-0.42 on Imru2), catches the exact verse that motivated this whole phase — but at real precision cost.",
        "Targeted مجاز مرسل probe (Nabigha, $2.73): the model reaches the right answer in 4 of 10 known-positive verses in at least one of two runs — but only 1 of 10 survives the standard 2-run-majority convention. Detection is reachable; it isn't yet reliable.",
        "A likely annotation-gap surfaced, not just a model error: Jarir v37 — all 3 models flag an antithesis ground truth doesn't mark, and it reads like a real one. On today's shortlist for Ali.",
    ]:
        add_para(doc, "• " + line, size=8.5)

    # --- 5. Two asks ---
    add_heading(doc, "5. Two asks")
    add_para(doc, "1. Error-review working session with Ali — a 13-verse shortlist is ready (results/phase2_chatlike/ali_adjudication_shortlist.md), spanning مجاز مرسل near-misses, Kenning blind spots, "
                  "antithesis over-claiming/possible annotation gaps, and cross-model disagreements. Aiming to resolve: which model alternates are defensible vs. wrong, and whether any ground-truth gaps exist.", size=8.5)
    add_para(doc, "2. A second annotator (for inter-annotator agreement — none exists yet, single-annotator throughout) and/or budget for the full Nabigha Config C validation (~$12, extends the probe above to real "
                  "precision/F1 numbers) or the designed-not-run few-shot follow-up (~$0.5, tests whether demonstrations can recover some of Config C's gain more cheaply). Both scoped, neither run — happy to prioritize based on discussion.", size=8.5)

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
