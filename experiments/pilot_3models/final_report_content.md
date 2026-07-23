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

**[NABIGHA REPLICATION RESULT — PLACEHOLDER, FILLED IN BELOW ONCE THE RUN COMPLETES]**

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
| Per-verse granularity grid (§1.6, Imru2 + Nabigha replication) | **[TBD]** |
| **Total** | **[TBD]** |

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
{{V4_SYSTEM_MESSAGE}}
```

### A.2 Full TEST results — both criteria, TP/FP/FN/TN

*(strict and token-overlap criteria, all 4 elements, all 3 models, baseline and v4_combined — reproducible via `experiments/pilot_3models/test_report.py`)*

{{APPENDIX_TEST_FULL_TABLE}}

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

{{APPENDIX_PER_VERSE_GRID}}

### A.7 Full cost breakdown

{{APPENDIX_COST_TABLE}}
