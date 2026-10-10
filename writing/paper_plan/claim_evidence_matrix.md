# Claim / Evidence Matrix

**Purpose**: every claim in `literature/notes/gap_statement.md` and every research question identifiable from that file and the thesis chapter drafts, mapped against the evidence actually found in this repo's result/experiment files. Status labels: **Supported** (evidence directly confirms the claim at the scale claimed) / **Partly supported** (some evidence exists but is thinner, single-poem, single-model, or not yet at TEST scale) / **Not yet supported** (claim is asserted but no matching evidence was found, or the only evidence contradicts it).

This file does not invent numbers. Every citation below points to an exact file and, where applicable, an exact figure already read from that file in this session.

---

## Part A — Novelty / gap claims (from `literature/notes/gap_statement.md`, `novelty_gap.md`, `dhq_gap_check.md`)

### A1. "No existing study evaluates multiple LLMs on named classical Arabic rhetorical elements, including the semantically-demanding cases rule-based systems exclude, against expert-annotated ground truth with a span-level, difficulty-stratified evaluation."
- **Evidence**: `literature/notes/novelty_gap.md` "Revised gap statement" (2026-10-07) and `literature/notes/dhq_gap_check.md` "Verdict" section — a documented DHQ-only search (DHQ site search tool, all volumes 1–20.3) plus a non-DHQ search (ACL Anthology, arXiv, CHR, JLCL, DSH, targeted Arabic-rhetoric web queries) found no paper doing all of: multi-LLM, named classical balagha categories, classical Arabic poetry, difficulty stratification, expert-vs-model quantified comparison. Closest precedents individually identified and ruled out: Abd Alhadi et al. 2023 (rule-based, not LLM), Al Kaabi et al. 2024 (1 model, 8 examples, qualitative), Attia et al. 2026/Kinayat (22 models, quantified, but modern idioms/proverbs not classical poetry, no span-level task), Kühn et al. 2024 x2 (general rhetorical-figure survey, zero Arabic-language coverage, periphrasis absent from both papers' figure lists).
- **Status**: **Supported**, with the explicit scope caveat already stated in the source document itself: "a screening result... not an exhaustive claim" (`novelty_gap.md`). The claim is accurate as worded in the gap statement as long as the paper keeps that same explicit scoping language (search terms, venues, date of search = 2026-10-07) rather than stating the gap as an unconditional absolute.
- **Reason**: this is the one claim in this matrix with a fully documented, repeatable search trail behind it (queries and hit counts tabulated in `dhq_gap_check.md`).

### A2. "Abd Alhadi, Hussein & Kuflik (2023) explicitly exclude metaphor and periphrasis (kinaya) as too semantically demanding for rule-based matching."
- **Evidence**: cited repeatedly in `gap_statement.md`, `novelty_gap.md`, `related_work_outline.md` §2b ("explicitly excluding metaphor and periphrasis (kinaya) as 'too semantic' for rule-based matching"). The literature-note files cite this as a read finding from the paper itself (per `deep-research-report.md`'s independent corroboration: Abd Alhadi et al. report overall F=0.902 across 20 elements and describe rule-based matching as an interim approach).
- **Status**: **Supported** as a literature claim (i.e., this project's own notes consistently and specifically attribute this exclusion to the source paper) — but this session did not independently re-read Abd Alhadi et al. 2023's PDF to verify the exact wording/exclusion claim; it is taken on the strength of three internally-consistent literature-note files rather than independently re-verified against the primary source in this session.
- **Reason for "Supported" rather than "Partly"**: the claim appears identically and specifically (not vaguely) across three separately-dated literature notes, which is the project's own citation-verification discipline (`CITATION_PLAN.md`/`RELATED_WORK_INDEX.md` referenced as the backing index, not re-opened here) — but a DHQ reviewer will expect the actual quote/page citation from Abd Alhadi et al., which is not reproduced verbatim in any file read this session.

### A3. "Kinayat (Attia et al. 2026) is the closest precedent for multi-model LLM evaluation of Arabic figurative language but does not touch classical poetry, named rhetorical categories, difficulty stratification by element, or span-level identification."
- **Evidence**: `literature/notes/novelty_gap.md`, "Update (2026-10-07)" section, itemizes exactly these four gaps with specifics (22 models vs. Al Kaabi's 1; 325 Egyptian-Arabic-idiom dataset; MCQ/fill-in-blank/connotation tasks, never span identification; stratifies by language/register/task type, not rhetorical category).
- **Status**: **Supported** — this is a direct, specific comparison drawn from a stated "deep-read" of the Attia et al. 2026 paper this session (per the note's own description), not a secondhand characterization.

---

## Part B — Research questions (from `gap_statement.md`)

### B1 (RQ1). "How accurately can current LLMs identify named classical Arabic rhetorical elements (antithesis, periphrasis, metaphor, metonymy) at the span level against expert-annotated ground truth?"
- **Evidence**: Phase 1's frozen TEST numbers answer this for 4 top-level elements (not metaphor/metonymy specifically as separate categories — Phase 1 treats trope as one undifferentiated category): `PROJECT_STATE.md` §3a — strict-criterion F1 ranges from Kenning/Periphrasis 0.051–0.176 (v4_combined) to Simile 0.651–0.727, with Trope 0.242–0.386 and Antonymy/Antithesis 0.145–0.197. Phase 3 (`results/phase3_subelements/MEETING_SUMMARY.md` §6) gives subtype-level recall (not full P/R/F1) for مجاز مرسل specifically: 29.2% recall (n=24), and استعارة تمثيلية: 7.1% recall (n=28) — these are the metaphor/metonymy-subtype-specific numbers RQ1 actually asks for.
- **Status**: **Partly supported**. Top-level element P/R/F1 exists and is TEST-frozen (final). Subtype-level numbers for metaphor/metonymy specifically exist only as **recall** (no precision/F1 — Phase 3 explicitly states "FP/TN/Precision/F1 are not measurable from this run," `MEETING_SUMMARY.md` §4) and only from **one model** (Gemini 3.5 Flash) on an unspecified DEV/TEST mix across all 5 poems pooled, not the frozen 3-poem TEST split specifically.
- **Reason**: RQ1 as phrased names the corrected 4-category scheme (antithesis/periphrasis/metaphor/metonymy) but the only full precision+recall+F1 evidence is for the old 4-category scheme (trope as one category, not split into metaphor/metonymy). The metaphor-vs-metonymy split only has recall-only, single-model Phase 3 data.

### B2 (RQ2). "Do the elements Abd Alhadi et al. excluded as 'too semantic' (metaphor, periphrasis) show a different accuracy/error profile than the surface-marked element they handle well (antithesis)?"
- **Evidence**: `PROJECT_STATE.md` §3a/§3d and `writing/chapters/discussion_draft.md` — Periphrasis/Kenning strict F1 never exceeds 0.176 (v4_combined) anywhere in Phase 1; Antithesis/Antonymy's failure mode is the *opposite* (over-claiming: FP > TP for every model, e.g. Claude baseline TP=5/FP=14, precision 0.263, `PROJECT_STATE.md` §3d) rather than under-detection. The discussion draft explicitly frames this as "a distinct failure mode, not a milder version of the same problem."
- **Status**: **Supported** for the antithesis-vs-periphrasis contrast specifically (both the F1-gap and the precision/recall-direction difference are TEST-frozen, final numbers). **Partly supported** for "metaphor" specifically, since Phase 1 never separately scored متaphor (استعارة) apart from the broader Trope category at the TEST level — the metaphor-specific subtype breakdown that exists (`PROJECT_STATE.md` §3c) is at the Trope-subtype level pooled across TEST, not a separate top-level "metaphor" score, and the Phase 3 metaphor-subtype numbers (مجاز مرسل, استعارة تمثيلية) are recall-only/single-model/DEV-TEST-pooled (see B1).

### B3 (RQ3). "Does evaluating multiple LLMs reveal consistent cross-model difficulty patterns by element, or does difficulty vary idiosyncratically by model, and how does this compare to non-Arabic rhetorical-figure detection (Kühn et al.) and Arabic figurative language more broadly (Attia et al.)?"
- **Evidence (cross-model consistency within this project)**: `PROJECT_STATE.md` §3a shows all 3 models rank Kenning hardest and Simile easiest — a consistent cross-model ordering. §3e (ensemble check) shows the 3 models miss the *same* instances for Trope/Kenning (ensemble F1 identical to best single model), which is itself evidence of a shared, not idiosyncratic, difficulty pattern. §3f/§3g show some genuinely idiosyncratic model behavior under specific interventions (e.g., GPT-5.4-mini swinging to near-total abstention under decomposition, §6.7; Gemini's per-verse Kenning gain not replicating in magnitude across poems while Claude's does, §3g).
- **Evidence (comparison to Kühn et al. / Attia et al.)**: no comparison has actually been computed or written — `novelty_gap.md` only establishes that those papers exist and what they do/don't cover, not a quantitative or qualitative cross-study comparison of difficulty patterns.
- **Status**: **Partly supported** for the within-project cross-model consistency claim (real evidence exists, both for consistency and for specific idiosyncrasies). **Not yet supported** for the comparison-to-other-languages/datasets half of RQ3 — this comparison has not been drafted anywhere in the repo.

---

## Part C — Thesis-draft claims that need checking against RQ framing

### C1. Abstract draft's headline claims (`writing/chapters/abstract_draft.md`)
- "GPT-5.4-mini's F1 nearly quadruples" (Trope) — **Supported**, exact match: `PROJECT_STATE.md` §3a / `results.md` Table 1, Trope GPT-5.4-mini baseline F1=0.065 → v4_combined F1=0.251 (a 3.86x / "+286%" increase, consistent with "nearly quadruples").
- "Kenning remains resistant across every intervention attempted, including per-element and per-verse prompt restructurings" — **Supported** as a Phase-1-only claim (`PROJECT_STATE.md` §3f, §3g). **Important gap**: the abstract and the frozen thesis chapters were written **before** Phase 2's Config C found a real, substantial Kenning/periphrasis recall gain via free-form reasoning (`report_3i.md` §3: Imru2 strict F1 0.111→0.316, token F1 0.111→0.421) — this is new evidence the abstract draft does not reflect, because it predates Phase 2. The abstract's claim is not wrong for what it covers (Phase 1's structural interventions) but is now incomplete as a statement about "every intervention attempted" project-wide. **Flagged explicitly in `results_for_paper.md` below.**
- Abstract uses old terminology throughout (kenning, antonymy) — **by design**, per `GLOSSARY.md`'s explicit rule that Phase 1 documents are not retroactively edited. A new DHQ submission's abstract would need a fresh rewrite using antithesis/periphrasis, not a copy-paste of this draft.

### C2. Discussion draft's "marker-explicitness" hypothesis (`writing/chapters/discussion_draft.md`)
- Claim: "what predicts a model's success is not how conceptually sophisticated a figure is, but whether its surface form gives the model a locatable anchor that forecloses... the literal reading."
- **Evidence**: internally consistent synthesis of §3a (Simile best), §3c (استعارة تمثيلية reversal), §3d (Antithesis over-claiming), §3i (Periphrasis/مجاز مرسل resistant to format-only fixes). All cited figures check out against `PROJECT_STATE.md` on re-reading.
- **Status**: **Partly supported**. This is a well-evidenced *interpretive* hypothesis, not a measured one — it is not independently tested against a held-out prediction (e.g., predicting in advance which of the 23 Phase-3 subtypes would be hard/easy and checking against `final_summary.xlsx`). Phase 3's own findings (`MEETING_SUMMARY.md` §6: مقابلة/تضاد 100% recall, تشبيه مطول/قصير ~90%, كناية نسبة 0%, استعارة تمثيلية 7.1%) are broadly consistent with the marker-explicitness story (markerless/closed-class subtypes score low) but this consistency check has not been written up anywhere as a confirmatory test of the hypothesis — it is an opportunity, not yet a completed analysis. Marked Partly supported rather than Not yet supported because the Phase 3 data, read directly, does not contradict the hypothesis and in fact aligns with it on inspection in this session.

---

## Summary table

| Claim/RQ | Status | Key file(s) |
|---|---|---|
| A1 — DHQ+non-DHQ novelty gap | Supported (scoped) | `novelty_gap.md`, `dhq_gap_check.md` |
| A2 — Abd Alhadi et al. exclude metaphor/periphrasis | Supported (not independently re-verified against primary source this session) | `gap_statement.md`, `novelty_gap.md`, `related_work_outline.md` |
| A3 — Kinayat gap specifics | Supported | `novelty_gap.md` |
| B1 — RQ1 accuracy at span level | Partly supported | `PROJECT_STATE.md` §3a; `results/phase3_subelements/MEETING_SUMMARY.md` §6 |
| B2 — RQ2 differential error profile | Supported (antithesis vs. periphrasis); Partly supported (metaphor specifically) | `PROJECT_STATE.md` §3a/§3c/§3d; `discussion_draft.md` |
| B3 — RQ3 cross-model consistency | Partly supported (within-project); Not yet supported (vs. other studies) | `PROJECT_STATE.md` §3e/§3f/§3g |
| C1 — Abstract draft Kenning claim | Supported but incomplete post-Phase-2 | `abstract_draft.md`; `report_3i.md` §3 |
| C2 — Marker-explicitness hypothesis | Partly supported (interpretive, consistent with data, not formally tested) | `discussion_draft.md`; `MEETING_SUMMARY.md` §6 |
