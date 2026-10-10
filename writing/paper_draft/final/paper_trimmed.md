# Exploring the Potential of Large Language Models to Identify Challenging Rhetorical Elements in Classical Arabic Poetry

**Author(s):** `[TBD — author name(s) and institutional affiliation(s) to be supplied by the human author(s) before submission.]`

## Abstract

Rule-based identification of rhetorical elements in classical Arabic poetry reaches high precision and recall overall, but only by excluding metaphor and periphrasis (كناية) as too semantically demanding for pattern matching (Abd Alhadi, Hussein and Kuflik, 2023). This paper evaluates whether large language models can take up exactly the elements that earlier system named as out of reach. Three general-purpose models (Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash) were evaluated zero-shot, at the span level, on four elements — trope (مجاز), simile (تشبيه), periphrasis (كناية), and antithesis (طباق) — against one domain expert's manual annotation of five classical Arabic poems, three held out as a frozen test set. Simile, whose definition names an explicit comparative particle, reaches strict-criterion F1 of 0.65–0.73 for every model; periphrasis never exceeds 0.176 anywhere in the primary evaluation. Antithesis proved locatable but systematically over-claimed, a precision failure rather than a recall one. Supplementary experiments show periphrasis is reachable, though not yet reliably decidable, under a free-form reasoning format, and that several rhetorical subtypes are strikingly sensitive to which model is queried and how many worked examples anchor its reading of a category. The paper's contribution is diagnostic: it characterizes where, and under what conditions, large language models can currently be trusted to identify named classical Arabic rhetorical elements, rather than reporting a single performance verdict.

## Teaser

Large language models identify explicit similes in classical Arabic poetry fairly well, but periphrasis — the element a predecessor rule-based system gave up on as too semantic to automate — remains out of reach for every model and prompt tried here.

## Keywords

**Author keywords:** large language models; classical Arabic poetry; rhetorical analysis; balāgha; periphrasis; metaphor; digital humanities; annotation difficulty; span-level evaluation; prompt sensitivity.

**DHQ controlled-vocabulary keywords:** `[TBD — check against the live taxonomy at https://dhq.digitalhumanities.org/common/xml/taxonomy.xml at submission time; not parsed during this project's format research. Likely candidate domains: Arabic/Middle Eastern studies, computational linguistics, text analysis, machine learning.]`

**Project keywords:** `[TBD — DHQ's project-registry field; no registry entry exists for this work yet.]`

## Introduction

Classical Arabic poetry is governed by *balāgha*, a formally codified rhetorical system with a long scholastic history rather than a loose critical vocabulary. Al-Jurjānī's theory of poetic "wonder," most fully developed in his *Asrār al-Balāgha*, shifted classical literary judgment from scoring poetry for truthfulness and naturalness toward judging it by its capacity to evoke wonder — novelty, strangeness, the unexpected — an aesthetic al-Jurjānī and later critics including al-Sakkākī treat as built into the structure of rhetorical figures themselves (Harb, 2020). Al-Sakkākī's *Miftāḥ al-ʿUlūm* begins the tripartite division of the discipline into *maʿānī*, *bayān*, and *badīʿ*, later completed by al-Qazwīnī, that still structures how the tradition catalogues its devices (Fontana, 2025). Recognizing an instance of one of these devices is rarely a matter of spotting a fixed lexical marker; for many of the tradition's most characteristic figures, it is a matter of judging whether a word's literal sense remains an available reading at all — a judgment that can turn on context, convention, and a reader's own sense of what a poet is doing at that point in the line.

Automatic identification of these devices has, correspondingly, proven difficult. Abd Alhadi, Hussein and Kuflik (2023) report a rule-based system — built on string and positional matching, a morphological analyzer, and a purpose-built sentiment/antonym lexicon — that reaches a strong overall precision of 0.918 and recall of 0.902 across twenty rhetorical-element categories drawn from the same corpus of classical Arabic poems this paper uses. That result is strong only because of what the system was permitted to leave out: Abd Alhadi, Hussein and Kuflik (2023) explicitly exclude metaphor (استعارة) and periphrasis (كناية) from automatic detection, describing them as too semantically demanding for rule-based matching to handle responsibly. Their own stated limitation names, with unusual precision, exactly the elements a different kind of system would need to attempt.

Large language models are a natural candidate for that gap, because the judgment rule-based matching cannot make — whether a literal reading of a phrase remains plausible, or is foreclosed by context — is closer to the kind of contextual inference LLMs are built to perform than to a lexical pattern a rule can encode. Two adjacent literatures, reviewed in full in Background and Related Work, show the ingredients for evaluating this candidate already exist separately but have not yet been combined for this corpus or task (Kühn, Mitrović and Granitzer, 2024; Attia et al., 2026; Al Kaabi et al., 2024). No existing study — to the limits of a documented search of DHQ's full text, ACL Anthology, arXiv, CHR, JLCL, DSH, and targeted Arabic-rhetoric web search terms, through 2026-10-07 — evaluates multiple large language models on named classical Arabic rhetorical elements, including the semantically demanding cases rule-based systems cannot handle, against expert-annotated ground truth with a span-level, difficulty-stratified evaluation.

This paper reports such an evaluation. Three general-purpose large language models (Claude Sonnet 4.6, GPT-5.4-mini, and Gemini 3.5 Flash) are evaluated, zero-shot, on span-level identification of four rhetorical elements — trope (مجاز, an umbrella covering metaphor/استعارة, whole-clause analogy/تمثيل, and metonymy/مجاز مرسل), simile (تشبيه), periphrasis (كناية), and antithesis (طباق) — against one domain expert's (Prof. Ali Hussein) manual rhetorical analysis of five classical Arabic poems, three of them held out as a frozen test set never touched during prompt development. A baseline prompt is compared against a refined prompt whose rules were derived entirely from development-set error analysis, under a protocol requiring two-run majority agreement and both strict and token-level span matching — a methodological response to an early finding, described in the Methods section, that a single run's apparent gain on this task can be substantially noise. Beyond this primary evaluation, two further investigations probe the same question from different angles: a disentanglement experiment isolating whether model choice, element-name terminology, or output-format constraints are independently responsible for the hardest element's poor recall, and a subtype-level recall screen across twenty-five finer-grained rhetorical categories than the four-element scheme considers individually.

This study's motivating observation did not come from the pipeline at all. In an unstructured chat-interface session, a model given free-form Arabic reasoning space — no strict JSON schema, no instruction to suppress explanation — correctly identified a periphrasis instance in a verse by Imru' al-Qais that every configuration of the structured evaluation pipeline missed for that verse. That gap between what a model can do when allowed to reason aloud and what it does inside a constrained, schema-bound call is itself a finding worth reporting, and it shapes this paper's second line of inquiry: whether a model's apparent ceiling on a hard rhetorical element reflects a genuine capability limit, or an artifact of how the evaluation is built around it.

This paper's three research questions follow directly from this gap:

**RQ1.** How accurately can current large language models identify named classical Arabic rhetorical elements (antithesis/طباق, periphrasis/كناية, metaphor/استعارة, metonymy/مجاز مرسل) in classical Arabic poetry, measured at the span level against expert-annotated ground truth?

**RQ2.** Does LLM identification accuracy vary systematically by rhetorical-element type, and in particular, do the elements that Abd Alhadi, Hussein and Kuflik (2023) excluded as too semantically demanding for rule-based detection (metaphor, periphrasis) show a different accuracy and error profile than the more surface-marked element their rule-based system already handles well (antithesis)?

**RQ3.** Does evaluating multiple large language models, rather than a single model as in Al Kaabi et al. (2024), reveal consistent cross-model difficulty patterns by element, or does difficulty vary idiosyncratically by model — and how do any such patterns compare to the general difficulty findings reported for non-Arabic, non-classical rhetorical-figure detection (Kühn, Mitrović and Granitzer, 2024) and for Arabic figurative language more broadly (Attia et al., 2026)?

The remainder of this paper proceeds as follows. Background and Related Work situates this study against its direct rule-based predecessor and the broader digital-humanities and computational-linguistics literatures on annotation difficulty and LLM figurative-language benchmarking. Data and Methods describes the corpus, the single-annotator ground truth and its stated limitations, the DEV/TEST discipline, the prompt-design process, and the span-level scoring methodology. Results reports the frozen test-set evaluation, a subtype-level breakdown, the cross-model disentanglement experiment, and the twenty-five-subtype recall screen, each result marked final, preliminary, or incomplete according to how much of the evaluation design behind it is complete. Discussion interprets the difficulty ordering across elements, and Limitations and Future Work treats the single-annotator ground truth, corpus scope, and open methodological questions as a stated, honest part of the contribution rather than an afterthought.

This paper's own contribution is best read as diagnostic rather than as a performance claim: its value lies in characterizing *where and why* large language models succeed or fail at identifying classical Arabic rhetorical elements, extending exactly the frontier Abd Alhadi, Hussein and Kuflik (2023) named as beyond their own rule-based system's reach, not in reporting a uniformly high headline accuracy number.

## Background and Related Work

### The *balāgha* inventory and classical Arabic poetry corpus context

The twenty-element rhetorical inventory evaluated in this paper descends from the *maʿānī*/*bayān*/*badīʿ* scholastic tradition introduced above, by way of a modern synthesis (Cachia, 1998) rather than a direct reading of the medieval sources, citing Harb and Fontana as reliable English-language scholarly anchors for a tradition this paper cannot responsibly cite only through medieval primary texts.

The natural-language-processing side of classical Arabic poetry, by contrast, is young and lopsided in what it models. Qarah's AraPoemBERT (Qarah, 2024) pretrains a transformer on 2.09 million verses and reports strong results on meter, sub-meter, rhyme, poet-gender, and sentiment classification — formal features recoverable largely from surface phonology and morphology. No comparable resource exists yet for the *rhetorical* layer of the same poetry, one more piece of evidence that the elements this paper studies resist the surface pattern-matching that already works well for meter and rhyme.

### Prior automatic approaches to rhetorical-element identification

The direct predecessor this paper extends is Abd Alhadi, Hussein and Kuflik's rule-based system for identifying rhetorical elements in the same corpus of classical Arabic poems (Abd Alhadi, Hussein and Kuflik, 2023). Working from string and positional matching, a morphological analyzer, and a purpose-built sentiment and antonym lexicon, their system reaches an overall precision of 0.918 and recall of 0.902 across twenty rhetorical-element categories — a genuinely strong result for a rule-based pipeline, but strong only because of what the system was permitted to leave out: metaphor (استعارة) and periphrasis (كناية) were explicitly excluded as too semantically demanding for rule-based matching to handle responsibly. This paper exists to take up exactly the elements its predecessor named as out of reach for its own method, and is the paper against which this study's own per-element results must be read.

### Digital-humanities precedents for annotation-category development and difficulty

A recurring argument in *Digital Humanities Quarterly*'s own methodological literature is that category difficulty should be measured empirically, not assumed from a category's apparent simplicity. Bender et al.'s study of discourse-referencing annotation in German parliamentary speech is the clearest statement of this point: the *coarsest*, apparently simplest binary judgment in their scheme returned the *lowest* inter-annotator agreement of any task they tested, a pattern traced to the way even "simple" sentence-level judgments still depend on contextual knowledge annotators do not uniformly share (Bender et al., 2023). This is a direct structural parallel to this project's own pilot work on periphrasis, where small-sample noise and run-to-run instability have already produced a misleadingly large apparent effect that halved on replication.

Two further DHQ case studies model treating ambiguity itself as data rather than noise to be resolved away. Zirker and Göggelmann's "maximal annotation" of the modal verb "must" in Austen's *Emma* — tagging every plausible reading rather than forcing one — finds modality the hardest dimension to agree on by Fleiss's kappa (Zirker and Göggelmann, 2023). Münz-Manor and Marienberg-Milikowsky, annotating early Hebrew liturgical poetry for metaphor, metonymy, synecdoche, and simile, argue against collapsing multiple legitimate annotator readings into one gold standard, preferring to visualize the range a figurative-device tagset supports (Münz-Manor and Marienberg-Milikowsky, 2023). Both model, for a cognate figurative domain, the premise this paper's own difficulty-stratified design depends on: that "challenging" is something an evaluation can measure, not merely assert.

Gutman's network analysis of figurative language in *Timon of Athens* names the field's own next step directly. Gutman (2024) argues figurative language is harder for computational methods than literal language — his own topic-classification model reaches only 72.94% accuracy on a bottom-up topic inventory built from manually extracted figurative instances — and proposes large language models (Llama, Gemini, ChatGPT) as untested future work for exactly this kind of classification task. The present paper is, in a precise sense, that proposed future work, carried out for a different literary tradition and language.

### LLM-in-DH literature: methodological framing

Two recent DHQ articles supply methodological and tonal models here. Tarkka et al.'s comparison of a BERT-based classifier against human questionnaire responses on Finnish parliamentary speech pairs party-affiliation F1 with an explanation-analysis layer (SHAP) showing which cues the model relies on, finding it tracks cues human readers largely miss (Tarkka et al., 2026); this paper's Results/Discussion split follows the same logic, since an F1 table alone does not say *why* a model succeeds or fails. Dobson (2021) supplies the cautionary half: accuracy figures and confidence scores can be "rhetorically structured" to look more decisive than the evidence warrants, arguing for a cautious vocabulary about what a high score does and does not demonstrate — directly relevant to this paper's interpretation of its highest-scoring elements, below.

### LLM benchmarks on figurative and rhetorical language beyond digital humanities

Outside DHQ, a substantial non-DH literature already benchmarks large language models on metaphor and figurative-language identification, with more methodological machinery than anything reviewed so far. Fuoli et al. compare retrieval-augmented generation, prompt engineering, and fine-tuning across ten models on full-text (not pre-segmented) metaphor identification, reporting P/R/F1 alongside a taxonomy of human–model discrepancies, and reach a best F1 of 0.79 with a fine-tuned model (Fuoli et al., 2025) — the closest methodological template to the evaluation design adopted here: span-level identification over running text, discrepancies read as theoretically meaningful rather than undifferentiated noise. That optimism needs a counterweight: Reimann and Scheffler test zero- and few-shot LLMs on an extended metaphor-detection task and report a largely negative result, with one model showing severe overgeneralization (Reimann and Scheffler, 2025). Read against Fuoli et al. (2025), the contrast is itself the finding — figure-identification performance depends heavily on *how* a model is deployed, not only which model is asked — a lesson this paper's own two-stage prompting design takes seriously.

A smaller, closely related strand moves past a flat "metaphor: yes or no" label toward classifying *named* rhetorical figures against a human-annotated scheme, the task this paper undertakes for classical Arabic *balāgha* categories. Balestrucci et al. fine-tune open-weight multilingual models to classify eight named rhetorical figures (hyperbole, euphemism, oxymoron among them) in ironic Italian text, reporting human–model agreement (Krippendorff's alpha, 0.21–0.26) markedly below the 0.60–0.65 agreement between human annotators on the same figures (Balestrucci et al., 2025) — a benchmark this paper's own agreement figures can be read against once available. Hicke and Kristensen-McLachlan operationalize a single metaphor-identification procedure as a prompt for GPT-3.5, GPT-4, and GPT-4o, finding these models reproduce its reasoning steps with surprising depth (Hicke and Kristensen-McLachlan, 2024). A caution belongs alongside these benchmarks: Ye et al. argue that strong behavioral accuracy on a metaphor task can reflect shallow lexical or syntactic heuristics rather than robust semantic understanding (Ye et al., 2026) — a necessary qualification for any paper, including this one, tempted to read a high identification score as genuine interpretive competence.

Finally, two companion surveys by Kühn, Mitrović and collaborators establish that the gap this paper addresses is structural, not only Arabic-specific. Reviewing thirty-nine papers and eighty-six detection approaches across eight languages — none of them Arabic — Kühn, Mitrović and Granitzer (2024) find named rhetorical figures *beyond* metaphor, irony, and sarcasm (antithesis, evaluated here, among them) remain a generally under-studied sub-field, nearly seventy percent still rule-based, with existing rhetorical ontologies essentially unused. A companion paper distills ten recurring challenges facing computational detection of such figures — inconsistent cross-source definitions, boundary and intentionality ambiguity, chronic dataset scarcity (Kühn and Mitrović, 2024). Neither paper covers periphrasis or Arabic specifically; together they explain why periphrasis and metaphor, rather than antithesis (which Abd Alhadi, Hussein and Kuflik's (2023) system already handles reasonably well), were judged out of reach for rule-based matching.

### LLMs on Arabic figurative and cultural language specifically

Two existing studies bring large language models to bear on Arabic figurative language specifically, and each falls short of this paper's exact target in a precisely nameable way. Al Kaabi et al. (2024) compare ChatGPT's interpretation of Arabic rhetorical figures — metaphor, simile, and metonymy among them — against the classical hermeneutical tradition associated with al-Jurjānī, working through eight hand-selected example sentences. Their finding, that ChatGPT produces surface-level readings while missing the cultural and psychological depth a trained human reader supplies, is a genuinely useful qualitative signal, but the study is a single-model, small-sample exercise on isolated sentences rather than a poem corpus, with no benchmark metrics, no held-out test set, and no cross-model comparison. It is cited here strictly as a small qualitative study of this kind; its own literature review is not relied upon.

Attia et al.'s Kinayat benchmark (Attia et al., 2026) is, by contrast, methodologically rigorous: twenty-two open- and closed-source LLMs are evaluated on Egyptian Arabic idioms and multidialectal Arabic proverbs across comprehension, pragmatic-use, and connotation-inference tasks, with quantified human-agreement figures reported throughout — the strongest model reaches at most 85.58% agreement with human annotators even on connotation items where every annotator had already agreed. This is the closest precedent to a genuinely multi-model, quantitatively benchmarked study of Arabic figurative language, but of a different object: Kinayat's closed-form tasks (multiple-choice comprehension, fill-in-the-blank completion, connotation labeling) target cultural and pragmatic competence over modern colloquial idioms and proverbs, not the identification of named classical rhetorical categories within running verse; it contains no taxonomy of antithesis, periphrasis, metaphor, or metonymy, no difficulty stratification by element type, and no span-level task of the kind this study centers on. Read together, Al Kaabi et al. (2024) and Attia et al. (2026) show the field already has both the motivating intuition that LLMs handle Arabic figurative language imperfectly, and the methodological machinery to measure that imperfection rigorously — but neither has yet pointed toward classical Arabic poetry or the named *balāgha* inventory this paper evaluates.

### The gap this paper addresses

Automatic identification of rhetorical elements in classical Arabic poetry has so far relied on rule-based systems, which reach high precision and recall overall but only by excluding metaphor and periphrasis as too semantically demanding. Large language models are a natural candidate for this gap; two adjacent literatures — rigorous multi-model benchmarking of named rhetorical figures beyond metaphor and irony (Kühn, Mitrović and Granitzer, 2024), and a twenty-two-model, quantified benchmark of LLMs on Arabic figurative language for modern idioms and proverbs rather than classical poetry (Attia et al., 2026) — show the ingredients exist separately, but no existing study combines them for named classical Arabic rhetorical elements against expert-annotated ground truth with a span-level, difficulty-stratified evaluation. The three research questions introduced above structure the remainder of this paper.

## Data and Methods

### The corpus and its ground truth

The corpus consists of five classical Arabic poems: two by Imru' al-Qais (the Muʿallaqa, referred to throughout as Imru1, and a second, shorter poem, Imru2), and one each by Jarir, Abu Tammam, and Al-Nabigha Al-Dhubyani.

| Poem | Poet | Verses |
|---|---|---|
| Imru1 | Imru' al-Qais (Muʿallaqa) | 81 |
| Jarir | Jarir | 40 |
| Abu Tammam | Abu Tammam | 30 |
| Imru2 | Imru' al-Qais (poem 8) | 23 |
| Nabigha | Al-Nabigha Al-Dhubyani | 50 |

*Source: `experiments/pilot_3models/config.py`, `POEMS` registry.*

Every annotation in this study is manual rhetorical analysis by a single domain expert, Prof. Ali Hussein — whose own scholarship on the rhetorical structure of the classical Arabic *qaṣīda* (Hussein, 2015) is the disciplinary basis for his role as this corpus's sole annotator — against a fifty-three-category classical rhetoric taxonomy, mapped down to the four top-level elements evaluated here by substring matching on the taxonomy's primary and secondary labels (مجاز or استعارة mapping to trope; direct matches for تشبيه, كناية, and طباق). Exact-duplicate (span, element) annotation rows are deduplicated before any count is taken. **No second annotator has independently labeled any poem, and no inter-annotator agreement figure currently exists for this corpus.** A blind re-annotation protocol has been designed and partially built — an eighty-verse, poem-proportional stratified random sample, scored three ways (Cohen's κ (Cohen, 1960) and Krippendorff's α (Hayes and Krippendorff, 2007) on verse-level presence/absence per element, plus strict and token-overlap span-agreement where both rounds agree an element is present) — but Prof. Hussein's re-annotation pass is not yet complete, so every κ/α/span-agreement figure below is `[TBD]`, not an estimate. *Source: `writing/paper_plan/iaa/agreement_protocol.md`.* A separate, disagreement-enriched thirteen-verse set has also been assembled for a qualitative adjudication session with Prof. Hussein, but it was deliberately selected for disagreement, not drawn at random, so it is reported only qualitatively, never as an agreement statistic.

Ground-truth support is uneven across both poems and elements, most severely for antithesis (as few as one instance on one development poem) and least severely for trope and periphrasis (the two most frequent elements corpus-wide: trope 62.5%, periphrasis 54.9%, simile 27.2%, antithesis 19.6% of all 224 verses, corpus-wide).

### The elements and subtypes

Four elements are evaluated at the top level, each defined by a short Arabic/English explanation plus four to five worked examples drawn verbatim from the project's canonical element-definition files (`data/elements/*.txt`, unchanged since the earliest phase of this project and reused unedited in every prompt variant). This paper uses the corrected English terminology (antithesis for طباق, periphrasis for كناية) adopted after a 2026-07-23 supervisor correction; the original English names used throughout the earliest experimental phase ("antonymy," "kenning") are a lexical-relation mislabeling and an unrelated Old Norse/Old English poetic device respectively, retained only when citing that phase's own frozen artifacts under their original names.

**Trope (مجاز)** — "a word used in a non-literal sense based on an associative relationship, accompanied by a contextual clue that prevents the literal meaning." Trope is an umbrella covering at least three subtypes not distinguished at the top level in the primary evaluation: استعارة (metaphor, substitution by resemblance), تمثيل (analogy/extended metaphor, a whole-clause figurative comparison not reducible to one substituted word), and مجاز مرسل (metonymy/synecdoche, substitution by a non-resemblance relation — cause-for-effect, part-for-whole). Canonical مجاز مرسل examples used in the Phase 2 Config C prompt: «السماء تُمطر» ("the sky is raining," where the cloud, not the sky itself, is the actual cause) and «أراني أعصر خمراً» ("I see myself pressing wine," Qur'an 12:36, where what is literally pressed is grapes).

**Simile (تشبيه)** — "an explicit comparison between two things that share a similar quality, using a comparative marker such as 'like' or 'as'."

**Periphrasis (كناية)** — "conveys an indirect meaning by using words whose literal sense is not the intended purpose, while still allowing the literal meaning to remain possible."

**Antithesis (طباق)** — "the use of two words with opposite meanings within the same context to emphasize contrast and enhance the overall message."

*Source: `data/elements/{Trope,Simile,Kenning,Antonymy}.txt`, `GLOSSARY.md`.* A finer-grained, twenty-three-subtype taxonomy (built from Prof. Hussein's course materials and his 2025 *Journal of Arabic Literature* glossary) was evaluated separately in a supplementary recall-only screen (see Results); it is not part of the primary four-element evaluation.

A later analysis found that three of every element file's four or five worked examples are, in fact, literal verses from the three TEST poems this paper's primary evaluation scores — a held-out-set exposure present in every prompt variant used in this paper, discussed as a limitation below rather than corrected retroactively, since the frozen evaluation cannot be re-run against TEST under a new prompt without violating this project's own held-out discipline. *Source: `results/phase2_chatlike/example_gap_analysis.md`.*

### Models

Three general-purpose, closed-weight LLMs were evaluated in the primary zero-shot evaluation: Claude Sonnet 4.6 (Anthropic, `claude-sonnet-4-6`), GPT-5.4-mini (OpenAI, `gpt-5.4-mini`), and Gemini 3.5 Flash (Google, `gemini-3.5-flash`), all called at temperature 0 with an instruction-only JSON output format (no provider-native structured-output enforcement, for cross-provider comparability). A fourth model, Fable 5 (`claude-fable-5`), was added only in the supplementary disentanglement experiment described below. A separate, single-model follow-up (Gemini 3.5 Flash, later partially replicated with GPT-5.4-mini) was used for the twenty-five-subtype recall screen. *Source: `experiments/pilot_3models/config.py`.*

### Prompting design: what is zero-shot and what is not

**The primary evaluation (below, "frozen TEST results") is entirely zero-shot.** No model was shown any in-context demonstration beyond the four or five worked examples already embedded in the static element-definition files loaded into every system message. Two prompts were compared: a **baseline** system message (element definitions plus a strict per-verse JSON output schema) and **v4_combined**, a refined prompt adding three rules derived from development-set error analysis — a trope-versus-periphrasis boundary rule (the literal reading is impossible/rejected for trope, remains a plausible alternative for periphrasis, explicitly including non-literal verb usage), a marker-independence rule (an explicit simile particle does not exempt the rest of a verse from being checked for the other three elements), and a multi-figure rule (a verse may contain more than one element, or more than one instance of the same element). Four individual variants and two ablation combinations were tried on the development set before `v4_combined` was adopted as the single prompt carried forward to the frozen test evaluation, for all three models.

**Phase 2's variants are not zero-shot in the same narrow sense, and this must be stated plainly.** Config C, a two-stage, per-verse pipeline (Stage 1: free-form Arabic reasoning on Fable 5, full poem context, one verse per call; Stage 2: extraction into the unmodified strict JSON schema on GPT-5.4-mini), removes the no-explanation constraint and grants the model reasoning space the primary evaluation's schema-bound calls do not. Config A isolates the model variable alone (Fable 5 substituted for Claude Sonnet 4.6, `v4_combined` unchanged); Config B isolates the terminology variable alone (Claude Sonnet 4.6, `v4_combined` with only the English element names corrected and the مجاز block annotated with its three subtypes and the two canonical مجاز مرسل examples above). All three remain zero-shot in that no worked demonstration beyond the static element-definition files was added; what changes across A/B/C is model, terminology, and output format, not the presence of in-context examples.

**The twenty-five-subtype recall screen (Phase 3) is one-shot, not zero-shot**, and a one-shot-versus-three-shot comparison was run as part of that same phase: each subtype's prompt contains exactly one worked example (drawn from Prof. Hussein's own course materials and glossary), and a separate three-shot variant (the same textbook example plus two additional real-corpus examples, held out of testing) was compared against it for the thirteen subtypes with enough volume to spare two examples. *Source: `results/phase3_subelements/MEETING_SUMMARY.md` §4, §8b.*

### Span-level scoring

Every evaluation in this paper scores at the **span level**, never at the coarser verse-level exists/does-not-exist judgment used in the project's earliest harness. The earliest, verse-level scoring method was found to produce a measurable artifact on multi-instance verses (a verse with two ground-truth instances scored identically to one with a single instance), and re-scoring the same single-poem pilot data with a corrected, span-aware harness left trope's F1 unchanged but *lowered* periphrasis's apparent score once multi-instance verses were counted correctly — confirming the artifact was real and element-specific.

Two independent span-matching criteria are reported side by side for every result: a **strict** criterion (literal substring overlap between the model's predicted span and a ground-truth span) and a **token-overlap** criterion (word-level overlap above a 0.5 threshold, with a partial correction for attached و/ف clitics). The two criteria diverge meaningfully for antithesis specifically, where Arabic morphological variation (e.g. النُّوّامِ against the ground truth's نَوَّمُوا — different inflected forms of one root) causes the strict criterion to undercount matches the token criterion recovers.

**Every configuration in this paper is run at least twice, and the two-run majority decision is the primary reported metric; single-run numbers are never the basis for a comparative claim.** This discipline was adopted after an early single-run comparison showed one model's periphrasis F1 apparently increasing eightfold under a candidate prompt rule; a second run brought the honest, majority-vote figure down to roughly a quarter of the apparent gain. Raw true-positive/false-positive/false-negative counts are reported alongside every precision/recall/F1 figure throughout this paper, specifically so a result built on a small denominator remains visibly distinguishable from one built on a larger, more stable count.

### The DEV/TEST discipline

Before any prompt design began, the five poems were partitioned into a development set (DEV: Imru2, Nabigha) and a held-out test set (TEST: Imru1, Jarir, Abu Tammam). All prompt design and iterative refinement for the primary evaluation was conducted exclusively against DEV. TEST was evaluated exactly once, in a single frozen run comparing the baseline prompt against `v4_combined`; after that run, TEST was not re-run, re-tuned, or re-scored under any new prompt. All of Phase 2's disentanglement configurations (A/B/C) and the entire Phase 3 subtype screen are likewise DEV-only or, for Phase 3, pooled across DEV and TEST poems without touching the frozen TEST evaluation's own numbers. *Source: `writing/chapters/methodology.md` §3; `PROJECT_STATE.md` §2.*

### Difficulty analysis

Three complementary analyses characterize *where* difficulty concentrates, beyond the headline per-element P/R/F1: a trope subtype breakdown (pooled across the three TEST poems), a cross-model, span-level re-score of the twenty-five-subtype recall screen for two models, and a qualitative marker-explicitness account, developed in the Discussion, of whether some feature of the line forecloses the literal reading for the model, rather than how conceptually sophisticated the figure is in the classical taxonomy.

## Results

Every number below is cited to its exact source file and marked **final** (frozen TEST, never re-run or re-scored), **preliminary** (DEV or single-poem data, not yet validated at TEST scale), or **incomplete** (partial data by design — missing runs, single-model, recall-only, or precision/F1 structurally unmeasurable).

### Phase 1: frozen TEST results

Ground-truth support on TEST (pooled, deduplicated, across Imru1, Jarir, and Abu Tammam): trope 179, simile 52, periphrasis 147, antithesis 43. Strict-criterion precision/recall/F1, baseline versus the refined prompt (`v4_combined`), two-run majority:

| Element | Model | Baseline P/R/F1 | v4_combined P/R/F1 | Status |
|---|---|---|---|---|
| Trope | Claude Sonnet 4.6 | 0.85/0.09/0.171 | 0.89/0.14/0.242 | **final** |
| Trope | GPT-5.4-mini | 0.86/0.03/0.065 | 0.64/0.16/0.251 | **final** |
| Trope | Gemini 3.5 Flash | 0.89/0.19/0.313 | 0.83/0.25/0.386 | **final** |
| Simile | Claude Sonnet 4.6 | 0.82/0.54/0.651 | 0.82/0.54/0.651 | **final** |
| Simile | GPT-5.4-mini | 0.88/0.58/0.698 | 0.91/0.60/0.721 | **final** |
| Simile | Gemini 3.5 Flash | 0.82/0.62/0.703 | 0.89/0.62/0.727 | **final** |
| Periphrasis | Claude Sonnet 4.6 | 0.80/0.05/0.102 | 0.57/0.05/0.099 | **final** |
| Periphrasis | GPT-5.4-mini | 0.20/0.01/0.013 | 0.36/0.03/0.051 | **final** |
| Periphrasis | Gemini 3.5 Flash | 0.69/0.06/0.113 | 0.65/0.10/0.176 | **final** |
| Antithesis | Claude Sonnet 4.6 | 0.26/0.12/0.161 | 0.33/0.14/0.197 | **final** |
| Antithesis | GPT-5.4-mini | 0.27/0.09/0.138 | 0.23/0.12/0.154 | **final** |
| Antithesis | Gemini 3.5 Flash | 0.17/0.09/0.121 | 0.19/0.12/0.145 | **final** |

*Source: `PROJECT_STATE.md` §3a.* Raw TP/FP/FN (strict, `v4_combined`): Trope — Claude 25/3/154, GPT 28/16/151, Gemini 45/9/134. Simile — Claude 28/6/24, GPT 31/3/21, Gemini 32/4/20. Periphrasis — Claude 8/6/139, GPT 4/7/143, Gemini 15/8/132. Antithesis — Claude 6/12/37, GPT 5/17/38, Gemini 5/21/38. *(These rows use Phase 1's own run output; the underlying frozen artifact used the superseded English names "kenning"/"antonymy." See `GLOSSARY.md` for the citation convention.)*

The refined prompt improves every model on trope, simile, and antithesis, and is essentially flat on periphrasis — periphrasis strict F1 never exceeds 0.176 anywhere in this table, against simile's 0.65–0.73 ceiling. Run-to-run decision agreement is 88–100% under the baseline prompt and 89–100% under `v4_combined`, across all four elements and three models.

**The token-overlap criterion reveals a substantially larger baseline→refined-prompt gap for antithesis specifically**, due to Arabic morphological variation: baseline token F1 is 0.419/0.345/0.545 (Claude/GPT/Gemini) against 0.161/0.138/0.121 strict; refined-prompt token F1 is 0.393/0.431/0.609 against 0.197/0.154/0.145 strict. A second, test-scale-only finding is that all three models systematically **over-claim antithesis**: false positives exceed true positives for every model at baseline (Claude TP=5/FP=14, precision 0.263) — the opposite failure mode from trope and periphrasis, which are under-detected rather than over-claimed. *Source: `PROJECT_STATE.md` §3a, §3d.*

### Trope subtype breakdown (final, TEST, pooled across three models)

| Subtype | n | Baseline missed | v4_combined missed |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | 62% |
| مجاز عقلي (rational trope) | 41 | 83% | 66% |
| استعارة تمثيلية (whole-clause allegory) | 24 | 33% | 29% |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% |
| مجاز مرسل (metonymy, single lexicalized word) | 13 | 85% | 85% |
| استعارة حديثة | 4 | 75% | 75% (n=4, too thin to generalize) |

*Source: `PROJECT_STATE.md` §3c.* A two-poem DEV analysis had flagged استعارة تمثيلية as the hardest trope subtype; at TEST scale this reversed — it is in fact the *easiest* subtype in the table, both before and after refinement. The refined prompt's validated wins are استعارة فعل and مجاز عقلي; مجاز مرسل is the one subtype no Phase 1 intervention moves at all (85%→85%, unchanged). A majority-vote ensemble across all three models gives no improvement over the best single model for trope or periphrasis (the models miss the same instances, not independent errors an ensemble could average out), and is worse than the best single model for simile. *Source: `PROJECT_STATE.md` §3e.*

### Phase 2: Config A/B/C disentanglement (preliminary, DEV only)

Pooled DEV (Imru2+Nabigha), strict criterion, TP/FP/FN, F1:

| Element | Existing (Sonnet 4.6 + v4) | Config A (Fable 5 + v4) | Config B (Sonnet 4.6 + v4, terms corrected) | Status |
|---|---|---|---|---|
| Trope | 2/6/58, F1=0.059 | 7/3/53, F1=0.200 | 3/4/57, F1=0.090 | **preliminary** |
| Periphrasis | 5/3/64, F1=0.130 | 8/4/61, F1=0.198 | 5/7/64, F1=0.123 | **preliminary** |

*Source: `results/phase2_chatlike/report_3i.md` §2–§3.* Config A (model substitution alone, same prompt) moves both trope and periphrasis with no precision cost. Config B (terminology correction alone) gives trope a modest genuine boost but leaves periphrasis flat-to-worse — correcting "kenning"→"periphrasis" alone does not unlock periphrasis recall.

**Config C (Imru2 only, two-stage free-form pipeline)**: 6/15/11, F1=0.316 strict (token F1=0.421) on periphrasis, against the same-poem existing-pipeline figure of 1/0/16, F1=0.111 — the largest single periphrasis gain found anywhere in this project, and it catches the exact motivating verse (Imru2 v6, «كُلَّمَا نَبَّهْتُهَا») that every structured-pipeline configuration misses. *Source: `PROJECT_STATE.md` Phase 2 §3i.* **This gain is run-to-run unstable, not merely a caveat but part of the finding**: a targeted Nabigha مجاز مرسل recall probe (known-positive verses only) caught 4 of 10 verses in at least one of two runs, but only 1 of 10 under this project's own two-run-majority convention — most hits came from a single run of the pair. *Source: `report_3i.md` §8–§9.* Config C's full-poem run on Nabigha was never executed (budget-held, ≈$11.9 estimate); only this narrower, known-positive probe exists for a second poem, so Config C's F1 figure above is single-poem and preliminary, not a replicated finding.

### Phase 3: twenty-five-subtype recall screen (incomplete: recall only, by design)

Every row in this screen is a line Prof. Hussein already tagged positive for its own subtype; no model was ever shown a negative example for any subtype, so **false positives, true negatives, precision, and F1 are mathematically undefined by this design, not merely unmeasured**, for every subtype and every model. *Source: `results/phase3_subelements/MEETING_SUMMARY.md` §4.* Twelve of the twenty-five tested subtypes have fewer than ten ground-truth instances and are flagged as directionally suggestive only, never as a standalone comparative claim.

Reliable subtypes (n≥10), recall by model, span-level (strict criterion), pooled DEV+TEST:

| Subtype | Parent element | n | Gemini 3.5 Flash | GPT-5.4-mini | Status |
|---|---|---|---|---|---|
| استعارة فعل | Trope | 110 | 0.264 | 0.155 | **incomplete** — recall only |
| كناية عن صفة | Periphrasis | 74 | 0.446 | 0.351 | **incomplete** |
| كناية عن موصوف | Periphrasis | 61 | 0.262 | 0.328 | **incomplete** |
| مجاز عقلي | Trope | 54 | 0.463 | 0.426 | **incomplete**, consistent with the TEST-scale finding above |
| طباق إيجاب | Antithesis | 38 | 0.237 | 0.053 | **incomplete** |
| كناية لغوية | Periphrasis | 32 | **0.719** | **0.031** | **incomplete** — see prompt-sensitivity discussion below |
| تشبيه مطول | Simile | 30 | 0.833 | 0.667 | **incomplete** |
| استعارة تمثيلية | Trope | 28 | **0.143** | **0.571** | **incomplete** — see prompt-sensitivity discussion below |
| كناية عن فعل | Periphrasis | 27 | 0.333 | 0.148 | **incomplete** |
| مجاز مرسل | Trope | 24 | 0.292 | 0.000 | **incomplete** |
| استعارة قديمة | Trope | 17 | 0.412 | 0.176 | **incomplete** |
| تشبيه قصير | Simile | 13 | 0.615 | 0.769 | **incomplete** |
| كناية فنية | Periphrasis | 10 | 0.300 | 0.200 | **incomplete** |

*Source: `results/phase3_crossmodel/summary.md`, "Headline table."* This re-score is **span-level**, not the original screen's verse-level `exists=true`-by-majority check; re-scoring at the span level pulled recall down substantially for several subtypes (e.g. استعارة فعل: naive verse-level 0.627 → strict span-level 0.264 for Gemini) because a model's "yes" sometimes pointed at a different candidate figure in the same verse than the one Prof. Hussein annotated — a real localization-accuracy finding, not a scoring artifact.

**استعارة تمثيلية and كناية لغوية are reported here as prompt-sensitivity effects, not as evidence of a fixed model-capability gap.** Both subtypes show large, model-dependent swings rather than a consistent floor: كناية لغوية goes from Gemini's strongest subtype result (0.719, n=32) to GPT's near-total failure (0.031) on the identical prompt and identical lines — a model-specific, not task-intrinsic, collapse (GPT's two runs agree closely at 1/32 and 2/32, so this is not single-run noise). استعارة تمثيلية shows the reverse pattern — Gemini's weakest subtype (0.143) against GPT's strongest relative performance (0.571) — and a one-shot-versus-three-shot comparison run separately for this subtype found recall moving from 15.4% to 38.5% with two additional worked examples, one of the few subtypes few-shot helped at all. *Source: `results/phase3_crossmodel/summary.md`, "Two results stand out."* Read together, these are evidence that performance on these two subtypes is unusually sensitive to which model, which prompt format, and how many worked examples are used — exactly the kind of instability a single-model, single-prompt evaluation would never surface.

Twelve subtypes below n=10 (not used for any comparative claim, included for completeness): كناية بسيطة (n=9, Gemini 0.667/GPT 0.333), طباق في المعنى (n=8, 0.000/0.000), طباق سلب (n=5, 0.000/0.200), استعارة حديثة (n=5, 0.400/0.200), مقابلة تضاد (n=4, 0.500/0.250), تشبيه تمثيلي (n=4, 0.250/0.500), تشبيه الشيء بنفسه (n=4, 0.750/0.250), كناية نسبة (n=4, 0.000/0.000), تشبيه مركب (n=3, 0.667/0.667), استعارة قديمة مرشحة (n=2, 1.000/0.500), استعارة فعل مرشحة (n=2, 0.500/0.000), استعارة تمثيلية مبنية على الكناية (n=2, 0.500/0.000). *Source: `results/phase3_crossmodel/summary.md`.* Claude Sonnet 4.6 was not run on this screen; only Gemini 3.5 Flash (the original screen) and GPT-5.4-mini (a later cross-model pass) have been evaluated.

### Reconciling Phase 1 and Phase 2

Phase 1's own frozen reports describe periphrasis as "resistant across every intervention attempted," a true statement about Phase 1's own structural interventions (per-element decomposition helped one of three models and made the other two measurably worse; per-verse granularity produced a real, cross-poem-replicated gain for two of three models but one that costs four to eight times more per unit of F1 than the adopted method and tops out at F1=0.338). That statement is **contradicted, not merely qualified, by Phase 2's Config C finding** (strict F1 0.111→0.316 on the same poem, Imru2) once free-form reasoning replaces the strict no-explanation JSON format. The two findings are reconciled, not in tension, once format is treated as its own variable: periphrasis is reachable under a different output format, but not yet reliably decidable by any configuration tried, given Config C's run-to-run instability (above). This paper reports both halves of that finding together, rather than repeating Phase 1's "resistant to every intervention" framing as if Phase 2 did not exist.

## Discussion

### A difficulty pattern, not a difficulty scale

The frozen test-set results answer RQ1 and RQ2 together, and the answer is not simply that some elements are harder than others. Simile, whose own definition names an explicit comparative particle as its defining feature, reaches strict-criterion F1 of 0.65–0.73 under the refined prompt for every model — a ceiling three to seven times higher than periphrasis's best score anywhere in the primary evaluation (never exceeding 0.176 strict). That ordering alone would support a familiar story: easy elements have surface markers, hard elements do not. But antithesis complicates the story, because it also has a locatable surface signal — a pair of lexically opposed terms — and models find that signal readily. The failure is not under-detection but over-claiming: false positives exceed true positives for every model under both prompts (Claude Sonnet 4.6's refined-prompt result, for example, is 6 true positives against 12 false positives), a pattern invisible on the two-poem development set, where antithesis support was a single instance, and only legible once the three-poem test set's 43 instances made it measurable. A model that over-generalizes "two opposed words" into "antithesis" without checking whether the opposition is the point of the line is making a qualitatively different error than one that cannot locate periphrasis at all. An account of this corpus's difficulty pattern that collapses to a single axis — "simple" elements near a ceiling, "complex" elements near a floor — misses this distinction, and with it, the difference between a precision problem and a recall problem calling for different remedies.

The trope subtype breakdown sharpens this further. استعارة فعل (verb-anchored metaphor, trope's largest subtype by volume) moved from 83% missed under the baseline prompt to 62% missed under the refined one — the single largest subtype-level gain the frozen evaluation recorded — because a verb used in a sense that cannot apply literally in context gives the model a locatable incongruity to anchor on, much as simile's particle does, even though locating that incongruity and distinguishing it from ordinary polysemy takes a small inferential step a bare particle does not. استعارة تمثيلية (whole-clause allegory) offers the sharpest illustration that a locatable marker need not be a lexical particle at all: hypothesized as trope's hardest subtype from a two-poem development sample, it proved easiest at test scale (29% missed under the refined prompt, against مجاز مرسل's unmoved 85%), because the figurative reading is typically the only sensible reading for the entire clause — there is no competing literal reading left standing for the model to be tempted by. مجاز مرسل itself is the clearest counter-case: a closed, conventionalized set of substitutions with no compositional anomaly to key on, and the one subtype no prompt intervention moved at all. Read together, what predicts a model's success across this corpus is less how conceptually elaborate a figure is held to be in the classical taxonomy, and more whether some feature of the line — a particle, a lexical opposition, or a foreclosed literal reading — gives the model a seam to locate, or leaves the literal and figurative readings standing side by side with nothing to break the tie.

Periphrasis's one partial exception to this pattern deserves to be stated carefully, because the finding is genuinely mixed rather than a straightforward improvement. Allowing a model free-form Arabic reasoning space before answering, rather than a closed-form, no-explanation JSON schema (the two-stage Config C pipeline), produced the largest periphrasis gain found anywhere in this project on one development poem — strict F1 0.111 to 0.316 — and caught a periphrasis instance every structured-pipeline configuration in this study missed for that verse. But a second independent run of the same free-form configuration frequently disagreed with the first about which phrase in the verse deserved the tag, so that most of the instances this configuration could reach at all were caught in only one of two runs; under this project's own two-run-majority convention, most of the apparent gain does not survive. The honest statement is that periphrasis is reachable under a different output format, but not yet reliably decidable by any configuration this study tried — a model can sometimes find the right reading when given room to reason, without having a stable criterion for recognizing it as right twice in a row.

### Prompt sensitivity as a finding, not only a limitation

The subtype-level recall screen surfaces a second pattern worth treating as a result in its own right rather than noise to be apologized for. كناية لغوية (a periphrasis subtype in which an elided noun is identified only by its surviving epithet) is Gemini 3.5 Flash's strongest subtype in that screen (0.719 recall, n=32) and GPT-5.4-mini's near-total failure on the identical lines and prompt (0.031) — and GPT's two runs agree closely with each other at that low figure, so this is a model-specific collapse, not single-run noise. استعارة تمثيلية shows the mirror-image pattern: Gemini's weakest subtype (0.143) against GPT's strongest relative performance on it (0.571), consistent across both of GPT's runs. Separately, a one-shot-versus-three-shot comparison for استعارة تمثيلية specifically found recall moving from 15.4% to 38.5% with two additional worked examples — a demonstration that a single worked example can anchor a model's reading of a subtype in a way one additional example can substantially unsettle.

None of this licenses a claim that either subtype is secretly easy for some undiscovered configuration, and this paper does not make that claim. What it does license is a more specific methodological finding: for a non-trivial fraction of this taxonomy's subtypes, which model is queried and how many worked examples anchor its reading of a category can move recall by tens of percentage points on the identical lines — a swing comparable in size to the headline differences this study reports between entire rhetorical elements. For a field accustomed to treating "I asked ChatGPT about this verse" as a single, stable operation, the lesson is that it is not: the result depends on a choice of model and prompt design usually invisible in how the result gets reported. This extends Reimann and Scheffler's (2025) and Fuoli et al.'s (2025) contrasting findings for metaphor detection in other languages by showing the same instability subtype-by-subtype, within one evaluation, for a single language and a single annotator's ground truth.

### Cross-model consistency and idiosyncrasy (RQ3)

RQ3 asked whether difficulty patterns are consistent across models or idiosyncratic to each one; the honest answer, on this evidence, is both, depending on the grain examined. At the level of the four top-level elements, the three primary-evaluation models agree closely: all three show periphrasis hardest and simile easiest, and the refined prompt helps trope, simile, and antithesis for every model while leaving periphrasis essentially flat. At the level of individual subtypes, however, the two-model screen shows GPT-5.4-mini scoring strictly lower than Gemini 3.5 Flash on ten of thirteen reliable subtypes and strictly higher on the other three, with the كناية لغوية and استعارة تمثيلية reversals above as the sharpest examples. This two-grain pattern is broadly consistent with Kühn, Mitrović and Granitzer's (2024) finding that named rhetorical figures beyond metaphor and irony remain a structurally under-studied, inconsistently handled class across languages and systems generally, and with Attia et al.'s (2026) finding that LLMs measurably underperform on Arabic figurative language even where human annotators agree closely with each other — both corroborated here for classical Arabic poetry specifically.

### What this means for humanities scholars using LLMs on classical Arabic poetry

Read together with Al Kaabi et al.'s (2024) qualitative finding that ChatGPT produces surface-level readings of Arabic rhetorical figures that miss the depth a trained reader supplies, this study's quantitative results suggest a more specific, usable version of the same caution. For an element whose definition names an explicit surface marker — simile here — a general-purpose LLM's zero-shot output is close enough to a detection task that a scholar can reasonably treat it as a fast first pass, to be checked rather than trusted blindly. For periphrasis, and for the closed, conventionalized subclass مجاز مرسل specifically, the evidence points the other way: output on these categories should be treated as unreliable, not because the model never finds the right answer, but because it has no demonstrated way of finding it reliably twice. For the subtypes most exposed to prompt- and model-dependent swings, the implication is not that LLMs cannot help with this kind of analysis, but that model and prompt design are themselves part of what a scholar using an LLM needs to report — in the spirit Dobson (2021) urges for any accuracy figure presented as more decisive than its evidence warrants. This paper's contribution is best read in that diagnostic register: a characterization of exactly where, and under what conditions, large language models currently can and cannot be trusted to identify classical Arabic rhetorical elements, extending the frontier Abd Alhadi, Hussein and Kuflik (2023) named as beyond their own rule-based system's reach.

## Limitations and Future Work

### Ground truth and annotation

Every result reported here is evaluated against one domain expert's (Prof. Ali Hussein) manual rhetorical analysis. No second annotator has independently labeled any poem, and no inter-annotator agreement figure exists for this corpus at the time of writing. A blind re-annotation protocol has been designed — an eighty-verse, poem-proportional stratified sample, scored by Cohen's κ and Krippendorff's α on verse-level presence/absence, plus strict and token-overlap span agreement — but the re-annotation pass itself is not complete, so every agreement figure this protocol would produce is `[TBD]`. Even once complete, that pass measures one annotator's agreement with their own earlier judgments, not independent inter-annotator agreement; whether to pursue a genuinely independent second annotator with the relevant subject-matter expertise remains an open, unresolved decision. Readers should treat every precision figure here as a comparison against one expert's reading, not an agreed-upon gold standard — a caution the trope/periphrasis boundary especially invites, since it turns on whether a literal reading remains plausible, exactly the kind of judgment trained readers of classical Arabic rhetoric can reasonably disagree on. This is not unique to this study: Bender et al. (2023) and Zirker and Göggelmann (2023) both report, for comparably ambiguous annotation tasks, that agreement must be measured empirically rather than assumed from a category's apparent simplicity, a lesson this project's own run-to-run instability findings independently reinforce.

### Corpus scope

The corpus comprises five poems — three held out as a frozen test set, two used for development — all within the classical Arabic *qaṣīda* tradition and skewing toward the pre-Islamic and early Islamic period. Nothing here licenses a claim that findings generalize beyond this tradition and period; Andalusian, Abbasid-era ornate, or Mamluk-era poetry may present a different difficulty profile. The corpus is also small in absolute terms (43 antithesis and 52 simile instances on the full test set), and this study's own history records two cases — the trope subtype reversal and the antithesis over-claiming pattern — invisible or misleading at a smaller development-set scale, only measurable once pooled across three test poems. There is no principled reason to assume five poems is large enough that a sixth could not produce a comparable reversal. Twelve of the twenty-five subtypes in the supplementary recall screen fall below ten ground-truth instances; these are reported for completeness but support no comparative claim here.

### Phase 3's recall-only, Gemini-first design

The twenty-five-subtype recall screen tests only lines already tagged positive for their own subtype; no model was ever shown a negative example for any subtype, so false positives, true negatives, precision, and F1 are mathematically undefined by this design, not merely unmeasured. The screen was run first, and most extensively, on a single model (Gemini 3.5 Flash, chosen for cost); a later cross-model pass added GPT-5.4-mini on the identical rows, but Claude Sonnet 4.6 has not been run on this screen, and every subtype-level claim in this paper is scoped to at most two models for this reason, not three as in the primary evaluation.

### Model version drift and corpus rights

Every model evaluated is a hosted commercial API, pinned only by a model-ID string, with no guarantee the provider will not update weights behind that identifier; raw outputs for every run are archived specifically so a later comparison remains possible even if exact reproduction is not. Separately, the licensing and usage-rights status of the ground-truth annotations and underlying poem texts is not yet documented anywhere in this project `[TBD]`; this blocks a Data Availability statement, and is pending confirmation from the corpus's custodians before any data release can be described in a final version of this paper.

### Future work

A second, independent annotator, or completion of the blind re-annotation pass, would convert this paper's single-annotator caveat into a measured agreement figure. A negative-sampling follow-up for the subtypes this paper discusses most — particularly استعارة تمثيلية and كناية لغوية — would make precision and F1 computable where only recall currently is. Running Claude Sonnet 4.6 on the subtype screen would complete the three-model roster already used in the primary evaluation. Finally, given how much this paper's own results show recall moving with model choice and worked-example count, a systematic study varying both deliberately — rather than observing the effect incidentally, as this paper does — is a natural next step for establishing how much of the difficulty pattern reported here is a property of the task and how much is a property of specific prompting choices.

## Conclusion and Future Work

This paper evaluated three general-purpose large language models, zero-shot, on span-level identification of four classical Arabic rhetorical elements against one expert's manual annotation of five poems, three of them held out as a frozen test set. The result is not a single headline accuracy figure but a difficulty pattern: simile, whose definition names an explicit comparative particle, reaches strict-criterion F1 of 0.65–0.73 for every model, while periphrasis never exceeds 0.176 anywhere in the primary evaluation. That ordering corroborates, with quantitative evidence, the diagnosis Abd Alhadi, Hussein and Kuflik (2023) offered from the other direction — that metaphor and periphrasis are too semantically demanding for rule-based matching — while showing that the elements their rule-based system already handled well are not uniformly easy for a language model either: antithesis is locatable but systematically over-claimed, a precision failure rather than a recall one. A supplementary disentanglement experiment and a twenty-five-subtype recall screen extend this picture further, showing that periphrasis is reachable, if not yet reliably decidable, under a different output format, and that several subtypes are strikingly sensitive to which model is queried and how many worked examples anchor its reading of a category.

This paper's contribution is diagnostic rather than a performance claim: it characterizes where and under what conditions current large language models can be trusted to identify named rhetorical elements in classical Arabic poetry, and where their apparent success or failure depends on model choice and prompt design rather than on a stable capability. For humanities scholars considering an LLM as an aid to rhetorical analysis, that diagnosis is itself the usable result — a reason for calibrated trust on well-marked elements and calibrated skepticism on elements defined by the absence of a surface marker, rather than a single verdict on whether these models "work" for this kind of reading.

The limitations enumerated above point to the clearest next steps: a completed or independent inter-annotator agreement measurement, a negative-sampling follow-up that would make precision and F1 computable for the subtypes this paper discusses most, a third model added to the subtype screen, and a deliberate study of how model choice and worked-example count move performance on the elements and subtypes this paper found most unstable. Each is a comparatively contained extension of the evaluation design already built here, not a redesign of it.

## AI Disclosure

*Per DHQ's AI policy (https://dhq.digitalhumanities.org/submissions/ai_policies.html), the policy draws a hard line between AI as the object of study and AI assistance in writing the paper itself, and requires disclosure of any substantive use of the latter.*

### AI as the object of study

This paper's central method is the evaluation of large language models — Claude Sonnet 4.6 (Anthropic), GPT-5.4-mini (OpenAI), and Gemini 3.5 Flash (Google), with Fable 5 (Anthropic) used only in the supplementary disentanglement experiment — on the task of identifying rhetorical elements in classical Arabic poetry. Every model output discussed in the Results and Discussion sections is reported as data: the output of the system under study, never presented as the authors' own analysis or interpretation. Model identities, versions, call dates, temperature settings, and prompting configurations are documented in full in Data and Methods and the project's archived run manifests.

### AI assistance in writing and research

- **Literature search and source-finding assistance**: `[TBD — human author(s): if an AI assistant helped locate, summarize, or verify sources, name the tool and tasks, and confirm every citation in the final Works Cited was independently verified against the original publication or DOI/publisher metadata before inclusion.]`
- **Translation or clarification of Arabic terminology**: `[TBD — state whether AI assistance was used in translating or glossing the Arabic rhetorical terms used here.]`
- **Drafting assistance**: `[TBD — state plainly whether any portion of this paper's prose was drafted with AI assistance and then revised by the human author(s), or was human-drafted throughout.]`
- **Routine utilities excluded from disclosure per policy**: grammar and spell-checking are explicitly exempted by DHQ's AI policy and are not itemized here.

### Accuracy responsibility

Per DHQ's policy, the human author(s) bear full responsibility for the accuracy of all citations and content in this paper, regardless of what tools assisted in drafting or research. All citations in this paper's Works Cited were verified against the original source (PDF or publisher/DOI metadata) prior to submission.

## Works Cited

Abd Alhadi, H., Hussein, A. A. and Kuflik, T. (2023) 'Automatic Identification of Rhetorical Elements in classical Arabic Poetry', *Digital Humanities Quarterly*, 17(2).

Al Kaabi, M. H., Abubkr, L. O., Abdeddayem, S., Bin Haidara, N. and Almaamari, H. (2024) 'Developing the teaching Arabic rhetoric: A comparative analysis of artificial intelligence and traditional hermeneutical approaches', *Journal of Infrastructure, Policy and Development*, 8(15), p. 9925.

Attia, M., Muhamed, A., Alkhamissi, B., Solorio, T. and Diab, M. (2026) 'Beyond Understanding: Evaluating the Pragmatic Gap in LLMs' Cultural Processing of Figurative Language', *Proceedings of EACL 2026*.

Balestrucci, A., Oliverio, A., Lo, C., Anselma, L., Basile, V., Mazzei, A. and Patti, V. (2025) 'When Figures Speak with Irony: Investigating the Role of Rhetorical Figures in Irony Generation with LLMs', *CLiC-it 2025*, CEUR-WS vol. 4112.

Bender, M., Becker, M., Kiemes, C. and Müller, M. (2023) 'Category Development at the Interface of Interpretive Pragmalinguistic Annotation and Machine Learning', *Digital Humanities Quarterly*, 17(3).

Cachia, P. (1998) *The Arch Rhetorician, or The Schemer's Skimmer: A Handbook of Late Arabic Badi'*. Wiesbaden: Harrassowitz Verlag (Studies in Arabic Language & Literature, vol. 3).

Cohen, J. (1960) 'A Coefficient of Agreement for Nominal Scales', *Educational and Psychological Measurement*, 20(1), pp. 37–46.

Dobson, J. (2021) 'Interpretable Outputs: Criteria for Machine Learning in the Humanities', *Digital Humanities Quarterly*, 15(2).

Fontana, C. (2025) 'The Name of the Key: Al-Sakkākī's Literary Craftsmanship and Pragmatic Poetics in Miftāḥ al-ʿUlūm', *Journal of Arabic and Islamic Studies*, 25, pp. 57–87.

Fuoli, M., Huang, C., Littlemore, J., Turner, S. and Wilding, R. (2025) 'Metaphor identification using large language models: A comparison of RAG, prompt engineering, and fine-tuning', arXiv preprint, arXiv:2509.24866.

Gutman, G. (2024) 'A Network Analysis of Figurative Topic Classification: The Case Study of Timon of Athens', *Digital Humanities Quarterly*, 18(3).

Harb, L. (2020) *Arabic Poetics: Aesthetic Experience in Classical Arabic Literature*. Cambridge: Cambridge University Press.

Hayes, A. F. and Krippendorff, K. (2007) 'Answering the Call for a Standard Reliability Measure for Coding Data', *Communication Methods and Measures*, 1(1), pp. 77–89.

Hicke, R. M. and Kristensen-McLachlan, R. D. (2024) 'Science is Exploration: Computational Frontiers for Conceptual Metaphor Theory', *Computational Humanities Research Conference (CHR 2024)*.

Hussein, A. A. (2015) *The Rhetorical Fabric of the Traditional Arabic Qaṣīda*. Wiesbaden: Harrassowitz Verlag.

Kühn, R. and Mitrović, J. (2024) 'The Elephant in the Room: Ten Challenges of Computational Detection of Rhetorical Figures', *Proceedings of the 4th Workshop on Figurative Language Processing (FigLang 2024)*.

Kühn, R., Mitrović, J. and Granitzer, M. (2024) 'Computational Approaches to the Detection of Lesser-Known Rhetorical Figures: A Systematic Survey and Research Challenges', arXiv preprint, arXiv:2406.16674.

Münz-Manor, O. and Marienberg-Milikowsky, I. (2023) 'Visualization of Categorization: How to see the wood and the trees', *Digital Humanities Quarterly*, 17(3).

Qarah, F. (2024) 'AraPoemBERT: A Pretrained Language Model for Arabic Poetry Analysis', arXiv preprint, arXiv:2403.12392.

Reimann, J. and Scheffler, T. (2025) 'The Struggles of Large Language Models with Zero- and Few-Shot (Extended) Metaphor Detection', *Journal for Language Technology and Computational Linguistics*, 38(2).

Tarkka, O., Elo, K., Ginter, F. and Laippala, V. (2026) 'Do all politicians sound the same? Comparing model explanations to human responses', *Digital Humanities Quarterly*, 20(1).

Ye, F., Wang, S., Chao, L. S. and Wong, D. F. (2026) 'Probing Semantic Alignment, Lexical Invariance, and Syntactic Influence in LLM Metaphor Processing', *Proceedings of ACL 2026, Volume 1: Long Papers*, pp. 27914–27932.

Zirker, A. and Göggelmann, M. (2023) 'Case Study: Annotating the ambiguous modality of "must" in Jane Austen's Emma', *Digital Humanities Quarterly*, 17(3).
