# Draft paragraph — Methods section, ground-truth reliability

**Status**: draft, with explicit `[TBD]` numeric placeholders. Do not fill these in by guessing — they come only from running `scripts/compute_agreement.py` on Dr. Hussein's completed re-annotation. Terminology follows `GLOSSARY.md` (antithesis/periphrasis), since this is new writing.

---

All ground-truth annotation for this corpus was produced by a single domain expert (Dr. Ali Hussein). To assess the stability of this annotation, a random, poem-proportional, stratified sample of 80 verses (36% of the 224-verse, 5-poem corpus) was drawn and re-annotated blind — without access to the original labels — by the same annotator after a time gap, following the same four-element, presence-plus-span label scheme used throughout the corpus. We report this as an intra-annotator (self-)agreement figure rather than independent inter-annotator agreement, since no second qualified annotator was available for this study; we note this as a limitation (see Limitations).

Agreement was measured three ways, consistent with the span-aware scoring methodology used for all model evaluation in this paper: (1) Cohen's κ on verse-level binary presence/absence, computed separately per element; (2) Krippendorff's α on the same binary judgments, which — unlike κ — pools both annotation rounds' marginal distributions when estimating chance agreement, and is reported alongside κ because the two measures can diverge under skewed label prevalence (Antithesis in particular is present in only 19.6% of verses corpus-wide); and (3) span-overlap agreement, using both the strict (substring) and token-overlap criteria defined in §[X] (`span_matching.py`), restricted to the subset of verse×element cells where both annotation rounds agreed the element was present — this is necessary because two rounds can agree a verse contains, e.g., a trope, while pointing at different phrases within it, which verse-level presence/absence alone cannot detect.

Results: Trope κ=`[TBD]`, α=`[TBD]` (n=`[TBD]` verses, `[TBD]` positive in round 1 / `[TBD]` in round 2); Simile κ=`[TBD]`, α=`[TBD]`; Periphrasis κ=`[TBD]`, α=`[TBD]`; Antithesis κ=`[TBD]`, α=`[TBD]` (smallest positive-cell count of the four, `[TBD]`; interpret with correspondingly wider uncertainty). Span-overlap agreement (strict / token), restricted to cells both rounds marked present: Trope `[TBD]`/`[TBD]`, Simile `[TBD]`/`[TBD]`, Periphrasis `[TBD]`/`[TBD]`, Antithesis `[TBD]`/`[TBD]`.

In addition to this quantitative check, a separate, purposively-selected 13-verse set spanning the disagreement patterns observed between model predictions and the ground truth (model-alternate-reading cases, elements every model missed, model-flagged-but-unannotated cases, and cross-model disagreements) was reviewed jointly with Dr. Hussein; this review is reported qualitatively in the Discussion/Limitations rather than as an agreement statistic, since the set was selected for disagreement rather than drawn at random and would bias any such statistic.

---

**Numbers NOT yet available — filled in only after Dr. Hussein completes the re-annotation and `compute_agreement.py` is run on the result**:
- All κ, α, and span-agreement values above.
- The §[X] cross-reference to the span-matching methodology subsection (fill in once the paper's section numbering is fixed).
- Whether the sample size (n=80) ultimately used matches this draft's n=80, or was revised per `agreement_protocol.md` §6 item 4's open decision.
