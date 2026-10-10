# Phase 4 — E1 Example-Sensitivity Pilot: Results

**Status: partial.** GPT-5.4-mini is complete (150/150 cells). Gemini 3.5 Flash is **incomplete**
(8/150 cells) because the configured Gemini API key is on Google's free tier (20 requests/day) and hit
that quota wall mid-run. Per the user's explicit decision, this report analyzes **GPT-5.4-mini only**;
Gemini results are not reported here and should be backfilled once the quota/billing issue is resolved.
Full detail of the run and the dotenv bug that preceded it: `docs/phase4/SESSION_LOG.md`.

## Design recap

- Poet: أبو نواس (Abu Nuwas). Element: مجاز (Trope), subtype focus استعارة فعل.
- 3 few-shot example sets, each built from 2 verses of a disjoint Abu Nuwas source poem (seed=42):
  - **Set A** — poem 16251, verses 1 & 5 (one dead-metaphor example on حُسن/رقّة, one on الدنيا/امتحن+تكشّف).
  - **Set B** — poem 17234, verses 3 & 4 (two dead-metaphor examples on كبر/صغر — "greatness/smallness of sin").
  - **Set C** — poem 21337, verses 1 & 2 — **both examples use the same root** (عقل/عقّل, "to
    bind/restrain" — the noun form being التعقيل), applied to الحياء in verse 1 and الكرى/الجفنين/الإغماء
    in verse 2. This is the narrowest, most repetitive set of the three.
- Eval pool: 50 poems, 1,010 verses, stratified **10 Abu Nuwas + 40 other poets** (seed=43), excluding the
  3 example-source poems and the 5 Phase-1 frozen poems.
- Models: Gemini 3.5 Flash + GPT-5.4-mini only, 1 run per (set, poem, model) — **no second run**, so
  there is no run-noise baseline for this pilot (see Caveats).

## Actual cost spent

| Provider | Calls succeeded | Calls failed | Spend |
|---|---|---|---|
| GPT-5.4-mini (openai) | 150 / 150 | 0 | **$1.28** |
| Gemini 3.5 Flash (google) | 8 / 150 | 142 (128× `429 RESOURCE_EXHAUSTED` free-tier quota, 14× transient `503`) | $0.18 |
| **Total** | | | **$1.46** |

Well under the $9 confirmed cap. (Dry-run estimate for the full 300-call design had been $7.95 — the
actual total is far lower only because 142 Gemini calls never happened, not because per-call cost ran
low.)

## Key results — GPT-5.4-mini, span-level, overall (50 poems, 1,010 verses)

**Strict matching:**

| Set | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| A | 92 | 180 | 833 | 0.338 | 0.099 | 0.154 |
| B | 132 | 199 | 802 | 0.399 | 0.141 | 0.209 |
| C | 78 | 125 | 844 | 0.384 | 0.085 | 0.139 |

**Token-overlap matching:**

| Set | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| A | 102 | 170 | 823 | 0.375 | 0.110 | 0.170 |
| B | 148 | 183 | 786 | 0.447 | 0.158 | 0.234 |
| C | 86 | 117 | 836 | 0.424 | 0.093 | 0.153 |

Both criteria agree on the ordering: **B > A > C**, with B the clear best and C the worst.

### Bootstrap 95% CI over poems (pairwise F1 differences, 2,000 resamples) — the only uncertainty measure used

| Pair | Strict point (F1₁−F1₂) | Strict 95% CI | Token point | Token 95% CI |
|---|---|---|---|---|
| A−B | −0.055 | [−0.108, 0.001] | −0.064 | [−0.121, **−0.006**] |
| A−C | +0.015 | [−0.014, 0.044] | +0.018 | [−0.011, 0.047] |
| B−C | +0.070 | [**0.023**, 0.124] | +0.081 | [**0.030**, 0.138] |

- **B is significantly better than C** on both criteria (CI excludes 0).
- **A vs. B**: CI excludes 0 under token-overlap but just touches 0 under strict (−0.108 to +0.001) —
  a borderline, criterion-dependent result, not a clean significant difference.
- **A vs. C**: not distinguishable (CI spans 0 on both criteria).

### Per-poem paired differences (strict F1, 50 poems)

| Comparison | Mean Δ | Poems where left > right | Poems where right > left | Tied (both 0 or equal) |
|---|---|---|---|---|
| B vs. A | +0.054 | 20 | 7 | 23 |
| B vs. C | +0.059 | 20 | 9 | 21 |
| A vs. C | +0.005 | 13 | 10 | 27 |

Many poems score F1=0 for both sets being compared (recall is low overall for this subtype), which is
why the "tied" count is large — the real signal is concentrated in a minority of poems where one set
catches a verse the other misses.

### Abu Nuwas (n=10 poems) vs. other poets (n=40 poems) — **indicative only, small n**

| Tag | Set | Strict TP/FP/FN | Strict F1 | Token F1 |
|---|---|---|---|---|
| abu_nuwas | A | 14/19/137 | 0.152 | 0.185 |
| abu_nuwas | B | 15/15/139 | 0.163 | 0.196 |
| abu_nuwas | C | 15/17/140 | 0.160 | 0.193 |
| other | A | 78/161/696 | 0.154 | 0.168 |
| other | B | 117/184/663 | 0.216 | 0.241 |
| other | C | 63/108/704 | 0.134 | 0.145 |

With only 10 Abu Nuwas poems, the abu_nuwas-vs-other split is **indicative only**: the three sets look
much closer together on Abu Nuwas's own poems than on the "other" poets, where B's advantage is largest
— but 10 poems is too small a sample to treat that gap as established rather than noise.

## Set C: the "both about التعقيل" effect

Set C's own two examples are visibly homogeneous — both are built on the same root ع-ق-ل (عقل/عقّل,
"to bind/restrain"; noun form التعقيل), applied to different objects (الحياء in verse 1, الكرى/الجفنين/
الإغماء in verse 2) but with no other metaphor pattern represented. Set C is the worst performer on both
criteria and is **significantly worse than Set B** (bootstrap CI excludes 0 on both strict and token).
This is consistent with — though does not prove — a narrow/repetitive example set generalizing worse
than a more varied one (Set A's two examples cover different objects: حُسن/رقّة and الدنيا/تكشّف; Set B's
two examples share a theme — كبر/صغر, greatness/smallness — but apply it across more varied phrasing).

## Caveats (read before drawing conclusions)

1. **No run-noise baseline.** This pilot used 1 run per (set, poem, model), per the frozen design — there
   is no second run to separate genuine set-to-set difference from a single run's noise.
   `CLAUDE.md` rule 2 documents a real precedent for this risk (an 8× apparent Kenning/Periphrasis gain
   that halved on a second run). **All set-to-set differences above should be read as indicative, not
   confirmed** — the bootstrap CI (over poems, not over repeated runs) is the only uncertainty measure
   available here, and it does not substitute for a second run.
2. **Abu Nuwas n=10 is small.** The abu_nuwas-vs-other breakdown above is explicitly indicative only.
3. **No model comparison.** Gemini is only 8/150 complete, so **this report does not compare Gemini vs.
   GPT-5.4-mini** — that comparison needs the Gemini backfill first.
4. **Set C's internal homogeneity is a real design artifact**, not a controlled variable — Set C isn't
   "a random few-shot set that happened to do worse," it's a set built from two near-duplicate examples.
   Its underperformance is consistent with that but the pilot wasn't designed to isolate homogeneity from
   other set-to-set differences (source poem, verse length, etc.).

## Bottom line

Example choice visibly moved GPT-5.4-mini's Trope/استعارة فعل F1 across the three sets tried (0.139 to
0.209 strict, 0.153 to 0.234 token) — a genuine, bootstrap-supported gap between the best (B) and worst
(C) sets, with C's weakness plausibly tied to its two near-duplicate عقل examples. But with only 1 run
per cell and no second run to check against, this should be treated as a real but **unconfirmed**
example-sensitivity signal for GPT-5.4-mini specifically — not yet a general finding, and not yet
compared against Gemini.
