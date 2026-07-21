# Methodology

## 1. Task definition

This thesis evaluates the ability of general-purpose large language models to identify four rhetorical elements in classical Arabic poetry: trope (مجاز), simile (تشبيه), kenning (كناية), and antonymy (طباق). Each element is treated as a span-level identification task rather than a verse-level classification task: for a given verse, a model must decide, independently for each of the four elements, whether an instance of that element is present, and if so, must identify the literal substring of the verse that constitutes the evidence for that instance. A verse may contain zero, one, or several instances of a given element, and may contain instances of more than one element simultaneously; the task definition and the scoring procedure (§6) are both built around this possibility rather than around a simpler exists/does-not-exist judgment per verse.

The decision to score at the span level, rather than the coarser verse level used in earlier phases of this project, was itself a methodological correction made partway through the pilot cycle and is discussed in §6.1.

## 2. Data

The corpus consists of five classical Arabic poems, drawn from the project's existing archive of poem texts and paired expert annotations: two poems by Imru' al-Qais (the Mu'allaqa, referred to as Imru1, and a second, shorter poem referred to as Imru2), one poem each by Jarir, Abu Tammam, and Al-Nabigha Al-Dhubyani (Nabigha).

<!-- source: experiments/pilot_3models/config.py (POEMS registry, n_verses field) -->
| Poem | Poet | Verses |
|---|---|---|
| Imru1 | Imru' al-Qais (Mu'allaqa) | 81 |
| Jarir | Jarir | 40 |
| Abu Tammam | Abu Tammam | 30 |
| Imru2 | Imru' al-Qais (poem 8) | 23 |
| Nabigha | Al-Nabigha Al-Dhubyani | 50 |

Ground truth for all five poems is a single expert's manual rhetorical analysis (Prof. Ali Hussein), originally produced against a 53-category classical rhetoric taxonomy and subsequently mapped down to the four elements studied here by substring matching on the taxonomy's primary and secondary element labels (مجاز or استعارة mapping to trope; direct matches for تشبيه, كناية, and طباق). Exact-duplicate (span, element) annotation rows — the same phrase double-tagged under two subtype labels of the same element — are deduplicated before any count is taken, so the instance counts reported throughout this thesis are the real, deduplicated counts actually used for scoring, not the raw annotation-row counts.

<!-- source: experiments/pilot_3models/ground_truth.py:load_ground_truth_spans, verified by direct re-execution against data/ground_truth/ali_ana/original/*.xlsx -->
| Poem | Trope | Simile | Kenning | Antonymy |
|---|---|---|---|---|
| Imru1 | 90 | 39 | 87 | 20 |
| Jarir | 51 | 4 | 48 | 17 |
| Abu Tammam | 38 | 9 | 12 | 6 |
| Imru2 | 8 | 5 | 17 | 1 |
| Nabigha | 52 | 15 | 52 | 4 |

The per-poem counts make clear that ground-truth support is highly uneven across both poems and elements. Antonymy in particular has fewer than 10 instances in three of the five poems, and Imru2 alone offers only a single antonymy instance — a fact that recurs throughout the discussion of which findings should be trusted and which should be treated as suggestive only.

Ground truth is drawn from a single annotator throughout; no inter-annotator agreement figure exists for any poem or element. This is treated as a limitation of the present work (see the limitations chapter) rather than something the pilot cycle attempted to address.

## 3. DEV/TEST split and leakage discipline

Before any prompt design or model comparison began, the five poems were partitioned into a development set (DEV: Imru2, Nabigha) and a held-out test set (TEST: Imru1, Jarir, Abu Tammam), fixed in code as `DEV_POEMS` and `TEST_POEMS` in the experiment configuration.

<!-- source: experiments/pilot_3models/config.py -->

All prompt design, error analysis, and iterative refinement described in §4 was conducted exclusively against DEV. TEST was evaluated exactly once, in a single frozen run comparing the initial baseline prompt against the final refined prompt (§4.2), after which no further prompt changes, re-runs, or re-scoring against TEST poems were permitted. This discipline was maintained throughout two supplementary experiments conducted after the TEST run (per-element decomposition and per-verse granularity, described fully in the Results chapter §6 and §7), both of which were evaluated on DEV poems only, specifically so that a promising-looking result could not create pressure to reopen TEST. The rationale is standard train/validation/test practice adapted to a zero-shot prompting context: without a held-out set that is never used to select among prompt variants, an apparently strong result risks reflecting overfitting to the quirks of the specific poems used for iteration rather than a genuine property of the prompt or model. §6.3 below and the Results chapter's account of the cross-poem replication check (§7) describe two concrete instances within this pilot cycle where exactly this kind of overfitting to a small development sample was observed and had to be corrected, which is offered as retrospective justification for why the discipline was maintained even when a supplementary finding looked encouraging.

## 4. Prompt architecture

### 4.1 Baseline

The baseline prompt used throughout this pilot cycle is adapted, without substantive change, from the most refined prompt developed during the project's earlier Forth_Step phase: a system message giving the model the four element definitions verbatim (Arabic and English explanations plus four to five worked examples per element, drawn from the project's canonical element-definition files) and instructing the model to rely only on those definitions, and a user message containing the poem text together with a strict output-format specification (one JSON object per verse, `exists`/`appearance` fields for each of the four elements, appearance required to be a literal substring of the verse when `exists` is true).

<!-- source: experiments/pilot_3models/prompts.py (SYSTEM_HEADER, ANALYSIS_INSTRUCTIONS); data/elements/{Trope,Simile,Kenning,Antonymy}.txt -->

### 4.2 v4_combined: refinement from DEV error analysis

Manual review of the baseline prompt's errors on DEV surfaced three recurring failure patterns, each of which was addressed with one added rule, and the three rules together constitute the refined prompt evaluated against TEST (`v4_combined`):

1. A boundary rule distinguishing trope from kenning on the criterion actually used by the element definitions — whether the literal meaning of an expression is rejected by context (trope) or remains a possible, if unusual, reading alongside the figurative one (kenning) — including an explicit note that this criterion applies to verbs used non-literally, not only to noun-based figures, since the baseline prompt was observed to under-recognize verbal trope.
2. A marker-independence rule stating that an explicit simile particle (كأن، كما، ك، مثل) is evidence for simile specifically and does not exempt the rest of a verse from being checked for the other three elements, since the baseline prompt was observed to treat the presence of a simile marker as closing the analysis of a verse prematurely.
3. A multi-figure rule reminding the model that a single verse may contain more than one element, and more than one instance of the same element, addressing an observed tendency to stop after finding the first applicable element in a verse.

<!-- source: experiments/pilot_3models/prompt_variants.py (RULE_1_BOUNDARY, RULE_2_MARKER_INDEPENDENCE, RULE_3_MULTI_FIGURE, VARIANTS["v4_combined"]) -->

Four individual variants (each adding one of these rules, plus a fourth baseline-only control) and two ablation combinations were evaluated against DEV before settling on the combined variant; per-model prompt splitting was also considered and rejected after the DEV-side evidence that had motivated it turned out to be noise rather than a real per-model effect.

<!-- source: PROJECT_STATE.md §2 (frozen decision 3) -->

`v4_combined` — baseline plus all three rules, applied identically across all three models — was the prompt carried forward to the frozen TEST evaluation.

### 4.3 Supplementary prompt variants

Two further prompt restructurings were evaluated on DEV only, after the TEST run was frozen, specifically targeting trope and kenning's continued difficulty: a per-element decomposition (one API call per element instead of one call covering all four) and a per-verse granularity restructuring (one API call per verse instead of one call for the whole poem), each described in full in the Results chapter (§6 and §7 respectively). A third, illustrative-only variant added a required natural-language justification field to the output schema; this was never scored against ground truth and is described in the Results chapter (§8) together with the reason it was excluded from the frozen evaluation.

## 5. Models and settings

Three general-purpose, closed-weight LLMs were evaluated: Claude Sonnet 4.6 (Anthropic), GPT-5.4-mini (OpenAI), and Gemini 3.5 Flash (Google). All three were called with temperature 0 and an instruction-only JSON output format — that is, without any provider-native structured-output or JSON-schema enforcement mode — for comparability across the three providers and with the prompting methodology used in earlier phases of this project.

<!-- source: experiments/pilot_3models/config.py (MODELS, TEMPERATURE); experiments/pilot_3models/providers.py -->
| Provider | Model | Temperature |
|---|---|---|
| Anthropic | Claude Sonnet 4.6 (`claude-sonnet-4-6`) | 0.0 |
| OpenAI | GPT-5.4-mini (`gpt-5.4-mini`) | 0.0 |
| Google | Gemini 3.5 Flash (`gemini-3.5-flash`) | 0.0 |

Anthropic's maximum output token allowance was raised from its default (4096) to 16,000 partway through the pilot, after the default was found to silently truncate a response mid-poem on a 50-verse poem; this is noted here because it means the earliest pilot data (before the fix) is not directly comparable to everything reported in this thesis, and only the corrected setting was used for any number reported here.

## 6. Scoring harness

### 6.1 From verse-level to span-level scoring

The earliest version of the evaluation harness scored each verse-element pair as a simple boolean judgment: did the model's `exists` decision for a given element match whether the ground truth contained *any* instance of that element in that verse. This measure produces an artifact on multi-instance verses — a verse with two ground-truth instances of an element is scored identically to a verse with one, and a model that finds one of the two instances (or the wrong one) is scored as fully correct. Re-scoring the same single-poem pilot data that motivated this observation with a corrected, span-aware harness left trope's F1 unchanged (0.222 under both scoring methods) but *lowered* kenning's apparent score (0.154 to 0.105) once multi-instance verses were counted correctly — confirming both that the artifact was real and that its size differs by element, which is why span-level scoring, not verse-level scoring, is used throughout the remainder of this thesis.

<!-- source: PROJECT_STATE.md §3j (original single-poem pilot, old-vs-new scoring comparison); experiments/pilot_3models/span_scoring.py (score_span_level, score_verse_level) -->

### 6.2 Span matching: strict and token-overlap criteria

The span-level harness matches a model's predicted appearance string against the ground-truth span(s) for that verse and element using one of two overlap criteria, both of which are reported for every result in this thesis: a strict criterion, requiring literal substring overlap, and a token-overlap criterion, requiring word-level overlap above a 0.5 threshold (with a partial correction for attached Arabic clitics و/ف). The two criteria are reported side by side rather than one being discarded, because Arabic morphological variation — a predicted span using an inflected form of the same root as the ground-truth span (e.g. النُّوّامِ against نَوَّمُوا) — causes the strict criterion to systematically undercount correct identifications for some elements, most visibly antonymy (Results chapter §4). When a verse contains more than one ground-truth instance of an element, a model's single predicted span is matched against whichever instance it best fits; any remaining ground-truth instances for that verse and element are counted as additional false negatives.

<!-- source: experiments/pilot_3models/span_matching.py (strict_overlap, token_overlap_ratio); experiments/pilot_3models/span_scoring.py (score_span_level, majority_exists_and_appearance) -->

### 6.3 The 2-run majority protocol

Every configuration reported in this thesis — every prompt variant, every model, every poem — was run at least twice, and the majority decision across runs is the primary reported metric; single-run numbers are shown only where explicitly noted, for transparency, and are never the basis for a comparative claim. This protocol was adopted midway through DEV-side prompt tuning, after an early single-run comparison showed Gemini's kenning F1 apparently increasing eightfold (0.056 to 0.433) under one candidate prompt rule. A second run of the same configuration brought the honest, majority-vote figure down to 0.225 — roughly half of the apparent gain was attributable to the variance of a single run rather than to the prompt change. Every subsequent comparison in this thesis, without exception, is reported as a 2-run majority with the raw true-positive/false-positive/false-negative counts shown alongside precision, recall, and F1, specifically so that a result built on a small denominator (for example, an F1 of 0.43 built on 9 true positives against 60 false negatives) remains visibly distinguishable from one built on a larger, more stable count.

<!-- source: PROJECT_STATE.md §6.1 -->

### 6.4 Replication across poems

A single-poem effect can be unstable in the same way a single run can be, and this pilot cycle encountered exactly this problem once, in a supplementary experiment rather than in the frozen TEST evaluation. A per-verse prompting restructuring (Results chapter §7) showed a large apparent kenning improvement for two of three models on one DEV poem (Imru2); before this could be reported as a finding, the same restructuring was re-run on the second DEV poem (Nabigha) specifically to check whether the effect size, not merely its direction, held. It did not for one of the two models, and held or grew for the other (Results chapter §7) — a result that is presented in this thesis as a second, poem-level instance of the same variance problem the 2-run majority protocol was designed to catch at the run level, and as a caution that a single poem's effect size, even under a proper 2-run-majority comparison, should not be treated as generalizable without a second poem's confirmation.

<!-- source: PROJECT_STATE.md §3g (Nabigha replication addendum), §6.9 -->

## 7. Process notes: three corrections made during this pilot cycle

Three episodes during this pilot cycle are recorded here in some detail because each directly motivated a piece of the protocol described above, rather than being incidental errors with no bearing on the final methodology.

**The DEV-to-TEST subtype reversal.** Error analysis on the two DEV poems identified استعارة تمثيلية (unmarked, whole-clause allegory with no lexical marker) as the trope subtype the baseline prompt handled worst, and this hypothesis shaped part of the initial rationale for refining the prompt's boundary rule. At TEST scale — three poems rather than two, and a larger number of instances per subtype — this hypothesis did not hold: استعارة تمثيلية turned out to be the *easiest* trope subtype both before and after the refined prompt (33% missed at baseline, 29% after refinement), while the refined prompt's genuine, TEST-validated wins were on verbal trope (استعارة فعل) and rational trope (مجاز عقلي), two subtypes the DEV-scale analysis had not flagged as the primary target. This is reported in full in the Results chapter (§5) and is the reason this thesis treats any subtype-level pattern observed on a two-poem development sample as provisional until checked against the larger held-out set.

**The single-run artifact.** Described in §6.3 above: an apparent eightfold improvement on one run of one DEV configuration was roughly halved once a second run was obtained, motivating the 2-run majority protocol adopted for every subsequent comparison in this thesis.

**An incomplete-data narrative error.** During the per-verse granularity supplementary experiment (Results chapter §7), a cross-poem replication check was run across all three models, but Anthropic's portion of the second poem's run initially failed for an unrelated infrastructure reason (an exhausted API credit balance). A preliminary write-up of the replication result, based on the two models with data available, concluded that the observed kenning effect was a poem-specific artifact that did not generalize. Once the missing model's data became available, the picture changed: that model's effect size held (and was, if anything, larger on the second poem) while another model's effect size did shrink substantially — a genuinely mixed result, not the uniformly negative one the two-model preliminary version had reported. The corrected version of this finding is what appears in the Results chapter (§7); the earlier, premature version is recorded in the project's internal history as a specific caution against drawing a multi-model comparative conclusion while any planned model's data is still outstanding, independent of and in addition to the more general lesson about single-poem effect sizes described in §6.4 above.

<!-- source: PROJECT_STATE.md §6.9 -->
