# Abd Alhadi, Hussein & Kuflik (2023) — Automatic Identification of Rhetorical Elements in classical Arabic Poetry

DHQ 17(2), https://dhq.digitalhumanities.org/vol/17/2/000673/000673.html — PDF: `literature/related_work/dhq/2023_AbdAlhadi_RhetoricalElementsArabicPoetry.pdf`
Read: all main text and the appendix definitions; the appendix tables (p.15–17) came out scrambled in text extraction, so I did not rely on them; references not read. Page refs below are PDF pages; "¶" is DHQ's own paragraph number printed in the margin. "Not reported" means I did not find it in the paper.

## Research question and task definition
- Can the identification of rhetorical elements (balagha) in classical Arabic poetry be automated? Task: given a poem and a chosen element, mark which verses/words realise it (PDF p.4–5, GUI description, ¶32–33).
- Scope: 20 element groups chosen from ~180 in the classical inventory (Cachia 1998), because manual analysis found them to be the main recurrent elements in pre-Islamic to early Abbasid poetry (p.1 ¶7; p.3 ¶26).
- Framed as an interim, rule-based solution until enough annotated data exist to train ML classifiers (abstract; p.1 ¶10; p.11 ¶56).
- Motivation: manual annotation is slow and needs expert knowledge; only 75 of 26,925 poems analysed by hand at that point (p.1 ¶4).
- Claims to be "the first" study of automatic identification of rhetorical elements in classical Arabic poetry (p.2 ¶22).

## Data
- Full repository (REI project): 26,925 poems by 675 poets, pre-Islamic to Mamluk (to early 16th c.), entered manually from printed editions by students; access restricted (p.1 ¶7; p.3 ¶29).
- Study set: 75 poems, 35 poets, avg. ~27 verses, Khalilian meters only; two periods: Abbasid (8th–10th c.) and pre-Abbasid (6th–8th c.). The text gives 48 poems vs 29 poems and 887 vs 752 verses (p.4 ¶30). The paper's wording on which period has more poems is confusing (I could not reconcile it).
- Split: 77% training (58 poems) / 23% test (17 poems) (p.8 ¶38; Appendix 2 table totals p.15). Rules were developed only on the training set.
- For elements absent from the 75 poems, a second set of example verses was built from other sources (p.8 ¶39).
- Language: classical Arabic, diacritised where available; some of the 75 poems lack diacritics (p.10 ¶54).
- Appendix 3 (counts of each element in train/test) exists but the PDF text extraction is scrambled; I did not rely on it.

## Annotation scheme
- 20 element groups, listed with Arabic names and definitions (p.2–3 ¶25; Appendix 1, p.11–14). Includes simile (tashbih), four "repetition" families with sub-elements (repetition, ploce, perfect paronomasia; extraction, semblance, free paronomasia; rhyme-echo; key words), flowing, afterthought/retraction, catchword, alliteration (2 types), hemming, unraveling, counterchange, repartee, homoeoteleuton (4 sub-types), verbal congruence, paronomasia (7 sub-types), negative and positive antithesis (tibaq), and the Satirist's and Encomiast's feints.
- Not covered: metaphor, periphrasis (kinaya), exaggeration and some paronomasia types, explicitly left to future work because they depend on semantics (p.11 ¶59).
- Who annotated: "an Arabic literature researcher" (p.8 ¶38). Inter-annotator agreement: not reported. Number of annotators beyond that: not reported.
- Definitions come mainly from Cachia 1998 (a bilingual dictionary of Arabic rhetoric) (p.11 Appendix 1 note).

## Method
- Rule-based pipeline in Java: string matching, morphological analysis (AlKhalil2 for prefix, stem, type, root), a polarity-based Arabic sentiment analyser built from ArSenL plus a self-built lexicon (8,765 positive, 9,813 negative words), and a self-built lexicon of 453 antonym pairs (p.4 ¶31 items 1–7).
- Elements are detected by rule families: simple string/position tests (catchword, hemming, flowing, repartee), morphology-based tests (simile tokens and ka- prefix, repetition after excluding particle types, unraveling via dual forms, paronomasia), lexicon-based tests (positive antithesis), and sentiment-based tests (feints) (p.7–8 ¶36 rules list).
- Output shown in a colour-coded GUI by verse (p.5).
- No ML, embeddings or LLMs used.

## Evaluation
- Metrics: precision, recall, F1, per element on the held-out test set (p.9 ¶40).
- Baselines: none reported (no comparison to another system or to a naive baseline).
- Overall: precision 0.918, recall 0.902, F 0.906 (p.9 ¶45). Note: the abstract says "F-measure of 0.902", which is the recall figure; the body gives F = 0.906. The "Average" row looks like a per-element mean (my reading).
- Per element (Table 2, p.9): Simile P 0.916 / R 0.891 / F1 0.904; Repetition1 F1 0.896; Repetition2 0.913; Repetition3 0.941; Paronomasia 0.800; Verbal congruence 0.824; Negative antithesis 0.777; Positive antithesis 0.500; Feints 0.750; many positional elements = 1.0 (some with very few instances, e.g. Flowing TP=3).
- Table 3 (p.10) gives TP/FP/FN. Simile 33/3/4. For Positive Antithesis it prints 13/16/19, but Table 2's precision (0.551) and recall (0.457) only work out with TP=16, FP=13, FN=19, so two columns look swapped. For the feints it prints 9/4/2, but Table 2 (P 0.818, R 0.692) implies FP=2 and FN=4. Treat Table 3 with care.
- AlKhalil2 itself: 74.2% of 1,333 words analysed correctly on 8 poems (p.9, Table 1).

## Difficulties and error analysis
- Context-free elements (string/position based) are near perfect; the authors explain this: identifying them needs no understanding of meaning (p.10 ¶48).
- Hard ones: positive antithesis (lexicon too small), the two feints (word polarity depends on context; lexicons taken from informal sources such as Twitter; poets boast of negative traits as positive, e.g. "his sword drips blood"; ambiguous words) (p.10 ¶52), paronomasia, verbal congruence.
- Simile: AlKhalil2 segments words in several ways, so a ka- prefix may be a word-internal letter (example: kawa'ib, "girls", wrongly readable as simile) and context is needed (p.10 ¶50).
- Negative antithesis: words intervening between the negation and the repeated word break the rule (example verse from Al-Najashi, p.10 ¶51).
- Repetition1 has high false negatives (p.10 ¶51).
- Authors state error analysis was done per element but its detail is left "for future study" (p.10 ¶49).
- Implicit similes (without a token) are excluded by design (p.7 ¶36, item 1).
- Diacritics help; without them results are poorer (p.10 ¶53).

## Limitations
Authors' own (p.10–11 ¶53–56):
- Only 75 of 26,925 poems; some undiacritised; AlKhalil2 is built for modern Arabic and misses parts of words; rule-based approach needs expert maintenance and only covers cases anticipated by the rules.
I notice:
- Test set is small (17 poems); elements with a handful of instances give 1.0 scores that are not stable.
- Single annotator, no agreement figure; test annotation and rule development were done within the same project.
- The abstract/body F-score mismatch and the Table 3 inconsistencies above.
- No baseline, no confidence intervals, no statistical test.
- Metaphor and periphrasis, the elements that most need semantics, are not evaluated at all.
- Error analysis is described but not shown.

## Reusable ideas for our paper
- This is the key DHQ comparator: same domain (classical Arabic poetry, Haifa group), same notion of "elements", and it explicitly says semantics-dependent elements (metaphor, periphrasis) were out of reach for rules. Our LLM study can be framed as testing exactly those.
- Their results give a difficulty ordering we can compare to: surface-marked elements easy; antithesis, feints, paronomasia, implicit similes hard.
- Per-element P/R/F1 reporting with raw TP/FP/FN (their Table 2/3 format) matches our project rule of reporting raw counts; their table errors are a reason to publish counts and compute metrics by script.
- Train/test discipline: they developed rules on 77% and tested on 23%; our DEV/TEST split mirrors this.
- Difficulty taxonomy hints: context-free vs context-dependent; token-marked vs unmarked (their simile rule); lexical-resource-dependent; polarity-dependent; ambiguity of segmentation. Could feed a "marker explicitness" taxonomy.
- Idea to test: do LLMs recover the cases the rules miss (unmarked simile, positive antithesis without a lexicon entry) and where do they over-trigger.

## Verbatim quotes (each under 15 words; PDF page, ¶)
- "a hard, if not impossible, mission" — p.1, ¶3
- "had widely differing success rates for different elements" — p.2, ¶11
- "the system does not need to understand the meaning of the verse" — p.10, ¶48
