# Paper Mapping — Existing Material vs. the DHQ Outline

Maps `literature/notes/dhq_format_guide.md` part (d)'s recommended outline (itself built from DHQ's official requirements and the structural patterns of 7 sampled DHQ articles) against what already exists in this repo. For each section: what's reusable as-is, what must be rewritten and why, what's missing entirely.

---

## 1. Abstract (~120-150 words)

- **Reusable as-is**: none of it directly — `writing/chapters/abstract_draft.md` is a complete draft but uses Phase 1's superseded terminology throughout (kenning, antonymy) and makes a claim ("Kenning remains resistant across every intervention attempted") that Phase 2's Config C finding now makes incomplete (see `results_for_paper.md`'s discrepancy note).
- **Must be rewritten**: terminology (antithesis/periphrasis per `GLOSSARY.md`), the Kenning/Periphrasis claim needs qualifying language reflecting Config C's reachable-but-unreliable finding, and — once the IAA/Phase-3-cross-model work from `experiment_priorities.md` lands — the headline finding may need updating to include a cross-model-difficulty-pattern statement if RQ3 gets resolved before submission.
- **Missing**: a stated RQ framed explicitly for DHQ's audience (`dhq_format_guide.md`'s own recommendation: "state the RQ... the method... and the headline finding/number once Phase 2 TEST results exist" — Phase 2 TEST results, i.e. a frozen Phase-2-equivalent evaluation, do not exist; Phase 2 is DEV-only throughout per its own frozen-decisions rule).

## 2. Teaser (one phrase/sentence)

- **Reusable**: none exists yet.
- **Missing entirely**: needs to be written from scratch — a short punchy line, e.g. around the gap-statement framing ("the elements rule-based systems couldn't handle are exactly the ones LLMs were asked to try").

## 3. Introduction

- **Reusable as-is**: the motivating "chat-gap observation" (Phase 2's origin story — a free-form chat session caught a periphrasis instance every pipeline configuration missed, `PROJECT_STATE.md` Phase 2 §0 item 2) is a genuinely strong, DHQ-readable hook that isn't in any chapter draft yet — it exists only in `PROJECT_STATE.md`'s internal framing.
- **Must be rewritten**: `methodology.md` §1's task-definition paragraph is solid content but is written as a methods-section opener, not an introduction-section motivator; it would need re-sequencing (motivation → contribution → roadmap) rather than content rewriting.
- **Missing**: an explicit statement of the paper's contribution relative to Abd Alhadi et al. 2023 and the other DHQ/non-DHQ precedents — this exists as a литerature-note draft (`gap_statement.md`'s ~150-word draft) but has never been integrated into a chapter-level introduction.

## 4. Background and Related Work

- **Reusable as-is**: `literature/notes/related_work_outline.md` is already a complete structural plan with per-subsection arguments (2a through 2g) built directly from the DHQ format guide's own recommendation to use "Background and Related Work" as the heading. This is the single most submission-ready piece of writing in the repo for this section — it just needs prose expansion, not restructuring.
- **Must be rewritten**: none of the outline's content needs rewriting; it needs *writing* (the outline is a plan, not prose).
- **Missing**: the actual prose paragraphs for all 7 subsections (2a-2g) — currently only argument summaries exist, not finished text.

## 5. Data and Annotation

- **Reusable as-is**: `methodology.md` §2 (corpus description, per-poem ground-truth counts table, deduplication methodology) and §3 (DEV/TEST split, leakage discipline) are both complete, carefully-sourced, and directly reusable with only a terminology pass (antithesis/periphrasis) needed.
- **Must be rewritten**: the annotation-process description needs a new paragraph on IAA — currently `methodology.md` §2's closing line ("Ground truth is drawn from a single annotator throughout; no inter-annotator agreement figure exists") is accurate but was written as a limitations-chapter pointer, not as the Data-and-Annotation section's own honest treatment DHQ reviewers would expect inline (per `dhq_format_guide.md`'s own recommendation that this section include "agreement if measured — note the DH pattern that the simplest-looking categories often get the lowest agreement").
- **Missing**: the actual IAA figure (item 1 in `experiment_priorities.md`) and — newly surfaced and not yet reflected anywhere — the TEST-leakage-via-worked-examples finding (`example_gap_analysis.md` §0), which belongs in this section as a described property of the data/prompt design, not buried only in `limitations_future_work.md`.

## 6. Method

- **Reusable as-is**: `methodology.md` §4 (prompt architecture, baseline and v4_combined rule derivation), §5 (models and settings table), §6 (scoring harness — span-level, strict/token criteria, 2-run majority protocol) are all complete, well-sourced, and need only the terminology pass plus one addition: a DHQ-required AI-use disclosure (`dhq_format_guide.md` part (a) "AI policy" — the LLMs are the object of study, and this must be stated explicitly, distinguishing that from any AI assistance used in writing the paper itself, which needs separate disclosure if used beyond grammar-checking).
- **Must be rewritten**: §4.2's prompt-refinement description should be extended to mention Phase 2's Config A/B/C disentanglement (model effect vs. terminology effect vs. format effect, `report_3i.md`) since this is now part of "the method" in a fuller sense than Phase 1 alone — currently Phase 2 is not mentioned anywhere in any chapter draft.
- **Missing**: a methods-level description of Phase 2's two-stage Config C pipeline (currently documented only in `report_3i.md`, not in any chapter draft) and the AI-use disclosure statement itself.

## 7. Results

- **Reusable as-is**: `writing/chapters/results.md` §1-§5 (frozen TEST results, run-consistency, token-criterion/antithesis divergence, trope-subtype analysis, ensemble check) are complete, well-sourced, and need only the terminology pass. The appendix TP/FP/FN table is directly reusable.
- **Must be rewritten**: §6-§8 (per-element decomposition, per-verse granularity, explanation-augmented illustrative run) are all Phase 1 supplementary findings presented as if they are the full picture of "what was tried to help Kenning" — this needs a new subsection inserted covering Phase 2's Config A/B/C findings (currently absent from this chapter entirely), since Config A/C materially change the "nothing helps Kenning" narrative these sections currently leave standing.
- **Missing**: a Results subsection for Phase 2 (Config A/B/C numbers, the مجاز مرسل probe, the run-to-run-instability finding) and, if item 2/5 from `experiment_priorities.md` are completed before submission, a Phase 3 subtype-level results subsection with real P/R/F1 rather than recall-only numbers.

## 8. Discussion

- **Reusable as-is**: `writing/chapters/discussion_draft.md` is already written using corrected terminology throughout, is explicitly marked "not yet reviewed," and is the single most DHQ-ready chapter in the repo — it already synthesizes Phase 1 and Phase 2 findings into the marker-explicitness hypothesis.
- **Must be rewritten**: minor — if Phase 3's subtype-level data is incorporated (per `experiment_priorities.md` item 2/5), the discussion's marker-explicitness hypothesis should explicitly cite the Phase 3 confirmatory pattern (`MEETING_SUMMARY.md` §6) as supporting evidence, which is not currently done (the discussion draft predates or does not reference Phase 3's `final_summary.xlsx` at all, despite being broadly consistent with it per `claim_evidence_matrix.md` C2).
- **Missing**: nothing structural — this section is in the best shape of any chapter.

## 9. Limitations

- **Reusable as-is**: `writing/chapters/limitations_future_work.md` §1-§5 (single annotator, corpus scope, span-matching ambiguity, taxonomy scope, prompt-only scope) are complete and well-argued.
- **Must be rewritten**: §6 ("Two specific unsolved cases") was written before Phase 2's Config C findings existed and should be updated — periphrasis/كناية is no longer accurately described as "resistant to every intervention attempted" once Config C's reachable-but-unreliable finding is accounted for; the honest updated framing is "reachable under free-form reasoning, but not yet a reliable decision procedure" (quoting `report_3i.md` §9's own phrase almost verbatim).
- **Missing**: the TEST-leakage-via-worked-examples finding (`example_gap_analysis.md` §0) is not mentioned anywhere in this chapter and needs its own paragraph — this is arguably the single most important omission in the current chapter drafts, since it is a real methodology gap already discovered and documented internally but not yet surfaced in any writing intended for an external reader.

## 10. Conclusion and Future Work

- **Reusable as-is**: `limitations_future_work.md` §7's four future-work items (fine-tuning, lexicon-augmented prompting, fresh held-out poem, properly-scored explanation-augmented prompt) are concrete and well-justified.
- **Must be rewritten**: minor reordering/prioritization to match `experiment_priorities.md`'s ranking if that ranking is adopted (the fresh-held-out-poem item, for instance, is ranked lower in the existing chapter draft's prose than its actual priority given the two-poem replication problem already on record).
- **Missing**: a future-work item for the single-model (Gemini-only) limitation of Phase 3, and for the IAA gap specifically as a planned next step rather than just an acknowledged limitation — currently IAA is mentioned only in Limitations, not restated as a concrete Future Work commitment.

## 11. Data Availability / Declarations

- **Reusable**: nothing exists yet, but the underlying facts are available (public GitHub repo already exists per the git status in this session's environment).
- **Missing entirely**: needs to be written from scratch, and **cannot be finalized until the licensing/rights question in `reviewer_risks.md` §7 is resolved** — this section is blocked, not just unwritten.

## 12. Notes and Works Cited

- **Reusable as-is**: `literature/CITATION_PLAN.md`, `literature/DHQ_LITERATURE_INDEX.md`, `literature/RELATED_WORK_INDEX.md`, and `literature/comparison_table.md` collectively provide the bibliographic backbone already (not re-read in full this session, but referenced consistently and specifically across every literature note read).
- **Missing**: the actual formatted Works Cited list in DHQ's Harvard author-date style (`dhq_format_guide.md` part (a) gives the exact format templates) — needs compiling from the citation plan into final form, and a decision on the "Works Cited" vs. "References" heading discrepancy the format guide itself flags (empirical practice uses "Works Cited" despite the official guidelines page saying "References").

## 13. Appendix (optional)

- **Reusable as-is**: `data/elements/*.txt` (the element definitions) are the natural candidate, matching Abd Alhadi et al.'s and Gutman's own appendix patterns per `dhq_format_guide.md` part (b). **Caveat**: if these are included as an appendix, the TEST-leakage finding (item 9 above) becomes directly visible to any reviewer who reads the appendix closely (since 3 of each file's 4-5 worked examples are literally Imru1/Jarir/Abu_Tammam verses) — this makes disclosing the leakage finding in Limitations not just good practice but close to unavoidable if the element-definition files are published as an appendix.

---

## Summary: biggest single rewrite needed

The chapter drafts (`abstract_draft.md`, `results.md`, `limitations_future_work.md`) were all written to reflect **Phase 1 only**. Phase 2's three findings — the Config A/B/C disentanglement, the مجاز مرسل run-to-run-instability discovery, and the TEST-leakage-via-worked-examples finding — exist only in `PROJECT_STATE.md` and the `results/phase2_chatlike/*.md` files, and have not been integrated into any chapter draft intended for external readers. This integration (not fresh experimentation) is the single largest piece of writing work standing between the current repo state and a submittable draft.
