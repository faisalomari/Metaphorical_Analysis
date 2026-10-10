# Changes v1 (`paper_trimmed.md`) → v2 (`paper_v2.md`)

Every change below is a wording, structuring, or evidentiary addition. **No number, Arabic text, or citation in `paper_trimmed.md` was altered** — every change either adds new, separately-sourced material (the ensemble table, the bootstrap-CI pointers, the leakage counts) or softens/relocates existing prose. Where a number appears that was not in v1, it is cited to a new supplementary file in this same directory, not asserted without a source.

Numbering follows `reviewer_simulation.md`'s ranked list where applicable.

---

## 1. Ensemble-vote claim given a table (ranked-fix #2, Reviewer 2 §3)

**Objection answered**: "no ensemble F1, TP/FP/FN, or methodology for how the ensemble vote was constructed... appears anywhere in the paper" — exactly the kind of claim the project's own standing discipline ("always report raw TP/FP/FN") would normally require.

**Before** (Results, "Trope subtype breakdown"):
> A majority-vote ensemble across all three models gives no improvement over the best single model for trope or periphrasis (the models miss the same instances, not independent errors an ensemble could average out), and is worse than the best single model for simile. *Source: `PROJECT_STATE.md` §3e.*

**After**:
> A majority-vote ensemble (2-of-3 agreement across the three models' own per-verse majority decisions, strict criterion, pooled TEST) underperforms the best single model on every one of the four elements, not only trope and periphrasis: Trope TP=31/FP=7/FN=148, F1=0.286 (against Gemini 3.5 Flash's single-model F1=0.386); Simile TP=29/FP=6/FN=23, F1=0.667 (against Gemini's 0.727); Periphrasis TP=8/FP=2/FN=139, F1=0.102 (against Gemini's 0.176); Antithesis TP=5/FP=17/FN=38, F1=0.154 (against Claude's 0.197). [...] *Source: `significance_analysis.py` / `significance_results.md` §3...*

**Not removed, because the underlying table was reconstructible** from already-archived run outputs with a stated voting rule (2-of-3 majority of each model's own already-majority-voted decision) — the reviewer's two offered options were "removed or given the same TP/FP/FN table treatment," and the data existed to do the latter. The reconstruction additionally found the claim extends to antithesis, not only trope/simile/periphrasis — new information the original one-sentence claim did not cover, now reported.

---

## 2. Periphrasis "reachable" framing softened in Abstract and Conclusion (ranked-fix #3, Reviewer 1 §3)

**Objection answered**: "this one-poem, run-unstable result should be elevated to the Abstract and the Conclusion's second sentence at all, given how much interpretive weight... a casual reader will place on a sentence that appears twice at the paper's most-read positions."

**Before** (Abstract):
> Supplementary experiments show periphrasis is reachable, though not yet reliably decidable, under a free-form reasoning format, and that several rhetorical subtypes are strikingly sensitive...

**After** (Abstract):
> A single-poem, preliminary supplementary experiment suggests periphrasis may be reachable, under a free-form reasoning format, though this specific gain did not replicate across runs and is not a settled finding (see Discussion); a separate supplementary screen shows that several rhetorical subtypes are strikingly sensitive...

**Before** (Conclusion):
> A supplementary disentanglement experiment and a twenty-five-subtype recall screen extend this picture further, showing that periphrasis is reachable, if not yet reliably decidable, under a different output format, and that several subtypes are strikingly sensitive to which model is queried...

**After** (Conclusion):
> A supplementary disentanglement experiment and a twenty-five-subtype recall screen extend this picture further: a single-poem, preliminary probe suggests periphrasis may be reachable under a different output format, though this specific finding is run-to-run unstable and has not replicated beyond one poem (see Results, "Phase 2: Config A/B/C disentanglement," and Discussion), and several subtypes are strikingly sensitive...

Also softened identically in Discussion's "A difficulty pattern, not a difficulty scale" section (the periphrasis-exception paragraph) and in "Reconciling Phase 1 and Phase 2" (the paper's own transition sentence now reads "periphrasis may be reachable under a different output format, but this specific finding is single-poem, run-to-run unstable... and not yet reliably decidable" rather than asserting reachability as the main clause).

**Why this is the right fix, not over-correction**: Results already uses this exact hedge ("single-poem and preliminary, not a replicated finding"); the fix makes the Abstract and Conclusion consistent with the paper's own most careful language, rather than inventing a new, more cautious position the data doesn't support either.

---

## 3. Phase 1/Phase 3 scope caveat moved to first use in Discussion (ranked-fix #4, Reviewer 2 §5)

**Objection answered**: the "two-model, recall-only" scope caveat "appears four sections later than where the comparison is actually made, and a reader moving straight through Discussion will not have it in view at the moment it is needed."

**Before** (Discussion, "Cross-model consistency and idiosyncrasy"):
> At the level of individual subtypes, however, the two-model screen shows GPT-5.4-mini scoring strictly lower than Gemini 3.5 Flash on ten of thirteen reliable subtypes and strictly higher on the other three, with the كناية لغوية and استعارة تمثيلية reversals above as the sharpest examples.

**After**:
> At the level of individual subtypes, however, the two-model screen — scoped to Gemini 3.5 Flash and GPT-5.4-mini only, pooled across DEV and TEST poems rather than TEST alone, and recall-only by design (see Limitations, "Phase 3's recall-only, Gemini-first design," for the full scope statement) — shows GPT-5.4-mini scoring strictly lower than Gemini 3.5 Flash on ten of thirteen reliable subtypes and strictly higher on the other three...

The original Limitations-section caveat is unchanged and still present; this adds a pointer at the point of first use, rather than removing the fuller statement from Limitations.

---

## 4. "Model-specific collapse" language softened (ranked-fix #5, Reviewer 2 §2)

**Objection answered**: "Recall alone cannot distinguish a genuine capability gap from a shift in a model's *decision threshold*... Without precision, 'collapse' is overstated."

**Before** (Results, Phase 3 section):
> ...a model-specific, not task-intrinsic, collapse (GPT's two runs agree closely at 1/32 and 2/32, so this is not single-run noise).

**After**:
> ...a large, model-specific recall gap (GPT's two runs agree closely at 1/32 and 2/32, so this is not single-run noise; a paired bootstrap over these same rows puts the gap at +0.688, 95% CI [+0.531, +0.844], see `significance_results.md` §4). This paper reports the gap as a recall difference, not as a "collapse," because Phase 3's recall-only design (see below) cannot distinguish a genuine capability gap from a shift in a model's decision threshold...

**Before** (Discussion, "Prompt sensitivity as a finding"):
> ...so this is a model-specific collapse, not single-run noise.

**After**:
> ...so this is a large, model-specific recall gap, not single-run noise (confirmed by a paired bootstrap over the same rows; see Results and `significance_results.md` §4). This paper deliberately does not call this a "collapse": Phase 3's recall-only design means precision, false positives, and true negatives are never measured for either model, so a large recall gap here is consistent with either a genuine capability difference or a difference in how conservatively each model answers "exists" generally — the data available cannot distinguish the two...

**Note on what changed and what didn't**: the reviewer's objection was about word choice/inferential overreach, not about whether the gap is statistically real. This revision keeps (and strengthens, with a bootstrap CI) the claim that the gap is not noise, while removing the word that implies a specific, unmeasurable cause (capability failure as opposed to threshold shift).

---

## 5. Seed/temperature/run policy stated explicitly (ranked-fix #6, Reviewer 2 §4)

**Objection answered**: "was a seed parameter available from any of the three providers and not used, or unavailable from all three? If available and unused, that is a mitigation the paper should have applied... if unavailable, the paper should say so explicitly."

**Before**: Data and Methods, "Models" ended after naming the three models, temperature, and JSON format — no mention of seed parameters anywhere in the paper.

**After** (new paragraph added to "Models"):
> No seed parameter is passed in any of the three provider wrapper functions used for this evaluation (`experiments/pilot_3models/providers.py`). As of the API versions this project used, OpenAI's and Google's chat/generation APIs each expose a seed parameter capable of constraining, though not guaranteeing, deterministic output; Anthropic's Messages API exposes no equivalent parameter. Temperature 0 did not, in practice, yield run-to-run deterministic output for any of the three models in this project's own data... — the two-run-majority protocol exists specifically because of this observed non-determinism. A seed parameter, where available, was not relied upon as a substitute for that protocol and was not tested as an alternative to it...

**Basis**: verified directly against `experiments/pilot_3models/providers.py` (`call_anthropic`, `call_openai`, `call_google`) — none passes a `seed` argument. The claim about which providers' public APIs expose a seed parameter is stated as "as of the API versions this project used" rather than as a permanent fact, since provider APIs change.

Also added to Limitations ("Model version drift and corpus rights"): one sentence tying the no-seed fact to the existing version-pinning caveat, so the two related reproducibility risks are stated together.

---

## 6. Zero-shot status and worked-example overlap counts stated explicitly, with a new DEV-leakage finding (relates to Reviewer 1 §2 / ranked-fix #10's spirit, done at $0 since the counting, not new data collection, was the missing piece)

**Objection answered**: Reviewer 1's leakage objection asked for "a quantified estimate of the worked-example leakage's effect" — this revision supplies the exact counts the paper's prose previously only characterized qualitatively ("three of every element file's four or five worked examples"), and surfaces a second leakage channel the original text did not mention at all.

**Before** (Data and Methods, "The elements and subtypes," final paragraph):
> A later analysis found that three of every element file's four or five worked examples are, in fact, literal verses from the three TEST poems this paper's primary evaluation scores — a held-out-set exposure present in every prompt variant used in this paper, discussed as a limitation below rather than corrected retroactively...

**After**:
> A later analysis found that 11 of the 19 worked examples across the four element files (58%) are, in fact, literal verses from the three TEST poems this paper's primary evaluation scores — a held-out-set exposure present in every prompt variant used in this paper's primary (zero-shot) evaluation, discussed as a limitation below rather than corrected retroactively... **The same four files' remaining examples are drawn from the two DEV poems, which creates a parallel, structurally identical exposure for Phase 2's Config A and Config B (both reuse these same files unedited, scored on DEV only): every one of the 8 DEV-poem example slots across the four files coincides with a verse in Config A/B's own DEV-only scored set — a channel this paper had not previously quantified.** Config C's prompt, by contrast, contains no worked example of any kind... Exact per-file, per-example counts and verse references for all of the above are tabulated in the supplementary `leakage_quantification.md`...

**This is a new finding, not merely a rewording**: the DEV-poem leakage channel for Config A/B (§2 of `leakage_quantification.md`) was not stated anywhere in v1. It is added here because it follows the same logic the paper already uses for the TEST channel, is $0 to state (pure code/file inspection, no new API calls), and a reviewer who checks `example_gap_analysis.md` (already in the repository) could notice the gap in the paper's current framing if it weren't added.

Corresponding additions: "Prompting design" section now states explicitly that Config C's Stage 1 prompt has zero worked examples (verified against the prompt template) and that Config A/B's examples are unchanged from Phase 1 "including its worked examples" / "otherwise unchanged" (made explicit, previously only implied). The Phase 2 Config A/B/C results table now has a parenthetical noting both configurations carry identical example exposure (so the table's own comparison isn't confounded by a difference in example presence between its two columns), and the Config C paragraph now notes the asymmetry between Config C (no examples) and the existing-pipeline comparison figure (does have examples).

---

## 7. Bootstrap confidence intervals added as supplementary material and referenced at point of use (ranked-fix #7, Reviewer 2 §1)

**Objection answered**: "No significance testing or confidence intervals are reported anywhere, despite denominators small enough that this matters a great deal."

**New supplementary files**: `significance_analysis.py` (the bootstrap/paired-comparison code, reusing the project's own unmodified scoring modules) and `significance_results.md` (the results, with a "what this analysis cannot support" section).

**Paper-text additions** (no removals): a new paragraph after Table 1 in Results pointing to the CI table and summarizing its two most load-bearing findings (the simile/periphrasis CI separation; GPT-5.4-mini's wide periphrasis interval and which cross-model rankings in Table 1 are/aren't statistically distinguishable); a parallel pointer added to Discussion's "A difficulty pattern" and "Cross-model consistency" sections and to the Conclusion's first paragraph.

**Scope of the claim added**: strictly "this ordering holds under resampling of the TEST verses" — not a claim that run-to-run (measurement) noise has been bounded, which `significance_results.md` §5 states explicitly cannot be done with only 2 archived runs per cell.

---

## 8. Crosswalk-mapping audit instrument referenced (relates to Reviewer 1 §1 / ranked-fix #8 — the audit *instrument* is $0 to build; the audit itself still requires Prof. Hussein's time and is explicitly NOT claimed as complete)

**Objection answered**: "the paper later argues the trope/periphrasis boundary itself 'turns on whether a literal reading remains plausible'... the reviewer wants to know how much of the periphrasis/trope confusion the models exhibit is actually inherited from an unaudited label-mapping step."

**New supplementary file**: `crosswalk_audit_sheet.xlsx` — a blind, ~40-category random sample (from the 59 distinct category labels found by direct enumeration of the ground-truth spreadsheets — see note below) with bilingual instructions, for Prof. Hussein to mark agree/disagree against his own expert judgment, with no verse counts shown (to keep the check blind to category frequency).

**Paper-text additions**: one new sentence in Data and Methods noting the instrument has been prepared but not completed; one new paragraph in Limitations ("Ground truth and annotation") stating explicitly that until the audit comes back, "the possibility that some fraction of the trope/periphrasis confusion this paper reports is inherited from the mapping step itself... [should be treated] as open and unquantified, not as ruled out" — language chosen to match the reviewer's own framing rather than overstate what the (not-yet-returned) instrument has shown.

**What this explicitly does NOT claim**: that the crosswalk has been validated. The paper now states the audit exists and is pending, not that it has resolved anything. See "What remains for the human authors" below.

**A discrepancy surfaced, not resolved**: the paper's existing text describes "a fifty-three-category classical rhetoric taxonomy" (unchanged in this revision, since v2 does not alter v1's numbers). Direct enumeration of the five ground-truth spreadsheets' own primary/secondary label columns (`crosswalk_audit_builder.py`) finds **59** distinct (primary, secondary) label pairs, not 53. This is flagged here and in the final task report, not corrected in the paper body, since (a) resolving it requires knowing where the "fifty-three" figure in the original source material came from (course materials vs. this specific annotation pass) and (b) the task's own standing instruction is not to change paper numbers except where a listed fix requires it — this discrepancy is not one of the five fixes the task specified, so it is surfaced for the human authors rather than silently corrected or silently left unmentioned.

---

## 9. What was considered and NOT changed, with reasons

- **AI Disclosure's three `[TBD]` items** (ranked-fix #1): **not filled in.** These require a factual, first-person statement from the human author(s) about their own writing process for this specific paper — not something this task has access to or standing to assert on their behalf. Inventing an answer would itself be exactly the kind of inaccurate AI Disclosure DHQ's policy is meant to catch. One sentence was added to the "Drafting assistance" `[TBD]` item noting that this v2 revision was itself AI-produced, so whatever the human authors ultimately state must account for this fact if any of v2's text is carried into the final submission — this is a factual note about what this task did, not a substitute for the author's own disclosure.
- **The "53-category" figure**: see item 8 above — flagged, not changed, since changing it was not one of the five requested fixes and the task's standing instruction is to preserve numbers except where a fix requires a change.
- **Author names, DHQ keywords, title, licensing status, IAA figures**: all remain `[TBD]` exactly as in v1 — these are the pre-existing `open_items.md` list, none of which this task's scope (or access to facts) can resolve.
- **Phase 1's frozen TEST numbers, every raw TP/FP/FN count, every cited percentage**: unchanged throughout. Every new number in v2 is either (a) copied verbatim from v1, or (b) newly computed in a supplementary file and explicitly cited to it.
