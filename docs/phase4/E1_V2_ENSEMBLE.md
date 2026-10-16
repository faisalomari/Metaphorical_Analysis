# E1 v2 — Majority-Vote Ensemble (Claude Sonnet 4.6 + GPT-5.4-mini + Gemini 3.6-flash)

**No new API calls.** Computed entirely from the existing 5,886-record
`results/phase4_e1_v2/run_manifest.json` (6 sets x 327 verse-units x 3 models, 0 errors) via
`experiments/phase4_e1_v2/ensemble_v2.py`, reusing `gt_v2.gt_spans_for_subtype`,
`parsing_v2.parse_verse_response`, `pilot_3models.span_matching.best_match`, and
`verse_analysis.bootstrap_pair` (resample-poems CI, same seed=0/n_iter=2000 method as every
other CI in this pilot) unchanged. Full numeric report:
`results/phase4_e1_v2/analysis_report_ensemble.json`.

## 0. Definitions (declared before any number below)

**Primary (verse-level)**: for each (set, poem, verse-unit),
`ensemble_exists = True` iff **at least 2 of the 3 models** (anthropic, openai, google) returned
`exists=True` for that cell. A model cell with an API error or unparseable JSON response would be
treated as a non-vote (False) for the 2-of-3 threshold — **this never actually happened**: 0 API
errors, 0 unparseable-JSON cells across all 5,886 model cells, confirmed directly in this task (no
assumption carried over from the prior completeness check).

**Secondary (strict/token span rule, declared with its stated limitation)**: among the models that
voted `exists=True` for a verse, each independently runs `best_match(appearance, gt_spans,
criterion)`. If **at least 2 of those per-model match indices agree on the same GT span**, that
span counts as 1 ensemble TP (the verse's remaining GT spans count as FN, same one-match-per-verse
convention `scoring_v2.score_poem` already uses for a single model). If `ensemble_exists` is True
but no GT span reaches 2 agreeing match-votes, the verse counts as 1 FP plus FN for every GT span.

> **Limitation, stated up front**: this rule under-counts ensemble TP whenever 2+ "yes" models each
> correctly identify a **different** real span in a multi-span verse — majority-of-span-IDENTITY is
> strictly harder to satisfy than majority-of-mere-existence. §2/§3 below show this limitation is not
> theoretical: the secondary-metric ensemble F1 is lower than every single model's F1 in most sets,
> a pattern the primary verse metric does not show. This is the one rule used throughout, not
> selected per cell.

**Errors/unparseable**: 0 API errors, 0 unparseable-JSON cells (checked, not assumed) — no
exclusion rule was needed.

---

## 1. Verse-level (PRIMARY) — ensemble TP/FP/FN/P/R/F1 per set

| Set | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| Z | overall | 56 | 66 | 71 | 0.459 | 0.441 | 0.450 |
| Z | abu_nuwas | 12 | 4 | 15 | 0.750 | 0.444 | 0.558 |
| Z | other | 44 | 62 | 56 | 0.415 | 0.440 | 0.427 |
| A | overall | 96 | 115 | 31 | 0.455 | 0.756 | 0.568 |
| A | abu_nuwas | 18 | 8 | 9 | 0.692 | 0.667 | 0.679 |
| A | other | 78 | 107 | 22 | 0.422 | 0.780 | 0.547 |
| B | overall | 94 | 125 | 33 | 0.429 | 0.740 | 0.543 |
| B | abu_nuwas | 19 | 14 | 8 | 0.576 | 0.704 | 0.633 |
| B | other | 75 | 111 | 25 | 0.403 | 0.750 | 0.524 |
| C | overall | 57 | 56 | 70 | 0.504 | 0.449 | 0.475 |
| C | abu_nuwas | 10 | 3 | 17 | 0.769 | 0.370 | 0.500 |
| C | other | 47 | 53 | 53 | 0.470 | 0.470 | 0.470 |
| D | overall | 97 | 112 | 30 | 0.464 | 0.764 | 0.577 |
| D | abu_nuwas | 18 | 7 | 9 | 0.720 | 0.667 | 0.692 |
| D | other | 79 | 105 | 21 | 0.429 | 0.790 | 0.556 |
| D2 | overall | 91 | 113 | 36 | 0.446 | 0.717 | 0.550 |
| D2 | abu_nuwas | 20 | 11 | 7 | 0.645 | 0.741 | 0.690 |
| D2 | other | 71 | 102 | 29 | 0.410 | 0.710 | 0.520 |

## 2. Secondary strict/token — ensemble TP/FP/FN/P/R/F1 per set (overall only; splits in the JSON)

| Set | strict TP/FP/FN | strict F1 | token TP/FP/FN | token F1 |
|---|---|---|---|---|
| Z | 27/95/152 | 0.179 | 28/94/151 | 0.186 |
| A | 44/167/135 | 0.226 | 47/164/132 | 0.241 |
| B | 44/175/135 | 0.221 | 48/171/131 | 0.241 |
| C | 25/88/154 | 0.171 | 30/83/149 | 0.205 |
| D | 45/164/134 | 0.232 | 52/157/127 | 0.268 |
| D2 | 45/159/134 | 0.235 | 48/156/131 | 0.251 |

## 3. Ensemble vs. each single model — F1/precision/recall diff, bootstrap 95% CI over poems

(`+` = ensemble higher. **SIG** = 95% CI excludes 0.)

### Verse (PRIMARY)
| Set | vs Claude | vs GPT | vs Gemini |
|---|---|---|---|
| Z | F1 **+0.073 [+0.005,+0.141] SIG**, R +0.134 SIG, P −0.028 ns | F1 **−0.099 [−0.171,−0.042] SIG**, R −0.291 SIG, P +0.020 ns | F1 **+0.057 [+0.001,+0.114] SIG**, R +0.071 SIG, P +0.039 ns |
| A | F1 −0.008 ns | F1 +0.027 ns | F1 **+0.057 [+0.011,+0.102] SIG**, R +0.134 SIG |
| B | F1 −0.003 ns | F1 +0.031 ns | F1 +0.034 ns, R **+0.126 SIG** |
| C | F1 **+0.059 [+0.005,+0.130] SIG**, R +0.071 SIG | F1 +0.038 ns | F1 −0.006 ns |
| D | F1 +0.015 ns | F1 **+0.045 [+0.012,+0.082] SIG**, P +0.057 SIG | F1 **+0.069 [+0.020,+0.127] SIG**, R +0.197 SIG |
| D2 | F1 −0.018 ns | F1 **+0.047 [+0.003,+0.088] SIG** | F1 **+0.050 [+0.009,+0.083] SIG**, R +0.126 SIG |

### Strict (secondary)
| Set | vs Claude | vs GPT | vs Gemini |
|---|---|---|---|
| Z | −0.014 ns | **−0.066 SIG** | −0.034 ns (P **−0.055 SIG**) |
| A | −0.031 ns (R **−0.050 SIG**) | −0.018 ns | −0.035 ns |
| B | −0.042 ns | −0.022 ns | **−0.075 SIG** (P **−0.095 SIG**) |
| C | −0.041 ns | −0.015 ns | **−0.071 SIG** (R **−0.073 SIG**) |
| D | −0.019 ns | −0.006 ns | **−0.055 SIG** (P **−0.092 SIG**) |
| D2 | **−0.062 SIG** (P **−0.054 SIG**, R **−0.073 SIG**) | −0.001 ns | −0.032 ns |

### Token-overlap (secondary)
| Set | vs Claude | vs GPT | vs Gemini |
|---|---|---|---|
| Z | −0.022 ns (P **−0.108 SIG**) | **−0.075 SIG** | −0.020 ns |
| A | −0.040 ns (R **−0.061 SIG**) | −0.008 ns | **−0.047 SIG** (P **−0.063 SIG**) |
| B | −0.037 ns | −0.017 ns | **−0.066 SIG** (P **−0.088 SIG**) |
| C | −0.035 ns | −0.001 ns | **−0.094 SIG** (P/R both **SIG**) |
| D | −0.030 ns | −0.003 ns | −0.042 ns (P **−0.085 SIG**) |
| D2 | **−0.072 SIG** (P/R both **SIG**) | −0.006 ns | −0.016 ns |

Full table (all 54 set x criterion x model cells): `results/phase4_e1_v2/analysis_report_ensemble.json`
→ `criteria.{verse,strict,token}.vs_single.{set}.{model}`.

## 4. Agreement — verse-unit vote-count buckets vs. plain ground truth (overall, all 25 poems)

Columns: `n` = verse-units in that vote bucket; `GT-positive rate` = fraction of that bucket's
verses that actually have a GT span; `accuracy vs GT` = agreement with ground truth **given the
bucket's own implied prediction** (3/3 and 2/3 predict positive → accuracy = GT-positive rate;
1/3 and 0/3 predict negative → accuracy = 1 − GT-positive rate).

| Set | 3/3 (n, rate, acc) | 2/3 (n, rate, acc) | 1/3 (n, rate, acc) | 0/3 (n, rate, acc) |
|---|---|---|---|---|
| Z | 48, 0.438, 0.438 | 74, 0.473, 0.473 | 112, 0.411, 0.589 | 93, 0.269, 0.731 |
| A | 131, 0.458, 0.458 | 80, 0.450, 0.450 | 54, 0.315, 0.685 | 62, 0.226, 0.774 |
| B | 125, 0.448, 0.448 | 94, 0.404, 0.404 | 57, 0.316, 0.684 | 51, 0.294, 0.706 |
| C | 42, 0.405, 0.405 | 71, 0.563, 0.563 | 82, 0.390, 0.610 | 132, 0.288, 0.712 |
| D | 125, 0.456, 0.456 | 84, 0.476, 0.476 | 58, 0.207, 0.793 | 60, 0.300, 0.700 |
| D2 | 121, 0.446, 0.446 | 83, 0.446, 0.446 | 58, 0.310, 0.690 | 65, 0.277, 0.723 |

Rows sum to 327 (the pool's full verse-unit count) in every set, as expected. Splits (abu_nuwas /
other) are in `results/phase4_e1_v2/analysis_report_ensemble.json` → `agreement.{set}.{abu_nuwas,other}`.

Two things worth flagging in this table, not just the F1 numbers above:
- **3/3 and 2/3 buckets are both "predicted positive," but their GT-positive rates diverge** for
  set C (0.405 vs 0.563) and Z (0.438 vs 0.473) — unanimous agreement is not uniformly more
  reliable than a bare 2-1 majority here, a genuinely counter-intuitive reading of "more agreement
  = more confidence."
- **The 1/3 and 0/3 "predicted negative" buckets are the most internally reliable** in every set
  (accuracy 0.59–0.79), i.e. when 2-of-3 models say "no," they are usually right — consistent with
  §3's finding that the ensemble's main value (where it beats the average) is suppressing isolated
  false positives, not surfacing true positives the best model missed.

## 5. Oracle context — best single model and average of the 3, per set

| Set | criterion | best single (model, F1) | avg of 3 singles F1 | ensemble F1 |
|---|---|---|---|---|
| Z | verse | GPT-5.4-mini, 0.549 | 0.440 | 0.450 |
| A | verse | Claude, 0.576 | 0.543 | 0.568 |
| B | verse | Claude, 0.547 | 0.523 | 0.543 |
| C | verse | Gemini, 0.481 | 0.444 | 0.475 |
| D | verse | Claude, 0.562 | 0.534 | 0.577 |
| D2 | verse | Claude, 0.568 | 0.524 | 0.550 |
| Z | strict | GPT-5.4-mini, 0.246 | 0.217 | 0.179 |
| A | strict | Gemini, 0.260 | 0.253 | 0.226 |
| B | strict | Gemini, 0.296 | 0.267 | 0.221 |
| C | strict | Gemini, 0.242 | 0.213 | 0.171 |
| D | strict | Gemini, 0.287 | 0.258 | 0.232 |
| D2 | strict | Claude, 0.297 | 0.267 | 0.235 |
| Z | token | GPT-5.4-mini, 0.261 | 0.225 | 0.186 |
| A | token | Gemini, 0.288 | 0.273 | 0.241 |
| B | token | Gemini, 0.307 | 0.281 | 0.241 |
| C | token | Gemini, 0.299 | 0.249 | 0.205 |
| D | token | Gemini, 0.310 | 0.293 | 0.268 |
| D2 | token | Claude, 0.323 | 0.282 | 0.251 |

## 6. Plain answer — does majority voting beat the best single model?

**No, not on any set or criterion.** The ensemble is never significantly better than that set's
best single model (§3's "vs [best model]" cell is `ns` in every row except Z-verse, where the
ensemble is **significantly worse** than GPT-5.4-mini's zero-shot F1). On the **primary verse
metric** the ensemble sits close to the best single model — sometimes marginally above its point
estimate (D: 0.577 vs. Claude's 0.562), sometimes marginally below (D2: 0.550 vs. Claude's 0.568)
— but never with a CI that excludes 0.

**Does it beat the average of the 3 single models?** On verse (primary), **yes, consistently** —
the ensemble's F1 point estimate exceeds the average of the 3 singles in all 6 sets (by +0.010 to
+0.043), and §3 shows this is often a *significant* improvement over the two weaker models
specifically (e.g., Z: ensemble beats Claude and Gemini significantly, loses to GPT significantly
— GPT's zero-shot F1 of 0.549 is simply far above the other two). On **strict/token (secondary)**,
the opposite: the ensemble's F1 is **below the average of the 3 singles in every single set**,
because the declared span-agreement rule (§0) is strictly harder to satisfy than plain existence
voting.

**Does this agree with Phase 1's ensemble finding?** `PROJECT_STATE.md` §3e found that
majority-vote-across-models gave no improvement over the best single model, and was sometimes
worse. **This result agrees on the primary metric** (no significant improvement over best,
one case of significantly worse) **and strengthens it on the secondary metrics**, where the
ensemble is significantly worse than the best single model in most sets (5 of 6 on strict, 5 of 6
on token). The overall picture across both Phase 1 (different task/elements) and this Phase 4
pilot (this subtype, this prompt, this model trio) is consistent: majority voting across these 3
models is not a free F1 win here, and can actively hurt when the per-model disagreement is about
*where* the figure is rather than *whether* it exists.

## Caveats

- **One run per (set, poem, verse, model) cell** — same as every other number in this pilot
  (CLAUDE.md rule 2's noise precedent applies to the ensemble exactly as it does to each single
  model; a second run could shift any individual CI, though the ensemble vote itself is a
  deterministic function of the 3 already-run cells, not a new source of run-to-run noise).
- **25 poems total, أبو نواس n=5** — the abu_nuwas split in §1/§4 is indicative only, same caveat
  as every other abu_nuwas/other breakdown in this pilot.
- **Voting is on the user-chosen verse criterion for the primary metric**; the secondary
  strict/token ensemble uses its own declared match-agreement rule (§0), which is not the only
  possible way to define an "ensemble span" — see the stated limitation there.
- **CLAUDE.md rule 4's standing caveat still applies to verse as a diagnostic**: it can reward
  `exists=True` regardless of span correctness. The disagreement between §3's verse-primary and
  strict/token-secondary verdicts here (ensemble competitive-or-better on verse, consistently worse
  on strict/token) is itself an instance of exactly that caveat, not a new phenomenon.
