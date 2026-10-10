# Kühn, Mitrović & Granitzer (2024) — Computational Approaches to the Detection of Lesser-Known Rhetorical Figures: A Systematic Survey and Research Challenges

arXiv:2406.16674 [cs.CL], preprint, submitted to ACM Computing Surveys. https://arxiv.org/abs/2406.16674 — PDF: `literature/related_work/non_dhq/2024_Kuhn_LesserKnownRhetoricalFiguresSurvey.pdf`
Read: full paper (35 pages: linguistic background, computational perspective, per-figure detection survey across 4.1–4.17, challenges section, conclusion, references). Page refs below are PDF pages. "Not reported" means not found in the paper.

## Task / scope
- A comprehensive systematic survey (not an empirical study) of computational detection approaches for **26 lesser-known rhetorical figures** (alliteration, figures of perfect lexical repetition [ploke, anadiplosis, anaphora, epiphora, symploke, epanalepsis, epizeuxis, diacope, conduplicatio], antimetabole/chiasmus, antithesis, dysphemism/euphemism, hyperbole, litotes, meiosis, metonymy, oxymoron, parallelism/isocolon, polyptoton, polysyndeton, rhetorical question, zeugma), drawn from 39 papers covering 86 distinct detection approaches, published 1991–2024 (mostly 2006–2024) (p.1, p.27–28).
- Explicitly excludes metaphor, irony, and sarcasm (pointed to existing surveys instead: Shutova 2010, Rai & Chakraverty 2020, Ge et al. 2023 for metaphor; Wallace 2015 for irony; Joshi et al. 2017 for sarcasm) (p.2, p.19).
- Explicitly does **not** cover computational *interpretation* of figures (only detection), citing lack of research in that area (p.2).
- Search method: manual Google Scholar search by figure name + "detection"/"identification", deliberately not restricted to ACL Anthology, extended to smaller conferences given limited big-venue coverage of the topic (p.5).

## Structure and per-figure content
For each of the 26 figures the survey reports: textual definition + example, related figures, rhetorical effect, domain of frequent use, available datasets, and a synthesis of detection approaches with a results table (P/R/F1 where available) (p.6 methodology note). This project's relevant-to-us figures:

### Antithesis (Section 4.4, p.14–15)
- Definition: antonyms in two often-syntactically-parallel phrases/sentences; syntactic parallelism required by some rhetoricians (Fahnestock 2002) but not others (Silva Rhetoricae, McGuigan 2011) — same definitional inconsistency problem flagged in the companion FigLang paper.
- Datasets: Zhu et al. 2022 Chinese ConFiguRe corpus (~250 antitheses); Green & Crotts 2020 extracted 120 antitheses from Dubremetz & Nivre's antimetabole corpus (not public); **Kühn et al. 2023/2024 built German antithesis datasets from Telegram chats of a COVID-19-skeptic journalist** (own prior work).
- Detection approaches and F1 (Table 4, p.16): Lawrence et al. 2017 (rule-based, antonyms via WordNet only, no parallelism check, no metrics reported) → Green & Crotts 2020 (rule-based, WordNet+ConceptNet antonym list, P 41.10/R 38.40/F1 39.70) → Zhu et al. 2022 (model-based E2ESeq/E2ECRF, P/R/F1 ≈31.10/31.10/30.99, aggregated across all 12 figures they study, not antithesis-specific) → **Kühn et al. 2023 (rule-based, German, spaCy POS-tag parallelism + Wiktionary-derived antonym list, P 57.00/R 45.24/F1 50.44)** → **Kühn et al. 2024 (rule-&-model-based, replaces antonym list with GELECTRA language model while keeping rule-based parallelism detection, P 83.16/R 54.02/F1 65.11, best result in the table)**.
- Domain: Green 2021 found antithesis juxtaposing contrasting views in environmental policy articles; Kühn et al. 2024 hypothesize antithesis is more frequent in populist rhetoric.

### Metonymy (Section 4.11, p.20–22)
- Definition: substituting one word/phrase for a closely associated one via contiguity (e.g., "reading Goethe" for his literature, "Washington said..." for the US government).
- Detection mostly specializes in location- or organization-based metonymy (not general literary metonymy). Best reported result: Wang et al. 2023, entity-aware BERT + ACGN, F1 95.8% on the RELOCAR dataset (Table 9, p.22) — but this is for geographic/institutional metonymy resolution in English/Chinese news-style text, not for classical-poetry metonymy (مجاز مرسل).
- Datasets: SemEval-2007 Task 8, RELOCAR, WIMCOR (Wikipedia location-based), a German metonymy dataset (Zarcone & Rüd 2012), Zhu et al. 2022's Chinese ConFiguRe (603 metonymy instances).
- No treatment of metonymy as a classical-rhetoric/balagha category; purely modern NLP (news, Wikipedia) context.

### Methodology-level findings (Section 5, "Current Challenges," p.28–30) — overlaps substantially with the companion FigLang 2024 paper (same authors, same underlying review), but with additional figures and a year-by-year trend chart
- 86 approaches across 39 papers: 68.97% rule-based, 27.59% model-based, 1.15% combined, 2.30% unknown (Table 16, p.29) — identical percentages to the companion paper (same underlying count).
- Language distribution: English 69.81%, German 9.43%, Russian 8.16%, French 7.55%, Latin 7.55%, Chinese 3.06%, Czech 2.83%, Japanese 0.94% (Table 17, p.29).
- Trend chart (Fig. 2, p.28) shows model-based approaches catching up to rule-based from ~2020 onward, but rule-based still dominant overall.
- Same ten-ish challenges as the companion paper, condensed into prose: lack of/imbalanced data, deceptive accuracy on imbalanced data, boundary definition, inconsistent definitions/spellings (same antithesis-parallelism example), non-binary ranking need, unused rhetorical ontologies (RhetFig, Serbian Retfig, English Ploke ontology, German GRhOOT), English-language dominance and its translation-loss problem, and explicit framing that **current approaches "cannot be solved by identifying shallow and obvious patterns"** given the complexity of the task (citing Zhu et al. 2022 again).

## Datasets found across the whole survey (general pattern, not Arabic-specific)
- No Arabic-language rhetorical-figure dataset or detection approach appears anywhere in the 39 papers / 86 approaches reviewed. Languages covered: English, German, Russian, French, Latin, Chinese, Czech, Japanese (Table 17, p.29) — Arabic is absent.
- No periphrasis/كناية-equivalent figure (nor any configuration resembling it) appears among the 26 surveyed figures.

## I notice
- This survey and its companion FigLang 2024 short paper are by largely the same author team and cover overlapping ground (same 68.97%/27.59% rule-vs-model split, same English-dominance statistic) — when citing both, be careful not to double-count or present them as fully independent confirmations of the same numbers; cite the survey as the primary/detailed source and the FigLang paper as the condensed companion.
- Kühn et al.'s own antithesis-detection work (2023, 2024) is both a *cited prior work* in this survey and *authored by the same people who wrote the survey* — self-citation, worth noting but not disqualifying (common DHQ-adjacent practice per our own `comparison_table.md` notes on self-citation in Bender/Rebora/Gutman).
- No periphrasis/كناية anywhere in this survey, and no Arabic rhetorical figures at all — this paper supports only the general "under-studied rhetorical figures beyond metaphor/irony are hard and under-resourced" claim, not any Arabic-specific or periphrasis-specific claim.
- The antithesis detection numbers (best F1 65.11% on a German populist-Telegram corpus) are a useful non-Arabic comparison point for how automated antithesis detection performs when it *does* get attempted with modern NLP methods, contrasted with Abd Alhadi et al. 2023's rule-based Arabic antithesis results.

## Reusable ideas for our paper
- The antithesis detection progression table (Lawrence et al. 2017 → Green & Crotts 2020 → Zhu et al. 2022 → Kühn et al. 2023 → Kühn et al. 2024) is a ready-made "state of the art for antithesis detection outside Arabic" citation chain, useful context for positioning our own antithesis results.
- The explicit absence of Arabic and of periphrasis/كناية from a 26-figure, 39-paper, cross-language survey is itself citable evidence (an absence-based argument) supporting the novelty claim that no comparable rhetorical-figure detection literature exists for classical Arabic balagha categories — strengthens, rather than narrows, the novelty_gap.md claim.
- The "model-based approaches are rising but still behind rule-based in raw approach count" trend (Fig. 2) is a useful one-line fact for framing why an LLM-based approach to periphrasis/antithesis/metaphor is still a timely, non-redundant contribution.

## Verbatim quotes (each under 15 words, with page)
- "a complex task such as the detection of rhetorical figures cannot be solved by" — p.28 (quoting Zhu et al. 2022)
- "none of the investigated approaches seemed to use those helpful resources" — p.30 (re rhetorical-figure ontologies)
- "the NLP community is dominated by approaches and tools for the English language" — p.29
