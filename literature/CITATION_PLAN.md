# Citation Plan — DHQ paper: "Exploring the Potential of Large Language Models to Identify Challenging Rhetorical Elements"

Compiled 2026-10-07. Built from `DHQ_LITERATURE_INDEX.md`, `RELATED_WORK_INDEX.md`, `literature/notes/*.md`, and the outline in `literature/notes/dhq_format_guide.md` §(d). Citations are grouped by the section of the paper they support, each marked **Must cite / Should cite / Optional**, with a one-line reason. All entries are Harvard style per DHQ's Citation Guidelines (`https://dhq.digitalhumanities.org/submissions/citationGuidelines.html`): `Author(s). (YYYY) 'Title', Venue, vol(issue), pp. X–Y.` DHQ requires each reference cited separately in-text — never grouped. Terminology in this plan follows the corrected terms in `GLOSSARY.md` (antithesis, periphrasis, metaphor/analogy/metonymy as مجاز subtypes) since this is new writing.

No entry below is included unless it was independently verified (PDF opened and matched, or metadata confirmed via DOI/publisher page) in `DHQ_LITERATURE_INDEX.md` or `RELATED_WORK_INDEX.md`. Where a source was flagged as unverifiable in those files (e.g. the Smyth al-Sakkākī pieces, the Munazarat argument-mining paper, Al Kaabi's own "Smith 2022"/"Jones 2020"-type citations), it is **excluded here**, not cited.

---

## 1. Introduction

| Citation | Status | Reason |
|---|---|---|
| Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2). | **Must** | The direct predecessor this paper extends — states the LLM-shaped gap itself (explicitly excludes metaphor/periphrasis as "too semantic" for rules), giving the paper its opening hook. |
| Al Kaabi, S. et al. (2024) 'Developing the teaching Arabic rhetoric: A comparative analysis of artificial intelligence and traditional hermeneutical approaches', *Journal of Infrastructure, Policy and Development*, 8(15), p. 9925. | **Must** | Establishes that LLM-on-Arabic-rhetoric is a live but under-studied question — motivates "why now." |
| Ziemińska (2026) 'AI-assisted hermeneutics: validating a large language model for the rhetorical analysis of the book of revelation', *Digital Scholarship in the Humanities*, 41(2), p. 1175. | **Should** | Closest precedent in spirit (LLM + rhetorical analysis of a canonical text + expert validation) — useful to frame the paper's novelty precisely (different text, different language, multi- vs. single-model). |

## 2. Background and Related Work

### 2a. The balagha inventory and classical Arabic poetry corpus context

| Citation | Status | Reason |
|---|---|---|
| Harb, L. (2020) *Arabic Poetics: Aesthetic Experience in Classical Arabic Literature*. Cambridge: Cambridge University Press. | **Must** | Reliable modern English-language scholarly anchor for al-Jurjānī's theory (*Asrār al-Balāgha*) underlying the rhetorical-element taxonomy, without relying on an unverifiable direct medieval-text citation. |
| Fontana, C. (2025) 'The Name of the Key: Al-Sakkākī's Literary Craftsmanship and Pragmatic Poetics in Miftāḥ al-ʿUlūm', *Journal of Arabic and Islamic Studies*, 25, pp. 57–87. | **Should** | Covers the tripartite maʿānī/bayān/badīʿ system (al-Sakkākī) that structures the classical inventory the paper's 20 elements are drawn from (Cachia 1998, via Abd Alhadi et al. 2023). Metadata-only (PDF blocked), cite with care. |
| Qarah, F. (2024) 'AraPoemBERT: A Pretrained Language Model for Arabic Poetry Analysis', arXiv preprint, arXiv:2403.12392. | **Optional** | Shows large annotated resources exist for Arabic poetry's *formal* features (meter, rhyme) but not its rhetorical/semantic features — a useful one-line contrast, not central. |

### 2b. Prior automatic approaches to rhetorical-element identification

| Citation | Status | Reason |
|---|---|---|
| Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2). | **Must** | The baseline/predecessor system (rule-based, F ≈ 0.906, explicitly brackets out metaphor/periphrasis) — this paper's results must be positioned against it directly. (Already cited in §1; DHQ permits repeat citation across sections.) |

### 2c. DH precedents for annotation-category development and difficulty

| Citation | Status | Reason |
|---|---|---|
| Bender, M., Becker, M., Kiemes, C. and Müller, M. (2023) 'Category Development at the Interface of Interpretive Pragmalinguistic Annotation and Machine Learning', *Digital Humanities Quarterly*, 17(3). | **Must** | Quality criteria for category design directly relevant to defining "challenging" rhetorical-element categories; its finding that the *simplest*-looking task got the *lowest* kappa is a direct parallel to periphrasis-type difficulty. |
| Zirker, A. and Göggelmann, M. (2023) 'Case Study: Annotating the ambiguous modality of "must" in Jane Austen's Emma', *Digital Humanities Quarterly*, 17(3). | **Must** | Models treating annotator ambiguity/difficulty as something to measure (Fleiss' kappa by dimension) — supports operationalizing "challenging" empirically rather than asserting it. |
| Münz-Manor, O. and Marienberg-Milikowsky, I. (2023) 'Visualization of Categorization: How to see the wood and the trees', *Digital Humanities Quarterly*, 17(3). | **Should** | A Semitic-language poetry corpus with a figurative-device tagset (metaphor, metonymy, synecdoche, simile) — direct typological parallel, and its argument against collapsing annotator disagreement into one gold standard is relevant to this paper's own DEV/TEST and agreement design. |
| Gutman, G. (2024) 'A Network Analysis of Figurative Topic Classification: The Case Study of Timon of Athens', *Digital Humanities Quarterly*, 18(3). | **Should** | States directly that figurative language is harder for computational methods than literal language, and explicitly proposes LLMs (Llama/Gemini/ChatGPT) as future work — this paper is, in effect, that future work for a different domain. |

### 2d. LLM-in-DH literature (methodological framing)

| Citation | Status | Reason |
|---|---|---|
| Tarkka, O., Elo, K., Ginter, F. and Laippala, V. (2026) 'Do all politicians sound the same? Comparing model explanations to human responses', *Digital Humanities Quarterly*, 20(1). | **Should** | Closest DHQ precedent in genre (model-vs-human comparison, rigorous P/R/F1 + explanation analysis) and in newness (2026) — useful structurally as a model for the paper's own Results/Discussion split. |
| Dobson, J. (2021) 'Interpretable Outputs: Criteria for Machine Learning in the Humanities', *Digital Humanities Quarterly*, 15(2). | **Optional** | Useful for the cautious, non-overclaiming register DHQ favors when discussing what a model's high score does/doesn't mean — supports the Discussion section's tone, not a load-bearing citation. |

### 2e. LLM benchmarks on figurative/rhetorical language beyond DH

| Citation | Status | Reason |
|---|---|---|
| Fuoli, M., Huang, C., Littlemore, J., Turner, S. and Wilding, R. (2025) 'Metaphor identification using large language models: A comparison of RAG, prompt engineering, and fine-tuning', arXiv preprint, arXiv:2509.24866. | **Must** | The closest methodological precedent overall: full-text (not pre-segmented) metaphor identification, multiple deployment strategies, precision/recall/F1 + discrepancy taxonomy — the template this paper's evaluation design borrows from most directly. |
| Reimann, J. and Scheffler, T. (2025) 'The Struggles of Large Language Models with Zero- and Few-Shot (Extended) Metaphor Detection', *Journal for Language Technology and Computational Linguistics*, 38(2). | **Must** | Essential counterweight to Fuoli et al.'s optimism — a negative result showing zero/few-shot LLM metaphor detection fails, calibrating this paper's own expectations and justifying why setup (not just model choice) matters. |
| Balestrucci, A., Oliverio, A., Lo, C., Anselma, L., Basile, V., Mazzei, A. and Patti, V. (2025) 'When Figures Speak with Irony: Investigating the Role of Rhetorical Figures in Irony Generation with LLMs', *CLiC-it 2025*, CEUR-WS vol. 4112. | **Must** | The closest non-Arabic precedent for "LLM classifies *named* rhetorical figures against a human-annotated scheme" with quantified human-model agreement (Krippendorff's α 0.21–0.26 vs. human-human ~0.60–0.65) — a direct comparison point for this paper's own agreement numbers. |
| Hicke, R. M. and Kristensen-McLachlan, R. D. (2024) 'Science is Exploration: Computational Frontiers for Conceptual Metaphor Theory', *Computational Humanities Research Conference (CHR 2024)*. | **Should** | Tests GPT-3.5/4/4o on a single operationalized metaphor-identification prompt (MIP) — relevant precedent for this paper's own prompt design, though at the token/decontextualized level rather than full-text. |
| Ye, [et al.] (2026) 'Probing Semantic Alignment, Lexical Invariance, and Syntactic Influence in LLM Metaphor Processing', *Proceedings of ACL 2026, Volume 1: Long Papers*, pp. 27914–27932. | **Should** | A methodological caution directly useful for the Discussion: argues high LLM metaphor-task scores can reflect shallow lexical/syntactic heuristics rather than semantic understanding — important for interpreting this paper's own high-F1 elements cautiously. |
| Kühn, R., Mitrović, J. and Granitzer, M. (2024) 'Computational Approaches to the Detection of Lesser-Known Rhetorical Figures: A Systematic Survey and Research Challenges', arXiv preprint, arXiv:2406.16674 (submitted to *ACM Computing Surveys*). | **Must** | A survey specifically about rhetorical figures *beyond* metaphor/irony — exactly the "under-studied, semantically demanding figures" category periphrasis and antithesis fall into; names dataset scarcity and rule-based reliance as the field's own diagnosis, which this paper's background section should echo. |
| Kühn, R. and Mitrović, J. (2024) 'The Elephant in the Room: Ten Challenges of Computational Detection of Rhetorical Figures', *Proceedings of the 4th Workshop on Figurative Language Processing (FigLang 2024)*. | **Should** | A ready-made ten-item checklist (annotation subjectivity, context-dependence, scarce datasets, etc.) to map this paper's own error analysis against — strengthens the Discussion's comparative framing. |

### 2f. LLMs on Arabic figurative/cultural language specifically

| Citation | Status | Reason |
|---|---|---|
| Al Kaabi, S. et al. (2024) 'Developing the teaching Arabic rhetoric: A comparative analysis of artificial intelligence and traditional hermeneutical approaches', *Journal of Infrastructure, Policy and Development*, 8(15), p. 9925. | **Must** | (Repeat from §1 — DHQ cites separately per section.) The only other work combining LLMs with classical Arabic rhetoric directly; its qualitative, small-N (8 examples) design is the explicit contrast this paper's multi-model, quantified design improves on. Cite the paper's own method/findings; do **not** cite or rely on its own literature review, which contains multiple unverifiable references (see `literature/notes/2024_AlKaabi_ChatGPTArabicRhetoricTeaching.md`, "Citation verification check"). |
| Attia, M., Muhamed, A., Alkhamissi, B., Solorio, T. and Diab, M. (2026) 'Beyond Understanding: Evaluating the Pragmatic Gap in LLMs' Cultural Processing of Figurative Language', *Proceedings of EACL 2026*. | **Must** | A rigorous, recent (22-model) benchmark showing LLMs underperform on culturally grounded Arabic figurative language (Egyptian idioms/proverbs) even relative to high human inter-annotator agreement — directly strengthens the paper's "LLMs on Arabic figurative language specifically lag behind English" framing with a second, non-poetry data point. |

### 2g. Foundational / theoretical references

| Citation | Status | Reason |
|---|---|---|
| Lakoff, G. and Johnson, M. (1980) *Metaphors We Live By*. Chicago: University of Chicago Press. | **Should** | Standard Conceptual Metaphor Theory anchor if the paper's discussion of استعارة (metaphor) or مجاز invokes CMT, as Hicke & Kristensen-McLachlan (2024) do. |
| Cohen, J. (1960) 'A Coefficient of Agreement for Nominal Scales', *Educational and Psychological Measurement*, 20(1), pp. 37–46. | **Should** | Original source for Cohen's kappa, needed if the paper reports inter-annotator agreement using this statistic. |
| Hayes, A. F. and Krippendorff, K. (2007) 'Answering the Call for a Standard Reliability Measure for Coding Data', *Communication Methods and Measures*, 1(1), pp. 77–89. | **Should** | Fetchable, DOI-bearing operational source for Krippendorff's alpha (use in place of, or alongside, Krippendorff 1980/2018, which has no stable OA link) if the paper reports this statistic instead of/alongside kappa. |

## 3. Data and Annotation

| Citation | Status | Reason |
|---|---|---|
| Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2). | **Must** | Source of the REI poetry corpus and the 20-element inventory (via Cachia 1998) this paper's gold standard builds on — the corpus/annotation-scheme lineage must be cited exactly here. |
| Bender, M., Becker, M., Kiemes, C. and Müller, M. (2023) 'Category Development at the Interface of Interpretive Pragmalinguistic Annotation and Machine Learning', *Digital Humanities Quarterly*, 17(3). | **Should** | Double-annotation-plus-resolution workflow and its reported kappa pattern (simplest task = lowest agreement) are a direct methodological parallel for describing this paper's own annotation process. |

## 4. Method

| Citation | Status | Reason |
|---|---|---|
| Fuoli, M., Huang, C., Littlemore, J., Turner, S. and Wilding, R. (2025) 'Metaphor identification using large language models: A comparison of RAG, prompt engineering, and fine-tuning', arXiv preprint, arXiv:2509.24866. | **Must** | Methodological template for span-level identification evaluation design and deployment-strategy comparison (prompting vs. fine-tuning vs. RAG). |
| Hicke, R. M. and Kristensen-McLachlan, R. D. (2024) 'Science is Exploration: Computational Frontiers for Conceptual Metaphor Theory', *Computational Humanities Research Conference (CHR 2024)*. | **Optional** | If the paper's prompt design directly operationalizes a procedure (as MIP-style prompting does here), cite as precedent for that prompting strategy. |

## 5. Results

| Citation | Status | Reason |
|---|---|---|
| Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2). | **Must** | The numeric baseline (P 0.918 / R 0.902 / F 0.906, per-element) this paper's results table must be compared against directly. |
| Balestrucci, A., Oliverio, A., Lo, C., Anselma, L., Basile, V., Mazzei, A. and Patti, V. (2025) 'When Figures Speak with Irony: Investigating the Role of Rhetorical Figures in Irony Generation with LLMs', *CLiC-it 2025*, CEUR-WS vol. 4112. | **Should** | Reference point for what a "fair" LLM-human agreement level looks like (α 0.21–0.26) when discussing this paper's own agreement/discrepancy numbers. |

## 6. Discussion

| Citation | Status | Reason |
|---|---|---|
| Ye, [et al.] (2026) 'Probing Semantic Alignment, Lexical Invariance, and Syntactic Influence in LLM Metaphor Processing', *Proceedings of ACL 2026, Volume 1: Long Papers*, pp. 27914–27932. | **Must** | Essential caution for interpreting any high-F1 element: strong scores may reflect shallow heuristics, not semantic understanding — the paper's Discussion should explicitly address this possibility for its own easiest elements. |
| Reimann, J. and Scheffler, T. (2025) 'The Struggles of Large Language Models with Zero- and Few-Shot (Extended) Metaphor Detection', *Journal for Language Technology and Computational Linguistics*, 38(2). | **Must** | Error-type vocabulary (overinterpretation, domain confusion, wrong boundaries) directly reusable for this paper's own per-element error analysis, especially for metaphor/periphrasis. |
| Kühn, R. and Mitrović, J. (2024) 'The Elephant in the Room: Ten Challenges of Computational Detection of Rhetorical Figures', *Proceedings of the 4th Workshop on Figurative Language Processing (FigLang 2024)*. | **Should** | Map this paper's own difficulty findings against the field's own ten-challenge checklist — a concrete way to generalize beyond the single corpus. |
| Attia, M., Muhamed, A., Alkhamissi, B., Solorio, T. and Diab, M. (2026) 'Beyond Understanding: Evaluating the Pragmatic Gap in LLMs' Cultural Processing of Figurative Language', *Proceedings of EACL 2026*. | **Should** | Supports a broader claim (if the data bears it) that LLM weakness on Arabic figurative language is not specific to classical poetry or to this paper's corpus. |
| Dobson, J. (2021) 'Interpretable Outputs: Criteria for Machine Learning in the Humanities', *Digital Humanities Quarterly*, 15(2). | **Optional** | Tone/register model for cautious claims about what model outputs do and do not demonstrate. |

## 7. Conclusion and Future Work

| Citation | Status | Reason |
|---|---|---|
| Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2). | **Must** | Echo its own "Conclusion and Future Work" framing — explicit intellectual lineage, as recommended in `dhq_format_guide.md` §(d). |
| Ziemińska (2026) 'AI-assisted hermeneutics: validating a large language model for the rhetorical analysis of the book of revelation', *Digital Scholarship in the Humanities*, 41(2), p. 1175. | **Optional** | Possible future-work pointer: the "reproducibility" problem it raises (considerable run-to-run variability) connects to this project's own 2-run-majority discipline — could be cited as a reason that discipline matters. |

---

## DHQ articles this paper should cite to fit the DHQ conversation

To read as a DHQ-native contribution (not an NLP leaderboard paper placed in the wrong venue), the paper should visibly engage with DHQ's own annotation/categorization-difficulty discourse, not only the Abd Alhadi baseline. Recommended minimum DHQ-internal citation set, beyond Abd Alhadi et al. (already Must-cite throughout):

1. **Bender et al. (2023)** — category-design quality criteria.
2. **Zirker & Göggelmann (2023)** — ambiguity/difficulty as a measurable annotation property.
3. **Münz-Manor & Marienberg-Milikowsky (2023)** — figurative-device annotation in a cognate Semitic-poetry corpus.
4. **Gutman (2024)** — figurative language as harder-than-literal for computation, explicitly proposes LLMs as next step.
5. **Tarkka et al. (2026)** — most recent DHQ precedent for rigorous model-vs-human comparison, useful as a structural/genre model.

Optional additional DHQ engagement: **Dobson (2021)** for interpretability caution.

---

## Summary counts

- **Must cite**: 13 distinct works (several appear in multiple sections).
- **Should cite**: 11 distinct works.
- **Optional**: 5 distinct works.
- **Excluded** (unverifiable, per `RELATED_WORK_INDEX.md`/notes files): Al Kaabi et al.'s own "Smith 2022"/"Jones 2020"/"Margolis 2019"/"Wright 2021"/"Al-Ghamdi 2021"/"Al-Tamimi 2019" citations (do not cite Al Kaabi's literature review via these); Smyth's two al-Sakkākī pieces (plausible but unconfirmed by direct fetch); the Munazarat/HBKU Arabic argument-mining paper (real work, unverified publication/DOI); the PeerJ Arabic-poetry-NLP systematic review (unpublished, no confirmed metadata).
