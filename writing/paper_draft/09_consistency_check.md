# Whole-Paper Consistency Check

Checked against every file in `writing/paper_draft/` as currently drafted: `00_abstract_and_keywords.md`, `01_introduction.md`, `02_related_work_v2.md`, `03_data_and_methods.md`, `04_results.md`, `05_discussion.md`, `06_limitations_and_future_work.md`, `07_conclusion.md`, `08_ai_disclosure.md`, and `00_merged_references.md`. `00_proposal_reuse_map.md` and `01_03_04_notes.md` are working/process documents, not sections of the paper itself, and are excluded from the in-text/Works-Cited reconciliation below (but their findings — e.g. the Hussein 2015 recommendation — are cross-checked where relevant). No new API calls were made to produce this check; it is a read-only audit of the existing nine drafted sections.

## 1. Numeric consistency across sections

Every headline number was traced back to its stated source file (not re-derived) and compared across every section that repeats it.

| Number | Where it appears | Consistent? |
|---|---|---|
| Simile strict F1 0.65–0.73 (v4_combined, all 3 models) | `00_abstract_and_keywords.md`, `05_discussion.md`, `07_conclusion.md` (ceiling comparison); source table in `04_results.md` | **Yes** — identical range quoted everywhere, matches `04_results.md`'s table exactly. |
| Periphrasis strict F1 never exceeds 0.176 | `00_abstract_and_keywords.md`, `05_discussion.md`, `07_conclusion.md`; source `04_results.md` prose line ("periphrasis strict F1 never exceeds 0.176 anywhere in this table") | **Yes.** |
| Antithesis over-claiming, Claude refined-prompt 6 TP / 12 FP | `05_discussion.md` | **Yes** — matches `04_results.md`'s raw TP/FP/FN row ("Antithesis — Claude 6/12/37") for `v4_combined`, and matches `writing/chapters/discussion_draft.md`'s own (frozen, Phase-1-era) citation of the same figure. Not conflated with the *baseline*-prompt figure (Claude TP=5/FP=14), which `04_results.md` cites separately for a different point (the baseline-only "all three models over-claim" observation). |
| استعارة فعل: 83%→62% missed (baseline→refined) | `05_discussion.md`; source `04_results.md` trope subtype table | **Yes**, exact match. |
| استعارة تمثيلية (TEST subtype table, n=24): 33%→29% missed | `05_discussion.md`; source `04_results.md` | **Yes**, exact match. Kept distinct from the *separate* Phase 3 recall-screen figure for the same subtype (next row) — the two are different evaluations (TEST-only vs. pooled DEV+TEST; "% missed" vs. recall) and `05_discussion.md` scopes each to its own source rather than treating them as one number. |
| استعارة تمثيلية (Phase 3 recall screen, n=28): Gemini 0.143 / GPT 0.571 | `05_discussion.md`; source `results/phase3_crossmodel/summary.md` | **Yes**, exact match, explicitly labeled as the recall-screen figure, not the TEST subtype-table figure. |
| كناية لغوية (n=32): Gemini 0.719 / GPT 0.031 | `05_discussion.md`; source `results/phase3_crossmodel/summary.md` | **Yes**, exact match. |
| One-shot→three-shot, استعارة تمثيلية: 15.4%→38.5% | `05_discussion.md`; source `04_results.md` ("a one-shot-versus-three-shot comparison... found recall moving from 15.4% to 38.5%") | **Yes**, exact match. |
| مجاز مرسل: 85% missed under both prompts (n=13, TEST subtype table) | `05_discussion.md`, `06_limitations_and_future_work.md` (implicitly, via "no intervention moved it"); source `04_results.md` | **Yes.** Kept distinct from the separate Phase 3 recall-screen مجاز مرسل figure (n=24, Gemini 0.292/GPT 0.000), which neither `05` nor `06` cites, avoiding a potential number clash. |
| Config C periphrasis: strict F1 0.111→0.316, Imru2 only, run-unstable | `05_discussion.md`, `06_limitations_and_future_work.md`; source `04_results.md` | **Yes**, and both sections correctly scope it as single-poem/DEV-only/unreplicated, matching `04_results.md`'s own hedge. |
| Corpus: 5 poems, 3 TEST / 2 DEV; antithesis n=43, simile n=52 on TEST | `03_data_and_methods.md`, `06_limitations_and_future_work.md` | **Yes**, exact match. |
| 25-subtype screen: 12 of 25 subtypes have n<10 | `04_results.md` ("Twelve of the twenty-five tested subtypes have fewer than ten ground-truth instances"), `06_limitations_and_future_work.md` ("Twelve of the twenty-five subtypes... fall below ten ground-truth instances") | **Yes**, exact match. |

**No numeric discrepancy was found** between any two sections that cite the same figure. Where two sections cite numbers for the same subtype from *different* evaluations (the TEST-only subtype table vs. the pooled-DEV+TEST recall screen — this happens for استعارة تمثيلية and مجاز مرسل), every section that does so states explicitly which evaluation the number comes from; nothing in the current drafts presents the two evaluations' numbers as if they were one figure.

## 2. Terminology consistency

- All nine sections use the corrected English terms (**antithesis** for طباق, **periphrasis** for كناية) throughout their own new prose, per `GLOSSARY.md`'s 2026-07-23 correction. `03_data_and_methods.md` and `04_results.md` each include one explicit parenthetical noting that the underlying *frozen Phase 1 artifact* used the superseded terms ("kenning"/"antonymy") where they cite that artifact's raw output directly — this is the citation convention `GLOSSARY.md` itself specifies, not an inconsistency.
- One subtype-gloss mismatch was found and fixed during this task: `05_discussion.md` initially glossed استعارة تمثيلية as "whole-clause analogy," while `04_results.md`'s own subtype table and `results/phase3_crossmodel/summary.md` both call it "whole-clause allegory." Corrected to "whole-clause allegory" in `05_discussion.md` for consistency with the source tables it cites.
- مجاز (trope) subtype names (استعارة فعل, مجاز عقلي, استعارة تمثيلية, استعارة قديمة, مجاز مرسل) and كناية (periphrasis) subtype names (كناية عن صفة, كناية عن موصوف, كناية لغوية, كناية عن فعل, كناية فنية) are spelled identically everywhere they recur across `04_results.md`, `05_discussion.md`, and `06_limitations_and_future_work.md` — checked by direct string comparison, not just visual inspection.
- The four top-level elements' Arabic terms (مجاز، تشبيه، كناية، طباق) and English glosses (trope, simile, periphrasis, antithesis) are used identically in `00_abstract_and_keywords.md`, `01_introduction.md`, `02_related_work_v2.md`, `03_data_and_methods.md`, `04_results.md`, `05_discussion.md`, and `07_conclusion.md`.

## 3. Research questions answered

| RQ (from `01_introduction.md` / `02_related_work_v2.md`, worded identically in both) | Answered where | Status |
|---|---|---|
| **RQ1** — how accurately can LLMs identify the four elements at the span level? | `04_results.md` (the full P/R/F1 table), restated in `05_discussion.md` ¶1 and `07_conclusion.md` ¶1 | **Answered**, with explicit per-element, per-model numbers. |
| **RQ2** — does accuracy vary systematically by element, and specifically do metaphor/periphrasis (excluded by Abd Alhadi et al. 2023) differ from antithesis (which that system handled well)? | `05_discussion.md` §1 ("A difficulty pattern, not a difficulty scale") | **Answered**, with the added, evidence-supported nuance that antithesis is locatable-but-over-claimed rather than simply "easy" — a more precise answer than a flat yes/no, consistent with what the data actually shows rather than overclaiming a single difficulty axis. |
| **RQ3** — do difficulty patterns hold consistently across models, or vary idiosyncratically, and how does this compare to Kühn et al. (2024) and Attia et al. (2026)? | `05_discussion.md` §"Cross-model consistency and idiosyncrasy" | **Answered** as "both, depending on the grain examined" — element-level consistency, subtype-level idiosyncrasy — with explicit comparison to both cited papers, not just a citation drop. |

All three RQs, as stated identically in `01_introduction.md` and `02_related_work_v2.md`, are directly addressed in `04_results.md` and/or `05_discussion.md`. None is left unanswered or answered only by implication.

## 4. Abstract claims checked against the body

| Abstract claim (`00_abstract_and_keywords.md`) | Supported in body? |
|---|---|
| Simile strict F1 0.65–0.73 for every model | **Yes** — `04_results.md` table, `05_discussion.md` ¶1. |
| Periphrasis never exceeds 0.176 | **Yes** — `04_results.md`, `05_discussion.md` ¶1. |
| Antithesis "locatable but systematically over-claimed, a precision failure rather than a recall one" | **Yes** — `05_discussion.md` ¶1, with raw TP/FP figures. |
| Periphrasis "reachable, though not yet reliably decidable, under a free-form reasoning format" | **Yes** — `04_results.md` Config C section, `05_discussion.md` ¶3, `06_limitations_and_future_work.md`'s reconciliation paragraph — all three use this exact hedge ("reachable but not reliably decided/decidable"), not a stronger claim. |
| "Several rhetorical subtypes are strikingly sensitive to which model is queried and how many worked examples anchor its reading of a category" | **Yes** — `05_discussion.md` §"Prompt sensitivity," citing كناية لغوية, استعارة تمثيلية, and the one-shot/three-shot comparison. |
| Teaser: periphrasis "remains out of reach for every model and prompt tried here" | **Yes**, consistent with the F1≤0.176 ceiling and Config C's non-replication. |

One overclaim was caught and corrected during this task: an earlier draft of the teaser stated that LLMs "find classical Arabic similes almost as well as a rule-based system can" — a direct quantitative comparison to Abd Alhadi, Hussein and Kuflik (2023)'s rule-based system that **no file in this project supports**, since that paper reports only an aggregate precision/recall across all twenty of its categories (0.918/0.902), not a simile-specific figure, and precision/recall is not directly comparable to this paper's own simile F1 in any case. The teaser was rewritten to drop the comparison and state only what the LLM results themselves show.

## 5. In-text citations vs. the merged Works Cited, and the reverse

**Citations used across `01_introduction.md` through `07_conclusion.md`** (union, by source file's own Works Cited list):

Abd Alhadi et al. (2023); Al Kaabi et al. (2024); Attia et al. (2026); Balestrucci et al. (2025); Bender et al. (2023); Cachia (1998); Cohen (1960); Dobson (2021); Fontana (2025); Fuoli et al. (2025); Gutman (2024); Harb (2020); Hayes and Krippendorff (2007); Hicke and Kristensen-McLachlan (2024); Kühn, Mitrović and Granitzer (2024); Kühn and Mitrović (2024, "Elephant in the Room"); Lakoff and Johnson (1980); Münz-Manor and Marienberg-Milikowsky (2023); Qarah (2024); Reimann and Scheffler (2025); Tarkka et al. (2026); Ye et al. (2026); Zirker and Göggelmann (2023).

That is **23 distinct sources**, every one of which appears in `00_merged_references.md`. **No in-text citation across any of the seven content sections (01–07) is missing from the merged Works Cited.**

**Reverse check** (every `00_merged_references.md` entry, used somewhere?): of the 24 main entries in `00_merged_references.md`, **23 are cited** in the sections above. The one exception:

- **Hussein, A. A. (2015) *The Rhetorical Fabric of the Traditional Arabic Qaṣīda*** — present in `00_merged_references.md`, explicitly recommended there for citation in Data and Methods "when introducing Prof. Hussein's scholarly expertise as the corpus's sole annotator," but **`03_data_and_methods.md`'s own Works Cited list only contains Abd Alhadi et al. (2023)** — the Hussein (2015) in-text citation that `00_merged_references.md` recommends was never actually added to `03_data_and_methods.md`'s prose. This is a pre-existing gap in an existing file this task was not permitted to edit (`03_data_and_methods.md` is a read-only input per this task's instructions); flagged here as an open item for whoever next revises that section, not fixed in place.

Additionally, `00_merged_references.md`'s own "Should-cite entries... not yet drawn on" section already flags **Ziemińska (2026)** as recommended but unused; this check confirms that is still accurate — Ziemińska (2026) appears in no section's Works Cited (01 through 08).

## 6. Word counts vs. the DHQ norm

Word counts below exclude each section's own "Works Cited" list and were measured directly from the current files (word-split count, not a prior estimate):

| Section | Body word count |
|---|---|
| `00_abstract_and_keywords.md` | 449 |
| `01_introduction.md` | 1,259 |
| `02_related_work_v2.md` | 2,499 |
| `03_data_and_methods.md` | 1,902 |
| `04_results.md` | 1,918 |
| `05_discussion.md` | 1,647 |
| `06_limitations_and_future_work.md` | 864 |
| `07_conclusion.md` | 408 |
| `08_ai_disclosure.md` | 598 |
| **Total (body text, 00–08)** | **~11,544** |

`literature/notes/dhq_format_guide.md` part (d) recommends a target of **~8,000–10,000 words body**, based on the seven sampled DHQ articles' empirical range (7,000–10,000 words, 15–20 PDF pages including bibliography). The current combined draft, at roughly 11,500 words, runs **about 15–45% over that norm**, depending which end of the range it is measured against. This matches the pattern already flagged in `01_03_04_notes.md` §6, where `03_data_and_methods.md` and `04_results.md` were each already ~7–8% over their own individually requested ranges, for the stated reason that the overage is concentrated in cited numeric/tabular content rather than discursive prose. The same is true of the two new content-heavy sections added here (`05_discussion.md` and `06_limitations_and_future_work.md`, both modestly over their requested per-file targets for the same reason). **At final-draft time, the whole paper will likely need a trimming pass** — most plausibly in `02_related_work_v2.md` (currently the single longest section, and the only one substantially padded with "held in reserve" citations not yet load-bearing in the current argument) rather than in the Results or Discussion sections, where the length is driven by required numeric reporting.

## 7. Outstanding `[TBD]` items across the whole paper draft

Collected from every section (00–08), in one place, for a final-draft checklist:

1. **Inter-annotator agreement figures** (κ, α, span-agreement) — `[TBD]` pending Prof. Hussein's blind re-annotation pass (`03_data_and_methods.md`, `06_limitations_and_future_work.md`).
2. **Corpus/annotation licensing and rights status** — `[TBD]`, blocks a Data Availability statement (`06_limitations_and_future_work.md`; `writing/paper_plan/TOP_5_BLOCKERS.md` item 1, `reviewer_risks.md` §7).
3. **DHQ controlled-vocabulary keywords** (`#dhq_keywords`) — `[TBD]`, the taxonomy XML could not be parsed during this project's format research; needs checking against the live file at submission time (`00_abstract_and_keywords.md`).
4. **DHQ project-registry keywords** (`#project_keywords`) — `[TBD]`, no registry entry exists yet (`00_abstract_and_keywords.md`).
5. **AI-disclosure specifics**: final model roster confirmation, whether AI assisted any Arabic–English translation in the paper, and how much of the paper's own prose was AI-drafted versus human-drafted — all three `[TBD]` in `08_ai_disclosure.md`, each requiring a factual answer from the human author(s), not an estimate.
6. **Hussein (2015) citation missing from `03_data_and_methods.md`'s actual prose** (not a bracketed `[TBD]` in the source file, but functionally an open item — see §5 above).
7. **Ziemińska (2026)** — recommended Should-cite source, not yet used in any drafted section; decide at final draft whether it belongs in Introduction or Conclusion framing, per `00_merged_references.md`'s own note.
8. **Whole-paper length** — likely needs trimming toward the ~8,000–10,000-word DHQ norm (§6 above); not a factual unknown but a drafting task still open.

No other `[TBD]`, placeholder, or unresolved factual claim was found in sections 00–08 beyond the eight items above.
