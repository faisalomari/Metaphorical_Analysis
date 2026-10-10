# Open Items — before `paper_trimmed.md` / `paper_draft_for_supervisors.docx` can be submitted

A checklist of every remaining `[TBD]` and every other fact, decision, or verification step the human author(s) must supply or perform. Nothing below can be resolved by further drafting — each item requires either a fact only the human author(s) know, an action only they can take (annotation, data-rights clearance, a submission-portal check), or a judgment call this task was not positioned to make on their behalf.

## 1. Second annotator and inter-annotator agreement figures

- **What's missing**: Every κ/α/span-agreement figure the paper's own Methods section describes (Cohen's κ and Krippendorff's α on an eighty-verse stratified sample, plus strict and token-overlap span agreement) is `[TBD]` because Prof. Hussein's blind re-annotation pass is not yet complete.
- **What the human author must supply**: Complete (or commission) the re-annotation pass described in `writing/paper_plan/iaa/agreement_protocol.md`, then fill in the resulting figures in Data and Methods and Limitations and Future Work. Separately, decide — this is a judgment call, not a data point — whether a second, *independent* annotator (not Prof. Hussein re-annotating his own earlier judgments) is needed before submission, since the paper's own Limitations section already flags that the planned protocol measures self-agreement, not independent inter-annotator agreement.
- **Where it affects the paper**: Abstract (if a headline agreement figure becomes available), Data and Methods, Limitations and Future Work.

## 2. Corpus and annotation rights / licensing status

- **What's missing**: The paper's Limitations section states plainly that "the licensing and usage-rights status of the ground-truth annotations and underlying poem texts is not yet documented anywhere in this project," which blocks any Data Availability statement.
- **What the human author must supply**: Confirm with the corpus's custodians (and, if relevant, Prof. Hussein as the annotator) what rights exist to redistribute the poem texts and/or the annotation layer, and whether any portion can be released publicly or only described. This is a factual/legal determination, not a drafting task.
- **Where it affects the paper**: Limitations and Future Work; optionally, a new "Data Availability" subsection if DHQ's 2026-era norm (seen in the Tarkka et al. 2026 sample article, per `literature/notes/dhq_format_guide.md` part (b)) is to be matched.

## 3. DHQ controlled-vocabulary keywords (`#dhq_keywords`)

- **What's missing**: DHQ's own controlled keyword taxonomy, at `https://dhq.digitalhumanities.org/common/xml/taxonomy.xml`, could not be parsed as readable text during this project's format research (`literature/notes/dhq_format_guide.md`, "Could not verify / open questions").
- **What the human author must supply**: Check that taxonomy file directly (e.g. by opening the raw XML in a text editor rather than a browser's text-extraction view) at submission time, and select at least one matching controlled term — likely candidates are in Arabic/Middle Eastern studies, computational linguistics, text analysis, or machine learning, but this is unconfirmed.
- **Where it affects the paper**: Keywords section.

## 4. DHQ project-registry keywords (`#project_keywords`)

- **What's missing**: No DHQ Project Registry entry exists for this work. DHQ's own template describes this field as "in development" and likely optional.
- **What the human author must supply**: Confirm whether a Project Registry entry is expected/required at submission time (check the current OJS submission form), and either register the project or leave the field blank with that decision documented.
- **Where it affects the paper**: Keywords section.

## 5. AI-disclosure facts

Three separate factual gaps, each requiring an honest answer about the actual writing process used for this specific paper, not a template answer:

- **Literature search/source-finding assistance**: if an AI assistant helped locate, summarize, or verify any candidate source, name the tool and the specific tasks, and confirm every citation in the final Works Cited was independently verified against the original publication or DOI/publisher metadata before inclusion — per DHQ's zero-tolerance citation-accuracy policy, this confirmation is a required statement, not optional framing.
- **Translation or clarification of Arabic terminology**: state whether any AI assistance was used translating or glossing the Arabic rhetorical terms used in this paper (the element names and definitions drawn from `data/elements/*.txt` and `GLOSSARY.md`).
- **Drafting assistance**: state plainly whether any portion of this paper's prose was AI-drafted and then human-revised, or human-drafted throughout. This must describe whatever process is actually used to produce the final submitted paper — which may differ from, or include, work done in this trimming task itself — not be filled in formulaically.
- **Where it affects the paper**: AI Disclosure section (all three bullets currently `[TBD]` in `paper_trimmed.md`, unchanged from the source draft).

## 6. Author names and affiliations

- **What's missing**: No author name or institutional affiliation appears in any file in `writing/paper_draft/`. `paper_trimmed.md`'s title block currently reads `[TBD — author name(s) and institutional affiliation(s) to be supplied by the human author(s) before submission.]`
- **What the human author must supply**: The actual author list (presumably including the human author and, depending on authorship-credit norms in this field, potentially Prof. Ali Hussein given his role as sole annotator — this is the author team's own decision, not inferable from the data) and affiliations, formatted per DHQ's author-template conventions (ORCID links are common but not mandatory per the sampled articles in `literature/notes/dhq_format_guide.md` part (b)).
- **Note**: per DHQ's AI policy, restated in the paper's own AI Disclosure section, AI systems are never listed as authors regardless of how much drafting assistance they provided — this does not need a decision, only correct execution.

## 7. Article title

- **What's missing**: No confirmed title exists in any drafted section. `paper_trimmed.md` uses "Exploring the Potential of Large Language Models to Identify Challenging Rhetorical Elements in Classical Arabic Poetry" — a working title taken from this project's own `literature/notes/dhq_format_guide.md` header, chosen over the original thesis proposal's title ("Combining Classical Rhetorical Theory with State-of-the-Art AI Techniques for Discovering Hidden Tashbīh in Arabic Poetry as a Case Study," `writing/paper_draft/00_proposal_reuse_map.md`) because the proposal's title names only tashbīh/simile, while this paper evaluates four elements (trope, simile, periphrasis, antithesis).
- **What the human author must supply**: Confirm or replace this working title before submission.

## 8. Ziemińska (2026) — recommended citation, not yet used

- **What's open**: `00_merged_references.md` flags Ziemińska (2026), 'AI-assisted hermeneutics: validating a large language model for the rhetorical analysis of the book of revelation' (*Digital Scholarship in the Humanities*, 41(2)), as the closest precedent in spirit (LLM + rhetorical analysis + expert validation) but never actually drawn on in any drafted section, recommended for Introduction (novelty framing) or Conclusion (reproducibility-over-time discussion).
- **What the human author must decide**: Whether to add an actual in-text citation of Ziemińska (2026) somewhere in the paper before submission. This task did not add it, since adding a wholly new citation not already present in any source draft is outside a trimming task's scope — see `trim_log.md`'s Works Cited reconciliation.

## 9. Lakoff and Johnson (1980) — dropped from this trimmed version

- **What happened**: This task dropped Lakoff and Johnson's *Metaphors We Live By* from the trimmed Works Cited (see `trim_log.md`), since it was held "in reserve" in the source Related Work draft but never actually used to interpret any finding.
- **What the human author must decide**: If a future revision wants to invoke Conceptual Metaphor Theory specifically when discussing استعارة (metaphor) results, Lakoff and Johnson (1980) should be reintroduced at that point, with an actual argumentative use, not simply restored as a reserve citation.

## 10. Things the authors should verify themselves before submission (not `[TBD]`, but flagged as needing a check)

- **The DHQ "Works Cited" vs. "References" heading discrepancy**: `literature/notes/dhq_format_guide.md` part (a)/(c) notes that DHQ's own Citation Guidelines page names the end section "References," but every one of the seven sampled published DHQ articles actually uses "Works Cited." `paper_trimmed.md` follows the empirical practice ("Works Cited"); confirm this is still correct with DHQ editors at submission time, since house style can change.
- **Numbered vs. unnumbered section headings**: DHQ's own Style Guidelines "strongly advise... avoid[ing] numbering/lettering headings," and the published sample is split roughly 5/7 numbered vs. 2/7 not. `paper_trimmed.md` uses unnumbered, descriptive headings throughout (matching Dobson 2021 and Tarkka et al. 2026's convention); this is a reasonable default but not the only attested option, and the author(s) may prefer numbered headings instead.
- **Overall word count against DHQ's unstated length norm**: DHQ states no numeric word/page limit ("very long submissions must merit the space they occupy"), but the seven sampled articles run roughly 7,000–10,000 words body. `paper_trimmed.md` lands at ≈9,665 words body (excluding Works Cited) — within that empirical range but near its upper end; if DHQ editors request further trimming at review time, Background and Related Work and Data and Methods are the sections with the most remaining prose to tighten without touching a number or table (see `trim_log.md`, item 3 under "Things I was unsure about").
- **Every model name/version string** (Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash, Fable 5) should be checked against the project's actual run manifests one more time immediately before submission, since Data and Methods itself flags that hosted commercial models can have their underlying weights updated behind a fixed model-ID string — the names are correct as of this project's own frozen run records, but "correct as of the run" and "correct as of submission" are two different claims if a provider renames or deprecates a model string in the interim.
- **Verify no accidentally-introduced inconsistency from trimming**: this task tightened many sentences for length; the human author(s) should do one more full read-through of `paper_trimmed.md` against `09_consistency_check.md`'s own numeric-consistency table (§1) to confirm no number was altered in the course of tightening prose around it. (This task's own check, done once during drafting, found none — but a second independent read is cheap insurance before submission.)
