# Phase 4 — Full Cost Model v2 (built on the real E1 v2 run)

**No API calls were made anywhere in producing this document.** Every number is either (a) computed
directly from `results/phase4_e1_v2/run_manifest.json`'s 3,924 real logged records, (b) arithmetic over
those real numbers, or (c) carried forward from `FULL_COST_MODEL.md`'s own live provider-page checks on
2026-10-11 (flagged explicitly where that applies — not re-checked live this session). Full step-by-step
trail: [`SESSION_LOG.md`](SESSION_LOG.md). Raw computed numbers for citation: `_cost_model_v2_data.json`,
`_cost_model_v2_step4.json` (same folder).

This v2 supersedes `FULL_COST_MODEL.md` in one specific way: that document's D4a/D4b full-taxonomy
figures were built entirely from **estimated** component sizes (no real full-taxonomy call had ever been
made). This document anchors the same full-taxonomy question on the **real** E1 v2 run — 3,924 real calls
of one real subtype (`استعارة فعل`), across 3 real models and 4 real prompt conditions (Z/A/B/C) — and
extrapolates from there, with every extrapolation explicitly flagged.

---

## 0. Headline findings

1. **The real E1 v2 spend ($10.5680, confirmed in `E1_V2_RESULTS.md`) exactly matches the project's own
   `config.py` Gemini rate ($1.50/$9.00 per MTok)** — not either of the two `gemini-3.6-flash` pricing
   scenarios `dryrun_v2.py`'s docstring flagged as more likely. This resolves (for this API key, as of
   2026-10-11) the pricing ambiguity `FULL_COST_MODEL.md` §0.1 could not resolve from a live page alone:
   whatever model string is actually served, **this key is being billed at the $1.50/$9.00 rate**. Treated
   as the working assumption below; still worth a one-time AI-Studio-console cross-check before a
   full-corpus run (see §5).
2. **Gemini's `thoughts_tokens` field was 0 on all 1,308 real Gemini calls in this run.** The
   thinking-token risk `providers_fixed.py`'s docstring warns about (the real past incident: computed cost
   $0.96, actual balance drop ~$7.5-8) **did not materialize this time** — `call_google_fixed`'s
   `thinking_level="minimal"` setting appears to have worked as intended. This is a real, measured data
   point, not an assumption that it will always be zero.
3. **Claude Sonnet 4.6 cost 37% more than `dryrun_v2.py`'s own pre-run estimate; GPT-5.4-mini and Gemini
   cost 14-19% less.** The driver is output-token volume, not input: the dry run assumed a flat 106.2
   output tokens/decision (Phase 3's historical GPT average) for all 3 models; the real run produced
   193.2 (anthropic), 97.8 (openai), 82.2 (google) output tokens/call on average — Claude's real reasoning
   text per decision runs almost 2x longer than GPT's. See §1.
4. **Scaling this one real subtype's behavior to the full 25-subtype taxonomy (S1/S2, §3) lands far below
   `FULL_COST_MODEL.md`'s D4a/D4b figures** ($601-$711 for 3 models/1 run here vs. $231-$236 there) —
   **the two are not measuring the same thing.** D4a/D4b costed ONE call per poem returning all 23
   subtypes' decisions for every verse at once (so output tokens scale with `verses × subtypes` inside a
   single giant response). This document's S1/S2 cost ONE call per `(subtype, verse)` pair instead — the
   real E1 v2 design — so output tokens scale the same way but each decision carries its own full
   input-token overhead (scaffold + instructions repeated on every call, not amortized across subtypes in
   one response). The real per-decision input/output averages used here come from an actual run; D4a/D4b's
   49,246-output-token/poem figure was never run and remains in `FULL_COST_MODEL.md` as pure estimate.
   Neither design is "the" right one — they trade off real per-call overhead against real amortization,
   and only a real run of each at small scale would show which is actually cheaper once batching/caching
   are applied (see §4).

---

## 1. Real per-call facts (Step 1)

Source: `results/phase4_e1_v2/run_manifest.json`, grouped by `(provider, set_name)`. 327 verse-units ×
4 sets × 3 models = 3,924 calls, 0 errors. All figures **MEASURED** unless marked.

| Provider | Set | n | avg input tok | avg output tok | $/call | total $ |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | Z | 327 | 629.3 | 197.5 | $0.00485 | $1.5860 |
| Claude Sonnet 4.6 | A | 327 | 888.3 | 192.4 | $0.00555 | $1.8150 |
| Claude Sonnet 4.6 | B | 327 | 971.3 | 192.2 | $0.00580 | $1.8957 |
| Claude Sonnet 4.6 | C | 327 | 877.3 | 190.6 | $0.00549 | $1.7953 |
| GPT-5.4-mini | Z | 327 | 497.6 | 100.4 | $0.000825 | $0.2698 |
| GPT-5.4-mini | A | 327 | 673.6 | 95.4 | $0.000935 | $0.3056 |
| GPT-5.4-mini | B | 327 | 731.6 | 98.8 | $0.000993 | $0.3248 |
| GPT-5.4-mini | C | 327 | 666.6 | 96.7 | $0.000935 | $0.3057 |
| Gemini (cfg rate) | Z | 327 | 517.9 | 86.9 | $0.00156 | $0.5098 |
| Gemini (cfg rate) | A | 327 | 697.9 | 82.0 | $0.00179 | $0.5837 |
| Gemini (cfg rate) | B | 327 | 750.9 | 79.8 | $0.00184 | $0.6033 |
| Gemini (cfg rate) | C | 327 | 688.9 | 80.0 | $0.00175 | $0.5732 |

**Overall per provider (all 4 sets, 1,308 calls each)**:

| Provider | avg input tok | avg output tok | total input tok | total output tok | thoughts tok billed | total $ |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | 841.5 | 193.2 | 1,100,747 | 252,650 | n/a | $7.0920 |
| GPT-5.4-mini | 642.4 | 97.8 | 840,205 | 127,967 | n/a | $1.2060 |
| Gemini (cfg $1.50/$9.00) | 663.9 | 82.2 | 868,392 | 107,493 | **0** | $2.2700 |
| Gemini (3.6-flash LOW $0.75/$3.75, estimate) | — | — | — | — | — | $1.0544 |
| Gemini (3.6-flash HIGH $1.50/$7.50, estimate) | — | — | — | — | — | $2.1088 |

**Grand total (cfg rate)**: $10.5680 — matches `E1_V2_RESULTS.md` exactly. **MEASURED.**

### Real cost vs. dry-run estimate (same 25-poem pool, 1,308 calls/model)

`dryrun_v2.py` priced this exact pool before the run, using tiktoken input counts + a flat 106.2
output-tokens/decision assumption for all 3 models:

| Model | Dry-run estimate | Real cost | Ratio (real / estimate) |
|---|---|---|---|
| Claude Sonnet 4.6 | $5.17 | $7.09 | **1.37×** (37% over) |
| GPT-5.4-mini | $1.40 | $1.21 | **0.86×** (14% under) |
| Gemini (cfg rate) | $2.79 | $2.27 | **0.81×** (19% under) |

The direction is consistent with each model's real average output length relative to the dry run's flat
106.2-token assumption: Claude's real output (193.2) ran ~82% longer than assumed; GPT's (97.8) and
Gemini's (82.2) both ran shorter. **Takeaway for future dry runs on this project: a single
cross-model output-token assumption systematically misprices Claude low and the other two models high.**

---

## 2. Cost per (verse × subtype) decision (Step 2)

### Real per-subtype template size variation

`subtype_defs.SUBTYPE_DEFS` has **25 entries**; `subtype_defs.py`'s own docstring says 23 were "confirmed
with the user" as having real distinct content — 2 of the 25 (`كناية بسيطة`, `كناية فنية`) share
byte-identical generic definition text rather than a subtype-specific one. Ground truth
(`data/ground_truth/by_subtype/`) has **28 label files total**; 3 of those (`تشبيه`, `تشبيه_غريب`,
`مقابلة_نحوية`) have no corresponding `SUBTYPE_DEFS` entry and are excluded from the taxonomy by the
existing code, leaving exactly the 25 mapped 1:1. **This document uses all 25** (not 23) wherever a
"full taxonomy" figure appears, since that's what the code actually sends; the 23-subtype distinct-content
figure is used only in §2's definition-size average, flagged below.

Rendered system-message size per subtype (scaffold + parent + definition + example), measured with
`tiktoken` `cl100k_base` (approximation — no offline tokenizer exists locally for any of the 3 real
models, same caveat `dryrun_v2.py` already carries):

| Stat | All 25 entries | Excl. the 2 duplicate-generic كناية entries (23) |
|---|---|---|
| Average | 313.2 tok | 303.3 tok |
| Min | 227 tok (`تشبيه قصير`) | 227 tok |
| Max | 428 tok (`كناية بسيطة`) | 378 tok (`استعارة تمثيلية مبنية على الكناية`) |

Shared scaffold alone (empty fields): **124 tok**. `ANALYSIS_INSTRUCTIONS` boilerplate (no verse): **245
tok**. Average verse-text + instructions (the full user message), measured over the real 327 verse-units
in the E1 v2 pool: **306.0 tok**.

### Provider-specific real/tiktoken scale factor (anchored on the one real subtype run)

The 327 real verse-units were only ever run on **one** subtype (`استعارة فعل`, system-message tiktoken
size 280). Dividing each provider's real average input tokens for set Z by that prompt's tiktoken count
gives a provider-specific scale factor, used below to extrapolate the other 24 subtypes' **real-token-
equivalent** input size (**ESTIMATE** — anchored on one real subtype, not independently measured for the
other 24):

| Provider | Real avg input (Z) | Tiktoken count (Z) | Scale factor |
|---|---|---|---|
| Claude Sonnet 4.6 | 629.3 | 586.0 | **1.074** |
| GPT-5.4-mini | 497.6 | 586.0 | **0.849** |
| Gemini | 517.9 | 586.0 | **0.884** |

Few-shot (set B) real absolute token overhead, measured directly (not extrapolated — this is a real
provider-specific delta, `avg_in(B) − avg_in(Z)`), applied uniformly to every subtype's estimate below
(**ESTIMATE on the "uniform" part only** — assumes other subtypes' 2 example verses would run about the
same length as `استعارة فعل`'s):

| Provider | Fewshot-B overhead (real tokens) |
|---|---|
| Claude Sonnet 4.6 | +342.0 |
| GPT-5.4-mini | +234.0 |
| Gemini | +233.0 |

### Cost per (verse × subtype) decision — zero-shot (Z-style) vs. few-shot (set B)

Mean / min / max taken across all 25 subtypes' individually-estimated input size (not a flat average
applied uniformly — each subtype's own definition length is priced separately, then summarized):

| Provider | Zero-shot mean | Zero-shot min | Zero-shot max | Fewshot-B mean | Fewshot-B min | Fewshot-B max |
|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | $0.004957 | $0.004679 | $0.005327 | $0.005904 | $0.005626 | $0.006274 |
| GPT-5.4-mini | $0.000846 | $0.000791 | $0.000919 | $0.001015 | $0.000960 | $0.001088 |
| Gemini (cfg) | $0.001603 | $0.001489 | $0.001755 | $0.001889 | $0.001775 | $0.002041 |

Output tokens used above: each provider's own real average at set Z (zero-shot) or set B (few-shot) —
**193.2/100.4/86.9 (anthropic/openai/google) at Z; 192.2/98.8/79.8 at B**. The project's own real E1 v2
data already shows output length is governed mainly by the fixed decision+reasoning JSON shape, not by
which subtype is being asked about (Z vs A/B/C output-token means are all within ±3% per provider — see
`_cost_model_v2_data.json`'s `avg_output_tokens_ABC_stats`) — but **this was only confirmed for
`استعارة فعل`**. A subtype that almost never appears in a verse (several of the 25 have single-digit
ground-truth counts, §3) may legitimately produce a shorter reasoning sentence on average ("this element
is clearly absent, no further analysis needed") — this is plausible, not measured, since no other subtype
was ever run.

---

## 3. Scaling to the full corpus (Step 3)

### Eligible-poem pool — exact counts, recomputed fresh from `manifest.csv` (167 rows)

| Pool | Poems | Verses |
|---|---|---|
| All scraped | 167 | 3,470 |
| Minus no-text poem (28601) | 166 | 3,470 |
| Minus the 5 Phase 1 poems | **161** | **3,246** |
| Minus also the 3 E1 example-source poems | **158** | **3,228** |

Same convention as `FULL_COST_MODEL.md`: designs needing few-shot examples (S2) use the 158-poem pool
(examples come from poems excluded from eval); designs that don't (S1) use the 161-poem pool.

### Design definitions

- **S1 — all 25 subtypes, zero-shot (Z-style), 1 run.** One call per `(subtype, verse)` pair, over the
  161-poem / 3,246-verse pool.
- **S2 — all 25 subtypes, few-shot with ONE selected example set (set B — the best observed point
  estimate in `E1_V2_RESULTS.md`; no set is statistically distinguishable from A, but B's point F1 ties or
  leads on 2 of 3 models), 1 run.** Over the 158-poem / 3,228-verse pool.

**Few-shot example availability is a real constraint, not assumed away.** Example sets A/B/C
(`experiments/phase4_e1/config/example_sets.json`) exist **only for `استعارة فعل`** — built once, by hand,
from 3 held-out example-source poems. For the other 24 subtypes, no curated example set exists; building
one would mean drawing 2 example instances from `data/ground_truth/by_subtype/`, which has as few as **2
total instances** for some subtypes:

| Subtype | Ground-truth instances |
|---|---|
| `استعارة قديمة مرشحة` | 2 |
| `استعارة فعل مرشحة` | 2 |
| `استعارة تمثيلية مبنية على الكناية` | 2 |
| `تشبيه مركب` | 3 |

For these 4 subtypes, a conventional "hold out 2 examples, evaluate on the rest" split leaves 0-1
instances to actually evaluate against — **few-shot is not a meaningful design for these subtypes without
either accepting zero held-out eval signal or finding additional annotation.** S2's cost figures below
still include them (priced at the uniform fewshot-overhead assumption, §2) because the question asked was
"cost of all 25 subtypes few-shot," but the methodological gap should be flagged to supervisors
separately from the cost question.

### S1 and S2 totals, per model and combined — **1 run, as instructed**

| Design | Claude Sonnet 4.6 | GPT-5.4-mini | Gemini (cfg) | **3-model total** | GPT+Gemini only | GPT only |
|---|---|---|---|---|---|---|
| **S1** (zero-shot, 161-pool, 3,246 verses × 25 subtypes = 81,150 calls/model) | $402.25 | $68.67 | $130.09 | **$601.00** | $198.75 | $68.67 |
| **S2** (fewshot-B, 158-pool, 3,228 verses × 25 subtypes = 80,700 calls/model) | $476.46 | $81.87 | $152.43 | **$710.76** | $234.30 | $81.87 |

All figures **ESTIMATE** (built from §2's measured components and per-subtype extrapolation, not from an
actual 25-subtype run) except where the underlying per-decision cost is directly anchored on real E1 v2
data for `استعارة فعل` itself. If supervisors want the 166-poem/3,470-verse maximum pool instead of 161,
every S1 number above scales up by **1.069×** (verse-count ratio).

**Comparison with `FULL_COST_MODEL.md`'s D4a/D4b**: those priced $231-$236 (3-model, no reasoning) for a
*different* call structure (one call/poem returning all subtypes at once, 23-subtype count, output
dominated by a single ~49,246-token/poem response). S1/S2 here cost more ($601/$711) for the *same*
subtype count with a *per-decision* call structure, because scaffold+instructions (369 tok) repeat on
every one of the 81,150 calls instead of being sent once per poem. Neither design has been run at this
scale; §0.4 and §4 discuss the real tradeoff.

---

## 4. Reduction options (Step 4)

### Subset of subtypes (by ground-truth instance count ≥ N)

| N | Qualifying subtypes | Share of 570 total GT instances | S1 3-model total | S2 3-model total |
|---|---|---|---|---|
| ≥20 | 10 | 478 (84%) | $236.18 | $280.11 |
| ≥50 | 4 | 299 (52%) | $94.57 | $112.14 |
| ≥100 | 1 (`استعارة فعل` — already run in E1 v2) | 110 (19%) | $23.48 | $27.88 |

### Stratified poem sample (50 / 100 poems, same per-poem verse rate as the full pools)

| Sample | Verses (≈) | S1 3-model total | S2 3-model total |
|---|---|---|---|
| 50 poems | 1,008 | $186.65 | $224.92 |
| 100 poems | 2,016 | $373.29 | $449.85 |

### Batch API (50% discount)

All 3 providers support a batch/async discount at ~50% off standard pricing (Claude "save 50% with batch
processing"; OpenAI ~50% off standard; Google 50% off, paid-tier feature) — **VERIFIED on live provider
pages in `FULL_COST_MODEL.md` on 2026-10-11, carried forward here, not re-checked live this session.**
Latency tradeoff: batch jobs are async with no guaranteed turnaround (typically within 24h for
Anthropic/OpenAI); not usable for interactive iteration, fine for a one-shot full-corpus run.

| Design | Standard 3-model total | Batch (50% off) 3-model total |
|---|---|---|
| S1 (full 25-subtype, 161-pool) | $601.00 | **$300.50** |
| S2 (full 25-subtype, 158-pool) | $710.76 | **$355.38** |

### Prompt caching (where applicable)

Carried forward from `FULL_COST_MODEL.md`'s live-page check (2026-10-11, **VERIFIED then, not
re-checked this session**): Anthropic 5-min-TTL cache read $0.30/MTok (vs $3.00 standard), write
$3.75/MTok; OpenAI automatic cached-input discount ~90% off (aggregator-sourced, **ESTIMATE**, official
page returned HTTP 403 when checked). Mechanically, the cacheable portion of each call here is the
**system message** (scaffold + subtype definition, ~280-428 tok) — reused identically across every verse
for a given subtype, so a single cache write amortizes across ~3,246 (S1) or ~3,228 (S2) calls per
subtype. The user message (instructions + verse text) changes every call and is not cacheable. Not
quantified to a dollar figure here (would require knowing real cache-hit-rate behavior under this
project's actual call-ordering, which has never been tested) — flagged as a real, available lever, not
sized.

### Five concrete packages

| Package | Scope | Run style | Total cost |
|---|---|---|---|
| **1. Cheapest** | GPT-5.4-mini only, S1 (zero-shot), N≥50 subtype subset (4 subtypes, 52% of GT instances), full 161-pool, standard pricing | 1 run | **$10.79** |
| **2. Balanced** | GPT-5.4-mini + Gemini, N≥20 subtype subset (10 subtypes, 84% of GT instances), S1 + S2, **batch API** | 1 run each | **$85.02** |
| **3. Thorough** | 3-model (incl. Claude), N≥20 subtype subset, S1 + S2, **batch API** | 1 run each | **$258.15** |
| **4. Supervisors' full request** | 3-model, all 25 subtypes, S1 + S2, standard pricing, full 161/158-pool | 1 run each | **$1,311.76** |
| **5. Budget-fit cuts** | See below | — | fits $100 / $300 |

**What to cut for a $100 ceiling**: Package 2 (Balanced, $85.02) fits with ~$15 headroom — cuts Claude
entirely (the single most expensive model on every row above) and restricts to the 10 subtypes with ≥20
ground-truth instances rather than all 25, covering 84% of the labeled corpus.

**What to cut for a $300 ceiling**: Package 3 (Thorough, $258.15) fits with ~$42 headroom — keeps all 3
models and both S1 and S2 (zero-shot and few-shot), but still restricts to the N≥20 subtype subset rather
than the full 25, and requires batch submission (async, no interactive turnaround).

**Getting to the full $1,311.76 request (Package 4) under $300 is not possible without either dropping to
batch pricing on everything AND restricting subtypes** — full-taxonomy batch alone (§4's batch table,
S1+S2 summed) is $300.50 + $355.38 = $655.88, still more than double a $300 ceiling.

---

## 5. Assumptions and uncertainty (Step 5)

- **Every number above is for 1 RUN, as the task instructed.** CLAUDE.md's standing rule (`CLAUDE.md`
  §"Standing experiment discipline", item 2) requires **2 runs minimum with 2-run majority as the primary
  metric** for any comparative conclusion, citing a real prior incident (an 8× apparent Kenning/Periphrasis
  gain that halved on a second run). **Doubling every package above for a trustworthy comparative run
  pushes Package 2 (Balanced) to $170.04 — over the $100 ceiling it was built to fit.** Package 1
  (Cheapest) doubles to $21.58, Package 3 (Thorough) to $516.30, Package 4 (full request) to $2,623.52.
  Any budget figure quoted to supervisors should state explicitly whether it is a 1-run or 2-run number.
- **Gemini pricing**: the real E1 v2 spend matches the project's `config.py` $1.50/$9.00 rate exactly
  (§0.1, §1) — treated as the working real rate here. Still carries the underlying uncertainty
  `FULL_COST_MODEL.md` §0.1 raised (model-string/billing-identity mismatch); worth a one-time manual
  AI-Studio-console balance check before committing real money to a full-corpus run, since a single
  25-poem/4-set/3,924-call run is too small a sample to rule out a billing surprise at 20-80× that volume.
- **OpenAI/Anthropic cached-input and batch exact rates**: VERIFIED on live pages by `FULL_COST_MODEL.md`
  on 2026-10-11; **not re-checked live in this session** (no API calls were made, and this session treated
  those figures as still current one day later — re-verify if this doc is used more than a few weeks after
  2026-10-11).
- **Per-subtype input-token extrapolation (§2)**: anchored on ONE real subtype (`استعارة فعل`) run on ONE
  real pool; the other 24 subtypes' real token behavior under the actual Claude/GPT/Gemini tokenizers has
  never been measured. The `tiktoken` cl100k_base approximation plus a single provider-specific scale
  factor is the best available estimate without spending money on a broader pilot.
- **Few-shot-overhead uniformity (§2, §3)**: assumes every subtype's 2 example verses would add roughly
  the same absolute token count as `استعارة فعل`'s set B did. Not measured for any other subtype.
- **Rare-subtype output-token length (§2)**: plausible that subtypes with very few ground-truth instances
  produce shorter "clearly absent" reasoning on average than `استعارة فعل` did — not measured, since no
  other subtype was ever run. If true, S1/S2's output-cost component (and thus Claude's share especially,
  since Claude's real output ran longest) is a slight overestimate.
- **Per-day rate limits, paid tier** (carried from `FULL_COST_MODEL.md`, not re-verified this session):
  OpenAI 500 RPM / 500,000 TPM / 5M-token batch queue for `gpt-5.4-mini` (VERIFIED 2026-10-11 against the
  OpenAI model page). Google: free tier is 20 requests/day (VERIFIED — this project's own real E1 v1
  429-quota failure); **paid-tier RPD was not retrieved definitively** — billing must be enabled on the
  key before any run bigger than ~20 Gemini calls, and the actual paid-tier ceiling should be checked in
  the AI Studio dashboard before committing to S1/S2/Package-4 scale (81,150+ Gemini calls). Anthropic: not
  checked in either session — this project has run Claude without hitting a limit so far, but never at
  this call volume.
- **Estimated wall-clock time for a full run**, using this session's real measured per-call latency
  (`run_manifest.json`'s own timestamps — **MEASURED**, not assumed):

  | Provider | Real mean latency/call | Sequential time for S1 (81,150 calls) | At 5x concurrency |
  |---|---|---|---|
  | Claude Sonnet 4.6 | 4.91s | ~110.7 hours | ~22.1 hours |
  | GPT-5.4-mini | 1.27s | ~28.6 hours | ~5.7 hours |
  | Gemini | 1.60s | ~36.1 hours | ~7.2 hours |

  Concurrency level is an **ESTIMATE** (not tested at this scale this session) and is bounded above by
  whichever per-day/per-minute rate limit above turns out to be real for each provider's paid tier —
  Gemini in particular must have billing enabled first, or the free-tier 20-requests/day wall makes a
  81,150-call run take over 11 years.

---

## Sources consulted

`CLAUDE.md`, `GLOSSARY.md`, `docs/phase4/{FULL_COST_MODEL,E1_V2_RESULTS}.md`,
`results/phase4_e1_v2/run_manifest.json` (3,924 records, read programmatically — too large for a direct
file read), `experiments/phase4_e1_v2/{e1v2_config,providers_v2,dryrun_v2,prompt_builder}.py`,
`experiments/phase3_subelements/{subtype_defs,subtype_prompts}.py`, `experiments/pilot_3models/config.py`
(`MODELS` pricing dict), `data/ali_poems/manifest.csv`, `data/ground_truth/by_subtype/*.xlsx` (28 files).
No live web pages were checked in this session; pricing/rate-limit figures sourced from live pages are
carried forward from `FULL_COST_MODEL.md`'s 2026-10-11 checks and flagged as such throughout.
