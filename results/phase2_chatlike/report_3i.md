# Phase 2 §3i — Model / Terminology / Full-Recipe Disentanglement (2026-07-23)

**Scope of this report**: Config A and Config B on full DEV (Imru2 + Nabigha, 2 runs each). Config C on **Imru2 only** (2 runs) — Nabigha's Config C was explicitly held pending a separate go/no-go (see §5). All numbers below are DEV; TEST remains untouched and spent, per standing discipline (`PROJECT_STATE.md` §2 / Phase 2 §1).

**Actual spend this cycle**: Config A $1.91, Config B $0.27, Config C (Imru2 only) $5.05 — **total $7.23**, against an approved ceiling of ~$1.85 (A+B) + $2.6–8.1 (C, Imru2-only). All three landed inside or near the approved ranges.

---

## 1. Setup recap

- **Config A** — v4_combined system message **unchanged**, run on Fable 5 (`claude-fable-5`), `effort=medium`, whole-poem (same call shape as Phase 1). Isolates the pure model effect.
- **Config B** — v4_combined with **only** the English element names corrected (antonymy→antithesis, kenning→periphrasis) plus a مجاز-subtype annotation (استعارة/تمثيل/مجاز مرسل + the two canonical examples), run on Sonnet 4.6. Isolates the pure terminology effect.
- **Config C** — two-stage, per-verse: Stage 1 is Fable 5, free-form Arabic rhetorical analysis (the user-specified prompt, used verbatim), full poem as context, one verse per call. Stage 2 is GPT-5.4-mini extracting Stage 1's free-form analysis into the unmodified strict JSONL schema. Isolates the full "chat-like" recipe (free-form reasoning + correct terminology + explicit مجاز subtypes, all at once).
- **Existing** — Phase 1's frozen Sonnet 4.6 + v4_combined DEV numbers (`results/pilot_3models/dev_variants/v4_combined/`), unchanged, used as the baseline for all three comparisons.

**A methodological fix made during scoring, not before**: Config C's Stage 1 quotes spans with Arabic guillemets (`«…»`), which `span_matching.py`'s `normalize()` didn't strip (only straight quotes were handled — this never came up in Phase 1 because no Phase 1 model ever produced guillemets). Fixed by extending `normalize()` to strip `«»` alongside `"'`. **Verified this changes zero Phase 1 frozen numbers** (a full TEST pooled-count snapshot before/after the fix was byte-identical — no Phase 1 raw output contains a guillemet). Config C's own numbers below are computed with the fix; without it, Kenning's token-criterion F1 on Imru2 reads 0.263 instead of the correct 0.421 — a real, non-trivial undercount purely from bracket characters, not content mismatches.

---

## 2. Pooled DEV (Imru2+Nabigha) — Existing vs Config A vs Config B

### Strict criterion (TP/FP/FN, F1)

| Element | Existing (Sonnet+v4) | Config A (Fable5+v4) | Config B (Sonnet+v4, terms corrected) |
|---|---|---|---|
| Trope | 2/6/58, F1=0.059 | 7/3/53, **F1=0.200** | 3/4/57, F1=0.090 |
| Simile | 14/7/6, F1=0.683 | 14/6/6, F1=0.700 | 14/7/6, F1=0.683 |
| Kenning | 5/3/64, F1=0.130 | 8/4/61, **F1=0.198** | 5/7/64, F1=0.123 |
| Antonymy (n=5, thin) | 1/6/4, F1=0.167 | 1/4/4, F1=0.200 | 0/4/5, F1=0.000 |

### Token criterion (TP/FP/FN, F1)

| Element | Existing | Config A | Config B |
|---|---|---|---|
| Trope | 2/6/58, F1=0.059 | 7/3/53, F1=0.200 | 3/4/57, F1=0.090 |
| Simile | 15/6/5, F1=0.732 | 13/7/7, F1=0.650 | 15/6/5, F1=0.732 |
| Kenning | 5/3/64, F1=0.130 | 9/3/60, F1=0.222 | 5/7/64, F1=0.123 |
| Antonymy | 3/4/2, F1=0.500 | 3/2/2, F1=0.600 | 2/2/3, F1=0.444 |

## 3. Imru2-only — Existing vs A vs B (re-sliced) vs Config C

### Strict criterion

| Element | Existing | Config A | Config B | Config C |
|---|---|---|---|---|
| Trope | 2/0/6, F1=0.400 | 1/1/7, F1=0.200 | 2/1/6, F1=0.364 | 2/13/6, F1=0.174 |
| Simile | 5/5/0, F1=0.667 | 4/5/1, F1=0.571 | 5/5/0, F1=0.667 | 4/6/1, F1=0.533 |
| Kenning | 1/0/16, F1=0.111 | 1/3/16, F1=0.095 | 2/2/15, F1=0.190 | **6/15/11, F1=0.316** |
| Antonymy (n=1, too thin) | 0/1/1, F1=0.000 | 0/2/1, F1=0.000 | 0/1/1, F1=0.000 | 0/3/1, F1=0.000 |

### Token criterion

| Element | Existing | Config A | Config B | Config C |
|---|---|---|---|---|
| Trope | 2/0/6, F1=0.400 | 1/1/7, F1=0.200 | 2/1/6, F1=0.364 | 1/14/7, F1=0.087 |
| Simile | 5/5/0, F1=0.667 | 4/5/1, F1=0.571 | 5/5/0, F1=0.667 | 5/5/0, F1=0.667 |
| Kenning | 1/0/16, F1=0.111 | 2/2/15, F1=0.190 | 2/2/15, F1=0.190 | **8/13/9, F1=0.421** |
| Antonymy | 1/0/0, F1=1.000 | 1/1/0, F1=0.667 | 1/0/0, F1=1.000 | 1/2/0, F1=0.500 |

---

## 4. Answers to the four key questions (PROJECT_STATE Phase 2 §3i)

**1. Model effect (Config A vs existing) — does Fable 5 alone move كناية/مجاز recall?**
Yes, clearly, on pooled DEV. Trope: F1 0.059→0.200 (TP 2→7, FN 58→53, FP actually *dropped* 6→3 — a genuine, precision-preserving recall gain). Kenning: F1 0.130→0.198 (TP 5→8, FN 64→61). Same prompt, same terminology, same schema — only the model changed. This is real signal, not noise: it improves both hard elements simultaneously with no precision cost, unlike every other intervention in this report or in Phase 1 (§3f/§3g), which traded precision for recall.

**2. Terminology effect (Config B vs existing) — does correct naming alone change results?**
Mixed, and smaller than the model effect — this needs a precise, not a blanket, answer. **Trope**: a modest real gain (F1 0.059→0.090, TP 2→3). **Kenning**: flat-to-slightly-worse (F1 0.130→0.123, TP unchanged at 5, FP up 3→7) — correcting "kenning"→"periphrasis" alone did **not** unlock the recall Phase 1 hoped for; it only added false positives. **Flag for the thesis, precisely stated**: Phase 1's frozen Trope numbers carry a small, real terminology caveat (correct naming alone would likely have modestly helped recall); Phase 1's frozen Kenning numbers do **not** carry this caveat — wrong terminology is not shown to be the reason Kenning stayed hard. Antonymy's B-column (F1=0.000) is on n=5 and should not be read as a real effect (see Phase 1 §3d/§6.1 on thin-denominator noise).

**3. Full recipe (Config C) — does كناية recall finally move, at what precision cost, and does it catch the target verse?**
Yes on all three counts, on Imru2. Kenning strict F1 0.111→0.316 (TP 1→6 out of GT n=16, i.e. recall roughly 6%→35%), token F1 0.111→0.421 (TP 1→8, recall ~50%) — the largest Kenning movement of any intervention tried in this project, Phase 1 included. The cost is real: precision on Imru2's Kenning is low (6 TP against 15 FP strict), consistent with Phase 1's established pattern that every recall-improving intervention here trades precision (§3f, §3g) — but this is the first intervention where the recall side of that trade is large rather than marginal. **And yes — it catches the specific verse.** Imru2 verse 6 («أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ»): ground truth marks كناية at «فُوهَا كُلَّمَا نَبَّهْتُهَا... »; Existing, Config A, and Config B **all** miss it (Kenning exists=False for all three); Config C correctly flags Kenning exists=True with appearance «كُلَّمَا نَبَّهْتُهَا», in **both** runs, with a substantively correct rhetorical justification (see §5 for the full quoted analysis). This is the chat-gap observation, replicated inside the harness rather than anecdotally.

**4. Do Phase 1's hard مجاز مرسل misses (§3c) change under Config C?**
**Inconclusive from Imru2 alone — flagging this rather than overstating a read.** Imru2's ground truth contains exactly **one** مجاز مرسل instance (verse 15, span «القرا»), and none of the four configs (Existing, A, B, C) caught it — Config A and Config C both flagged Trope as present in that verse but pointed at a different sub-span («فَجُزِيتِ خَيْرَ جَزَاءِ...» rather than «القرا» specifically), so it's not a clean miss either. n=1 is far too thin to answer this question either way (thinner even than Phase 1's own DEV n, which §3c already flagged as unreliable for subtype-level conclusions). Nabigha would need to be included to say anything real here — this is one more concrete reason (beyond the recall/cost picture in §3) to consider extending Config C to Nabigha, not just a side note.

---

## 5. Verse-specific case study — Imru2 verse 6

**Verse**: أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ

**Ground truth** (Dr. Ali Hussein): Simile at «فُوهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ» (تشبيه); Kenning at «فُوهَا كُلَّمَا نَبَّهْتُهَا كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ» (كناية بسيطة). No Trope, no Antonymy marked.

| Config | Trope | Simile | Kenning | Antonymy |
|---|---|---|---|---|
| Existing (Sonnet+v4, frozen) | False | True — «كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ» | **False** | False |
| Config A (Fable5+v4) | False | True — «كَالمِسْكِ» | **False** | False |
| Config B (Sonnet+v4-term) | False | True — «كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ» | **False** | False |
| Config C (2-stage) | False | True — «كَالمِسْكِ» | **True — «كُلَّمَا نَبَّهْتُهَا»** | True — «بَاتَ وَظَلَّ» (not in GT — a false positive) |

Only Config C catches the كناية. It also flags طباق at «بَاتَ وَظَلَّ» ("was at night" / "remained by day"), which ground truth does not mark — a genuine false positive, consistent with Config C's broader precision cost documented in §3.

**Config C's Stage 1 free-form analysis, run 1, quoted in full** (the reasoning behind the correct كناية call):

> ## تحليل البيت السادس
>
> **"أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا / كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ"**
>
> (الفَدّام: خرقة أو مصفاة تُوضع على فم الإناء، فيبقى ما فيها محفوظَ الرائحة)
>
> ### ١. المجاز
> **موجود، وهو مجاز مرسل** في قوله **«فُوهَا»**: الشاعر لم يُرِد الفم بذاته (العضو)، وإنما أراد **ريقها ورائحة فمها**؛ إذ لا يُشبَّه الفم نفسه بالمسك، وإنما تُشبَّه رائحته وطعمه. فهو من إطلاق **المحلّ وإرادة الحالّ فيه** (علاقته المحلّية)، كقولهم «شربتُ الكأس» والمشروب ما فيها.
>
> ### ٢. التشبيه
> **موجود صريح بأداة ظاهرة** هي الكاف في **«كَالمِسْكِ»**: المشبَّه فوها (أي ريقها ورائحته حين تستيقظ)؛ المشبَّه به مركّب، وهو «المسك الذي بات وظل في الفدّام»؛ نوعه تشبيه مرسل، أقرب إلى **التشبيه التمثيلي**؛ وجه الدلالة المبالغة في طيب فمها.
>
> ### ٣. الكناية
> **موجودة** من وجهين:
> - **«كُلَّمَا نَبَّهْتُهَا»**: كناية عن **قربه منها وخلوته بها ومبيته عندها**؛ إذ لا يوقظها من نومها إلا من كان ملاصقاً لها، مع جواز إرادة المعنى الأصلي (الإيقاظ الحقيقي).
> - تخصيصُ طيب فمها بوقت التنبيه من النوم كناية عن **صفة**: أنها طيبةُ النكهة أصالةً لا تصنّعاً.
>
> ### ٤. الطباق
> **موجود** في قوله **«بَاتَ وَظَلَّ»**: «بات» تفيد الكينونة ليلاً، و«ظلّ» تفيد الكينونة نهاراً، فجمع بين الزمنين المتضادين في سياق واحد. وهو **طباق إيجاب**، وفائدته الدلالة على **دوام** احتباس المسك في الفدّام.
>
> **الخلاصة:** البيت جامع للفنون الأربعة: مجاز مرسل في «فوها»، وتشبيه تمثيلي مرسل في «كالمسك بات وظل في الفدّام»، وكناية في «كلما نبهتها»، وطباق بين «بات» و«ظلّ».

(Run 2's independent analysis reaches the same كناية verdict on «كُلَّمَا نَبَّهْتُهَا» by similar reasoning — see `results/phase2_chatlike/config_c/Imru2/stage1_analysis_run2.json` for the full text — so this is not a one-run fluke.)

---

## 6. Cost, actual vs estimated

| Config | Estimated | Actual |
|---|---|---|
| A (full DEV) | $0.91–$1.58 | $1.91 |
| B (full DEV) | ≈$0.27 | $0.27 |
| C (Imru2 only) | $2.6–$8.1 | $5.05 |
| **Total** | | **$7.23** |

Config C's measured Stage 1 average: **~2,447 input / ~1,681 output tokens per call** at `effort=medium` — this replaces the earlier blind 600–3,000 output-token guess. Extending Config C to Nabigha (50 verses × 2 runs = 100 pairs), using this measured average and Nabigha's actual `count_tokens` input (~3,443/call), is estimated at **≈$11.9** (Stage 1 ≈$11.85 + Stage 2 ≈$0.07), bringing Config C's full-DEV total to ≈$17 and the whole §3i cycle to ≈$19.

---

## 7. Open item — Nabigha extension

**Not run. Awaiting explicit confirmation**, per the approved scope (Imru2-only first). Reasons to consider it, weighed honestly:

- **For**: question 4 (مجاز مرسل) is genuinely unanswerable from Imru2's n=1; Nabigha would give a real read. The Kenning recall gain (question 3) is large on one poem — Phase 1's own §3g/§6.9 lesson is explicit that a single-poem effect size should never be quoted as if it generalizes, and this project already has one on-the-record instance (Gemini's per-verse Kenning gain shrinking from +152% to +11% between poems) of exactly this kind of number not surviving a second poem.
- **Against**: ≈$11.9 more, on a config whose defining trait so far is a large precision cost (more FP than TP on Kenning even with the recall win) — extending it doesn't change that trade-off, only tests whether the trade-off's *size* replicates.

No recommendation is substituted for your decision here — flagging the considerations, not the call.

---

## 8. Addendum (2026-07-23, later same day) — Nabigha مجاز مرسل targeted recall probe

**This section is a TARGETED RECALL PROBE, not an evaluation.** Every verse below was selected *because* it is a known ground-truth positive (or, for the 2 contrast verses, a known positive for a different Trope subtype). There is no negative-verse sample here, so **no precision, recall-as-a-rate-over-a-representative-set, or F1 number is computed or claimed anywhere in this section** — only per-instance hit/miss on verses already known to contain the target figure. The full-poem Config C run on Nabigha (which *would* support real precision/F1 claims) remains **not run**, held open for budget reasons — this probe answers question 4 only, cheaply, without committing to that larger spend.

**Scope**: Config C's unchanged recipe (Stage 1 Fable 5 free-form analysis, verbatim prompt, full poem context, `effort=medium`; Stage 2 GPT-5.4-mini extraction into the strict schema), run on 11 hand-picked Nabigha verses, 2 runs each = 22 stage-pairs. 9 verses contain Nabigha's entire ground-truth مجاز مرسل population (10 instances — one verse, #7, has two). 2 contrast verses (v2: استعارة فعل, v5: مجاز عقلي) check whether the same recipe reliably catches subtypes Phase 1 already found tractable (§3c: "v4's real, validated wins are استعارة فعل and مجاز عقلي").

**Cost**: estimated ≈$2.42 at the Imru2-measured $0.1098/pair average; actual **$2.73** (75,820 Stage-1 input / 38,864 Stage-1 output / 24,851 Stage-2 input / 2,100 Stage-2 output tokens, zero errors across all 22 pairs).

**Methodology note**: hit/miss is judged **per run**, and a verse-instance is called "caught" if **either** of the 2 independent runs hit it (not the 2-run-majority convention used in §2–§3's comparative tables). This is a deliberate choice for a recall-only probe: majority-vote would sometimes report "not detected" even when one of two independent readings did find the exact right span (see v7, v14, v30 below, where the two runs disagree on which phrase to foreground) — collapsing that to a single majority verdict would hide the real signal of whether the reasoning *can* find the instance at all, which is what question 4 asks.

### مجاز مرسل instances (9 verses, 10 instances)

| Verse | GT span | Run 1 verdict (stage-1 excerpt) | Run 2 verdict (stage-1 excerpt) | Strict hit | Token hit |
|---|---|---|---|---|---|
| 4 | «الثأدِ» | «ردّت عليه أُقاصيه» — مجاز عقلي (إسناد إلى غير فاعله) | «ولبّده ضربُ الوليدة» — مجاز عقلي (إسناد إلى السبب) | ✗ | ✗ |
| 7 | «القُتُودَ» / «له،» | «عَيْرانة» — استعارة/تشبيه مطوي (missed القتود) | **«القُتُود» — مجاز مرسل علاقته الجزئية** (ذكر الجزء وأراد الكل) | ✓ (run2) | ✓ (run2) |
| 8 | «بالمسَدِ» | «مقذوفةٍ بدخيس النحض» — استعارة تبعية | «مقذوفةٍ بدخيس النحض» — استعارة تبعية (same, different span) | ✗ | ✗ |
| 10 | «المصير،» | «مَوشيٍّ أكارعُهُ» — استعارة تبعية (different word) | «مَوْشِيٍّ أكارعُهُ» — استعارة (same) | ✗ | ✗ |
| 14 | «طعن» | **«طعن المُعارك» — استعارة مكنية/تبعية** | «لا مجاز مستقلاً في البيت» (exists=False) | ✓ (run1) | ✓ (run1) |
| 16 | «صفحته،» | «ليس في البيت استعارة ولا مجاز مرسل» (exists=False) | extraction artifact — appearance came back as the literal word "التمثيل" (a stage-2 mis-extraction, not a real quote) | ✗ | ✗ |
| 30 | «والراكضاتِ ذيولَ الريط،» | «فانَقها بردُ الهواجرِ» — استعارة مكنية / قريب من مجاز مرسل | **«الراكضاتِ ذيولَ الريط» — مجاز (ركض مستعمَل توسّعاً)** | ✓ (run2) | ✓ (run2) |
| 33 | «وتُتبِعُهُ مثل الزجاجة،» | «يحفّه جانبا نيقٍ» — استعارة مكنية (different phrase) | «يحفّه جانبا نيقٍ» — استعارة مكنية (same; run2 does separately note «مثل الزجاجة» but as simile, not مرسل) | ✗ | ✗ |
| 47 | «بالخيزُرانةِ،» | **«الخيزُرانة» — مجاز مرسل، علاقته اعتبار المادة (تسمية الشيء باسم ما صُنع منه)** | **«الخيزُرانة» — مجاز مرسل (same reasoning, same span)** | ✓ (both) | ✗ (both — GT span carries the attached ب-prefix and trailing ة marker that the model's bare quote doesn't reproduce; token-overlap has no rule for this prefix, only و/ف, so it doesn't recover the match the way strict's substring check does) |

**مجاز مرسل: 4 of 9 verses caught in at least one of 2 runs** (v7, v14, v30, v47 strict; v7/v14/v30 also token — v47 is strict-only, a token-matching artifact, not a real miss). 5 of 9 (v4, v8, v10, v16, v33) were not caught by either run *at that specific span* — though in 4 of those 5 (all but v16), both runs did identify **some** figurative device in the verse's general vicinity, just classified as a different subtype (usually استعارة) or anchored to a different word than Dr. Hussein's exact annotation. v16 is a genuine two-run agreement that no مجاز exists in that verse at all (a real, clean miss) — plus one stage-2 extraction artifact (the literal word "التمثيل" leaking into the appearance field) worth noting as a pipeline defect, not a model-reasoning defect.

*Denominator note: counted per verse (9), not per GT instance (10) — v7 has two co-located مجاز مرسل instances («القُتُودَ», «له،») but the extraction schema records only one `مجاز_appearance` per verse-call, so a single verse-call can never register more than one hit there regardless of how many instances the ground truth lists. Per-instance counting would overstate the number of independent catch opportunities.*

### Contrast verses (other subtypes)

| Verse | GT span | Run 1 | Run 2 | Strict | Token |
|---|---|---|---|---|---|
| 2 (استعارة فعل) | «عَيّتْ جواباً،» | «أُسائِلُها... عَيَّتْ جواباً» — استعارة مكنية (تشخيص) | «أُسائِلها ... عَيّتْ جواباً» — استعارة مكنية (same) | ✗ (both — model's quote links two non-adjacent phrases with a literal "..." ellipsis, breaking substring containment even though the target phrase is present) | ✓ (both) |
| 5 (مجاز عقلي) | «سبيل أتِيٍّ كانَ يحبسهُ،» | **«كان يحبسهُ» — استعارة مكنية (تشخيص)** | «خلّت سبيلَ أتيٍّ كان يحبسهُ» — استعارة مكنية (same figure, longer quote) | ✓ (run1) / ✗ (run2 — GT's trailing Arabic comma isn't reproduced in run2's longer quote, breaking strict containment) | ✓ (both) |

**Contrast: 2/2 caught in at least one run, on both criteria** (token: 2/2 both runs; strict: at least one run each). This matches §3c's finding that استعارة فعل and مجاز عقلي are the subtypes v4_combined already handles reasonably — the recipe doesn't regress on them.

### Answer to the framing question, per instance then overall

**Per instance**: of the 9 مجاز مرسل ground-truth verses, the recipe (free-form reasoning with مجاز مرسل explicitly named and exemplified via «السماء تمطر»/«أراني أعصر خمراً» in the prompt) caught 4 in at least one of 2 runs (v7, v14, v30, v47), missed the specific annotated span in 5 (v4, v8, v10, v16, v33) while still identifying *some* rhetorical device nearby in 4 of those 5 (all but v16). Pooled with Imru2's single instance (verse 15, «القرا», missed in both runs — see §5), the combined probe is **4 of 10 known-positive verses caught, strict criterion; 3 of 10, token criterion** (counting per verse, not per GT instance — v7's 2 co-located instances share one catch opportunity since the schema records only one appearance per verse-call; v47's strict-only match doesn't carry to token).

**One sentence**: naming and exemplifying مجاز مرسل explicitly in a free-form-reasoning prompt gets the model to catch roughly two-fifths of lexicalized-metonymy verses in at least one of two independent readings (4/10 strict, 3/10 token — counting per verse, since the extraction schema allows only one appearance span per verse-call, so v7's 2 co-located instances share a single catch opportunity, not two) — a directional improvement over Phase 1's flat ~15% recall (§3c) — but it is inconsistent run-to-run on which specific instance gets foregrounded (3 of the 4 hits came from only one of the two runs), and this probe's methodology (any-of-2-runs, single recipe, n=10 verses, known-positive-only) is different enough from Phase 1's pooled-3-model 2-run-majority TEST measurement that the two numbers should be read as suggestive of a real but partial effect, not as directly comparable figures.

**Nabigha's full-poem Config C run remains open, not run, for budget reasons** — this probe answers question 4 economically but does not produce (and was never intended to produce) the precision/F1 picture a full run would.

---

## 9. Closing verdict

**The three-variable decomposition holds up as three genuinely different effects, not three flavors of the same thing.**

| Variable | What it moves | What it doesn't move | Cost |
|---|---|---|---|
| **Model** (Config A: Fable 5, same prompt/terms as existing) | Trope and Kenning recall, pooled DEV, **with no precision cost** (Trope F1 0.059→0.200, Kenning 0.130→0.198; FP flat or down on both) | Simile, Antonymy (already near-ceiling or too thin to move) | Free to isolate — same prompt, same schema, only the model call changed |
| **Terminology** (Config B: corrected names, same model) | Trope, modestly (F1 0.059→0.090) | Kenning — flat to slightly worse (F1 0.130→0.123); wrong naming is **not** shown to be the reason Kenning stayed hard | Free to isolate — same model, only text changed |
| **Format** (Config C: free-form reasoning + correct terms + named/exemplified مجاز subtypes, per-verse) | Kenning recall substantially, on Imru2 (strict F1 0.111→0.316; token 0.111→0.421) — the largest Kenning movement of any intervention in this project, Phase 1 included; **catches the exact motivating verse** in both runs | Trope and Simile get *worse* on Imru2 (precision collapses under FP volume); مجاز مرسل only partially (see below) | The expensive one — per-verse batching repeats full-poem context every call, the known 4-8× cost tax from Phase 1 §3g, compounded by Fable 5's always-on thinking |

**Only the model effect is a clean win** (recall up, precision unchanged). Terminology is a small, real, element-specific effect — worth a caveat in the thesis for Trope, not for Kenning. Format is the largest lever on the hardest element (Kenning) but is not a free lunch: it buys that recall by spending precision, consistent with every recall-improving intervention this project has ever tried (Phase 1 §3f, §3g; Phase 2 Config C Imru2-only table, §3).

**مجاز مرسل probe, stated under both counting conventions** (see §8 for full detail):

| Convention | Result | Why it differs |
|---|---|---|
| Any-of-2-runs (used in §8, appropriate for a recall-only probe) | **4/10 strict, 3/10 token** (per verse — see §8 footnote on why instances, not verses, would double-count v7) | Counts a verse as caught if *either* independent run found it — appropriate when the question is "can the reasoning find this at all," not "does it reliably decide this" |
| 2-run majority (the project's standard comparative convention, used in §2–§3) | **1/10 strict, 0/10 token** (only v47 keeps a majority under strict, and even that fails token; v7/v14/v30 each had exactly one run catch it, which a majority vote reports as "not detected") | This is the convention used for every comparative F1 number in this report and in Phase 1 — applying it here shows almost the entire probe signal evaporates, because the recipe didn't independently reach the same conclusion twice |

**This gap is the finding, not a methodological inconvenience to paper over.** It is not that one convention is "right" and the other "wrong" — they answer different questions. Any-of-2-runs answers "is the correct reading reachable by this recipe at all" (yes, for 4 of 10 known-positive verses). 2-run majority answers "does this recipe reliably decide the correct answer" (no — for 3 of those 4 verses, a second independent run reached a different conclusion about which phrase in the verse deserved the مجاز مرسل tag). **Determinism is unavailable by design here, not by an implementation shortfall**: Stage 1 is genuinely free-form reasoning over an open-ended "what rhetorical devices exist in this verse" question, with no fixed answer key constraining where attention lands — unlike the strict-JSON pipelines (Existing, Config A, Config B), which ask a closed yes/no question per element and so have much less room for two runs to disagree about *what* they're even answering. Buying Kenning/مجاز مرسل recall through free-form reasoning appears to trade not only precision (documented above) but also **run-to-run reproducibility of the specific correct answer** — a cost that doesn't show up in a single-run read of the probe and only becomes visible by holding both conventions side by side, as done here.

**Net for the thesis**: Config A's model effect is the safest, most portable finding (clean, precision-free, replicates without caveat). Config B's terminology caveat is real but small and Trope-specific. Config C is genuine evidence that free-form reasoning *can* reach the right answer on hard, previously-flat instances (Kenning, some مجاز مرسل) that no strict-JSON configuration — Phase 1 or Phase 2 — ever reached, but it is not yet a reliable *decision* procedure for those instances, only a reachable one.

