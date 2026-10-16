# E1 v2 Results — Example-Sensitivity Pilot on the Phase 3 Subtype Prompt

**Design**: E1 v2 (`experiments/phase4_e1_v2/`), built on `phase3_subelements`'s subtype-level prompt
(`subtype_prompts.SYSTEM_TEMPLATE` / `fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT`) — **not** Phase 1's
whole-poem prompt that E1 v1 mistakenly reused (see `docs/phase4/PROMPT_INVENTORY.md`). Target subtype:
**استعارة فعل** (verbal metaphor, parent مجاز/Trope). One API call per verse-unit, schema
`{"exists","appearance","reasoning"}`.

- **Pool**: 25 poems (5 أبو نواس + 20 other poets), seed=43, persisted at
  `experiments/phase4_e1_v2/config/eval_pool_25.json` — 327 verse-units total.
- **Sets**: Z (zero-shot — Phase 3's original 1-example definition prompt, no injected fewshot block),
  A/B/C (fewshot — Z's prompt + 2 extra example verses each, reused unchanged from E1 v1's
  `config/example_sets.json`, seed=42).
- **Models**: Claude Sonnet 4.6 (anthropic), GPT-5.4-mini (openai), Gemini (google, requested as
  `gemini-3.5-flash` — **actually served and billed as `gemini-3.6-flash`**, confirmed directly from the
  API response's own `model_version` field in this session's pre-run verification call, consistent with
  `FULL_COST_MODEL.md`'s independent finding that `gemini-3.5-flash` no longer exists on Google's current
  pricing/models pages).
- **Runs**: 1 run per (set, poem, verse, model) cell — **no second run, no noise baseline**. Every
  set-to-set and model-to-model difference below is reported with a bootstrap 95% CI, but **all
  differences are indicative only**, per CLAUDE.md rule 2 (the Kenning/Periphrasis 8x→1/2 incident is the
  concrete precedent for why a single run's apparent gain/loss cannot be trusted on its own).
- **Completeness**: 3,924/3,924 cells complete, 0 errors, verified every (set, model) combination has
  exactly 327/327 cells.
- **Actual total cost: $10.5680** (anthropic $7.0920, openai $1.2060, google $2.2700) — not an estimate;
  computed from real logged token usage × `config.py` pricing after the run. Anthropic's $3/$15-per-MTok
  rate makes it the dominant cost driver despite having the same call count as the other two models.

Scoring: `experiments/phase4_e1_v2/scoring_v2.py`, three criteria —
- **verse (PRIMARY as of 2026-10-14)**: model's binary `exists` vs. whether the verse has any GT span at
  all, no span-text match. **This is a user methodological decision, recorded in
  `docs/phase4/SESSION_LOG.md`** — not a project-rule change, and CLAUDE.md is not edited.
  **CLAUDE.md rule 4 still flags this metric as a supplementary diagnostic prone to rewarding
  `exists=True` regardless of whether the span itself is right** (the documented كناية/Periphrasis
  artifact is the standing precedent). Every verse-primary conclusion below should be read with that
  caveat live, and §4 below states explicitly where verse and the secondary span-level metrics disagree.
- **strict (secondary)**: `appearance` must exactly span-match a GT span (`pilot_3models.span_matching`,
  reused unchanged).
- **token (secondary)**: token-overlap match on the same GT spans.

**أبو نواس split (n=5 poems) is indicative only** — too small to draw a reliable same-poet-vs-other-poet
conclusion on its own; included for completeness, not as a finding.

---

## 1. Claude Sonnet 4.6 (anthropic)

### criterion: verse (PRIMARY — user decision, see CLAUDE.md rule 4 caveat above)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 39 | 41 | 88 | 0.487 | 0.307 | 0.377 |
| Z | abu_nuwas | 5 | 0 | 22 | 1.000 | 0.185 | 0.312 |
| Z | other | 34 | 41 | 66 | 0.453 | 0.340 | 0.389 |
| A | overall | 104 | 130 | 23 | 0.444 | 0.819 | 0.576 |
| A | abu_nuwas | 23 | 14 | 4 | 0.622 | 0.852 | 0.719 |
| A | other | 81 | 116 | 19 | 0.411 | 0.810 | 0.545 |
| B | overall | 94 | 123 | 33 | 0.433 | 0.740 | 0.547 |
| B | abu_nuwas | 20 | 14 | 7 | 0.588 | 0.741 | 0.656 |
| B | other | 74 | 109 | 26 | 0.404 | 0.740 | 0.523 |
| C | overall | 48 | 56 | 79 | 0.462 | 0.378 | 0.416 |
| C | abu_nuwas | 6 | 3 | 21 | 0.667 | 0.222 | 0.333 |
| C | other | 42 | 53 | 58 | 0.442 | 0.420 | 0.431 |

### criterion: strict (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 25 | 55 | 154 | 0.312 | 0.140 | 0.193 |
| Z | abu_nuwas | 3 | 2 | 33 | 0.600 | 0.083 | 0.146 |
| Z | other | 22 | 53 | 121 | 0.293 | 0.154 | 0.202 |
| A | overall | 53 | 181 | 126 | 0.226 | 0.296 | 0.257 |
| A | abu_nuwas | 9 | 28 | 27 | 0.243 | 0.250 | 0.247 |
| A | other | 44 | 153 | 99 | 0.223 | 0.308 | 0.259 |
| B | overall | 52 | 165 | 127 | 0.240 | 0.291 | 0.263 |
| B | abu_nuwas | 10 | 24 | 26 | 0.294 | 0.278 | 0.286 |
| B | other | 42 | 141 | 101 | 0.230 | 0.294 | 0.258 |
| C | overall | 30 | 74 | 149 | 0.288 | 0.168 | 0.212 |
| C | abu_nuwas | 1 | 8 | 35 | 0.111 | 0.028 | 0.044 |
| C | other | 29 | 66 | 114 | 0.305 | 0.203 | 0.244 |

### criterion: token (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 27 | 53 | 152 | 0.338 | 0.151 | 0.208 |
| A | overall | 58 | 176 | 121 | 0.248 | 0.324 | 0.281 |
| B | overall | 55 | 162 | 124 | 0.253 | 0.307 | 0.278 |
| C | overall | 34 | 70 | 145 | 0.327 | 0.190 | 0.240 |
(abu_nuwas/other splits in `results/phase4_e1_v2/analysis_report.json`.)

### Pairwise bootstrap 95% CI (F1_i − F1_j), per-poem diff signs
| Pair | verse | strict | token |
|---|---|---|---|
| Z−A | **−0.199 [−0.302,−0.100] SIG** | −0.064 [−0.126,+0.010] ns | **−0.072 [−0.140,−0.000] SIG** |
| Z−B | **−0.170 [−0.280,−0.068] SIG** | **−0.070 [−0.133,−0.005] SIG** | −0.069 [−0.145,+0.001] ns |
| Z−C | −0.039 [−0.103,+0.036] ns | −0.019 [−0.066,+0.043] ns | −0.032 [−0.083,+0.030] ns |
| A−B | +0.030 [−0.000,+0.065] ns | −0.006 [−0.044,+0.025] ns | +0.003 [−0.038,+0.034] ns |
| A−C | **+0.161 [+0.085,+0.249] SIG** | +0.045 [−0.007,+0.101] ns | +0.041 [−0.026,+0.111] ns |
| B−C | **+0.131 [+0.050,+0.225] SIG** | **+0.051 [+0.003,+0.114] SIG** | +0.038 [−0.036,+0.122] ns |

---

## 2. GPT-5.4-mini (openai)

### criterion: verse (PRIMARY — user decision, see CLAUDE.md rule 4 caveat above)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 93 | 119 | 34 | 0.439 | 0.732 | 0.549 |
| Z | abu_nuwas | 17 | 16 | 10 | 0.515 | 0.630 | 0.567 |
| Z | other | 76 | 103 | 24 | 0.425 | 0.760 | 0.545 |
| A | overall | 86 | 105 | 41 | 0.450 | 0.677 | 0.541 |
| A | abu_nuwas | 15 | 12 | 12 | 0.556 | 0.556 | 0.556 |
| A | other | 71 | 93 | 29 | 0.433 | 0.710 | 0.538 |
| B | overall | 90 | 134 | 37 | 0.402 | 0.709 | 0.513 |
| B | abu_nuwas | 17 | 17 | 10 | 0.500 | 0.630 | 0.557 |
| B | other | 73 | 117 | 27 | 0.384 | 0.730 | 0.503 |
| C | overall | 52 | 59 | 75 | 0.468 | 0.409 | 0.437 |
| C | abu_nuwas | 7 | 8 | 20 | 0.467 | 0.259 | 0.333 |
| C | other | 45 | 51 | 55 | 0.469 | 0.450 | 0.459 |

### criterion: strict (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 48 | 164 | 131 | 0.226 | 0.268 | 0.246 |
| Z | abu_nuwas | 8 | 25 | 28 | 0.242 | 0.222 | 0.232 |
| Z | other | 40 | 139 | 103 | 0.223 | 0.280 | 0.248 |
| A | overall | 45 | 146 | 134 | 0.236 | 0.251 | 0.243 |
| A | abu_nuwas | 6 | 21 | 30 | 0.222 | 0.167 | 0.190 |
| A | other | 39 | 125 | 104 | 0.238 | 0.273 | 0.254 |
| B | overall | 49 | 175 | 130 | 0.219 | 0.274 | 0.243 |
| B | abu_nuwas | 9 | 25 | 27 | 0.265 | 0.250 | 0.257 |
| B | other | 40 | 150 | 103 | 0.211 | 0.280 | 0.240 |
| C | overall | 27 | 84 | 152 | 0.243 | 0.151 | 0.186 |
| C | abu_nuwas | 3 | 12 | 33 | 0.200 | 0.083 | 0.118 |
| C | other | 24 | 72 | 119 | 0.250 | 0.168 | 0.201 |

### criterion: token (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 51 | 161 | 128 | 0.241 | 0.285 | 0.261 |
| A | overall | 46 | 145 | 133 | 0.241 | 0.257 | 0.249 |
| B | overall | 52 | 172 | 127 | 0.232 | 0.291 | 0.258 |
| C | overall | 30 | 81 | 149 | 0.270 | 0.168 | 0.207 |
(abu_nuwas/other splits in `results/phase4_e1_v2/analysis_report.json`.)

### Pairwise bootstrap 95% CI (F1_i − F1_j), per-poem diff signs
| Pair | verse | strict | token |
|---|---|---|---|
| Z−A | +0.008 [−0.046,+0.060] ns | +0.002 [−0.049,+0.040] ns | +0.012 [−0.031,+0.043] ns |
| Z−B | +0.036 [−0.006,+0.071] ns | +0.002 [−0.049,+0.040] ns | +0.003 [−0.050,+0.041] ns |
| Z−C | **+0.112 [+0.038,+0.194] SIG** | **+0.059 [+0.013,+0.111] SIG** | **+0.054 [+0.007,+0.108] SIG** |
| A−B | +0.028 [−0.012,+0.067] ns | +0.000 [−0.040,+0.030] ns | −0.009 [−0.052,+0.024] ns |
| A−C | **+0.104 [+0.028,+0.194] SIG** | **+0.057 [+0.013,+0.113] SIG** | +0.042 [−0.002,+0.101] ns |
| B−C | **+0.076 [+0.004,+0.160] SIG** | **+0.057 [+0.004,+0.123] SIG** | +0.051 [−0.006,+0.122] ns |

**Note the sign**: for GPT, Z beats C significantly on every criterion — zero-shot outperforms the
fewshot-C design, the opposite of what "examples help" would predict.

---

## 3. Gemini (served: gemini-3.6-flash)

### criterion: verse (PRIMARY — user decision, see CLAUDE.md rule 4 caveat above)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 47 | 65 | 80 | 0.420 | 0.370 | 0.393 |
| Z | abu_nuwas | 11 | 5 | 16 | 0.688 | 0.407 | 0.512 |
| Z | other | 36 | 60 | 64 | 0.375 | 0.360 | 0.367 |
| A | overall | 79 | 103 | 48 | 0.434 | 0.622 | 0.511 |
| A | abu_nuwas | 17 | 8 | 10 | 0.680 | 0.630 | 0.654 |
| A | other | 62 | 95 | 38 | 0.395 | 0.620 | 0.482 |
| B | overall | 78 | 101 | 49 | 0.436 | 0.614 | 0.510 |
| B | abu_nuwas | 16 | 10 | 11 | 0.615 | 0.593 | 0.604 |
| B | other | 62 | 91 | 38 | 0.405 | 0.620 | 0.490 |
| C | overall | 63 | 72 | 64 | 0.467 | 0.496 | 0.481 |
| C | abu_nuwas | 14 | 6 | 13 | 0.700 | 0.519 | 0.596 |
| C | other | 49 | 66 | 51 | 0.426 | 0.490 | 0.456 |

### criterion: strict (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 31 | 81 | 148 | 0.277 | 0.173 | 0.213 |
| Z | abu_nuwas | 6 | 10 | 30 | 0.375 | 0.167 | 0.231 |
| Z | other | 25 | 71 | 118 | 0.260 | 0.175 | 0.209 |
| A | overall | 47 | 135 | 132 | 0.258 | 0.263 | 0.260 |
| A | abu_nuwas | 7 | 18 | 29 | 0.280 | 0.194 | 0.230 |
| A | other | 40 | 117 | 103 | 0.255 | 0.280 | 0.267 |
| B | overall | 53 | 126 | 126 | 0.296 | 0.296 | 0.296 |
| B | abu_nuwas | 10 | 16 | 26 | 0.385 | 0.278 | 0.323 |
| B | other | 43 | 110 | 100 | 0.281 | 0.301 | 0.291 |
| C | overall | 38 | 97 | 141 | 0.281 | 0.212 | 0.242 |
| C | abu_nuwas | 6 | 14 | 30 | 0.300 | 0.167 | 0.214 |
| C | other | 32 | 83 | 111 | 0.278 | 0.224 | 0.248 |

### criterion: token (secondary)
| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 30 | 82 | 149 | 0.268 | 0.168 | 0.206 |
| A | overall | 52 | 130 | 127 | 0.286 | 0.291 | 0.288 |
| B | overall | 55 | 124 | 124 | 0.307 | 0.307 | 0.307 |
| C | overall | 47 | 88 | 132 | 0.348 | 0.263 | 0.299 |
(abu_nuwas/other splits in `results/phase4_e1_v2/analysis_report.json`.)

### Pairwise bootstrap 95% CI (F1_i − F1_j), per-poem diff signs
| Pair | verse | strict | token |
|---|---|---|---|
| Z−A | **−0.118 [−0.167,−0.073] SIG** | −0.047 [−0.108,+0.023] ns | **−0.082 [−0.128,−0.027] SIG** |
| Z−B | **−0.117 [−0.185,−0.052] SIG** | **−0.083 [−0.137,−0.025] SIG** | **−0.101 [−0.150,−0.050] SIG** |
| Z−C | **−0.088 [−0.148,−0.033] SIG** | −0.029 [−0.075,+0.020] ns | **−0.093 [−0.137,−0.050] SIG** |
| A−B | +0.002 [−0.033,+0.037] ns | −0.036 [−0.078,+0.000] ns | −0.019 [−0.062,+0.016] ns |
| A−C | +0.030 [−0.015,+0.078] ns | +0.018 [−0.031,+0.062] ns | −0.011 [−0.058,+0.028] ns |
| B−C | +0.029 [−0.019,+0.085] ns | **+0.054 [+0.009,+0.101] SIG** | +0.008 [−0.049,+0.065] ns |

---

## Question 1 — Do the few-shot examples help at all (Z vs A/B/C)? [answered on the PRIMARY verse metric]

**It depends on the model, and the picture is NOT uniform.** (Verse-criterion bootstrap 95% CIs,
F1(X) − F1(Z); secondary strict/token noted only where they disagree.)

- **Claude Sonnet 4.6**: Yes, clearly, for sets A and B — Z is significantly worse than both (verse:
  Z−A = **−0.199 SIG**, Z−B = **−0.170 SIG**). Z vs C is not significant (Z−C = −0.039 ns) — C behaves
  statistically like the zero-shot baseline, not like an improvement. (Secondary metrics agree on the
  direction here; strict's Z−A point estimate is smaller and not significant on its own — see §4.)
- **GPT-5.4-mini**: No. Z vs A and Z vs B are never significant (Z−A = +0.008 ns, Z−B = +0.036 ns).
  Worse: **Z is significantly BETTER than C** (Z−C = **+0.112 SIG**) — adding Set C's examples measurably
  *hurt* GPT relative to zero-shot. (Agrees with both secondary metrics.)
- **Gemini**: Yes, the strongest and most consistent signal of the three — Z is significantly worse than
  A, B, **and now C too** (Z−A = **−0.118 SIG**, Z−B = **−0.117 SIG**, Z−C = **−0.088 SIG**). Few-shot
  helps Gemini regardless of which example set is used. (Secondary strict shows Z−C as `ns` — one of
  §4's disagreements: on the primary metric, Gemini's few-shot advantage over Z is uniform across A/B/C;
  on strict alone it looked like C might be the exception.)

**Bottom line**: few-shot examples help Gemini unambiguously (now on all 3 sets, not just 2), help Claude
for 2 of 3 example sets, and do not help — or actively hurt — GPT-5.4-mini. A single blanket "yes,
few-shot helps" conclusion would be wrong for this subtype/prompt/model combination; the effect is
model-dependent.

## Question 2 — How much does the choice of examples matter (spread among A/B/C vs. CI width)? [verse-primary]

**A vs B is never significant for any model** on the primary verse metric (all 3 model A−B comparisons are
`ns`, point estimates all within ±0.03 F1) — A and B are statistically indistinguishable from each other
everywhere, same conclusion as the secondary metrics.

**C is where the spread shows up, but on verse it is now concentrated in 2 of 3 models, not the same 2 as
before**:
- Claude: A−C = **+0.161 SIG**, B−C = **+0.131 SIG** — C performs meaningfully worse than A/B for Claude.
- GPT: A−C = **+0.104 SIG**, B−C = **+0.076 SIG** — same pattern, C is the worst set.
- Gemini: A−C = +0.030 ns, B−C = +0.029 ns — **both now `ns` on the primary metric**. This is a
  disagreement worth flagging: the secondary strict metric showed Gemini's B−C as significant
  (+0.054 SIG), which had been read as "Gemini is *mostly* insensitive to example choice, with one
  exception." On verse (primary), Gemini shows **no** significant sensitivity to which example set it
  gets, at all — a cleaner, stronger version of "Gemini doesn't care which fewshot set it's given" than
  the secondary-metric read suggested.

**So example-choice sensitivity is real but concentrated**: specifically "Set C differs from A and B" for
Claude and GPT, and Gemini shows no significant choice-sensitivity on the primary metric at all.
`example_sets.json` confirms Set C's two example verses are both built on the same root ع-ق-ل (التعقيل)
applied to different objects — the leading candidate explanation this pilot was designed to test (see
`docs/phase4/E1_V2_SET_D.md` for the direct follow-up test of that hypothesis), and the data here is
consistent with (not proof of) that homogeneity hurting generalization for Claude and GPT. Gemini's
insensitivity to the same C-set homogeneity is itself a notable, model-dependent finding.

## Question 3 — How do the three models compare on the same sets? [verse-primary, strict/token secondary]

Primary verse F1, set by set (secondary strict/token in parentheses):

| Set | Claude (verse \| strict/token) | GPT (verse \| strict/token) | Gemini (verse \| strict/token) |
|---|---|---|---|
| Z | 0.377 (0.193/0.208) | **0.549** (0.246/0.261) | 0.393 (0.213/0.206) |
| A | **0.576** (0.257/0.281) | 0.541 (0.243/0.249) | 0.511 (0.260/**0.288**) |
| B | 0.547 (0.263/0.278) | 0.513 (0.243/0.258) | **0.510** (**0.296**/0.307) |
| C | 0.416 (0.212/0.240) | 0.437 (0.186/0.207) | 0.481 (0.242/0.299) |

- **Zero-shot (Z)**: GPT-5.4-mini is clearly the best out of the box on this subtype on the primary
  metric too — highest verse-F1 (0.549), and the cheapest model by far ($1.21 total openai spend vs.
  $7.09 anthropic). Claude and Gemini are both weaker than GPT at Z.
- **With any few-shot set (A/B/C)**: on verse, Claude takes the lead at A (0.576, the single highest
  number in the table) and stays ahead at B; Gemini's few-shot gains are real (confirmed SIG above) but
  land it below Claude and GPT's A/B numbers in absolute verse-F1, even though it leads on the secondary
  token-overlap metric for the same sets — a case where the primary and secondary metrics rank the models
  differently (see §4). GPT barely moves from its Z performance on verse and is the weakest of the three
  on A/B.
- **Cost-adjusted**: Claude's much higher cost ($7.09 of the $10.57 total) now looks better-justified on
  the primary metric for sets A/B than it did on strict/token, where Gemini led outright; cost-conscious
  choices should weigh which metric is actually decision-relevant for the downstream use case.

## Question 4 — Where do verse (primary) and strict/token (secondary) disagree?

Since the primary metric changed, every pairwise conclusion above was re-derived from verse CIs, not
carried over from the old strict/token-based write-up. The clearest disagreements:

| Comparison | verse (primary) | strict (secondary) | Note |
|---|---|---|---|
| Claude, Z vs A | **SIG** (−0.199) | ns (−0.064) | user's own example: verse alone affirms "A helps," strict alone does not |
| Claude, Z vs D (`E1_V2_SET_D.md`) | **SIG** (+0.185) | ns (+0.058) | same pattern as Z vs A |
| Claude, D vs C (`E1_V2_SET_D.md`) | **SIG** (+0.146) | ns (+0.039) | flips the Set-D hypothesis verdict for Claude — see that doc |
| Gemini, Z vs C | **SIG** (−0.088) | ns (−0.029) | verse shows a uniform few-shot advantage over Z for Gemini; strict suggested C might be an exception |
| Gemini, B vs C | ns (+0.029) | **SIG** (+0.054) | the one Q2 "exception" for Gemini disappears under the primary metric |
| GPT, D2 vs C (`E1_V2_SET_D.md`) | **SIG** (+0.066) | ns (+0.049) | strengthens D2's case for GPT specifically |

Every case above is a genuine criterion disagreement, not a rounding difference — each pair's
significance flips sign of "ns ↔ SIG" depending which metric is used. This is expected and explicitly
why CLAUDE.md rule 4 flags verse as a metric that can diverge from span-level correctness: a model can
correctly say "yes, this verse has the sub-element" (scored right on verse) while pointing at the wrong
span (scored wrong on strict/token), or vice versa in rarer cases. The user's choice to make verse
primary is a decision about which question matters more for this project's conclusions (does the model
detect presence vs. does it also localize correctly) — it is not a claim that verse is more "correct."

## Ensemble (majority vote)

Added 2026-10-16, no new API calls — full tables in `docs/phase4/E1_V2_ENSEMBLE.md`, numeric
report in `results/phase4_e1_v2/analysis_report_ensemble.json`
(`experiments/phase4_e1_v2/ensemble_v2.py`). **Definition (verse-primary)**: `ensemble_exists` =
True iff >=2 of the 3 models agree for that verse-unit (0 unparseable/error cells, so no tie-break
rule was ever exercised). Secondary strict/token use a declared, stated-limitation span-agreement
rule — see that doc's §0.

Verse-primary F1, ensemble vs. the 3 single models, every set:

| Set | Claude | GPT | Gemini | **Ensemble** | best single | avg of 3 |
|---|---|---|---|---|---|---|
| Z | 0.377 | 0.549 | 0.393 | **0.450** | GPT 0.549 | 0.440 |
| A | 0.576 | 0.541 | 0.511 | **0.568** | Claude 0.576 | 0.543 |
| B | 0.547 | 0.513 | 0.510 | **0.543** | Claude 0.547 | 0.523 |
| C | 0.416 | 0.437 | 0.481 | **0.475** | Gemini 0.481 | 0.444 |
| D | 0.562 | 0.533 | 0.509 | **0.577** | Claude 0.562 | 0.534 |
| D2 | 0.568 | 0.503 | 0.500 | **0.550** | Claude 0.568 | 0.524 |

**Plain answer**: majority voting **never significantly beats the best single model** on any set
or criterion (one case — Z — where it is significantly *worse* than GPT's zero-shot F1). On the
primary verse metric it **consistently beats the average of the 3 singles** (all 6 sets, point
estimate +0.010 to +0.043), often significantly against the two weaker models specifically. On
the secondary strict/token metrics the ensemble's conservative span-agreement rule makes it
**worse than the average of the 3 singles in every set**, and significantly worse than the best
single model in most sets (5 of 6 on both strict and token). **This agrees with and strengthens
`PROJECT_STATE.md` §3e's Phase 1 finding** that model ensembles give no improvement over the best
single model here, and are sometimes worse. Full agreement-bucket table (3/3, 2/3, 1/3, 0/3 vote
counts and each bucket's accuracy against ground truth) and every pairwise CI: `E1_V2_ENSEMBLE.md`.

## Opus 5.5 on set A

Claude Opus 5.5 (`claude-opus-5-5`) was run on **set A only** (not Z/B/C/D/D2, not added to the
ensemble) — $4.3157, 327/327 cells. Verse-primary F1 = **0.585** (vs. Sonnet 0.576, GPT 0.541,
Gemini 0.511, ensemble 0.568 — all also on set A): Opus numerically leads all four but the
difference is only statistically significant against Gemini; vs. Sonnet/GPT/ensemble it is `ns`.
On the secondary strict/token span-level metrics, Opus **significantly beats all four** by a wide
margin (strict F1=0.387 vs. 0.226-0.260; token F1=0.440 vs. 0.241-0.288) — the opposite of this
project's usual verse-vs-span disagreement pattern, because Opus's plain "exists" recall is lower
than Sonnet's while its span-level precision/correctness is higher. Set A is a few-shot set and
Opus has no Z/B/C/D/D2 results, so no gain-over-Z or other cross-set read exists for it. Full
tables, CIs, and the plain answer: `E1_V2_OPUS_A.md`.

## Caveats (apply to everything above)

- **No run-noise baseline exists** — 1 run per cell, per the frozen design. Every difference reported
  above, significant or not, is **indicative only** and could look different on a second run; this is
  exactly the failure mode CLAUDE.md rule 2 exists to guard against (a prior 8x apparent gain on one run
  halved on a second run for an unrelated element/model pair).
- **أبو نواس split (n=5 poems) is indicative only** in every table above — far too small to support a
  same-poet-vs-other-poet conclusion on its own.
- **Verse is the PRIMARY metric by explicit user decision (2026-10-14), not a project-rule change.**
  CLAUDE.md rule 4's standing warning still applies in full: plain exists/not-exists rewards a model that
  says "yes, present" regardless of whether it points at the right span, and can produce artifacts (the
  documented كناية/Periphrasis case is the precedent). §4 above lists where this actually changed a
  significance verdict versus the secondary strict/token metrics — read those rows as the concrete cost
  of the methodological choice, not as noise.
- **TEST is unaffected** — this entire pilot runs on a newly-scraped, separate corpus (`data/ali_poems/`),
  not Phase 1's frozen DEV/TEST poems; nothing here touches the frozen Phase 1 numbers.

---

*Full numeric report (all splits, all pairs, all criteria): `results/phase4_e1_v2/analysis_report.json`,
`results/phase4_e1_v2/analysis_report_verse.json` (verse-criterion bootstrap CIs, 2026-10-14 addition).
Raw manifest: `results/phase4_e1_v2/run_manifest.json` (5,886 records as of the Set D/D2 addition, 0
errors — this report's own Z/A/B/C numbers are unaffected by that later addition).*
