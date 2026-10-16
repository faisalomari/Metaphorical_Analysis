# E1 v2 — Claude Opus 5.5 on set A only

**Scope**: Claude Opus 5.5 (`claude-opus-5-5`), run on **set A only** (25-poem pool, all 327
verse-units, 1 run, temperature omitted per Opus 5.5's own request-shape requirements — see
`docs/phase4/SESSION_LOG.md`). Not run on Z/B/C/D/D2, and **not added to the majority-vote
ensemble**. All numbers below are read programmatically from
`results/phase4_e1_v2/analysis_report_opus_a.json`, produced by
`experiments/phase4_e1_v2/scoring_opus_a.py` (no API calls; reads `run_manifest.json` + `raw/*.txt`
only).

Verse-level is the **PRIMARY** metric throughout (the user's 2026-10-14 decision, applied
consistently with every other Phase 4 E1 v2 doc); strict/token-overlap span-matching are
secondary. CLAUDE.md rule 4 still flags plain verse-exists as a supplementary diagnostic prone to
rewarding "present" regardless of span correctness — see §3 below for where this matters here.

**Set A is one of the few-shot sets** (Z's zero-shot prompt + 2 extra example verses). Opus 5.5
has no Z, B, C, D, or D2 results, so **no gain-over-Z and no other cross-set comparison can be
computed for it** — this write-up is a same-set, cross-model comparison only.

## 0. Cost and completeness

- Model id: `claude-opus-5-5`. Pricing: $4.00/MTok input, $20.00/MTok output (verified against
  `claude.com/pricing` and `platform.claude.com/docs/en/models/overview`, 2026-10-16).
- 327/327 cells OK, 0 errors (after fixing a `temperature`-parameter 400 error on the first live
  attempt — Opus 5.5 rejects any non-default `temperature`/`top_p`/`top_k` — and resuming once the
  Anthropic account's credit balance was topped up; see `SESSION_LOG.md` for the full incident).
- **Real cost: $4.3157** (327 calls; real average 1,144.31 input / 431.03 output tokens/call) —
  above the $2.42 dry-run estimate (which used Claude Sonnet 4.6's real set-A token averages as a
  proxy): Opus 5.5's real input tokens ran ~1.29x higher (consistent with Anthropic's own
  migration-guide note that Opus 4.7+'s updated tokenizer can use up to ~1.35x more tokens than
  earlier models for the same text) and real output tokens ran ~2.24x higher (consistent with
  Opus 5.5's adaptive thinking being always on, unlike Sonnet 4.6's).

## 1. Opus 5.5 on set A — verse (PRIMARY), strict/token (secondary)

| Criterion | Split | TP | FP | FN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| verse | overall | 83 | 74 | 44 | 0.529 | 0.654 | **0.585** |
| verse | abu_nuwas | 19 | 7 | 8 | 0.731 | 0.704 | 0.717 |
| verse | other | 64 | 67 | 36 | 0.489 | 0.640 | 0.554 |
| strict | overall | 65 | 92 | 114 | 0.414 | 0.363 | 0.387 |
| strict | abu_nuwas | 13 | 13 | 23 | 0.500 | 0.361 | 0.419 |
| strict | other | 52 | 79 | 91 | 0.397 | 0.364 | 0.380 |
| token | overall | 74 | 83 | 105 | 0.471 | 0.413 | 0.440 |
| token | abu_nuwas | 16 | 10 | 20 | 0.615 | 0.444 | 0.516 |
| token | other | 58 | 73 | 85 | 0.443 | 0.406 | 0.423 |

## 2. Set-A comparison: Opus 5.5 vs Claude Sonnet 4.6 / GPT-5.4-mini / Gemini / ensemble

All CIs are bootstrap 95% over poems (seed=0, 2000 iterations, resample-with-replacement — same
method as every other Phase 4 E1 v2 comparison in this repo). Point = F1/P/R(Opus) − F1/P/R(other);
positive favors Opus.

### Verse (PRIMARY)

| vs. | Other's F1 | ΔF1 | 95% CI | Sig? | ΔP | Sig? | ΔR | Sig? |
|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | 0.576 | +0.008 | [-0.050, +0.066] | ns | +0.084 | **SIG** | -0.165 | **SIG** |
| GPT-5.4-mini | 0.541 | +0.044 | [-0.019, +0.103] | ns | +0.078 | **SIG** | -0.024 | ns |
| Gemini (3.6-flash) | 0.511 | +0.073 | [+0.025, +0.126] | **SIG** | +0.095 | **SIG** | +0.031 | ns |
| Majority-vote ensemble | 0.568 | +0.017 | [-0.038, +0.072] | ns | +0.074 | **SIG** | -0.102 | ns |

### Strict (secondary)

| vs. | Other's F1 | ΔF1 | 95% CI | Sig? |
|---|---|---|---|---|
| Claude Sonnet 4.6 | 0.257 | +0.130 | [+0.080, +0.183] | **SIG** |
| GPT-5.4-mini | 0.243 | +0.144 | [+0.073, +0.215] | **SIG** |
| Gemini (3.6-flash) | 0.260 | +0.127 | [+0.071, +0.195] | **SIG** |
| Majority-vote ensemble | 0.226 | +0.161 | [+0.098, +0.227] | **SIG** |

### Token-overlap (secondary)

| vs. | Other's F1 | ΔF1 | 95% CI | Sig? |
|---|---|---|---|---|
| Claude Sonnet 4.6 | 0.281 | +0.160 | [+0.101, +0.228] | **SIG** |
| GPT-5.4-mini | 0.249 | +0.192 | [+0.115, +0.271] | **SIG** |
| Gemini (3.6-flash) | 0.288 | +0.152 | [+0.086, +0.233] | **SIG** |
| Majority-vote ensemble | 0.241 | +0.200 | [+0.131, +0.279] | **SIG** |

Full pairwise precision/recall CIs for strict/token are in
`results/phase4_e1_v2/analysis_report_opus_a.json`; they are significant and positive across the
board on both secondary criteria (Opus's span-level correctness, not just plain existence calls,
is real here, not an artifact of the verse metric's known weakness).

## 3. Where verse (primary) and strict/token (secondary) disagree for Opus

This is the opposite of the project's usual pattern (CLAUDE.md rule 4 warns that verse-level
scoring tends to look *better* than span-level scoring because it rewards "present" regardless of
whether the model points at the right text). **Here Opus's advantage is far larger and uniformly
significant on the secondary span-level metrics, and mostly washes out to `ns` on the primary
verse metric** — against Sonnet and the ensemble specifically, verse is `ns` while strict/token
are both clearly `SIG`. The reason is visible in the raw counts: Opus's verse-level recall is
*lower* than Sonnet's (0.654 vs 0.819) because Opus says "no sub-element here" more often — but
when Opus does say "yes," it is far more often pointing at the actually-correct span (its
precision is higher everywhere, and its strict/token F1s are higher than every other model's by a
wide, significant margin). Sonnet's higher verse-recall inflates its verse F1 relative to its own
much weaker span-level accuracy (strict F1=0.257, well below Opus's 0.387) — exactly the exists-
regardless-of-span-correctness effect CLAUDE.md rule 4 describes, just showing up as a
*disadvantage* for the metric's usual beneficiary here, not Opus.

## 4. Caveats

- **Single run, no run-noise baseline** (CLAUDE.md rule 2) — this is one run per cell, not the
  project's usual 2-run minimum. Indicative only.
- **Set A only; no Z/B/C/D/D2 results for Opus** — no gain-over-Z, no example-sensitivity read for
  Opus specifically. This write-up cannot say whether Opus's few-shot examples (set A) help *it*
  at all, only how it does on the same set A every other model/ensemble was also scored on.
- Verse is the PRIMARY metric by the same standing user decision as every other Phase 4 E1 v2 doc;
  CLAUDE.md rule 4's own caveat about it (rewards "present" regardless of span correctness) is the
  documented reason §3 above looks the way it does.

## 5. Plain answer

**Does Opus 5.5 beat Sonnet/Gemini/GPT on set A?** On the **primary verse metric**: Opus
numerically leads all three single models and the ensemble (F1=0.585 vs 0.576/0.541/0.511/0.568),
but the difference is only statistically significant against **Gemini**; vs. Sonnet, GPT, and the
ensemble it is **not significant** (one run, no noise baseline). On the **secondary span-level
metrics (strict/token)**, Opus **significantly beats every other model and the ensemble**, by a
wide margin on both — its higher precision and correct-span accuracy are the most robust part of
this result, even though its plain "does it exist" recall is lower than Sonnet's.
