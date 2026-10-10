# Significance Analysis — Bootstrap CIs and Paired Comparisons

Computed by [`significance_analysis.py`](significance_analysis.py) (same directory), run once, output captured verbatim below in the tables' numeric cells. **Zero API calls.** Every number here is derived from already-archived run outputs (`results/pilot_3models/test_final/`, `results/phase3_subelements/raw/`, `results/phase3_crossmodel/raw/openai/`) plus Prof. Hussein's ground-truth spreadsheets, loaded through the project's own unmodified `experiments/pilot_3models/` modules (`config`, `analyze`, `ground_truth`, `span_matching`, `span_scoring`). No frozen number in `paper_trimmed.md` is changed by this analysis — this document adds an uncertainty estimate around existing point estimates and reconstructs one table (the ensemble) that was previously asserted without one.

**Validation**: before trusting any new number below, the script's own strict-criterion TP/FP/FN point estimates were checked against `paper_trimmed.md`'s published raw counts (line 174). They match exactly for all 12 v4_combined cells (e.g. Trope/Gemini 45/9/134, Periphrasis/GPT 4/7/143, Antithesis/Claude 6/12/37) — confirming the re-implementation reproduces the frozen scoring, not a different method.

Addresses reviewer fix #7 (Phase 1 confidence intervals) and part of #2 (an ensemble table) from `reviewer_simulation.md`'s ranked list, and gives a partial, data-only answer to R2 §2 (whether the Phase 3 "collapse" language is statistically distinguishable from noise — see §4 below for what it still cannot answer).

---

## 1. Phase 1: bootstrap 95% CIs per element × model × prompt (strict criterion)

Method: for each cell, the three TEST poems' 151 verses are pooled; each verse's own (TP, FP, FN) contribution is fixed by the already-frozen 2-run-majority decision (this analysis does not re-litigate that decision); 10,000 bootstrap resamples (with replacement, verse-level, seed 20261007) recompute pooled precision/recall/F1 each time; the reported interval is the resample distribution's 2.5th–97.5th percentile.

### v4_combined (the paper's adopted prompt)

| Element | Model | TP/FP/FN | Precision [95% CI] | Recall [95% CI] | F1 [95% CI] |
|---|---|---|---|---|---|
| Trope | Claude Sonnet 4.6 | 25/3/154 | 0.893 [0.760, 1.000] | 0.140 [0.093, 0.191] | 0.242 [0.167, 0.317] |
| Trope | GPT-5.4-mini | 28/16/151 | 0.636 [0.488, 0.778] | 0.156 [0.110, 0.206] | 0.251 [0.183, 0.319] |
| Trope | Gemini 3.5 Flash | 45/9/134 | 0.833 [0.727, 0.926] | 0.251 [0.195, 0.313] | 0.386 [0.312, 0.459] |
| Simile | Claude Sonnet 4.6 | 28/6/24 | 0.824 [0.684, 0.941] | 0.538 [0.400, 0.690] | 0.651 [0.514, 0.779] |
| Simile | GPT-5.4-mini | 31/3/21 | 0.912 [0.800, 1.000] | 0.596 [0.452, 0.754] | 0.721 [0.597, 0.833] |
| Simile | Gemini 3.5 Flash | 32/4/20 | 0.889 [0.775, 0.976] | 0.615 [0.471, 0.771] | 0.727 [0.606, 0.833] |
| Periphrasis | Claude Sonnet 4.6 | 8/6/139 | 0.571 [0.300, 0.833] | 0.054 [0.021, 0.092] | 0.099 [0.040, 0.164] |
| Periphrasis | GPT-5.4-mini | 4/7/143 | 0.364 [0.091, 0.667] | 0.027 [0.006, 0.055] | 0.051 [0.012, 0.099] |
| Periphrasis | Gemini 3.5 Flash | 15/8/132 | 0.652 [0.444, 0.850] | 0.102 [0.057, 0.152] | 0.176 [0.102, 0.251] |
| Antithesis | Claude Sonnet 4.6 | 6/12/37 | 0.333 [0.118, 0.571] | 0.140 [0.047, 0.244] | 0.197 [0.068, 0.328] |
| Antithesis | GPT-5.4-mini | 5/17/38 | 0.227 [0.056, 0.417] | 0.116 [0.028, 0.213] | 0.154 [0.036, 0.273] |
| Antithesis | Gemini 3.5 Flash | 5/21/38 | 0.192 [0.045, 0.355] | 0.116 [0.026, 0.212] | 0.145 [0.033, 0.261] |

### baseline (for reference)

| Element | Model | TP/FP/FN | Precision [95% CI] | Recall [95% CI] | F1 [95% CI] |
|---|---|---|---|---|---|
| Trope | Claude Sonnet 4.6 | 17/3/162 | 0.850 [0.667, 1.000] | 0.095 [0.055, 0.139] | 0.171 [0.103, 0.240] |
| Trope | GPT-5.4-mini | 6/1/173 | 0.857 [0.500, 1.000] | 0.034 [0.011, 0.062] | 0.065 [0.021, 0.116] |
| Trope | Gemini 3.5 Flash | 34/4/145 | 0.895 [0.784, 0.976] | 0.190 [0.135, 0.248] | 0.313 [0.234, 0.392] |
| Simile | Claude Sonnet 4.6 | 28/6/24 | 0.824 [0.684, 0.943] | 0.538 [0.412, 0.676] | 0.651 [0.525, 0.765] |
| Simile | GPT-5.4-mini | 30/4/22 | 0.882 [0.767, 0.974] | 0.577 [0.433, 0.733] | 0.698 [0.571, 0.810] |
| Simile | Gemini 3.5 Flash | 32/7/20 | 0.821 [0.692, 0.933] | 0.615 [0.472, 0.762] | 0.703 [0.582, 0.811] |
| Periphrasis | Claude Sonnet 4.6 | 8/2/139 | 0.800 [0.500, 1.000] | 0.054 [0.021, 0.093] | 0.102 [0.041, 0.168] |
| Periphrasis | GPT-5.4-mini | 1/4/146 | 0.200 [0.000, 0.667] | 0.007 [0.000, 0.021] | 0.013 [0.000, 0.041] |
| Periphrasis | Gemini 3.5 Flash | 9/4/138 | 0.692 [0.417, 0.923] | 0.061 [0.026, 0.100] | 0.113 [0.050, 0.177] |
| Antithesis | Claude Sonnet 4.6 | 5/14/38 | 0.263 [0.071, 0.471] | 0.116 [0.028, 0.214] | 0.161 [0.040, 0.286] |
| Antithesis | GPT-5.4-mini | 4/11/39 | 0.267 [0.062, 0.500] | 0.093 [0.022, 0.184] | 0.138 [0.033, 0.261] |
| Antithesis | Gemini 3.5 Flash | 4/19/39 | 0.174 [0.040, 0.350] | 0.093 [0.022, 0.184] | 0.121 [0.029, 0.235] |

### What survives, and what does not

- **The simile/periphrasis ordering is robust to sampling noise, not just to the point estimate.** Even periphrasis's *best* 95% CI upper bound anywhere in the v4_combined table (Gemini, F1 upper bound 0.251) sits well below simile's *worst* 95% CI lower bound (Claude, F1 lower bound 0.514). The two elements' confidence intervals do not approach each other under any model. This is the one claim in the paper's Abstract/Discussion that this analysis makes *more*, not less, confident than the point estimates alone suggested.
- **GPT-5.4-mini's periphrasis cell is exactly the small-count case Reviewer 2 flagged (§1), and the interval shows why that flag was warranted**: TP=4 produces a 95% F1 CI of [0.012, 0.099] under v4_combined — a more-than-eightfold range relative to its own width, and the lower bound is close to zero. The point estimate (0.051) is not wrong, but it is one draw from a visibly wide distribution, exactly the pattern the paper's own text already uses to argue single-run numbers are unreliable (Data and Methods, "Span-level scoring") — this shows the same caution applies to the TEST-scale point estimate itself, not only to run-to-run noise.
- **Antithesis's three models are statistically indistinguishable from each other** at every granularity tested here (see §2) — appropriate, since the paper's own claim about antithesis is a shared over-claiming failure mode across all three models, not a ranking among them.

---

## 2. Phase 1: paired bootstrap F1 differences across models (v4_combined, strict)

Method: the same bootstrap draw (same resampled verse indices) is applied to both models being compared in each of the 10,000 resamples, so the comparison is paired on the same underlying verses — appropriate here because all three models are scored against the identical 151 TEST verses. `P(a>b)` is the fraction of resamples where model A's F1 exceeded model B's; this is an informal bootstrap heuristic, not a calibrated p-value (see §5).

| Element | A − B | Point diff | 95% CI | P(A>B) | P(B>A) | Distinguishable? |
|---|---|---|---|---|---|---|
| Trope | Claude − GPT | −0.010 | [−0.096, +0.079] | 0.414 | 0.585 | No |
| Trope | Claude − Gemini | −0.145 | [−0.212, −0.080] | 0.000 | 1.000 | **Yes** — Gemini > Claude |
| Trope | GPT − Gemini | −0.135 | [−0.226, −0.047] | 0.001 | 0.999 | **Yes** — Gemini > GPT |
| Simile | Claude − GPT | −0.070 | [−0.167, +0.014] | 0.049 | 0.936 | Borderline |
| Simile | Claude − Gemini | −0.076 | [−0.168, +0.002] | 0.029 | 0.968 | Borderline |
| Simile | GPT − Gemini | −0.006 | [−0.044, +0.022] | 0.311 | 0.554 | No |
| Periphrasis | Claude − GPT | +0.049 | [−0.001, +0.108] | 0.961 | 0.035 | Borderline |
| Periphrasis | Claude − Gemini | −0.077 | [−0.141, −0.017] | 0.006 | 0.993 | **Yes** — Gemini > Claude |
| Periphrasis | GPT − Gemini | −0.126 | [−0.210, −0.048] | 0.001 | 0.999 | **Yes** — Gemini > GPT |
| Antithesis | Claude − GPT | +0.043 | [−0.057, +0.150] | 0.797 | 0.194 | No |
| Antithesis | Claude − Gemini | +0.052 | [−0.047, +0.156] | 0.848 | 0.148 | No |
| Antithesis | GPT − Gemini | +0.009 | [−0.072, +0.093] | 0.609 | 0.369 | No |

**Reading this against the paper's Discussion ("Cross-model consistency and idiosyncrasy," RQ3)**: the claim "all three show periphrasis hardest and simile easiest" (per-element ordering within each model) is not challenged by this table — it is about ordering *within* a model across elements, which this table does not test. What this table *does* bear on is a different, implicit claim: whether one model is simply "better" than another across elements. The answer is no — **Gemini 3.5 Flash is the only model with a statistically clear advantage over the other two, and only on trope and periphrasis specifically**; on simile and antithesis, and on periphrasis for the Claude/GPT pair, the three models' TEST-scale performance is not distinguishable from sampling noise at this corpus size. A reader should not conclude from Table 1 alone that, e.g., GPT-5.4-mini is "worse" than Claude Sonnet 4.6 on trope (diff CI crosses zero) even though its point F1 is nominally higher (0.251 vs 0.242).

---

## 3. Ensemble (2-of-3 majority vote across models): the table Reviewer 2 §3 asked for

Reviewer 2 (`reviewer_simulation.md` §3) flagged that `paper_trimmed.md`'s "Trope subtype breakdown" section asserts an ensemble finding ("[a] majority-vote ensemble across all three models gives no improvement over the best single model for trope or periphrasis... and is worse than the best single model for simile") with **no table, no TP/FP/FN, and no stated voting rule anywhere in the paper**. This table reconstructs it from the same archived run outputs, using the most natural voting rule given what the paper already reports (2-of-3 majority on each model's own already-majority-voted per-verse decision; span for a TP determined by `best_match` against whichever provider in the majority supplied an appearance), strict criterion, v4_combined, pooled TEST:

| Element | TP | FP | FN | Precision | Recall | F1 | Best single-model F1 | Ensemble vs. best single |
|---|---|---|---|---|---|---|---|---|
| Trope | 31 | 7 | 148 | 0.816 | 0.173 | 0.286 | 0.386 (Gemini) | **Worse** |
| Simile | 29 | 6 | 23 | 0.829 | 0.558 | 0.667 | 0.727 (Gemini) | **Worse** |
| Periphrasis | 8 | 2 | 139 | 0.800 | 0.054 | 0.102 | 0.176 (Gemini) | **Worse** (≈ equal to Claude's own 0.099) |
| Antithesis | 5 | 17 | 38 | 0.227 | 0.116 | 0.154 | 0.197 (Claude) | Worse |

**This supports the paper's existing prose claim with numbers, and sharpens it**: the ensemble is not merely "no improvement" on trope and periphrasis — on every one of the four elements, including antithesis (not previously discussed in this context), 2-of-3 majority voting underperforms the single best model. The periphrasis ensemble (F1=0.102) lands almost exactly at Claude Sonnet 4.6's own standalone periphrasis score (F1=0.099, Table 1 v4_combined) rather than anywhere near Gemini's higher standalone score (0.176) — consistent with the paper's own diagnosis elsewhere that "the models miss the same instances, not independent errors an ensemble could average out" (Results, "Trope subtype breakdown"): when the three models' periphrasis hits barely overlap, a 2-of-3 rule rarely finds two models agreeing on the same true positive, so recall drops toward whichever pair of models happens to overlap most, which is not the same as the best individual model's recall.

**Caveat**: this is one voting rule (majority-of-majorities) under one criterion (strict) and one prompt (v4_combined); the paper's original one-sentence claim does not specify which rule or criterion it used, so this table cannot confirm it is *the same* reconstruction the original internal analysis ran — only that *a* reasonable, stated reconstruction from the same archived data supports the same qualitative conclusion.

---

## 4. Phase 3: paired recall comparison on identical rows (Gemini 3.5 Flash vs. GPT-5.4-mini)

Method: `results/phase3_subelements/raw/{subtype}_all.jsonl` (Gemini) and `results/phase3_crossmodel/raw/openai/{subtype}_all.jsonl` (GPT) share identical `row_id` values for the same subtype (verified directly, not assumed — see §5 for one exception). A "hit" is span-level, matching the paper's own `*_strict` convention: a run counts only if it both claims the subtype exists *and* its predicted span strictly overlaps that row's own annotated ground-truth span (the naive "exists"-only criterion overstates recall — e.g. it gives Gemini 0.938 instead of 0.719 on كناية لغوية — because a verse can contain other figures the model may be matching instead; see `results/phase3_crossmodel/summary.md`'s own naive-vs-strict distinction). Majority is taken over each model's 2 runs per row, then recall is bootstrapped by resampling row_ids (paired: the same resampled rows are used for both models in each draw).

| Subtype | n (rows) | Gemini recall [95% CI] | GPT recall [95% CI] | Diff (Gemini−GPT) [95% CI] | P(Gemini>GPT) |
|---|---|---|---|---|---|
| كناية لغوية | 32 | 0.719 [0.562, 0.875] | 0.031 [0.000, 0.094] | +0.688 [+0.531, +0.844] | 1.000 |
| استعارة تمثيلية | 26 | 0.154 [0.038, 0.308] | 0.577 [0.385, 0.769] | −0.423 [−0.654, −0.192] | 0.001 |

**Both reversals are statistically overwhelming, not sampling noise** — neither difference's confidence interval comes close to zero, and the validation point estimates (23/32 and 1/32 for كناية لغوية; 4/26 and 15/26 for استعارة تمثيلية) match the archived `crossmodel_scoring_snapshot.json`'s own `*_strict` fields for the first subtype exactly, and closely (within the row-count discrepancy noted in §5) for the second.

**What this does, and does not, settle for Reviewer 2 §2's "model-specific collapse" objection**: this analysis confirms the recall *gap* itself is real and not an artifact of small-sample noise on either model's side — a legitimate partial answer to the "is this just noise" half of the objection. It does **not** answer the objection's deeper, structural point: recall-only data, bootstrapped or not, still cannot distinguish a genuine capability gap from a shift in a model's decision threshold (a model that recalls less here while also producing far fewer false positives elsewhere would look identical on this metric). A confidently-estimated recall gap is not the same claim as a confidently-estimated *capability* gap. The paper's "collapse" language should still be softened per the reviewer's objection (see `changes_v2.md` item 5) — this analysis changes *how sure we can be the numbers aren't noise*, not *what kind of difference the numbers are evidence of*.

---

## 5. What this analysis cannot support

- **No multiple-comparison correction.** §1 reports 24 CIs and §2 reports 12 paired comparisons; at a nominal 95% level, roughly one or two "significant" results among this many tests would be expected by chance alone even if no true difference existed anywhere. None of the findings highlighted above rest on a single borderline interval, but the Simile "borderline" rows in §2 specifically should not be read as confirmed effects.
- **Run-to-run (within-cell) noise is not estimated, only cross-verse noise.** Every cell's underlying prediction was already collapsed into one 2-run-majority decision per verse before this bootstrap ever ran; resampling verses estimates how much the pooled F1 would vary if a different sample of TEST verses had been drawn, not how much it would vary if the same verses were re-run against the API again. The project's own documented incident (an apparent eightfold periphrasis gain on one run that fell to roughly a quarter of that on a second run, Data and Methods) is exactly this second kind of noise, and this analysis cannot bound it — only 2 runs exist per cell, too few to itself bootstrap. **The true uncertainty around every number in §1–§3 is therefore at least as wide as reported, and plausibly wider.**
- **Verse-level bootstrap treats 151 TEST verses as exchangeable, when they come from only 3 poems.** A stricter cluster-bootstrap (resampling whole poems, n=3) would produce enormous, uninformative intervals, but would be the more conservative choice if poem-level stylistic effects matter — plausible, given the paper's own finding that antithesis support is wildly uneven by poem. This analysis reports the less conservative verse-level bootstrap as the practical middle ground; a reader who suspects strong poem-level clustering should treat every interval above as an underestimate.
- **`P(A>B)` is a bootstrap resampling proportion, not a calibrated frequentist p-value or a Bayesian posterior probability.** It is reported because it is the most direct, assumption-light summary of "how often did the ranking flip across resamples," not because it carries the same guarantees a parametric test would.
- **The استعارة تمثيلية row count does not reconcile.** `results/phase3_crossmodel/raw/crossmodel_scoring_snapshot.json` reports n=28 for this subtype; the per-row `.jsonl` files this analysis actually read (`results/phase3_subelements/raw/استعارة_تمثيلية_all.jsonl` and `results/phase3_crossmodel/raw/openai/استعارة_تمثيلية_all.jsonl`) contain only 26 matching `row_id` values between the two models, and the two files agree with each other on which 26. Two rows present in the published aggregate figure (n=28, TP=4/16) could not be located in the archived per-row data read for this analysis. This is flagged, not resolved — it does not change the direction or statistical clarity of the finding (4/26=0.154 vs. the published 4/28=0.143; 15/26=0.577 vs. 16/28=0.571), but a human author should locate the missing 2 rows before citing this table's exact n in the paper.
- **This analysis does not address Reviewer 1's crosswalk-validity objection (§1 of her review) or quantify worked-example leakage (§2)** — those are separate, unresolved items (see `crosswalk_audit_sheet.xlsx` and `leakage_quantification.md` in this same directory).
- **No new data was collected and none of Phase 1's frozen TEST numbers were altered.** This document only adds uncertainty bounds and one reconstructed table around numbers `paper_trimmed.md` already reports.
