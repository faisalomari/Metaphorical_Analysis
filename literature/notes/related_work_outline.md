# Related-work section plan (DHQ paper)

Built 2026-10-07 from `literature/notes/dhq_format_guide.md` §(d) (recommended paper outline) and `literature/CITATION_PLAN.md` (which papers support which section). This is a structural plan only — subsection headings, which cited works go where, and a 2–3 sentence summary of each subsection's argument. No full prose yet. Terminology follows `GLOSSARY.md` (antithesis, periphrasis, metaphor/analogy/metonymy as مجاز subtypes) since this is new writing.

Section heading follows Abd Alhadi et al.'s own phrasing per the format guide: **"Background and Related Work."**

---

## 2a. The balagha inventory and classical Arabic poetry corpus context

**Cited:** Harb 2020 (Must), Fontana 2025 (Should), Qarah 2024 / AraPoemBERT (Optional)

**Argument:** Classical Arabic rhetoric (balagha) is a centuries-old, formally codified system (al-Jurjānī's *Asrār al-Balāgha*, al-Sakkākī's tripartite maʿānī/bayān/badīʿ taxonomy in *Miftāḥ al-ʿUlūm*) that the 20-element inventory this paper evaluates is drawn from — Harb and Fontana are cited as reliable modern English-language scholarly anchors for this tradition rather than relying on unverifiable direct medieval-text citation. Qarah's AraPoemBERT shows that large annotated NLP resources already exist for classical Arabic poetry's *formal* features (meter, rhyme) — a one-line contrast establishing that the *rhetorical/semantic* layer remains comparatively under-resourced even as other poetry-NLP tasks mature.

## 2b. Prior automatic approaches to rhetorical-element identification

**Cited:** Abd Alhadi, Hussein & Kuflik 2023 (Must — repeat citation from §1, DHQ permits this)

**Argument:** Abd Alhadi et al. 2023 is the direct predecessor and baseline this paper extends: a rule-based system on the same REI poetry corpus, scoring P 0.918/R 0.902/F 0.906 but explicitly excluding metaphor and periphrasis (kinaya) as "too semantic" for rule-based matching. This paper exists specifically to fill the gap Abd Alhadi et al. name themselves as out of reach for their own method.

## 2c. DH precedents for annotation-category development and difficulty

**Cited:** Bender, Becker, Kiemes & Müller 2023 (Must), Zirker & Göggelmann 2023 (Must), Münz-Manor & Marienberg-Milikowsky 2023 (Should), Gutman 2024 (Should)

**Argument:** DHQ's own annotation-methodology literature already treats category difficulty and annotator disagreement as something to measure empirically rather than assume — Bender et al.'s finding that the *simplest*-looking category got the *lowest* kappa is a direct structural parallel to this paper's own periphrasis-type difficulty; Zirker & Göggelmann and Münz-Manor & Marienberg-Milikowsky further model treating ambiguity, and multiple legitimate annotator readings, as data rather than noise. Gutman 2024 closes the loop by explicitly naming LLMs (Llama/Gemini/ChatGPT) as untested future work for exactly this kind of figurative-language classification task — this paper is, in effect, that future work carried out for a different (classical Arabic, not early-modern English) domain.

## 2d. LLM-in-DH literature (methodological framing)

**Cited:** Tarkka, Elo, Ginter & Laippala 2026 (Should), Dobson 2021 (Optional)

**Argument:** Tarkka et al. 2026 is the closest DHQ precedent in genre — a rigorous, recently-published model-vs-human comparison with full P/R/F1 reporting and an explanation-analysis layer — offering a structural model for this paper's own Results/Discussion split. Dobson 2021 supplies the cautious, non-overclaiming register DHQ favors when describing what a high model score does or does not demonstrate, relevant to this paper's own interpretation of its easiest-scoring elements.

## 2e. LLM benchmarks on figurative/rhetorical language beyond DH

**Cited:** Fuoli, Huang, Littlemore, Turner & Wilding 2025 (Must), Reimann & Scheffler 2025 (Must), Balestrucci et al. 2025 (Must), Hicke & Kristensen-McLachlan 2024 (Should), Ye et al. 2026 (Should), Kühn, Mitrović & Granitzer 2024 (Must), Kühn & Mitrović 2024 (Should)

**Argument:** A substantial non-DH literature already benchmarks LLMs on metaphor and figurative-language identification with rigorous multi-model, multi-strategy designs (Fuoli et al.'s RAG/prompting/fine-tuning comparison; Reimann & Scheffler's negative zero-shot result as a calibrating counterweight; Balestrucci et al.'s named-rhetorical-figure classification with quantified human-model agreement) — this is the methodological template this paper's own evaluation design borrows from most directly, while Ye et al.'s skeptical probing of what high metaphor-task scores actually measure supplies a necessary caution for this paper's own Discussion. The two Kühn et al. surveys independently establish, across 39 papers and 86 detection approaches in eight non-Arabic languages, that *named* rhetorical figures beyond metaphor/irony/sarcasm — exactly the category periphrasis and antithesis belong to — are a generally under-studied, rule-based-dominated sub-field with no Arabic-language coverage at all, giving this paper's background a structural (not just domain-specific) reason why periphrasis and antithesis resisted Abd Alhadi et al.'s rule-based system.

## 2f. LLMs on Arabic figurative/cultural language specifically

**Cited:** Al Kaabi et al. 2024 (Must), Attia, Muhamed, Alkhamissi, Solorio & Diab 2026 / Kinayat (Must)

**Argument:** Two precedents combine LLMs with Arabic figurative language specifically, and each falls short of this paper's exact combination in a different, precisely nameable way: Al Kaabi et al. 2024 is qualitative and single-model (8 hand-picked examples, one ChatGPT run) on isolated rhetorical sentences, not a poem corpus; Attia et al. 2026 is a rigorous 22-model benchmark with quantified human-agreement metrics but evaluates modern colloquial idioms and proverbs for cultural/pragmatic competence, not named classical balagha categories in classical poetry, and uses no span-level identification task. Together they show the field has both the motivating intuition (Al Kaabi) and the methodological machinery (Attia) this paper needs, but has not yet pointed either at classical Arabic poetry's named rhetorical-element inventory.

## 2g. Foundational / theoretical references

**Cited:** Lakoff & Johnson 1980 (Should), Cohen 1960 (Should), Hayes & Krippendorff 2007 (Should)

**Argument:** Standard, citable anchors held in reserve rather than argued at length: Lakoff & Johnson for Conceptual Metaphor Theory if the Discussion invokes it when discussing استعارة; Cohen and Hayes & Krippendorff as the operational sources for whichever inter-annotator-agreement statistic (kappa vs. alpha) the Data and Annotation section ultimately reports.

---

## Cross-subsection framing note

Subsections 2e and 2f together carry the paper's central novelty argument and should be read as a pair: 2e establishes that rigorous multi-model LLM benchmarking of named rhetorical figures is a mature, exportable methodology (just not yet Arabic or classical-poetry-specific), while 2f establishes that the two existing attempts to apply any of that machinery to Arabic figurative language each stop short of this paper's exact target (classical poetry + named balagha elements + difficulty stratification). 2b and 2c jointly motivate *why this particular domain and these particular elements*; 2a and 2g supply background and methodological apparatus without carrying argumentative weight on their own.
