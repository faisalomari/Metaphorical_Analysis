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
- **verse** (supplementary diagnostic only): model's binary `exists` vs. whether the verse has any GT
  span at all, no span-text match. CLAUDE.md rule 4 explicitly warns this metric alone produces artifacts
  (the documented كناية/Periphrasis case) — reported here only alongside, never instead of, the two
  span-level metrics below.
- **strict** (primary): `appearance` must exactly span-match a GT span (`pilot_3models.span_matching`,
  reused unchanged).
- **token** (primary): token-overlap match on the same GT spans.

**أبو نواس split (n=5 poems) is indicative only** — too small to draw a reliable same-poet-vs-other-poet
conclusion on its own; included for completeness, not as a finding.

---

## 1. Claude Sonnet 4.6 (anthropic)

### criterion: verse (supplementary)
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

### criterion: strict (primary)
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

### criterion: token (primary)
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

### criterion: verse (supplementary)
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

### criterion: strict (primary)
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

### criterion: token (primary)
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

### criterion: verse (supplementary)
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

### criterion: strict (primary)
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

### criterion: token (primary)
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

## Question 1 — Do the few-shot examples help at all (Z vs A/B/C)?

**It depends on the model, and the picture is NOT uniform.**

- **Claude Sonnet 4.6**: Yes, clearly, for sets A and B. Z is significantly worse than A (verse, token)
  and significantly worse than B (verse, strict). Z vs C is never significant — C behaves statistically
  like the zero-shot baseline, not like an improvement.
- **GPT-5.4-mini**: No. Z vs A and Z vs B are never significant on any criterion. Worse: **Z is
  significantly BETTER than C on every single criterion** (verse, strict, token) — adding Set C's
  examples measurably *hurt* GPT relative to zero-shot.
- **Gemini**: Yes, the strongest and most consistent signal of the three. Z is significantly worse than
  A, B, *and* C on the verse and token criteria, and significantly worse than B on strict too. Few-shot
  helps Gemini regardless of which example set is used.

**Bottom line**: few-shot examples help Gemini unambiguously, help Claude for 2 of 3 example sets, and do
not help — or actively hurt — GPT-5.4-mini. A single blanket "yes, few-shot helps" conclusion would be
wrong for this subtype/prompt/model combination; the effect is model-dependent.

## Question 2 — How much does the choice of examples matter (spread among A/B/C vs. CI width)?

**A vs B is never significant for any model on any criterion** (all 9 model×criterion A−B comparisons are
`ns`, point estimates all within ±0.04 F1) — A and B are statistically indistinguishable from each other
everywhere.

**C is where the spread shows up, and only for 2 of the 3 models**:
- Claude: A−C and B−C are both significant (verse) and B−C significant (strict) — C performs
  meaningfully worse than A/B for Claude.
- GPT: A−C and B−C are both significant (verse, strict) — same pattern, C is the worst set.
- Gemini: A−C and B−C are **not** significant on verse/token; only B−C is significant on strict. Gemini
  is comparatively insensitive to which example set it gets.

**So example-choice sensitivity is real but concentrated**: it's not "any two example sets differ," it's
specifically "Set C differs from A and B" — and that gap is large enough to be a bigger factor than
whether few-shot is used at all, for 2 of the 3 models (Claude, GPT). `example_sets.json` confirms Set C's
two example verses are both built on the same root ع-ق-ل (التعقيل) applied to different objects, with no
other pattern represented — the leading candidate explanation this pilot was designed to test, and the
data here is consistent with (not proof of) that homogeneity hurting generalization for Claude and GPT.
Gemini's relative insensitivity to the same C-set homogeneity is itself a notable, model-dependent
finding, not something assumed in advance.

## Question 3 — How do the three models compare on the same sets?

Primary span-level F1 (strict / token), set by set:

| Set | Claude (strict/token) | GPT (strict/token) | Gemini (strict/token) |
|---|---|---|---|
| Z | 0.193 / 0.208 | **0.246** / **0.261** | 0.213 / 0.206 |
| A | 0.257 / 0.281 | 0.243 / 0.249 | 0.260 / **0.288** |
| B | 0.263 / 0.278 | 0.243 / 0.258 | **0.296** / **0.307** |
| C | 0.212 / 0.240 | 0.186 / 0.207 | **0.242** / **0.299** |

- **Zero-shot (Z)**: GPT-5.4-mini is clearly the best out of the box on this subtype — highest F1 on both
  criteria, and the cheapest model by far ($1.21 total openai spend vs. $7.09 anthropic). Claude and
  Gemini are both weaker than GPT at Z.
- **With any few-shot set (A/B/C)**: Gemini overtakes and stays ahead on token-overlap for every set, and
  ties-or-leads on strict for B/C. Claude catches up to roughly Gemini's level on A/B but falls back on C.
  GPT barely moves from its Z performance and is the weakest of the three on A/B/C.
- **Cost-adjusted**: Gemini's advantage with few-shot, combined with being ~3x cheaper than Claude and
  only slightly pricier than GPT, makes it the standout choice for this subtype if few-shot examples are
  used — Claude's much higher cost ($7.09 of the $10.57 total) is not matched by a corresponding
  performance edge over Gemini anywhere in this table.

## Caveats (apply to everything above)

- **No run-noise baseline exists** — 1 run per cell, per the frozen design. Every difference reported
  above, significant or not, is **indicative only** and could look different on a second run; this is
  exactly the failure mode CLAUDE.md rule 2 exists to guard against (a prior 8x apparent gain on one run
  halved on a second run for an unrelated element/model pair).
- **أبو نواس split (n=5 poems) is indicative only** in every table above — far too small to support a
  same-poet-vs-other-poet conclusion on its own.
- **Verse-level criterion is a supplementary diagnostic, not a primary metric** — CLAUDE.md rule 4's
  standing warning about plain exists/not-exists artifacts applies; strict and token-overlap are the
  metrics this report's conclusions are actually based on.
- **TEST is unaffected** — this entire pilot runs on a newly-scraped, separate corpus (`data/ali_poems/`),
  not Phase 1's frozen DEV/TEST poems; nothing here touches the frozen Phase 1 numbers.

---

*Full numeric report (all splits, all pairs, all criteria): `results/phase4_e1_v2/analysis_report.json`.
Raw manifest: `results/phase4_e1_v2/run_manifest.json` (3,924 records, 0 errors).*
