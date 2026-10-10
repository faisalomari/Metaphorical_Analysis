# Phase 3 (sub-rhetorical elements) — meeting summary, 2026-08-12

Read this before the meeting. Full detail and all data live under
`results/phase3_subelements/` and `experiments/phase3_subelements/` — this
file is the orientation layer, not the source of truth for numbers (that's
`final_summary.xlsx`).

## 1. What this phase is

Following the meeting on 2026-08-09, the goal shifted from "does element X
exist in this verse" (Phase 1/2) to "which **sub-type** of element X exists,
line by line." Two source documents were used to build the sub-type
taxonomy:

- `arabic rhetoric.pptx` (Ali Ahmad Hussein's Haifa University course slides)
- `"Statistical Development of the Use of Rhetorical Elements in Classical
  Arabic Poetry"` (Hussein, *Journal of Arabic Literature*, 2025) — its
  glossary (pages 27-38) gives precise definitions, transliterations, and
  examples for every subtype.

Both sources were cross-checked against each other and against this
project's existing four elements (طباق antithesis, تشبيه simile, مجاز
trope/كناية periphrasis — `GLOSSARY.md`).

## 2. The taxonomy built

~35 candidate sub-branches were catalogued across the 4 main elements (full
table given earlier in this conversation). Cross-referencing that taxonomy
against Dr. Hussein's actual ground-truth annotations
(`data/ground_truth/ali_ana/original/*.xlsx`, 5 poems) found:

- **23 subtypes** with both a clear definition/example AND ≥2 ground-truth
  occurrences — these are what got tested.
- **5 subtypes present in the ground truth but with NO definition in either
  source**: `كناية فنية`, `كناية بسيطة`, `تشبيه غريب`, `مقابلة نحوية`, and a
  generic `تشبيه` (no subtype specified). 45 lines total. **Excluded from
  the first round per your explicit instruction** ("استبعدها بسبب انها بدون
  تعريف").
  - **Update (post-meeting, same day)**: per Dr. Ali Hussein's direction,
    `كناية فنية` and `كناية بسيطة` are counted as plain كناية with no
    subtype — tested against the project's general/parent-level periphrasis
    definition (`data/elements/Kenning.txt`, unchanged) instead of a
    subtype-specific one. Results: كناية بسيطة 88.9% recall (8/9 TP),
    كناية فنية 50% recall (5/10 TP). Now included in `final_summary.xlsx`
    (25 subtypes, 570 rows total) and have their own files in
    `xlsx_results/`.
  - **Still open**: `تشبيه غريب`, `مقابلة نحوية`, and generic `تشبيه` (36
    lines) — still need direction before they can be tested.
- **7 subtypes** with only 1 ground-truth occurrence — too thin to test
  meaningfully, excluded.

One naming note worth flagging: `كناية عائلة` (family periphrasis) is,
by Hussein's own account in the paper, **his own suggested term** — classical
scholars always called this construction periphrasis even though it's
logically a metaphor. Not a concern, just worth knowing the term's provenance
if it comes up.

## 3. Data prepared

- `data/ground_truth/by_subtype/<subtype>.xlsx` — 28 files (23 tested + 5
  excluded-but-extracted for later), each a full slice of the ground truth
  filtered to that one subtype, tagged with DEV/TEST split and source poem.
- `experiments/phase3_subelements/subtype_defs.py` — the 23 tested subtypes'
  definitions + one canonical example each, sourced from the two documents
  above.

## 4. Method: what was actually measured

For each of the 23 subtypes, every ground-truth line already tagged with
that subtype was sent to the model with a subtype-specific prompt (system
message = ONLY that subtype's definition + example, no outside knowledge)
asking a strict yes/no + a required 1-3 sentence Arabic justification. 2
runs per line (project's 2-run-minimum rule), DEV first as a pilot, then the
full 551-line set.

**Important limitation, worth stating plainly at the meeting**: this design
only tests **recall** — every line is a known positive for its own subtype,
so we get TP/FN honestly, but **FP/TN/Precision/F1 are not measurable from
this run** (no negative examples were shown to the model for any subtype).
Getting real F1 needs a follow-up experiment (e.g. testing each subtype's
prompt against *other* subtypes' lines as negatives) — designed but not
run, pending your/the supervisor's direction.

## 5. Model used and why

**Gemini 3.5 Flash** (not Fable 5 — explicitly ruled out for cost, $10/$50
per MTok vs Gemini's $1.50/$9.00). Chosen because it was the best or
near-best of the 3 models already validated in Phase 1 on Trope/Kenning/
Simile (`PROJECT_STATE.md` §3a), at roughly half Claude Sonnet 4.6's price
and with the highest run-to-run consistency of the three.

## 6. Results (2-run majority, matches `analyze.py`'s convention: a 1-1
split counts as FN, not a coin flip)

Full table: `results/phase3_subelements/final_summary.xlsx`. Headlines:

| High recall (model + definition agree easily) | Low recall (model struggles even with the definition) |
|---|---|
| مقابلة (تضاد) 100% (n=4) | كناية نسبة 0% (n=4) |
| كناية لغوية 90.6% (n=32) | استعارة تمثيلية مبنية على الكناية 0% (n=2) |
| تشبيه مطول 90% (n=30) | استعارة تمثيلية 7.1% (n=28) |
| تشبيه قصير 92.3% (n=13) | مجاز مرسل 29.2% (n=24), طباق في المعنى 25% (n=8) |

Two findings worth flagging as methodologically interesting, not just noise:

- **استعارة تمثيلية looked fine on the small DEV sample (n=4) but collapsed
  at full scale (n=28, 7.1%)** — this is the *exact same DEV→TEST reversal
  pattern* already documented for a different subtype in Phase 1
  (`PROJECT_STATE.md` §3c). Second time this project has seen small-sample
  DEV analysis point at the wrong conclusion.
- **مجاز عقلي (54 ground-truth lines) is a real, well-defined subtype that
  was missing from my first taxonomy pass** (not in either source's
  "official" subtype list) but turned out to already be tracked in Phase 1
  (`PROJECT_STATE.md` §3c, "rational trope"). Its 56% recall here lines up
  with Phase 1's finding that it's a genuinely hard subtype for these
  models, not a broken prompt.

## 7. Cost — full transparency

Two separate spend events this session, tracked differently:

1. **DEV pilot + TEST run** (the first pass, no reasoning field): reported
   as $0.2332 + $0.7238 = $0.957, but that number is **known to be wrong
   (undercounted)** — see the bug below. The real charge on your Google AI
   Studio account for this pass was **~28-32 NIS (~$7.5-8.6)**, which is what
   took your balance from 19 NIS to -13.66 NIS. Already paid via your
   subsequent top-up; not part of the 36 NIS below.
2. **The final, reasoning-enabled full re-run** (all 551 lines, cost-tracking
   bug fixed): 1 small verification call ($0.0032) + the full run ($1.9991)
   + 1 retry for a truncated response ($0.0048) = **$2.0071 (~7.3 NIS)**,
   spent out of the fresh 36 NIS top-up. **≈28.7 NIS remains untouched.**

**A real bug was found and fixed mid-session** (this is what caused event 1's
number to be wrong): Gemini 3.5 Flash bills
internal "thinking" tokens (`thoughts_token_count`) at the output rate, but
the cost-tracking code (inherited from Phase 1's harness) only read the
visible-answer token count and silently dropped thinking tokens. This is why
an early estimate ($0.96) diverged sharply from the real AI Studio charge
(~28 NIS/~$7.5). Fixed in `experiments/phase3_subelements/providers_fixed.py`
(kept separate from Phase 1's frozen `pilot_3models/providers.py` so Phase 1
reproducibility is untouched): now bills thinking tokens correctly AND sets
`thinking_level="minimal"` to keep them small, since this task doesn't need
deep internal reasoning. **This bug may also mean historical Gemini cost
figures elsewhere in this project were undercounted** — not fixed
retroactively (those are frozen artifacts), but worth being aware of if
anyone audits old Gemini spend.

## 8. Where everything is

- `results/phase3_subelements/final_summary.xlsx` — **start here**: n/TP/FN/
  Recall per subtype, links to detail files.
- `results/phase3_subelements/xlsx_results/<subtype>.xlsx` — 23 files, one
  per subtype: every ground-truth line + both runs' full model response
  (exists/appearance/reasoning) + verdict.
- `results/phase3_subelements/raw/<subtype>_all.jsonl` — raw API records
  behind the xlsx files.
- `data/ground_truth/by_subtype/` — the 28 ground-truth slices (input side).
- `experiments/phase3_subelements/` — all code (subtype definitions, prompt
  builder, runner, scoring).

## 8b. Follow-up: one-shot vs few-shot (post-meeting, 2026-08-12)

Built a 3-shot version (1 original textbook example + 2 real-corpus examples,
held out of testing) for the 13 subtypes with enough volume to spare 2
examples (n>=10). Cost $1.974 (984 calls). Full table:
`results/phase3_subelements/fewshot_comparison.xlsx`.

**Headline: few-shot mostly hurt recall.** 10 of 13 subtypes got worse
(استعارة فعل -23.1pp, مجاز عقلي -17.3pp, مجاز مرسل -18.1pp, كناية لغوية -14.0pp
among the largest drops), 1 flat, only 3 improved — and those 3 were exactly
the subtypes where one-shot was already failing badly (استعارة تمثيلية:
15.4%->38.5%, كناية فنية: 37.5%->62.5%, تشبيه قصير: 90.9%->100%). Reading:
extra real-corpus examples seem to help only when the model didn't grasp the
category at all from one example, but otherwise make it pattern-match toward
the specific (noisier) extra examples instead of the general definition -
this echoes the same real-corpus-example risk already flagged elsewhere in
this project (`PROPOSAL_fewshot.md`'s contradiction). **Recommendation: don't
default to few-shot with real-corpus examples for this task; one-shot with a
clean textbook example is the safer default**, few-shot only as a targeted
fix for specific subtypes already shown to be failing.

## 9. Open questions for the meeting

1. ~~Definitions needed for the 5 excluded subtypes~~ — `كناية فنية`/`كناية
   بسيطة` resolved (counted as plain كناية, tested, see §2 update). Still
   need direction on `تشبيه غريب`, `مقابلة نحوية`, generic `تشبيه`.
2. Is recall-only sufficient for this round, or is real Precision/F1 (via a
   negative-sampling follow-up) needed before drawing conclusions?
3. Direction on the low-recall subtypes (استعارة تمثيلية, كناية نسبة,
   مجاز مرسل, طباق في المعنى) — model limitation, definition-wording issue,
   or genuinely hard/ambiguous cases worth a closer manual look?
4. Whether to extend this sub-type analysis to more poems beyond the
   original 5, once the above is settled.
