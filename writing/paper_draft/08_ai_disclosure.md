# AI Disclosure

*Per DHQ's AI policy (https://dhq.digitalhumanities.org/submissions/ai_policies.html), placed in the methods discussion or as an appendix. The policy draws a hard line between AI as the object of study and AI assistance in writing the paper itself, and requires disclosure of any substantive use of the latter.*

## AI as the object of study

This paper's central method is the evaluation of large language models — Claude Sonnet 4.6 (Anthropic), GPT-5.4-mini (OpenAI), and Gemini 3.5 Flash (Google), with Fable 5 (Anthropic) used only in the supplementary disentanglement experiment — on the task of identifying rhetorical elements in classical Arabic poetry. Every model output discussed in the Results and Discussion sections is reported as data: the output of the system under study, never presented as the authors' own analysis or interpretation. Model identities, versions, call dates, temperature settings, and prompting configurations are documented in full in the Data and Methods section and the project's archived run manifests, so that the evaluation is reproducible against the exact configuration used, independent of any later drift in the underlying hosted models.

## AI assistance in writing and research

- **Literature search and source-finding assistance**: `[TBD — to be completed by the human author(s) once the final writing process for this paper is settled. If an AI assistant was used to help locate, summarize, or verify candidate sources, name the tool, the specific tasks it was used for, and confirm — as DHQ's zero-tolerance citation-accuracy policy requires — that every citation in the final Works Cited was independently verified against the original publication or publisher/DOI metadata before inclusion, not accepted on the assistant's word alone.]`
- **Translation or clarification of Arabic terminology**: `[TBD — state whether any AI assistance was used in translating or glossing Arabic rhetorical terms used in this paper (e.g., the element names and definitions drawn from data/elements/*.txt and GLOSSARY.md), consistent with DHQ's own boilerplate for AI-assisted translation disclosure noted in the author TEI template.]`
- **Drafting assistance**: `[TBD — state plainly whether any portion of this paper's prose was drafted with AI assistance and then revised by the human author(s), or was human-drafted throughout. This is a disclosure of fact about the actual process used to produce this specific paper, not a template answer, and must be filled in accurately once that process is complete, not assumed from this draft's own production method.]`
- **Routine utilities excluded from disclosure per policy**: grammar and spell-checking are explicitly exempted by DHQ's AI policy and are not itemized here.

## Accuracy responsibility

Per DHQ's policy, the human author(s) bear full responsibility for the accuracy of all citations and content in this paper, regardless of what tools assisted in drafting or research. All citations in this paper's Works Cited were verified against the original source (PDF or publisher/DOI metadata) prior to submission; the per-source verification record is maintained in `literature/notes/` and `literature/RELATED_WORK_INDEX.md` / `literature/DHQ_LITERATURE_INDEX.md`.

## Open items before this disclosure is final

1. The exact final model roster is fixed above (Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash, Fable 5) based on the Data and Methods section as currently drafted; revisit if the model roster changes before submission.
2. Whether any Arabic–English translation in the final paper (verse excerpts, element definitions, or glossary terms) used AI assistance beyond what `GLOSSARY.md` and `data/elements/*.txt` already document as their own provenance — unresolved, see `[TBD]` above.
3. A factual decision from the human author(s) on how much of the paper's prose was AI-drafted — this cannot be filled in formulaically and must accurately describe whatever process is actually used when the final paper is written.
