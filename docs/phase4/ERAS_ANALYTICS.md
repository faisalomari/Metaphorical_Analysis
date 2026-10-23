# Poet Death-Year / Era Analytics

Generated 2026-10-23 12:10 UTC by `scripts/build_eras_report.py` from `data/ali_poems/poet_dates.csv` + `experiments/phase4_e1_v2/config/eras_axis.json` (itself built from `data/ali_poems/manifest.csv` + `data/ali_poems/poems/*.json` by `experiments/phase4_e1_v2/eras_analytics.py`). No number below is hand-typed.

Verse counts exclude poem 28601 (no verse text; the only annotated-but-textless poem in the corpus, per the task's explicit instruction).

## 1. Corpus coverage

- Poets total: **52**
- Poets with a reliable death year (any confidence): **36**
- Poets without a reliable death year: **16** (listed in §6, excluded from every year-indexed statistic below)

## 2. Central tendency and axis midpoint

| Statistic | Value (CE) |
|---|---|
| Median, weighted by verses (**PRIMARY** -- see note below) | 784.0 |
| Median, weighted by poems | 814.0 |
| Median, plain per-poet (unweighted) | 730.5 |
| Mean, weighted by verses | 765.7 |
| Mean, weighted by poems | 779.5 |
| Mean, plain per-poet (unweighted) | 765.4 |
| **Midpoint of the time axis** ((min+max)/2) | 917.5 |
| Range | 544 - 1291 |

**Why verse-weighted is PRIMARY**: every other metric in this project (CLAUDE.md rule 4, the 2026-10-14 verse-primary decision) is computed per verse-unit, not per poem or per poet; the verse-weighted median is the one all band/half/extreme definitions below are built on. The midpoint is a property of the axis's *range*, not of its *distribution* -- reported separately because it answers a different question ("what year is exactly between the earliest and latest death?" vs. "where is the bulk of the corpus's verses centered?").

## 3. Bands and extremes (relative to the verse-weighted median)

- **Middle band**: within ±75 years of the median (784.0), i.e. 709.0–859.0 CE.
- **First half**: death_year_ce < 784.0. **Second half**: >= 784.0. First-half median = 635.0, second-half median = 845.0.
- **Extremes**: earliest/latest 15% of dated poets by rank, sorted by death year (ties at the boundary year are all included, so a group can be slightly larger than the exact percentage). Earliest-extreme threshold: <= 635 CE. Latest-extreme threshold: >= 897 CE.

| Group | Poets | Poems | Verses |
|---|---|---|---|
| First half | 23 | 50 | 1262 |
| Second half | 13 | 86 | 1725 |
| Middle band | 15 | 82 | 1637 |
| Earliest extreme | 6 | 22 | 652 |
| Latest extreme | 6 | 10 | 295 |

## 4. By 100-year death-year bin

| Bin (CE) | Poets | Poems | Verses | استعارة فعل positive verses |
|---|---|---|---|---|
| 500-599 | 2 | 4 | 230 | 83 |
| 600-699 | 10 | 27 | 600 | 160 |
| 700-799 | 12 | 31 | 735 | 234 |
| 800-899 | 7 | 67 | 1215 | 513 |
| 900-999 | 4 | 6 | 193 | 82 |
| 1200-1299 | 1 | 1 | 14 | 3 |

## 5. By site era (الفترة)

| Era | Poets (dated) | Poems | Verses | استعارة فعل positive verses |
|---|---|---|---|---|
| العصر العباسي | 13 (11) | 75 | 1451 | 614 |
| العصر الجاهلي | 9 (5) | 29 | 768 | 240 |
| العصر الأموي | 17 (14) | 28 | 537 | 231 |
| مخضرم الدولتين | 2 (2) | 14 | 359 | 62 |
| مخضرم | 5 (3) | 7 | 199 | 51 |
| الخلفاء الراشدون | 1 (0) | 7 | 35 | 17 |
| (blank) | 3 (0) | 5 | 107 | 40 |
| غير معروف | 1 (0) | 1 | 0 | 0 |
| العصر المملوكي | 1 (1) | 1 | 14 | 3 |

## 6. Poets without a reliable death year

Excluded from every year-indexed statistic above (§2-5); their poems/verses still count toward corpus totals in §1 and in the by-era table (§5)'s poem/verse columns, just not the dated-poet columns.

| Poet | Reason |
|---|---|
| ربيعة بن مقروم | No reliable source found for death year; sources describe him as a mukhadram warrior-poet (fought at al-Qadisiyyah) but give no date of death. |
| ابن قيس الرُّقيّات | No reliable source found for an actual death year; a library authority record lists him as 'active 657-704' (an activity span, not a death date), and no biographical source found gives a specific death year. |
| مُليح بن الحكم | No reliable source found. Note: do not confuse with the hadith transmitter 'Abu al-Malih al-Hudhali' (d. 101-112 AH), a different person despite the similar name, who turned up repeatedly in searches for this poet. |
| المُرقِّشُ الأَصغر | No reliable source found for a death year. Pre-Islamic; described as nephew of al-Muraqqish al-Akbar and paternal uncle of Tarafa ibn al-'Abd, which places him in roughly the same mid-6th-century CE generation, but no specific year is documented in available sources. |
| السموأل بن عادياء | No reliable source found for a death year; sources (Jawad Ali's al-Mufassal, al-Zirikli's al-A'lam per citation only) describe his legendary 'loyalty' story (refusing to surrender Imru' al-Qais's armor) but none in this search gave a date of death, and some researchers question the story's historicity altogether. |
| تأبّطَ شَرًّا | No reliable source found for a specific death year. Wikipedia gives only an era ('late 6th or early 7th century CE'); an old English translation on Wikisource offers two speculative readings (shortly before 569 CE, the year of Muhammad's birth, or sometime in the 40 years between 569 and 609 CE), neither treated as established. |
| النجاشي الحارثي | No reliable source found for death year; described as a mukhadram satirist from Najran who settled in Kufa and was threatened by both 'Umar ibn al-Khattab and 'Ali, but no source found gives a date of death. |
| يزيد بن مفرغ الحميري | No reliable source found for death year; sources describe his conflict with and satire of 'Abbad ibn Ziyad under Umayyad governor 'Ubayd Allah ibn Ziyad, but none found gives a date of death. |
| أيمن بن خريم | No reliable source found for death year; biographical dictionaries found describe his lineage and a poem of reproach to Mu'awiya but give no date of death. |
| الحمدوي | No reliable source found for a specific death year. One source describes him as named after his grandfather Hamduwayh, who carried out the execution of heretics (zandaqa) under Harun al-Rashid (r. 786-809 CE), placing the poet in the early-to-mid Abbasid period, but no death year is given. |
| مجهول (شعراء عباسيون منسيون) | Anonymous/collective attribution ('unknown -- forgotten Abbasid poets'), not an individual -- no individual death year applicable. |
| عبيد بن الأخطل | No reliable source found. Search results only ever returned information about the major Umayyad poet al-Akhtal (Ghiyath ibn Ghawth al-Taghlibi, d. ~90-92 AH) or about the unrelated pre-Islamic poet 'Ubayd ibn al-Abras -- neither is confirmed as the same person as this corpus entry, and no source describing an 'Ubayd ibn al-Akhtal' was found. |
| عبد الله بن عبد الحميد اللاحقي | No reliable source found. Likely related to the attested poet Aban ibn 'Abd al-Hamid al-Lahiqi (same nisba/patronymic pattern), but no source found confirms the relationship or gives any biographical/death information for this specific name. |
| المُرَقِّشُ الأكبر (عمرو بن سعد بن مالك) | No reliable source found for a death year. One source mentions he worked as a scribe for al-Harith ibn Abi Shamir al-Ghassani 'around 524 CE' (a career anecdote, not a death date, and sourced from only one site); he died before his nephew al-Muraqqish al-Asghar. |
| القرآن الكريم | Not an individual poet -- Qur'anic text; no death year applicable. |
| زياد بن حنظلة | No reliable source found for a specific death year; described as a warrior-poet who fought in the Rashidun-era conquests (including against the apostates under Abu Bakr), which places him in the 7th century CE per the site's own period label, but no source found gives an actual death date. |

## 7. Cumulative curve (by death year, ascending)

| Poet | Death year (CE) | Cumulative poets | Cumulative poems | Cumulative verses |
|---|---|---|---|---|
| امرؤ القيس | 544 | 1 | 2 | 104 |
| طرفة بن العبد  | 569 | 2 | 4 | 230 |
| علقمة بن عبدة الفحل | 603 | 3 | 5 | 285 |
| النابغة الذبياني | 604 | 4 | 19 | 572 |
| الأعشى ميمون | 629 | 5 | 21 | 628 |
| النمر بن تولب العكلي | 635 | 6 | 22 | 652 |
| الخنساء بنت عمرو بن الشريد | 646 | 7 | 23 | 663 |
| أبو ذؤيب الهذلي  | 649 | 8 | 25 | 757 |
| عبيد الله بن الحر | 687 | 9 | 26 | 771 |
| قيس بن ذريح | 687 | 10 | 28 | 792 |
| قيس بن المُلَوَّح (مجنون ليلى) | 688 | 11 | 30 | 818 |
| قطري بن الفجاءة المازني | 698 | 12 | 31 | 830 |
| جميل بن معمر | 701 | 13 | 33 | 876 |
| عمران بن حطان | 703 | 14 | 34 | 892 |
| عمر بن أبي ربيعة | 712 | 15 | 35 | 914 |
| الحكم بن عبدل | 719 | 16 | 36 | 941 |
| الفرزدق | 728 | 17 | 39 | 1033 |
| جرير بن عطيّة | 728 | 18 | 41 | 1094 |
| عبد الله بن عمر العرجي | 733 | 19 | 43 | 1127 |
| ذو الرُّمّة | 735 | 20 | 44 | 1154 |
| الطرماح بن حكيم | 743 | 21 | 46 | 1179 |
| الكميت بن زيد الأسدي | 743 | 22 | 48 | 1206 |
| أبو دلامة | 777 | 23 | 50 | 1262 |
| بشار بن برد | 784 | 24 | 62 | 1565 |
| أبو نواس | 814 | 25 | 92 | 2022 |
| أبان بن عبد الحميد اللاحقي | 815 | 26 | 93 | 2036 |
| محمد بن يسير الرياشي | 830 | 27 | 94 | 2050 |
| أبو تمّام | 845 | 28 | 106 | 2382 |
| ديك الجن | 849 | 29 | 116 | 2529 |
| ابن الرومي | 896 | 30 | 126 | 2692 |
| البحتري | 897 | 31 | 129 | 2780 |
| الصنوبري | 945 | 32 | 130 | 2806 |
| المتنبي | 965 | 33 | 132 | 2893 |
| أبو فراس الحمداني | 968 | 34 | 134 | 2961 |
| محمد بن هاشم (ابو بكر الخالدي) | 996 | 35 | 135 | 2973 |
| عفيف الدين التلمساني | 1291 | 36 | 136 | 2987 |

## 8. Full per-poet table

| Poet | Period | Death year (CE) | Death year (AH) | Approx.? | Confidence | Poems | Verses | استعارة فعل positive |
|---|---|---|---|---|---|---|---|---|
| أبان بن عبد الحميد اللاحقي | العصر العباسي | 815 | 200 | yes | low | 1 | 14 | 2 |
| أبو تمّام | العصر العباسي | 845 | 231 | no | high | 12 | 332 | 152 |
| أبو دلامة | مخضرم الدولتين | 777 | 161 | no | medium | 2 | 56 | 18 |
| أبو ذؤيب الهذلي  | مخضرم | 649 |  | yes | medium | 2 | 94 | 14 |
| أبو فراس الحمداني | العصر العباسي | 968 | 357 | no | high | 2 | 68 | 31 |
| أبو نواس | العصر العباسي | 814 | 199 | yes | high | 30 | 457 | 173 |
| أيمن بن خريم | العصر الأموي |  |  |  |  | 1 | 10 | 3 |
| ابن الرومي | العصر العباسي | 896 | 283 | no | high | 10 | 163 | 68 |
| ابن قيس الرُّقيّات | العصر الأموي |  |  |  |  | 3 | 46 | 17 |
| الأعشى ميمون | العصر الجاهلي | 629 | 7 | yes | medium | 2 | 56 | 19 |
| البحتري | العصر العباسي | 897 | 284 | no | high | 3 | 88 | 35 |
| الحكم بن عبدل | العصر الأموي | 719 | 100 | yes | low | 1 | 27 | 7 |
| الحمدوي | (blank) |  |  |  |  | 3 | 20 | 6 |
| الخنساء بنت عمرو بن الشريد | مخضرم | 646 |  | yes | low | 1 | 11 | 5 |
| السموأل بن عادياء | العصر الجاهلي |  |  |  |  | 1 | 23 | 9 |
| الصنوبري | العصر العباسي | 945 | 334 | no | high | 1 | 26 | 14 |
| الطرماح بن حكيم | العصر الأموي | 743 |  | yes | low | 2 | 25 | 11 |
| الفرزدق | العصر الأموي | 728 | 110 | no | high | 3 | 92 | 44 |
| القرآن الكريم | (blank) |  |  |  |  | 1 | 45 | 18 |
| الكميت بن زيد الأسدي | العصر الأموي | 743 | 126 | no | high | 2 | 27 | 17 |
| المتنبي | العصر العباسي | 965 | 354 | no | high | 2 | 87 | 30 |
| المُرقِّشُ الأَصغر | العصر الجاهلي |  |  |  |  | 2 | 41 | 21 |
| المُرَقِّشُ الأكبر (عمرو بن سعد بن مالك) | العصر الجاهلي |  |  |  |  | 4 | 50 | 21 |
| النابغة الذبياني | العصر الجاهلي | 604 |  | yes | medium | 14 | 287 | 73 |
| النجاشي الحارثي | مخضرم |  |  |  |  | 2 | 56 | 11 |
| النمر بن تولب العكلي | مخضرم | 635 | 14 | yes | low | 1 | 24 | 12 |
| امرؤ القيس | العصر الجاهلي | 544 |  | yes | medium | 2 | 104 | 33 |
| بشار بن برد | مخضرم الدولتين | 784 | 168 | no | high | 12 | 303 | 44 |
| تأبّطَ شَرًّا | العصر الجاهلي |  |  |  |  | 1 | 26 | 14 |
| جرير بن عطيّة | العصر الأموي | 728 | 110 | no | high | 2 | 61 | 29 |
| جميل بن معمر | العصر الأموي | 701 |  | yes | medium | 2 | 46 | 26 |
| ديك الجن | العصر العباسي | 849 | 236 | yes | medium | 10 | 147 | 76 |
| ذو الرُّمّة | العصر الأموي | 735 | 117 | no | high | 1 | 27 | 8 |
| ربيعة بن مقروم | مخضرم |  |  |  |  | 1 | 14 | 9 |
| زياد بن حنظلة | الخلفاء الراشدون |  |  |  |  | 7 | 35 | 17 |
| طرفة بن العبد  | العصر الجاهلي | 569 |  | yes | medium | 2 | 126 | 50 |
| عبد الله بن عبد الحميد اللاحقي | العصر العباسي |  |  |  |  | 1 | 19 | 11 |
| عبد الله بن عمر العرجي | العصر الأموي | 733 | 115 | yes | low | 2 | 33 | 12 |
| عبيد الله بن الحر | العصر الأموي | 687 | 68 | yes | low | 1 | 14 | 8 |
| عبيد بن الأخطل | العصر العباسي |  |  |  |  | 1 | 24 | 8 |
| عفيف الدين التلمساني | العصر المملوكي | 1291 | 690 | no | high | 1 | 14 | 3 |
| علقمة بن عبدة الفحل | العصر الجاهلي | 603 |  | yes | low | 1 | 55 | 0 |
| عمر بن أبي ربيعة | العصر الأموي | 712 |  | yes | low | 1 | 22 | 10 |
| عمران بن حطان | العصر الأموي | 703 | 84 | yes | medium | 1 | 16 | 8 |
| قطري بن الفجاءة المازني | العصر الأموي | 698 | 79 | no | high | 1 | 12 | 9 |
| قيس بن المُلَوَّح (مجنون ليلى) | العصر الأموي | 688 |  | yes | low | 2 | 26 | 10 |
| قيس بن ذريح | العصر الأموي | 687 | 68 | yes | low | 2 | 21 | 10 |
| مجهول (شعراء عباسيون منسيون) | غير معروف |  |  |  |  | 1 | 0 | 0 |
| محمد بن هاشم (ابو بكر الخالدي) | العصر العباسي | 996 | 386 | yes | medium | 1 | 12 | 7 |
| محمد بن يسير الرياشي | العصر العباسي | 830 | 215 | yes | low | 1 | 14 | 7 |
| مُليح بن الحكم | (blank) |  |  |  |  | 1 | 42 | 16 |
| يزيد بن مفرغ الحميري | العصر الأموي |  |  |  |  | 1 | 32 | 2 |
