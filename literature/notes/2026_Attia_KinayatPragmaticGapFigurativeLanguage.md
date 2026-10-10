# Attia, Muhamed, Alkhamissi, Solorio & Diab (2026) — Beyond Understanding: Evaluating the Pragmatic Gap in LLMs' Cultural Processing of Figurative Language

EACL 2026 (19th Conf. of the European Chapter of the ACL), Main Conference, pp. 7238–7265. https://aclanthology.org/2026.eacl-long.341/ — PDF: `literature/related_work/non_dhq/2026_Attia_KinayatPragmaticGapFigurativeLanguage.pdf`
Read: full paper (main text, appendices with prompts, data, error analysis). Page refs below are PDF pages. "Not reported" means not found in the paper.

## Research question / task
- Evaluates LLMs' ability to process culturally grounded figurative language (idioms, proverbs) along three axes: contextual understanding (MCQ), pragmatic use (using an idiom correctly in context), and connotation inference — not just "can the model explain the idiom" (p.1, p.7238).
- Central contribution: **Kinayat**, a new dataset of 325 Egyptian Arabic colloquial idioms with MSA explanations, extracted from the 1949 book *Al-Kinayat Al-'Amiyya* (Pasha, 1949) (p.2, p.5). Also uses existing Jawaher (20-dialect Arabic proverbs, 198 test items) and MAPS (English proverbs, 394 items) datasets.
- Note on terminology: "Kinayat" here is simply the dataset's name, borrowed from the Arabic word كناية (kinaya/periphrasis, literally "allusive/indirect expression," used here in its broader colloquial sense of "idiom/allusion") — the paper is about Egyptian colloquial **idioms and proverbs**, not about كناية as a classical balagha rhetorical category. Do not conflate this with our periphrasis/كناية element.

## Data
- Kinayat: 325 Egyptian Arabic idioms + MSA explanations (10 entries excluded during cleaning) (p.5).
- Jawaher (Magdy et al. 2025): 198 test proverbs across 20 Arabic dialects (p.5).
- MAPS (Liu et al. 2024): 394 English proverbs (p.5).
- Pragmatic-use subset: 150 of the 325 Kinayat idioms (the more familiar ones), used for the pragmatic-use, understanding, and contextual-understanding comparison (p.5, p.10).

## Annotation / human involvement
- No classical annotation scheme with IAA on a rhetorical-element taxonomy — instead: (1) a native Egyptian Arabic speaker reviews/edits GPT-4.1-generated example sentences (51.3% modified) (p.3); (2) a native Arabic speaker scores 50+50 generated incorrect MCQ distractors on a 0–2 plausibility scale (avg. 1.72 idioms, 1.68 proverbs) (p.4); (3) three native Egyptian Arabic speakers label connotation (positive/negative/neutral) per idiom/proverb — only items with 100% 3-way agreement are used for model evaluation (69.3% of idioms, 53.03% of proverbs reached full agreement) (p.5); (4) human evaluation of 220 generated explanations (10 per model × 22 models) to validate an LLM-as-a-judge scorer, finding 62.27% exact agreement, human score lower than LLM-judge in 29.09% of cases (p.6).
- No Krippendorff's alpha or Cohen's kappa reported anywhere — agreement is reported only as raw percentage of 100%-agreement items, or as exact-match percentage between human and LLM-judge scores.

## Method
- 22 LLMs: open multilingual (Llama-3.1 8B/70B, Gemma-2 9B/27B, Qwen2.5 7B/14B/32B, Aya-Expanse 8B/32B, Mistral-7B), open Arabic-specific (Jais 6.7B/13B, ALLaM-7B, SILMA-9B, Fanar-1-9B, AceGPT-v2-8B), and closed-source (GPT-4o, GPT-4o-mini, Gemini 1.5 Flash, Gemini 2.5 Flash Lite, Claude 3.5 Sonnet, Claude Sonnet 4) (p.5).
- Tasks (all zero-shot, single run per experiment, English-language prompts for consistency) (p.3–5): MCQ Understanding (2-choice, correct vs. GPT-4.1-generated incorrect explanation, both a "general" and an SRL-based distractor variant), Contextual Understanding MCQ (idiom + usage sentence), Negation MCQ (pick the incorrect explanation), Explanation Generation (scored by BERTScore-F1 and LLM-as-a-judge, cross-validated by GPT-4.1/Claude-3.5 judges to avoid self-preference bias), Proverb Completion (predict masked final word), Connotation Labeling (positive/negative/neutral, on 100%-agreement items only), and the paper's own new **Pragmatic Use task**: given a sentence with a blanked-out idiom, pick the correct idiom from two options (150-idiom subset) (p.3–4).
- Evaluation framework: lm-eval harness with vLLM for open models; log-likelihood scoring for open models, generated-output parsing for closed APIs (p.5).

## Evaluation / reported results
- Headline "Pragmatics Gap": average accuracy on Pragmatic Use (64.45%) is 14.07 points lower than average accuracy on plain Understanding (78.52%) for the same 150 idioms; adding the idiom's usage sentence as context raises Understanding to 89.18% (+10.66 pts) (Table 3, p.8; abstract p.7238).
- MCQ Understanding difficulty hierarchy (Fig. 2, p.6): MAPS+Context 95.66% > MAPS 90.86% > Jawaher 86.57% > Kinayat (idioms) 76.29% — Arabic lower than English, idioms lower than proverbs within Arabic.
- Connotation: best model (Claude-3.5-Sonnet) reaches at most 85.58% agreement with humans on idioms where human inter-annotator agreement was already 100% (p.8, abstract).
- Proverb completion: huge English/Arabic gap (75.43% vs. 10.65% average accuracy), attributed to lower Arabic-proverb representation in training data (p.6–7).
- Raw TP/FP/FN: **not reported anywhere** — all results are accuracy/weighted-metric percentages with standard error, no confusion-matrix counts except the per-idiom "number of models that failed" counts in the error-analysis appendix (Tables 20–22, p.27).
- Model-size correlation: weak-to-moderate positive correlation between parameter count (6.7B–32B, open models only) and accuracy; strongest for Pragmatic Use (R²=0.600, p=0.0007) (p.9, Appendix E).

## Difficulties / error analysis
- Dissociation between comprehension and pragmatic use: models that correctly identify idiom meaning in MCQ often fail to use the same idiom correctly in context — error patterns for the two tasks differ markedly (Section 6.1, p.9).
- Negation inversion (pick the *incorrect* answer) drops accuracy further (idioms: 76.29%→70.97%; proverbs: 86.57%→82.71%) (p.6).
- Dialectal breakdown (Jawaher): UAE/MSA/Libya/Oman score highest, Sudan/Mauritania/Qatar/Yemen lowest; high-resource Egyptian dialect scores only mid-range — attributed to culturally-shared vs. highly localized proverbs (p.7–8).
- Connotation harder to judge from the bare idiom/proverb than from its explanation (idioms: 50.10% vs. 72.21% average accuracy from explanations) (p.8, Table 12).

## Limitations (authors' own, p.10)
- Egyptian idioms only (one dialect, albeit high-resource); source book from 1949, so some idioms may be dated (mitigated by using a "more familiar" 150-item subset for pragmatic testing).
- Scope limited to idioms and proverbs — explicitly excludes metaphor, simile, hyperbole, irony, sarcasm, and "other culturally specific figures of speech," naming this as future work.
- Connotation labeling has inherent subjectivity; authors cite perspectivist/anthropological critiques (Bender et al. 2021, Aroyo & Welty 2015) of forcing a single "objective" gold standard in annotation — directly relevant to how we frame disagreement on our own four elements.
- Single evaluation run per experiment (zero-shot) — no 2-run-majority or multi-run robustness check, unlike this project's own discipline.

## I notice
- No raw TP/FP/FN anywhere; evaluation is purely accuracy/weighted-metric on closed-choice or scored-generation tasks, not span-level identification — methodologically quite different from this project's span-level P/R/F1 scoring.
- "Kinayat" as a dataset name should not be confused with كناية/periphrasis as a rhetorical category in our taxonomy — risk of a false-friend citation if not flagged clearly in our writing.
- No classical/named rhetorical-figure taxonomy at all (no antithesis, metaphor, metonymy, periphrasis labels) — this is cultural/pragmatic figurative-language competence (idioms, proverbs), not classical balagha rhetorical-element identification. The gap this paper fills (LLM cultural/pragmatic competence on Arabic figurative language) is adjacent to, not identical with, our gap (LLM identification of named classical rhetorical elements in classical poetry).
- 22-model multi-model design and the "accuracy drops even for frontier models relative to 100%-agreement human baseline" finding are the two most citable facts for our novelty framing.

## Reusable ideas for our paper
- The three-tier task design (understanding → contextual understanding → pragmatic use) as a template for stratifying difficulty beyond a single flat identification task.
- Using "accuracy on items where human annotators reached 100% agreement" as a clean way to report human-model gap without being confounded by human disagreement — could be a useful framing device for our own difficulty-stratified evaluation, though our actual scoring remains span-level P/R/F1 per project discipline.
- Explicit methodology for validating an LLM-as-a-judge against human spot-checks (220-sample validation set) — relevant if any part of our Phase 2+ pipeline uses LLM-based scoring.

## Verbatim quotes (each under 15 words, with page)
- "models often interpret figurative meaning, they face challenges in using it appropriately" — p.1 (abstract)
- "achieving at most 85.58% agreement with humans on samples with 100% inter-annotator agreement" — p.1 (abstract)
- "figurative language serves as an effective diagnostic for cultural reasoning" — p.1 (abstract)
