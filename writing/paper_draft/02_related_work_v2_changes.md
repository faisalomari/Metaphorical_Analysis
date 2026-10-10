# Changes from `02_related_work.md` to `02_related_work_v2.md`

Source draft untouched (`02_related_work.md` is the historical v1; nothing in it was edited). This file logs every substantive change applied in v2, with before/after text and the reason, plus what remains unverifiable. Verification work (PDF reads, browser lookups, web searches) is described inline; nothing below was invented.

## 1. Antithesis contradiction (factcheck Issue 1)

**Before** (in the "LLM benchmarks… beyond digital humanities" section): "...together they explain why antithesis and periphrasis resisted Abd Alhadi, Hussein and Kuflik's (2023) rule-based system..."

**After**: "...together they explain why periphrasis and metaphor — rather than antithesis, which Abd Alhadi, Hussein and Kuflik's (2023) rule-based system already handles reasonably well — were the elements that paper's authors judged out of reach for rule-based matching..."

**Reason**: Per `literature/notes/2023_AbdAlhadi_RhetoricalElementsArabicPoetry.md` (p.11 ¶59), Abd Alhadi et al. excluded only metaphor and periphrasis as "too semantic"; antithesis was attempted by the rules (F1 0.777 negative antithesis, F1 0.500 positive antithesis). The original wording put antithesis in the same excluded bucket as metaphor/periphrasis, directly contradicting RQ2 later in the same document, which correctly says antithesis is "handled well" by the rule-based system. Fixed to match RQ2 and the source note.

## 2. "Antithesis, a close typological relative of periphrasis" (factcheck Issue 2)

**Before**: "...named rhetorical figures beyond metaphor, irony, and sarcasm (among them antithesis, a close typological relative of periphrasis)..."

**After**: "...named rhetorical figures beyond metaphor, irony, and sarcasm (among them antithesis, a figure this paper's own corpus also evaluates)..."

**Reason**: No source (`2024_Kuhn_LesserKnownRhetoricalFiguresSurvey.md` included) supports a "typological relative" claim between antithesis and periphrasis; that note explicitly warns periphrasis doesn't even appear in Kühn et al.'s figure list. The claim appears to have been invented. Removed and replaced with a claim the project can actually verify (both elements are in this paper's own evaluated set).

## 3. Periphrasis framing in the DH-precedents section (factcheck Issue 6)

**Before**: "...a direct structural parallel to a finding already visible in this project's own pilot work on periphrasis, where the category that looks easiest to define on paper has proven to be among the hardest to apply consistently."

**After**: "...a direct structural parallel to this project's own pilot work on periphrasis, where small-sample noise and run-to-run instability have already produced a misleadingly large apparent effect that halved on replication — the same lesson Bender et al.'s finding points to: difficulty must be measured, not read off a category's surface description."

**Reason**: `PROJECT_STATE.md` §6.1 documents the periphrasis/Kenning finding as **run-to-run noise** (an apparent 8x gain that halved on a second run), not as a category that "looks easiest to define on paper" — periphrasis is in fact already flagged project-wide as the semantically *hardest* element. The original sentence conflated this project's noise finding with Bender et al.'s unrelated "coarsest category, lowest agreement" finding. Reworded to state the actual finding (measurement noise) while keeping the Bender et al. parallel (both findings share the lesson that difficulty must be measured empirically).

## 4. Qarah / AraPoemBERT task list (task instruction #2)

**Before**: "...reports strong results on meter, rhyme, era, and gender classification — all *formal* features of the verse, recoverable in large part from its surface phonology and morphology."

**After**: "...reports strong results across five tasks — meter, sub-meter, and rhyme classification, poet-gender classification, and poem-level sentiment analysis — the first four of which are *formal* features recoverable in large part from surface phonology and morphology."

**Reason**: Opened and read `literature/related_work/non_dhq/2024_Qarah_AraPoemBERT.pdf` directly (the PDF's own abstract and "main contributions" list). The paper's actual 5 downstream tasks are: poetry meter classification, poetry sub-meter classification, poems' rhyme classification, poet's gender classification, and poems' sentiment analysis. "Era" is a dataset attribute (Figure 6) but is **not** one of the 5 benchmarked tasks anywhere in the paper — it was a fabricated/mistaken item in the original draft. "Sentiment" (which `RELATED_WORK_INDEX.md`'s one-liner had correctly, against the draft's "era") is confirmed as a real task but is not a *formal* feature like meter/rhyme/sub-meter/gender, so the "all formal features" framing was narrowed to the first four tasks only.

## 5. Harb (2020) and Fontana (2025) (factcheck Issue 4)

**Before**: "Al-Jurjani's theory of poetic 'wonder'... treats figuration as a cognitive and aesthetic achievement rather than ornamental excess, and supplies much of the conceptual vocabulary later writers use to argue that a figure succeeds or fails (Harb, 2020). Al-Sakkaki's *Miftah al-'Ulum* then organizes this inventory into the tripartite division of *ma'ani*, *bayan*, and *badi'* that still structures how the tradition's rhetorical devices are taught and catalogued (Fontana, 2025)."

**After**: "Al-Jurjani's theory of poetic 'wonder'... marks a shift in classical literary judgment from scoring poetry for truthfulness and naturalness to judging it by its capacity to evoke wonder — novelty, strangeness, the unexpected — in the listener, an aesthetic al-Jurjani and later critics including al-Sakkaki treat as built into the structure of rhetorical figures themselves (Harb, 2020). Al-Sakkaki's *Miftah al-'Ulum* begins the tripartite division of the discipline into *ma'ani*, *bayan*, and *badi'*, later completed by al-Qazwini, that still structures how the tradition's rhetorical devices are catalogued (Fontana, 2025)."

**Reason**: The factcheck flagged these sentences as adding specificity beyond the verified one-line index descriptions (neither PDF had been obtained). This session obtained primary-source text for both:
- **Harb**: found the publisher's (Cambridge Core) own chapter abstract for *Arabic Poetics*, Chapter 1 ("Wonder: A New Paradigm"), which confirms the shift from a truth/naturalness-based criticism to a wonder-based one (novelty, strangeness, the unexpected), and that this wonder-aesthetic is treated as inherent in the structure of rhetorical figures including those of al-Sakkaki. The new sentence is built directly from that abstract.
- **Fontana**: found and read the full text of the paper via its academia.edu listing (footnote 22 of "The Name of the Key"), which states verbatim that "the three-branched systematization of the discipline in al-maʿānī, al-bayān, and al-badīʿ which started with Sakkākī, was later completed by Jalāl al-Dīn al-Qazwīnī." The new sentence matches this exactly (al-Sakkaki *begins* the tripartite division; al-Qazwini completes it) rather than crediting al-Sakkaki with the full tripartite system outright.

Both PDFs were not downloaded into `literature/related_work/non_dhq/` (Harb: Cambridge UP monograph, no accessible full PDF found despite search for an excerpt/OA copy; the Cambridge Core chapter-abstract page was read directly instead. Fontana: `cris.unibo.it`'s hosted PDF is still blocked by Cloudflare bot-detection, as the factcheck noted, but the paper's full text was obtained via its academia.edu mirror and read directly, so the claim is now verified from primary-source text even though the file itself was not added to the repo).

## 6. Cachia (1998) Works Cited entry (task instruction #1)

**Before**: Cachia (1998) was cited in-text with no Works Cited entry (factcheck Issue, Counts §5).

**After**: Added a Works Cited entry: "Cachia, P. (1998) *The Arch Rhetorician, or The Schemer's Skimmer: A Handbook of Late Arabic Badi'*. Wiesbaden: Harrassowitz Verlag (Studies in Arabic Language & Literature, vol. 3)."

**Reason**: Verified via web search (TUM library catalog record and a Cambridge University obituary of Cachia listing his works): Pierre Cachia's 1998 book, published by Harrassowitz in the "Studies in Arabic Language & Literature" series (vol. 3), 137 pp. This matches the "bilingual dictionary of Arabic rhetoric" description in `2023_AbdAlhadi_RhetoricalElementsArabicPoetry.md` (p.11, Appendix 1 note), which is the source citing Cachia 1998 as the origin of its element definitions. Since the citation could be verified, a Works Cited entry was added rather than removing the in-text citation.

## 7. Tarkka et al. (2026) (factcheck Issue 5)

**Before**: "...comparison of a BERT-based classifier against human questionnaire responses on Finnish parliamentary speech... pairs standard precision, recall, and F1 reporting with an explanation-analysis layer (SHAP)..."

**After**: "...comparison of a BERT-based classifier against human questionnaire responses on Finnish parliamentary speech... pairs party-affiliation F1 reporting with an explanation-analysis layer (SHAP)..."

**Reason**: Opened the actual DHQ article at `dhq.digitalhumanities.org/vol/20/1/000839/000839.html` in the built-in browser and read its abstract and body. Confirmed: Finnish Parliament, FinBERT classifier predicting MP party affiliation from plenary speeches, SHAP explainability, 438-participant human questionnaire, model more accurate than humans, model picks up personal style/rhetoric vs. humans' topical cues — all of which the original sentence already got right. But a direct text search of the article body for "F1" confirms the paper reports only **F1** ("average macro F1-score," "party-wise F1 scores") — never precision or recall as separate figures. "Precision, recall, and F1" was corrected to "F1" throughout.

## 8. Ye et al. (2026) — spelled-out author names (task instruction #1)

**Before** (Works Cited): "Ye, [et al.] (2026) 'Probing Semantic Alignment, Lexical Invariance, and Syntactic Influence in LLM Metaphor Processing'..."

**After**: "Ye, F., Wang, S., Chao, L. S. and Wong, D. F. (2026) '...'"

**Reason**: Read the actual paper PDF (`literature/related_work/non_dhq/2026_Ye_ProbingLLMMetaphorProcessing.pdf`), page 1 byline: Fengying Ye, Shanshan Wang, Lidia S. Chao, Derek F. Wong (University of Macau). Spelled out in full, replacing the literal "[et al.]" placeholder.

## 9. Al Kaabi et al. (2024) — first-author initials (factcheck "lower-severity items")

**Before** (Works Cited): "Al Kaabi, S. et al. (2024)..."

**After**: "Al Kaabi, M. H., Abubkr, L. O., Abdeddayem, S., Bin Haidara, N. and Almaamari, H. (2024)..."

**Reason**: Read the actual paper PDF (`literature/related_work/non_dhq/2024_AlKaabi_ChatGPTArabicRhetoricTeaching.pdf`), page 1 byline: Moza H. Al Kaabi, Lutfi Omar Abubkr, Sellami Abdeddayem, Nabeeha Bin Haidara, Hayam Almaamari (Mohamed Bin Zayed University for Humanities). The original draft's "Al Kaabi, S." initial was wrong (no "S. Al Kaabi" exists among the authors); corrected to the verified full author list and initials.

## 10. Word count

v1's body (excluding Works Cited) was ~2,512 words, 12 words over the stated 2,500 ceiling. v2's body is **2,499 words**, trimmed from the already-corrected text by tightening several sentences (removing redundant qualifiers like "genuinely," "already," "directly," and combining clauses) without cutting any citation, claim, or research question. The three RQs were kept verbatim (per `02_related_work_notes.md`, they are reused near-verbatim from `gap_statement.md` and are frozen phrasing).

## What remains unverifiable / unchanged

- **Harb (2020) and Fontana (2025) full PDFs**: still not in `literature/related_work/non_dhq/`. Harb's book has no accessible open-access copy (Cambridge UP monograph; only the publisher's own chapter-abstract page was accessible). Fontana's institutional-repository PDF (`cris.unibo.it`) is still blocked by Cloudflare bot detection, exactly as the factcheck found — but this session located and read the paper's full text via its author-hosted academia.edu listing, which is a legitimate author-authorized copy, so the claims in §5 above are verified from primary-source text even though no local PDF file was added.
- **Al-Jurjani / al-Sakkaki as historical figures**: still cited only as names embedded in Harb's and Fontana's own English-language scholarly discussion, never as direct citations of the medieval primary texts, per the original notes file's stated policy.
- Everything else in the factcheck's "Everything else checked out" section (§4) — the Abd Alhadi P/R figures, Gutman's accuracy, Fuoli's F1, Balestrucci's Krippendorff's alpha, Attia et al.'s 85.58% figure, Kühn et al.'s survey statistics, Al Kaabi et al.'s 8-example design, and the novelty/gap paragraph and RQs — was left unchanged, since the factcheck found no issues with these claims.
