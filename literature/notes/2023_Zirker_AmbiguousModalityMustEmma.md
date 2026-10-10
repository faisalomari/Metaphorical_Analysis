# Zirker & Göggelmann (2023) — Case Study: Annotating the ambiguous modality of "must" in Jane Austen's Emma

DHQ 17(3), https://dhq.digitalhumanities.org/vol/17/3/000727/000727.html — PDF: `literature/related_work/dhq/2023_Zirker_AmbiguousModalityMustEmma.pdf`
Read: all main text and footnotes (p.1–14, 16–17) and the appendix guidelines in part (p.14–15); references not read. Page refs are PDF pages; "¶" is DHQ's paragraph number. "Not reported" means not found.

**Scoping fact:** this is a human annotation study in a teaching context. It contains no machine-learning or LLM component.

## Research question and task definition
- Can the ambiguity of the modal verb "must" (epistemic / deontic / bouletic) and the ambiguity of voice (narrator vs character; speaker vs focalizer) in *Emma* be annotated reliably, and what difficulties and mistakes appear when student groups do it? (abstract; p.1–2 ¶1–3)
- Task: find every instance of "must" and tag (a) the figure (narrator or character) that is speaker or focalizer, (b) its role, (c) the modality, with "maximal annotation": if unsure, annotate all possibilities rather than disambiguate (p.4–5 ¶17–18).
- Second aim: use annotation as a teaching tool and compare two tools (CATMA, CorefAnnotator) (p.3 ¶15).

## Data
- Text: Jane Austen, *Emma* (1816), English; 571 occurrences of "must" in the novel (p.3 ¶11). Annotated chapters contain 323 occurrences: 156 in volume 1, 167 in volume 3 (p.8–9 ¶32–36). Chapter 1: "must" occurs 16 times (p.13 ¶52); chapters 1–3: 22 times (p.11 ¶40).
- Annotators: 19 students of a "Digital Methods in Literary Studies" class: 6 with CATMA (two groups of three) and 13 with CorefAnnotator (three groups of three, one of four) (p.3–4 ¶15–16; Table 1 lists chapter packages per group).

## Annotation scheme
- Tags: figure (character or narrator), role (speaker, focalizer; narrator is speaker by default), modality (epistemic, deontic, bouletic; multiple allowed) (p.4–5 ¶17–18; Appendix p.14).
- Guidelines were derived from a close reading of the novel and revised during the term with student feedback, plus an FAQ section (p.4–5 ¶17–18).
- Tool configuration differed: tags fixed in advance in CATMA; annotators could add tags in CorefAnnotator (p.6 ¶23).
- Inter-annotator agreement (CorefAnnotator groups, chapters 1–3): Fleiss kappa figure = 0.67, role = 0.5, modality = 0.16 (printed with decimal commas) (p.11 ¶43). Footnote 21 (p.16) reads these on the Landis and Koch scale as good, moderate and poor agreement. A pairwise-agreement analysis on 22 instances shows the loss of agreement when modality is added (Figure 6, p.11 ¶40–42).
- Gold standard: none; the authors say one "would have to be developed" (p.5 ¶20).

## Method
- Individual annotation first, then group discussion to a joint result (done by the CorefAnnotator groups only; the CATMA groups never negotiated, which only came to light at the end of term) (p.4 ¶16).
- Analysis is descriptive: counts of technical flaws per tool (Table 2, p.5), comparison of annotations of specific instances (Tables 3–6, p.6–7, p.12), counts of annotations per instance (Figures 1–5, p.8–10), kappa and pairwise agreement (p.11).
- The CATMA groups' results were set aside for the detailed analysis because they mainly applied the guidelines wrongly and had unexplained gaps (p.6 ¶25).

## Evaluation
- No accuracy, precision or recall against a gold standard (none exists). Agreement is the only quantitative measure: Fleiss kappa 0.67 / 0.5 / 0.16 for figure / role / modality, on 22 instances and three groups (p.11 ¶40–43).
- Technical flaws: 255 (CATMA) vs 195 (CorefAnnotator); 224 of the CATMA ones are annotations of a following space, mostly by one student (Table 2, p.5).
- Baselines, models, automatic methods: not applicable / not reported.

## Difficulties and error analysis (central content of the paper)
- Modality is the hardest dimension: figure and role annotation are comparatively straightforward (partly derivable from each other), modality is "clearly inferior" in agreement (p.11 ¶42).
- Worked examples where groups diverge: the first "must" (great must be the difference), "We must begin, we must go and pay our wedding-visit" (bouletic/deontic), and "his second must shew him" (narrator vs Mr Weston; deontic/epistemic/bouletic) (p.6–7, p.12 ¶25–48).
- Students tended to disambiguate rather than annotate all readings, and often could not accept multiple meanings of a common modal verb (p.7 ¶31; p.13 ¶52).
- Students overlooked instances (e.g. in direct speech), stopped annotating partway (two CATMA students), or ignored guideline defaults (narrator as focalizer) (p.8–10 ¶32–37; p.13 ¶51–52).
- A misconception that annotating makes reading the whole novel unnecessary, so context was missed (p.5 ¶19; p.14).
- The authors speak of an "ambiguity of ambiguity": hard to decide which modalities are actualised in context (p.13 ¶51). Ambiguity may produce irony and meta-narrative effects (p.13 ¶51).

## Limitations
Authors' own: student annotations are "not really of any use" for quantitative analysis; expert teams needed; no gold standard; the CATMA groups' data unusable; guideline compliance varied; only one phenomenon and one novel (p.13 ¶50–51).
I notice:
- Agreement is computed on a very small sample (22 instances, three groups), so the kappa values are rough.
- Annotators are novices, so the kappa for modality (0.16) may reflect training and motivation as much as the inherent difficulty of the phenomenon; the paper acknowledges teaching issues but cannot separate the two.
- Tool and group are confounded (different groups, different chapter packages, different tag-configuration).
- The "maximal annotation" instruction makes agreement hard to define (multi-label sets) and the paper does not say how partial overlaps were scored.

## Reusable ideas for our paper
- A ready model for operationalising "challenging": measure difficulty by inter-annotator agreement per dimension (here, figure 0.67 > role 0.5 > modality 0.16) and by how often annotators disagree on the same item. We could tag each verse by expert agreement and report LLM performance by difficulty tier.
- Annotating ambiguous phenomena: allow multi-label annotation and record every plausible reading instead of forcing one (relevant to rhetorical elements that overlap, e.g. trope subtypes).
- Documentation practice worth copying: guidelines with theory background, defaults (e.g. "narrator = speaker"), FAQ and revision history.
- Best-practice list for annotating complex literary phenomena (p.13–14 ¶53): check early results, work in teams, start with simple examples, require contextual knowledge. Supports using expert annotators and a pilot.
- Caution on the interpretation of low agreement: distinguish phenomenon difficulty from annotator training.
- The paper links ambiguity to irony and narrative strategy; a possible qualitative angle for error analysis of LLM mistakes.

## Verbatim quotes (each under 15 words; PDF page, ¶)
- "an ambiguity of ambiguity" — p.13, ¶51
- "the complexity of the material makes the annotation by expert teams necessary" — p.13, ¶51
- "no guarantor of their correct application" — p.13, ¶53
