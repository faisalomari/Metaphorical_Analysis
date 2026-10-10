# Phase 4 Cost Plan — Example-Sensitivity Pilot (E1) + Full-CV Projection

**Status**: planning + arithmetic only, now against the **real** Ali-corpus manifest (167 poems /
52 poets, downloaded 2026-10-10). Zero API calls made in producing this document; every number below
comes from local files (`data/ali_poems/manifest.csv` + `data/ali_poems/poems/*.json`) and arithmetic, per
instruction. All costs are estimates to be re-confirmed against real token counts the first time any cell
is actually run (`CLAUDE.md` rule 5 — cost estimate + explicit confirmation before any API call, every
time).

**This replaces the previous placeholder version** (2026-10-10T03:00–03:55, logged in
`docs/phase4/SESSION_LOG.md`), which was written before `manifest.csv` existed and used Phase 1's 5-poem
averages as a stand-in. The manifest now exists — every number in this version is computed directly from
the 167-poem corpus, not extrapolated from a different, longer-poem corpus.

---

## 0. Exclusions applied before any analysis

From the 167 downloaded poems:
- **Excluded: poem 28601** ("قصيدة شعراء عباسيون منسيون 9") — has 29 manual annotations but zero
  word-level text in the source site (`getWordsPoem` returns an empty array), so no verse text is
  obtainable. Cannot be used for either examples or eval.
- **Excluded: the 5 poems already used in the project** (`manifest.csv`'s `already_used_in_project`
  column) — `Imru1` (poem 3205), `Imru2` (2196), `Nabigha` (3218), `Jarir` (10539), `Abu_Tammam` (2127).
  These are the frozen Phase 1 TEST/DEV poems; per `CLAUDE.md` rule 1, TEST stays spent and DEV stays DEV —
  neither is available as new example or eval material.

**Resulting candidate pool: 161 poems**, spanning **50 distinct poets** (of the corpus's 52 — the 2
poets lost are those whose only poem was one of the 6 excluded above... in fact only Imru' al-Qais and
Jarir's poets lose poems to the exclusion, and both still have other poems in some corpora, but not in
this one specifically since each had only the excluded poem(s); see per-poet table below for exact counts).

---

## 1. Pool analysis — poet × element table

### 1.1 Per-poet summary (full candidate pool, 161 poems, sorted by poem count)

Trope/Simile/Kenning/Antonymy columns use this project's own `SUBSTRING_MAP` logic (مجاز/استعارة→Trope,
تشبيه→Simile, كناية→Kenning, طباق→Antonymy), applied to each poem's real annotation records (not the
coarser manifest CSV column, which collapses subtypes). The three right-most columns are the
`INFO_REPORT.md` §1e mid-difficulty subtype candidates, counted directly from each poem's `subtype` field.

| Poet | #poems | verses | annotations | Trope | مجاز عقلي | استعارة فعل | كناية عن صفة | Period |
|---|---|---|---|---|---|---|---|---|
| **أبو نواس** | **30** | **457** | 1,160 | **448** | 68 | **222** | 63 | العصر العباسي |
| النابغة الذبياني | 13 | 237 | 566 | 145 | 25 | 70 | 21 | العصر الجاهلي |
| بشار بن برد | 12 | 303 | 297 | 168 | 7 | 52 | 23 | مخضرم الدولتين |
| أبو تمّام | 11 | 302 | 1,365 | 608 | 111 | 239 | 49 | العصر العباسي |
| ابن الرومي | 10 | 163 | 435 | 178 | 27 | 91 | 29 | العصر العباسي |
| ديك الجن | 10 | 147 | 569 | 224 | 33 | 110 | 39 | العصر العباسي |
| زياد بن حنظلة | 7 | 35 | 145 | 56 | 11 | 19 | 32 | mixed |
| المُرَقِّشُ الأكبر | 4 | 50 | 206 | 63 | 14 | 30 | 27 | العصر الجاهلي |
| الفرزدق | 3 | 92 | 346 | 150 | 38 | 59 | 37 | العصر الأموي |
| البحتري | 3 | 88 | 261 | 111 | 28 | 47 | 0 | العصر العباسي |
| ابن قيس الرُّقيّات | 3 | 46 | 142 | 56 | 11 | 24 | 12 | العصر الأموي |
| الحمدوي | 3 | 20 | 57 | 17 | 5 | 6 | 3 | العصر العباسي |
| *(38 more poets, each 1–2 poems)* | 1–2 | — | — | — | — | — | — | — |

Pool-wide totals (161 poems): 3,246 verses, 9,634 annotations, Trope=3,643, Simile=644, Kenning=2,110,
Antonymy=690. Subtype totals pool-wide: مجاز عقلي=653, استعارة فعل=1,646, كناية عن صفة=709 — all three
mid-difficulty candidates have ample pool-wide volume; the question is concentration per poet.

### 1.2 Which poets satisfy "enough poems + enough instances to supply 2–3 examples AND leave a large
eval pool"?

**Candidates with ≥3 poems** (the practical floor for drawing 2–3 *disjoint* example-source poems without
touching the eval pool): the 12 poets in the table above. All 12 clear "enough instances" trivially — even
the smallest candidate (الحمدوي, 3 poems) has 6 استعارة فعل instances, enough for one 2-example set.

**The literal "leave 50–100 eval poems from the same poet" criterion fails for every poet.** The corpus
averages 3.2 poems/poet; even أبو نواس, the largest poet by a wide margin, has only 30 poems total — after
holding out 2–3 for examples, at most ~27–28 of *that poet's own* poems remain, nowhere near 50. This
confirms what the previous (placeholder) version of this plan had already flagged as a risk before the
manifest existed (§1.1 there) — it is now a confirmed fact, not a guess. **No single-poet design can hit a
50–100-poem eval pool from that poet alone.**

**Resolution: relax "eval pool" to cross-poet.** Examples are drawn from one poet (small, disjoint source
poems); the eval pool is the full remaining 158-poem cross-poet pool (161 minus the 3 example-source
poems — see §2.2). This trivially supports both a 50-poem subsample and a ~150-poem full-pool run, and
additionally lets the eval pool include the example poet's *other* poems (a same-poet-vs-other-poet split
is then available as a secondary readout, answering the same question Phase 2 session A looked at on the
old 5-poem corpus with no clear signal — this pool is ~30x bigger for that specific poet).

### 1.3 Recommendation

**Poet: أبو نواس (Abu Nuwas).** Reasons:
1. By far the largest poem count in the corpus (30, next is 13) — comfortably supports 3 disjoint,
   small example-source poems while leaving 27 of the poet's own poems in the eval pool.
2. **Not used anywhere in the project before** (not one of Imru' al-Qais / Al-Nabigha / Jarir / Abu
   Tammam) — a completely clean poet, no risk of any interaction with frozen Phase 1 material.
3. Largest absolute instance counts for the recommended mid-difficulty subtype: 222 استعارة فعل instances
   within this one poet alone (pool-wide total is 1,646 — this poet supplies ~13% of the entire corpus's
   supply on its own), far more than needed to pick clean, varied example verses.

**Element: مجاز (Trope)**, specifically oriented toward the **استعارة فعل** subtype — matches
`INFO_REPORT.md` §1e's #3 mid-difficulty recommendation (largest single subtype overall, n=110 in Phase 3,
recall 0.155–0.264, low criterion-sensitivity) and is the subtype with the cleanest, most abundant supply
in Abu Nuwas's own poems (5 instances in a single 6-verse poem, repeatedly).

**Alternatives considered and why not chosen**:
- **أبو تمّام** — even larger raw Trope volume (608 instances, 239 استعارة فعل), but this poet already has
  one poem (`Abu_Tammam`/2127) spent as frozen Phase 1 TEST. Reusing the *poet* is explicitly fine per
  standing discipline ("reusing a poet is fine, reusing an already-scored poem is not" — the Phase 1 poem
  is already excluded from this pool), but picking a poet with a foot already in frozen TEST adds an
  interpretive wrinkle (is a generalization gain partly "this poet's style is already known to these
  models from training data associations with the project"?) that a clean, unused poet avoids.
- **النابغة الذبياني** — same caveat (1 poem already DEV), 13 poems is a smaller margin than Abu Nuwas's
  30, otherwise a reasonable second choice.
- **مجاز عقلي** as the primary subtype — Abu Nuwas has only 68 instances (vs. 222 for استعارة فعل) and
  they are less evenly distributed across his short poems (clustered in a few longer ones), making clean
  2-example source poems harder to find without touching likely eval material.
- **كناية عن صفة** (periphrasis) — INFO_REPORT's own ranking already flags كناية/periphrasis overall as
  resistant to ordinary interventions (§1e "hardest... resistant to every Phase 1/2 intervention except
  Config C"); a few-shot example-sensitivity pilot is more informative on an element that responds to
  *ordinary* prompting at all, which Trope does and Kenning historically does not.

---

## 2. E1 design — example-sensitivity pilot

### 2.1 Example sets (3 sets, A/B/C — see §4.3 for why 3 over 2)

Each set = 2 verses, one poem per set, drawn from three of Abu Nuwas's shortest poems (6 verses each),
each independently rich in استعارة فعل annotations. **Selection method**: for each source poem, list the
distinct verse numbers carrying an استعارة فعل annotation, then `random.sample(verses, 2)` with
**`random.seed(42)`** (one global seed, sets drawn in order A→B→C) — reproducible, logged here in full so
it can be re-derived without re-running anything.

| Set | Source poem | Verses (of 6) with استعارة فعل | Seed-42 draw | Chosen verse text |
|---|---|---|---|---|
| A | poem 16251 (باب 7، قصيدة 2) | 1, 2, 3, 5 | **1, 5** | v1: "أيا رُبَّ وَجْهٍ في التُّراب عَتيقِ ... ويا رُبَّ حُسْنٍ في التُّرابِ رَقيقِ"; v5: "إِذا امتحن الدُّنْيا لَبيبٌ تكشَّفتْ ... له عن عَدُوّ في ثِياب صَديقِ" |
| B | poem 17234 (باب 7، قصيدة 6) | 3, 4 (only 2 available) | **3, 4** | v3: "يا كَبيرَ الذَّنْب عَفْوُ الـ ... ـله من ذَنْبك أَكْبَرْ"; v4: "أَكبرُ الأَشياء في أَصـ ... ـغر عَفْوِ الله يصغَرْ" |
| C | poem 21337 (باب 9، قصيدة 18) | 1, 2, 4, 6 | **1, 2** | v1: "ومترَّفٍ عقل الحَياءُُ لِسانَه ... فكَلامُه بالوَحْي والإِيماءِ"; v2: "لمّا نظرتُ إِلى الكَرَى في عَيْنه ... قد عقّل الجَفْنَيْن بالإِغماءِ" |

**Exclusion statement** (per the earlier plan's §1.2 template): examples are drawn from poems 16251,
17234, 21337 (Abu Nuwas); these 3 poems are excluded from the eval pool below.

### 2.2 Eval pool (real numbers, not placeholders)

- **Candidate pool after §0 exclusions**: 161 poems.
- **Eval pool** (also excluding the 3 example-source poems above): **158 poems, 3,228 verses** (mean
  20.4 verses/poem, range 2–103). Of these, 27 are Abu Nuwas's own remaining poems (439 verses) — kept in
  the eval pool rather than excluded wholesale, so a same-poet-as-examples vs. other-poet split is
  available as a secondary readout.
- **50-poem subsample**: drawn with `random.seed(43)` from the 158-poem eval pool (a different seed from
  the example draw, so the two randomizations don't interact) — **50 poems, 885 verses** (mean 17.7
  verses/poem; this specific sample, not a hypothetical average, is what gets costed in §3).
- **Full pool**: all 158 poems, 3,228 verses.

### 2.3 Comparison metrics (unchanged from the previous plan — still correct)

For each of (50-poem pool, full 158-poem pool) × (Set A, B, C):
- Raw TP/FP/FN per set, pooled across the poem pool (`CLAUDE.md` rule 3).
- Precision/recall/F1 per set, span-level, strict **and** token-overlap (`CLAUDE.md` rule 4).
- **Per-poem paired difference**: per-poem F1 (or TP) delta between sets, not just two pooled numbers.
- **Bootstrap CI over poems** (resample the poem pool with replacement, ~2,000 iterations, recompute
  pooled F1 per set each time) on each pairwise (F1_A − F1_B), (F1_A − F1_C), (F1_B − F1_C).
- **Run-to-run noise vs. set-to-set difference**: 2-run spread within each set vs. the cross-set gaps —
  the exact check that would have caught the Kenning/Periphrasis 8×→1/2 incident (`CLAUDE.md` rule 2) had
  it existed at the time.
- **Same-poet vs. other-poet split** (secondary, using §2.2's 27 Abu-Nuwas-remaining-poems subset): does
  example-sensitivity look different on the example poet's own other poems vs. the rest of the pool?

### 2.4 2 vs. 3 example sets

Unchanged reasoning from the previous plan: 2 sets gives one pairwise difference with no way to judge
whether it's typical variation or an outlier; 3 sets gives 3 pairwise differences, enough to see whether
set-to-set gaps cluster (bounded, real effect) or scatter as wide as run-to-run noise (no effect). The
3 example-source poems identified in §2.1 already exist and cost almost nothing extra (§3 shows the 3rd
set adds ~$1–2, not a meaningful budget line) — **recommend 3 sets outright**, not as a stretch goal.

---

## 3. Cost tables (real pool, real per-poem cost model)

### 3.1 Cost model — fixed to the real corpus, not Phase 1's longer poems

The previous plan used Phase 1's *pooled average* cost/call ($0.0865 Anthropic, $0.0161 OpenAI, $0.0402
Google), which bakes in Phase 1's poem lengths (23–81 verses, mean ≈45). The real Ali-corpus eval pool
averages only 20.4 verses/poem — using the flat pooled average would have **overstated** cost for this
corpus, because a whole-poem call has a large *fixed* component (frozen system message: 4 element
definitions + 19 examples, same regardless of poem length) plus a *per-verse variable* component.

Linear fit (`cost = a + b × n_verses`) over Phase 1's 5 real (verses, cost) points per model
(`run_manifest.json` data already in `INFO_REPORT.md` §4):

| Model | fixed cost `a` (per call) | per-verse cost `b` |
|---|---|---|
| Anthropic (Claude Sonnet 4.6, $3/$15 per MTok) | $0.00698 | $0.001684/verse |
| OpenAI (GPT-5.4-mini, $0.75/$4.50) | $0.00100 | $0.000316/verse |
| Google (Gemini 3.5 Flash, $1.50/$9.00) | $0.00454 | $0.000757/verse |

(Fit quality: predicts Phase 1's 5 known poem costs within ~3–15% — good enough for a planning estimate,
to be re-confirmed against real token counts per `CLAUDE.md` rule 5 before any actual spend.)

This model is applied per-poem-pool as `cost = n_poems × a + total_verses × b`, using the **real** eval
pool's poem count and verse total from §2.2 (not an assumed average).

### 3.2 E1 cost — 50-poem subsample vs. full 158-poem pool, 2 vs. 3 sets, 1 vs. 2 models, 2 runs

| Pool | Sets | Model(s) | Calls | **Total cost** |
|---|---|---|---|---|
| 50 poems (885 verses) | 2 | GPT-5.4-mini only | 200 | **$1.32** |
| 50 poems | 2 | Gemini 3.5 Flash only | 200 | **$3.59** |
| 50 poems | 2 | Claude Sonnet 4.6 only | 200 | **$7.36** |
| 50 poems | 2 | GPT + Gemini | 400 | **$4.91** |
| 50 poems | 2 | Claude + Gemini | 400 | **$10.95** |
| 50 poems | 3 | GPT-5.4-mini only | 300 | **$1.98** |
| 50 poems | 3 | GPT + Gemini | 600 | **$7.36** |
| 50 poems | 3 | Claude + Gemini | 600 | **$16.42** |
| Full pool, 158 poems (3,228 verses) | 2 | GPT-5.4-mini only | 632 | **$4.71** |
| Full pool | 2 | Gemini only | 632 | **$12.64** |
| Full pool | 2 | GPT + Gemini | 1,264 | **$17.36** |
| Full pool | 2 | Claude + Gemini | 1,264 | **$38.80** |
| Full pool | 3 | GPT-5.4-mini only | 948 | **$7.07** |
| Full pool | 3 | GPT + Gemini | 1,896 | **$26.03** |
| Full pool | 3 | Claude + Gemini | 1,896 | **$58.20** |

**Headline range, as actually recommended (3 sets, GPT+Gemini, 2 runs): ≈$7.36 for the 50-poem pilot,
≈$26.03 for the full 158-poem pool.** Both are substantially *cheaper* than the previous placeholder
plan's equivalent rows (≈$17–51) — the real corpus's shorter average poem length is the reason, and it
cuts cost, not raises it, contrary to the placeholder's stated risk direction.

**Recommended E1 sequencing**: run the 50-poem subsample first (≈$7.36, 3 sets × 2 runs, GPT+Gemini). If
the bootstrap CI (§2.3) already shows a clear, run-noise-exceeding set-to-set gap or a clear null result,
the full-pool run (≈$26.03 marginal, i.e., ≈$33 total for both) may not be needed to answer the pilot's
question — a second decision point for Tuesday, not a cost line to pre-commit.

### 3.3 Marginal cost of each design choice

- 2→3 sets: +50% of the 2-set total (exact, since cost scales linearly in sets) — e.g. $4.91→$7.36 for
  50 poems/GPT+Gemini — not the deciding factor between 2 and 3.
- 50-poem pool → full 158-poem pool: ≈3.5× (158/50 poems, but verse totals scale similarly: 3,228/885
  ≈3.65×) — the real driver of E1's cost range.
- 1 model → 2 models: exactly 2× (no shared fixed cost between providers in this design).

---

## 4. Projection — full supervisors' request (10-fold CV, per-poet prompts), now against real poet counts

### 4.1 The literal "~30 poets" ask does not fit this corpus

The real manifest shows only **50 distinct poets in the entire usable pool, and only 12 of them have ≥3
poems** (the practical floor for even a crude per-poet holdout, let alone 10-fold CV, which wants closer
to ≥10 samples per poet to form 10 meaningful folds). A literal "30 poets, 10-fold CV each" design would
need to include at least 18 poets with 1–2 poems, for whom 10-fold CV is not a meaningful operation (you
cannot form 10 folds from 1–2 poems). **This is a finding, not a guess** — the previous plan's "30 poets ×
3/5/8 poems" scenario table was built before the manifest existed and should be treated as superseded by
the table below.

### 4.2 Real poet tiers

| Tier | Poets | Poems | Verses | 10-fold CV meaningful? |
|---|---|---|---|---|
| **≥10 poems** (true 10-fold possible) | **6**: أبو نواس(30), النابغة الذبياني(13), بشار بن برد(12), أبو تمّام(11), ابن الرومي(10), ديك الجن(10) | 86 | 1,609 | Yes |
| ≥3 poems (minimal CV, <10-fold) | 12 (adds زياد بن حنظلة(7), المرقش الأكبر(4), الفرزدق(3), البحتري(3), ابن قيس الرقيات(3), الحمدوي(3)) | 109 | 1,940 | Only as k-fold with k=poems (e.g. 3-fold to 7-fold) |
| All poets, any count | 50 | 161 | 3,246 | No — most have 1–2 poems, cannot fold at all |

### 4.3 Cost — same-poet (holdout) + cross-poet, shared-benchmark design vs. literal full grid

Same-poet cost = evaluate each poet's own pool once (10-fold CV's per-fold cost sums to "each poem once" —
it doesn't multiply by 10). Cross-poet cost compares the recommended **shared benchmark** (reuse the
same 50-poem/885-verse eval subsample from §2.2 as a fixed cross-poet test set for every per-poet prompt)
against the **literal full grid** (each per-poet prompt evaluated against every *other* poet's actual
pool, real sizes, no shared set) — both computed exactly from real per-poet poem/verse counts, 2 runs:

| Tier | Model(s) | Same-poet cost | **Shared-benchmark total** | **Full-grid total** |
|---|---|---|---|---|
| 6 poets (≥10 poems) | GPT-mini only | $1.19 | **$5.14** | $7.13 |
| 6 poets | Gemini only | $3.22 | **$13.98** | $19.30 |
| 6 poets | GPT + Gemini | $4.41 | **$19.13** | $26.43 |
| 12 poets (≥3 poems) | GPT-mini only | $1.44 | **$9.36** | $17.33 |
| 12 poets | Gemini only | $3.93 | **$25.45** | $47.12 |
| 12 poets | GPT + Gemini | $5.37 | **$34.81** | $64.45 |

The full-grid/shared-benchmark gap here (≈1.4–1.9×) is much smaller than the previous placeholder's
projected gap (≈13–50×, from a hypothetical 30×30 grid) — because the *real* poet counts are small enough
(6–12, not 30) that a full grid isn't the O(n²) explosion the literal 30-poet ask would have been. This
changes the recommendation: **with the real, smaller poet tiers, the full grid is affordable** (≈$26–64
for 6–12 poets, GPT+Gemini, 2 runs) and answers the supervisors' literal question (per-poet prompt tested
against every other poet, not a fixed shared set) at a cost much closer to the shared-benchmark
alternative than previously estimated. The shared-benchmark alternative remains worth doing anyway for its
secondary benefit (every per-poet prompt's cross-poet score is measured on the exact same set, so scores
are directly comparable to each other), but cost alone no longer forces that choice.

### 4.4 Recommendation

Run the **6-poet tier** (true 10-fold-eligible: أبو نواس, النابغة الذبياني, بشار بن برد, أبو تمّام, ابن
الرومي, ديك الجن) with the **full grid**, GPT+Gemini, 2 runs: **≈$26.43 total**. This is the literal
supervisor request, on the subset of poets for which it's actually a meaningful operation, at a real,
affordable cost — a stronger answer than either the previous placeholder's $1,140 "High" scenario (an
artifact of assuming 30 poets that don't exist with enough data) or an unprincipled shared-benchmark
shortcut taken only because a full grid looked unaffordable (it no longer does, at the real scale).

Extending to the 12-poet tier (≥3 poems) is a secondary option (≈$64.45 full grid) but should wait on
whether the 6-poet tier's results already answer the generalization question — poets with only 3–7 poems
give each held-out fold very little data to score against, so the per-poet prompt's "own-poet" performance
estimate for those 6 additional poets will be noisier than for the 6 main poets regardless of spend.

---

## 5. One-page recommendation for Tuesday

**Headline ask**: run E1 first (≈$7.36 for the 50-poem pilot with the recommended 3-set design), because
it answers whether per-poet example choice matters at all before committing to the (now much cheaper, real
not placeholder) full-CV design.

**Chosen poet and element for E1**: **أبو نواس (Abu Nuwas)**, element **مجاز (Trope)**, subtype focus
**استعارة فعل** (§1.3). Example sets A/B/C and the exact verses are fixed and logged in §2.1
(`random.seed(42)`). Eval pool is the real 158-poem cross-poet pool (§2.2); 50-poem subsample fixed via
`random.seed(43)`.

**Decision points, in order**:

1. **E1 scope**: 50-poem pilot only (≈$7.36) first, full 158-poem pool (+≈$26.03 marginal) only if the
   pilot's bootstrap CI (§2.3) doesn't already give a clear answer.
2. **Model scope for E1**: GPT+Gemini (recommended, ≈2× a single cheap model, cross-model robustness) vs.
   GPT-5.4-mini alone (cheapest signal, ≈$2–7) vs. adding Claude (≈2–3× GPT+Gemini, premium option).
3. **Full-CV scope**: the 6-poet tier (true 10-fold-eligible, real full grid, ≈$26.43) is now affordable
   and answers the literal supervisor request — recommend running it over any shared-benchmark shortcut,
   which was only necessary under the old (incorrect) 30-poet assumption.
4. **12-poet extension**: optional, ≈$64.45 full grid, lower marginal value per dollar than the 6-poet
   tier (noisier per-poet folds) — a stretch goal, not a baseline ask.
5. **Full-CV timing**: run after E1, since a null example-sensitivity result from E1 would weaken the
   premise of per-poet prompt tuning in the first place.

**Options table** (the single artifact meant to travel into Tuesday's meeting as-is):

| Option | What it buys | Cost |
|---|---|---|
| E1 pilot (50 poems, 3 sets, GPT+Gemini, 2 runs) | Example-sensitivity signal + run-noise baseline | **$7.36** |
| E1 pilot, cheapest (50 poems, 3 sets, GPT-mini only) | Same signal, single-model, less robust | **$1.98** |
| E1 full pool (158 poems, 3 sets, GPT+Gemini, 2 runs) | Same question, full statistical power | **$26.03** |
| Full-CV, 6-poet tier, full grid, GPT+Gemini | Literal supervisor request, true 10-fold poets | **$26.43** |
| Full-CV, 12-poet tier, full grid, GPT+Gemini | Extends to all ≥3-poem poets | **$64.45** |
| **E1 pilot + full-CV 6-poet tier (recommended path)** | **Both questions answered** | **≈$33.79** |
