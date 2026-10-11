# Phase 4 — Full Cost Model (decision-ready)

**No API calls were made anywhere in producing this document.** Every number below is either (a) read
from a local file/log, (b) computed by arithmetic over those local numbers, or (c) read from a provider's
public pricing/model page. Full step-by-step trail: `docs/phase4/SESSION_LOG.md`.

**Every number is tagged VERIFIED (confirmed this session against an official provider page or a real
project log) or ESTIMATE (arithmetic extrapolation, flagged explicitly).** Nothing is silently guessed.

---

## 0. Headline flags (read this before the tables)

1. **`gemini-3.5-flash` is not on Google's current official pricing or models page** (checked
   2026-10-11: `ai.google.dev/gemini-api/docs/pricing` and `.../docs/models`). Current Flash lineup is
   3.5 Flash-Lite, 3.6 Flash, 3.8 Flash, 3-flash-preview, 2.5-flash (legacy). The $1.50/$9.00 price this
   project has used throughout (`config.py`) is repeated by every third-party aggregator found but
   **could not be verified against a live official page this session**. Treated as ESTIMATE below, not
   guessed as VERIFIED.
2. **Our Gemini API key is on the free tier — 20 requests/day** (not an estimate: this is what actually
   happened in the real E1 run, `E1_RESULTS.md` — 128/150 calls failed with `429 RESOURCE_EXHAUSTED`,
   quota value 20). Any design below involving more than ~20 Gemini calls/day needs billing enabled on
   that key first.
3. **The single biggest cost driver in this whole model is D4's output-token volume**: asking for all 23
   subtypes on every verse of every poem in one pass produces roughly **49,000 output tokens per poem**
   (106.2 tokens/decision × 23 subtypes × ~20 verses/poem) before any reasoning/thinking budget is added —
   1-2 orders of magnitude larger than every other cost term in this document. See §4 and §6.

---

## 1. Prices — Table 1

| Model | Input $/MTok | Output $/MTok | Cached input | Batch API | Reasoning/thinking billing | Status |
|---|---|---|---|---|---|---|
| **Claude Sonnet 4.6** (Anthropic) | **$3.00** | **$15.00** | 5-min TTL: read $0.30, write $3.75/MTok | ~50% off standard ("save 50% with batch processing") | Billed as ordinary output tokens (Anthropic's documented general convention for extended thinking) | VERIFIED (claude.com/pricing, 2026-10-11, listed under "Legacy models" — still priced/billable). Caching+batch terms VERIFIED on same page. Reasoning-billing convention: general provider practice, **not re-confirmed on a live page this session** → ESTIMATE. |
| **GPT-5.4-mini** (OpenAI) | **$0.75** | **$4.50** | ~$0.075 (≈90% off input) | ~50% off standard (≈$0.375/$2.25) | Billed as ordinary output tokens (OpenAI's documented convention for reasoning-effort models) | Base price VERIFIED (`developers.openai.com/api/docs/models/gpt-5.4-mini`, matches this project's own `config.py`). Cached-input and batch figures are **third-party-aggregator only** (direct fetch of `openai.com/api/pricing/` returned HTTP 403 this session) → ESTIMATE. Reasoning-billing convention → ESTIMATE (not re-confirmed this session). |
| **Gemini 3.5 Flash** (Google) | **$1.50** (ESTIMATE) | **$9.00** (ESTIMATE) | not found for this model on the current page | 50% off standard (official, general paid-tier feature — VERIFIED) | Billed as ordinary output tokens (Google's documented convention for "thinking" budgets on Flash models) | **Base price NOT found on the live official pricing/models page this session (see §0.1) — carried forward from this project's own `config.py` + third-party aggregators only.** Treat as ESTIMATE, re-verify in AI Studio/billing console before spending real money on Gemini-heavy designs. |

**Paid-tier rate limits that matter:**

| Provider | Free tier (what we're actually on) | Paid tier 1 |
|---|---|---|
| Google Gemini | **20 requests/day** (VERIFIED — real E1 run hit this wall) | Not retrieved definitively this session (search was inconclusive/conflicting) — **check the AI Studio rate-limits dashboard before any run bigger than ~20 calls**; billing must be enabled on the key regardless. |
| OpenAI | n/a (we're already on a paid key) | **500 RPM / 500,000 TPM / 5,000,000-token batch queue** for `gpt-5.4-mini` — VERIFIED (`developers.openai.com/api/docs/models/gpt-5.4-mini`). |
| Anthropic | n/a (we're already on a paid key) | Not re-checked this session (project has run Claude before without hitting a limit) — ESTIMATE/not verified. |

**Reasoning/thinking tokens — a real finding, not an assumption**: grepped every manifest and log this
project has ever produced (`results/**/*.json`); **none contains an actual logged reasoning-token count**
for any of the 3 models. This project has never actually turned on and billed a reasoning/thinking budget
for Claude Sonnet 4.6, GPT-5.4-mini, or Gemini 3.5 Flash. §4's "mid" reasoning-volume scenario is instead
anchored to Phase 2 Config C's real `stage1_output_tokens` (a genuine free-form reasoning pass, just not
one logged under a field literally named "reasoning_tokens") — see §3.

---

## 2. Token facts from real logs

**Whole-poem design (current/frozen: 4 element definitions + 19 baked-in examples, all 4 elements per
call, one call per poem)** — linear fit `tokens = a + b × n_verses` over the 5 real Phase 1
(verses, in_tokens, out_tokens) data points per provider (`INFO_REPORT.md` §4's own table; fit computed
fresh with `numpy.polyfit`, not transcribed):

| Provider | Fixed input `a_in` (tokens) | Per-verse input `b_in` | Fixed output `a_out` | Per-verse output `b_out` |
|---|---|---|---|---|
| Anthropic | 2,356 | 82.6/verse | −6 (≈0) | 95.7/verse |
| OpenAI | 1,689 | 55.5/verse | −58 (≈0) | 60.8/verse |
| Google | 1,815 | 50.8/verse | 204 | 75.6/verse |

VERIFIED — fit directly from real logged `run_manifest.json` usage across 5 real poems (23-81 verses).
Fit quality: predicts the 5 known points within the same ~3-15% COST_PLAN.md already reported for its own
(dollar-denominated) version of this fit.

**Real measured prompt-component sizes** (via `tiktoken`'s `cl100k_base` encoding — the only local
tokenizer available; **not the real tokenizer for any of the 3 actual models**, an approximation flagged
the same way `experiments/phase4_e1/dryrun.py` already flagged it):

| Component | Tokens | Source |
|---|---|---|
| Base system message (4 elements + 19 baked examples) | **2,226** | `pilot_3models.prompts.build_system_message()`, measured directly |
| 2-example few-shot block (E1 sets A/B/C) | 283 / 358 / 291 (avg **311**) | `phase4_e1.fewshot_examples.build_fewshot_block()`, measured directly |
| Per-subtype system template, avg over 25 `SUBTYPE_DEFS` entries | avg **313** (227-428 range) | `phase3_subelements.subtype_prompts.SYSTEM_TEMPLATE`, measured directly |
| ↳ of which: shared scaffold alone | 126 | same template, filled with an empty definition |
| ↳ of which: avg per-subtype definition content | ≈187 (313−126) | derived |
| `ANALYSIS_INSTRUCTIONS` boilerplate (no verse) | 245 | measured directly |
| Avg output per (subtype, verse) decision, incl. 1-3-sentence Arabic reasoning | **106.2** | `results/phase3_crossmodel/summary_openai.json`: 121,119 output tokens / 1,140 calls — **real logged GPT-5.4-mini data**, VERIFIED |

**Real E1 per-call averages** (actual spend, not estimate — `results/phase4_e1/run_manifest.json`, error-free
records only, E1's real 50-poem pool, avg 20.2 verses/poem, base system + 2-example few-shot):

| Provider | n (succeeded) | avg input tokens | avg output tokens |
|---|---|---|---|
| OpenAI (GPT-5.4-mini) | 150/150 | 2,772 | 1,438 |
| Google (Gemini 3.5 Flash) | 8/150 (free-tier wall) | 2,886 | 1,978 |

**Real E1 actual spend** (given, matches `E1_RESULTS.md`): GPT-5.4-mini $1.28 for 150 calls ($0.00853/call);
Gemini $0.18 for 8 calls ($0.0225/call, small-n).

**Mid-scenario reasoning-token anchor** (Phase 2 Config C, `results/phase2_chatlike/config_c/Imru2/run_manifest.json`,
real logged data, 23-verse poem, 2 runs): `stage1_output_tokens` = 39,306 (run1) / 38,030 (run2) → avg
38,668 tokens / 23 verses = **1,681 tokens/verse** of real, measured free-form Arabic reasoning. This is
the closest real analogue this project has to a per-verse "reasoning token" cost, even though no manifest
anywhere logs a field literally named `reasoning_tokens` (confirmed by grep — zero hits project-wide).

---

## 3. Eligible-poem pool — exact counts (computed fresh from `manifest.csv`, 167 rows)

| Pool | Poems | Verses | Exclusions applied |
|---|---|---|---|
| All scraped | 167 | 3,470 | none |
| Minus no-text poem (28601) | **166** | 3,470 (unchanged — 28601 had 0 reconstructable verses anyway) | 28601 |
| Minus the 5 already-used Phase 1 poems (Abu_Tammam/Imru2/Imru1/Nabigha/Jarir) | **161** | **3,246** | 28601 + the 5 |
| Minus also the 3 E1 example-source poems (16251/17234/21337) | **158** | **3,228** | 28601 + the 5 + the 3 |

**Decision taken for this doc** (stated explicitly, overridable): designs that need few-shot examples
(**D1, D2**) use the **158-poem / 3,228-verse** pool, matching E1's own convention (examples come from
poems excluded from eval). Designs that don't need examples (**D3, D4a, D4b**) use the **161-poem /
3,246-verse** pool — the 5 Phase 1 poems are excluded by default for consistency with the project's
established practice (never mixing frozen-TEST/DEV poems into a new large-scale run), **not** because
running a new design on them would violate the "TEST stays spent" rule (that rule is about re-scoring
frozen *element-level* F1 numbers, not about running an unrelated subtype-taxonomy design on the same poem
text). If the supervisors want every scraped poem included regardless, the 166-poem/3,470-verse pool is
the literal maximum and every total in §4/§5 scales up by ≈1.7%.

---

## 4. Cost per call and per poem — Table 2

All costs: `cost = (input_tokens/1e6)×price_in + (output_tokens/1e6)×price_out`, at the pool's average
**20.2 verses/poem** (161-poem pool) or **20.4 verses/poem** (158-poem pool — close enough to use the same
figure without materially changing any number below).

Design definitions (every assumption stated explicitly — this is the one place in this doc where
judgment calls were made, not measurements):

- **D1 — one-shot (1 example, one subtype), 1 run.** Whole-poem call (not per-verse — kept consistent
  with this project's established cost-efficient batching convention, §4's "4-8x more expensive" finding
  in `PROJECT_STATE.md` §3g). Input = scaffold(126) + 1 subtype definition(187) + instructions(245) + 1
  example (≈155, half of the measured 2-example block, ESTIMATE) + verse text (provider's real per-verse
  marginal × n_verses). Output = 106.2 tokens/verse (one subtype's decision only).
- **D2 — few-shot (2 examples), 1 run.** Same as D1 but with the real measured 2-example block (311
  tokens) instead of 1.
- **D3 — "our current design," per-poem call.** Reinterpreted from the task's literal "one element"
  wording: this project's actual, already-run design (`v4_combined`) asks about **all 4 elements in one
  call**, not one element per call — a genuinely single-element-per-call design is the already-tried
  "decomposed" variant (`PROJECT_STATE.md` §3f), which cost ~1.75× more for no net accuracy gain and is
  *not* the current production design. D3 below costs the actual current design (whole-poem fit from §2)
  as the comparison baseline; it happens to deliver all 4 elements for this price, not just one.
- **D4a — full 23-subtype taxonomy, all elements, ONE call per poem**, reasoning disabled (baseline).
  Input = scaffold(126) + 23×187(subtype defs) + 245(instructions) + verse text. Output = 106.2 × 23 ×
  n_verses (one decision object per subtype per verse).
- **D4b — same taxonomy, ONE call per element family per poem (4 calls)**. 23 subtypes apportioned
  8(مجاز)/6(كناية)/5(تشبيه)/4(طباق) — an ESTIMATE split, not a measured one. Each call repeats the
  scaffold+instructions+full poem-verse text; total decision output is the same as D4a (same 23×n_verses
  decisions, just split across 4 responses).

| Design | Anthropic in/out (tokens) | Anthropic $/poem | OpenAI in/out | OpenAI $/poem | Google in/out | Google $/poem |
|---|---|---|---|---|---|---|
| D1 (1-shot, 1 subtype) | 2,378 / 2,141 | $0.0393 | 1,832 / 2,141 | $0.0110 | 1,737 / 2,141 | $0.0219 |
| D2 (2-shot, 1 subtype) | 2,534 / 2,141 | $0.0397 | 1,988 / 2,141 | $0.0111 | 1,893 / 2,141 | $0.0221 |
| D3 (current, all 4 elements) | 4,021 / 1,924 | $0.0409 | 2,808 / 1,168 | $0.0074 | 2,839 / 1,728 | $0.0198 |
| D4a (23 subtypes, 1 call/poem) | 6,337 / 49,246 | **$0.7577** | 5,791 / 49,246 | **$0.2260** | 5,696 / 49,246 | **$0.4518** |
| D4b (23 subtypes, 4 calls/poem) | 12,446 / 49,246 | **$0.7760** | 10,261 / 49,246 | **$0.2293** | 9,882 / 49,246 | **$0.4580** |

All figures ESTIMATE (built from measured components, §2, not from an actual API call for this exact
design) except where noted. D4a/D4b's output column is the dominant term by ~20-25× over every other
design in this table — see §0.3.

---

## 5. Total cost per design × model, over the eligible pool — Table 3

D1/D2 priced over the **158-poem / 3,228-verse** pool; D3/D4a/D4b over the **161-poem / 3,246-verse**
pool (§3). 1 run only, as instructed.

| Design | Anthropic total | OpenAI total | Google total | **3-model total** |
|---|---|---|---|---|
| D1 (1-shot, 1 subtype) | $6.21 | $1.74 | $3.46 | **$11.41** |
| D2 (2-shot, 1 subtype) | $6.27 | $1.75 | $3.49 | **$11.51** |
| D3 (current design, all 4 elements) | $6.59 | $1.19 | $3.19 | **$10.96** |
| D4a (23 subtypes, 1 call/poem, no reasoning) | $121.99 | $36.38 | $72.73 | **$231.10** |
| D4b (23 subtypes, 4 calls/poem, no reasoning) | $124.94 | $36.92 | $73.74 | **$235.60** |

**D4, with reasoning/thinking enabled** — low/mid/high scenarios, extra output tokens on top of D4a's
49,246/poem baseline (§0.3):

| Scenario | Extra tokens/verse | Basis | Extra 3-model total (161 poems) | **D4a grand total** |
|---|---|---|---|---|
| Low (no added budget beyond the required reasoning sentence already counted) | +0 | the 106.2/decision figure already includes one required 1-3-sentence justification | $0 | **$231.10** (= D4a baseline above) |
| Mid | +1,681/verse | Phase 2 Config C's real `stage1_output_tokens`, a genuine free-form reasoning pass (§2) — **this is the one number in this scenario set that's anchored to a real log, per the task's instruction** | $155.5 | **≈$386.6** |
| High | +5,000/verse | ESTIMATE, ~3× Mid — reasoning-budget models can burn substantially more under a higher thinking-token cap; no real log in this project reaches this volume, this is a planning ceiling, not a measurement | $462.4 | **≈$693.5** |

D1/D2/D3 stay cheap (all three single-run, 3-model totals land in the **$11-12** range) regardless of
pool-size or example-count choices — the per-subtype or per-element call structure is inherently far
cheaper than the full-taxonomy cross-product. **D4 is 20-60× more expensive than D1/D2/D3, driven almost
entirely by its output-token volume, not its input/context size.**

---

## 6. Table 4 — cheapest sensible combination, and what to cut at a ~$100 budget

**Cheapest way to get *some* real signal on every design question, 3-model, 1 run each**: D1 + D2 + D3
together cost **≈$33.88** (3-model totals summed) — well under $100, answers the one-shot-vs-few-shot
question (D1 vs D2) and gives a current-design cost baseline (D3) for comparison, all on the full eligible
pool, no example/subsample compromises needed anywhere.

**For the full-taxonomy design (D4), which is the expensive one**:

- **3-model, no reasoning (D4a baseline, $231.10) exceeds $100 outright.** Cannot fit all 3 models at
  full pool size under $100 even with reasoning off.
- **Single cheapest model alone (GPT-5.4-mini, D4a, $36.38)** fits easily, with **~$63.62 of budget left**
  — enough to add Gemini on a 50-poem subsample (reusing E1's own `config/eval_pool.json` stratification,
  10 Abu Nuwas + 40 other) instead of the full 161-poem pool: Gemini's D4a cost scales linearly with poem
  count, so 50/161 × $72.73 ≈ **$22.60** — GPT-5.4-mini (full pool) + Gemini (50-poem subsample) =
  **$58.98**, leaving room for the Mid reasoning scenario on GPT-5.4-mini alone (+$24.55/161-poems, or
  +$7.63 on just a 50-poem GPT subsample) without breaking $100.
- **What to cut first if $100 is a hard ceiling and all 3 models + reasoning + full pool is the wish
  list, in priority order**:
  1. **Drop Claude Sonnet 4.6 from D4 entirely** — it's the single most expensive line in every D4 row
    ($121.99-$124.94 baseline alone, more than half the entire $100 budget on its own) and is not the
    model this project has found strongest on any of the 4 elements (`INFO_REPORT.md` §1a: Gemini ≥
    Claude on Trope/Kenning/Simile/Antonymy F1 at baseline).
  2. **Drop the full 161-poem pool to a stratified subsample** (reuse E1's 10/40 Abu-Nuwas/other
    stratification at a smaller N, e.g. 50 or 80 poems) rather than dropping reasoning — reasoning is the
    part of this design that answers a *new* question (does extended thinking help subtype recall at
    all); pool size mostly affects statistical power, which a smaller stratified sample still provides
    *some* of.
  3. **Drop D4b (the 4-calls-per-poem variant) in favor of D4a** — D4b costs strictly more ($235.60 vs
    $231.10 baseline, and the gap widens under any reasoning scenario since the extra per-call scaffold
    and the 3× extra poem-verse-text repetition both scale with reasoning-token volume too) for no
    accuracy benefit this document can show (no run of either variant has ever happened) — and this
    project's own prior decomposition experiments (`PROJECT_STATE.md` §3f/§3g) consistently found
    decomposing a batched call into multiple narrower calls costs more without reliably improving
    accuracy.
  4. **Keep the Mid reasoning scenario, drop High** — Mid is anchored to a real log (Config C); High is a
    planning ceiling with no supporting measurement in this project, and the gap between Mid (+$155.5
    3-model) and High (+$462.4 3-model) is itself larger than the entire $100 budget.

**Recommended ~$90-95 package under a hard $100 ceiling**: GPT-5.4-mini D4a, full 161-poem pool, Mid
reasoning ($36.38 + $24.55 = **$60.93**) + Gemini D4a, 50-poem stratified subsample, no reasoning
(**≈$22.60**) = **≈$83.53**, leaving ~$16 headroom. This answers "does the full taxonomy + reasoning
change subtype recall" on the cheaper, historically-stronger-performing model at full statistical power,
plus a cross-model spot-check on a representative subsample — without Claude, without D4b, and without
the unanchored High-reasoning scenario.

---

## Assumptions and estimate/verified summary

- **VERIFIED this session**: GPT-5.4-mini $0.75/$4.50 + Tier-1 rate limits (OpenAI model page); Claude
  Sonnet 4.6 $3/$15 + prompt-caching rates + batch discount (claude.com/pricing); Gemini batch = 50% off,
  free-tier = 20 req/day (project's own failed-call data); the 5-poem linear token fit (real
  `run_manifest.json` data); all measured prompt-component token sizes (real source files, `tiktoken`
  approximation); E1's real per-call averages and real spend; Config C's real `stage1_output_tokens`.
- **ESTIMATE / unverified this session**: Gemini 3.5 Flash's base price (not on the current official
  page — §0.1); OpenAI/Anthropic cached-input and batch *exact* rates (aggregator-sourced, not a fetched
  official page); every reasoning/thinking-token billing convention (general provider practice, not
  re-confirmed for these 3 specific model IDs); Gemini's paid-tier RPM/RPD; D1/D2's 1-example token size
  (half of measured 2-example, not independently measured); D4b's 23-subtype 8/6/5/4 family split; the
  High reasoning-volume scenario (no supporting log); using `tiktoken`'s `cl100k_base` as a stand-in
  tokenizer for all 3 real models (consistent with how `dryrun.py` already handled this limitation).
- **Taxonomy-size discrepancy, stated not resolved**: the task instruction says 23 subtypes; this
  project's own code (`subtype_defs.SUBTYPE_DEFS`) has 25, and `data/ground_truth/by_subtype/` has 28
  files. This doc uses 23 throughout per the explicit instruction.

---

## Sources consulted

`CLAUDE.md`, `docs/phase4/{COST_PLAN,INFO_REPORT,E1_RESULTS,SESSION_LOG}.md`, `PROJECT_STATE.md`,
`data/ali_poems/manifest.csv`, `results/phase3_crossmodel/summary.md`, `results/phase3_crossmodel/summary_openai.json`,
`experiments/phase4_e1/{e1_config,fewshot_examples}.py`, `results/phase4_e1/run_manifest.json`,
`experiments/pilot_3models/prompts.py`, `experiments/phase3_subelements/{subtype_defs,subtype_prompts}.py`,
`results/phase2_chatlike/config_c/Imru2/run_manifest.json`; live pages:
`developers.openai.com/api/docs/models/gpt-5.4-mini`, `ai.google.dev/gemini-api/docs/{pricing,models}`,
`claude.com/pricing` (redirected from `anthropic.com/pricing`) — all checked 2026-10-11.
