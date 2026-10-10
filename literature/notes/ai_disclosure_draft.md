# AI disclosure draft note (for DHQ submission)

Drafted 2026-10-07, per DHQ's AI policy (`literature/notes/dhq_format_guide.md` §"AI policy", sourced from https://dhq.digitalhumanities.org/submissions/ai_policies.html). DHQ requires disclosure of any *substantive* AI use in research and writing, placed in the methods discussion or as an appendix, and draws a hard line: AI systems are not authors, and the paper's own method — evaluating LLMs — must keep the LLMs' role as *object of study* clearly separate from any AI assistance in *writing the paper itself*.

This draft covers two categories per the policy's own distinction. Fill in bracketed placeholders once Phase 2 is complete and the paper is actually drafted; the structure and wording discipline should not change.

---

## Draft text (place in Methods or as an appendix, per DHQ's AI policy)

**AI as the object of study.** This paper's central method is the evaluation of large language models — [list final model set, e.g., Claude, GPT, Gemini, Fable] — on the task of identifying rhetorical elements in classical Arabic poetry. Every model output discussed in the Results and Discussion sections is reported as *data*: the output of the system under study, never presented as the authors' own analysis or interpretation. Model identities, versions, and prompting configurations are documented in full in [Method section / Appendix] so that the evaluation is reproducible.

**AI assistance in writing and research.** [To be completed once the writing process is finalized. If AI tools were used for any of the following, name the specific use per DHQ's policy — "authors may not use AI tools to generate the content of their submission" as a blanket matter, but assisted tasks such as finding sources, translating/clarifying language, or diagramming are permitted and must be disclosed if substantive:]
- Literature search and source-finding assistance: [e.g., "Claude (Anthropic) was used to assist with literature search, verification of bibliographic metadata against primary sources, and drafting of structured research notes; all citations were independently verified against the original publication or publisher metadata before inclusion — see `literature/RELATED_WORK_INDEX.md` and `literature/DHQ_LITERATURE_INDEX.md` for the verification record."]
- Translation/clarification of Arabic terminology: [fill in if applicable — note any case where AI-assisted translation or glossing of Arabic rhetorical terms was used, per the format guide's note that DHQ's translation-disclosure boilerplate applies here]
- Drafting assistance: [state plainly whether any portion of the prose itself was AI-drafted and then revised by the human author(s), vs. human-drafted throughout — DHQ's zero-tolerance rule on hallucinated citations means every citation must be independently author-verified regardless of drafting method]
- Routine utilities excluded from disclosure per policy: grammar/spell-checking is explicitly exempted by DHQ's policy and does not need to be itemized here.

**Accuracy responsibility.** Per DHQ's policy, the human author(s) bear full responsibility for the accuracy of all citations and content in this paper, regardless of what tools assisted in drafting or research. All citations in this paper's Works Cited were verified against the original source (PDF or publisher/DOI metadata) prior to submission — see the verification notes in `literature/notes/` for the per-source record.

---

## Open items before this can be finalized

1. Exact final model roster for Phase 2 (affects "AI as object of study" paragraph).
2. Whether any Arabic-English translation in the paper (e.g., of verse excerpts or element definitions) used AI assistance — check against `GLOSSARY.md` and `data/elements/*.txt` provenance.
3. A factual decision from the authors on how much of the paper's actual prose was AI-drafted, since this is a disclosure of fact, not a template to fill formulaically — it must accurately describe whatever process is actually used when the paper is written.
