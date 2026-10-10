# Results for the Paper — What a DHQ Submission Could Actually Report

Every row below cites its exact source file. Status tags: **final** (TEST, frozen, spent, per `PROJECT_STATE.md` §2), **preliminary** (DEV or supplementary, not validated at TEST scale), **incomplete** (partial data — missing runs, single-model only, recall-only, etc.).

---

## Table 1 — Frozen TEST results (final): strict-criterion P/R/F1, pooled across Imru1+Jarir+Abu_Tammam

**Source**: `PROJECT_STATE.md` §3a; reproduced identically in `writing/chapters/results.md` Table 1. Ground-truth support (deduped): Trope=179, Simile=52, Kenning=147, Antonymy=43.

| Element (Phase-1 term → corrected term) | Model | Baseline P/R/F1 | v4_combined P/R/F1 | Status |
|---|---|---|---|---|
| Trope → Trope (umbrella, uncorrected subtype split) | Claude Sonnet 4.6 | 0.85/0.09/0.171 | 0.89/0.14/0.242 | **final** |
| Trope | GPT-5.4-mini | 0.86/0.03/0.065 | 0.64/0.16/0.251 | **final** |
| Trope | Gemini 3.5 Flash | 0.89/0.19/0.313 | 0.83/0.25/0.386 | **final** |
| Simile → Simile | Claude Sonnet 4.6 | 0.82/0.54/0.651 | 0.82/0.54/0.651 | **final** |
| Simile | GPT-5.4-mini | 0.88/0.58/0.698 | 0.91/0.60/0.721 | **final** |
| Simile | Gemini 3.5 Flash | 0.82/0.62/0.703 | 0.89/0.62/0.727 | **final** |
| Kenning → Periphrasis | Claude Sonnet 4.6 | 0.80/0.05/0.102 | 0.57/0.05/0.099 | **final** |
| Kenning → Periphrasis | GPT-5.4-mini | 0.20/0.01/0.013 | 0.36/0.03/0.051 | **final** |
| Kenning → Periphrasis | Gemini 3.5 Flash | 0.69/0.06/0.113 | 0.65/0.10/0.176 | **final** |
| Antonymy → Antithesis | Claude Sonnet 4.6 | 0.26/0.12/0.161 | 0.33/0.14/0.197 | **final** |
| Antonymy → Antithesis | GPT-5.4-mini | 0.27/0.09/0.138 | 0.23/0.12/0.154 | **final** |
| Antonymy → Antithesis | Gemini 3.5 Flash | 0.17/0.09/0.121 | 0.19/0.12/0.145 | **final** |

Raw TP/FP/FN (strict, v4_combined) — `writing/chapters/results.md` Appendix:
Trope: Claude 25/3/154, GPT 28/16/151, Gemini 45/9/134. Simile: Claude 28/6/24, GPT 31/3/21, Gemini 32/4/20. Kenning: Claude 8/6/139, GPT 4/7/143, Gemini 15/8/132. Antonymy: Claude 6/12/37, GPT 5/17/38, Gemini 5/21/38.

**Note on terminology column**: these rows use Phase 1's original, now-superseded terms (kenning, antonymy) because the number was produced under that terminology and is frozen (`GLOSSARY.md`'s citation convention: cite under corrected name with the original noted). A DHQ submission's results table should use antithesis/periphrasis as the primary labels with a footnote tracing provenance to this file.

---

## Table 2 — Trope subtype breakdown (final, TEST, pooled)

**Source**: `PROJECT_STATE.md` §3c; `results.md` Table 2.

| Subtype | n (TEST) | Baseline missed | v4_combined missed | Status |
|---|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | 62% | **final** |
| مجاز عقلي (rational trope) | 41 | 83% | 66% | **final** |
| استعارة تمثيلية (whole-clause allegory) | 24 | 33% | 29% | **final** |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% | **final** |
| مجاز مرسل (metonymy, single lexicalized word) | 13 | 85% | 85% | **final** |
| استعارة حديثة | 4 | 75% | 75% | **final** (n=4, too thin to generalize) |

---

## Table 3 — Phase 3 subtype recall-only results (incomplete: recall only, single model, pooled DEV+TEST)

**Source**: `results/phase3_subelements/MEETING_SUMMARY.md` §6, `final_summary.xlsx` (not re-opened; table below reproduces only what the Markdown summary states explicitly).

| Subtype | n | Recall | Model | Status |
|---|---|---|---|---|
| مقابلة (تضاد) | 4 | 100% | Gemini 3.5 Flash | **incomplete** — recall only, n=4 too thin |
| كناية لغوية | 32 | 90.6% | Gemini 3.5 Flash | **incomplete** — recall only |
| تشبيه مطول | 30 | 90% | Gemini 3.5 Flash | **incomplete** — recall only |
| تشبيه قصير | 13 | 92.3% | Gemini 3.5 Flash | **incomplete** — recall only, n=13 |
| كناية نسبة | 4 | 0% | Gemini 3.5 Flash | **incomplete** — recall only, n=4 too thin |
| استعارة تمثيلية مبنية على الكناية | 2 | 0% | Gemini 3.5 Flash | **incomplete** — n=2, not usable for any claim |
| استعارة تمثيلية | 28 | 7.1% | Gemini 3.5 Flash | **incomplete** — recall only. Note the DEV→full-scale reversal explicitly flagged in the source (looked fine at n=4 DEV, collapsed at n=28 full) |
| مجاز مرسل | 24 | 29.2% | Gemini 3.5 Flash | **incomplete** — recall only |
| طباق في المعنى | 8 | 25% | Gemini 3.5 Flash | **incomplete** — recall only, n=8 |
| مجاز عقلي | 54 | 56% | Gemini 3.5 Flash | **incomplete** — recall only, but consistent with Table 2's TEST-scale finding that this subtype is a genuine, Phase-1-replicated hard case |
| كناية بسيطة | 9 | 88.9% (8/9 TP) | Gemini 3.5 Flash | **incomplete** — recall only, n=9 |
| كناية فنية | 10 | 50% (5/10 TP) | Gemini 3.5 Flash | **incomplete** — recall only, n=10 |

**This entire table cannot be reported as F1 or compared directly to Tables 1–2**, because the Phase 3 design shows every model only known-positive lines for a subtype — no negative examples, so FP/TN/precision/F1 are structurally unmeasurable from this run (`MEETING_SUMMARY.md` §4, explicit limitation acknowledged in the source). A DHQ reviewer would immediately ask for precision; the answer is "not measured, by design, in this round." The source also documents a few-shot follow-up (`fewshot_comparison.xlsx`, 984 calls, $1.974) finding few-shot mostly *hurts* recall (10 of 13 subtypes worse) — real additional evidence, same recall-only caveat.

---

## Table 4 — Phase 2 Config A/B/C disentanglement (preliminary, DEV only — Imru2 + Nabigha probe)

**Source**: `results/phase2_chatlike/report_3i.md` §2, §3, §8.

### Pooled DEV (Imru2+Nabigha), strict criterion, TP/FP/FN, F1

| Element | Existing (Sonnet+v4) | Config A (Fable5+v4) | Config B (Sonnet+v4, terms corrected) | Status |
|---|---|---|---|---|
| Trope | 2/6/58, F1=0.059 | 7/3/53, F1=0.200 | 3/4/57, F1=0.090 | **preliminary** — DEV only |
| Simile | 14/7/6, F1=0.683 | 14/6/6, F1=0.700 | 14/7/6, F1=0.683 | **preliminary** |
| Kenning | 5/3/64, F1=0.130 | 8/4/61, F1=0.198 | 5/7/64, F1=0.123 | **preliminary** |
| Antonymy (n=5, too thin) | 1/6/4, F1=0.167 | 1/4/4, F1=0.200 | 0/4/5, F1=0.000 | **incomplete** — n=5 |

### Imru2-only, strict criterion, including Config C

| Element | Existing | Config A | Config B | Config C (2-stage, free-form) | Status |
|---|---|---|---|---|---|
| Trope | 2/0/6, F1=0.400 | 1/1/7, F1=0.200 | 2/1/6, F1=0.364 | 2/13/6, F1=0.174 | **preliminary** — single-poem |
| Simile | 5/5/0, F1=0.667 | 4/5/1, F1=0.571 | 5/5/0, F1=0.667 | 4/6/1, F1=0.533 | **preliminary** |
| Kenning | 1/0/16, F1=0.111 | 1/3/16, F1=0.095 | 2/2/15, F1=0.190 | **6/15/11, F1=0.316** | **preliminary** — single poem, and this is Config C's headline Kenning/periphrasis result |
| Antonymy (n=1) | 0/1/1, F1=0.000 | 0/2/1, F1=0.000 | 0/1/1, F1=0.000 | 0/3/1, F1=0.000 | **incomplete** — n=1, uninterpretable |

**Config C is not run on full DEV** (Nabigha's full-poem Config C run was never executed — budget-held at ~$11.9 estimate, `report_3i.md` §7/Phase 2 §4 item 1). What exists instead for Nabigha is a **targeted recall probe** (11 hand-picked verses, known-positives only, no precision/F1 possible by design): "4 of 10 known-positive مجاز مرسل verses caught in at least one of 2 runs (any-of-2-runs convention); under the project's own standard 2-run-majority convention this collapses to 1/10 strict, 0/10 token" (`report_3i.md` §8–§9). **This run-to-run instability is itself a headline finding, not just a caveat** — flagged explicitly in the source as "the finding, not a methodological inconvenience to paper over."

---

## Table 5 — Cost-efficiency and run-consistency figures (final, derived from frozen TEST + DEV supplementary data)

**Source**: `PROJECT_STATE.md` §3g, §9 of `results.md`.

| Configuration | Micro F1 (strict, Imru2) | Cost (Imru2, 2 runs, 3 models) | F1/$ | Status |
|---|---|---|---|---|
| Whole-poem, all-4-elements (v4_combined) | 0.333 | $0.156 | 2.14 | **final** (Phase 1 adopted method) |
| Whole-poem, decomposed (single-element) | 0.308 | $0.243 | 1.27 | **preliminary** — DEV supplementary |
| Per-verse, all-4-elements (Mode A) | 0.398 (best accuracy) | $0.804 | 0.50 | **preliminary** |
| Per-verse, decomposed (Mode B) | 0.351 | $1.128 | 0.31 (worst) | **preliminary** |

Total realized API spend, entire Phase 1 pilot cycle: **$8.29 across 1,134 calls** (`PROJECT_STATE.md` §1). Phase 2 §3i total: **$7.23** (Config A $1.91 + B $0.27 + C-Imru2 $5.05) + Nabigha probe **$2.73** = **$9.96** Phase 2 total so far. Phase 3: **~$2.96** total across both passes (first pass actual Google billing ~$7.5–8.6 due to an uncounted-thinking-token bug later fixed; second, corrected pass $2.0071) + few-shot follow-up $1.974.

---

## Discrepancies between chapter drafts and underlying source numbers

Checked every number quoted in `abstract_draft.md`, `results.md`, and `discussion_draft.md` against the files they cite. **No numeric discrepancy was found** — every figure in the three chapter drafts traced back exactly to `PROJECT_STATE.md` or a results file, including the one arithmetic correction already self-documented in the source (`PROJECT_STATE.md` §6.9: Gemini's Imru2 Kenning delta corrected from "+136%" to "+152%," and the corrected figure is what appears in `results.md` §7 Table 3).

**The one substantive gap is not a numeric discrepancy but a completeness gap**: `abstract_draft.md` and `limitations_future_work.md` both state, in effect, "kenning remains resistant across every intervention attempted" — true as a description of Phase 1's structural interventions (decomposition, per-verse granularity), but written before Phase 2's Config C existed, which **did** find a real (if run-to-run-unstable) Kenning/periphrasis recall gain via free-form reasoning (`report_3i.md` §3). A DHQ submission drafted from these chapters as-is would materially understate what has since been found. See `claim_evidence_matrix.md` C1 for the full statement of this gap, and `paper_mapping.md` for what needs rewriting as a result.

**A second completeness note, not a contradiction**: `limitations_future_work.md` §1 states ground truth is single-annotator with "no inter-annotator agreement figure exists anywhere in this project" — this remains true as of every file read in this session; no IAA figure was found anywhere in `results/` or `experiments/`.
