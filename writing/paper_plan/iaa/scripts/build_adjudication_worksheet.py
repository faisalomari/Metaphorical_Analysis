"""Build a working xlsx version of the existing 13-verse adjudication
shortlist (`results/phase2_chatlike/ali_adjudication_shortlist.md`) for the
live session with Dr. Hussein.

This is NOT a blind annotation instrument - unlike blind_reannotation_sample.xlsx,
it deliberately shows the ground-truth span and the model disagreement for
each row, because its purpose is a structured discussion of already-known
disagreement patterns (see agreement_protocol.md §2's adjudication-of-model-
outputs track), not a fresh independent label used in a kappa/alpha
computation. The 13 rows and their content are transcribed verbatim from the
existing markdown (not edited); only the worksheet formatting/columns here
are new.
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from common import IAA_DIR

HEADER_FILL = PatternFill(start_color="6B2D5C", end_color="6B2D5C", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)

# Transcribed verbatim from results/phase2_chatlike/ali_adjudication_shortlist.md.
ROWS = [
    dict(n=1, group="A", poem="Imru2", verse=15,
         text="فَجُزِيتِ خَيْرَ جَزَاءِ نَاقَةِ وَاحِدٍ وَرَجَعْتِ سَالِمَةَ القَرَا بِسَلامِ",
         gt="«القرا» (مجاز مرسل)",
         models="Existing/A/C all flagged Trope somewhere in this verse, but anchored to «فَجُزِيتِ خَيْرَ جَزَاءِ...» - the general clause, not the specific word «القرا»",
         question="A"),
    dict(n=2, group="A", poem="Nabigha", verse=33,
         text="وَتُتبِعُهُ مِثلَ الزُّجاجَةِ لَم تُكحَل مِنَ الرَّمَدِ",
         gt="«وتُتبِعُهُ مثل الزجاجة» (مجاز مرسل)",
         models="[Phase 2 probe] Both Config C runs instead flagged «يحفّه جانبا نيقٍ» (a different phrase, earlier in the verse) as استعارة مكنية",
         question="A"),
    dict(n=3, group="A", poem="Nabigha", verse=8,
         text="مَقذوفَةٍ بِدَخيسِ النَحضِ بازِلُها لَه صَريفٌ صَريفَ القَعوِ بِالمَسَدِ",
         gt="«بالمسَدِ» (مجاز مرسل)",
         models="[Phase 2 probe] Both runs flagged «مقذوفةٍ بدخيس النحض» as استعارة instead - same general area, different word, different subtype label",
         question="A"),
    dict(n=4, group="B", poem="Imru1", verse=2,
         text="فَتُوضِحَ فالمِقْراةِ لم يَعْفُ رسْمُهَا لِمَا نَسَجَتْهَا منْ جَنُوبٍ وشَمْألِ",
         gt="«جَنُوبٍ», «وشَمْألِ» (two separate instances - the two winds)",
         models="All 3 models miss",
         question="B"),
    dict(n=5, group="B", poem="Imru1", verse=4,
         text="كَأنِّي غَدَاةَ البَيْنِ يَوْمَ تَحَمَّلوا لَدَى سَمُراتِ الحَيِّ نَاقِفُ حَنْظَلِ",
         gt="«يَوْمَ تَحَمَّلوا»",
         models="All 3 models miss",
         question="B"),
    dict(n=6, group="B", poem="Imru1", verse=25,
         text="إذا ما الثُّرَيَّا في السَّمَاءِ تَعَرَّضَتْ تَعَرَّضَ أثْنَاءِ الوِشَاحِ المُفَصَّلِ",
         gt="whole verse - note: this exact couplet is also data/elements/Simile.txt's canonical example #1 for Simile.",
         models="All 3 models miss; worth asking Ali directly whether this is Kenning/Periphrasis, Simile, or legitimately both",
         question="B"),
    dict(n=7, group="C", poem="Jarir", verse=37,
         text="وباسِطَ خير فيكمُ بيمينه وقابِضَ شر عنكمُ بشماليا",
         gt="ground truth does not tag «باسِطَ خير...وقابِضَ شر...» (extending good with the right hand, withholding evil with the left)",
         models="All 3 models agree it IS طباق/antithesis - strongest candidate in the whole shortlist for a genuine annotation gap rather than model error",
         question="C"),
    dict(n=8, group="C", poem="Abu_Tammam", verse=16,
         text="وَكَأَنَّ بَهجَتَها وَبَهجَةَ كَأسِها نارٌ وَنورٌ قُيِّدَا بِوِعَاءِ",
         gt="ground truth does not tag «نارٌ وَنورٌ» (fire and light)",
         models="2 of 3 models flag it as طباق/antithesis",
         question="C"),
    dict(n=9, group="C", poem="Nabigha", verse=48,
         text="...وَلا يَحولُ عَطاءُ اليَومِ دونَ غَدِ",
         gt="ground truth does not tag «اليوم دون غَدِ» (today vs. tomorrow)",
         models="2 of 3 models flag it as طباق/antithesis",
         question="C"),
    dict(n=10, group="D", poem="Imru1", verse=43,
         text="ولَيْلٍ كموج البَحْر مُلْقٍ سُدُولَهُ عليَّ بأنْوَاعِ الهُمُومِ لِيَبْتَلِي",
         gt="«ولَيْلٍ مُلْقٍ سُدُولَهُ...» (Trope)",
         models="Claude FP («كموج البحر...») / GPT FN / Gemini TP («مُلْقٍ سُدُولَهُ»)",
         question="D"),
    dict(n=11, group="D", poem="Imru1", verse=45,
         text="ألَا أيُّها اللَّيْلُ الطَّوِيْلُ ألا انْجَلِي بِصُبْح وما الإصْبَاحُ فِيْكَ بأمْثَلِ",
         gt="«اللَّيْلُ الطَّوِيْلُ», «انْجَلِي» (two instances, Trope)",
         models="Claude FN / GPT TP («ألا انْجَلِي») / Gemini FP («أيُّها اللَّيْلُ»)",
         question="D"),
    dict(n=12, group="D", poem="Imru1", verse=34,
         text="غَدَائِرُهُ مُسْتَشْزَرَاتٌ إلى العُلا تَضِلُّ العِقَاصُ في مُثَنًّى وَمُرْسَلِ",
         gt="«غَدَائِرُهُ مُسْتَشْزَرَاتٌ», «تَضِلُّ العِقَاصُ» (two instances, Trope)",
         models="Claude TP (caught it) / GPT FN / Gemini FN",
         question="D"),
    dict(n=13, group="D", poem="Imru2", verse=6,
         text="أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ",
         gt="«فُوهَا كُلَّمَا نَبَّهْتُهَا...» (Kenning/Periphrasis)",
         models="Existing/A/B: all miss. Phase 2 Config C: TP, both runs, with worked reasoning - the capstone example connecting Phase 1's blind spot to Phase 2's finding",
         question="D"),
]

QUESTIONS = {
    "A": "هل القراءة البديلة للنموذج مقبولة، أم أن الموضع المُعلَّم هو الصحيح فقط؟ / Is the model's alternate reading defensible, or is the annotated span the only correct one?",
    "B": "هل معيار 'إمكانية بقاء المعنى الحرفي قائمًا' يُطبَّق بشكل صحيح هنا، أم أنه مُتشدد/متساهل أكثر من اللازم؟ / Is 'the literal reading stays plausible' being judged correctly here, or is this over-/under-strict?",
    "C": "هل تحديد النموذج للطباق هو ثغرة حقيقية في التصنيف، أم أنه مبالغة فعلية من النموذج؟ / Is the model's antithesis call a real annotation gap, or genuine over-claiming?",
    "D": "عندما تختلف النماذج في نفس البيت، أيّ منها (إن وُجد) على حق؟ / Where models split on the same verse, which one (if any) is right?",
}


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Adjudication"
    ws.sheet_view.rightToLeft = True

    headers = ["#", "Group", "Poem", "Verse", "Verse text", "Ground truth / annotation note",
               "What the model(s) said", "Discussion question", "Ali's verdict (fill in)", "Notes"]
    for col, text in enumerate(headers, start=1):
        c = ws.cell(row=1, column=col, value=text)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"

    r = 2
    for row in ROWS:
        ws.cell(row=r, column=1, value=row["n"])
        ws.cell(row=r, column=2, value=row["group"])
        ws.cell(row=r, column=3, value=row["poem"])
        ws.cell(row=r, column=4, value=row["verse"])
        ws.cell(row=r, column=5, value=row["text"]).alignment = Alignment(horizontal="right", wrap_text=True)
        ws.cell(row=r, column=6, value=row["gt"]).alignment = Alignment(wrap_text=True)
        ws.cell(row=r, column=7, value=row["models"]).alignment = Alignment(wrap_text=True)
        ws.cell(row=r, column=8, value=QUESTIONS[row["question"]]).alignment = Alignment(wrap_text=True)
        ws.row_dimensions[r].height = 70
        r += 1

    widths = {1: 4, 2: 8, 3: 12, 4: 7, 5: 45, 6: 35, 7: 45, 8: 45, 9: 30, 10: 25}
    for col, w in widths.items():
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = w

    out_path = IAA_DIR / "sheets" / "adjudication_shortlist_worksheet.xlsx"
    wb.save(out_path)
    print(f"Wrote {out_path} ({len(ROWS)} rows)")


if __name__ == "__main__":
    main()
