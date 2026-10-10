# IAA / Ground-Truth Validation Working Session — Overview

Everything in this directory is new (nothing elsewhere in the repo was modified). See `agreement_protocol.md` for the full design and reasoning; this file is a short index plus the explicit answers to the 5 questions this task was asked to resolve.

## 1. The adjudication shortlist — what it is

`results/phase2_chatlike/ali_adjudication_shortlist.md` (pre-existing, read not written by this task): **13 verses**, hand-selected (not random) from across all 5 poems, grouped into 4 disagreement patterns (A: model found a different مجاز مرسل phrase than annotated, 3 verses; B: all 3 models miss Kenning/periphrasis, 3 verses; C: models flag طباق/antithesis the ground truth doesn't tag, 3 verses; D: models disagree with each other, 4 verses). Source: Phase 1's frozen per-verse scoring data + Phase 2's مجاز مرسل probe. Full detail in `agreement_protocol.md` §1.

## 2. The protocol

Two separate tracks — see `agreement_protocol.md` §2 for why they can't be merged into one sample:
- **Track 1 (qualitative adjudication)**: the existing 13-verse shortlist, discussed live with Dr. Hussein, feeds Limitations/Discussion — not a statistic.
- **Track 2 (quantitative IAA/reliability)**: a new, random, stratified 80-verse sample, re-annotated **blind** by Dr. Hussein after a time gap (the realistic option — no second qualified annotator currently exists on this project). Measured with Cohen's κ, Krippendorff's α (both verse-level binary presence), and span-overlap agreement (strict + token, reusing `span_matching.py`). Full reasoning, including why n=80 and why it's stratified proportionally by poem (not by element), is in `agreement_protocol.md` §3-§4.

**Feasibility, stated plainly**: an independent second annotator is the most defensible design but is not available; this protocol is built around Dr. Hussein re-annotating, which gives **intra-annotator stability**, not independent inter-annotator agreement — the paper must say this explicitly (see `methods_paragraph_draft.md`).

## 3. What was generated

```
writing/paper_plan/iaa/
  agreement_protocol.md          - full protocol design (read this first)
  methods_paragraph_draft.md     - draft paper paragraph, numeric placeholders only
  README.md                      - this file
  sheets/
    sample_manifest.csv                      - the 80 sampled (poem, verse_no) pairs, seed=42
    blind_reannotation_sample.xlsx           - BLIND annotation workbook (Track 2) - fill this in
    adjudication_shortlist_worksheet.xlsx    - working copy of the 13-verse shortlist (Track 1)
    instructions.docx                        - one-page AR+EN instructions for Track 2
  scripts/
    common.py                      - shared loaders (poem text, ground truth, labels)
    build_sample.py                - reproduces sample_manifest.csv from ground truth
    build_annotation_sheet.py      - builds blind_reannotation_sample.xlsx
    build_adjudication_worksheet.py- builds adjudication_shortlist_worksheet.xlsx
    build_instructions.py          - builds instructions.docx (uses rtl_utils.py)
    compute_agreement.py           - kappa / alpha / span-agreement, run once Track 2 is filled in
  tests/
    test_compute_agreement.py      - dummy-data tests for compute_agreement.py (all passing)
```

No API calls, no cost, nothing touches TEST-poem model evaluation (see `agreement_protocol.md` §3's scope note on why re-annotating TEST-poem verses for *ground-truth* reliability doesn't conflict with the TEST-is-spent rule).

## 4. What Dr. Ali Hussein needs to do

1. Read `sheets/instructions.docx` (one page, Arabic + English).
2. Fill in `sheets/blind_reannotation_sample.xlsx`'s "Annotation" tab (80 verses, ~1.5-2.5 hours), without reopening the original `data/ground_truth/ali_ana/` files while doing so. Save as `sheets/blind_reannotation_sample_<something>_FILLED.xlsx`.
3. Separately, join a working session (any format) to go through `sheets/adjudication_shortlist_worksheet.xlsx` row by row and record a verdict for each of the 13 rows' attached question.
4. Decide (with the supervisors) whether n=80 is enough or a larger sample is worth the extra time, per `agreement_protocol.md` §6 item 4.

Once step 2's file exists, run:

```bash
python writing/paper_plan/iaa/scripts/compute_agreement.py
```

which auto-discovers the filled sheet(s) and prints the real κ/α/span-agreement numbers (no numbers are invented anywhere in this deliverable — every placeholder in `methods_paragraph_draft.md` stays a placeholder until this script actually runs on real data).

## 5. No numbers invented

Every count in `agreement_protocol.md` (prevalence percentages, sample-size breakdown by poem, expected-positives-per-element) is reproducible by running `scripts/build_sample.py` and is computed directly from the existing, frozen ground truth via `experiments/pilot_3models/ground_truth.py` — none of it is estimated or guessed. `methods_paragraph_draft.md`'s actual agreement numbers (κ, α, span-agreement rates) do not exist yet and are marked `[TBD]` throughout; they are not filled in with placeholder or illustrative values anywhere in this deliverable.
