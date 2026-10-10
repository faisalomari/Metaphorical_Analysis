This file proposes new content for `PROJECT_STATE.md`. **Not merged into
PROJECT_STATE.md by this task** — only this standalone file was written, per
instruction. Drop this in as a new subsection (e.g. after the Phase 3
section, as "Phase 3 cross-model") if/when you want it made official.

---

## Phase 3 cross-model (sub-element recall, GPT-5.4-mini added) — 2026-10-07

Following Phase 3's sub-element recall work (Gemini 3.5 Flash only), ran the
identical 570-row, 25-subtype task on **GPT-5.4-mini** for comparison, and
re-scored Gemini's existing data with a stricter span-level check. **Claude
Sonnet 4.6 was not run** (cost — see below); only GPT-5.4-mini was added.

**Status: done for GPT-5.4-mini; Claude Sonnet 4.6 intentionally deferred.**

**Key facts**:

1. **Precision and F1 are undefined by this experiment's design, for every
   model including Gemini — not a gap to fill with more compute, a property
   of how the data was collected.** Every row is a line already tagged
   positive for its own subtype by Dr. Hussein; no model was ever shown a
   negative example for any subtype. TP/FN/Recall are real; FP/TN/Precision/F1
   cannot be computed without a new negative-sampling experiment (designed
   in concept, not run). Do not report P/F1 numbers for this task under any
   circumstances — see `results/phase3_subelements/score_subtypes.py` and
   `results/phase3_crossmodel/summary.md` for the full reasoning.
2. **The original Gemini recall numbers (`recall_by_subtype.xlsx`) were
   verse-level (exists=true/false only), which is the exact scoring artifact
   CLAUDE.md's standing discipline (#4) warns against.** Re-scored both
   models at the span level instead (model's claimed span must actually
   overlap the ground-truth span, strict + token criteria) — this pulled
   recall down substantially for several subtypes (e.g. Gemini استعارة فعل:
   naive 0.627 → strict 0.264) and should be treated as the more honest
   number going forward. See `results/phase3_crossmodel/per_subtype_table.xlsx`.
3. **GPT-5.4-mini scores strictly lower than Gemini on 10 of 13 reliable
   (n≥10) subtypes, and strictly higher on the other 3** under the strict
   criterion (no ties) — consistent with Phase 1's
   existing finding that Gemini was the best/near-best of the original 3
   models on most elements, the reason Phase 3 picked Gemini in the first
   place.
4. **Two subtype-level results worth a closer look, not yet explained**:
   - **كناية لغوية (linguistic ellipsis periphrasis): Gemini 0.719 strict
     recall → GPT-5.4-mini 0.031, n=32** — near-total GPT failure (2/32 both
     runs) on a subtype Gemini handles well. Not yet investigated whether
     this is a real capability gap or a narrower prompt/formatting issue
     specific to this one subtype.
   - **استعارة تمثيلية (unmarked whole-clause allegory): Gemini 0.143 → GPT
     0.571, n=28** — the one subtype where GPT clearly beats Gemini, and by
     a large margin. This is the same subtype already flagged twice before
     for surprising, sample-size-sensitive behavior (Phase 1's DEV→TEST
     reversal, `PROJECT_STATE.md` §3c; Phase 3's own small-sample optimism
     collapse, `MEETING_SUMMARY.md` §6) — a third surprise on the same
     subtype. GPT's own 2 runs agree closely (20/28 and 19/28 "yes"; strict
     TP=16/FN=12), so it isn't single-run noise within GPT's data, but it's
     still one model pair on one sample — treat the Gemini/GPT reversal
     itself as provisional until cross-checked further.
5. **12 of 25 subtypes have n<10** (flagged, not excluded, in the table) —
   same thin-sample caveat this project applies everywhere; none of these
   should be quoted as a standalone finding.
6. **No provider errors or refusals.** GPT-5.4-mini: 1,140/1,140 calls
   succeeded, $0.9842 actual spend (estimate was $1.34, hard cap was $1.60 —
   neither was reached).
7. **Claude Sonnet 4.6 was priced out, not run**: ~$4.96-5.64 estimated for
   the same 570-row/2-run task (`cost_estimate.md`'s options table) — a
   separate decision/spend if wanted later. Fable 5 was never under
   consideration here (cost, same reasoning as Phase 3's original exclusion).

**Where it lives**: `experiments/phase3_crossmodel/` (code — `run_crossmodel.py`,
`score_crossmodel.py`, `build_report.py`), `results/phase3_crossmodel/`
(`summary.md`, `per_subtype_table.xlsx`, `cost_estimate.md`,
`summary_openai.json`, `raw/`).
