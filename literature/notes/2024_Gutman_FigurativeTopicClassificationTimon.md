# Gutman (2024) — A Network Analysis of Figurative Topic Classification: The Case Study of Timon of Athens

DHQ 18(3), https://dhq.digitalhumanities.org/vol/18/3/000753/000753.html — PDF: `literature/related_work/dhq/2024_Gutman_FigurativeTopicClassificationTimon.pdf`
Read: all methodology, results tables and conclusions (p.1–8, 12–14); the long literary interpretation of the play (p.9–12) was read less closely, since it carries little methodological content. Page refs are PDF pages; "¶" is DHQ's paragraph number. "Not reported" means not found in the paper.

## Research question and task definition
- How can figurative language be analysed computationally as a network of interacting conceptual domains, and does that help literary interpretation? (abstract; p.1 ¶1–3)
- Task actually automated: assign each word of a (manually extracted) figurative instance to one of 103 topics (p.3 ¶20). The topics then become nodes in a co-occurrence network (an edge = two topics co-occurring in the same figurative instance, p.3 ¶22).
- Task NOT automated: finding the figurative instances. The author says there is "no escape" from extracting them manually (p.3 ¶16).
- The interpretive aim is to read *Timon of Athens* (and compare Timon's phases and other characters) through the network, and to test existing critical interpretations (p.1 ¶2; p.5–13).

## Data
- Training data for the classifier: four tragedies from c.1605–1610: Macbeth, A Yorkshire Tragedy, The Rape of Lucrece (Heywood), The Bloody Banquet (p.3 ¶16). A footnote mentions five plays in total, so the "four tragedies" wording and the footnote count differ slightly (p.14, note 9–10). Early modern English, modern spelling editions used (p.3 ¶20; note 14).
- 1,388 manually extracted figurative instances: 146 (Yorkshire Tragedy), 482 (Macbeth), 415 (Rape of Lucrece), 345 (Bloody Banquet) (p.3 ¶17).
- Case study text: Timon of Athens, 546 figurative instances, 4,715 topic interactions (p.4–5 ¶27–28).
- Timon-specific counts of words inside figurative instances by act (Table 6, p.8).
- Source editions listed in notes (Middleton 2016, Shakespeare 2015, EEBO for Lucrece with manual spelling standardisation).

## Annotation scheme
- 103 topics, built bottom-up from the instances, not fixed in advance (e.g. nature, politics, economy, sexuality; full list in the appendix, p.13–14) (p.3 ¶17).
- Each instance can carry several topics (Table 1 shows up to five per instance, p.3 ¶18).
- Who annotated: the author alone (implied by "the original ones made by the creator of the dataset", p.3 ¶20). Inter-annotator agreement: not reported; footnote 12 says it "will be implemented in a future study" (p.14).
- The author acknowledges the topic set is partly subjective and other classifications are possible (p.3 ¶19).
- No scheme for figure types (metaphor vs simile vs metonymy): the unit is a "figurative instance", mostly discussed as metaphor.

## Method
- Pre-processing: stop words and character names removed (p.3 ¶20).
- Classifier: a neural network combined with DistilBERT, trained on contemporary-spelling editions (p.3 ¶20).
- Network analysis in Gephi: undirected, weighted graph; degree, weighted degree, betweenness and eigenvector centrality; cluster detection; ForceAtlas2 layout (p.3–5 ¶21–28).
- Interpretive step: compare centralities between characters and between Acts 1–2 and 3–5, then connect to criticism (p.5–13).
- It is not stated clearly in the paper whether the Timon network used classifier output or manual labels. I could not resolve this from the text.

## Evaluation
- Classifier accuracy 72.94% and F-score 71.12 on a held-out part of the random split (training 66%, test 33%) (p.3 ¶20; note 15, p.14). Number of test instances, number of runs, per-topic scores, and how the F-score is averaged: not reported.
- Baselines: not reported (no comparison to topic modelling, other models or a majority-class baseline). Gutman discusses LDA qualitatively with cited studies (p.2 ¶11–13).
- Interpretive evaluation, not metric-based: whether the network corroborates or challenges existing readings (p.5–13).
- Detection of figurative language itself is not evaluated (done by hand).

## Difficulties and error analysis
- Figurative language is harder than literal for topic modelling: topics are incoherent, no single dominant topic per text, a word in poetry often refers to other topics (quotes from Navarro-Colorado and Rhody, p.2 ¶12–13).
- A figurative sentence can contain several distinct metaphors, so sentence-level processing does not work (p.3 ¶16).
- Boundary question: which words in an instance are figurative, e.g. "great" in "great revenge" (p.2 ¶9).
- Subjectivity in topic inventory and in assigning topics (p.3 ¶19).
- Directed networks (tenor to vehicle) would be hard when the tenor is only implied (p.12 ¶51).
- No classifier error analysis reported (no confusion matrix, no examples of wrong topics).

## Limitations
Authors' own: accuracy can be improved by fine-tuning, fewer topics and more data; IAA to be done later; manual extraction; one case study; suggest trying other LLMs such as Llama, Gemini, ChatGPT (p.12–13 ¶51).
I notice:
- Single annotator for both extraction and topic labelling, no agreement, no external gold standard.
- 103 topics on 1,388 instances is a sparse label space, so 72.94% accuracy hides likely poor performance on rare topics (not shown).
- Network results rest on topic labels whose reliability is unknown; centrality differences are interpreted without any uncertainty estimate.
- Unclear whether Timon labels were predicted or manual.
- Classification is of topics (domains), not of rhetorical figures, so it does not test figure identification.

## Reusable ideas for our paper
- Clear statement that figurative language is harder than literal for NLP and that identification of instances was still manual in 2024: our paper tests precisely whether an LLM can replace that manual step.
- Operationalisation language (Moretti): turning a literary concept into measurable operations. Useful for defining each rhetorical element as an annotation task.
- Design lesson: make the annotation unit explicit (instance vs sentence vs word); Gutman's note that sentence-level processing fails for multiple metaphors per sentence is relevant to span-level scoring.
- Interpretive evaluation as a complement to F1 (do the outputs support or challenge existing readings?). Could inform a qualitative error review with an expert.
- Warning about subjectivity of label inventory supports reporting annotator agreement and allowing multiple valid labels.
- The paper itself suggests LLMs as the next step, which supports the gap argument (but DHQ-published, not tested).

## Verbatim quotes (each under 15 words; PDF page, ¶)
- "there is no escape from extracting the figurative instances manually" — p.3, ¶16
- "The topic classifier currently achieves a promising result of 72.94% accuracy" — p.3, ¶20
- "experimenting with other large language models, such as Llama, Gemini or ChatGPT" — p.13, ¶51
