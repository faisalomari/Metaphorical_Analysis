# Fuoli, Huang, Littlemore, Turner & Wilding (2025) — Metaphor Identification Using Large Language Models: A Comparison of RAG, Prompt Engineering, and Fine-Tuning

arXiv:2509.24866v2 [cs.CL], preprint (University of Birmingham / Coventry University) — PDF: `literature/related_work/non_dhq/2025_Fuoli_MetaphorIdentificationLLMs.pdf`
Read: full paper. Page refs below are PDF pages.

## Research question and task definition
- Can LLMs identify and annotate metaphorical expressions in *full texts* (not pre-selected single words in decontextualized sentences, which the authors argue is the norm in prior NLP work and has limited validity) (p.1–2, p.5)?
- Compares three LLM deployment strategies for this task: (i) RAG (model given the project's own annotation codebook as a retrieval resource), (ii) prompt engineering (zero-shot / few-shot / chain-of-thought), (iii) fine-tuning (p.1–2, p.6–8).
- Adopts a "phraseological" metaphor identification approach (meaning units at phrase level, not just single words), following Cameron's Vehicle Identification Procedure / MIV and the authors' own prior protocol (Fuoli et al. 2022) rather than strict MIP(VU) (p.2–4).

## Data
- Corpus: 94 IMDb film review texts, 2,828 sentences, 59,147 words, 2,599 hand-annotated metaphorical expressions (Table 1, p.6). Hand-annotated by two of the paper's authors in a prior study (Fuoli et al. 2022), average Cohen's κ = 0.85 (p.6).
- Fine-tuning split: 80% train / 20% held-out test, with a different random split for each of 5 experimental runs (p.7).
- Few-shot/CoT examples drawn from the corpus; original corpus ratio of conventional:creative metaphors ≈ 9:1, tested both with this original ratio and an artificially balanced (even) ratio in the example sets (p.7).

## Annotation scheme
- Metaphor defined as a tool comparing a "topic" to a "vehicle" to express an opinion, feeling, or aid understanding (p.2). Annotation unit = phrase-level "meaning unit" (not strictly single words): includes conventional idioms, hyphenated compounds, adjectival/adverbial entailments internally coherent with literal or metaphorical sense of a noun/verb, with explicit rules for when to split vs. merge adjacent metaphorical phrases (p.3–4, detailed rule list with worked examples, e.g. "sunken ship of a movie" vs. "negative baggage"). Distinguishes "conventional" vs. "creative" metaphors (ratio ~9:1 in corpus) (p.7).
- Not covered by MIP(VU) strictly — authors explicitly chose the more flexible phrase-based approach over MIP(VU) for better ecological validity, acknowledging this sacrifices some replicability (p.2–3).

## Method
- 10 LLMs tested: 3 Llama variants (3.1 8B, 3.2 3B, 3.2 1B), Deepseek R1 8B (open-source, reasoning), GPT-4.1 / 4.1-mini / 4.1-nano (closed, non-reasoning), o3 / o3-mini / o4-mini (closed, reasoning) (Table 3, p.8).
- RAG: full codebook (definitions + rules + examples) provided as context, model asked to tag metaphors per the codebook (p.6).
- Prompt engineering: zero-shot, few-shot (4 or 8 examples, "even" or "original" conventional:creative ratio), chain-of-thought few-shot with GPT-4o-generated explanations manually checked for accuracy (p.6–8, Table 2 full matrix of variants).
- Fine-tuning: on 80% of corpus; not performed for reasoning models (o-series) because reasoning models use multi-stage RL-based training incompatible with the standard supervised fine-tuning API (p.7–8).
- 5 experimental runs per method/variant; default temperature; output format = XML <Metaphor></Metaphor> tags over the whole text (p.6, p.9).
- Statistical testing: mixed-effects beta regression (glmmTMB in R) with method, model type (open/closed-source), and text length as fixed effects, random intercepts for model/text/run (p.9).

## Evaluation
- Metrics: token-level precision, recall, F1 against the hand-coded gold corpus (proportional credit for partial span overlap, not requiring exact span match) (p.9).
- Fine-tuning gave the highest accuracy overall; best model GPT-4.1 mini, median F1 = **0.79** (IQR 0.73–0.83) (p.9, Figure 1).
- Best prompt-engineering config: o3 + chain-of-thought, median F1 = 0.76 (IQR 0.72–0.80); o3 zero-shot alone already reached median F1 = 0.73 (IQR 0.69–0.77) (p.10).
- Best RAG config: o3, median F1 = 0.74 (IQR 0.69–0.78) (p.9).
- Regression results (p.9–10): vs. RAG, prompt engineering β=0.11 (p<.001, ΔF1=0.02) and fine-tuning β=0.43 (p<.001, ΔF1=0.10) both significantly better; fine-tuning > prompt engineering (β=0.33, p<.001, ΔF1=0.07). Closed-source >> open-source overall (β=0.84, p<.001, ΔF1=0.20). Longer texts → lower F1 (β=−0.10, p<.001, ΔF1=−0.02 per SD). Within prompting strategies: few-shot and CoT each significantly beat zero-shot, CoT beats few-shot too (all p<.001); more examples (4→8) gave a small additional gain (ΔF1=0.01); preserving the corpus's natural 9:1 conventional:creative ratio in examples slightly outperformed an artificially balanced ratio (ΔF1=0.01).
- No raw TP/FP/FN counts reported (token-level, with proportional partial-overlap credit) — precision/recall/F1 only.
- Human-LLM discrepancy analysis (fine-tuned GPT-4.1 mini output, 19 texts) coded into 8 categories of disagreement reason (Table 4, p.11): raw counts per category given for false negatives/false positives, e.g. Degree of conventionality 59 FN / 12 FP; Difficulties in perceiving source-target distinction 34 FN / 56 FP; Personification 30 FN / 7 FP; Phrase-level meaning 22 FN / 26 FP. Totals: 189 FN, 129 FP (26 further discrepancies had no assignable reason and were excluded).

## Difficulties and error analysis
- False negatives dominated by: (1) highly conventional metaphors with no literal alternative, especially TIME-related ("the very near future," "spent their life") (p.11); (2) personification ("the fury mother nature can unleash") (p.11); (3) explicit similes/comparisons the model may treat as categorically distinct from metaphor ("funny as a root canal") (p.12); (4) grammatical-class cues (noun vs. verb use of "approach"; passive-voice "bathed in") that signal metaphoricity but the model misses (p.12).
- Bidirectional discrepancies: difficulty locating the source-target boundary (grey-area cases, e.g. "join the list of ... bad movies" — is "list" literal or ironic-metaphorical?) (p.12); disagreement on whether metaphoricity sits at word or phrase level (e.g. model tags just "club" where humans tag "member of that undistinguished club" as one unit) (p.13); sub-word/decomposability cases like "eye-catching" (p.13); "twice-true" metaphors that are literally true in context too, e.g. "dark" describing a horror film (p.13).
- False positives' main driver: historically faded/dead metaphors where the model still flags a synchronically opaque idiom (e.g. "red herring") that humans no longer perceive as metaphorical because the source-target mapping has eroded (p.13).
- Authors explicitly connect these discrepancy categories to long-standing theoretical grey areas in metaphor scholarship (personification-vs-metaphor boundary, word-vs-phrase level, conventionality/semantic bleaching continuum) rather than treating them as simple model failures (p.13–14).

## Limitations
Authors' own: not an exhaustive explicit "Limitations" section, but acknowledged throughout — text length negatively affects F1 (longer texts harder); fine-tuning not tested on reasoning models; results from a single genre (film reviews) with possible genre/domain effects flagged as future work (p.9–10, p.14 Conclusion/future work). Authors note F1 and Cohen's/Krippendorff's agreement stats are "not directly comparable" when arguing LLM performance approaches human inter-coder reliability levels (reported MIP κ range 0.56–0.70, MIPVU 0.74–0.88) — flagged by the authors themselves as an imperfect comparison (p.14).
I notice:
- Single-domain, single-language (English film reviews) corpus — generalization to poetry/Arabic/classical registers untested here.
- "Gold standard" built by only 2 annotators (albeit with κ=0.85 reported for their original annotation); no third-party/independent replication of the gold labels in this paper.
- Partial-credit token-level scoring (not exact span match) is a looser criterion than strict span matching; this project's own standard of reporting both strict and token-overlap span scoring is a stricter, dual-criterion standard by comparison.

## Reusable ideas for our paper
- Closest methodological precedent in this set: full-text (not pre-selected word) identification, phraseological (span-based, not pure single-token) annotation unit, multiple LLM deployment strategies systematically compared (RAG vs. prompting vs. fine-tuning) with proper mixed-effects statistical testing rather than simple significance-free comparisons.
- The human-LLM discrepancy taxonomy (Table 4, 8 named categories with raw FN/FP counts) is a strong template for our own error-taxonomy sections — directly transferable structure (name the grey-area category, give a worked example, count FN vs FP separately).
- Useful citation for "LLM performance is in the ballpark of human inter-annotator reliability" argument, with the explicit caveat that F1 and kappa/alpha are not strictly comparable — a caution we should carry into any similar claim in our own writing.
- Explicit discussion of chain-of-thought and few-shot examples' example-ratio sensitivity (preserving natural class imbalance beats artificial balancing) is relevant if we tune Periphrasis/Antithesis example sets for our own prompts.
- Confirms (via its own lit review of Puraivan 2024, Tian 2024, Hicke & Kristensen-McLachlan 2024, Liang 2025) that word-level MIP-style LLM metaphor identification tends to score much lower (Liang et al. 2025: F1=30.4 at best) than this paper's full-text phraseological approach (F1=0.79) — a strong argument, citable in our own framing, that task operationalization (word-level vs. span-level) drives a large share of reported LLM performance variance across studies.

## Verbatim quotes (each under 15 words; PDF page)
- "fine-tuning yielding a median F1 score of 0.79" — p.1 (abstract)
- "most discrepancies are not random but reflect well-known grey areas" — p.14
- "LLMs fail to consistently apply false dichotomies renders them human-like" — p.14
