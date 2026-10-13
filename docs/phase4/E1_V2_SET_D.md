# E1 v2 — Set D: Does Diversifying Set C's Examples Restore Performance?

**Hypothesis under test**: In `E1_V2_RESULTS.md`, Set C underperformed Sets A/B for Claude and
GPT (and was the set Gemini was comparatively least sensitive to among A/B/C). `example_sets.json`
shows Set C's two fewshot example verses are both built on the same root ع-ق-ل (التعقيل),
applied to different objects — the leading candidate explanation for that underperformance. This
report tests: **does replacing one of Set C's two ع-ق-ل examples with a different-root example
restore performance toward A/B's level?**

## 0. Design

- **Set D**: Example 1 = Set C's example (poem 21337, verse 1, root ع-ق-ل). Example 2 = Set A's
  second example (poem 16251, verse 5, different root) — a direct swap-in to probe root diversity.
- **Set D2 (control)**: Example 1 = same as D (Set C's example). Example 2 = Set B's second
  example (poem 17234, verse 4) — a different diversifying example, to check the result isn't
  specific to A's particular verse.
- Both sets built programmatically from `experiments/phase4_e1/config/example_sets.json`'s
  existing A/B/C example dicts (no text/annotation retyped) — see
  `experiments/phase4_e1_v2/prompt_builder.py`'s `_examples_for_set` and
  `e1v2_config.py`'s `SET_D_SOURCE`/`SET_D2_SOURCE`.
- Same prompt scaffold as A/B/C (`fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT`, Example 1 = the
  subtype's own definition example, Examples 2/3 = the two fewshot verses). Same eval pool
  (`config/eval_pool_25.json`, 327 verse-units, 25 poems: 5 أبو نواس + 20 other). Same 3 models
  (Claude Sonnet 4.6, GPT-5.4-mini, Gemini — requested `gemini-3.5-flash`, served/billed as
  `gemini-3.6-flash`, same as Z/A/B/C). **1 run per cell — no second run, no noise baseline**,
  per CLAUDE.md rule 2's standing caveat.
- **Verified before any API call**: regenerating Z/A/B/C's system messages still produces
  byte-identical output to the already-committed `config/prompt_preview_{Z,A,B,C}.txt`; D/D2
  differ from A/B/C only in the Example 2/3 lines.
- **Completeness**: 5,886/5,886 manifest records (3,924 existing Z/A/B/C + 1,962 new D/D2),
  0 errors; every one of the 18 (set × provider) combinations has exactly 327/327 cells with
  identical (poem, verse) coverage.
- **Actual cost for D+D2**: $5.4451 (cumulative total across all 6 sets: $16.0131 — within the
  user-approved $6 cap on top of the $10.5680 already spent on Z/A/B/C).

### Confound found during Step 1 (before any run)

Set A's second example (poem 16251, verse 5) has **one span with an empty `analysis` note**
(`"الدُّنْيا لَبيبٌ امتحن"`, `analysis: ""`) — unlike every other example across A/B/C, all of
which carry a non-empty note on every span. Because **D inherits this example verbatim**, D is
not a clean single-variable swap: relative to C, it changes both (a) the root-diversity variable
under test and (b) note-completeness. Note-completeness per set (examples with a non-empty note
on every span / total examples):

| Set | A | B | C | D | D2 |
|---|---|---|---|---|---|
| Fully-annotated examples | 1/2 | 2/2 | 2/2 | 1/2 | 2/2 |

**D2 is the clean root-diversity-only control** (both its examples are fully annotated, like
B/C) — D's result should be read alongside D2's, not in isolation.

## 1. Results by model

(Scoring: `experiments/phase4_e1_v2/scoring_v2.py`, reused unchanged — strict span-match and
token-overlap span-match are the primary criteria per CLAUDE.md rule 4; verse-level
exists-vs-ground-truth is a supplementary diagnostic only. Full report:
`results/phase4_e1_v2/analysis_report_D.json`.)

## Claude Sonnet 4.6 (anthropic)

### criterion: strict (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 25 | 55 | 154 | 0.312 | 0.140 | 0.193 |
| A | 53 | 181 | 126 | 0.226 | 0.296 | 0.257 |
| B | 52 | 165 | 127 | 0.240 | 0.291 | 0.263 |
| C | 30 | 74 | 149 | 0.288 | 0.168 | 0.212 |
| D | 48 | 156 | 131 | 0.235 | 0.268 | 0.251 |
| D2 | 58 | 153 | 121 | 0.275 | 0.324 | **0.297** |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | -0.0060 | [-0.0511, +0.0410] | ns | 10 / 8 / 7 |
| D-B | -0.0120 | [-0.0689, +0.0371] | ns | 8 / 10 / 7 |
| D-C | +0.0386 | [-0.0234, +0.1075] | ns | 14 / 7 / 4 |
| D-Z | +0.0576 | [-0.0070, +0.1177] | ns | 14 / 6 / 5 |
| D2-A | +0.0408 | [+0.0092, +0.0759] | **SIG** | 13 / 3 / 9 |
| D2-B | +0.0348 | [-0.0078, +0.0774] | ns | 10 / 8 / 7 |
| D2-C | +0.0854 | [+0.0325, +0.1479] | **SIG** | 15 / 6 / 4 |
| D2-Z | +0.1044 | [+0.0278, +0.1709] | **SIG** | 14 / 7 / 4 |
| D-D2 | -0.0468 | [-0.0844, -0.0098] | **SIG** | 3 / 13 / 9 |

### criterion: token (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 27 | 53 | 152 | 0.338 | 0.151 | 0.208 |
| A | 58 | 176 | 121 | 0.248 | 0.324 | 0.281 |
| B | 55 | 162 | 124 | 0.253 | 0.307 | 0.278 |
| C | 34 | 70 | 145 | 0.327 | 0.190 | 0.240 |
| D | 57 | 147 | 122 | 0.279 | 0.318 | 0.298 |
| D2 | 63 | 148 | 116 | 0.299 | 0.352 | **0.323** |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | +0.0168 | [-0.0259, +0.0671] | ns | 10 / 8 / 7 |
| D-B | +0.0199 | [-0.0366, +0.0715] | ns | 9 / 9 / 7 |
| D-C | +0.0574 | [-0.0134, +0.1382] | ns | 14 / 7 / 4 |
| D-Z | +0.0892 | [+0.0208, +0.1564] | **SIG** | 15 / 6 / 4 |
| D2-A | +0.0422 | [+0.0105, +0.0806] | **SIG** | 13 / 3 / 9 |
| D2-B | +0.0453 | [+0.0012, +0.0903] | **SIG** | 10 / 7 / 8 |
| D2-C | +0.0828 | [+0.0156, +0.1602] | **SIG** | 14 / 7 / 4 |
| D2-Z | +0.1146 | [+0.0408, +0.1846] | **SIG** | 14 / 7 / 4 |
| D-D2 | -0.0254 | [-0.0568, +0.0053] | ns | 5 / 12 / 8 |

### criterion: verse (supplementary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 39 | 41 | 88 | 0.487 | 0.307 | 0.377 |
| A | 104 | 130 | 23 | 0.444 | 0.819 | 0.576 |
| B | 94 | 123 | 33 | 0.433 | 0.740 | 0.547 |
| C | 48 | 56 | 79 | 0.462 | 0.378 | 0.416 |
| D | 93 | 111 | 34 | 0.456 | 0.732 | 0.562 |
| D2 | 96 | 115 | 31 | 0.455 | 0.756 | 0.568 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | -0.0142 | [-0.0486, +0.0178] | ns | 7 / 10 / 8 |
| D-B | +0.0154 | [-0.0286, +0.0621] | ns | 9 / 10 / 6 |
| D-C | +0.1463 | [+0.0829, +0.2235] | **SIG** | 17 / 4 / 4 |
| D-Z | +0.1851 | [+0.1015, +0.2747] | **SIG** | 17 / 5 / 3 |
| D2-A | -0.0081 | [-0.0370, +0.0161] | ns | 7 / 9 / 9 |
| D2-B | +0.0215 | [-0.0104, +0.0549] | ns | 11 / 5 / 9 |
| D2-C | +0.1525 | [+0.0813, +0.2306] | **SIG** | 18 / 4 / 3 |
| D2-Z | +0.1912 | [+0.0923, +0.2893] | **SIG** | 16 / 6 / 3 |
| D-D2 | -0.0061 | [-0.0358, +0.0259] | ns | 5 / 9 / 11 |

## GPT-5.4-mini (openai)

### criterion: strict (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 48 | 164 | 131 | 0.226 | 0.268 | 0.246 |
| A | 45 | 146 | 134 | 0.236 | 0.251 | 0.243 |
| B | 49 | 175 | 130 | 0.219 | 0.274 | 0.243 |
| C | 27 | 84 | 152 | 0.243 | 0.151 | 0.186 |
| D | 50 | 191 | 129 | 0.207 | 0.279 | 0.238 |
| D2 | 45 | 158 | 134 | 0.222 | 0.251 | 0.236 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | -0.0051 | [-0.0365, +0.0233] | ns | 6 / 13 / 6 |
| D-B | -0.0051 | [-0.0487, +0.0332] | ns | 9 / 12 / 4 |
| D-C | +0.0519 | [+0.0135, +0.1011] | **SIG** | 14 / 7 / 4 |
| D-Z | -0.0074 | [-0.0485, +0.0331] | ns | 8 / 13 / 4 |
| D2-A | -0.0076 | [-0.0441, +0.0349] | ns | 8 / 11 / 6 |
| D2-B | -0.0076 | [-0.0419, +0.0246] | ns | 10 / 12 / 3 |
| D2-C | +0.0494 | [-0.0016, +0.1150] | ns | 13 / 6 / 6 |
| D2-Z | -0.0099 | [-0.0572, +0.0498] | ns | 8 / 9 / 8 |
| D-D2 | +0.0025 | [-0.0399, +0.0368] | ns | 8 / 13 / 4 |

### criterion: token (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 51 | 161 | 128 | 0.241 | 0.285 | 0.261 |
| A | 46 | 145 | 133 | 0.241 | 0.257 | 0.249 |
| B | 52 | 172 | 127 | 0.232 | 0.291 | 0.258 |
| C | 30 | 81 | 149 | 0.270 | 0.168 | 0.207 |
| D | 57 | 184 | 122 | 0.237 | 0.318 | **0.271** |
| D2 | 49 | 154 | 130 | 0.241 | 0.274 | 0.257 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | +0.0228 | [-0.0056, +0.0463] | ns | 9 / 10 / 6 |
| D-B | +0.0134 | [-0.0348, +0.0542] | ns | 9 / 12 / 4 |
| D-C | +0.0645 | [+0.0231, +0.1104] | **SIG** | 15 / 6 / 4 |
| D-Z | +0.0106 | [-0.0266, +0.0489] | ns | 9 / 12 / 4 |
| D2-A | +0.0079 | [-0.0274, +0.0484] | ns | 9 / 9 / 7 |
| D2-B | -0.0015 | [-0.0389, +0.0342] | ns | 12 / 10 / 3 |
| D2-C | +0.0496 | [-0.0033, +0.1177] | ns | 13 / 5 / 7 |
| D2-Z | -0.0043 | [-0.0509, +0.0585] | ns | 8 / 9 / 8 |
| D-D2 | +0.0149 | [-0.0355, +0.0543] | ns | 9 / 12 / 4 |

### criterion: verse (supplementary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 93 | 119 | 34 | 0.439 | 0.732 | 0.549 |
| A | 86 | 105 | 41 | 0.450 | 0.677 | 0.541 |
| B | 90 | 134 | 37 | 0.402 | 0.709 | 0.513 |
| C | 52 | 59 | 75 | 0.468 | 0.409 | 0.437 |
| D | 98 | 143 | 29 | 0.407 | 0.772 | 0.533 |
| D2 | 83 | 120 | 44 | 0.409 | 0.654 | 0.503 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | -0.0083 | [-0.0553, +0.0337] | ns | 8 / 11 / 6 |
| D-B | +0.0198 | [-0.0310, +0.0641] | ns | 10 / 10 / 5 |
| D-C | +0.0956 | [+0.0297, +0.1657] | **SIG** | 15 / 6 / 4 |
| D-Z | -0.0161 | [-0.0536, +0.0228] | ns | 7 / 14 / 4 |
| D2-A | -0.0379 | [-0.0813, -0.0019] | **SIG** | 5 / 12 / 8 |
| D2-B | -0.0098 | [-0.0569, +0.0318] | ns | 11 / 12 / 2 |
| D2-C | +0.0661 | [+0.0093, +0.1347] | **SIG** | 14 / 6 / 5 |
| D2-Z | -0.0456 | [-0.1023, +0.0030] | ns | 6 / 9 / 10 |
| D-D2 | +0.0296 | [-0.0140, +0.0698] | ns | 10 / 11 / 4 |

## Gemini (served: gemini-3.6-flash)

### criterion: strict (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 31 | 81 | 148 | 0.277 | 0.173 | 0.213 |
| A | 47 | 135 | 132 | 0.258 | 0.263 | 0.260 |
| B | 53 | 126 | 126 | 0.296 | 0.296 | **0.296** |
| C | 38 | 97 | 141 | 0.281 | 0.212 | 0.242 |
| D | 48 | 108 | 131 | 0.308 | 0.268 | 0.287 |
| D2 | 47 | 126 | 132 | 0.272 | 0.263 | 0.267 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | +0.0262 | [-0.0089, +0.0712] | ns | 12 / 6 / 7 |
| D-B | -0.0095 | [-0.0451, +0.0256] | ns | 9 / 7 / 9 |
| D-C | +0.0445 | [+0.0162, +0.0787] | **SIG** | 10 / 2 / 13 |
| D-Z | +0.0735 | [+0.0170, +0.1262] | **SIG** | 12 / 5 / 8 |
| D2-A | +0.0067 | [-0.0371, +0.0619] | ns | 9 / 6 / 10 |
| D2-B | -0.0290 | [-0.0719, +0.0188] | ns | 7 / 10 / 8 |
| D2-C | +0.0250 | [-0.0205, +0.0741] | ns | 12 / 7 / 6 |
| D2-Z | +0.0540 | [+0.0022, +0.1006] | **SIG** | 14 / 4 / 7 |
| D-D2 | +0.0195 | [-0.0317, +0.0693] | ns | 9 / 9 / 7 |

### criterion: token (primary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 30 | 82 | 149 | 0.268 | 0.168 | 0.206 |
| A | 52 | 130 | 127 | 0.286 | 0.291 | 0.288 |
| B | 55 | 124 | 124 | 0.307 | 0.307 | 0.307 |
| C | 47 | 88 | 132 | 0.348 | 0.263 | 0.299 |
| D | 52 | 104 | 127 | 0.333 | 0.291 | **0.310** |
| D2 | 47 | 126 | 132 | 0.272 | 0.263 | 0.267 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | +0.0224 | [-0.0174, +0.0679] | ns | 12 / 7 / 6 |
| D-B | +0.0032 | [-0.0423, +0.0494] | ns | 9 / 7 / 9 |
| D-C | +0.0111 | [-0.0258, +0.0431] | ns | 8 / 7 / 10 |
| D-Z | +0.1043 | [+0.0526, +0.1528] | **SIG** | 13 / 4 / 8 |
| D2-A | -0.0210 | [-0.0597, +0.0220] | ns | 7 / 9 / 9 |
| D2-B | -0.0402 | [-0.0822, +0.0044] | ns | 5 / 12 / 8 |
| D2-C | -0.0323 | [-0.0849, +0.0169] | ns | 7 / 11 / 7 |
| D2-Z | +0.0609 | [+0.0134, +0.1022] | **SIG** | 14 / 3 / 8 |
| D-D2 | +0.0434 | [-0.0131, +0.0991] | ns | 11 / 7 / 7 |

### criterion: verse (supplementary)

| Set | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|
| Z | 47 | 65 | 80 | 0.420 | 0.370 | 0.393 |
| A | 79 | 103 | 48 | 0.434 | 0.622 | 0.511 |
| B | 78 | 101 | 49 | 0.436 | 0.614 | 0.510 |
| C | 63 | 72 | 64 | 0.467 | 0.496 | 0.481 |
| D | 72 | 84 | 55 | 0.462 | 0.567 | 0.509 |
| D2 | 75 | 98 | 52 | 0.434 | 0.591 | 0.500 |

Bootstrap 95% CI (F1_probe − F1_baseline), per-poem diff signs:

| Pair | point | CI95 | sig | per-poem (probe>base / base>probe / tied) |
|---|---|---|---|---|
| D-A | -0.0025 | [-0.0565, +0.0350] | ns | 9 / 9 / 7 |
| D-B | -0.0010 | [-0.0519, +0.0338] | ns | 11 / 9 / 5 |
| D-C | +0.0279 | [-0.0183, +0.0653] | ns | 8 / 5 / 12 |
| D-Z | +0.1155 | [+0.0531, +0.1746] | **SIG** | 14 / 3 / 8 |
| D2-A | -0.0113 | [-0.0565, +0.0360] | ns | 7 / 10 / 8 |
| D2-B | -0.0098 | [-0.0630, +0.0475] | ns | 8 / 11 / 6 |
| D2-C | +0.0191 | [-0.0339, +0.0742] | ns | 11 / 7 / 7 |
| D2-Z | +0.1067 | [+0.0483, +0.1676] | **SIG** | 17 / 4 / 4 |
| D-D2 | +0.0088 | [-0.0616, +0.0635] | ns | 9 / 10 / 6 |

## 2. Gain over Z (summary)

| Model | D vs Z (strict) | D vs Z (token) | D2 vs Z (strict) | D2 vs Z (token) |
|---|---|---|---|---|
| Claude | +0.058 ns | **+0.089 SIG** | **+0.104 SIG** | **+0.115 SIG** |
| GPT | -0.007 ns | +0.011 ns | -0.010 ns | -0.004 ns |
| Gemini | **+0.074 SIG** | **+0.104 SIG** | **+0.054 SIG** | **+0.061 SIG** |

Both D and D2 beat zero-shot for Claude and Gemini on at least one criterion each (D2 on both,
for Claude); neither beats zero-shot for GPT — consistent with `E1_V2_RESULTS.md`'s Q1 finding
that few-shot does not help GPT on this subtype, regardless of which examples are used.

## 3. Does D restore performance toward A/B? (the hypothesis's direct test)

**D vs C** (the most direct test — same example-1, swapped example-2):

| Model | strict | token |
|---|---|---|
| Claude | +0.039 ns | +0.057 ns |
| GPT | **+0.052 SIG** | **+0.065 SIG** |
| Gemini | **+0.045 SIG** | +0.011 ns |

D beats C significantly in 3 of 6 model×criterion cells (GPT both, Gemini strict), and is
statistically indistinguishable from C in the other 3 (Claude both, Gemini token). **No model
shows D significantly *worse* than C** — the swap never backfires.

**D vs A and D vs B** (does D reach the A/B level?): **every single one of the 12
model×criterion×baseline comparisons (D-A and D-B, strict and token, 3 models) is `ns`** — D is
never statistically distinguishable from A or B, for any model, on either primary criterion.
This is the strongest piece of evidence for the hypothesis: diversifying Set C's examples
produces a set that behaves statistically like A/B, not like C's low-diversity pair.

**But this is a double-edged read**: D is *also* statistically indistinguishable from C in half
the cells (3/6 on D-C above). A-B themselves were already shown in `E1_V2_RESULTS.md` to be
close to C in absolute terms for some model/criterion pairs, and bootstrap CIs over 25 poems are
wide — "D is not significantly different from A/B" and "D is not significantly different from
C" are **not contradictory outcomes**; with this much sampling noise, three different example
sets landing in overlapping CIs is the expected picture, not necessarily evidence that D closed
a real gap.

**D2 (the confound-free control)** tells a different, model-dependent story: for Claude, D2 is
significantly *better* than A and C and is the single best-performing set among all 6 (F1=0.297
strict, 0.323 token) — a stronger result than D's own numbers, suggesting D's inherited
unannotated-span confound may be *suppressing* Claude's D performance specifically (the one
significant D-vs-D2 gap, strict, D2 > D). For GPT and Gemini, D2 sits statistically flat against
A/B/C/Z on both criteria (all `ns`) — diversifying did not clearly move the needle either
direction for those two models when the confound is removed.

## 4. Plain answer

**Partial, model-dependent support — not a clean "yes."**

- For **GPT-5.4-mini**, D is a real, significant improvement over C (both criteria) — closest
  to a clean confirmation of the hypothesis, though D never clears Z either, so the ceiling it's
  reaching toward is modest.
- For **Gemini**, D beats C on strict but not token, and beats Z on both — some support, but
  weaker and criterion-dependent; D2 (the cleaner control) only clears Z, not C/A/B, undercutting
  "diversity specifically helps" versus "any few-shot helps a bit."
- For **Claude**, D itself never significantly beats C — no support from D's own numbers. But D2
  (the clean control) is the best-performing set of all 6, significantly ahead of A, C, and Z —
  the opposite pattern from D, and the clearest sign that root-diversity-style editing *can* help
  Claude, just not with D's specific borrowed (partially unannotated) example.

**Taken together**: diversifying away from Set C's root-homogeneity never hurts, and helps on at
least one criterion for 2 of 3 models (GPT, Gemini) via D, and helps Claude strongly via D2. It
does not uniformly "restore" performance to A/B's exact level in a statistically confirmable way
for any model — D/D2 land in the same broad, overlapping-CI neighborhood as A/B/C, which is
consistent with the hypothesis without being proof of it.

## 5. What this does NOT prove (caveats)

- **1 run per cell, no noise baseline** (CLAUDE.md rule 2) — every point estimate and CI above
  reflects a single run; a second run could shift set rankings, exactly as the documented
  Kenning/Periphrasis 8×→½ precedent shows for this kind of design.
- **Example-2 note confound**: Set D's example 2 (borrowed from A) has an empty analysis note on
  one of its spans — the only example among A/B/C/D that is partially unannotated. D's result is
  therefore a joint test of "different root" AND "possibly weaker annotation," not an isolated
  root-diversity manipulation. D2 (fully annotated on both examples) is the cleaner test, and its
  results sometimes diverge from D's (most notably for Claude).
- **25 poems, 327 verse-units** — the same small pool as Z/A/B/C; bootstrap CIs are correspondingly
  wide, and several "ns" results above likely reflect limited power, not a confirmed null effect.
- **n=2 examples per set** — this experiment only tested one specific swap (C's example 1 + one
  other example). It does not establish that "any diverse 2nd example" works, or that 3+ diverse
  examples would do better; it tests exactly the two swaps defined in §0, nothing more general.
- **TEST is unaffected** — this entire pilot runs on `data/ali_poems/`, a separate corpus from
  Phase 1's frozen DEV/TEST split; nothing here touches any frozen Phase 1 number.

---

*Full numeric report (all splits not shown above, all pairs, all criteria):
`results/phase4_e1_v2/analysis_report_D.json`. Raw manifest (now includes D/D2):
`results/phase4_e1_v2/run_manifest.json` (5,886 records, 0 errors).*
