# Münz-Manor & Marienberg-Milikowsky (2023) — Visualization of Categorization: How to See the Wood and the Trees

DHQ 17(3), https://dhq.digitalhumanities.org/vol/17/3/000703/000703.html — PDF: `literature/related_work/dhq/2023_MunzManor_VisualizationOfCategorization.pdf`
Read: all text pages (p.1–18); figure pages 13–16 contain charts, and the reference list (p.18–20) was not read. Page refs are PDF pages; "¶" is DHQ's paragraph number. "Not reported" means not found.

**Important scoping fact:** this is a manual-annotation and visualisation study. It does not build or evaluate an automatic detector of figurative language (it only mentions one as ongoing work, p.18 note 8).

## Research question and task definition
- Does figurative language in early Hebrew liturgical poetry (piyyut) really play only a marginal role, and what happens when a hand-annotated corpus is re-examined with computer-assisted annotation (CATMA) and a new visualisation tool, ViS-À-ViS? (abstract; p.2 ¶2; p.3 ¶6–8)
- Methodological question: how to move between detailed annotation ("trees") and corpus-level generalisation ("wood"), and how categories get re-assessed once visualised (a "hermeneutical circle") (abstract; p.17 ¶43).
- Task: manual in-line annotation of figurative devices (by word spans), then counting and visualising their distribution (p.3 ¶6; p.18 note 4).

## Data
- Corpus: all known poems of early (5th c. CE, Galilee) piyyut recovered from the Cairo Genizah: 211 poems, 47,556 words, mostly anonymous (p.2 ¶2).
- Language: Hebrew (late antiquity).
- Of 47,556 words, 5,113 are figurative (11%) (p.3 ¶8). The dissertation had stated roughly 1,000 of about 5,000 lines contained figurative devices (20%), and about 100 lines had developed figurative usage (p.2 ¶4).
- Comparison corpora newly annotated for figurative language: the Book of Psalms (14% figurative words) and the poetry of Pinchas the Priest, 9th c. (9%) (p.3 ¶9). Their sizes: not reported.
- Genre-level figurative density, e.g. Hosha'not at 25% against 11% overall (p.4 ¶10).
- Source: manuscripts of the Cairo Genizah, original annotations from Münz-Manor's 2006 dissertation.

## Annotation scheme
- Original paper-based stage: flat tagset of metaphor, metonymy, synecdoche and simile, marked with coloured highlighters; the authors say no well-defined tagset existed and the definitions "bore some flexibility" (p.2 ¶2).
- CATMA stage: the paper annotations were uploaded unchanged to keep the experiment sound (p.3 ¶7). A richer, hierarchical tagset is discussed but the final tagset is not listed in the article (not reported). Annotation targets individual text elements, not whole texts (p.3 ¶5; "in-line annotation", p.18 note 4).
- Annotator(s): Münz-Manor (the dissertation annotation). Number of annotators and any second-annotator study: not reported. Inter-annotator agreement: not reported. The authors argue against collapsing disagreement into a gold or silver standard and instead visualise multiple annotators side by side (p.10–11 ¶33–34).
- The authors state that deciding whether a word is figurative is a hermeneutic act on which scholars differ, and even the same annotator may differ later (p.3 ¶7).

## Method
- CATMA for annotation and queries; export to ViS-À-ViS (their own web tool, Vue.js front end, Python Flask back end; p.18 note 7) which offers Gantt, stacked area, sunburst, force-directed network and bubble charts, tagset browsing, multi-annotator view, gallery and boards (p.7–12).
- Quantitative step: counts and percentages of figurative words, per genre and per corpus (Case Study A, p.3–4).
- Exploratory step: cross-genre visual comparison led to the finding that figurative density drops partway through Seder Avodah poems and rises again, then back to close reading (Case Study B, p.12–16).
- No machine learning, models or LLMs in the study.

## Evaluation
- No metrics, baselines or accuracy figures (the work is interpretive). Validation is by corroborating or refuting the earlier qualitative claims with counts (p.3–4).
- Note a methodological comment: the authors cite a call for validation of DH findings (Hammond) and propose cautious, annotation-based generalisation (p.16–17).

## Difficulties and error analysis
- What counts as figurative is a judgement call; annotator and time dependence (p.3 ¶7).
- Original flat tagset limited analysis; enlarging it later was "neither efficient, systematic nor clever" (p.2 ¶3).
- Mismatch between quantity and impression: the Hosha'not genre has high figurative density (25%) but sounds low in figurativeness; the dissertation's qualitative claim was wrong on this point (p.4 ¶10).
- Moving from annotation to classification and generalisation is hard; categories look rigid after annotation (p.5 ¶13–16; p.17 ¶43–45).
- Annotators tend to over-extend the tagset and want to tag everything (p.17 ¶44).
- No error analysis of an automatic method (none exists here).

## Limitations
Authors' own: ViS-À-ViS currently works only with CATMA (p.18 note 5); automated pattern detection is future work (p.16 ¶41); one corpus; they note tension between systematic annotation and speculative interpretation.
I notice:
- Single annotator origin, no agreement figures, and the annotation was deliberately not revised, so errors carry through.
- No automatic detection or LLM comparison, so the article gives no performance benchmark.
- Comparison corpora (Psalms, Pinchas) are described without sizes or annotation details.
- The final CATMA tagset is not given in the paper.
- The DHQ PDF is marked "Preview" 2023 in its header; check the final published version if citing page numbers.

## Reusable ideas for our paper
- Treat annotator disagreement as data: show multiple annotations side by side rather than forcing one gold label (p.11 ¶34). Supports a design where "challenging" cases are those with expert disagreement and where LLM output is compared to each annotator.
- Documented case that figurative-language annotation is subjective and unstable over time (same annotator, later date): cite as a reason to report agreement and to keep a "frozen gold" for TEST.
- Figurative density per genre/poem as a descriptive statistic for corpus characterisation.
- Closely related corpus type (poetry in a Semitic language, similes/metaphors/metonymy) and a Haifa-adjacent scholarly context for the Hebrew side.
- Note 8 mentions a DH2023 poster on training deep models to detect metaphors in this corpus ("FigureOut"); not a DHQ article, but a pointer to related work outside DHQ.

## Verbatim quotes (each under 15 words; PDF page, ¶)
- "the decision whether a word is figurative or not is a hermeneutical one" — p.3, ¶7
- "ViS-À-ViS advocates for the visualization of multiplicity" — p.11, ¶34
- "metadata becomes data, and interpretation becomes a rigid text" — p.17, ¶45
