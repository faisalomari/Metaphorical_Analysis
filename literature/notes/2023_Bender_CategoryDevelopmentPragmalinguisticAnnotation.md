# Bender, Becker, Kiemes & Müller (2023) — Category Development at the Interface of Interpretive Pragmalinguistic Annotation and Machine Learning

DHQ 17(3), https://dhq.digitalhumanities.org/vol/17/3/000720/000720.html — PDF: `literature/related_work/dhq/2023_Bender_CategoryDevelopmentPragmalinguisticAnnotation.pdf`
Read: all main text (p.1–15); references (p.15–17) not read. Page refs are PDF pages; "¶" is DHQ's paragraph number. "Not reported" means not found.

## Research question and task definition
- Which design properties of an annotation category system (segment size, granularity, interpretation depth) make interpretive pragmalinguistic categories machine-learnable and reliably annotatable? (abstract; p.1–2 ¶1–7)
- Phenomenon: "discourse referencing" in German Bundestag speeches (sentences that refer back to earlier utterances or texts), including implicit cases that need context to interpret (p.2 ¶2–3).
- Task 1: sentence-level binary detection (discourse referencing yes/no). Task 2: classify the actor mention in discourse references into three classes (actor explicit / metonymic mention of actor / no actor) (p.9 ¶35–36).

## Data
- Source: plenary minutes of the German Bundestag, 1949–May 2021, ~810,000 texts, ~260 million tokens (Discourse Lab corpus) (p.5 ¶20).
- Experimental sample: random 6,000 sentences from 5–7 May 2021 transcripts, heckling excluded (p.5 ¶20). German, one session week, so no diachronic variation by design.
- Gold result: 1,935 of 6,000 sentences (32.25%) are discourse referencing (p.7 ¶28). Of those, 1,155 (59.69%) explicit actor, 721 (37.26%) no actor, 59 (3.05%) metonymic (p.8 ¶30).

## Annotation scheme
- Step 1 (sentence): discourse referencing yes/no. Step 2a (sentence): explicit / metonymic / none. Step 2b (phrase): extract the phrases that signal discourse referencing (noun phrases, verb phrases) (Table 1, p.7; Tables 2–3, p.8).
- Categories were developed collaboratively, deductively from theory then inductively on pilot data; no overlapping categories allowed; sentences shown in random order with minimal co-text (p.6 ¶21–23).
- Annotators: teams of two annotated 3,000 sentences each, independently (so all 6,000 were double annotated). Described as student annotators in the discussion (p.14 ¶65). Disagreements were decided by an independent annotator (p.7 ¶28).
- Agreement (Cohen's kappa, reported on a 0–100 scale): group 1 = 72.87 (88% raw agreement), group 2 = 57.44 (83.5%), average 65.02 for step 1; 84.35 for step 2a (p.7 ¶27–28; p.8 ¶30). Group 2's low value is blamed on a misunderstanding about the rare label.
- Kappa for step 2b phrase extraction: not reported.

## Method
- Models: Multinomial Naive Bayes (baseline, bag-of-words, 90/10 train/test split) and fine-tuned DistilBERT (70/15/15 train/validation/test; epochs 4; batch 16 for Task 1 and 4 for Task 2; learning rate 5e-5) (p.9–10 ¶39–44).
- Task 2 input variants: sentence, phrase only, sentence plus phrase; and three label settings: A (3 classes), B (metonymy dropped), C (explicit and metonymic merged) (p.9 ¶36).
- They state that initial experiments with several models found BERT best (p.10 ¶42); those other models are not described.
- No LLM prompting (GPT mentioned only as an example of pre-trained models).

## Evaluation
- Metrics: micro precision, recall, F1 on the test set (p.10 ¶45). Majority baselines are given in the text: 64.48% for "no discourse referencing" (Task 1) and 59.69% for "actor explicitly mentioned" (Task 2).
- Task 1 F1: Naive Bayes 80.30; DistilBERT 93.16 (Table 5, p.10).
- Task 2 F1, Setting A: Naive Bayes 78.81 (sentence), 80.34 (phrase), 81.45 (sentence+phrase); DistilBERT 92.41, 96.90, 95.98 (Table 6, p.11). Setting B: DistilBERT up to 98.47; Setting C: up to 97.82 (Tables 7–8, p.11–12).
- Sizes of the test sets and number of runs or seeds: not reported. No significance tests or confidence intervals. The text refers to "Table 3" for Setting A results where Table 6 is meant (p.11 ¶47).
- Naive Bayes and DistilBERT were evaluated on different split proportions, so the comparison is not on identical test data (my observation).

## Difficulties and error analysis
- Implicit discourse referencing needs contextual knowledge (example "With your behavior ... improper proximity", p.2 ¶2); form-function relation varies a lot, so expert, procedural knowledge is needed (p.14 ¶65).
- Surprising result: the lowest inter-annotator agreement was for the least granular, "simplest" binary distinction, because sentence-level binary judgments still need full contextual and domain knowledge (p.14 ¶64–65).
- DistilBERT Task 1 errors: 37 false positives and 29 false negatives; FPs often involve a named actor without a referencing function; FNs showed no visible pattern (p.12 ¶53–55).
- Task 2 error types: (1) actor vs metonymy confusion (metonymy is only 3.05% of data); (2) predicting an actor when none (named entities, pronouns in the sentence); (3) metonymy recognised only when given the extracted phrase (p.13 ¶57–60).
- Rare, harder class (metonymy) hurts Naive Bayes most; merging classes (Setting C) shows the model struggles with it (p.12 ¶50).

## Limitations
Authors' own: results are on pilot corpora and one phenomenon; they believe findings generalise but have not shown it (p.15 ¶68). The authors note phrase-level input requires manual selection of the relevant phrase (p.15 ¶67).
I notice:
- Very high F1 (93–98) with unreported test-set sizes and a tiny metonymy class (59 gold instances in total), so metonymy results are fragile.
- Phrase-input results use phrases extracted by the annotators who already know the gold label, so they are not a realistic end-to-end detection setting (the model is told where the phenomenon is).
- The authors read high F1 as evidence of category robustness and annotation quality (p.14 ¶61), but the lowest kappa (65 average, 57 in one group) points the other way for Task 1; this tension is only partly discussed.
- Models trained on one week of one parliament; no out-of-domain test.
- Kappa values presented on a 0–100 scale rather than 0–1, which can confuse comparison with other papers.

## Reusable ideas for our paper
- Three quality criteria for a tagset: segmentation (annotation unit), granularity, and interpretation depth. Maps directly onto our design choices (verse vs hemistich vs span; element vs subtype; how much poetic and cultural context the annotator or model sees).
- Evidence that agreement can be lowest for the "simple" coarse decision: supports treating exists/not-exists labels with caution and scoring spans (consistent with our span-level rule).
- Their Task 2 shows a rare, metonymy-like, context-dependent class is both the hardest for models and under-represented; relevant to our rare element types (e.g. periphrasis) and to interpreting small-n results.
- Error taxonomy example: confusion between neighbouring categories, over-reliance on surface cues (named actors), recognition only when a span is hinted. Reusable for an LLM error taxonomy.
- Reporting practice: majority baseline, a classical baseline (Naive Bayes), kappa per annotator group. Suggests including a trivial baseline and per-poem or per-annotator agreement.
- Expert-vs-student annotator point: procedural expert knowledge cannot be fully written into guidelines (p.14 ¶65); supports using expert adjudication for the gold standard.

## Verbatim quotes (each under 15 words; PDF page, ¶)
- "procedural expert knowledge, as it were, is required" — p.14, ¶65
- "The lowest inter-annotator agreement value was obtained for +/- discourse referencing" — p.14, ¶64
- "more precise operationalization of the phenomenon under investigation" — p.15, ¶68
