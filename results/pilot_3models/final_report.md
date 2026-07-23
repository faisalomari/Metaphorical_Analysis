# LLM Rhetorical Element Detection — Pilot, DEV Tuning & Frozen TEST Evaluation

**Thesis:** Exploring the Potential of LLMs to Identify Challenging Rhetorical Elements (classical Arabic poetry: trope/مجاز, simile/تشبيه, kenning/كناية, antonymy/طباق)

**Report generated:** 2026-07-21

This report covers the full 3-model pilot cycle: an initial single-poem pilot, a ground-truth audit and scoring-harness fix, DEV-side prompt tuning, the frozen TEST evaluation (the thesis's primary numbers), and two supplementary DEV-only follow-up experiments run after TEST was frozen. Findings are presented first; methodology and full per-run tables follow.

---

## 1. Executive Summary

Three general-purpose LLMs (Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash) were evaluated, zero-shot, on detecting four classical Arabic rhetorical elements against a single expert annotator's (Prof. Ali Hussein) manual ground truth. Two prompts were compared on a frozen held-out TEST set (3 poems, never touched during tuning): a **baseline** prompt and **v4_combined**, a tuned version incorporating three rules derived from DEV-side error analysis. v4_combined is the recommended prompt for all three models going forward.

### 1.1 Frozen TEST results (the thesis's headline numbers)

TEST = Imru' al-Qais Poem 1, Jarir, Abu Tammam (pooled), ground truth support: **Trope=179, Simile=52, Kenning=147, Antonymy=43**. 2-run majority, strict span-overlap criterion (see §2.2 for what "strict" means and why a token-overlap criterion is also tracked).

| Element | Model | Baseline TP/FP/FN | Baseline F1 | v4_combined TP/FP/FN | v4 F1 | Δ |
|---|---|---|---|---|---|---|
| **Trope** | Claude Sonnet 4.6 | 17/3/162 | 0.171 | 25/3/154 | 0.242 | +42% |
| Trope | GPT-5.4-mini | 6/1/173 | 0.065 | 28/16/151 | 0.251 | **+286%** |
| Trope | Gemini 3.5 Flash | 34/4/145 | 0.313 | 45/9/134 | 0.386 | +23% |
| **Kenning** | Claude Sonnet 4.6 | 8/2/139 | 0.102 | 8/6/139 | 0.099 | ~flat |
| Kenning | GPT-5.4-mini | 1/4/146 | 0.013 | 4/7/143 | 0.051 | +0.038 (4x, still tiny) |
| Kenning | Gemini 3.5 Flash | 9/4/138 | 0.113 | 15/8/132 | 0.176 | +56% |
| **Simile** | Claude Sonnet 4.6 | 28/6/24 | 0.651 | 28/6/24 | 0.651 | flat |
| Simile | GPT-5.4-mini | 30/4/22 | 0.698 | 31/3/21 | 0.721 | +3% |
| Simile | Gemini 3.5 Flash | 32/7/20 | 0.703 | 32/4/20 | 0.727 | +3% |
| **Antonymy** | Claude Sonnet 4.6 | 5/14/38 | 0.161 | 6/12/37 | 0.197 | +22% |
| Antonymy | GPT-5.4-mini | 4/11/39 | 0.138 | 5/17/38 | 0.154 | +12% |
| Antonymy | Gemini 3.5 Flash | 4/19/39 | 0.121 | 5/21/38 | 0.145 | +20% |

The token-overlap criterion tells the same Trope/Simile/Kenning story but reveals a much larger baseline→v4 gap for **Antonymy** specifically, where Arabic morphological variation (e.g. النُّوّامِ vs. نَوَّمُوا — different inflected forms of the same root) causes strict substring matching to under-count real hits: baseline token F1 = 0.419/0.345/0.545 (Claude/GPT/Gemini) vs. v4 token F1 = 0.393/0.431/0.609.

**Bottom line:** v4_combined is a clear win for Trope (all 3 models, GPT +286%) and a moderate win for Simile and Antonymy. Kenning remains the hardest element by a wide margin for all three models and v4_combined barely moves it — this is the clearest open problem the thesis surfaces.

### 1.2 Trope false-negative breakdown by ground-truth subtype (TEST) — a DEV→TEST reversal

| Subtype | n | Baseline missed | v4 missed |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | **62%** |
| مجاز عقلي (rational trope) | 41 | 83% | **66%** |
| استعارة تمثيلية (unmarked whole-clause allegory) | 24 | 33% | 29% |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% |
| مجاز مرسل (metonymy, single lexicalized word) | 13 | 85% | **85% — unchanged** |
| استعارة حديثة (modern/innovative metaphor) | 4 | 75% | 75% — unchanged |

A 2-poem DEV analysis (Imru2+Nabigha) had flagged استعارة تمثيلية as the hardest Trope subtype — at TEST scale (3 poems, larger n) that did **not** hold up: it is actually the *easiest* subtype both before and after v4. v4's genuine, TEST-validated wins are استعارة فعل and مجاز عقلي; مجاز مرسل is the one subtype v4 does nothing for at all. **Lesson carried forward: small-sample DEV subtype analysis pointed at the wrong culprit — always re-check subtype breakdowns at TEST scale before trusting a DEV-derived narrative.**

### 1.3 Antonymy over-claiming (first honest evaluation, n=43 — too thin on DEV to see this, n=5 there)

All three models systematically over-claim Antonymy: false positives exceed true positives at baseline for every model (e.g. Claude baseline: TP=5, FP=14 → precision only 0.263). This pattern was invisible on DEV's tiny n=5 and only became visible once TEST provided enough support to evaluate honestly.

### 1.4 Ensemble (majority-vote-across-3-models) is not useful here

Computed once on the original single-poem pilot data (no new API calls): ensemble F1 for Trope (0.222) and Kenning (0.167) is **identical to the best single model** — because all 3 models miss the *same* instances (a systematic gap, not independent noise an ensemble could average out). Simile ensemble F1 (0.667) is actually *worse* than GPT-5.4-mini alone (0.769), since ensembling trades recall for precision. **A multi-model panel does not reliably improve recall on the hard elements for this task.**

### 1.5 Run-to-run consistency (TEST, decision-level agreement)

| | Trope | Simile | Kenning | Antonymy |
|---|---|---|---|---|
| baseline: Claude / GPT / Gemini | 98% / 88% / **100%** | 99% / 96% / 100% | 99% / 95% / 100% | 99% / 93% / 100% |
| v4: Claude / GPT / Gemini | 95% / 89% / 97% | 100% / 98% / 99% | 91% / 98% / 89% | 95% / 95% / 96% |

Gemini's baseline was perfectly deterministic on TEST; v4's added rules cost some of that (down to 89-97%) — a reasonable trade for the recall gains in §1.1.

### 1.6 Supplementary DEV-only experiments — NOT part of the frozen thesis numbers

Two follow-up ideas were tested strictly on DEV (Imru2 + Nabigha) after TEST was frozen, specifically to see whether a cheap prompt-engineering change could help Kenning (the open problem from §1.1). **Neither is a recommended technique; both are reported as negative/mixed supplementary findings.**

**Per-element decomposition** (splitting v4_combined into 4 single-element calls instead of 1 call for all 4 elements): motivated by the idea that Kenning might suffer from competing with 3 other elements in the same call. Result: mixed, not a win. Only Claude improved on Kenning (trading precision for recall); GPT and Gemini both got *worse* — GPT's Kenning collapsed to near-total abstention (positive calls dropped from 15 to 4) and became *less* consistent (98%→82% run agreement), the opposite of what isolation was supposed to buy. This argues against a simple task-interference explanation for Kenning's difficulty.

**Per-verse granularity grid** (one API call per verse instead of one call for the whole poem, crossed with all-4-elements vs. single-element, on Imru2 only — 23 verses): completes a 2x2 grid (whole-poem/per-verse × all-4/single-element). The one clean positive signal — Gemini's per-verse Kenning F1 roughly doubling (0.190→0.480) — motivated a targeted follow-up: the same Mode A (per-verse, all-4-elements) prompt was re-run on Nabigha (50 verses, 52 Kenning ground-truth instances) specifically to check whether this replicates on a second poem before it could appear anywhere in the thesis as a finding.

**Nabigha replication result (Mode A, per-verse, all-4-elements, Kenning slice, n=52), compared against the same poem's whole-poem (v4_combined) Kenning baseline, alongside the original Imru2 result for direct comparison:**

| Model | Imru2: whole→verse F1 (Δ) | Nabigha: whole→verse F1 (Δ) |
|---|---|---|
| Claude Sonnet 4.6 | 0.111→0.250 (+125%) | 0.136→0.338 (+149%) |
| GPT-5.4 mini | 0.200→0.174 (-13%) | 0.156→0.143 (-9%) |
| Gemini 3.5 Flash | 0.190→0.480 (+152%) | 0.262→0.290 (+11%) |

**Result: the direction replicates for 2 of 3 models (Claude Sonnet 4.6, Gemini 3.5 Flash), but the magnitude does not.** Gemini's dramatic Imru2 gain (+152%) shrank to +11% on Nabigha — the single-poem-optimism this replication check was designed to catch. But Claude's gain did the opposite: +125% on Imru2, **+149% on Nabigha** — as large or larger on the second poem, not a shrinking effect. GPT-5.4-mini is the one model with a consistent story: flat-to-negative on both poems, never benefiting from per-verse calling. **Revised conclusion**: per-verse Mode A does produce a real, cross-poem-replicated Kenning improvement for 2 of 3 models (Claude, Gemini) — this is a genuine positive finding, not purely an artifact of one lucky poem, and the earlier framing of this as a fully negative result was premature (it was written before Claude's data existed). What does NOT replicate is the *size* of any single model's gain — Gemini's magnitude collapsed by an order of magnitude while Claude's held or grew, so no specific percentage from one poem should be quoted as if it generalizes. Two things still argue against adopting per-verse calling as a technique regardless: absolute Kenning F1 even at its best (Claude 0.338, Gemini 0.290 on Nabigha) remains far below Simile's ~0.65-0.7 ceiling, and it costs 4-8x more per unit of F1 than whole-poem batching (§1.6/§A.7) for a benefit that only 2 of 3 models show.

Independent of the replication check, per-verse calls cost **4-8x more per unit of F1** than whole-poem batching (the system prompt is re-sent on every single-verse call), and the per-verse Kenning gain does not survive being combined with element-isolation (Mode B is worse than Mode A on both accuracy and cost). Full grid in Appendix §A.6.

**This cross-poem result names a methodological pattern worth stating explicitly, since a version of it has now occurred twice in this project — though the full picture (once Claude's data was retried and included) is more nuanced than "everything shrinks."** §2.1.6 describes a single *run's* apparent gain turning out to be partly noise (corrected by the 2-run-majority rule). The Nabigha check found a related but not identical failure mode one level up, across *poems*: Gemini's dramatic Kenning gain (+152% on Imru2) shrank to +11% on Nabigha — the *magnitude* did not replicate. But Claude's gain (+125% on Imru2) held at +149% on Nabigha — the magnitude was, if anything, larger the second time. **The lesson is therefore specifically about magnitude, not direction: on this task, a single poem's effect *size* is not a reliable estimate even when its *direction* is real, which is precisely why the frozen TEST numbers (§1.1) — pooled across 3 poems, 2-run majority — are the only numbers this report treats as quantitatively conclusive.** Combined with §1.6's decomposition finding, the fuller picture on Kenning is: whole-poem decomposition doesn't help (§1.6), but per-verse calling (Mode A) produces a real, cross-poem-replicated improvement for 2 of 3 models (Claude, Gemini) — just not one large or reliable enough, or cheap enough (4-8x the cost per unit of F1), to recommend adopting, and one that GPT never shows on either poem.

### 1.7 Cost of the whole pilot cycle

| Stage | Cost (USD) |
|---|---|
| Original single-poem pilot (Imru2, baseline prompt) | $0.15 |
| DEV Nabigha baseline run | $0.14 |
| DEV prompt-variant tuning (v1-v4 + ablations) | $1.72 |
| Per-element decomposition (§1.6, DEV) | $0.67 |
| Frozen TEST run (baseline + v4_combined, 3 TEST poems) | $1.85 |
| Per-verse granularity grid (§1.6, Imru2 + Nabigha replication) | $3.64 |
| **Total** | **$8.16** |

---

## 2. Methodology

### 2.1 Project arc

1. **Original single-poem pilot** (Imru2, 23 verses): first 3-model comparison, established the basic instruction-only-JSON calling pattern (no provider-native structured-output mode, for comparability with earlier project phases).
2. **Ground-truth audit** across all 5 annotated poems, confirming Dr. Ali Hussein's manual annotations as the sole ground-truth source and mapping the original 53-element classical taxonomy down to the thesis's 4 target elements.
3. **Scoring harness fix**: the original verse-level exists/not-exists scoring produced artifacts on multi-instance verses. A span-level harness (§2.2) was built to match predicted spans against ground-truth spans rather than just voting a verse's element in or out. Re-scoring the same single-poem data with the fixed harness left Trope's F1 unchanged (0.222 both ways) but *worsened* Kenning's apparent score (0.154→0.105) once multi-instance verses were counted correctly — confirming the fix mattered, and mattered differently per element.
4. **DEV/TEST split frozen**: DEV = Imru2 + Nabigha (used for all prompt iteration); TEST = Imru1 + Jarir + Abu Tammam (touched exactly once, for the frozen final numbers in §1.1). This split, once set, was never revisited.
5. **DEV-side prompt tuning**: 4 prompt variants (each adding one candidate rule to the baseline) plus 2 ablation combinations were tried on DEV, converging on **v4_combined** (baseline + all 3 rules: a Trope-vs-Kenning literal-meaning boundary rule, a rule preventing simile-marker words from short-circuiting other elements' checks, and a rule reminding the model that a verse can contain multiple elements/instances).
6. **A noise-correction lesson that shaped the whole methodology**: an early ablation run showed Gemini's Kenning F1 apparently jumping 0.056→0.433 (8x) with one candidate rule, on a single run. A second real run brought the honest, 2-run-majority number down to 0.225 — **half the apparent gain was noise from one lucky run.** This is why the project's hard rule became: never draw a comparative conclusion from a single run; always require ≥2 runs and report 2-run-majority as the primary metric, with raw TP/FP/FN always shown alongside F1 so small denominators stay visible.
7. **Frozen TEST run**: baseline vs. v4_combined, all 3 models, 2 runs each, on the 3 TEST poems — never re-run, never re-scored with a different prompt. These are the numbers in §1.1.
8. **Two supplementary DEV-only follow-ups** (§1.6), run strictly after TEST was frozen, testing whether decomposition or per-verse granularity could help close the Kenning gap. Both are negative/mixed and do not change the v4_combined recommendation.
9. **A cross-poem replication check** (§1.6) of the one promising signal from step 8 (per-verse Kenning gains) found the *direction* replicates for 2 of 3 models (Claude, Gemini) but the *magnitude* does not: Gemini's dramatic +152% Imru2 gain shrank to +11% on Nabigha, while Claude's held (+125%→+149%, if anything larger on the second poem). This is treated as a named methodological pattern (not a one-off) going forward: single-sample-unit effect *sizes* (one run, or one poem) are systematically unreliable on this task even when the *direction* of an effect is real, which is precisely why the frozen TEST numbers (pooled across 3 poems, 2-run majority) are the only numbers this report treats as conclusive.

### 2.2 Scoring harness

Every model response is JSONL (one JSON object per verse), instruction-only (no provider-native JSON-schema enforcement, for comparability across all 3 providers and with the project's earlier phases). Each verse+element prediction is either absent, `exists=false`, or `exists=true` with a predicted appearance span (a literal substring of the verse). Two independent instance-matching criteria are always reported side by side:

- **Strict**: the predicted span must literally overlap a ground-truth span.
- **Token-overlap**: word-level overlap above a 0.5 threshold, with a partial fix for attached Arabic clitics (و/ف) — recovers cases where the model found the right instance but strict substring matching fails due to Arabic morphological variation (inflected forms of the same root), a gap that matters a lot for Antonymy specifically (§1.1).

Multi-instance verses (more than one ground-truth instance of the same element in one verse) are handled by matching the model's single predicted span against whichever ground-truth instance it best fits; any remaining unmatched ground-truth instances count as additional false negatives. **2-run majority vote is always the primary metric**; single-run numbers are shown only for transparency, never as the reported number, per the noise lesson in §2.1.6.

### 2.3 Ground truth

Sole source: Prof. Ali Hussein's manual rhetorical analysis (53-element classical taxonomy), one annotated spreadsheet per poem. Mapped down to the 4 thesis elements by substring match on the primary/secondary element columns (مجاز or استعارة → Trope; direct matches for تشبيه/كناية/طباق). Exact-duplicate (span, element) rows are deduplicated before counting, so reported ground-truth instance counts are the real, deduped numbers actually used for scoring (not earlier back-of-envelope estimates from planning).

### 2.4 Models & settings

| Provider | Model ID | Temperature | Runs | Input $/1M | Output $/1M |
|---|---|---|---|---|---|
| Anthropic | `claude-sonnet-4-6` | 0.0 | 2 | $3.00 | $15.00 |
| OpenAI | `gpt-5.4-mini` | 0.0 | 2 | $0.75 | $4.50 |
| Google | `gemini-3.5-flash` | 0.0 | 2 | $1.50 | $9.00 |

### 2.5 The v4_combined prompt

v4_combined = the baseline system message (4 element definitions, verbatim from the project's canonical definitions) plus 3 added rule blocks, all DEV-error-analysis-derived:

1. **Trope-vs-Kenning boundary rule**: Kenning requires the literal meaning to remain a *possible* reading alongside the figurative one; Trope requires the literal meaning to be *impossible or rejected*, explicitly including verbs used non-literally (not just noun-based figures).
2. **Marker-independence rule**: an explicit simile particle (كأن، كما، ك، مثل) is evidence for Simile specifically, not automatically for Trope, and does not end the check for the verse's other elements.
3. **Multi-figure rule**: a single verse can contain more than one element, and more than one instance of the same element — check all 4 independently every time.

Full system message text: Appendix §A.1.

### 2.6 Frozen decisions (non-negotiable throughout)

- TEST (Imru1, Jarir, Abu Tammam) is spent and was never re-run, re-tuned, or re-scored with a new prompt.
- All new prompt ideas are evaluated on DEV only, as clearly-labeled supplementary experiments — they do not retroactively change the §1.1 numbers even when promising.
- 2 runs per configuration always; 2-run majority is always the primary metric; raw TP/FP/FN always reported alongside F1/precision/recall.

---

## Appendix

### A.1 Full v4_combined system message

```
You are an Arabic rhetoric analysis engine. Follow instructions strictly.

================================
ELEMENT DEFINITIONS (REFERENCE)
================================
Below are EXACTLY 4 rhetorical elements. Learn them deeply using ONLY the
definitions and examples provided here. Do NOT use outside knowledge. Build
your internal detection rules from these examples. You will apply these
definitions to the poem given in the user's message.

--------------------------------
ELEMENTS_BLOCK
--------------------------------


ELEMENT_1:
Arabic name: مجاز
English name: Trope
Arabic explanation: المجاز هو استخدام اللفظ في غير معناه الأصلي لعلاقة بين المعنيين مع وجود قرينة تمنع إرادة المعنى الحقيقي، فيمنح الكلام قوة إيحائية واتساعًا في الدلالة. وهو أسلوب يُعيد تشكيل المعنى بطريقة غير مباشرة لخلق صورة أعمق وأكثر تأثيرًا.
English explanation: A trope (figurative expression) uses a word in a non-literal sense based on an associative relationship, accompanied by a contextual clue that prevents the literal meaning. It enriches the language by expanding meaning and creating more expressive, nuanced imagery.
Examples:
1) وَمَا ذَرَفَتْ عَيْنَاكِ إلَّا لتَضْرِبي	بِسَهْمَيْكِ في أعشَارِ قَلْبٍ مُقَتَّلِ
2) فَجُزِيتِ خَيْرَ جَزَاءِ نَاقَةِ وَاحِدٍ	وَرَجَعْتِ سَالِمَةَ القَرَا بِسَلامِ
3) فعَدّ عَمّا ترى ، إذ لا ارتجاع له،	وانمِ القُتُودَ على عَيْرانة ٍ أُجُدِ
4)  لَحِقْتُ وأَصحابي على كل حُرَّةٍ	مَرُوح تُبارِي الأَحْبَشِيَّ المُكارِيَا

ELEMENT_2:
Arabic name: تشبيه
English name: Simile
Arabic explanation: التشبيه هو عقد مقارنة صريحة بين شيئين يشتركان في صفة ما، باستخدام أداة تُظهر هذا الربط مثل كأنّ أو مثل. يهدف إلى توضيح المعنى وتقريبه للقارئ من خلال إبراز وجه الشبه بين الطرفين
English explanation: A simile is an explicit comparison between two things that share a similar quality, using a comparative marker such as “like” or “as.” It serves to clarify an idea and make it more vivid by highlighting the similarity between the compared elements.
Examples:
1) إذا ما الثُّرَيَّا في السَّمَاءِ تَعَرَّضَتْ تَعَرَّضَ أثْنَاءِ الوِشَاحِ المُفَصَّلِ
2) أَزْمَانَ فُوهَا كُلَّمَا نَبَّهْتُهَا	كَالمِسْكِ بَاتَ وَظَلَّ فِي الفَدّامِ
3) وكان ضُمْران منه حيث يوزعهُ،	طعن المُعارك عند المُحجر النّجُدِ
4) دُنُوَّ عتاق الطير للزجر بعدما	شَمَسْنَ وولَّيْنَ الخدود العواصيا
5) عُنِيَ الرَبيعُ بِرَوضِهِ فَكَأَنَّما	أَهدى إِلَيهِ الوَشيَ مِن صَنعاءِ

ELEMENT_3:
Arabic name: كناية
English name: Kenning
Arabic explanation: الكناية هي تعبير يُراد به معنى غير ظاهر من اللفظ، دون ذكره مباشرة، مع إمكان إرادة المعنى الحقيقي أيضًا، مما يمنح الكلام عمقًا وإيحاءً. تعتمد على الإشارة غير المباشرة لصفة أو معنى، فيفهم السامع المقصود من خلال الدلالة والسياق
English explanation: A kenning (metonymic or euphemistic expression) conveys an indirect meaning by using words whose literal sense is not the intended purpose, while still allowing the literal meaning to remain possible. It relies on hinting at a quality or idea rather than stating it directly, giving the language subtlety and layered meaning.
Examples:
1) وبَيْضَةِ خِدْرٍ لا يُرَامُ خَبَاؤُهَا	تَمَتَّعْتُ منْ لَهْوٍ بها غَيْرَ مُعْجَلِ
2) وَأنَا المُنَبِّهُ بَعْدَمَا قَدْ نَوَّمُوا	وَأنَا المُعَالِنُ صَفْحَة َ النُّوّامِ
3) مقذوفة ٍ بدخيس النحض، بازِلُها	له صريفٌ، صريف القَعْوِ بالمسَدِ
4) فما أَبصر النارَ التي وضحت له	وراءَ جُفاف الطير إِلا تماريا
5) صَبَّحتُهُ بِسُلافَةٍ صَبَّحتُها	بِسُلافَةِ الخُلَطاءِ وَالنُّدَمَاءِ

ELEMENT_4:
Arabic name: طباق
English name: Antonymy
Arabic explanation: الطباق هو الجمع بين لفظين متضادين في المعنى داخل سياق واحد، لإبراز التباين وتقوية الدلالة من خلال التضاد الواضح بينهما. يُستخدم لإضفاء إيقاع معنوي وزيادة التأثير عبر شدّ انتباه القارئ إلى المفارقة بين الكلمتين
English explanation: Antonymy (or oxymoronic pairing) is the use of two words with opposite meanings within the same context to emphasize contrast and enhance the overall message. It creates a stronger expressive effect by drawing attention to the semantic opposition between the paired terms.
Examples:
1) تُضِيءُ الظَّلامَ بالعِشَاءِ كَأنَّهَا	مَنَارَة ُ مُمْسَى رَاهِبٍ مُتَبَتِّلِ
2) وَأنَا المُنَبِّهُ بَعْدَمَا قَدْ نَوَّمُوا	وَأنَا المُعَالِنُ صَفْحَة َ النُّوّامِ
3) فتلك تُبْلغني النعمانَ ، إن له	فضلاً على الناس في الأدنى ، وفي البَعَدِ
4) دعوتُ إِلى ذي العرش ربِّ محمد	لِيَجْمَعَ شعبًا أَو يُقَرِّبَ نائيًا
5) بِمُدامَةٍ تَغدو المُنى لِكُؤوسِها	خَوَلاً عَلى السَرّاءِ وَالضََرَّاءِ

--------------------------------
ADDITIONAL RULE: Trope vs. Kenning boundary
--------------------------------
Kenning (كناية): the literal meaning remains a POSSIBLE, plausible reading -
the speaker could mean it literally, even if the phrasing is unusual. The
figurative meaning is implied ALONGSIDE the literal one, not instead of it.

Trope (مجاز): the literal meaning is IMPOSSIBLE or clearly rejected by
context - only the figurative sense works. This includes a VERB whose action
is applied non-literally (e.g. a day "fading away" as if dying, an emotion
"seizing/enslaving" someone as if physically) - not only noun-based figures.

Worked contrast (same verse, two different verdicts):
  "تَسْتَبِيكَ" ("captivates you") -> Trope: a verb describing physical capture/
  slavery applied to a feeling; the literal act of enslaving cannot be meant.
  "بِواضِحٍ" ("radiant/bright [smile]") in the same verse -> Kenning: it could
  still literally describe brightness, while indirectly conveying beauty.

--------------------------------
ADDITIONAL RULE: evaluate each element on its own evidence
--------------------------------
The presence of an explicit comparison particle (كأن، كما، ك، مثل) is
evidence for SIMILE specifically - it is NOT evidence for Trope, and it does
NOT mean you have finished checking the verse. A verse containing an
explicit simile may ALSO separately contain a different word or verb used
figuratively (Trope) or indirectly (Kenning) elsewhere in the same verse.
Do not let a simile-particle phrase satisfy your check for a different
element. Re-read the verse independently for each of the 4 elements' own
definition and evidence before deciding exists=false.

--------------------------------
ADDITIONAL RULE: verses can contain multiple elements
--------------------------------
A single verse can contain more than one of these 4 elements at the same
time, and can contain more than one instance of the SAME element. Check ALL
4 elements independently for every verse, regardless of what you already
found for other elements in that verse.
```

### A.2 Full TEST results — both criteria, TP/FP/FN/TN

*(strict and token-overlap criteria, all 4 elements, all 3 models, baseline and v4_combined — reproducible via `experiments/pilot_3models/test_report.py`)*

| Element | Model | Strict TP/FP/FN | P/R/F1 (strict) | Token TP/FP/FN | P/R/F1 (token) |
|---|---|---|---|---|---|
| **baseline** | | | | | |
| Trope | Claude Sonnet 4.6 | 17/3/162 | 0.85/0.09/0.171 | 17/3/162 | 0.85/0.09/0.171 |
| Trope | GPT-5.4 mini | 6/1/173 | 0.86/0.03/0.065 | 6/1/173 | 0.86/0.03/0.065 |
| Trope | Gemini 3.5 Flash | 34/4/145 | 0.89/0.19/0.313 | 35/3/144 | 0.92/0.20/0.323 |
| Simile | Claude Sonnet 4.6 | 28/6/24 | 0.82/0.54/0.651 | 32/2/20 | 0.94/0.62/0.744 |
| Simile | GPT-5.4 mini | 30/4/22 | 0.88/0.58/0.698 | 30/4/22 | 0.88/0.58/0.698 |
| Simile | Gemini 3.5 Flash | 32/7/20 | 0.82/0.62/0.703 | 33/6/19 | 0.85/0.63/0.725 |
| Kenning | Claude Sonnet 4.6 | 8/2/139 | 0.80/0.05/0.102 | 8/2/139 | 0.80/0.05/0.102 |
| Kenning | GPT-5.4 mini | 1/4/146 | 0.20/0.01/0.013 | 1/4/146 | 0.20/0.01/0.013 |
| Kenning | Gemini 3.5 Flash | 9/4/138 | 0.69/0.06/0.113 | 9/4/138 | 0.69/0.06/0.113 |
| Antonymy | Claude Sonnet 4.6 | 5/14/38 | 0.26/0.12/0.161 | 13/6/30 | 0.68/0.30/0.419 |
| Antonymy | GPT-5.4 mini | 4/11/39 | 0.27/0.09/0.138 | 10/5/33 | 0.67/0.23/0.345 |
| Antonymy | Gemini 3.5 Flash | 4/19/39 | 0.17/0.09/0.121 | 18/5/25 | 0.78/0.42/0.545 |
| **v4_combined** | | | | | |
| Trope | Claude Sonnet 4.6 | 25/3/154 | 0.89/0.14/0.242 | 26/2/153 | 0.93/0.15/0.251 |
| Trope | GPT-5.4 mini | 28/16/151 | 0.64/0.16/0.251 | 30/14/149 | 0.68/0.17/0.269 |
| Trope | Gemini 3.5 Flash | 45/9/134 | 0.83/0.25/0.386 | 46/8/133 | 0.85/0.26/0.395 |
| Simile | Claude Sonnet 4.6 | 28/6/24 | 0.82/0.54/0.651 | 32/2/20 | 0.94/0.62/0.744 |
| Simile | GPT-5.4 mini | 31/3/21 | 0.91/0.60/0.721 | 31/3/21 | 0.91/0.60/0.721 |
| Simile | Gemini 3.5 Flash | 32/4/20 | 0.89/0.62/0.727 | 32/4/20 | 0.89/0.62/0.727 |
| Kenning | Claude Sonnet 4.6 | 8/6/139 | 0.57/0.05/0.099 | 8/6/139 | 0.57/0.05/0.099 |
| Kenning | GPT-5.4 mini | 4/7/143 | 0.36/0.03/0.051 | 3/8/144 | 0.27/0.02/0.038 |
| Kenning | Gemini 3.5 Flash | 15/8/132 | 0.65/0.10/0.176 | 15/8/132 | 0.65/0.10/0.176 |
| Antonymy | Claude Sonnet 4.6 | 6/12/37 | 0.33/0.14/0.197 | 12/6/31 | 0.67/0.28/0.393 |
| Antonymy | GPT-5.4 mini | 5/17/38 | 0.23/0.12/0.154 | 14/8/29 | 0.64/0.33/0.431 |
| Antonymy | Gemini 3.5 Flash | 5/21/38 | 0.19/0.12/0.145 | 21/5/22 | 0.81/0.49/0.609 |

### A.3 Per-element decomposition — full grid (§1.6, pooled DEV)

| Element | Model | v4_combined TP/FP/FN | v4 F1 | Decomposed TP/FP/FN | Dec. F1 | Run-agree (v4→dec.) |
|---|---|---|---|---|---|---|
| **Kenning** | Claude Sonnet 4.6 | 5/3/64 | 0.130 | 8/7/61 | 0.190 | 89%→95% |
| Kenning | GPT-5.4-mini | 7/8/62 | 0.167 | 4/0/65 | 0.110 (worse) | 98%→82% (worse) |
| Kenning | Gemini 3.5 Flash | 10/3/59 | 0.244 | 7/5/62 | 0.173 (worse) | 95%→96% |
| Trope | Claude Sonnet 4.6 | 2/6/58 | 0.059 | 4/6/56 | 0.114 | 93%→97% |
| Trope | GPT-5.4-mini | 6/9/54 | 0.160 | 6/14/54 | 0.150 (token: 0.175) | 77%→93% |
| Trope | Gemini 3.5 Flash | 5/5/55 | 0.143 | 7/6/53 | 0.192 | 82%→85% |
| Simile | Claude Sonnet 4.6 | 14/7/6 | 0.683 | 15/7/5 | 0.714 | 99%→99% |
| Simile | GPT-5.4-mini | 13/7/7 | 0.650 | 16/7/4 | 0.744 | 96%→99% |
| Simile | Gemini 3.5 Flash | 13/7/7 | 0.650 | 12/7/8 | 0.615 | 96%→93% |
| Antonymy (n=5, too thin) | all 3 | — | — | — | — | — |

### A.6 Per-verse granularity — full grid (§1.6, Imru2 + Nabigha replication)


**Imru2 full grid (n_verses=23, GT support: {'Trope': 8, 'Simile': 5, 'Kenning': 17, 'Antonymy': 1})**

| Element | Model | Whole+All4 (v4) | Whole+Single (decomp.) | Verse+All4 (Mode A) | Verse+Single (Mode B) |
|---|---|---|---|---|---|
| Trope | Claude Sonnet 4.6 | 2/0/6, 0.400 | 2/1/6, 0.364 | 2/2/6, 0.333 | 4/3/4, 0.533 |
| Trope | GPT-5.4 mini | 1/0/7, 0.222 | 1/1/7, 0.200 | 3/9/5, 0.300 | 2/3/6, 0.308 |
| Trope | Gemini 3.5 Flash | 1/2/7, 0.182 | 1/2/7, 0.182 | 3/3/5, 0.429 | 1/4/7, 0.154 |
| Simile | Claude Sonnet 4.6 | 5/5/0, 0.667 | 5/5/0, 0.667 | 5/5/0, 0.667 | 5/5/0, 0.667 |
| Simile | GPT-5.4 mini | 4/5/1, 0.571 | 5/5/0, 0.667 | 5/4/0, 0.714 | 5/5/0, 0.667 |
| Simile | Gemini 3.5 Flash | 4/5/1, 0.571 | 4/5/1, 0.571 | 5/5/0, 0.667 | 4/6/1, 0.533 |
| Kenning | Claude Sonnet 4.6 | 1/0/16, 0.111 | 1/2/16, 0.100 | 3/4/14, 0.250 | 3/6/14, 0.231 |
| Kenning | GPT-5.4 mini | 2/1/15, 0.200 | 2/0/15, 0.211 | 2/4/15, 0.174 | 2/6/15, 0.160 |
| Kenning | Gemini 3.5 Flash | 2/2/15, 0.190 | 1/3/16, 0.095 | 6/2/11, 0.480 | 4/4/13, 0.320 |
| Antonymy | Claude Sonnet 4.6 | 0/1/1, 0.000 | 0/2/1, 0.000 | 0/2/1, 0.000 | 0/2/1, 0.000 |
| Antonymy | GPT-5.4 mini | 0/1/1, 0.000 | 0/1/1, 0.000 | 0/1/1, 0.000 | 0/1/1, 0.000 |
| Antonymy | Gemini 3.5 Flash | 1/0/0, 1.000 | 0/1/1, 0.000 | 0/3/1, 0.000 | 0/3/1, 0.000 |

**Nabigha Mode A only (n_verses=50, GT support: {'Trope': 52, 'Simile': 15, 'Kenning': 52, 'Antonymy': 4}) — the targeted replication run**

| Element | Model | Mode A (verse, all-4) TP/FP/FN | F1 (strict) | F1 (token) | Run-agree |
|---|---|---|---|---|---|
| Trope | GPT-5.4 mini | 6/21/46 | 0.152 | 0.177 | 44/49 |
| Trope | Gemini 3.5 Flash | 15/8/37 | 0.400 | 0.400 | 47/50 |
| Trope | Claude Sonnet 4.6 | 5/7/47 | 0.156 | 0.156 | 50/50 |
| Simile | GPT-5.4 mini | 9/3/6 | 0.667 | 0.593 | 49/49 |
| Simile | Gemini 3.5 Flash | 9/2/6 | 0.692 | 0.692 | 48/50 |
| Simile | Claude Sonnet 4.6 | 9/3/6 | 0.667 | 0.741 | 50/50 |
| Kenning | GPT-5.4 mini | 5/13/47 | 0.143 | 0.171 | 44/49 |
| Kenning | Gemini 3.5 Flash | 10/7/42 | 0.290 | 0.319 | 45/50 |
| Kenning | Claude Sonnet 4.6 | 13/12/39 | 0.338 | 0.390 | 48/50 |
| Antonymy | GPT-5.4 mini | 1/4/3 | 0.222 | 0.444 | 49/49 |
| Antonymy | Gemini 3.5 Flash | 1/5/3 | 0.200 | 0.400 | 50/50 |
| Antonymy | Claude Sonnet 4.6 | 1/3/3 | 0.250 | 0.500 | 49/50 |

### A.7 Full cost breakdown

| Stage | Cost (USD) |
|---|---|
| Original single-poem pilot (Imru2, baseline prompt) | $0.15 |
| DEV Nabigha baseline run | $0.13 |
| DEV prompt-variant tuning (v1-v4 + ablations) | $1.72 |
| Per-element decomposition (supplementary, DEV) | $0.67 |
| Frozen TEST run (baseline + v4_combined) | $1.85 |
| Per-verse granularity grid (supplementary, DEV, incl. Nabigha replication) | $3.64 |
| **Total** | **$8.16** |
