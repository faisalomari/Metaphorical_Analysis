# Phase 3 cross-model — summary (2026-10-07)

**Scope actually run**: Option A only, per explicit instruction — **GPT-5.4-mini**,
full 570-row Phase 3 subtype set (same 25 subtypes, same prompts/data,
unchanged), **2 runs**, temperature 0.0. **Claude Sonnet 4.6 was NOT run.**

**Actual spend: $0.9842** (1,140/1,140 calls succeeded, 0 failures/retries) —
under both the $1.34 estimate and the $1.60 hard cap; the cap was never hit,
so nothing was aborted. Raw data: `results/phase3_crossmodel/raw/openai/`,
run log: `results/phase3_crossmodel/summary_openai.json`.

**Gemini's existing data was re-scored, not re-run** (zero new API calls for
Gemini) — see "Methodology" below for what changed in that re-score.

---

## Precision and F1: undefined by design, for both models — not computed, not estimated

Every row in this dataset (for Gemini originally, and now for GPT-5.4-mini
on the identical rows) is a line **Dr. Hussein already tagged as positive**
for its own subtype. No model was ever shown a line that is NOT that
subtype, for any subtype. That means:

- **TP, FN, and Recall are real and honestly measured** — reported below.
- **FP, TN, Precision, and F1 are mathematically undefined, not just
  unmeasured** — there is no negative sample in this data to compute a false
  positive from, for either model. They are **not** reported as 0, not
  estimated, and not approximated anywhere in this deliverable (consistent
  with `experiments/phase3_subelements/score_subtypes.py`'s original finding
  and the already-recorded limitation in `MEETING_SUMMARY.md` §4).

Getting real Precision/F1 for either model would need a new negative-sampling
follow-up (testing each subtype's prompt against other subtypes' lines as
negatives) — out of scope for this task, not run, not estimated here.

## Methodology note: this re-score is NOT identical to the original recall_by_subtype.xlsx

The original Phase 3 recall (`results/phase3_subelements/recall_by_subtype.xlsx`)
counted a row as a true positive whenever the model said `exists=true` by
2-run majority — a **verse-level** check, exactly the kind of scoring
artifact CLAUDE.md's standing discipline (#4) warns against ("never plain
verse-level exists/not-exists... produces artifacts"). This deliverable
re-scores **both** models' data at the **span level** instead
(`experiments/phase3_crossmodel/score_crossmodel.py`, using Phase 1's
`span_matching.best_match`, strict substring + token-overlap≥0.5): a row
only counts as a true positive if the model's `appearance` span actually
overlaps the ground truth's own annotated span (`span` field), not just if
the model said yes for some reason.

**This matters a lot in practice.** Spot-checking GPT/Gemini "yes" answers
against their claimed span vs. the ground-truth span surfaced real
mismatches — e.g. one row's ground truth span is `جاشت`, the model said
"yes, exists" but pointed at `ترمي` (a different word in the same verse).
The model may be detecting a real instance of the subtype elsewhere in a
verse that has more than one candidate figure, while missing the specific
one Dr. Hussein annotated — a verse-level "yes" doesn't distinguish these
cases, span-level scoring does. Across subtypes this pulls recall down
substantially versus the naive number (e.g. استعارة فعل: naive 0.627 →
strict 0.264 for Gemini) — **this gap is a real, reportable finding about
both models' localization accuracy, not a scoring bug.**

## Headline table — recall per subtype, Gemini vs GPT-5.4-mini, naive/strict/token

Full table (25 subtypes, both models, all 3 criteria, raw TP/FN, thin-sample
flags): [`per_subtype_table.xlsx`](per_subtype_table.xlsx). Raw JSON behind
it: `raw/crossmodel_scoring_snapshot.json`.

Reliable subtypes only (n≥10 — see "too few gold instances" section below
for why this cutoff), sorted by n:

| Subtype | Parent | n | Gemini strict | GPT strict | Gemini token | GPT token |
|---|---|---|---|---|---|---|
| استعارة فعل | مجاز (Trope) | 110 | 0.264 | 0.155 | 0.255 | 0.164 |
| كناية عن صفة | كناية (Periphrasis) | 74 | 0.446 | 0.351 | 0.486 | 0.378 |
| كناية عن موصوف | كناية (Periphrasis) | 61 | 0.262 | 0.328 | 0.279 | 0.344 |
| مجاز عقلي | مجاز (Trope) | 54 | 0.463 | 0.426 | 0.463 | 0.481 |
| طباق إيجاب | طباق (Antithesis) | 38 | 0.237 | 0.053 | 0.579 | 0.263 |
| كناية لغوية | كناية (Periphrasis) | 32 | **0.719** | **0.031** | 0.656 | 0.031 |
| تشبيه مطول | تشبيه (Simile) | 30 | 0.833 | 0.667 | 0.933 | 0.767 |
| استعارة تمثيلية | مجاز (Trope) | 28 | **0.143** | **0.571** | 0.143 | 0.571 |
| كناية عن فعل | كناية (Periphrasis) | 27 | 0.333 | 0.148 | 0.481 | 0.185 |
| مجاز مرسل | مجاز (Trope) | 24 | 0.292 | **0.000** | 0.250 | 0.042 |
| استعارة قديمة | مجاز (Trope) | 17 | 0.412 | 0.176 | 0.412 | 0.235 |
| تشبيه قصير | تشبيه (Simile) | 13 | 0.615 | 0.769 | 0.769 | 0.846 |
| كناية فنية | كناية (Periphrasis) | 10 | 0.300 | 0.200 | 0.300 | 0.200 |

**Overall pattern: GPT-5.4-mini scores strictly lower than Gemini on 10 of
these 13 reliable subtypes, and strictly higher on the other 3** (strict
criterion; no ties) — consistent with Phase 1's existing
finding that Gemini was the best/near-best of the 3 original models on most
elements (`PROJECT_STATE.md` §3a) — the reason Phase 3 chose Gemini in the
first place (`MEETING_SUMMARY.md` §5). Two results stand out as worth a
closer look, not just noise:

- **كناية لغوية (linguistic ellipsis periphrasis): Gemini 0.719 → GPT 0.031,
  n=32.** This is a near-total GPT failure on a subtype Gemini handles well
  — both runs only ever got 2/32 right. Worth checking manually whether
  GPT-5.4-mini is systematically failing to recognize this specific
  construction (the subtype where the described noun is elided and only its
  epithet remains), or something more mundane (e.g. a schema/formatting
  issue specific to this subtype's prompt) before concluding it's a real
  model-capability gap.
- **استعارة تمثيلية (unmarked whole-clause allegory): Gemini 0.143 → GPT
  0.571, n=28 — the one subtype where GPT clearly beats Gemini**, and by a
  large margin. This is the same subtype Phase 1 already flagged for a
  DEV→TEST reversal pattern (`PROJECT_STATE.md` §3c) and Phase 3 flagged
  again for a small-sample optimism collapse (`MEETING_SUMMARY.md` §6) — a
  subtype with a history of surprising, hard-to-predict behavior across
  models and samples. GPT's 2 runs agree closely here (20/28 and 19/28 said
  "yes"; strict TP=16/FN=12), so this isn't single-run noise within GPT's
  own data — but it's still one model pair on one sample, not yet
  cross-checked against anything else.

Run-to-run agreement for GPT (both runs' yes-counts per subtype are in the
raw run log) was high everywhere except **مجاز مرسل** (run1: 1/24 yes,
run2: 2/24 yes — consistent near-total abstention, not disagreement) and a
few small-n subtypes where a 1-count swing looks large in percentage terms
only because of the small denominator (e.g. كناية عن صفة 55/74→57/74,
تشبيه الشيء بنفسه 2/4→1/4).

## Subtypes with too few gold instances (n < 10) — flagged, not excluded

Per the project's own precedent (`MEETING_SUMMARY.md` §2: "7 subtypes with
only 1 ground-truth occurrence... too thin to test meaningfully, excluded"),
n<10 is flagged here as **directionally suggestive only, not reliable for
any comparative conclusion** (marked in `per_subtype_table.xlsx`'s "ملاحظة"
column):

| Subtype | n | Gemini strict | GPT strict |
|---|---|---|---|
| كناية بسيطة | 9 | 0.667 | 0.333 |
| طباق في المعنى | 8 | 0.000 | 0.000 |
| طباق سلب | 5 | 0.000 | 0.200 |
| استعارة حديثة | 5 | 0.400 | 0.200 |
| مقابلة (تضاد) | 4 | 0.500 | 0.250 |
| تشبيه تمثيلي | 4 | 0.250 | 0.500 |
| تشبيه الشيء بنفسه | 4 | 0.750 | 0.250 |
| كناية نسبة | 4 | 0.000 | 0.000 |
| تشبيه مركب | 3 | 0.667 | 0.667 |
| استعارة قديمة مرشحة | 2 | 1.000 | 0.500 |
| استعارة فعل مرشحة | 2 | 0.500 | 0.000 |
| استعارة تمثيلية مبنية على الكناية | 2 | 0.500 | 0.000 |

12 of the 25 subtypes fall below n=10. None of these numbers should be
quoted as a finding on their own — they're included for completeness and
because a future, larger sample might confirm or overturn them, same
caveat the project already applies elsewhere (`PROJECT_STATE.md` §6.1).

## Provider errors / refusals

**None.** GPT-5.4-mini: 1,140/1,140 calls succeeded, 0 failures, 0 malformed
JSON responses requiring exclusion (checked via `excluded_parse_errors` in
`score_crossmodel.py` — zero for every subtype). Gemini's original run also
reported 0 errors (`MEETING_SUMMARY.md` §7). Nothing to flag here.

## What was NOT run

- **Claude Sonnet 4.6**: not run, per explicit instruction to proceed with
  Option A only. Estimated at ~$4.96-5.64 if it were added later (see
  `cost_estimate.md`'s options table) — would need a fresh go-ahead.
- **Fable 5**: excluded from consideration throughout, same reasoning as the
  original Phase 3 session (cost).
- **Precision/F1 for any model**: see above — not a "not run yet", a "not
  computable from this design" without a new negative-sampling experiment.

## Where everything is

- `results/phase3_crossmodel/cost_estimate.md` — pre-spend estimate, options
  table (A-D), and the approval trail.
- `results/phase3_crossmodel/summary_openai.json` — the actual run log (cost,
  tokens, per-subtype yes-counts, both runs).
- `results/phase3_crossmodel/per_subtype_table.xlsx` — the full per-subtype,
  per-model, per-criterion comparison table (this file's source data).
- `results/phase3_crossmodel/raw/openai/<slug>_all.jsonl` — GPT-5.4-mini's
  raw per-row records (exists/appearance/reasoning), same schema as Phase 3's
  Gemini data.
- `results/phase3_crossmodel/raw/crossmodel_scoring_snapshot.json` — the
  exact scored numbers behind the table above, for reproducibility.
- `experiments/phase3_crossmodel/` — all code: `run_crossmodel.py` (the
  runner, with a cost-ceiling abort mechanism used this run), `score_crossmodel.py`
  (the span-level re-scorer, shared by both models), `build_report.py` (the
  table generator).
