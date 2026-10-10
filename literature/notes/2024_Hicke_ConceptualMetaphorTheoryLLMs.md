# Hicke & Kristensen-McLachlan (2024) — SCIENCE IS EXPLORATION: Computational Frontiers for Conceptual Metaphor Theory

CHR 2024 (Computational Humanities Research Conference), arXiv:2410.08991v1 [cs.CL] — PDF: `literature/related_work/non_dhq/2024_Hicke_ConceptualMetaphorTheoryLLMs.pdf`
Read: full paper. Page refs below are PDF pages.

## Research question and task definition
- Can LLMs accurately identify and explain the presence of conceptual metaphors (Lakoff & Johnson's CMT — systematic structuring of one experiential domain in the language of another, e.g. LIFE IS A JOURNEY) in natural language data? (Abstract, p.1).
- Operationalizes the Metaphor Identification Procedure (MIP, Pragglejaz Group 2007), specifically Step 3b ("does this word have a more basic contemporary meaning in other contexts"), as an LLM prompt, since steps 1–3a already have rough analogues in transformer attention/tokenization/contextual embeddings (p.3–5, Figure 1).
- Framed as: if LLMs can replicate MIP (a procedure designed for human annotators), this is evidence of a non-trivial capacity for analogical/cultural reasoning not obviously explained by next-token pretraining (p.2).

## Data
- Two datasets: (1) TroFi (Trope Finder) — 3,736 human-labeled sentences (literal/non-literal) from Wall Street Journal 1987–89, each containing one of 50 target words (p.5). (2) MWLB — a new dataset the authors built: 544 sentences hand-pulled from Lakoff & Johnson's *Metaphors We Live By* that are metaphorical without needing context; a 100-sentence subset was manually, qualitatively annotated by the authors for fine-grained analysis (p.5–6). Dataset and model outputs made public on GitHub.

## Annotation scheme
- Not a human-annotation study in the traditional inter-annotator sense. For TroFi, ground truth = pre-existing literal/non-literal labels. For the MWLB qualitative subset (100 sentences), the two authors scored each model output on 5 binary categories: (1) all Lakoff & Johnson (L&J) metaphors correctly identified; (2) correct/plausible basic meanings given for those; (3) additional (non-L&J) words also labeled; (4) additional labels plausibly metaphorical; (5) additional labels given correct/plausible basic meanings (p.6). Confusing cases discussed to consensus between the two authors — explicitly stated as subjective, not claimed as ground truth (p.6–7).
- No formal inter-annotator agreement statistic (e.g. kappa) reported — not reported.

## Method
- Prompt (Figure 2, p.4): adapted almost verbatim from MIP Step 3b, asking the model to mark, word-by-word, whether each word in a sentence has a more basic (concrete/bodily/precise/older) meaning than its contextual use, with two in-context examples and a requirement to output a parenthetical part-of-speech + basic-meaning gloss per word (format reportedly suggested by gpt-4o itself during pilot exploration, then baked into the prompt as a forced-explanation / CoT-like device).
- Models: gpt-3.5-turbo-0125, gpt-4-turbo-2024-04-09, gpt-4o-2024-05-13, via OpenAI Chat Completion API; system prompt "You are a helpful assistant. You have extensive linguistic knowledge."; top_p = 0.1 (other params default) (p.5).
- Total API cost for all experiments: ~$100 (p.5).

## Evaluation
- TroFi (Table 1, p.6 and confusion matrices Figure 3, p.7): precision/recall for Metaphorical and Literal classes separately.
  - 3.5-turbo: Metaphorical P 58.30 / R 97.90; Literal P 66.42 / R 5.59.
  - 4-turbo: Metaphorical P 74.80 / R 86.90; Literal P 77.41 / R 60.53.
  - 4o: Metaphorical P 73.40 / R 93.66; Literal P 83.69 / R 54.24.
  - Confusion-matrix raw counts given (p.7): e.g. 3.5-turbo: true-metaphorical/predicted-metaphorical 2100, true-metaphorical/predicted-literal 45, true-literal/predicted-metaphorical 89, true-literal/predicted-literal 1502 (so recall for Literal is very low: 1502/(1502+89) ≈ 94%... note the paper's own reported Literal recall of 5.59 for 3.5-turbo does not arithmetically match this confusion matrix as I read it — row/column orientation in Figure 3's caption ("rows = true values, columns = model labels") should be checked against Table 1 directly if reusing these numbers; I flag this as a possible inconsistency I could not fully resolve from the text alone).
  - MWLB qualitative subset (Figure 4, p.8): % of 100 sentences where model found ALL L&J metaphors: 4-turbo 62%, 3.5-turbo 63%, 4o 74%; % where it additionally gave correct basic meanings for all of them: 4-turbo 57%, 3.5-turbo 52%, 4o 65%.
  - Additional (non-L&J) annotations (Figure 5, p.9): % of sentences with extra words labeled: 4-turbo 34%, 3.5-turbo 45%, 4o 54%; of those, % plausibly metaphorical: 4-turbo 91%, 3.5-turbo 89%, 4o 85%; % with correct basic meanings: 4-turbo 65%, 3.5-turbo 40%, 4o 48%.
- No F1 computed for the MWLB subset (not reported) — only the percentage-correct breakdowns above.

## Difficulties and error analysis
- All three models over-label words as metaphorical on TroFi: high recall for "metaphorical," low recall for "literal" — 3.5-turbo struggles most with literal word usage (p.6–7).
- Function words (especially prepositions like "in") are missed as metaphorical, weakening detection of so-called container metaphors (e.g. "in the center of my field of vision" — LIFE/VISUAL FIELDS ARE CONTAINERS); all three models miss "in" in the given example (p.8).
- Entity-type metaphors (personification, PLACE FOR INSTITUTION, PRODUCER FOR PRODUCT) are easier for GPT-4-family models than for 3.5-turbo; worked examples given for "Vietnam" and "Heidegger" being correctly reinterpreted metaphorically by 4-turbo/4o (p.8). All three models still miss "the Alamo" as metaphorical in "Remember the Alamo!" (p.8–9).
- Word-by-word annotation format struggles with multi-word metaphorical units (e.g. "get the most out of life") and compound words (e.g. "underage," "brainchild") — 3.5-turbo gives an incoherent gloss for "brainchild" ("a child conceived in the mind") while 4-turbo correctly decomposes "brain" and "child" into their separate basic/concrete meanings (p.9).
- 3.5-turbo also struggled with following the output format itself (truncating sentences, inconsistent list formatting, dropping parenthetical explanations), which directly hurt its measured accuracy (p.8).

## Limitations
Authors' own: future work flagged as needed includes probing where metaphoricity/basic-meaning information is stored in the models, extending to open-source models, and operationalizing other linguistic procedures beyond MIP (p.9–10).
I notice:
- MWLB annotations are explicitly subjective (by the paper's own authors, not independent raters), with no inter-annotator agreement statistic reported, and are also used to generate the very ground truth the models are scored against — a circularity the authors themselves flag ("we do not claim these represent a ground truth," p.6).
- No held-out train/dev/test discipline — this is a zero-shot evaluation study, not an iteratively tuned one.
- The TroFi confusion-matrix numbers in Figure 3 and the Table 1 precision/recall figures are hard to reconcile by direct arithmetic from the text as I read it; flagging as unresolved rather than silently repeating possibly-mismatched numbers.
- Word-level-only operationalization (inherited from MIP) structurally cannot handle multi-word metaphors — acknowledged by the authors as a source of error, not fixed in this paper.

## Reusable ideas for our paper
- Direct precedent for "operationalize an existing human annotation procedure (MIP) as an LLM prompt and test fidelity to the procedure" — closely analogous to what this project could do with classical balagha definitions as prompt material.
- The explicit entity-type/personification/container-metaphor difficulty taxonomy (container metaphors and function-word metaphors are hard; entity-renaming metaphors like place-for-institution are comparatively easy for larger models) is a reusable difficulty axis to compare against our own per-element difficulty findings (e.g. is Periphrasis/كناية similarly a "function-word-adjacent" hard case, or closer to the entity-renaming easy case?).
- Good methodological caution: flag when annotator judgments used as ground truth are themselves informal/non-independent, and say so explicitly rather than presenting them as objective — matches this project's own standing discipline around reporting raw counts and avoiding overclaiming from small/subjective samples.
- Cited directly by Fuoli et al. 2025 (another paper in our non-DHQ set) as a word-level precedent this project's phraseological approach improves on — useful for situating our own span-level (not plain word-level) scoring choice in the literature.

## Verbatim quotes (each under 15 words; PDF page)
- "displaying a surprising depth of linguistic knowledge" — p.1 (abstract)
- "basic meanings are not necessarily the most frequent meanings of the lexical unit" — p.3, Figure 1
- "the models are prone to over-labeling words as metaphorical" — p.7
