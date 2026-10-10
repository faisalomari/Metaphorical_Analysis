# DHQ format guide — for "Exploring the Potential of Large Language Models to Identify Challenging Rhetorical Elements"

Compiled 2026-10-07. Sources: official DHQ pages (fetched directly, URLs below) and the 7 sampled DHQ PDFs in `literature/related_work/dhq/`. Anything not found in an official source is marked **not stated**; nothing below is invented.

---

## (a) Official DHQ requirements

### Article types
Source: [Submission Guidelines](https://dhq.digitalhumanities.org/submissions/index.html)

DHQ accepts four submission categories:
- **Articles** — "Article-length pieces describing original research."
- **Reviews** — "Reviews of other publications (digital or print), tools, artworks, conferences, and other relevant material."
- **Case Studies** — "Detailed analyses of specific projects that contextualize the project within the DH field, and demonstrate its significance for other practitioners."
- **Field Reports** — "Reports on digital humanities-related practice from the perspective of a particular locale."

Our paper (a multi-model LLM benchmark against an expert-annotated gold standard) fits **Article**.

Every submission, regardless of category, must additionally:
> "fall within the content domain of the journal... communicate effectively to the broad DHQ readership, rather than being narrowly limited to specialists... have an argument, and... represent an original contribution... must be well written" (Submission Guidelines).

### Length limits
Source: [Submission Guidelines](https://dhq.digitalhumanities.org/submissions/index.html)

> "Submissions may be of any length, but please bear in mind that although the digital medium is comparatively unbounded, reader attention is not; very long submissions must merit the space they occupy."

**No numeric word/page limit is stated anywhere in the official guidelines.** The sampled-article lengths in part (b) below are the only empirical signal for a reasonable target.

### Abstract and keyword requirements
Source: [DHQ author TEI template](https://raw.githubusercontent.com/Digital-Humanities-Quarterly/dhq-journal/refs/heads/main/articles/templates/dhq_author_template.xml) (linked from Style Guidelines)

- **Abstract**: a `<dhq:abstract>` element, one or more `<p>`. Template comment: "Include a brief abstract of the article." No sentence/word count is specified — "brief" is the only guidance given.
- **Teaser**: a separate `<dhq:teaser>` element. Template comment: "Include a brief teaser, no more than a phrase or a single sentence." This is distinct from the abstract and shorter.
- **Keywords**: three parallel keyword lists in `<textClass>`:
  1. `#dhq_keywords` — one or more terms chosen from DHQ's controlled vocabulary at `https://dhq.digitalhumanities.org/common/xml/taxonomy.xml` ("Authors may suggest one or more keywords from the DHQ keyword list... these may be supplemented or modified by DHQ editors").
  2. `#authorial_keywords` — free-text author keywords, "no controlled vocabulary."
  3. `#project_keywords` — DHQ Project Registry terms ("in development" per the template; likely optional).
- Exact minimum/maximum **number** of keywords: **not stated**.

### Bibliography / citation style
Source: [Citation Guidelines](https://dhq.digitalhumanities.org/submissions/citationGuidelines.html)

- DHQ uses the **Harvard referencing system** (author–date), in-text: surname + 4-digit year, optional page/¶/§ locator — e.g. `(Phillips, 2016, pp. 4–9)`, `(Chandler, Li, and Osborne, 2018, ¶15)`.
- 4+ authors abbreviate to "first author + et al." in-text.
- **DHQ-specific deviation from standard Harvard**: "Multiple references... should never be combined. Please provide each reference as a unique entity" (i.e., no `(Smith 2020; Jones 2021)` grouped citations — cite separately).
- Reference list header must be **"References"**, alphabetical (single-author first), then chronological.
- Full format templates given for: printed book, edited book, book chapter, e-book, journal article (`Author. (YYYY) 'Title', Journal, vol(issue), pp. X–Y.`), conference proceedings, newspaper/magazine, website, social media, image, music, film, media program.
- Notes are for **comments only**, never for bibliographic citations; numbered consecutively, anchored in text, gathered at the end unless using DHQauthor XML (where they can be inline).

### Figure / table / image rules
Source: [Style Guidelines](https://dhq.digitalhumanities.org/submissions/textGuidelines.html)

- Accepted formats: PNG, JPG, GIF, SVG (plus PDF for final submission per the Submission Guidelines' supplementary-materials list).
- Initial submission: figures **embedded in the text** (for ease of review). Final (accepted) version: all images submitted as **separate files**, high-quality, uploaded to OJS.
- Naming convention: `figure01.jpg`, `figure02.jpg`, etc., in order of appearance; the text must reference the filename at the intended insertion point.
- DHQ **auto-generates** the "Figure N." label; authors may add a descriptive caption after it (caption may be "the length of a short paragraph" but no "complex internal structures").
- **Mandatory accessibility alt-text** for every figure, distinct from the caption: short (phrase to one sentence), describing the image's rhetorical/evidentiary function, not its visual appearance; explicit guidance against reusing caption text or describing color/medium unless functionally relevant; template examples given (including a chart-description template: "[chart type] of [type of data] where [reason for including chart]").
- Tables/examples (code samples, etc.) follow the same label+caption convention as figures.
- Cross-references in prose must use the full capitalized word — "see Figure 1", "see Section 2.5" — never abbreviated ("fig.", "sec.").
- Math: TeX or MathML; simple formulas can autoconvert, complex ones need a separate TeX/MathML file at final submission.

### TEI/XML or template requirements
Source: [Submission Guidelines](https://dhq.digitalhumanities.org/submissions/index.html), [Style Guidelines](https://dhq.digitalhumanities.org/submissions/textGuidelines.html), [author TEI template](https://raw.githubusercontent.com/Digital-Humanities-Quarterly/dhq-journal/refs/heads/main/articles/templates/dhq_author_template.xml)

- DHQ is "an entirely digital journal, published in XML." Accepted **submission** formats: DHQ-markup XML (DHQauthor, a TEI customization), plain TEI XML, or **RTF / OpenOffice / MS Word** (i.e., a plain Word document is explicitly acceptable for submission — DHQ's own staff convert/encode it into XML after acceptance).
- If authors do want to pre-encode in XML, a schema, the `dhq_author_template.xml` (used above for the abstract/keyword fields), and encoding documentation are provided.
- Heading guidance (applies regardless of submission format): use headings for "major sections... signal... turning points," not for every minor point; "heading levels beyond two or at most three layers are not necessary except in very long articles"; headings should be **descriptive, not purely numeric** — DHQ "strongly advises authors to avoid numbering/lettering headings (e.g. '3. Methodology')" unless numbers materially help the reader; DHQ may normalize heading numbering/capitalization at copyediting regardless.
- Use actual word-processor heading *styles*, not manually bolded/underlined text.
- US/Commonwealth spelling both permitted; just stay internally consistent.

### Review process
Source: [Submission Guidelines](https://dhq.digitalhumanities.org/submissions/index.html), [Peer Reviewing for DHQ](https://dhq.digitalhumanities.org/submissions/peerReviewing.html)

- Rolling submission deadlines: **January 15, April 15, July 15, October 15** (quarterly).
- Submitted via **Open Journal System (OJS)**; account required.
- Step 1: editorial team checks basic fit (domain, audience, argument, writing quality, no defamatory/hate content).
- Step 2: external peer review, typically **2–4 months** (can be longer if reviewers are hard to secure).
- Decisions: **Accept pending revisions**, **Revise and resubmit** (sent back out for fresh review, usually to an original reviewer), or **Decline**.
- Review is **blind but not double-blind** — "concealing the author's identity from reviewers is not as essential for DHQ"; authors *may* anonymize if they wish, but it's optional, not required.
- After acceptance: copyediting for DHQ style/consistency → encoding into DHQ TEI-XML → author reviews an internal proof version (~1 week) → publication, first in "preview" form on the site, then folded into a quarterly issue; permanent archiving at Northeastern University's digital repository.
- No article submission or processing charges of any kind (diamond open access).

### Language policy
- **Not stated as an explicit standalone policy** on the Submission Guidelines, Style Guidelines, or Citation Guidelines pages — no page states which languages are accepted or how non-English submissions are reviewed.
- Indirect evidence that DHQ **does** publish non-English-language articles: the author TEI template includes an `xml:lang` attribute on the title ("Change the value of xml:lang if not English") and a boilerplate `<respStmt>` block specifically for cases where "a translation... was provided or facilitated, at least initially, by an AI system like Google Translate or Claude," together with the explicit note that "Artificial intelligence systems, including machine translation systems, are not considered by DHQ to be authors." Our own corpus includes a French-language DHQ article (Riguet & Alrahabi 2018, DHQ 12.1), confirming non-English publication happens in practice.
- Given our paper concerns Arabic poetry and rhetorical terminology, note: the AI policy (below) would govern any AI-assisted translation of Arabic terms/quotations if we used one — this must be disclosed if "substantive."

### AI policy (highly relevant to this paper)
Source: [DHQ AI Policies](https://dhq.digitalhumanities.org/submissions/ai_policies.html) — DHQ follows COPE guidelines on authorship/AI plus DHQ-specific rules.

- **Authorship**: "Artificial intelligence systems are not considered by DHQ to be authors and should not be listed as authors." Human author bears full intellectual/ethical responsibility.
- **Content generation**: authors "may not use AI tools to generate the content of their submission" as a blanket matter, but AI-assisted tasks (finding sources, making diagrams, translating/clarifying language) are permitted; authors *may* use AI to generate portions of the article specifically **if AI use is thematically relevant to the article's topic and is disclosed** — this is squarely our case, since the paper's subject is LLM performance.
- **Content accuracy**: zero tolerance for hallucinated/falsified citations or content of any kind; a submission found to cite non-existent sources will be declined, and reinstated-after-publication discovery leads to retroactive removal. "It is the author's responsibility to ensure the accuracy of all citations."
- **Acknowledgement**: "must acknowledge any substantive use of AI tools in their research and writing process... beyond... routine utilities such as grammar checking," placed either in the methods discussion or as an appendix.
- **Practical implication for us**: because our paper's own method *is* evaluating LLMs (Claude, GPT, Gemini, Fable, etc.) on a research task, we should include an explicit methods-adjacent statement distinguishing (i) the LLMs as the *object of study* (their outputs are data/results, clearly presented as such, never passed off as the authors' own analysis) from (ii) any use of AI tools in *writing the paper itself* (which must be separately disclosed per the policy, if applicable, e.g. grammar/translation help).

### Submission steps (summary)
1. Prepare manuscript in DHQauthor XML, plain TEI XML, or Word/RTF/OpenOffice, embedding any figures in the submission text for review.
2. Register/sign in to DHQ's OJS instance (link given on the Submission Guidelines page) and submit by one of the quarterly deadlines (Jan 15 / Apr 15 / Jul 15 / Oct 15).
3. Editorial team screens for basic fit.
4. External peer review (2–4 months).
5. Decision: accept-pending-revisions / revise-and-resubmit / decline; resubmissions go back out for review.
6. On acceptance: submit final high-resolution figures as separate files (not embedded), any complex formulas as separate TeX/MathML; copyediting and TEI-XML encoding by DHQ staff; author checks a proof version (~1 week).
7. Publication in preview form, later folded into a quarterly issue; archived permanently.

### Not stated anywhere in the official pages reviewed
- Numeric word/page count limit.
- Minimum/maximum number of keywords.
- A required section list or outline (DHQ explicitly leaves section structure to the author/discipline, only constraining heading *style*, not content).
- Font, margin, or any print-layout specification (irrelevant — DHQ is XML/web-native, not print-formatted by authors).
- A fixed number of peer reviewers assigned per submission.
- Any blanket language-acceptance policy or a list of supported languages.

---

## (b) Structure of the 7 sampled DHQ articles

All 7 PDFs were read in full by a dedicated structural pass (separate from the content-focused notes in `literature/notes/` for Abd Alhadi, Gutman, and Bender). Page/length figures are approximate (PDF page counts, since DHQ's own pagination is the marginal paragraph number, not the page).

| Article | Section order (top level) | Length | Abstract | Related work placement | Methods/results structure | Figures / tables | Limitations/discussion | Citation style & bibliography size | Tone (1=narrative, 10=technical) |
|---|---|---|---|---|---|---|---|---|---|
| **Abd Alhadi et al. 2023** (17.2) | Abstract → 1 Intro → 2 Background & Related Work → 3 Features of Classical Arabic Poems → 4 Tools and Methods (i–iv) → 5 Experiments and Results (i–iv) → 6 Discussion → 7 Conclusion & Future Work → Appendices 1–4 → Acknowledgement → Notes → Works Cited | ~18 pp. (body ~11 pp.; appendices ~40% of doc) | 1 ¶, ~6 sent./~130 words; RQ+method+headline F-score | Dedicated §2 "Background and Related Work," ~15 sources | §4 Methods fully separate from §5 Results, lettered sub-steps | 8 figures (architecture/GUI screenshots), 6 tables (P/R/F1, TP/FP/FN) | Dedicated numbered §6 "Discussion" then separate §7 "Conclusion" | Author–date brackets `[Hussein 2015b]`; ~45 entries | 6 |
| **Gutman 2024** (18.3) | Abstract → 1 Intro → 2 Theory: Figurative Language as a Network → 3 Methodology (3.1–3.2) → 4 Case Study: Timon (4.1–4.2) → 5 Conclusions → Appendix: Topic List → Notes → Works Cited | ~16 pp., ~7,000–8,000 words body | 1 ¶, 5 sent./~100 words; RQ+method+case study, no numeric finding | No dedicated heading — folded into theory (§2) and methodology (§3.1) review | §3 Methodology (2 subsections) separate from §4 application/results | 8 figures (Gephi network graphs, 1 bar chart), 11 tables (centrality data) | No separate heading; caveats woven into §5 Conclusions | Author–date brackets; ~70 entries | 5 |
| **Bender et al. 2023** (17.3) | Abstract → 1 Intro → 2 Capturing discourse referencing (2.1–2.2) → 3 Dataset & annotation workflow (3.1–3.2) → 4 Automatic classification (4.1–4.3) → 5 Analysis of results → 6 Discussion → 7 Conclusion → Works Cited | ~16 pp., ~8,000–9,000 words | 1 ¶, ~7 sent./~150 words; methods-forward, no headline accuracy number in the abstract itself | No dedicated heading — folded into §2.1 ("Criteria for...") | §3 dataset/annotation, §4.1–4.2 model, §4.3 results, §5 dedicated error analysis — most ACL-paper-like | Only 4 figures (confusion matrices); 8 tables (P/R/F1 across 3 settings, hyperparameters) | Dedicated numbered §6 "Discussion" before separate §7 "Conclusion" | Author–date brackets `[Devlin et al. 2019]`; ~35 entries | 8 |
| **Rebora 2023** (17.2) | Abstract → 1 Intro → 2 Theoretical criticism (2.1–2.2) → 3 Tools criticism (3.1 taxonomy incl. 3.1.1–3.1.3; 3.2 SA tools 3.2.1–3.2.6) → 4 Conclusion → Notes → Works Cited | ~17 pp., ~7,500–8,500 words (survey genre — dense prose) | 1 ¶, 4 sent./~80 words; topic+structure, no empirical finding (survey genre) | No dedicated section — the whole article is a literature review; continuous high citation density | No empirical methods/results in the conventional sense; "results" = a 3-axis taxonomy applied tool-by-tool (§3.2.1–3.2.6) | **0 figures**, 1 small table — least illustrated of the 7 | No dedicated heading; critique distributed throughout, §4 Conclusion reflects on field-wide open problems | Author–date brackets; ~90 entries (largest bibliography of the 7) | 3 |
| **Hua & Raley 2023** (17.2) | Abstract → 1 Overview → 2 Mapping Deep Learning Code → 3 Applications of GPT-2 → 4 Conclusion → Notes → Works Cited (flat — no numbered subsections at all) | ~19 pp. (longest), ~9,000–10,000 words, 19 endnotes | 1 ¶, ~6 sent./~160 words; premise+method+case studies+stakes, no quantitative finding | No dedicated section — woven into §1 Overview as extended literature engagement (~7 ¶s) | Qualitative: close readings of reproduced Python source code, no quantitative results | 10 figures (**all reproduced source-code screenshots/console output**, zero data charts); **0 tables** | No dedicated heading; caveats pushed into extensive endnotes (19 notes, several paragraph-length) | Author–date brackets routinely with page numbers, e.g. `[Mackenzie 2017, p. 22]`; ~45 entries | 2 |
| **Dobson 2021** (15.2) | **No boxed Abstract** → unlabeled opening essay (~6 ¶s, functions as intro+lit review) → Data Objects → Topic Models → Classification Algorithms → Conclusion → Acknowledgments → Works Cited (no numbered headings anywhere — unique among the 7) | ~15 pp., ~8,000 words | **None** — only DHQ article of the 7 sampled with no separate abstract; opens directly into argumentative prose | No dedicated section — theory/lit review woven into the unlabeled opening | 3 case-study sections, each a worked Python/scikit-learn mini-tutorial-as-argument | 4 figures (2 code screenshots, 2 confusion-matrix heatmaps), 4 tables (topic/feature word lists) | No dedicated heading; the whole essay is sustained critique; Conclusion restates the thesis, unhedged | Author–date parenthetical, comma before page, e.g. `[Rawson and Muñoz 2019, 290]`; ~40 entries | 5 |
| **Tarkka et al. 2026** (20.1, preview) | Abstract → Introduction → Background and previous work (3 subsections) → Data & Methods (5 subsections) → Results (4 subsections) → Conclusion → Appendix A → Data availability → Declarations → Notes → Works Cited → auto-generated "Recommendations" (no numbered top-level headings) | ~20 pp. (longest), ~9,000–10,000 words | 1 ¶, 6 sent./~130 words; RQ+method+headline finding — most complete/quantified alongside Abd Alhadi | Dedicated subsection "Previous work on predicting party affiliation" nested inside "Background and previous work," ~8 prior studies compared systematically | Separate major "Data & Methods" (5 subsections incl. a worked SHAP toy example) and "Results" (4 subsections) — most rigorously social-science-shaped of the 7, with numbered RQs in the intro | 7 figures (confusion matrices, SHAP text-highlight visualizations, bar/line charts), 5 tables (per-party F1, cue phrases) | No dedicated heading; brief caveats inside Conclusion (e.g., SHAP's own interpretive limits) | Author–date brackets; ~55 entries; **also has "Data availability" and "Declarations" (funding + a conflict-of-interest-style disclosure) — not present in the other 6, newest article of the 7** | 8 |

## (c) Common patterns

- **Section order**: every article opens with a boxed "Abstract" except Dobson 2021 (which has none and opens directly into prose) — DHQ clearly does not enforce an abstract box universally, but 6/7 have one, so we should include one. After the abstract comes an Introduction (sometimes unlabeled, as in Dobson/Hua & Raley), then background/prior-literature treatment that is **almost never** isolated under a literal "Related Work" heading — only Abd Alhadi uses that exact phrase as a section title; Tarkka nests it as a subsection; the other 5 weave it into a theory/overview section. Methods and Results are cleanly separated into their own major sections in the more empirical pieces (Abd Alhadi, Bender, Tarkka); the more essayistic/survey pieces (Rebora, Hua & Raley, Dobson) blend method and finding into continuous argumentative prose. All 7 end with a Conclusion (sometimes "Conclusion and Future Work") and an alphabetical bibliography headed **"Works Cited"** — never "References" or "Bibliography," despite the official Citation Guidelines page itself saying the end section should be headed "References." (Note the discrepancy: **published DHQ articles use "Works Cited," not the "References" the Citation Guidelines page names — flag this as worth a direct editor check, or simply follow DHQ's actual practice.**) Numbering of top-level headings is inconsistent across the sample (5/7 number them; Dobson and Tarkka don't), consistent with the Style Guidelines' own statement that numbering is optional and not encouraged unless it helps the reader.
- **Length**: consistently 15–20 PDF pages including bibliography; body text (excluding appendices/bibliography) runs roughly 7,000–10,000 words. The more ML/data-heavy pieces (Bender, Tarkka, Abd Alhadi) run long because of extensive tables; the survey piece (Rebora) is comparably long but through continuous prose rather than tables.
- **Abstract style**: one paragraph, no internal structure, 80–160 words / 4–7 sentences, in a bordered box under the title (when present). The two most quantitative/empirical articles (Abd Alhadi, Tarkka) state RQ + method + a headline number; the more qualitative/survey pieces (Rebora, Hua & Raley, Gutman) state RQ + method + scope/stakes but skip a single numeric finding, which fits their genre. Dobson is the outlier with none at all.
- **Citation style**: all 7 use author–date bracketed in-text citations (`[Author Year]` or `[Author Year, page]`), resolved against an alphabetical bibliography — never a numbered reference list, never footnote-only citation. This matches the official Harvard-style Citation Guidelines in form, except that the published articles' end-section heading ("Works Cited") differs from what the Citation Guidelines page names ("References") — see note above. Citation density is highest in the two survey/theory-heavy pieces (Rebora ~90 sources, Hua & Raley ~45 with unusually frequent page-pinned citations); self-citation to the authors' own prior work is common (Bender, Rebora, Gutman all do this) and acceptable DHQ practice.
- **Figures/tables**: usage varies enormously by genre — from 0 figures (Rebora, a pure-text survey) to 10 figures (Hua & Raley, all reproduced source code) to 11 tables (Gutman, all centrality statistics). Confusion matrices and P/R/F1 tables are the standard way empirical pieces (Abd Alhadi, Bender, Tarkka, Dobson) report model performance; all follow the official auto-captioned "Figure N."/"Table N." convention.
- **Limitations/discussion**: only Abd Alhadi and Bender use an explicit, separately headed "Discussion" section before the Conclusion; the other 5 fold methodological caveats into the Conclusion itself or (Hua & Raley) into extended endnotes. None of the 7 uses a section literally titled "Limitations."
- **Tone spectrum** (1 = narrative/interpretive, 10 = metric-dense/technical): Hua & Raley (2) < Rebora (3) < Gutman (5) ≈ Dobson (5) < Abd Alhadi (6) < Bender (8) ≈ Tarkka (8). DHQ publishes across this entire spectrum, from a pure critical-humanities essay with zero statistics (Hua & Raley) to a near-social-science empirical paper with confusion matrices, F1 tables and SHAP values (Bender, Tarkka) — but even the most technical pieces retain substantial humanistic framing (literary/political/pragmalinguistic theory) around the metrics; none of the 7 reads as a pure CS conference paper.
- **DHQ-specific formatting markers common to all 7**: sequential marginal paragraph numbers running the full article length (used for precise citation, e.g. "¶12"); bolded "Figure N."/"Table N." captions in bordered boxes; a CC BY-ND 4.0 license footer; a volume/issue header; ORCID links by most (not all) author names; "Works Cited" as the invariant bibliography heading. The newest article (Tarkka 2026) shows features not present in the 2021–2024 articles — an assigned DOI, "Data availability" and "Declarations" sections, and an auto-generated "Recommendations" (related-articles) block — which may reflect emerging DHQ platform norms worth matching in a 2026 submission (a GitHub/data-availability statement in particular is a cheap, easy addition given our repo already exists).

## (d) Recommended outline for our paper

Given the official requirements (part a) and the structural norms above, our paper sits closest to **Abd Alhadi et al. and Tarkka et al.** in genre (an empirical LLM-vs-gold-standard benchmark with a human/expert-difficulty angle) but should keep Abd Alhadi's and Rebora's humanistic framing proportions rather than Bender's maximally ACL-style density, since DHQ's audience includes non-specialist humanists. Target length: **~8,000–10,000 words body** (matching the 7-article range), explicitly within DHQ's "no numeric limit, but justify the space" norm.

1. **Abstract** (~120–150 words, 1 paragraph) — state the RQ (can LLMs identify rhetorical elements in classical Arabic poetry that existing rule-based/ML systems struggle with, i.e. metaphor/periphrasis/antithesis), the method (multi-model LLM benchmark against an expert-annotated span-level gold standard, DEV/TEST split), and the headline finding/number once Phase 2 TEST results exist. Mirrors Abd Alhadi/Tarkka's RQ+method+finding pattern.
2. **Teaser** (one phrase/sentence, separate TEI field) — a single punchy line, e.g. the gap being filled.
3. **Introduction** — motivation (why rhetorical elements matter for classical Arabic poetry scholarship; why "challenging" elements like metaphor/periphrasis/antithesis resisted earlier automation per Abd Alhadi's own stated limitation), the paper's contribution, and a roadmap sentence. No numbered heading (follow the Dobson/Tarkka convention and DHQ's own de-emphasis of numbering) or use a plain "1. Introduction" if the final house style prefers numbers — either is attested.
4. **Background and Related Work** — explicitly headed this way (Abd Alhadi's own phrasing), covering: (a) the balagha/rhetorical-element inventory and classical Arabic poetry corpus context; (b) prior automatic approaches (Abd Alhadi's rule-based system as the direct predecessor/baseline, explicitly noting it excluded metaphor/periphrasis as "semantics-dependent"); (c) DH precedents for annotation-category development and difficulty (Bender's quality criteria, Zirker's ambiguity treatment, Münz-Manor's figurative-annotation argument); (d) LLM-in-DH literature (Hua & Raley on understanding model internals; Tarkka on model-vs-human comparison; Dobson on interpretability caveats) to justify why an LLM benchmark, done carefully, is a DH-relevant contribution and not just an NLP leaderboard exercise.
5. **Data and Annotation** — corpus description, the gold-standard annotation scheme and process (annotators, agreement if measured — note the DH pattern that the *simplest*-looking categories often get the *lowest* agreement, per the comparison table), DEV/TEST split and the rule that TEST is spent once.
6. **Method** — models tested, prompting/pipeline design (two-stage Config C etc.), span-level scoring methodology (strict + token-overlap, per `span_scoring.py`), and the AI-use disclosure required by DHQ's AI policy (the LLMs are the object of study; any AI assistance in *writing* the paper, if used beyond grammar-checking, disclosed separately per policy).
7. **Results** — per-model, per-element precision/recall/F1 **with raw TP/FP/FN** (matching this project's own experiment-discipline rule and Abd Alhadi's table format), 2-run majority as the primary metric, tables/figures for the headline comparison, and a figure type DHQ doesn't yet have an example of in our sample but that would fit naturally — e.g. a confusion-style breakdown or SHAP-style explanation visualization (as Tarkka did) if interpretability analysis is part of the design.
8. **Discussion** — explicitly headed this way (Abd Alhadi/Bender precedent): where LLMs succeed vs. fail relative to the rule-based baseline and to each other; link failure patterns to the "challenging" framing (semantics-dependent elements, context-dependence, ambiguity) established in Background; discuss what the per-element difficulty ordering tells us about LLMs' current limits for classical Arabic rhetorical analysis, in the cautious, non-overclaiming register Dobson's article models.
9. **Limitations** — fold into Discussion or give a short final subsection (no DHQ article in the sample used a standalone "Limitations" heading, but nothing forbids one); be explicit about gold-standard size, single/limited annotators if applicable, model version pinning, and anything else this project's own experiment-discipline notes already flag as a caveat.
10. **Conclusion and Future Work** — restate contribution, point to future directions (larger corpora, fine-tuning, more elements), matching Abd Alhadi's own "Conclusion and Future Work" heading, which is a direct intellectual lineage point worth echoing.
11. **Data availability / Declarations** (optional but recommended, following the 2026 Tarkka precedent) — link to the project's public repo/results if we make any portion public, and a brief AI-use declaration as DHQ's AI policy requires.
12. **Notes** (DHQ-style endnotes, comments only, never citations) and **Works Cited** (alphabetical, Harvard author–date, per the official Citation Guidelines — note again the "Works Cited" vs. "References" heading discrepancy between guidance and practice; default to "Works Cited" to match actual house practice unless editors say otherwise during review).
13. **Appendix** (optional) — full element/definition list (as Abd Alhadi and Gutman both do), analogous to our own `data/elements/*.txt` glossary, if space in the body needs to be kept down.

Keywords: at minimum one term from the DHQ controlled taxonomy (e.g., something under Arabic/Middle Eastern studies, computational linguistics, or text analysis categories — check `https://dhq.digitalhumanities.org/common/xml/taxonomy.xml` for the current list at submission time) plus free author keywords (e.g., "large language models," "classical Arabic poetry," "rhetorical analysis," "annotation difficulty").

## Could not verify / open questions

- Exact word/page length DHQ editors would consider "very long" and ask to trim — no numeric threshold given; only inferable from the comparable published articles above (15–20 pp. / 7,000–10,000 words seems to be the de facto norm, but this is an inference, not a stated rule).
- Whether DHQ's "Case Studies" vs. "Articles" category has different length/structure norms — the Submission Guidelines distinguish them by content/purpose, not by format.
- Whether non-English submission requires English translation at submission time or only at some later stage — not addressed by any official page found.
- Minimum/maximum number of keywords, and the current full contents of the DHQ controlled keyword taxonomy (the XML taxonomy file at `https://dhq.digitalhumanities.org/common/xml/taxonomy.xml` returned as raw XML with no readable body in the browser text-extraction tool used here; it was not parsed, so we cannot list current controlled-vocabulary terms — this should be checked directly at submission time).
- Discrepancy between the Citation Guidelines page (names the bibliography section "References") and actual published-article practice (all 7 sampled articles use "Works Cited") — not resolved; recommend following the empirical "Works Cited" practice but flagging the question to DHQ editors if asked.
- Whether the "Data availability" / "Declarations" sections seen only in the 2026 Tarkka article are a new formal requirement or simply that particular author team's/special issue's choice — no official guidance page mentions either section, so this is inferred from a single data point, not confirmed as current DHQ policy.
