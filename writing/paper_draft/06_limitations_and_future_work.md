# Limitations and Future Work

## Ground truth and annotation

Every result reported here is evaluated against one domain expert's (Prof. Ali Hussein) manual rhetorical analysis. No second annotator has independently labeled any poem, and no inter-annotator agreement figure exists for this corpus at the time of writing. A blind re-annotation protocol has been designed — an eighty-verse, poem-proportional stratified sample, scored by Cohen's κ and Krippendorff's α on verse-level presence/absence, plus strict and token-overlap span agreement — but the re-annotation pass itself is not complete, so every agreement figure this protocol would produce is `[TBD]`. Even once complete, that pass measures one annotator's agreement with their own earlier judgments, not independent inter-annotator agreement; whether to pursue a genuinely independent second annotator with the relevant subject-matter expertise remains an open, unresolved decision. Readers should treat every precision figure here as a comparison against one expert's reading, not an agreed-upon gold standard — a caution the trope/periphrasis boundary especially invites, since it turns on whether a literal reading remains plausible, exactly the kind of judgment trained readers of classical Arabic rhetoric can reasonably disagree on. This is not unique to this study: Bender et al. (2023) and Zirker and Göggelmann (2023) both report, for comparably ambiguous annotation tasks, that agreement must be measured empirically rather than assumed from a category's apparent simplicity, a lesson this project's own run-to-run instability findings independently reinforce.

## Corpus scope

The corpus comprises five poems — three held out as a frozen test set, two used for development — all within the classical Arabic qaṣīda tradition and skewing toward the pre-Islamic and early Islamic period. Nothing in this paper licenses a claim that its findings generalize beyond this tradition and period; Andalusian, Abbasid-era ornate, or Mamluk-era poetry may present a different difficulty profile. The corpus is also small in absolute terms (43 antithesis instances and 52 simile instances on the full test set), and this study's own internal history records two cases — the trope subtype reversal and the antithesis over-claiming pattern — that were invisible or misleading at a smaller development-set scale and only became measurable once pooled across three test poems. There is no principled reason to assume five poems is large enough that a sixth could not produce a comparable reversal. Twelve of the twenty-five subtypes evaluated in the supplementary recall screen fall below ten ground-truth instances; these are reported for completeness but are not used to support any comparative claim in this paper, and a larger sample could confirm or overturn any of them.

## Phase 3's recall-only, Gemini-first design

The twenty-five-subtype recall screen tests only lines already tagged positive for their own subtype; no model was ever shown a negative example for any subtype, so false positives, true negatives, precision, and F1 are mathematically undefined by this design, not merely unmeasured. The screen was run first, and most extensively, on a single model (Gemini 3.5 Flash, chosen for cost); a later cross-model pass added GPT-5.4-mini on the identical rows, but Claude Sonnet 4.6 has not been run on this screen, and every subtype-level claim in this paper is scoped to at most two models for this reason, not three as in the primary evaluation.

## Model version drift and corpus rights

Every model evaluated is a hosted commercial API, pinned only by a model-ID string, with no guarantee the provider will not update weights behind that identifier; raw outputs for every run are archived specifically so a later comparison remains possible even if exact reproduction is not. Separately, the licensing and usage-rights status of the ground-truth annotations and underlying poem texts is not yet documented anywhere in this project `[TBD]`; this blocks a Data Availability statement, and is pending confirmation from the corpus's custodians before any data release can be described in a final version of this paper.

## Reconciling Phase 1 and Phase 2 without overclaiming either way

Phase 1's own internal reports describe periphrasis as resistant across every structural intervention attempted on the fixed, no-explanation JSON pipeline. Phase 2's Config C finding — a substantial periphrasis gain under a free-form reasoning format, unstable across repeated runs — does not simply confirm or overturn that earlier statement; the two are reconciled once output format is treated as its own variable, and this paper reports both findings together rather than treating either as superseding the other.

## Future work

A second, independent annotator, or completion of the blind re-annotation pass, would convert this paper's single-annotator caveat into a measured agreement figure. A negative-sampling follow-up for the subtypes this paper discusses most — particularly استعارة تمثيلية and كناية لغوية — would make precision and F1 computable where only recall currently is. Running Claude Sonnet 4.6 on the subtype screen would complete the three-model roster already used in the primary evaluation. Finally, given how much this paper's own results show recall moving with model choice and worked-example count, a systematic study varying both deliberately — rather than observing the effect incidentally, as this paper does — is a natural next step for establishing how much of the difficulty pattern reported here is a property of the task and how much is a property of specific prompting choices.

## Works Cited

Bender, M., Becker, M., Kiemes, C. and Müller, M. (2023) 'Category Development at the Interface of Interpretive Pragmalinguistic Annotation and Machine Learning', *Digital Humanities Quarterly*, 17(3).

Zirker, A. and Göggelmann, M. (2023) 'Case Study: Annotating the ambiguous modality of "must" in Jane Austen's Emma', *Digital Humanities Quarterly*, 17(3).
