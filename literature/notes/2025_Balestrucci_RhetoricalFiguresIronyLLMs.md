# Balestrucci, Oliverio, Lo, Anselma, Basile, Mazzei & Patti (2025) — When Figures Speak with Irony: Investigating the Role of Rhetorical Figures in Irony Generation with LLMs

CLiC-it 2025 (CEUR-WS vol. 4112), https://aclanthology.org/2025.clicit-1.7 — PDF: `literature/related_work/non_dhq/2025_Balestrucci_RhetoricalFiguresIronyLLMs.pdf`
Read: full paper including appendix. Page refs below are PDF pages. "Not reported" means I did not find it in the paper.

## Research question and task definition
- RQ1: To what extent can LLMs accurately classify rhetorical figures in ironic Italian texts? RQ2: Does fine-tuning LLMs on rhetorical figure classification lead to generation of more human-like ironic replies, in terms of rhetorical devices? (p.1–2).
- Task: classify Italian ironic tweets/replies into one of 8 rhetorical-figure categories (analogy, hyperbole, euphemism, rhetorical question, context shift, false assertion, oxymoron/paradox, other) drawn from Karoui et al. (2017)'s irony-pragmatics annotation scheme (p.3, Table 1).
- Domain: irony in social media Italian, not classical/literary rhetoric; figures are a *subset* used specifically to signal irony, not a general rhetorical taxonomy.

## Data
- TWITTIRÒ-UD: 1,424 ironic Italian tweets, 28,387 tokens, annotated with rhetorical figure (one of the 8) plus UD morphosyntax. Split: train 1,138 / dev 144 / test 142 tweets (p.2–3, Table 2).
- MultiPICo (Italian subset): 18,778 multilingual post-reply pairs (Reddit 8,956, Twitter 9,822), 506 annotators, 94,342 labels; Italian subset: 24 annotators, 4,790 annotations on 1,000 post-reply pairs (p.2–3). Ironic pairs selected via majority vote → 278 ironic post-reply pairs used for enrichment/generation experiments (p.5).

## Annotation scheme
- 8 categories (Table 1, p.3): Analogy (covers analogy, simile, *and metaphor* — all three collapsed into one label), Hyperbole, Euphemism, Rhetorical Question, Context Shift, False Assertion, Oxymoron/Paradox, Other. Scheme reproduced from Karoui et al. (2017), originally for French/English/Italian irony.
- For human validation (Section 6.1): two of the paper's authors (both computational-linguistics experts) annotated a 20-pair subset. Cohen's κ = 0.63, Krippendorff's α = 0.60 between the two human annotators — "substantial agreement," comparable to Karoui et al.'s own reported 0.60 (p.5).

## Method
- Fine-tuned 5 open-weight multilingual LLMs (Qwen2.5-7B, Llama-3.1-8B, Ministral-8B, LLaMAntino-3-8B, Minerva-7B) via LoRA, two strategies: plain instruction fine-tuning (FT) and chain-of-thought fine-tuning (CoT-FT) (p.3–4).
- Baselines: random classifier; zero-shot prompting with the best FT model's base (non-fine-tuned) version (p.4).
- Each model run 3 times per input, temperature 0.1; weighted P/R/F1 reported (p.4).
- Best model (Ministral-8B, CoT-FT) then used to auto-annotate the Italian MultiPICo ironic subset, validated by human spot-check, and finally used to *generate* ironic replies for comparison with human-written ones and with a non-fine-tuned baseline generator (p.5–7).

## Evaluation
- Classification (Table 3, p.4): weighted P/R/F1 across 3 runs, 8 models/configs.
  - FT: Qwen2.5-7B 0.346/0.359/0.350; Llama-3.1-8B 0.370/0.394/0.378; LLaMAntino-3-8B 0.373/0.399/0.379; Ministral-8B 0.371/0.371/0.366; Minerva-7B 0.382/0.399/0.388.
  - CoT-FT: Qwen2.5-7B 0.350/0.352/0.349; Llama-3.1-8B 0.378/0.406/0.384; LLaMAntino-3-8B 0.382/0.397/0.385; Ministral-8B (best) 0.393/0.408/**0.396**; Minerva-7B 0.367/0.385/0.372.
  - Baselines: Random P/R/F1 = 0.138/0.122/0.125; Zero-shot = 0.213/0.218/0.185.
- No raw TP/FP/FN counts given anywhere in the paper — only weighted P/R/F1 and a confusion matrix (Figure 2) for one run of the best model, which does give per-cell counts (e.g. Rhetorical Question 19/22 correct, Analogy 15/26, Euphemism 0/8 correct) (p.4–5).
- Human-vs-model agreement (Section 6.1, p.5): Krippendorff's α between the two human annotators and the model = 0.21 ("fair" agreement) on the 20-pair MultiPICo validation subset; on a second 20-generated-reply subset, human-model α = 0.26 (vs. human-human α = 0.65 on that same subset) (p.5–6).
- Generation comparison (Table 4, p.5; Table 5 linguistic analysis, p.7): distribution of rhetorical figures and stylistic markers (token count, TTR, interjections, negations) compared across human replies, CoT-FT-model replies, and non-fine-tuned baseline replies.

## Difficulties and error analysis
- Best model (Ministral-8B CoT-FT) performs well on well-represented figures (Rhetorical Question, Analogy) but made 0/8 correct predictions on Euphemism (p.4–5).
- On human-vs-model disagreement (11/20 mismatched pairs): model over-predicted Oxymoron/Paradox when humans chose Other/sarcasm in 6/11 cases; one case the model picked Analogy, apparently misled by the post's framing rather than the reply's actual pragmatic content (p.5–6, worked examples given).
- Minerva-7B (the most Italian-trained model) got *worse* with CoT fine-tuning, attributed to mixing Italian/English labels (e.g. outputting "EUFEMISMO" instead of "EUPHEMISM") (p.4).
- Non-fine-tuned baseline generator over-relies on Rhetorical Question and Other/humor as generic, less-targeted rhetorical strategies; baseline also massively over-uses negations (0.982 per reply vs. 0.072 for humans) (p.7).

## Limitations
Authors' own (p.8, Section 9):
- Relatively small training dataset (TWITTIRÒ-UD), hurting generalizability especially for under-represented categories (Euphemism, Hyperbole).
- Human evaluation on a small subset (20 pairs, then another 20) — reduces statistical robustness of agreement scores.
- No direct comparison against models explicitly fine-tuned for irony generation (as opposed to rhetorical-figure classification), so the paper cannot isolate whether rhetorical-figure awareness specifically (vs. other factors) drives the generation improvements.
I notice:
- The 8-category scheme is irony-specific, not a general rhetorical taxonomy; "Analogy" collapses simile, analogy, and metaphor into one bucket, which is a much coarser grain than this project's four-way distinction (antithesis/periphrasis/metaphor/metonymy subtypes).
- Weighted P/R/F1 only — no raw per-class TP/FP/FN table, unlike our project's reporting standard.
- F1 of best model (~0.40) is modest in absolute terms even though it clears the random (0.125) and zero-shot (0.185) baselines by a wide margin — classification of rhetorical figures from a closed label set is hard even with fine-tuning.

## Reusable ideas for our paper
- Precedent for reporting *both* a classification metric (weighted F1) *and* a separate human-vs-model agreement statistic (Krippendorff's α) rather than F1 alone, with the explicit point that human-human agreement (0.60–0.65) is itself well below 1.0 and substantially higher than human-model agreement (0.21–0.26) — useful comparison point for our own inter-annotator vs LLM-annotator agreement framing.
- The CoT fine-tuning condition's gain over plain fine-tuning, and the zero-shot vs fine-tuned baseline comparison, is a template for isolating the effect of explanation-before-label prompting, relevant to our Config C two-stage pipeline design.
- Confusion-matrix-level error analysis (which categories get confused with which, and worked bilingual examples of why) is a useful format for our own per-element error analysis sections.
- Caution: this paper's rhetorical-figure label set is irony-specific and much coarser than classical Arabic balagha categories — not directly transferable, but the "fair agreement, with systematic confusions traceable to specific figures" finding parallels difficulties we may see with Periphrasis/كناية.

## Verbatim quotes (each under 15 words; PDF page)
- "LLMs achieve fair agreement with annotators in rhetorical figure classification" — p.1 (abstract)
- "the model frequently labeled replies as OXYMORON PARADOX when annotators had chosen OTHER" — p.5
- "a notable increase in the use of RHETORICAL QUESTION and OTHER" — p.6
