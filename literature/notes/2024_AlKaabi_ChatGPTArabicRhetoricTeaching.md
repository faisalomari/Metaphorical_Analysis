# Al Kaabi, Abubkr, Abdeddayem, Bin Haidara & Almaamari (2024) — Developing the teaching Arabic rhetoric: A comparative analysis of artificial intelligence and traditional hermeneutical approaches

Journal of Infrastructure, Policy and Development, 8(15), 9925, https://doi.org/10.24294/jipd9925 — PDF: `literature/related_work/non_dhq/2024_AlKaabi_ChatGPTArabicRhetoricTeaching.pdf`
Read: full paper including references. Page refs below are PDF pages. "Not reported" means I did not find it in the paper.

## Research question and task definition
- "What are ChatGPT's capabilities and limitations in understanding classical Arabic rhetoric compared to traditional methods with a specific focus on cultural and contextual elements?" (p.2).
- Task: input 8 classical Arabic rhetorical examples (metaphor, simile, metonymy, loose metaphor, poetry, abstraction) into ChatGPT, compare its interpretation against classical scholarly hermeneutics (chiefly al-Jurjani's *Dala'il al-I'jaz*, also Ibn al-Athir, al-Sakkaki) (p.2, p.4).
- Secondary framing: the paper also positions itself as an AI-in-higher-education-policy paper (infrastructure, governance, faculty training) layered on top of the rhetoric comparison — the two threads (close textual comparison vs. institutional AI-policy recommendations) are not tightly integrated in the paper's structure.

## Data
- 8 hand-picked rhetorical examples, not a corpus: (1) "Zayd is a lion" (metaphor), (2) "A random/unknown person is full of ash" (metonymy), (3) "Zayd is like the sea" (simile), (4) "Flowing Rivers" (loose metaphor), (5) a line of classical Arabic poetry on death ("sinks its claws... amulets ineffective"), (6) "She is a late morning sleeper" / "He has a long sword-strap" (metonymy), (7) "He is the sea, from which side did you come to it" (poem), (8) "The moon became between us" (abstraction) (p.4).
- Selection criteria stated: diversity of device type, historical significance (cited by classical rhetoricians), semantic/cultural complexity (p.4). No corpus size beyond these 8 examples — not reported for any larger dataset.

## Annotation scheme
- No formal annotation scheme / no inter-annotator agreement — comparison is a narrative qualitative contrast between (a) the classical scholarly interpretation as found in al-Jurjani/Ibn al-Athir/al-Sakkaki and (b) ChatGPT's single generated interpretation, example by example (p.4, Methodology).
- Who ran the comparison / how many researchers: not reported explicitly beyond general author contributions statement; not reported whether multiple authors independently judged ChatGPT's outputs or whether one person conducted the comparison.
- No numeric scoring of any kind (no precision/recall/F1/accuracy) — purely qualitative, descriptive matching.

## Method
- "Qualitative...comparative analytical methodology": classical examples selected, input into ChatGPT, outputs compared narratively against classical hermeneutics (p.4).
- ChatGPT version/date, prompt wording, and number of queries per example are not reported. Not reported whether the same prompt template was used for all 8 examples or how follow-up questions (e.g. "two consecutive instances" for the death-poem example, p.7) were phrased.
- No code, no public repository, no reproducibility materials referenced.

## Evaluation
- No quantitative metrics anywhere in the paper (no P/R/F1, no accuracy, no agreement score) — purely descriptive per-example comparison (Section 4, p.5–9) plus a prose "general comparison of interpretations" (Section 4.9, p.9) and a bullet "Summary of the findings" (Section 5.5, p.12–13).
- Example of the comparison format: for "Zayd is a lion," the paper states al-Jurjani sees the metaphor as a "psychological and aesthetic experience" of identification, not mere attribute transfer, while "ChatGPT provided a straightforward interpretation that focused on the superficial level of meaning, connecting the lion to bravery and strength" (p.5).
- One example (the death-poem / "claws" metaphor, item 5) is treated as a partial exception: the paper states ChatGPT gave "a convincing and direct interpretation, with greater detail" across two queries, covering both hemistiches and offering a "general meaning" gloss broadly matching the traditional al-Sakkaki/Qasim-and-Deeb reading, though without naming the specific rhetorical term "metaphor by metonymy" (al-isti'ārah bil-kināyah) (p.7).

## Difficulties and error analysis
- Recurring pattern across all 8 examples except the death-poem one: ChatGPT gives the lexically/surface-correct reading but misses deeper cultural/psychological/symbolic layers the classical scholar identifies — e.g. for "Zayd is like the sea," ChatGPT gives only "generosity" where al-Jurjani's reading also carries "mystery, depth, and stability" (p.6); for "A person full of ash" (metonymy for generosity, per Ibn al-Athir, tied to the custom of lighting cooking fires for guests), ChatGPT instead suggests it "could indicate activity or a lot of work" — read by the authors as a wrong interpretation, not merely a shallow one (p.5).
- For "flowing rivers" (loose metaphor), ChatGPT reportedly gave a fully literal reading (actual water flow), missing the metaphorical reading entirely (p.6).
- Authors' general diagnosis: "AI relies on analyzing linguistic patterns in their apparent meanings," unable to access the "psychological and social depths" that require cultural/historical context (p.9).
- One item (metonymy "he has a long sword-strap" → tall stature) is reported as ChatGPT correctly inferring the cultural/logical chain without using the technical term "metonymy" (p.8).

## Limitations
Authors' own (Section 5.2, p.10, and Section 5.3, p.11–12):
- AI "relies on limited data models on which it is trained," leading to superficial readings of complex examples, citing Margolis (2019) — see citation-verification section below regarding this specific source.
- Non-native learners may find ChatGPT's explanations insufficiently detailed/nuanced.
- Experts caution against relying solely on AI tools; deep rhetorical understanding "requires human intervention."
I notice (not stated by the authors):
- Sample size of 8 hand-picked examples, chosen partly because they are canonical textbook cases already discussed at length by al-Jurjani et al. — this is closer to an illustrative case-study than a systematic evaluation, and the examples are not drawn from a held-out or blind set.
- No quantitative metric of any kind, so "basic/superficial vs. deep" is an entirely qualitative judgment made by the same authors who selected the examples.
- No control for prompt wording, ChatGPT model version, sampling temperature, or number of trials per example.
- The paper's own literature review leans heavily on a cluster of citations (Smith 2022, Jones 2020, Margolis 2019, Wright 2021, Al-Ghamdi 2021, Al-Tamimi 2019, Al-Khawli 2018) that could not be independently verified — see citation-verification section below. This materially weakens confidence in several claims in Sections 2, 5.1, 5.2, and 5.3 that are attributed to these specific sources (e.g. the claim that "AI relies on limited data models," attributed to Margolis 2019, p.10).

## Reusable ideas for our paper
- The only found non-DHQ precedent combining ChatGPT + classical Arabic rhetoric + direct comparison against a named classical authority (al-Jurjani's *Dala'il al-I'jaz*) — directly supports a "small-scale, qualitative, under-studied" framing for the gap this project addresses.
- Its own finding — that LLMs give linguistically correct but culturally/psychologically shallow readings of metaphor/simile/metonymy — is a useful qualitative companion to our own quantitative span-level findings; we can cite it as corroborating (at small scale, qualitatively) a "surface-correct, depth-deficient" pattern, while being explicit about its lack of metrics and its citation-integrity issues.
- Negative methodological exemplar: this paper is a clear illustration of why our own project's "report raw TP/FP/FN, 2 runs minimum, DEV/TEST discipline" standards matter — this paper has none of these and its qualitative claims (e.g. "ChatGPT struggles with cultural depth") cannot be directly quantified or reproduced from what is reported.
- Caution for how we cite this paper ourselves: given the citation-verification findings below, we should cite only its own methodology/findings/examples directly, and avoid repeating any claim it attributes to Smith/Jones/Margolis/Wright/Al-Ghamdi(2021)/Al-Tamimi, since those underlying sources could not be confirmed to exist as described.

## Verbatim quotes (each under 15 words; PDF page)
- "AI tools...currently serve best as supplementary teaching aids rather than replacements" — p.1 (abstract)
- "it lacks the psychological and cultural dimensions emphasized by Al-Jurjani" — p.2
- "AI relies on analyzing linguistic patterns in their apparent meanings" — p.9

## Citation verification check

As instructed, I went through Al Kaabi et al.'s own reference list (pp.14–15 of the PDF) looking for citations with generic author names, vague/non-indexed journal titles, no DOI, and not findable via a web search for the exact title + author. I ran targeted web searches for the most load-bearing of these (the ones whose claims are actually used in the paper's argument, not merely background filler). Searches used the exact citation text as printed.

**Citations I could NOT verify (searched, no independent source found):**

1. **Smith, J. (2022). "Artificial Intelligence in Language Education." *Journal of Educational Technology*, 45(3), 22-47.** — Cited 3 times in the paper (pp.3, 9, 12) to support claims that "AI tools are helpful for quick analysis" and that ChatGPT "successfully analyzed basic comparisons." Web search for the exact title/author/journal/volume returned no matching article; only unrelated AI-in-language-education papers from other authors and years. "Journal of Educational Technology" as printed is a generic-sounding title; no identifiable DOI or publisher given in the reference.

2. **Jones, P. (2020). "AI in Arabic Language Teaching: Opportunities and Challenges." *International Journal of Educational Technology*, 33(2), 115-130.** — Cited 3 times (pp.10, 11) including as the basis for specific recommendations ("Jones (2020) suggests that technology should be integrated with the hermeneutics of rhetoricians' traditions"). Web search returned several *differently-titled* and differently-authored papers on AI + Arabic language teaching, none matching this specific citation. No DOI given.

3. **Margolis, E. (2019). "Cultural Implications in AI-driven Language Processing." *Language and Society*, 12(4), 78-90.** — Cited twice (p.10) to support the claim that "AI relies on limited data models on which it is trained," a claim used in the paper's own Limitations section. Web search returned no matching article under this title/author/journal; "Language and Society" as given does not match the name of the well-known journal *Language in Society* (note the discrepancy), and no DOI is given.

4. **Wright, M. (2021). "Teaching Classical Arabic Rhetoric with AI: Methods and Implications." *Journal of Language & AI Education*, 14(1), 45-70.** — Listed in the reference list but, notably, I could not find this citation actually invoked anywhere in the paper's body text (it appears to be an uncited reference-list entry). Web search returned no matching article; "Journal of Language & AI Education" does not appear to be an indexed journal.

5. **Al-Ghamdi, R. (2021). "Natural Language Processing and Arabic Rhetoric: A Comparative Study." *AI & Humanities Journal*, 19(2), 88-105.** — Cited twice (pp.4, 10, 12) for claims that AI "can improve the educational process by providing quick and comprehensive analysis of texts" and that deep neural network techniques could enhance multi-dimensional interpretation. Web search returned no independent source; the only pages mentioning this exact citation are copies/indexes of the Al Kaabi et al. (2024) paper itself (i.e., the citation is only found reflected back from this paper's own reference list, not confirmed elsewhere). "AI & Humanities Journal" does not appear to be an indexed/discoverable journal.

6. **Al-Tamimi, A. (2019). "Applications of Artificial Intelligence in Arabic Text Processing." King Saud University Publishing.** — Cited once (p.11, in-text as a general claim about Arabic NLP). Web search returned no matching title from King Saud University Publishing or elsewhere.

**Additional lower-confidence/unverified entries (not individually web-searched, flagged only by inspection):** several further reference-list entries are self-published-looking Arabic-language books cited without DOIs or ISBNs — Al-Ghamdi, A. (2020) *Arabic Rhetoric and Artificial Intelligence Applications* (Dar Al-Manara Publishing); Al-Khawli, M. (2018) *Artificial Intelligence and Its Applications in the Arabic Language* (Dar Al-Fikr Al-Arabi); Al-Tamimi again as above; Al-Majri, M. (2017) *Rhetorical Interpretation in the Abbasid Era* (Dar Al-Fikr Al-Urduni); Al-Haidari, H. (2005) *The Science of Rhetoric and Its Impact on Linguistic Interpretation* (Dar Al-Ma'rifa). Books from named Arabic academic publishers are plausible in principle and harder to verify by web search than journal articles (no DOI/indexing expected), so I have not flagged these as "unverifiable" in the same way as items 1–6 — they are simply outside what a web search can confirm either way. I did not attempt to verify the classical primary sources (al-Jurjani 1980, al-Sakkaki 1987/1992, Ibn al-Athir 1990, al-Qazwini 1998, Ibn Jinni 1952, al-Sharif al-Radi 1998, Rasheeq 2001, al-Andalusi 2006) as these are well-known classical Arabic rhetoric texts with real, independently verifiable editions.

**Citations confirmed as real (for contrast):** the paper's other modern citations — e.g. Adewale et al. (2024, *Heliyon*, DOI given), Alaqlobi et al. (2024, *Cogent Arts & Humanities*, DOI given), Alqahtani & Wafula (2024, *Innovative Higher Education*, DOI given), Chan (2023, *International Journal of Educational Technology in Higher Education*), Chugh et al. (2023, *Education and Information Technologies*), Naseer et al. (2024, *Heliyon*, DOI given), Wang et al. (2024, *Expert Systems With Applications*, DOI given), and the authors' own prior paper Al-Kaabi et al. (2024c, *Journal of Language Teaching and Research*, DOI given) — all carry real DOIs/identifiable venues and are consistent with genuine publications, unlike items 1–6 above.
