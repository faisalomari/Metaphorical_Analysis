# DHQ gap check: "no DHQ paper benchmarks LLMs on rhetorical elements"

Run 2026-10-07 with DHQ's own site search (`https://dhq.digitalhumanities.org/vol/search.html?q=<term>`), executed in the browser pane. The search is client-side (staticSearch). It matches word stems, so `prompt`, `prompts` and `prompting` return the same 224 documents, and `transformer` is stemmed to *transform* (629 documents, noise). An unquoted multi-word query matches any of its words (`large language model` = 974 documents), so multi-word terms were rerun as exact phrases in quotes. Corpus searched: all DHQ volumes 1 to 20, including the 20.3 preview issue (index as of the search date). Search hits count issue front-matter pages (`index.html`, `bios.html`) too; these are marked below and are not articles.

## Queries and hit counts

| Query | Docs found | Relevant to the gap? |
|:--|--:|:--|
| GPT | 13 | Two articles substantively about GPT (Hua & Raley 2020, 2023). Rest incidental. None on rhetoric. |
| ChatGPT | 21 | Incidental mentions or critical-code-studies/pedagogy pieces. None on rhetoric. |
| "large language model" | 6 | None on rhetoric. |
| "large language models" | 17 | None on rhetoric. (Gutman 2024 only suggests LLMs as future work.) |
| LLM | 11 | None on rhetoric. |
| LLMs | 21 | None on rhetoric. |
| "generative AI" | 18 | Conceptual, pedagogy or ethics pieces. None on rhetoric. |
| "generative artificial intelligence" | 1 | True Digital Poiesis (conceptual framework). Not relevant. |
| prompt / prompts / prompting | 224 | Noise (classroom prompts, game prompts). Of those also matching a figurative term (>=3 hits), none is about LLM prompting for rhetoric. |
| BERT | 29 | Bender 2023 (DistilBERT), Gutman 2024 (DistilBERT), Fuchs 2025 (BEREL), Tarkka 2026, plus incidental. None benchmarks rhetorical elements. |
| transformer / transformers | 629 | Stemming noise (XSLT, "transform"). Not usable as a signal. |
| zero-shot | 3 | Sánchez-Salido 2024 (NER on Spanish newspapers), Glass 2026 (CLIP image tagging), SILKNOW data model (1 hit). None on rhetoric. |
| "zero shot" | 0 | none |
| few-shot | 6 | Same two, plus an image-classification CNN paper (19/3/000789), Compounded Mediation, Hua & Raley 2020, bios page. None on rhetoric. |
| "few shot" | 0 | none |
| "figurative language" | 13 | Real hits: Gutman 2024 (39 hits), Münz-Manor 2023 (13). Others incidental or issue pages. |
| metaphor / metaphors | 283 | Mostly metaphor as a theme. Intersected with ML terms below. |
| irony / ironic | 65 / 123 | Theme, not detection. Intersected with ML terms below. |
| rhetorical | 323 | Mostly rhetoric studies and "rhetorical" used loosely. Intersected with ML terms below. |
| trope / tropes | 68 | Same. |
| simile / similes | 10 | Abd Alhadi 2023 (23 hits), Münz-Manor 2023 (6), libEscansión 2024 (1), Schropp 2024 (4, quotations), plus older non-ML articles. |
| balagha | 0 | none |
| balāgha | 1 | Abd Alhadi 2023 (6 hits) |
| balaghah | 0 | none |
| "rhetorical figure" | 1 | Abd Alhadi 2023 (2 hits) |
| "figures of speech" | 4 | Münz-Manor 2023, Abd Alhadi 2023, a 2023 issue page, Varieties of Digital Literary Studies (2020, non-ML). |
| "language model" | 33 | Used in the cross-check below. |

Not run: `metonymy` and other trope names beyond the list you gave.

## Cross-check: ML-term documents that also match a figurative term

I intersected documents matching any of GPT, ChatGPT, LLM(s), "large language model(s)", "generative AI", BERT, zero-shot, few-shot or "language model" with documents matching figurative language, metaphor, irony, rhetorical, trope, simile or "figures of speech". Result: 49 hits (issue and bios pages included). I checked the title for all of them and the DHQ abstract for the ones that looked plausible. Metadata for these was read from the article pages.

Articles about text analysis or NLP, with what they do (none benchmarks LLMs on rhetorical elements):

| Article | Authors | Year, vol.issue | URL id | What it does | Status |
|:--|:--|:--|:--|:--|:--|
| Automatic Identification of Rhetorical Elements in classical Arabic Poetry | Abd Alhadi, Hussein, Kuflik | 2023, 17.2 | 000673 | Rule-based identification of 20 rhetorical elements, no ML or LLM | in index, read |
| A Network Analysis of Figurative Topic Classification: Timon of Athens | Gutman | 2024, 18.3 | 000753 | DistilBERT topic classifier on manually extracted figurative instances | in index, read |
| Category Development ... Pragmalinguistic Annotation and Machine Learning | Bender et al. | 2023, 17.3 | 000720 | Naive Bayes vs DistilBERT on discourse referencing, not rhetorical figures | in index, read |
| Visualization of Categorization | Münz-Manor, Marienberg-Milikowsky | 2023, 17.3 | 000703 | Manual figure-of-speech annotation, no system evaluated | in index, read |
| How to Do Things with Deep Learning Code | Hua, Raley | 2023, 17.2 | 000684 | Critical reading of GPT-2/BERT code, no benchmark | in index |
| Playing With Unicorns: AI Dungeon and Citizen NLP | Hua, Raley | 2020, 14.4 | 000533 | Analysis of GPT-2 generated text in a game | in index |
| Do all politicians sound the same? | Tarkka et al. | 2026, 20.1 | 000839 | Model explanations vs human responses on political text | in index |
| Counting Feeling: Affect Theory and Sentiment Analysis in TextBlob | Moro | 2026, 20.1 | 000825 | Critical code reading of a sentiment tool | in index |
| Genre 2.0? Embedding-Based Cluster Analysis ... Medieval Hebrew | Fuchs | 2025, 19.3 | 000806 | Embeddings and clustering of genre | in index |
| Sentiment Analysis in Literary Studies. A Critical Survey | Rebora | 2023, 17.2 | 000691 | Survey of sentiment tools | in index |
| Responsible AI and the Middle Ages | Demelas | 2026, 20.3 | 000874 | Detoxify toxicity model on 2,605 sentences, finds false negatives; not rhetorical | in index, no PDF |
| Visions in the Machine: Automated Tagging of the William Blake Archive | Glass | 2026, 20.2 | 000869 | CLIP/FAISS tagging of 200 images with three difficulty tiers; images, not text | **new, added** |
| Seeking Information in Spanish Historical Newspapers (Diario de Madrid) | Sánchez-Salido, Menta, García-Serrano | 2024, 17.4 | 000735 | NER with transfer and zero/few-shot setups on OCR text; not rhetorical | seen, not added |
| True Digital Poiesis | Hasty et al. | 2026, 20.3 | 000876 | Conceptual framework for generative AI in teaching history | seen, not added |
| Infrastructures of Listening: ManoWhisper | Ruest et al. | 2026, 20.1 | 000860 | Podcast transcription and analysis pipeline | seen, not added |
| Striving towards automated writing | Hongisto | 2026, 20.1 | 000851 | Rhetoric of authorship in story-generation papers (a discourse analysis, not rhetorical-element identification) | seen, not added |
| From Semi-structured Text to Tangible Categories | Resch, Rastinger, Kirchmair | 2023, 17.3 | 000711 | NER annotation of death lists, GPT-4 mentioned | seen, not added |
| Project Quintessence | Pizelo et al. | 2023, 17.3 | 000709 | Corpus explorer using unsupervised methods | seen, not added |
| Keywords in Digital Humanities | Blanke, Papadopoulou | 2025, 19.3 | 000804 | Keyword extraction and ML | seen, not added |
| Slow, Painful and Expensive | Warner et al. | 2025, 19.3 | 000790 | Corpus construction challenges | seen, not added |
| libEscansión | Sanz-Lázaro | 2024, 18.3 | 000739 | Rule-based metrical scansion of Spanish verse; poetry, but meter, not rhetoric | seen, not added |
| Computational Paremiology | Davis et al. | 2023, 17.2 | 000676 | Proverb frequencies over time; no LLM | seen, not added |

The remaining ML-term and figurative-term hits are articles on critical code studies, pedagogy, ethics, infrastructure or media (for example 17/2/000713, 20/1/000848, 19/3/000803, 20/2/000853, 18/2/000742, 20/1/000857, 19/1/000771). I triaged these by title and hit context only and did not read their abstracts; I did not find anything indicating a rhetorical-element task, but this part is title-level screening.

Metadata for the "seen, not added" rows comes from the DHQ article pages. Authors and dates were not re-verified beyond that.

## Added to the index and downloaded

- Glass, *Visions in the Machine: Automated Tagging of the William Blake Archive*, DHQ 20.2 (2026), https://dhq.digitalhumanities.org/vol/20/2/000869/000869.html. Background, 5.3. Reason: its three-tier difficulty framing for AI tagging (object, motif, iconography) is a methodological analogue for a difficulty taxonomy, though it uses CLIP on images, not an LLM on text. PDF: `literature/related_work/dhq/2026_Glass_AutomatedTaggingWilliamBlakeArchive.pdf` (30 pages, title page checked; the PDF says DOI pending).
- Nothing else was added, and no existing file was redownloaded.

## Verdict: gap confirmed, with narrow wording

I found no DHQ article that evaluates an LLM, GPT-style model or other generative model on identifying rhetorical or figurative elements in text. The closest DHQ items are:

- Abd Alhadi et al. 2023: identifies rhetorical elements, but with rule-based NLP and no LLM.
- Gutman 2024: classifies topics of figurative instances with DistilBERT, but the instances were extracted manually and the paper only proposes testing LLMs (Llama, Gemini, ChatGPT) as future work (p.13).
- Bender et al. 2023: BERT-based classification of pragmalinguistic categories on German text, which is neither rhetorical figures nor an LLM benchmark.
- Hua & Raley 2020 and 2023: study GPT-2 qualitatively; no rhetorical-element task.

Suggested wording for the paper: "A search of Digital Humanities Quarterly (all volumes through 20.3) found no study that benchmarks large language models on identifying rhetorical elements; the closest work uses rule-based methods (Abd Alhadi et al. 2023) or a BERT-family classifier on manually extracted figurative instances (Gutman 2024)."

## What this does and does not support

- It supports a claim about DHQ only. It says nothing about other venues.
- Full-text search covers the DHQ site index as of 2026-10-07. Articles that discuss the topic without using the searched words (for example Arabic terms in other transliterations such as `balaghah` or `balaga`) could be missed. `balagha` and `balaghah` returned 0; only `balāgha` returned a hit.
- The stemming search is noisy for `prompt` and `transformer`, so those two queries give weak evidence either way.
- Only titles and abstracts (plus hit context) were checked for articles outside the five deep-read papers.
- The word "benchmark" has not been searched as a term; the verdict rests on reading what each candidate does, not on that word.
