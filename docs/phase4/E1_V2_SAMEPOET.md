# E1 v2 — Same-Poet Check (Abu Nuwas vs. Other Poets)

**Question**: do the few-shot example verses (sets A/B/C), all three of which are drawn from Abu Nuwas
poems (`example_sets.json` source poems `16251`/`17234`/`21337`, all poet `أبو نواس`, all excluded from
the eval pool), help more on *other Abu Nuwas poems* in the eval pool than on poems by other poets?

**No new API calls.** Everything below is recomputed from the already-complete E1 v2 results
(`results/phase4_e1_v2/run_manifest.json`, `results/phase4_e1_v2/analysis_report.json`) using
`experiments/phase4_e1_v2/scoring_v2.py`'s existing per-poem TP/FP/FN counts, plus a new bootstrap
computed by `samepoet_analysis.py` (scratch script, not committed) and persisted to
`results/phase4_e1_v2/samepoet_analysis.json`. No files in `pilot_3models/`, `phase3_*`, or E1 v1
(`phase4_e1/`) were touched.

**Headline caveat, repeated throughout**: the Abu Nuwas group is **5 poems**, scored with **1 run per
cell** (no noise baseline, per CLAUDE.md rule 2). Every number below is indicative only. Most of the
bootstrap CIs are wide enough to include zero — treat this as a "no signal detected" result, not
evidence either for or against the hypothesis, except where stated otherwise.

**2026-10-14 update — PRIMARY metric is now verse** (user methodological decision, recorded in
`docs/phase4/SESSION_LOG.md`; CLAUDE.md is unedited and its rule 4 still flags plain verse-level
exists/not-exists as a supplementary diagnostic prone to rewarding `exists=True` regardless of span
correctness). §0 below adds the verse-criterion version of this same-poet check, computed fresh by
`experiments/phase4_e1_v2/samepoet_verse.py` (reuses `samepoet_analysis.py`'s bootstrap helpers
unchanged) and persisted to `results/phase4_e1_v2/samepoet_verse.json`. §1-§5 below are the original
strict/token-based write-up, kept as the secondary-metric view; §0's plain answer is now the
headline one.

---

## 0. Verse-criterion version (PRIMARY) — gain over Z per group

F1 at Z per group (verse criterion):

| Model | Abu Nuwas F1 | Other F1 |
|---|---|---|
| Claude | 0.312 | 0.389 |
| GPT | 0.567 | 0.545 |
| Gemini | 0.512 | 0.367 |

Gain over Z (verse), per model/set, with 95% CI, resampling poems **within** each group independently
(same method as §3's strict/token version):

| Model | Set | Gain abu_nuwas [CI] | Gain other [CI] | diff (abu−other) [CI] | Sig? |
|---|---|---|---|---|---|
| Claude | A | +0.406 [+0.047, +0.759] | +0.157 [+0.065, +0.247] | +0.249 [−0.125, +0.633] | ns |
| Claude | B | +0.343 [−0.063, +0.768] | +0.134 [+0.039, +0.226] | +0.209 [−0.192, +0.656] | ns |
| Claude | C | +0.021 [−0.270, +0.292] | +0.042 [−0.023, +0.101] | −0.021 [−0.336, +0.247] | ns |
| GPT | A | −0.011 [−0.059, +0.062] | −0.007 [−0.069, +0.051] | −0.004 [−0.084, +0.090] | ns |
| GPT | B | −0.009 [−0.057, +0.041] | −0.041 [−0.085, +0.007] | +0.032 [−0.034, +0.099] | ns |
| GPT | C | **−0.233** [−0.353, −0.079] | **−0.086** [−0.177, −0.015] | −0.148 [−0.295, +0.037] | ns |
| Gemini | A | +0.142 [+0.048, +0.287] | +0.115 [+0.060, +0.170] | +0.027 [−0.094, +0.176] | ns |
| Gemini | B | +0.092 [−0.054, +0.338] | +0.123 [+0.054, +0.194] | −0.031 [−0.199, +0.207] | ns |
| Gemini | C | +0.084 [−0.069, +0.262] | +0.089 [+0.030, +0.155] | −0.004 [−0.165, +0.180] | ns |

**All 9 diff cells are `ns` on verse** — same headline conclusion as the strict/token version (no
detectable same-poet effect). **One notable disagreement with §3**: the strict/token write-up's single
significant cell (Claude, set C, both criteria: diff ≈ −0.14 to −0.16, SIG) is **not significant on
verse** (diff = −0.021, CI [−0.336, +0.247] — much wider, straddling zero). That one significant
finding in the whole strict/token analysis does not survive the switch to the primary metric; it was
driven by a single poem (`9078`) going to 0 TP on span-matching at set C for 2 of 3 models (§4 below),
which does not move the *verse-level* exists/not-exists count the same way (the model can still have
said `exists=True` on that poem's verses even while pointing at the wrong span). **Plain answer under
the primary metric**: no evidence of a same-poet effect, and the one exception found under the
secondary metrics turns out not to replicate on the metric now being used for conclusions.

---

## 1. Per-model, per-set TP/FP/FN/P/R/F1 — Abu Nuwas (5 poems) vs. Other (20 poems)

Pool: Abu Nuwas = 5 poems, 59 verses. Other = 20 poems, 268 verses. (327 total, matching the full pool.)

Figures below are pulled directly from `results/phase4_e1_v2/analysis_report.json` (already computed by
the main E1 v2 analysis — reproduced here for the same-poet comparison in one place).

### Claude Sonnet 4.6 (anthropic)

| Set | Split | n poems | n verses | criterion | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Z | abu_nuwas | 5 | 59 | strict | 3 | 2 | 33 | 0.600 | 0.083 | 0.146 |
| Z | other | 20 | 268 | strict | 22 | 53 | 121 | 0.293 | 0.154 | 0.202 |
| Z | abu_nuwas | 5 | 59 | token | 3 | 2 | 33 | 0.600 | 0.083 | 0.146 |
| Z | other | 20 | 268 | token | 24 | 51 | 119 | 0.320 | 0.168 | 0.220 |
| A | abu_nuwas | 5 | 59 | strict | 9 | 28 | 27 | 0.243 | 0.250 | 0.247 |
| A | other | 20 | 268 | strict | 44 | 153 | 99 | 0.223 | 0.308 | 0.259 |
| A | abu_nuwas | 5 | 59 | token | 10 | 27 | 26 | 0.270 | 0.278 | 0.274 |
| A | other | 20 | 268 | token | 48 | 149 | 95 | 0.244 | 0.336 | 0.282 |
| B | abu_nuwas | 5 | 59 | strict | 10 | 24 | 26 | 0.294 | 0.278 | 0.286 |
| B | other | 20 | 268 | strict | 42 | 141 | 101 | 0.230 | 0.294 | 0.258 |
| B | abu_nuwas | 5 | 59 | token | 11 | 23 | 25 | 0.324 | 0.306 | 0.314 |
| B | other | 20 | 268 | token | 44 | 139 | 99 | 0.240 | 0.308 | 0.270 |
| C | abu_nuwas | 5 | 59 | strict | 1 | 8 | 35 | 0.111 | 0.028 | 0.044 |
| C | other | 20 | 268 | strict | 29 | 66 | 114 | 0.305 | 0.203 | 0.244 |
| C | abu_nuwas | 5 | 59 | token | 1 | 8 | 35 | 0.111 | 0.028 | 0.044 |
| C | other | 20 | 268 | token | 33 | 62 | 110 | 0.347 | 0.231 | 0.277 |

### GPT-5.4-mini (openai)

| Set | Split | n poems | n verses | criterion | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Z | abu_nuwas | 5 | 59 | strict | 8 | 25 | 28 | 0.242 | 0.222 | 0.232 |
| Z | other | 20 | 268 | strict | 40 | 139 | 103 | 0.223 | 0.280 | 0.248 |
| Z | abu_nuwas | 5 | 59 | token | 8 | 25 | 28 | 0.242 | 0.222 | 0.232 |
| Z | other | 20 | 268 | token | 43 | 136 | 100 | 0.240 | 0.301 | 0.267 |
| A | abu_nuwas | 5 | 59 | strict | 6 | 21 | 30 | 0.222 | 0.167 | 0.190 |
| A | other | 20 | 268 | strict | 39 | 125 | 104 | 0.238 | 0.273 | 0.254 |
| A | abu_nuwas | 5 | 59 | token | 7 | 20 | 29 | 0.259 | 0.194 | 0.222 |
| A | other | 20 | 268 | token | 39 | 125 | 104 | 0.238 | 0.273 | 0.254 |
| B | abu_nuwas | 5 | 59 | strict | 9 | 25 | 27 | 0.265 | 0.250 | 0.257 |
| B | other | 20 | 268 | strict | 40 | 150 | 103 | 0.211 | 0.280 | 0.240 |
| B | abu_nuwas | 5 | 59 | token | 10 | 24 | 26 | 0.294 | 0.278 | 0.286 |
| B | other | 20 | 268 | token | 42 | 148 | 101 | 0.221 | 0.294 | 0.252 |
| C | abu_nuwas | 5 | 59 | strict | 3 | 12 | 33 | 0.200 | 0.083 | 0.118 |
| C | other | 20 | 268 | strict | 24 | 72 | 119 | 0.250 | 0.168 | 0.201 |
| C | abu_nuwas | 5 | 59 | token | 4 | 11 | 32 | 0.267 | 0.111 | 0.157 |
| C | other | 20 | 268 | token | 26 | 70 | 117 | 0.271 | 0.182 | 0.218 |

### Gemini (served: gemini-3.6-flash)

| Set | Split | n poems | n verses | criterion | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Z | abu_nuwas | 5 | 59 | strict | 6 | 10 | 30 | 0.375 | 0.167 | 0.231 |
| Z | other | 20 | 268 | strict | 25 | 71 | 118 | 0.260 | 0.175 | 0.209 |
| Z | abu_nuwas | 5 | 59 | token | 6 | 10 | 30 | 0.375 | 0.167 | 0.231 |
| Z | other | 20 | 268 | token | 24 | 72 | 119 | 0.250 | 0.168 | 0.201 |
| A | abu_nuwas | 5 | 59 | strict | 7 | 18 | 29 | 0.280 | 0.194 | 0.230 |
| A | other | 20 | 268 | strict | 40 | 117 | 103 | 0.255 | 0.280 | 0.267 |
| A | abu_nuwas | 5 | 59 | token | 8 | 17 | 28 | 0.320 | 0.222 | 0.262 |
| A | other | 20 | 268 | token | 44 | 113 | 99 | 0.280 | 0.308 | 0.293 |
| B | abu_nuwas | 5 | 59 | strict | 10 | 16 | 26 | 0.385 | 0.278 | 0.323 |
| B | other | 20 | 268 | strict | 43 | 110 | 100 | 0.281 | 0.301 | 0.291 |
| B | abu_nuwas | 5 | 59 | token | 11 | 15 | 25 | 0.423 | 0.306 | 0.355 |
| B | other | 20 | 268 | token | 44 | 109 | 99 | 0.288 | 0.308 | 0.297 |
| C | abu_nuwas | 5 | 59 | strict | 6 | 14 | 30 | 0.300 | 0.167 | 0.214 |
| C | other | 20 | 268 | strict | 32 | 83 | 111 | 0.278 | 0.224 | 0.248 |
| C | abu_nuwas | 5 | 59 | token | 8 | 12 | 28 | 0.400 | 0.222 | 0.286 |
| C | other | 20 | 268 | token | 39 | 76 | 104 | 0.339 | 0.273 | 0.302 |

---

## 2. Confound check

**Verse counts per poem, per group**: Abu Nuwas poems are short (9, 9, 12, 13, 16 verses — mean 11.8,
median 12) vs. the "other" group, which spans 4 to 40 verses (mean 13.4, median 10) across 20 poets. The
groups are roughly comparable on verse count, so verse count alone is not an obvious confound, but the
Abu Nuwas group is a narrow, size-5 slice with no spread.

**Ground-truth density** (number of GT استعارة فعل spans per verse):

| Group | n poems | total verses | total GT spans | density (spans/verse) |
|---|---|---|---|---|
| abu_nuwas | 5 | 59 | 36 | 0.610 |
| other | 20 | 268 | 143 | 0.534 |

Abu Nuwas poems have **~14% higher GT density** than the other-poet group — slightly more positive
instances per verse, which would tend to make recall easier to achieve on Abu Nuwas poems regardless of
examples.

**F1 at Z (zero-shot, no extra examples) per group** — this answers "are Abu Nuwas poems simply easier or
harder for the model with no help at all?":

| Model | Criterion | Abu Nuwas F1 | Other F1 | Abu Nuwas easier? |
|---|---|---|---|---|
| Claude | strict | 0.146 | 0.202 | No — harder |
| Claude | token | 0.146 | 0.220 | No — harder |
| GPT | strict | 0.232 | 0.248 | Slightly harder |
| GPT | token | 0.232 | 0.267 | Slightly harder |
| Gemini | strict | 0.231 | 0.209 | Slightly easier |
| Gemini | token | 0.231 | 0.201 | Slightly easier |

**No consistent baseline-difficulty confound**: Abu Nuwas poems are *harder* at Z for Claude, *slightly
harder* for GPT, and *slightly easier* for Gemini. There's no uniform "Abu Nuwas poems are just easier/
harder" effect across models that would by itself explain a differential gain from Abu-Nuwas-sourced
examples — the baseline is roughly comparable (within ~0.03–0.07 F1) for 2 of 3 models, with Claude the
outlier (its Z/abu_nuwas is noticeably low, driven by a single near-zero-recall poem, see §4).

---

## 3. Gain over Z (the key measure)

For each model/criterion/set (A/B/C), gain = F1(set) − F1(Z), computed separately within each group
(poems resampled **within** that group only — Abu Nuwas poems never mixed into the "other" bootstrap
sample and vice versa). `diff = gain(abu_nuwas) − gain(other)`: positive means the Abu-Nuwas-sourced
examples helped Abu Nuwas poems *more* than they helped other poets' poems — the effect the question asks
about. 2,000-resample bootstrap, 95% CI.

### Claude Sonnet 4.6

| Set | Criterion | Gain abu_nuwas [CI] | Gain other [CI] | diff (abu−other) [CI] | Sig? |
|---|---|---|---|---|---|
| A | strict | +0.100 [−0.141, +0.341] | +0.057 [−0.018, +0.120] | +0.043 [−0.215, +0.310] | ns |
| A | token | +0.128 [−0.141, +0.419] | +0.062 [−0.006, +0.118] | +0.066 [−0.218, +0.376] | ns |
| B | strict | +0.139 [−0.065, +0.384] | +0.056 [−0.012, +0.117] | +0.084 [−0.128, +0.333] | ns |
| B | token | +0.168 [−0.065, +0.451] | +0.050 [−0.020, +0.115] | +0.118 [−0.123, +0.414] | ns |
| C | strict | **−0.102** [−0.300, +0.000] | +0.042 [−0.012, +0.090] | **−0.144** [−0.340, −0.015] | **SIG** |
| C | token | **−0.102** [−0.300, +0.000] | +0.057 [+0.007, +0.110] | **−0.159** [−0.354, −0.031] | **SIG** |

### GPT-5.4-mini

| Set | Criterion | Gain abu_nuwas [CI] | Gain other [CI] | diff (abu−other) [CI] | Sig? |
|---|---|---|---|---|---|
| A | strict | −0.041 [−0.164, +0.142] | +0.006 [−0.028, +0.054] | −0.047 [−0.179, +0.133] | ns |
| A | token | −0.010 [−0.092, +0.145] | −0.013 [−0.042, +0.028] | +0.003 [−0.097, +0.163] | ns |
| B | strict | +0.025 [−0.085, +0.165] | −0.008 [−0.045, +0.046] | +0.034 [−0.086, +0.170] | ns |
| B | token | +0.054 [−0.008, +0.170] | −0.015 [−0.057, +0.043] | +0.069 [−0.024, +0.191] | ns |
| C | strict | −0.114 [−0.241, +0.053] | −0.048 [−0.102, −0.004] | −0.067 [−0.204, +0.096] | ns |
| C | token | −0.075 [−0.225, +0.060] | −0.050 [−0.113, −0.001] | −0.026 [−0.182, +0.130] | ns |

### Gemini (served: gemini-3.6-flash)

| Set | Criterion | Gain abu_nuwas [CI] | Gain other [CI] | diff (abu−other) [CI] | Sig? |
|---|---|---|---|---|---|
| A | strict | −0.001 [−0.055, +0.077] | +0.057 [−0.028, +0.131] | −0.059 [−0.156, +0.050] | ns |
| A | token | +0.031 [−0.024, +0.092] | +0.093 [+0.026, +0.149] | −0.061 [−0.143, +0.025] | ns |
| B | strict | +0.092 [−0.012, +0.229] | +0.081 [+0.014, +0.144] | +0.011 [−0.117, +0.161] | ns |
| B | token | +0.124 [+0.017, +0.244] | +0.097 [+0.036, +0.153] | +0.028 [−0.092, +0.160] | ns |
| C | strict | −0.017 [−0.102, +0.092] | +0.039 [−0.018, +0.090] | −0.055 [−0.154, +0.059] | ns |
| C | token | +0.055 [−0.015, +0.126] | +0.102 [+0.052, +0.156] | −0.047 [−0.136, +0.039] | ns |

**18 of 18 model×criterion×set diff cells**: 17 are not significant (CI straddles zero), and the one
significant cell (Claude, set C, both criteria) is **negative** — the opposite sign from the hypothesis
(C hurt Abu Nuwas poems significantly *more* than it hurt other poems, not less).

---

## 4. Per-poem table — the 5 Abu Nuwas poems individually

F1 per set, per model/criterion. These are exactly the numbers the pooled Abu Nuwas-group F1 in §1/§3 is
built from — single-poem F1 is extremely noisy (poems have 9–16 verses each), shown here so the pooled
number isn't read as more stable than it is.

| Poem ID | Verses | Model | Criterion | Z | A | B | C |
|---|---|---|---|---|---|---|---|
| 9078  | 13 | Claude  | strict | 0.222 | 0.133 | 0.267 | 0.182 |
| 9078  | 13 | Claude  | token  | 0.222 | 0.133 | 0.267 | 0.182 |
| 9078  | 13 | GPT     | strict | 0.267 | 0.167 | 0.308 | 0.000 |
| 9078  | 13 | GPT     | token  | 0.267 | 0.167 | 0.308 | 0.000 |
| 9078  | 13 | Gemini  | strict | 0.000 | 0.000 | 0.364 | 0.000 |
| 9078  | 13 | Gemini  | token  | 0.000 | 0.000 | 0.364 | 0.000 |
| 13666 | 12 | Claude  | strict | 0.000 | 0.533 | 0.571 | 0.000 |
| 13666 | 12 | Claude  | token  | 0.000 | 0.667 | 0.714 | 0.000 |
| 13666 | 12 | GPT     | strict | 0.500 | 0.286 | 0.533 | 0.333 |
| 13666 | 12 | GPT     | token  | 0.500 | 0.429 | 0.533 | 0.500 |
| 13666 | 12 | Gemini  | strict | 0.545 | 0.462 | 0.615 | 0.500 |
| 13666 | 12 | Gemini  | token  | 0.545 | 0.615 | 0.615 | 0.667 |
| 17233 | 16 | Claude  | strict | 0.500 | 0.182 | 0.333 | 0.000 |
| 17233 | 16 | Claude  | token  | 0.500 | 0.182 | 0.333 | 0.000 |
| 17233 | 16 | GPT     | strict | 0.286 | 0.182 | 0.133 | 0.000 |
| 17233 | 16 | GPT     | token  | 0.286 | 0.182 | 0.267 | 0.000 |
| 17233 | 16 | Gemini  | strict | 0.167 | 0.154 | 0.143 | 0.000 |
| 17233 | 16 | Gemini  | token  | 0.167 | 0.154 | 0.286 | 0.182 |
| 31126 | 9  | Claude  | strict | 0.000 | 0.133 | 0.000 | 0.000 |
| 31126 | 9  | Claude  | token  | 0.000 | 0.133 | 0.000 | 0.000 |
| 31126 | 9  | GPT     | strict | 0.000 | 0.000 | 0.000 | 0.000 |
| 31126 | 9  | GPT     | token  | 0.000 | 0.000 | 0.000 | 0.000 |
| 31126 | 9  | Gemini  | strict | 0.000 | 0.143 | 0.167 | 0.167 |
| 31126 | 9  | Gemini  | token  | 0.000 | 0.143 | 0.167 | 0.167 |
| 31384 | 9  | Claude  | strict | 0.000 | 0.235 | 0.267 | 0.000 |
| 31384 | 9  | Claude  | token  | 0.000 | 0.235 | 0.267 | 0.000 |
| 31384 | 9  | GPT     | strict | 0.000 | 0.333 | 0.308 | 0.200 |
| 31384 | 9  | GPT     | token  | 0.000 | 0.333 | 0.308 | 0.200 |
| 31384 | 9  | Gemini  | strict | 0.400 | 0.364 | 0.333 | 0.364 |
| 31384 | 9  | Gemini  | token  | 0.400 | 0.364 | 0.333 | 0.364 |

**Individual-poem pattern**: poem `9078` is the outlier driving Claude's significant negative diff at C —
Claude goes from F1=0.222 (Z) to 0.182 (A... wait, actually C=0.182) with GPT dropping to 0.000 at C on
that same poem, and Gemini at 0.000 for Z/A/C but a one-off 0.364 at B. One poem (9078) swinging to near-
zero for 2 of 3 models at set C is enough, with only 5 poems in the group, to move the pooled Abu Nuwas
F1 sharply — exactly the single-poem sensitivity this table is meant to expose. Poems `31126` and `31384`
start at F1=0.000 at Z for 2 of 3 models (small poems, very few GT positives), so any nonzero TP at A/B/C
reads as a large relative "gain" that is really 1–2 additional hits on a 9-verse poem.

---

## 5. Plain answer (secondary metrics — see §0 for the current primary-metric answer)

**No — this data does not show that Abu-Nuwas-sourced examples help more on Abu Nuwas poems than on
other poets' poems.**

- Across all 3 models × 2 criteria × 3 example sets (18 comparisons), the gain-over-Z for the Abu Nuwas
  group is **not significantly different** from the gain-over-Z for the other-poets group in 17 of 18
  cases — the 95% CIs on the difference are wide and straddle zero.
- The **one significant case** (Claude, set C, strict and token) goes in the **opposite** direction: set
  C hurt Abu Nuwas poems' F1 significantly *more* than it hurt other poems' F1, not less — and this is
  driven heavily by a single poem (`9078`) collapsing to F1=0 for 2 of 3 models at set C, not a broad
  same-poet pattern.
- The confound check (§2) rules out "Abu Nuwas poems are just inherently easier, so any boost looks
  bigger" as a confound in a consistent direction — Abu Nuwas is *harder* than average at zero-shot for
  Claude and GPT, easier only for Gemini, and GT density is only mildly higher (+14%) for Abu Nuwas, not
  enough to explain swings of the size seen in §4.

**Why this should be read as "no detectable effect," not "proven absent"**: the Abu Nuwas group is only
**5 poems**, every cell is **1 run** (no noise baseline per CLAUDE.md rule 2), and §4 shows single-poem
swings of 0.1–0.3 F1 are common at this poem count — individual poems, not a same-poet effect, are doing
most of the moving. The bootstrap CIs in §3 are correspondingly wide (often spanning ±0.15–0.35 F1),
i.e. too wide to rule out a real but modest same-poet effect either. This check is **indicative only** and
should not be treated as a settled finding; a same-poet effect, if real, would need a substantially larger
Abu Nuwas sample (and ideally a 2nd run per cell) to detect reliably.

---

*Underlying numeric data: `results/phase4_e1_v2/samepoet_analysis.json` (gain-over-Z bootstrap, GT
density, per-poem table) and `results/phase4_e1_v2/analysis_report.json` (per-set/per-split TP/FP/FN/P/R/
F1, reused from the main E1 v2 analysis). No API calls were made for this check.*
