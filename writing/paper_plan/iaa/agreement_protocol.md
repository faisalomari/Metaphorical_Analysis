# Agreement / Validation Protocol for Ground Truth — Working Design

**Status**: design + tooling only. No second-annotator data exists yet. Every number below is either (a) computed from the existing, frozen ground truth (`data/ground_truth/ali_ana/*.xlsx`, via `experiments/pilot_3models/ground_truth.py`), and is reproducible by re-running `scripts/build_sample.py`, or (b) an explicit placeholder marked `[TBD]`. Nothing here is invented.

---

## 1. What already exists: the adjudication shortlist

`results/phase2_chatlike/ali_adjudication_shortlist.md` — **13 verses**, hand-selected (not randomly sampled) from the full 5-poem corpus, grouped into 4 categories:

- **A (3 verses)** — مجاز مرسل cases where a model found a *different* phrase than the annotated span (same verse, different word/phrase).
- **B (3 verses)** — Kenning/periphrasis cases all 3 Phase-1 models miss entirely.
- **C (3 verses)** — طباق/antithesis cases where models flag something the ground truth does not tag — candidate annotation gaps, not necessarily model error.
- **D (4 verses)** — cases where the 3 models disagree with each other on the same verse.

Source: `results/pilot_3models/detailed_results.docx`'s underlying per-verse scoring data, plus Phase 2's مجاز مرسل probe (`results/phase2_chatlike/report_3i.md` §8). Each row already carries a specific discussion question (A–D, see the shortlist file).

**What this shortlist is for, and what it is not for**: it is a *curated* set, selected specifically because the model(s) and the ground truth disagree (or the models disagree with each other). That selection process is exactly what would bias a kappa/alpha statistic computed from it — the sample is not representative of "typical" verses, it's enriched for disagreement by construction. It is well suited to a **qualitative adjudication session**: a structured conversation with Dr. Hussein about specific, already-identified disagreement patterns, with a concrete question attached to each one. It is **not** suited to producing a defensible, reportable IAA number — a reviewer who checks the sampling method would correctly object that a disagreement-enriched sample will always show more disagreement than chance, which tells you nothing about the ground truth's general reliability.

This protocol therefore treats the shortlist and a proper IAA figure as **two separate deliverables with two separate samples**, not one.

## 2. Two tracks, not one

| | Track 1: Adjudication of model outputs | Track 2: Blind re-annotation (IAA) |
|---|---|---|
| Purpose | Resolve specific known disagreements; decide if a model's alternate reading is defensible, or if the ground truth has a gap | Produce a citable agreement statistic for the paper |
| Sample | The existing 13-verse shortlist | A **new, random, stratified** sample (§3) |
| Blind to GT/predictions? | No — the whole point is to discuss the disagreement | Yes — must be blind for the statistic to mean anything |
| Who | A live session/meeting with Dr. Hussein | Dr. Hussein (self, after a time gap) or an independent second annotator |
| Output | Qualitative verdicts per row, feeding `limitations_future_work.md` / `discussion_draft.md` | Cohen's κ / Krippendorff's α + span-overlap agreement, feeding the Methods section |
| Tooling (this task) | `sheets/adjudication_shortlist_worksheet.xlsx` | `sheets/blind_reannotation_sample.xlsx` + `scripts/compute_agreement.py` |

Both are useful; only Track 2 produces a number a reviewer would accept as "inter-annotator agreement." `writing/paper_plan/reviewer_risks.md` §1 and `experiment_priorities.md` §1 already flag the shortlist as the starting point for *a* session with Dr. Hussein — this protocol keeps that session, but routes its output to the Limitations/Discussion narrative, not to a reported κ/α.

## 3. Track 2 design: sample

**Who can annotate**: realistically, the only person with the subject-matter expertise to re-annotate classical Arabic rhetorical figures at the needed level is Dr. Hussein himself (he is also the paper's co-author and supervisor). An independent second annotator with comparable training does not currently exist on this project (`PROJECT_STATE.md` §5.1 item 2 — "whether this is worth pursuing... is the supervisor's call"). This protocol is therefore designed around the **realistic** option:

> **Dr. Hussein re-annotates a random sample of verses, blind, after a time gap from his original annotation.**

This measures **intra-annotator (self-)agreement/stability**, not independent inter-annotator agreement — that distinction must be stated explicitly and honestly in the paper (see §6's draft paragraph). It is still a meaningful, reportable number: it tells a reviewer whether the ground truth is a stable, repeatable judgment or a noisy one, which is the actual concern "single annotator" raises. If a second, independent annotator becomes available later, the identical sample/sheet/protocol applies unchanged — the tooling does not assume which case it is.

**Sample size and stratification**: computed from the real ground-truth density (`scripts/build_sample.py`, reproduced here):

| Element | Verse-level prevalence across all 224 verses, 5 poems |
|---|---|
| مجاز (Trope) | 140/224 = 62.5% |
| تشبيه (Simile) | 61/224 = 27.2% |
| كناية (Periphrasis) | 123/224 = 54.9% |
| طباق (Antithesis) | 44/224 = 19.6% |

All 4 elements have high enough prevalence that a **plain proportional random sample** (no per-element oversampling needed) gives a usable 2×2 table for every element at a moderate sample size. At **n=80** (stratified proportionally by poem: Imru1 29, Imru2 8, Nabigha 18, Jarir 14, Abu_Tammam 11 — `sheets/sample_manifest.csv`, fixed seed=42, reproducible via `scripts/build_sample.py`), the expected positive-verse counts within the drawn sample are:

| Element | Expected positives in the n=80 sample |
|---|---|
| Trope | 53 |
| Simile | 19 |
| Kenning/Periphrasis | 49 |
| Antonymy/Antithesis | 14 |

Antithesis's 14 is the thinnest cell — still above the common rule-of-thumb floor (≥10 in each 2×2 cell) for a stable kappa, but its confidence interval will be the widest of the four; the paper should report it with that caveat, consistent with this project's standing small-sample discipline (`PROJECT_STATE.md` §6.1). **If a larger, more decisive Antithesis figure is wanted, the fix is to raise the overall sample size (e.g. n=120–150), not to oversample only Antithesis-positive verses** — oversampling by outcome is the same selection-bias problem as §2 flags for the shortlist, just on one element instead of one disagreement pattern.

**Why not all 224 verses**: a full second pass would be the "expensive" option `reviewer_risks.md` §1 already lists — it would produce the most defensible possible IAA figure but at ~3x the annotation burden for a reviewer-facing number that, per the same file, is a "nice-to-have," not a submission blocker. n=80 is sized to be completable in a single sitting or two (§5 of the instruction sheet estimates 1.5–2.5 hours) while remaining large enough that none of the 4 elements lands in a degenerate 2×2 table.

**Important scope note, for the standing TEST-is-spent rule (CLAUDE.md)**: re-annotating verses that happen to fall in the TEST poems (Imru1, Jarir, Abu_Tammam) does **not** violate that rule. The rule protects against re-running or re-scoring *model evaluation* on TEST; this track never touches a model prediction or a frozen TEST number — it only asks whether the ground truth itself is stable. The two are orthogonal, but this is worth stating plainly in the paper so a reader familiar with the DEV/TEST discipline doesn't misread the re-annotation as a TEST violation.

## 4. Label scheme and agreement measures

**Label scheme** (matches the existing ground-truth schema in `ground_truth.py`, so the new data is directly comparable): for each verse × element (4 elements), a binary presence/absence judgment, and — if present — the exact span (the "appearance" text), matching the same `{"span": ..., "primary": ..., "secondary": ...}` shape Dr. Hussein's original annotation uses (subtype capture is optional in the sheet; presence + span is the minimum needed for both measures below).

**Measures, and which is feasible with the data we have**:

1. **Cohen's κ, verse-level binary presence/absence, per element.** Feasible immediately once Track 2's sheet is filled twice (original-vs-rerun, or annotator-A-vs-annotator-B). Standard for exactly 2 raters, which is what this project will have. Implemented in `scripts/compute_agreement.py:cohens_kappa`.
2. **Krippendorff's α, same binary presence/absence data.** Also feasible with 2 raters and no missing data (the general case this implementation supports also handles >2 raters and missing ratings, for no extra cost, in case a 3rd rater is ever added). α and κ estimate chance agreement differently (α pools both raters' marginals, Scott's-π style; κ uses each rater's own marginal) and can diverge, especially with skewed prevalence like Antithesis's 19.6% — **report both**, don't pick one. Implemented in `scripts/compute_agreement.py:krippendorff_alpha_nominal`.
3. **Span-overlap agreement, both strict and token-overlap criteria.** Feasible and *mandatory* per this project's standing scoring discipline (CLAUDE.md: "span-level scoring, both strict and token-overlap criteria... never plain verse-level exists/not-exists") — the same discipline that applies to model evaluation applies here, because verse-level presence/absence alone can agree while the two annotators are pointing at entirely different phrases in the same verse (exactly what shortlist group A documents happening between models and ground truth already — the same failure mode is possible between two human annotators). Reuses `experiments/pilot_3models/span_matching.py`'s `strict_overlap`/`token_match` directly (not reimplemented) for exactly this reason: consistency with how every other span comparison in this project is scored. Implemented in `scripts/compute_agreement.py:span_overlap_agreement` and `span_prf1`.

**Not pursued, and why**: a full adjudicated/merged gold standard (reconciling every disagreement into a single "true" label) is the `reviewer_risks.md` §1 "expensive" option — out of scope for this protocol, which targets a reportable *agreement statistic*, not a corpus revision.

## 5. What this task produced

- `sheets/sample_manifest.csv` — the 80-verse stratified random sample (poem, verse_no), seed=42.
- `sheets/blind_reannotation_sample.xlsx` — the annotation workbook: an "Annotation" tab (80 rows, verse text only, empty label columns, Yes/No dropdown validation), an "Element Definitions" tab (verbatim from `data/elements/*.txt`), and a pointer tab to the instruction sheet. **Blind by construction**: no model prediction, no original ground-truth label, anywhere in this file.
- `sheets/adjudication_shortlist_worksheet.xlsx` — a working xlsx transcription of the existing 13-verse shortlist, with a "verdict" column, for the live Track 1 session.
- `sheets/instructions.docx` — one-page bilingual (Arabic + English) instruction sheet for Track 2, built with the project's shared RTL helpers and visually render-verified per CLAUDE.md.
- `scripts/` — `build_sample.py` (reproduces the stratified sample from ground truth), `build_annotation_sheet.py`, `build_adjudication_worksheet.py`, `build_instructions.py`, `compute_agreement.py` (the analysis script, §4), and `common.py` (shared loaders).
- `tests/test_compute_agreement.py` — dummy-data tests for every function in `compute_agreement.py` (κ, α, span agreement, span P/R/F1, and a round-trip through a synthetic filled sheet), all passing.
- `methods_paragraph_draft.md` — draft paragraph for the paper, numbers as placeholders.

## 6. What Dr. Hussein needs to do

1. **Track 2 (produces the reportable number)**: open `sheets/instructions.docx`, then fill in `sheets/blind_reannotation_sample.xlsx`'s "Annotation" tab — ideally after enough time has passed since the original annotation that recall of the specific verses is unlikely (the original annotation files are in `data/ground_truth/ali_ana/`; he should not reopen them while doing this). Save the completed file as e.g. `sheets/blind_reannotation_sample_ali_rerun_FILLED.xlsx`. Estimated time: 1.5–2.5 hours, splittable across sessions.
2. **Track 1 (feeds Limitations/Discussion, no statistic)**: a single working session (in person or video) going through `sheets/adjudication_shortlist_worksheet.xlsx` row by row, recording his verdict per the discussion question already attached to each row.
3. Once (1) exists, run `python scripts/compute_agreement.py` (it auto-discovers `*_FILLED.xlsx` files in `sheets/`) to get the real κ/α/span-agreement numbers — this fills in `methods_paragraph_draft.md`'s placeholders.
4. **Decision needed from Dr. Hussein / the supervisors, not this task**: whether n=80 is sufficient, or whether a larger sample (and more of his time) is worth it before submission — see `writing/paper_plan/reviewer_risks.md` §1's cheap/moderate/expensive framing.
