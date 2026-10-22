# E1 v2 — Multi-Poet Few-Shot Experiment (F5 vs F10)

**Supervisor request**: take 5 and 10 examples of the same sub-element, each from a
**different poet**, and run on 50 poems — once with 5 few-shot examples, once with 10 —
to separate "number of examples" from "which examples" (E1 v2's existing A/B/C/D sets
each use only 2 examples, both from the same 3 Abu Nuwas poems).

**Target**: same as every other E1/E1 v2 set — **استعارة فعل** (verbal metaphor, parent
مجاز/Trope), Phase 3's subtype prompt, schema `{"exists","appearance","reasoning"}`, one
API call per verse-unit.

**Status**: **run complete, 0 errors, full coverage** — 6000/6000 cells (F5: 3000, F10:
3000; 3 models × 1000 verse-units × 1 run each). Real cost: **$28.03** (anthropic $18.94,
google $5.99, openai $3.10) — under the $29.97 pre-run estimate. One mid-run stoppage
occurred (Anthropic credit balance ran dry partway through the pool's two largest poems,
120 calls failed + 326 never attempted, 0 of them silent — the runner's existing
5-consecutive-error stop fired correctly) and was resumed cleanly after the user topped up
credits; see `docs/phase4/SESSION_LOG.md` (2026-10-22 entry) for the full incident log.

---

## 1. Design

### 1.1 Poet/example selection (declared before any API call, seed=42)

**Eligibility rule**: a poem is a candidate example source for poet P iff it is not one of
the 5 frozen Phase 1 poems, not the no-text poem, and not one of v1's own 3 Abu-Nuwas-only
example-source poems (`EXAMPLE_POEM_IDS`) — and, **only for أبو نواس**, also not one of the
original `eval_pool.json`'s 10 Abu Nuwas poems (so Abu Nuwas could appear as one of the
poets, but only via a poem outside the existing eval pool and the existing fewshot
examples, as the supervisor's design asked). A **verse** is eligible iff it carries ≥1
annotation with `subtype == "استعارة فعل"` (exact match) **and** a non-empty `analysis`
note. A **poet** is eligible iff ≥1 of their candidate poems has ≥1 eligible verse.

**47 eligible poets** were found, spanning 8 periods: العصر الأموي=16, العصر العباسي=12,
العصر الجاهلي=7, مخضرم=5, مخضرم الدولتين=2, blank/unknown=3, الخلفاء الراشدون=1,
العصر المملوكي=1.

**Poet-selection order** is a **deterministic period-diversity round robin** — NOT
randomized: periods are visited in a fixed order (chronological-ish: جاهلي → مخضرم →
مخضرم الدولتين → أموي → عباسي → any other period → blank), poets within a period ordered
by `poet_id`, cycling through periods and taking the next poet from each until enough are
collected. **F5 = the first 5 poets** in this order, **F10 = the first 10** (so F5's
poets are a strict prefix of F10's — guaranteed by construction, not by chance), and the
costed-but-not-run optional **F5b = poets 11–15** (5 *other* poets, disjoint from F10, to
separate "more examples" from "which examples" a second way). Abu Nuwas was **not**
selected by this round robin (other عباسي-period poets filled those slots first by
poet_id order) — so the Abu-Nuwas-specific exclusion rule above never actually had to
fire for this draw.

Only the **per-poet verse draw** is randomized: one `random.seed(42)` call, then one
`random.sample(eligible_verses_for_poet, 1)` per poet **in selection order** — sequential
RNG consumption that is never reseeded mid-draw, so F5's 5 draws are byte-identical
whether or not F10 (or F5b) is ever built.

### 1.2 The selected poets, periods, poems, verses, spans, notes

| # | Set | Poet | Period | Poem id | Poem | Verse | Verse text | GT span(s) + note |
|---|---|---|---|---|---|---|---|---|
| 1 | F5 | الأعشى ميمون | العصر الجاهلي | 6574 | قصيدة رقم 78، رمل، نْ | 6 | خُلِقَتْ هِنْدٌ لِقَلْبِي فِتْنَةً هَكَذَا تَعْرِضُ لِلنّاسِ الْفِتَنْ | «فِتْنَةً» — مأخوذ من الفَتن وهو إذابة الذهب والفضة بالنار لتمييز الرديء من الجيد، والفتنة الإثم والمعصية، أو إدخال الإنسان في النار والعذاب. |
| 2 | F5 | أبو ذؤيب الهذلي | مخضرم | 5661 | قصيدة رقم 2، الطويل، بُهَا | 6 | فَقُلْتُ لِقَلْبِي يالَكَ الخَيْرُ إِنَّما يُدَلِّيك لِلْمَوْتِ الجَدِيدِ حِبَابُهَا | 3 spans: «فَقُلْتُ لِقَلْبِي» (الحديث مع القلب استعارة عبارات إنسانية)؛ «يُدَلِّيك لِلْمَوْتِ» (التدلية استعارة)؛ «لِلْمَوْتِ» (الموت مستعار، ليس موتًا جسديًّا) |
| 3 | F5 | بشار بن برد | مخضرم الدولتين | 27110 | قصيدة رقم 26ب، طويل، دِ | 45 | ويوْمٍ تَرَى فيه النجوم تكَشَّفَتْ تَرَاكًا وَهَتْ عنْهُ كريم المشَاهِدِ | 2 spans: «النجوم وَهَتْ» (انشقت)؛ «كريم المشَاهِدِ» (كريم تكون استعارة إن قصد المرات التي يُشاهد فيها) |
| 4 | F5 | الفرزدق | العصر الأموي | 7891 | قصيدة رقم 181، الطويل، رُهْ | 2 | وَرَبْعٍ كجثمانِ الحَمامةِ أدرَجَتْ عَلَيْهِ الصَّبَا حَتى تَنَكّرَ داثِرُهْ | «أدرَجَتْ عَلَيْهِ الصَّبَا» — جعلت الصبا شيئًا يمرّ عليه |
| 5 | F5 | أبو تمّام | العصر العباسي | 4480 | قصيدة رقم 03، البسيط، بِ | 62 | والحَرْبُ قائمَة ٌ في مأْزِقٍ لَجِجٍ تَجْثُو القِيَامُ بِه صُغْراً على الرُّكَبِ | «والحَرْبُ قائمَة... مأْزِقٍ» — استعار القيام للحرب (استعارة ميّتة) للدلالة على حدوثها |
| 6 | +F10 | زياد بن حنظلة | الخلفاء الراشدون | 34779 | قصيدة رقم 2، طويل، بُ | 2 | يَنُوءُ وَتَثْنِيهِ جَوَارِحُ جَمَّةٌ وَحَالَفَهُ مِنَّا سِنَانٌ وَثَعْلَبُ | «وَحَالَفَهُ مِنَّا سِنَانٌ وَثَعْلَبُ» — محالفة السنان والثعلب على سبيل الاستعارة |
| 7 | +F10 | عفيف الدين التلمساني | العصر المملوكي | 29516 | قصيدة رقم 1، خفيف، اءُ | 12 | أَسْكَرُوهَا بِهِمْ كَمَا أَسْكَرَتْهُمْ فِي ابْتِدَاهُمْ بِهَا فَتَمَّ الوَفَاءُ | 2 spans: «أَسْكَرُوهَا بِهِمْ» (الخمرة سكرت)؛ «الوَفَاءُ» (تمّ الوفاء بينهما، كانا عادلين) |
| 8 | +F10 | مُليح بن الحكم | (blank) | 7408 | قصيدة رقم 02، الوافر، رُ | 42 | وَأَنْتِ بَرِيئَةٌ مِنْ كُلِّ سُوءٍ وَعَنْ ذِي الوَصْمِ شَامِخَةٌ قَذَورُ | 3 spans around «الوَصْمِ»/«شَامِخَةٌ»/«قَذَورُ» — ما يدنس العرض يُشبَّه بمحسوس تشمخ/تبتعد عنه الذات |
| 9 | +F10 | النابغة الذبياني | العصر الجاهلي | 3331 | قصيدة رقم 36، الكامل، دِ | 2 | أفِدَ التّرَحّلُ، غير أنّ ركابنا لمّا تَزُلْ برِحالنا، وكان قَدِ | «أفِدَ التّرَحّلُ،» — أَفِدَ: أسرع أو اقترب ودنا |
| 10 | +F10 | ربيعة بن مقروم | مخضرم | 2187 | مفضلية رقم 43، البسيط، د. | 5 | وجَسْرَةٍ حَرَجٍ تَدْمَى مَنَاسِمُها أَعْمَلْتُها بِيَ حتَّى تَقْطَعَ البِيدَا | «حَرَجٍ» — الحُرجُوج/الحَرَج: الناقة السمينة الجسيمة أو الشديدة؛ استعارة مجازية (تاج العروس) |

(F5b, costed but not run — 5 more, disjoint poets: أبو دلامة، عمر بن أبي ربيعة، المتنبي،
الحمدوي، طرفة بن العبد.)

Every drawn verse was **independently re-verified** against the poem JSON (not just
trusted from the draw step) to carry a real `استعارة فعل` GT span — all 15 passed
(`experiments/phase4_e1_v2/unit_checks_multipoet.py`).

### 1.3 Prompt

`experiments/phase4_e1_v2/multipoet_prompt_builder.py` generalizes
`prompt_builder.py`'s A/B/C/D fewshot scaffold from exactly 2 extra examples to N (Example
1 = the unchanged canonical definition example; Example 2…N+1 = the multipoet draw, same
"Example i (from the annotated corpus - verse: …): …" line format as A/B/C). **Does not
edit** `prompt_builder.py`, `fewshot_prompts.py`, or `subtype_prompts.py` — confirmed byte
identical for Z/A/B/C (`unit_checks_multipoet.py`'s check 1). F10's full rendered prompt:
`experiments/phase4_e1_v2/config/prompt_preview_F10.txt` (11 examples total, ~2,574 input
tokens/call once combined with a verse — vs. A/B/C/D's ~3-example, much shorter scaffold).

### 1.4 The 50-poem pool

`experiments/phase4_e1/config/eval_pool.json`'s existing 50 poems **minus** 3 poems used
as F10 example sources (5661, 29516, 34779 — all poet-tagged "other"), **replaced** by
"the next poems from the same seed-43 stratified draw": the replacement method was
**verified empirically before use** — CPython's `random.sample(pop, k)` under a fixed
seed satisfies `sample(pop, k)[:j] == sample(pop, j)` for any `j ≤ k`, so requesting more
items from the same seeded draw deterministically reproduces the original prefix and
extends it. Implemented as two independently-reseeded strata draws, each **verified to
reproduce `eval_pool.json`'s exact original 50 poems as a prefix** before any replacement
was taken. Replacements: `23986`, `27929`, `28093` (all "other").

**Final pool**: 50 poems, **1000 verse-units**, **421** استعارة فعل GT instances,
**10 abu_nuwas + 40 other** (composition preserved exactly), 47/50 overlap with the
original `eval_pool.json`, and **only 9/25 overlap with `eval_pool_25.json`** — the pool
Z/A/B/C/D actually ran on. (If F5b were ever run, 2 more poems — 4554, 28095 — would need
removing/replacing too, giving a slightly different 991-verse pool; computed for costing
only, not written over the canonical F5/F10 pool file.)

**This 9/25 overlap is the central limitation of this experiment**: F5/F10's own numbers
are solid (full 1000-verse pool), but any comparison against Z/A/B/C/D is necessarily
restricted to those 9 poems — see §3.

### 1.5 Models, run, cost

GPT-5.4-mini, Gemini (`providers_fixed.call_google_fixed`, served as `gemini-3.6-flash`),
Claude Sonnet 4.6 — 1 run per cell, 3 models × 2 sets × 1000 verse-units = 6000 calls.
**Real cost: $28.03** (anthropic $18.94, google $5.99, openai $3.10) — all 6000 cells
succeeded with 0 errors in the final manifest (full coverage verified programmatically:
expected = present = 6000). The optional Z add-on (Z on the 41/50 pool poems not already
covered by the existing `eval_pool_25.json` Z run, estimated **$6.45**) and the optional
F5b set (**+$11.82**) were **not run** — the user chose F5+F10 only, capped at
`--max-additional-usd 40`.

---

## 2. PRIMARY: F5 vs F10, full 50-poem / 1000-verse pool

Bootstrap 95% CI over poems (2000 iters, seed=0, same method as every other E1 v2
analysis), point = F5 F1 − F10 F1.

| Model | Criterion | F5 TP/FP/FN | F5 F1 | F10 TP/FP/FN | F10 F1 | F5−F10 | CI95 | Sig? | Per-poem (F5>F10 / F10>F5 / tied) |
|---|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | verse | 220/370/100 | 0.484 | 266/456/54 | **0.511** | −0.027 | [−0.047,−0.004] | **SIG (F10 wins)** | 15/23/12 |
| Claude Sonnet 4.6 | strict | 137/453/284 | 0.271 | 164/558/257 | 0.287 | −0.016 | [−0.037,+0.008] | ns | 17/18/15 |
| Claude Sonnet 4.6 | token | 153/437/268 | 0.303 | 185/537/236 | 0.324 | −0.021 | [−0.041,+0.002] | ns | 16/20/14 |
| GPT-5.4-mini | verse | 158/315/162 | **0.398** | 132/240/188 | 0.382 | +0.017 | [−0.014,+0.049] | ns | 23/14/13 |
| GPT-5.4-mini | strict | 91/382/330 | 0.204 | 83/289/338 | 0.209 | −0.006 | [−0.034,+0.023] | ns | 13/18/19 |
| GPT-5.4-mini | token | 99/374/322 | 0.221 | 87/285/334 | 0.219 | +0.002 | [−0.026,+0.030] | ns | 15/17/18 |
| Gemini (3.6-flash) | verse | 200/277/119 | **0.503** | 204/305/116 | 0.492 | +0.010 | [−0.016,+0.039] | ns | 17/21/12 |
| Gemini (3.6-flash) | strict | 140/337/279 | 0.312 | 138/371/283 | 0.297 | +0.016 | [−0.011,+0.047] | ns | 17/20/13 |
| Gemini (3.6-flash) | token | 150/327/269 | 0.335 | 149/360/272 | 0.320 | +0.014 | [−0.009,+0.040] | ns | 18/19/13 |

**9 of 9 model×criterion comparisons are either `ns` or favor F10 by a small amount; none
favors F5.** Only one — Claude, verse (the primary metric) — reaches significance, and it
favors **F10** (+0.027 F1). Every strict/token comparison for every model is `ns`. Abu
Nuwas vs. "other" splits (full numbers in `analysis_report_multipoet.json`) show the same
pattern model-by-model as overall, no reversal.

---

## 3. SECONDARY (thin, n=9 poems, Abu-Nuwas-skewed): F5/F10 vs. Z/A/B/C/D

**Caveat stated up front**: this 9-poem subset is 5/9 (56%) Abu Nuwas poems, vs. 20%
(10/50) in F5/F10's own full pool and 20% (5/25) in `eval_pool_25.json` — the overlap is
small *and* compositionally skewed relative to either full pool, so these numbers are
indicative only, not a clean apples-to-apples comparison. `point` below is the F1
difference computed **on the same 9-poem intersection** the bootstrap CI is drawn from
(not each set's own full-pool F1 — an initial version of this analysis computed `point`
incorrectly from each side's full pool before this fix; caught before being written up).

| Model | Criterion | F5 | F10 | Z | A | B | C | D |
|---|---|---|---|---|---|---|---|---|
| Claude | verse | 0.653 | 0.654 | 0.291 | 0.642 | 0.608 | 0.317 | 0.589 |
| Claude | strict | 0.294 | 0.331 | 0.145 | 0.233 | 0.293 | 0.104 | 0.220 |
| Claude | token | 0.312 | 0.364 | 0.145 | 0.267 | 0.328 | 0.130 | 0.312 |
| GPT | verse | 0.424 | 0.390 | 0.551 | 0.596 | 0.552 | 0.314 | 0.518 |
| GPT | strict | 0.182 | 0.154 | 0.250 | 0.259 | 0.286 | 0.119 | 0.222 |
| GPT | token | 0.202 | 0.198 | 0.268 | 0.278 | 0.303 | 0.167 | 0.270 |
| Gemini | verse | 0.652 | 0.645 | 0.438 | 0.575 | 0.545 | 0.541 | 0.568 |
| Gemini | strict | 0.340 | 0.280 | 0.207 | 0.257 | 0.294 | 0.227 | 0.274 |
| Gemini | token | 0.377 | 0.318 | 0.207 | 0.297 | 0.333 | 0.295 | 0.295 |

**Gain over Z** (bootstrap CI, same 9 poems):

| Model | Criterion | F5−Z | Sig? | F10−Z | Sig? |
|---|---|---|---|---|---|
| Claude | verse | +0.362 | **SIG** | +0.363 | **SIG** |
| Claude | strict | +0.149 | **SIG** | +0.186 | ns |
| Claude | token | +0.167 | **SIG** | +0.219 | **SIG** |
| GPT | verse | **−0.128** | **SIG** | **−0.161** | **SIG** |
| GPT | strict | −0.068 | ns | −0.096 | ns |
| GPT | token | −0.066 | ns | −0.070 | ns |
| Gemini | verse | +0.214 | **SIG** | +0.207 | **SIG** |
| Gemini | strict | +0.133 | **SIG** | +0.074 | ns |
| Gemini | token | +0.171 | **SIG** | +0.111 | **SIG** |

**F5/F10 vs. the already-good 2-example sets (A/B/D)**, same 9 poems — summarized, full
numbers in `analysis_report_multipoet.json`:

- **Claude**: F5/F10 vs. A/B/D are all **ns** (F5/F10 land in the same statistical
  neighborhood as A/B/D — not a further improvement, not a regression) on verse. On
  strict/token, F10 vs. A is **SIG positive** for both criteria (F10 beats A on the span-
  level metrics specifically), everything else vs. A/B/D is `ns`. F5/F10 vs. C: **SIG
  positive** on every criterion (both multipoet sets clearly beat C, same as A/B/D already
  did in the original E1_V2_RESULTS.md finding — C's homogeneous-root examples remain the
  one weak 2-example set).
- **GPT**: F5/F10 are **SIG worse** than A, B, and D on verse (every one of those 6
  comparisons is significant and negative); strict/token are directionally the same but
  mostly `ns` at this sample size. Vs. C: `ns` everywhere — F5/F10 sit at roughly the same
  (low) level as GPT's own worst 2-example set.
- **Gemini**: mixed and criterion-dependent. F5 beats B, C, D significantly on verse (not
  A — `ns` but positive); F10 beats B, C significantly, A/D `ns`. On strict, F5 beats A,
  C, D significantly; F10 only beats C significantly. Token criterion has fewer
  significant pairs (mostly `ns`, one SIG: F5 vs. D).

---

## 4. Ensemble (2-of-3 majority vote), full 50-poem pool

Same majority-vote rule as the project's existing ensemble analysis
(`experiments/phase4_e1_v2/ensemble_v2.py`, reused unchanged).

| Set | Criterion | Ensemble F1 | Best single | Avg of 3 singles |
|---|---|---|---|---|
| F5 | verse | 0.479 | google 0.503 | 0.462 |
| F5 | strict | 0.257 | google 0.312 | 0.262 |
| F5 | token | 0.284 | google 0.335 | 0.286 |
| F10 | verse | 0.482 | anthropic 0.511 | 0.461 |
| F10 | strict | 0.254 | google 0.297 | 0.264 |
| F10 | token | 0.278 | anthropic 0.324 | 0.288 |

**Same conclusion as every prior ensemble check in this project** (Phase 1 §3e,
`E1_V2_ENSEMBLE.md`): the majority vote never beats the best single model, but does beat
the plain average of the 3 singles in every one of these 6 cells (a small, consistent
+0.01 to +0.02 F1 bump over "average model," not over "best model"). Agreement-bucket
accuracy (3/3 and 2/3-vote verses are both correctly positive ~34-43% of the time — i.e.
majority agreement does not imply correctness here; 1/3 and 0/3-vote verses are correctly
negative 70-82% of the time) is consistent across F5/F10, no interesting shift from adding
more examples.

---

## 5. Plain answer

**Do more examples from different poets help? Does 10 beat 5?**

**Mostly no, with one exception.** On the full 1000-verse pool — the reliable, primary
comparison — **8 of 9 model×criterion combinations show no significant difference between
F5 and F10.** The one exception is Claude on the primary verse metric, where F10
significantly beats F5 (+0.027 F1) — but even there, Claude's own strict/token numbers for
the same comparison are not significant, and the per-poem sign count (23 poems favor F10,
15 favor F5, 12 tied) shows a real but not overwhelming tilt, not a clean sweep. Going
from 5 to 10 different-poet examples is, for GPT and Gemini, statistically indistinguishable
from noise in every one of 6 criterion checks; for Claude it may buy a small amount on the
primary metric specifically.

**Does it beat the existing 2-example sets (A/B/C/D)?** This can only be checked on a
thin, Abu-Nuwas-skewed 9-poem overlap, so read it as indicative, not conclusive — but the
model-dependence already well-documented in `E1_V2_RESULTS.md` for Z vs. A/B/C **continues
cleanly into F5/F10**: Gemini and Claude both get a real, often-significant lift from
*any* fewshot block (2-example or multi-poet) over zero-shot Z, and the multi-poet sets
sit roughly level with (Claude) or somewhat above (Gemini, on verse) the best 2-example
sets — more examples from more poets does not clearly hurt these two models, and may help
Gemini a little. **GPT is the opposite story, sharper here than it already was for Set C**:
F5/F10 are **significantly worse** than A/B/D on this subset (and no better than C, GPT's
already-identified weak set) — for GPT specifically, piling on more examples from more
poets looks actively counterproductive, consistent with GPT's established pattern
(`E1_V2_RESULTS.md` Q1) of not benefiting from fewshot examples at all and sometimes being
actively hurt by them.

**Caveats** (same discipline as every other table in this project):
- **One run per cell, one draw of poets/verses, no noise baseline.** Nothing here has been
  replicated a second time; a single comparative result (especially the one SIG F5-vs-F10
  finding) should not be treated as fully settled, per the project's own standing
  Kenning/Periphrasis precedent (`CLAUDE.md` rule 2).
- **The vs-A/B/C/D comparison rests on only 9 poems, disproportionately Abu Nuwas (56% vs.
  20% elsewhere)** — a different overlap sample could plausibly shift GPT's apparent
  "multi-poet hurts" finding or Gemini's "multi-poet helps" finding in either direction.
  Running the optional Z add-on (Z on the full 50-poem pool, ~$6.45, not yet run) would at
  least remove the Z side of this thinness, though A/B/C/D would remain pool_25-only
  regardless.
- **F5's poet/verse selection is one specific deterministic draw** (period-diversity round
  robin + one seeded verse per poet) — a different period-ordering rule or a different
  seed could select different poets/verses entirely; no sensitivity check against an
  alternative selection rule was run.

---

## 6. Reproducing this experiment

```
python experiments/phase4_e1_v2/multipoet_examples.py [--include-f5b]   # Step 1: sets
python experiments/phase4_e1_v2/multipoet_pool.py [--include-f5b]       # Step 1: pool
python experiments/phase4_e1_v2/unit_checks_multipoet.py                 # Step 1: checks
python experiments/phase4_e1_v2/dryrun_multipoet.py                      # Step 2: cost
python experiments/phase4_e1_v2/run_multipoet.py --confirm \
    --max-additional-usd <cap>                                           # Step 3: run
python experiments/phase4_e1_v2/analyze_multipoet.py                     # Step 4: analysis
```

No API calls in any step except `run_multipoet.py --confirm`. All code under
`experiments/phase4_e1_v2/` (new files only — `prompt_builder.py`, `fewshot_prompts.py`,
`subtype_prompts.py`, `e1_config.py`/v1, `phase3_subelements/`, and `pilot_3models/` are
unmodified). Raw manifest: `results/phase4_e1_v2/run_manifest.json` (set_name `F5`/`F10`,
additive to the existing Z/A/B/C/D/D2/anthropic_opus records). Full numeric report:
`results/phase4_e1_v2/analysis_report_multipoet.json`.
