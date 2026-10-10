# Adjudication Shortlist — Working Session with Dr. Ali Hussein

**Purpose**: 13 verses selected for quick joint review, spanning the disagreement patterns that matter most for this thesis. All model verdicts are v4_combined, 2-run majority, strict criterion (Phase 1's frozen scoring) unless marked [Phase 2 probe]. Selected from `results/pilot_3models/detailed_results.docx`'s underlying data (all 5 poems) plus Phase 2's مجاز مرسل probe (`report_3i.md` §8).

**What to ask Ali, per group**: (A) is the model's alternate reading defensible, or is the annotated span the only correct one? (B) is "the literal reading stays plausible" being judged correctly here, or is this over-strict/under-strict? (C) is the model's antithesis call a real annotation gap, or genuine over-claiming? (D) where models split on the same verse, which one (if any) is right?

## A. مجاز مرسل — model found a *different* phrase than the annotated span (3)

| # | Poem, verse | Verse text | GT span (subtype) | What the model(s) said instead |
|---|---|---|---|---|
| 1 | Imru2 v15 | فَجُزِيتِ خَيْرَ جَزَاءِ نَاقَةِ وَاحِدٍ وَرَجَعْتِ سَالِمَةَ القَرَا بِسَلامِ | «القرا» (مجاز مرسل) | Existing/A/C all flagged Trope somewhere in this verse, but anchored to «فَجُزِيتِ خَيْرَ جَزَاءِ...» — the general clause, not the specific word «القرا» |
| 2 | Nabigha v33 | وَتُتبِعُهُ مِثلَ الزُّجاجَةِ لَم تُكحَل مِنَ الرَّمَدِ | «وتُتبِعُهُ مثل الزجاجة» (مجاز مرسل) | [Phase 2 probe] Both Config C runs instead flagged «يحفّه جانبا نيقٍ» (a different phrase, earlier in the verse) as استعارة مكنية |
| 3 | Nabigha v8 | مَقذوفَةٍ بِدَخيسِ النَحضِ بازِلُها لَه صَريفٌ صَريفَ القَعوِ بِالمَسَدِ | «بالمسَدِ» (مجاز مرسل) | [Phase 2 probe] Both runs flagged «مقذوفةٍ بدخيس النحض» as استعارة instead — same general area, different word, different subtype label |

## B. Kenning — all 3 models miss (3)

| # | Poem, verse | Verse text | GT span |
|---|---|---|---|
| 4 | Imru1 v2 | فَتُوضِحَ فالمِقْراةِ لم يَعْفُ رسْمُهَا لِمَا نَسَجَتْهَا منْ جَنُوبٍ وشَمْألِ | «جَنُوبٍ», «وشَمْألِ» (two separate instances — the two winds) |
| 5 | Imru1 v4 | كَأنِّي غَدَاةَ البَيْنِ يَوْمَ تَحَمَّلوا لَدَى سَمُراتِ الحَيِّ نَاقِفُ حَنْظَلِ | «يَوْمَ تَحَمَّلوا» |
| 6 | Imru1 v25 | إذا ما الثُّرَيَّا في السَّمَاءِ تَعَرَّضَتْ تَعَرَّضَ أثْنَاءِ الوِشَاحِ المُفَصَّلِ | whole verse — **note**: this exact couplet is also `data/elements/Simile.txt`'s canonical example #1 for Simile. Worth asking Ali directly whether this is Kenning, Simile, or legitimately both — a good test case for the Trope/Kenning-adjacent boundary question already flagged in Phase 1 (`prompt_variants.py` RULE_1). |

## C. Antithesis (طباق) — models flag it, ground truth doesn't (possible annotation gap, not just over-claiming) (3)

| # | Poem, verse | Verse text | Models' claimed span | Agreement |
|---|---|---|---|---|
| 7 | Jarir v37 | وباسِطَ خير فيكمُ بيمينه وقابِضَ شر عنكمُ بشماليا | «باسِطَ خير...وقابِضَ شر...» (extending good with the right hand, withholding evil with the left) | **All 3 models agree** — this is the strongest candidate in the whole shortlist for a genuine annotation gap rather than model error |
| 8 | Abu_Tammam v16 | وَكَأَنَّ بَهجَتَها وَبَهجَةَ كَأسِها نارٌ وَنورٌ قُيِّدَا بِوِعَاءِ | «نارٌ وَنورٌ» (fire and light) | 2 of 3 models |
| 9 | Nabigha v48 | ...وَلا يَحولُ عَطاءُ اليَومِ دونَ غَدِ | «اليوم دون غَدِ» (today vs. tomorrow) | 2 of 3 models |

## D. Cross-model disagreement on the same verse — genuinely ambiguous cases (4)

| # | Poem, verse | Element | Verse text | GT span | Verdicts (Claude / GPT / Gemini) |
|---|---|---|---|---|---|
| 10 | Imru1 v43 | Trope | ولَيْلٍ كموج البَحْر مُلْقٍ سُدُولَهُ عليَّ بأنْوَاعِ الهُمُومِ لِيَبْتَلِي | «ولَيْلٍ مُلْقٍ سُدُولَهُ...» | FP («كموج البحر...») / FN / **TP** («مُلْقٍ سُدُولَهُ») |
| 11 | Imru1 v45 | Trope | ألَا أيُّها اللَّيْلُ الطَّوِيْلُ ألا انْجَلِي بِصُبْح وما الإصْبَاحُ فِيْكَ بأمْثَلِ | «اللَّيْلُ الطَّوِيْلُ», «انْجَلِي» (two instances) | FN / **TP** («ألا انْجَلِي») / FP («أيُّها اللَّيْلُ») |
| 12 | Imru1 v34 | Trope | غَدَائِرُهُ مُسْتَشْزَرَاتٌ إلى العُلا تَضِلُّ العِقَاصُ في مُثَنًّى وَمُرْسَلِ | «غَدَائِرُهُ مُسْتَشْزَرَاتٌ», «تَضِلُّ العِقَاصُ» (two instances) | **TP** (Claude caught it) / FN / FN |
| 13 | Imru2 v6 | Kenning | أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ | «فُوهَا كُلَّمَا نَبَّهْتُهَا...» | Existing/A/B: **FN** (all miss) — [Phase 2] Config C: **TP**, both runs, with full worked reasoning (see `report_3i.md` §5) — included as the capstone example connecting Phase 1's blind spot to Phase 2's finding |
