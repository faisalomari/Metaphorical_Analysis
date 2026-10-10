# Phase 4 Cost Plan — Example-Sensitivity Pilot (E1) + Full-CV Projection

**Status**: planning + arithmetic only. Zero API calls made in producing this document. All costs are
estimates to be re-confirmed against real token counts the first time any cell is actually run (per
`CLAUDE.md` rule 5 — cost estimate + explicit confirmation before any API call, every time).

---

## 0. Blocking gap found while planning

`data/ali_poems/manifest.csv` **does not exist**. Per `docs/phase4/SESSION_LOG.md` (2026-10-10T02:10–02:45),
the Ali Hussein corpus scrape was only a **Phase A recon** — it found 167 manually-analyzed poems across 52
poets reachable via the site's public `/api/*` endpoints, but the actual download (Phase B) was never
approved or run. There is currently no concrete poem list, no per-poet poem counts, and no per-poem verse
counts for this corpus beyond the aggregate recon numbers.

**Consequence for this plan**: every "50 poems" / "100 poems" / "~30 poets" number below is a *placeholder
pool size*, not a count against a real manifest. All per-poem cost figures are extrapolated from Phase 1's
5-poem corpus (`docs/phase4/INFO_REPORT.md` §4), which has a different (likely shorter) average verse count
than the wider Ali corpus — flagged explicitly in §3's assumptions. **Running the Phase B scraper (or
getting the real manifest some other way) is a prerequisite for turning this plan's estimates into real
ones**, and is itself one of Tuesday's decision points (§5).

---

## 1. E1 design — example-sensitivity pilot

### 1.1 Poet and element recommendation

**Element: مجاز (Trope / "majāz").** `INFO_REPORT.md` §1e ranks the 4 elements by v4_combined mean strict
F1: تشبيه (Simile) ≈0.70 (ceiling, no room to move), مجاز (Trope) ≈0.293 (2nd), طباق (Antithesis) ≈0.165,
كناية (Periphrasis) ≈0.109 (hardest, resistant to nearly every Phase 1/2 intervention). Trope is the cleanest
"mid" pick at the element level — not saturated, not floor/resistant — and all three of INFO_REPORT's
subtype-level mid-difficulty recommendations (مجاز عقلي, استعارة فعل, and the largest periphrasis subtype
كناية عن صفة) point the same direction: two of the three are themselves Trope subtypes. Choosing Trope lets
E1's verdict generalize to those subtype findings without requiring a separate subtype-level ground-truth
slice.

**Poet: cannot be finalized without the manifest (§0).** The criterion should be: (a) a poet distinct from,
or only partially overlapping with, the 5 poems already spent in Phase 1 (`Imru' al-Qais`, `Al-Nabigha`,
`Jarir`, `Abu Tammam`) — reusing a poet is fine, reusing an already-scored *poem* is not; (b) a poet with
enough annotated poems in the Ali corpus to support both the 50-poem and 100-poem pool sizes *after*
excluding the 2 example-source poems. Given the Phase A recon's 167-poems/52-poets aggregate (≈3.2
poems/poet on average), **no single poet is likely to have 100 annotated poems** — that average is too
thin. The practical options are: (i) relax "one poet" to "one poet's prompt, evaluated on a cross-poet
pool" (the pool spans multiple poets, only the two example verses come from one chosen poet), or (ii) pick
whichever single poet turns out to have the largest diwan in the real manifest, and only run the 50-poem
condition for them (dropping the 100-poem comparison if the pool is smaller). This is a Tuesday decision
point (§5), not something to guess here.

### 1.2 Example-source exclusion

Both example sets (A and B — 2 examples each) must be drawn from verses that do **not** appear anywhere in
the eval pool. Concretely: pick 2 source poems from the chosen poet (or corpus) that are *not* in the 50- or
100-poem eval pool, pull one example verse per set from each (A: verse pair from source-poem-1; B: verse pair
from source-poem-2, or two disjoint verse pairs from the same two source poems — either way, disjoint from
each other and from the pool). State the exclusion explicitly in any report: "Examples drawn from
[poem X, verses i/j] and [poem Y, verses k/l]; these 2 poems are excluded from the N-poem eval pool."

### 1.3 Comparison metrics (paired, per CLAUDE.md discipline)

For each of (50-poem pool, 100-poem pool) × (Set A, Set B):

- Raw TP/FP/FN per set, pooled across the poem pool (not just F1 — per CLAUDE.md rule 3).
- Precision/recall/F1 per set, span-level, both strict and token-overlap criteria (CLAUDE.md rule 4).
- **Per-poem paired difference**: for each poem in the pool, (Set A's span-level outcome) − (Set B's
  outcome) — e.g. per-poem F1 delta, or simpler: per-poem TP delta — so the comparison isn't just two
  pooled numbers but a distribution over poems.
- **Bootstrap CI over poems**: resample the poem pool with replacement (e.g. 2,000 iterations), recompute
  pooled F1 for Set A and Set B each time, report the CI on (F1_A − F1_B). This is what actually answers
  "is the example-set effect distinguishable from pool noise."
- **Run-to-run noise vs. set-to-set difference**: compute the 2-run spread *within* Set A (run1 vs run2) and
  within Set B separately, then compare that spread to the Set A vs Set B difference. If within-set run
  noise is comparable in magnitude to the cross-set difference, the experiment cannot support a
  example-sensitivity claim (this is exactly the failure mode CLAUDE.md rule 2 already documented once —
  the Kenning/Periphrasis 8x gain that halved on a second run).

### 1.4 How many example sets (2 vs 3)?

**2 sets is the minimum, not enough for a confident conclusion.** With 2 sets, "set-to-set difference" is a
single number — there's no way to tell whether that one gap is typical example-to-example variation or an
outlier pair, and the run-to-run-noise-vs-set-to-set-difference comparison in §1.3 reduces to comparing one
spread against one gap (no distribution on either side of that comparison).

**3 sets is the minimum that supports the actual claim being tested.** With 3 sets (A/B/C) there are 3
pairwise differences (A-B, A-C, B-C) — enough to see whether the differences cluster (suggesting real but
bounded example-sensitivity) or scatter as wide as the within-set run noise (suggesting the apparent
"effect" in any one pair is noise). It also lets a one-way ANOVA-style variance decomposition (between-set
variance vs. within-set run variance) replace the single-pair comparison in §1.3 with something slightly
more principled. Recommend 3 sets if the Tuesday budget allows it (§5 shows the marginal cost of the 3rd
set); fall back to 2 only as an explicitly underpowered pilot.

---

## 2. Cost tables

### 2.1 Assumptions (stated once, used throughout)

- **Per-call cost basis**: Phase 1's pooled whole-poem-call averages (`INFO_REPORT.md` §4) — one API call
  covers one full poem, one model, one run, all 4 elements (the system message is shared/frozen across
  elements; there is no cheaper way to query Trope alone without a new, unvalidated reduced-prompt variant,
  so this plan assumes full-element calls).
  - Anthropic (Claude Sonnet 4.6, $3/$15 per MTok): ≈6,227 in / 4,518 out → **$0.0865/call**
  - OpenAI (GPT-5.4-mini, $0.75/$4.50 per MTok): ≈4,290 in / 2,854 out → **$0.0161/call**
  - Google (Gemini 3.5 Flash, $1.50/$9.00 per MTok): ≈4,185 in / 3,771 out → **$0.0402/call**
- **Pool poem length unknown** (§0) — these per-call costs come from Phase 1 poems averaging 23–81 verses
  (mean ≈45). If the Ali corpus's typical poem is longer, multiply accordingly; this plan does **not**
  attempt to guess a correction factor without the manifest.
- **2 runs per (set, pool-size, model) cell**, per CLAUDE.md rule 2 (this is the floor, not a safety margin).
- **No prompt caching exists in the codebase today** (`INFO_REPORT.md` §4) — every call resends the full
  system message; these per-call costs already reflect that (no caching discount assumed).
- Calls = `n_poems × n_sets × n_runs × n_models`.

### 2.2 E1 cost — 1 model vs. 2 models, 50 vs. 100 poems, 2 sets

| Pool | Sets | Runs | Model config | Calls | Cost/call | **Total** |
|---|---|---|---|---|---|---|
| 50 poems | 2 | 2 | 1 model — GPT-5.4-mini (cheapest) | 200 | $0.0161 | **$3.22** |
| 50 poems | 2 | 2 | 1 model — Gemini 3.5 Flash (mid) | 200 | $0.0402 | **$8.04** |
| 50 poems | 2 | 2 | 1 model — Claude Sonnet 4.6 (priciest) | 200 | $0.0865 | **$17.30** |
| 50 poems | 2 | 2 | 2 models — GPT + Gemini (cheap combo) | 400 | $0.0563 avg | **$11.26** |
| 50 poems | 2 | 2 | 2 models — Claude + Gemini (quality combo) | 400 | $0.1267 avg | **$25.34** |
| 100 poems | 2 | 2 | 1 model — GPT-5.4-mini | 400 | $0.0161 | **$6.44** |
| 100 poems | 2 | 2 | 1 model — Gemini 3.5 Flash | 400 | $0.0402 | **$16.08** |
| 100 poems | 2 | 2 | 1 model — Claude Sonnet 4.6 | 400 | $0.0865 | **$34.60** |
| 100 poems | 2 | 2 | 2 models — GPT + Gemini | 800 | $0.0563 avg | **$22.52** |
| 100 poems | 2 | 2 | 2 models — Claude + Gemini | 800 | $0.1267 avg | **$50.68** |

**Marginal cost of a 3rd example set** (§1.4): multiply the "2 sets" totals above by 1.5 (2→3 sets). E.g.
100 poems / 2 models (cheap combo) / 3 sets ≈ $22.52 × 1.5 ≈ **$33.78** instead of $22.52.

**Headline range for E1 as actually scoped (2 sets, 2 runs)**: **≈$3 (smallest: 50 poems, 1 cheap model) to
≈$51 (largest: 100 poems, 2 premium models)**. A reasonable middle choice — 100 poems, 2 models
(GPT+Gemini) for robustness without Anthropic's premium — is **≈$22.50 for 2 sets, ≈$33.75 for 3 sets**.

---

## 3. Projection — full supervisors' request (10-fold CV, per-poet prompts, ~30 poets)

### 3.1 Reading of the request

Per-poet prompt (e.g., few-shot examples drawn from that poet's own style/verses), evaluated two ways:
**same-poet generalization** (held-out fold of that poet's own poems) and **cross-poet generalization**
(that same poet-specific prompt run against other poets' poems). Taken literally as a full design, this is a
**30×30 cross grid**: 30 poet-specific prompts, each evaluated against all 29 *other* poets' poems plus its
own held-out fold — before any CV multiplies it further.

### 3.2 Assumptions (explicit, since the manifest doesn't exist — §0)

- 30 poets selected from the 52-poet Ali corpus (presumably the better-annotated subset, so poems/poet is
  likely *above* the corpus-wide average of 3.2 — no real basis to pin this down yet).
- Average poems/poet: **low=3, mid=5, high=8** (the "high" case is capped by the corpus total of 167 poems
  across 52 poets, so a high-end 30-poet subset pulling 8/poet ≈ 240 poems is implausible unless skewed;
  treat high as an upper bound on cost, not a realistic forecast).
- 10-fold CV's inference cost ≈ evaluating each poem exactly once (each poem lands in exactly one held-out
  fold) — i.e., same-poet evaluation cost does **not** multiply by 10; it's `n_poems_in_pool × n_runs`.
- Cross-poet evaluation is the expensive part and has two design options:
  - **Full grid**: each of the 30 prompts evaluated against every other poet's full poem set.
  - **Cheaper alternative (recommended)**: each of the 30 prompts evaluated against one **shared, fixed
    cross-poet benchmark set** (e.g. 20–30 poems sampled once across all other poets) instead of a full
    30×30 grid — turns an O(n²) design into O(n).
- Per-call cost uses the same per-model figures as §2.1; "1 model" and "2 models" scenarios both given.

### 3.3 Low / mid / high scenarios

| Scenario | Pool basis | Same-poet calls | Cross-poet design | Cross-poet calls | Model(s) | **Total cost** |
|---|---|---|---|---|---|---|
| **Low** | 30 poets × 3 poems/poet = 90 poems | 90 × 2 runs = 180 | Cheap alt: 20-poem shared benchmark × 30 prompts × 2 runs | 1,200 | 1 model (GPT-5.4-mini, $0.0161) | **≈$22** |
| **Mid** | 30 poets × 5 poems/poet = 150 poems | 150 × 2 runs = 300 | Cheap alt: 30-poem shared benchmark × 30 prompts × 2 runs | 1,800 | 1 model (Gemini 3.5 Flash, $0.0402) | **≈$84** |
| **High** | 167-poem corpus cap, ≈8/poet for 30 poets (upper bound) | 167 × 2 runs × 2 models = 668 | **Full grid**: 30 prompts × ~29 other poets × ~5 poems/poet avg × 2 runs × 2 models | ≈17,400 | 2 models (Claude + Gemini, $0.1267 avg) | **≈$1,140** |

The **High** row is the literal full-grid reading of the request and is an order of magnitude more
expensive than Low/Mid — almost entirely because of the O(n²) cross-poet grid, not the CV itself. This is
the strongest argument for the cheaper alternative design.

### 3.4 Recommended cheaper alternative design

Replace the full 30×30 cross-poet grid with a **single shared cross-poet benchmark set** (e.g. 20–30 poems
stratified across the other 29 poets, held fixed across all 30 prompt evaluations). This answers the same
scientific question — "does a poet-specific prompt generalize beyond that poet?" — without re-paying for a
full grid, and keeps the projection in the **$20–$85** range (Low/Mid) instead of **~$1,100+** (High/full
grid). It also reuses the same shared benchmark set across all 30 prompts, which makes the per-prompt
cross-poet scores directly comparable (same eval set, not 30 different ones) — arguably a methodological
improvement over the full grid, not just a cost-cutting shortcut.

---

## 4. One-page recommendation for Tuesday

**Headline ask**: run E1 (example-sensitivity pilot) before committing to the full 30-poet CV design, because
E1's own open question (2 vs 3 example sets, §1.4) and the manifest gap (§0) both need resolving first, and
E1 is 1–2 orders of magnitude cheaper to get wrong.

**Decision points, in order**:

1. **Manifest gap.** `data/ali_poems/manifest.csv` doesn't exist — Phase B of the Ali corpus scrape (recon
   done, download not yet approved — `docs/phase4/SESSION_LOG.md`, 2026-10-10T02:10–02:45) needs to run
   before any real poem pool, real poet pool-size, or real per-poem verse-count number exists. Everything
   costed above is a placeholder until then.
2. **Poet choice for E1** — depends on #1. Decide whether to keep "one poet" strict (likely forces dropping
   the 100-poem condition for most poets, given the ≈3.2 poems/poet corpus average) or relax to "one poet's
   examples, cross-poet eval pool."
3. **2 vs 3 example sets** — 2 sets is underpowered for the actual claim (§1.4); 3 sets costs 1.5× more but
   is the minimum that can distinguish "example choice matters" from "run noise."
4. **Model scope for E1** — 1 model (cheap pilot signal) vs 2 models (cross-model robustness check, roughly
   2–3× the cost).
5. **Full-CV design** — full 30×30 grid (≈$1,100+) vs. the recommended shared-benchmark alternative
   (≈$20–85) — this should wait on E1's result anyway, since if E1 shows example choice barely matters,
   the per-poet-prompt premise of the full design weakens.

**Options table** (see below) is the one artifact meant to travel into Tuesday's meeting as-is.
