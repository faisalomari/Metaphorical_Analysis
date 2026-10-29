# Phase 7 — Subtype-Level Checks: 4 Subtypes (استعارة قديمة, كناية عن صفة, تشبيه قصير, تشبيه مطول)

**STATUS: COMPLETE.** All 4 subtypes x {zero-shot, few-shot} x 3 models, full run,
2026-10-29. Zero outstanding errors. Code: `experiments/phase7_subtypes/`.

**Scope**: per Dr. Ali Hussein's request, this phase runs the same verse-by-verse
subtype-detection check already built for استعارة قديمة (lexicalized/archaic metonymic
metaphor) and كناية عن صفة (periphrasis of quality) over two additional تشبيه (simile)
subtypes: **تشبيه قصير** (short simile — single-word vehicle, no elaboration) and
**تشبيه مطول** (elaborated simile — vehicle followed by an extra descriptive clause).
Same 25-poem / 327-verse-unit pool (`eval_pool_25.json`, seed=43, the pool already used
for استعارة قديمة/كناية عن صفة), same prompt/scoring machinery, same per-subtype
eval-pool-exclusion rule (a subtype's few-shot example poems are removed from *that
subtype's own* pool only — never a cross-subtype union, so one subtype's draw can never
retroactively shrink another's already-spent pool).

**All decisions below this point in the pipeline (dry-run cap, go/no-go, which cells to
retry, when to call the run final) were made autonomously** per the user's explicit
instruction left before going to sleep ("make the decision yourself, finish everything —
including the HTML — by morning"). Every decision is logged contemporaneously in
`docs/phase4/SESSION_LOG.md`.

---

## 0. Step 0 addendum — census + "تشبيه طويل" string check

Dr. Ali's reply used the informal phrasing "تشبيه طويل" for the elaborated-simile
subtype. Checked directly against the corpus rather than assumed:

| String | Exact annotation hits |
|---|---|
| `تشبيه طويل` | **0** |
| `تشبيه مطول` | **227** |

`تشبيه مطول` is confirmed as the real corpus string; it is also present in
`subtype_defs.py` with a definition and example, same as `تشبيه قصير`. No ambiguity to
flag to the user.

### Corpus-wide census (`census_tashbih2.py`)

| Subtype | Positive verses (corpus) | Poems w/ positive | Poets w/ positive | Notes passing quality filter | Eligible example verses | Positives in eval pool (25 poems) |
|---|---|---|---|---|---|---|
| تشبيه قصير | 137 | 58 | 29 | 57/160 (35.6%) | 53 | **13** |
| تشبيه مطول | 217 | 85 | 39 | 78/226 (34.5%) | 72 | **25** |

(For reference, the already-run subtypes: استعارة قديمة — 146 positive verses corpus-wide,
15 in-pool; كناية عن صفة — 619 positive verses corpus-wide, 49 in-pool.)

### Verse-boundary-crossing materiality check (تشبيه مطول only)

Some annotation spans cross a verse boundary (`verse_index` spanning >1 verse number).
Checked against the task's own 20% materiality bar before deciding whether the scoring
unit needs to change:

| Subtype | Multi-verse annotations | Share |
|---|---|---|
| تشبيه قصير | 3 / 160 | 1.9% |
| تشبيه مطول | 19 / 226 | **8.4%** |

Both well under 20% — **no STOP needed**, single-verse remained the scoring unit
(Option (a), same choice already made for the first 2 subtypes). All multi-verse-crossing
annotations were excluded from the few-shot *candidate* pool regardless (see §1), since a
scrambled/cross-verse span is a poor worked example even though it doesn't force a
unit-redefinition for scoring.

---

## 1. Step 1 — few-shot example draws (anti-"set C" guard, seed=42)

Standard draw: 2 examples per subtype, reject on same-poem/same-poet/missing-note/≥0.5
token-overlap with any pool poem (span, verse, or note text), re-draw with seed+1 on
rejection, full attempt log kept.

**Data-quality finding made during this draw** (not user-reported — caught by manual
inspection of the drawn examples before they were sent to any paid API): some
`span_text` values in the corpus are **not in verse reading order** — words from the
annotated span appear scrambled relative to the actual verse text. First surfaced on a
multi-verse-crossing تشبيه مطول annotation (poem 6174 v24–25, interleaved words from both
verses); a second, *single-verse* annotation (poem 27576 v30) showed the same scrambling,
proving it's a general corpus property, not limited to multi-verse spans. Fixed by adding
a strict contiguous-subsequence check (`is_in_reading_order()`) to the eligible-example
filter, on top of the existing multi-verse exclusion. Retroactively verified this changes
nothing already spent: all 4 few-shot examples used for استعارة قديمة/كناية عن صفة
(poems 27110, 6174 v5, 8470, 4480) are clean/in-order. **This does not affect scoring**
(token-overlap and verse-level matching are both order-independent) — it only matters for
which candidates are safe to hand an LLM as a worked example, and is noted here as a
standing corpus-quality caveat for any future few-shot work on this corpus.

### Final examples drawn (both clean under `is_in_reading_order`)

| Subtype | Example 1 | Example 2 |
|---|---|---|
| تشبيه قصير | ديك الجن, poem 18729 v24 — «يا كلَّ مَنْيٍ» | أبو دلامة, poem 28688 v5 — «جَعَلُوا عَلَيْهَا طِينَةً كالعَقْرَبِ» |
| تشبيه مطول | الأعشى ميمون, poem 6574 v4 — «وَهْيَ إِنْ تَقْعُدْ نَقًا مِنْ عَالِجٍ» | أبو دلامة, poem 28688 v7 — «وإذَا شَبِيهٌ بالأفَاعِي رُقِّشَتْ» |

0 pool poems removed by either draw (the drawn example poems were not already in
`eval_pool_25.json`), so both subtypes kept the full 25-poem/327-verse pool. System-prompt
sizes: تشبيه قصير 227 tok zero-shot / 558 tok few-shot; تشبيه مطول 277 tok zero-shot /
604 tok few-shot.

---

## 2. Step 2 — cost dry-run + go decision

Same token-based method as the original 2-subtype dry-run (real tiktoken input tokens +
Phase-3-calibrated 120-token output estimate per call).

| | Calls | Claude | GPT | Gemini | Total |
|---|---|---|---|---|---|
| استعارة قديمة + كناية عن صفة (already spent) | 3,924 | $5.34 | $1.45 | $2.91 | **$9.70** |
| تشبيه قصير + تشبيه مطول (new) | 3,924 | $5.18 | $1.41 | $2.82 | **$9.41** |
| **Combined 4-subtype total** | **7,848** | | | | **~$19.12** |

**Pool-positive floor check**: the task's own gate is <30 in-pool positives → flag
indicative-only, run anyway (established precedent: استعارة قديمة already ran at n=15).
Three of the four subtypes fall under the floor:

| Subtype | In-pool positives | Status |
|---|---|---|
| استعارة قديمة | 15 | indicative-only |
| تشبيه قصير | 13 | indicative-only |
| تشبيه مطول | 25 | indicative-only |
| كناية عن صفة | 49 | **above floor** |

**Go decision (autonomous, per the user's sleep-time instruction)**: applied the same
buffer ratio the user had already approved minutes earlier at the identical decision
point for the first 2 subtypes (~1.55x on a $9.70 estimate → $15 cap). Cap set to **$15**
for the $9.41-estimated new run. Smoke-tested first (`--max-additional-usd 1
--limit-poems 1 --limit-verses-per-poem 1`): 12/12 calls succeeded, $0.0296 spent, all raw
responses verified as clean, on-topic `{exists, appearance, reasoning}` JSON.

---

## 3. Step 3 — the real run

Both runs (original + new) executed in the background, each with its own manifest/raw
directory to avoid any file-write race:

| Run | Manifest | Calls | Result | Spend |
|---|---|---|---|---|
| استعارة قديمة / كناية عن صفة | `run_manifest.json` | 3,924 | **3,924/3,924 ok, 0 errors** | — |
| تشبيه قصير / تشبيه مطول | `run_manifest_tashbih2.json` | 3,924 | **3,924/3,924 ok, 0 errors** (2 transient Google 503s hit mid-run, retried individually post-run and succeeded) | $9.975 |

Full identical coverage per (subtype, condition, model) confirmed programmatically
(`score_phase7.py`'s own coverage check: **True**) before any number below was treated as
final.

---

## 4. Results — verse-level F1 (primary metric), raw TP/FP/FN always shown

All 4 subtypes, 2 conditions (zero/few), 3 models + 3-model majority-vote ensemble.
**استعارة قديمة, تشبيه قصير, تشبيه مطول are indicative-only (n<30 pool positives) —
read every number for these three as "what happened in this one 25-poem sample," not as
a generalizable estimate.** كناية عن صفة (n=49) is the one subtype in this batch above
the pool-positive floor.

### استعارة قديمة (pool positives = 15 — INDICATIVE ONLY)

| Model | Zero F1 (TP/FP/FN) | Few F1 (TP/FP/FN) |
|---|---|---|
| Claude | 0.114 (2/18/13) | 0.126 (9/119/6) |
| GPT | 0.065 (3/75/12) | 0.140 (3/25/12) |
| Gemini | **0.211** (8/53/7) | **0.182** (12/105/3) |
| 3-model ensemble | 0.175 (5/37/10) | 0.162 (9/87/6) |

### كناية عن صفة (pool positives = 49)

| Model | Zero F1 (TP/FP/FN) | Few F1 (TP/FP/FN) |
|---|---|---|
| Claude | 0.318 (14/25/35) | **0.322** (24/76/25) |
| GPT | **0.317** (42/174/7) | 0.247 (20/93/29) |
| Gemini | 0.297 (15/37/34) | 0.342 (27/82/22) |
| 3-model ensemble | 0.336 (18/40/31) | 0.282 (21/79/28) |

### تشبيه قصير (pool positives = 13 — INDICATIVE ONLY)

| Model | Zero F1 (TP/FP/FN) | Few F1 (TP/FP/FN) |
|---|---|---|
| Claude | **0.262** (8/40/5) | 0.188 (8/64/5) |
| GPT | 0.209 (9/64/4) | 0.180 (9/78/4) |
| Gemini | 0.258 (4/14/9) | **0.250** (7/36/6) |
| 3-model ensemble | 0.298 (7/27/6) | 0.254 (9/49/4) |

### تشبيه مطول (pool positives = 25 — INDICATIVE ONLY)

| Model | Zero F1 (TP/FP/FN) | Few F1 (TP/FP/FN) |
|---|---|---|
| Claude | **0.394** (13/28/12) | 0.306 (13/47/12) |
| GPT | 0.283 (15/66/10) | **0.370** (20/63/5) |
| Gemini | 0.388 (13/29/12) | 0.328 (11/31/14) |
| 3-model ensemble | **0.406** (14/30/11) | 0.351 (13/36/12) |

Bootstrap 95% CIs (few − zero, over poems, n=2000) for the 3-model ensemble, verse
criterion: all four subtypes' intervals straddle 0 (استعارة قديمة −0.11 to +0.20;
تشبيه قصير −0.03 to +0.08; تشبيه مطول −0.07 to +0.02) except كناية عن صفة, whose
few-shot delta is likewise not distinguishable from zero at this sample size. **No
subtype shows an ensemble-level few-shot effect that survives a 95% CI at n≤49 pool
positives** — same "too few positives to prove a few-shot effect" pattern Phase 4 ran
into on other subtypes at comparable sample sizes.

**At the per-model level (not the ensemble), a handful of individual few-vs-zero deltas do
clear their own 95% CI**, all but one concentrated in GPT-5.4-mini: few-shot significantly
**helps** GPT on تشبيه مطول (verse +0.087 [+0.021, +0.133], strict +0.069 [+0.006, +0.114],
token +0.087 [+0.021, +0.133]) but significantly **hurts** it on تشبيه قصير (strict −0.059
[−0.127, −0.004], token −0.046 [−0.102, −0.004]) and on كناية عن صفة (token only, −0.064
[−0.136, −0.003]). Claude shows one significant hit too, on تشبيه قصير/verse (−0.074
[−0.162, −0.009]). These are real per-model, per-criterion signals, opposite in direction
across subtypes for the same model (GPT), and at these small sample sizes (13–49 pool
positives) should be read as "GPT's few-shot behavior is subtype-sensitive here," not as a
stable rule for whether few-shot helps or hurts that model in general.

---

## 5. Design-choice check per subtype: GPT-zero-shot + Claude-few-shot, with/without Gemini

Phase 4's production candidate ("GPT-Z + Claude-FS") re-checked here per-subtype:
GPT-Z alone, Claude-FS alone, their OR combination, their AND combination, and the
3-model majority vote (few-shot), plus a Gemini-leave-one-out CI check.

| Subtype | GPT-Z alone | Claude-FS alone | OR | AND | 3-vote (few) | Gemini LOO: 3-model vs 2-model (no Gemini) |
|---|---|---|---|---|---|---|
| استعارة قديمة | 0.065 | 0.126 | 0.108 | 0.086 | 0.162 | 0.162 vs 0.111, CI [−0.11, 0.20] (overlaps 0) |
| كناية عن صفة | 0.317 | 0.322 | 0.301 | **0.356** | 0.282 | 0.282 vs 0.231, CI [−0.04, 0.16] (overlaps 0) |
| تشبيه قصير | 0.209 | 0.188 | 0.154 | **0.296** | 0.254 | 0.254 vs 0.230, CI [−0.03, 0.08] (overlaps 0) |
| تشبيه مطول | 0.283 | 0.306 | 0.281 | 0.317 | 0.351 | 0.351 vs **0.381**, CI [−0.07, 0.02] (overlaps 0; point estimate favors dropping Gemini here) |

**No consistent winner across subtypes.** AND is best for 2 of 4 (كناية عن صفة,
تشبيه قصير); the full 3-model vote is best for 1 of 4 (استعارة قديمة); for تشبيه مطول
the 2-model (no-Gemini) combination has the higher point estimate, the only subtype in
this batch where dropping Gemini looks (non-significantly) better than keeping it. Every
comparison's CI overlaps zero — none of these differences clear the bootstrap bar at
these sample sizes (n=13–49 pool positives). **This batch does not change the Phase 4
production recommendation** (GPT-Z + Claude-FS, OR'd) either way — it simply shows that
recommendation is not uniformly best or worst across these 4 subtypes either, within
noise.

---

## 6. Rank-only comparison with earlier Phase 1/3 patterns

**Caveat up front, same as Phase 4's own design-choice doc**: these are *different
experiments* — Phase 3's numbers are **recall-only** (every row is a known positive,
no FP/precision/F1 is computable by that design — see `INFO_REPORT.md` §1d), scored on
a different, larger sample than this phase's 25-poem pool, under a different prompt
variant. Only the **relative ordering across subtypes** is worth reading across phases,
not the absolute numbers.

| Subtype | Phase 3 recall-only rank (Gemini/GPT, strict+token, `INFO_REPORT.md` §1d) | Phase 7 F1 rank (3-model ensemble, zero-shot, verse) |
|---|---|---|
| تشبيه مطول | 1st (recall 0.667–0.933, near-ceiling) | **1st** (F1 0.406) |
| كناية عن صفة | 3rd (recall 0.351–0.486, mid) | **2nd** (F1 0.336) |
| تشبيه قصير | 2nd (recall 0.615–0.846, near-ceiling) | **3rd** (F1 0.298) |
| استعارة قديمة | 4th (recall 0.176–0.412, hardest of these 4) | **4th** (F1 0.175) |

**تشبيه مطول's top rank and استعارة قديمة's bottom rank both survive the switch from a
recall-only, larger-sample measure to a full precision/recall, small-sample measure** —
the most durable pattern in this comparison. **تشبيه قصير and كناية عن صفة swap places**:
تشبيه قصير's recall-only numbers were near-ceiling (second only to تشبيه مطول), but at
n=13 pool positives in this phase, its FP count is large enough relative to that small
denominator to pull its F1 below كناية عن صفة's (which has roughly 4x as many pool
positives, n=49, giving its precision term more room to average out). This is consistent
with — not a contradiction of — CLAUDE.md's standing rule 3 (always show raw TP/FP/FN): a
near-ceiling recall and a mediocre F1 can both be true for the same subtype when its
positive count is this small and its false-positive count this large.

---

## 7. Plain answer

**All 4 subtypes ran cleanly to completion, 7,848 calls total, 0 unresolved errors,
~$20.74 actual total spend (original run $10.76 + new run $9.98) against a combined
~$19.12 pre-run estimate — both runs individually stayed under their own $15 hard cap.**
تشبيه مطول is the easiest of the 4 (F1 up to 0.406, 3-model ensemble, zero-shot) and
confirms its historical near-ceiling standing from Phase 3's recall-only numbers.
استعارة قديمة remains the hardest (F1 0.175 at best), also consistent with its
historical standing. تشبيه قصير and كناية عن صفة land in the middle but in reversed
relative order versus Phase 3's recall-only ranking — explained by تشبيه قصير's very
thin pool-positive count (13) amplifying the effect of its false positives on F1 in a way
recall alone never showed. **Three of the four subtypes (استعارة قديمة, تشبيه قصير,
تشبيه مطول) are indicative-only** (pool positives 13–25, under this project's own n=30
floor) — their numbers describe this one 25-poem sample, not a generalizable claim, and
every few-shot-vs-zero-shot and Gemini-leave-one-out comparison in this batch has a
bootstrap 95% CI overlapping zero, i.e. **no comparative conclusion in this batch clears
the statistical bar CLAUDE.md's standing discipline requires** — consistent with every
other thin-sample subtype check this project has already run. The one above-floor
subtype, كناية عن صفة (n=49), shows AND(GPT-Z, Claude-FS) as its single best combination
(F1 0.356) but that too sits inside a CI that overlaps the alternatives — a plausible
but unproven signal, not a new production recommendation.

**Known data-quality caveat for future few-shot work on this corpus**: some annotation
`span_text` values are not stored in verse reading order (§1) — a general corpus
property unrelated to multi-verse crossing, now guarded against by
`is_in_reading_order()` in the few-shot example filter, and worth carrying into any
future phase that draws worked examples from this corpus's annotation notes.
