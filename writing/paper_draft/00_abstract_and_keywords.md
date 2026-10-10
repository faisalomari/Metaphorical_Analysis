# Abstract, Teaser, and Keywords

## Abstract (DHQ `<dhq:abstract>`)

Rule-based identification of rhetorical elements in classical Arabic poetry reaches high precision and recall overall, but only by excluding metaphor and periphrasis (كناية) as too semantically demanding for pattern matching (Abd Alhadi, Hussein and Kuflik, 2023). This paper evaluates whether large language models can take up exactly the elements that earlier system named as out of reach. Three general-purpose models (Claude Sonnet 4.6, GPT-5.4-mini, Gemini 3.5 Flash) were evaluated zero-shot, at the span level, on four elements — trope (مجاز), simile (تشبيه), periphrasis (كناية), and antithesis (طباق) — against one domain expert's manual annotation of five classical Arabic poems, three held out as a frozen test set. Simile, whose definition names an explicit comparative particle, reaches strict-criterion F1 of 0.65–0.73 for every model; periphrasis never exceeds 0.176 anywhere in the primary evaluation. Antithesis proved locatable but systematically over-claimed, a precision failure rather than a recall one. Supplementary experiments show periphrasis is reachable, though not yet reliably decidable, under a free-form reasoning format, and that several rhetorical subtypes are strikingly sensitive to which model is queried and how many worked examples anchor its reading of a category. The paper's contribution is diagnostic: it characterizes where, and under what conditions, large language models can currently be trusted to identify named classical Arabic rhetorical elements, rather than reporting a single performance verdict.

*(Word count: approximately 215 words — within the 150–250-word target range.)*

## Teaser (DHQ `<dhq:teaser>`)

Large language models identify explicit similes in classical Arabic poetry fairly well, but periphrasis — the element a predecessor rule-based system gave up on as too semantic to automate — remains out of reach for every model and prompt tried here.

## Keywords

### Author keywords (`#authorial_keywords`, free text, no controlled vocabulary)

large language models; classical Arabic poetry; rhetorical analysis; balāgha; periphrasis; metaphor; digital humanities; annotation difficulty; span-level evaluation; prompt sensitivity

### DHQ controlled-vocabulary keywords (`#dhq_keywords`)

`[TBD]`. DHQ's own controlled keyword taxonomy is maintained at `https://dhq.digitalhumanities.org/common/xml/taxonomy.xml`; per `literature/notes/dhq_format_guide.md` (part (a), "Could not verify / open questions"), that file returned as raw XML with no readable body in the browser text-extraction tool used during this project's format research and was not parsed, so the current list of controlled terms is not available in this project's files. Likely candidate categories, based on the taxonomy's evident domain areas and this paper's subject matter — Arabic/Middle Eastern studies, computational linguistics, text analysis, machine learning — should be confirmed against the live taxonomy file at submission time, not assumed from this note.

### Project keywords (`#project_keywords`)

`[TBD]` — DHQ's template describes this field as "in development" and likely optional; no project-registry entry exists for this work at the time of writing.
