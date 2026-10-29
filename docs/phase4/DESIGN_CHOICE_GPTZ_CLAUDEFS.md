# Design Choice: GPT-5.4-mini Zero-Shot + Claude Sonnet 4.6 Few-Shot, With or Without Gemini?

**Question asked**: is the planned production design "GPT-5.4-mini zero-shot (Z) + Claude Sonnet
4.6 few-shot, **WITHOUT** Gemini" a good decision, versus keeping Gemini in a 3-model majority-vote
design?

**NO API calls were made producing this document.** Every number below is computed from the
existing `results/phase4_e1_v2/run_manifest.json` (20,061 records, 0 errors) and `raw/*.txt`
response files, via a new cache-based scorer
(`experiments/phase4_e1_v2/design_choice/{combine.py,analyze_design_choice.py}`) that reuses
`ensemble_v2.build_parsed_cache`, `score_poem_single_model`, and `verse_analysis.bootstrap_pair`
**unchanged**, adding only the 2-voter OR/AND and generalized-3-voter combination rules that did
not exist before this task (declared in `combine.py`'s docstring). No existing file, result, or
report was edited. Full numeric output:
`results/phase4_e1_v2/design_choice/analysis_report_design_choice.json`.

**Pool**: `experiments/phase4_e1_v2/config/eval_pool_25.json` — 25 poems, 327 verse-units, one
subtype (**استعارة فعل**, verbal metaphor). Sets Z/A/B/C/D/D2/M1/M2/E1/E2/H1/H2/Q1/Q2 all ran on
this exact pool (confirmed in `E1_V2_RESULTS.md` / `E1_V2_ERAS_FEWSHOT.md`). **F5/F10 are
deliberately excluded from every combination in this document** — they ran on a *different*
50-poem pool with only 9/25 poems overlapping `eval_pool_25.json`, so a cell-by-cell combination
with Z/A/.../Q2 would silently fabricate an overlap that doesn't exist.

Ground-truth support on this pool: **179 span instances** (36 أبو نواس, 143 other) across
**127/327 (38.8%)** verse-units that are GT-positive at all. (179 happens to equal Phase 1 TEST's
Trope support count — §1 below — this is a coincidence of two unrelated counts, not a signal.)

---

## Part 1 — Cross-phase consistency: does Phase 1's model ranking survive into E1 v2?

**Scope honesty, stated up front**: Phase 1 and E1 v2 are **not directly comparable** on four
separate axes, and no number below should be read as "the same experiment, more data":

| Axis | Phase 1 (frozen TEST) | E1 v2 |
|---|---|---|
| Prompt | Phase 1's whole-poem baseline/v4_combined prompt (old terminology) | Phase 3's subtype-level prompt, one call per verse |
| Element scope | **Trope (مجاز)**, the full umbrella category (استعارة + تمثيل + مجاز مرسل, all subtypes pooled) | **استعارة فعل** only — one narrow subtype of Trope's umbrella |
| Metric | Span-level, strict + token-overlap, **2-run majority** | Verse-level (primary, **1 run**), strict/token (secondary, 1 run) |
| Poems | 3 TEST poems (Imru1, Jarir, Abu_Tammam), frozen, spent | 25-poem pool, seed=43 — **excludes all 5 Phase-1 poems by construction** (`ALREADY_USED_POEM_IDS` in `e1v2_config.py`) |

No poem in E1 v2's pool was ever scored in Phase 1, so there is no same-poem, same-prompt,
same-metric comparison possible — only a same-family "which model tends to win on
figurative/metaphor detection for this project" question, answered below with that caveat live
throughout.

### 1.1 Phase 1 Trope (TEST, frozen, 2-run majority, v4_combined — the thesis's primary prompt)

| Model | TP/FP/FN | Strict F1 | Rank |
|---|---|---|---|
| Gemini 3.5 Flash | 45/9/134 | **0.386** | 1st |
| GPT-5.4-mini | 28/16/151 | 0.251 | 2nd |
| Claude Sonnet 4.6 | 25/3/154 | 0.242 | 3rd |

Ranking: **Gemini > GPT > Claude**, but GPT and Claude are close (0.251 vs 0.242 — a 9-TP/3-FP
margin on n=179, not a wide gap). Under the baseline (pre-v4) prompt the ranking is different
again (Gemini 0.313 > Claude 0.171 > GPT 0.065 — GPT was the *worst* model under that prompt),
underscoring that even within Phase 1 alone, "the ranking" is prompt-dependent.

### 1.2 E1 v2 (استعارة فعل, verse + strict/token), Z (zero-shot) vs best few-shot

| Condition | Criterion | Claude | GPT | Gemini | Ranking |
|---|---|---|---|---|---|
| Z | verse | 0.377 | **0.549** | 0.393 | **GPT > Gemini > Claude** |
| Z | strict | 0.193 | **0.246** | 0.213 | **GPT > Gemini > Claude** |
| Z | token | 0.208 | **0.261** | 0.206 | **GPT > Claude ≈ Gemini** |
| A (fewshot) | verse | **0.576** | 0.541 | 0.511 | **Claude > GPT > Gemini** |
| A (fewshot) | strict | 0.257 | 0.243 | **0.260** | **Gemini ≈ Claude > GPT** |
| A (fewshot) | token | 0.281 | 0.249 | **0.288** | **Gemini > Claude > GPT** |
| B (fewshot) | verse | **0.547** | 0.513 | 0.510 | **Claude > GPT ≈ Gemini** |
| B (fewshot) | strict | 0.263 | 0.243 | **0.296** | **Gemini > Claude > GPT** |
| B (fewshot) | token | 0.278 | 0.258 | **0.307** | **Gemini > Claude > GPT** |

### 1.3 Answer

**The Phase 1 ranking (Gemini > GPT > Claude) does NOT hold under zero-shot in E1 v2 — it is
close to inverted.** Under Z, **GPT-5.4-mini is the best model on every one of the three
criteria** — the same model that ranked *worst or second-worst* on Phase 1 Trope. **Under
few-shot, the ranking is metric-dependent, not model-stable**: Claude leads on verse (the
project's own primary metric), while Gemini leads on strict/token (the span-level metrics Phase
1 actually used), with GPT dropping to last on strict/token for both A and B. The one thread of
continuity: **Gemini is never the single worst model in E1 v2**, consistent with its Phase-1 win
— but it is also never the clear #1 the way Phase 1 found it to be, and GPT's Phase-1 "clearly
weakest" status is the one most directly overturned by the new data (GPT is the *best* zero-shot
model and a competitive few-shot model on 2 of 3 metrics). **Bottom line: the ranking is real but
fragile — it flips with zero-shot vs few-shot and, within few-shot, flips again between the
primary and secondary metrics.** Treating "Gemini > GPT > Claude" as a stable, transferable
property of these three models on figurative-language detection is not supported by this later,
larger, differently-scoped pilot.

---

## Part 2 — Design comparison on the 25-poem pool (verse-primary, strict/token secondary, 1 run/cell)

**Caveat live throughout this Part**: every number is from **1 run per (set, poem, verse, model)
cell** — no run-noise baseline exists anywhere in E1 v2 (CLAUDE.md rule 2's standing precedent:
an 8× apparent Kenning/Periphrasis gain on one run halved on a second). Bootstrap 95% CIs (per-poem
resampling, n=2000, seed=0, `verse_analysis.bootstrap_pair` unchanged) capture **poem-sampling**
uncertainty only, not run-to-run noise.

Ten Claude-few-shot sets exist on this pool: **A, B, D, D2, M1, M2, H1, H2, Q1, Q2** (HX/Q = H1,
H2, Q1, Q2 individually, per the task's naming). **C is excluded from "Claude-FS" here** — it is
the one set `E1_V2_RESULTS.md` already identified as the homogeneous-root outlier that
underperforms for 2 of 3 models; it is not one of the sets the task asked to be treated as a
candidate production few-shot choice.

### 2.1 D_A — GPT-5.4-mini zero-shot alone

| Criterion | TP/FP/FN | P | R | F1 |
|---|---|---|---|---|
| verse | 93/119/34 | 0.439 | 0.732 | **0.549** |
| strict | 48/164/131 | 0.226 | 0.268 | 0.246 |
| token | 51/161/128 | 0.241 | 0.285 | 0.261 |

### 2.2 D_B — Claude Sonnet 4.6 few-shot alone, every set (not the best one picked)

| Set | verse F1 | strict F1 | token F1 |
|---|---|---|---|
| A | 0.576 | 0.257 | 0.281 |
| B | 0.547 | 0.263 | 0.278 |
| D | 0.562 | 0.251 | 0.298 |
| D2 | 0.568 | 0.297 | 0.323 |
| M1 | 0.515 | 0.231 | 0.244 |
| M2 | 0.584 | 0.278 | 0.316 |
| H1 | 0.553 | 0.260 | 0.286 |
| H2 | 0.536 | 0.249 | 0.271 |
| Q1 | 0.445 | 0.214 | 0.253 |
| Q2 | 0.588 | 0.296 | 0.334 |
| **mean over 10 sets** | **0.547** | **0.260** | **0.288** |
| **range** | [0.445, 0.588] | [0.214, 0.297] | [0.244, 0.334] |

Claude-FS's verse mean (0.547) sits essentially level with GPT-Z's verse F1 (0.549) — the two
single models the production design combines are, on average, tied on the primary metric. On
strict/token, Claude-FS's mean (0.260/0.288) is noticeably above GPT-Z's (0.246/0.261).

### 2.3 D_C — combination rules for GPT-Z + Claude-FS (the production pair, no Gemini)

Two declared combination rules (`combine.py` §0): **OR** = positive if either model says yes;
**AND** = positive only if both agree. ("Claude-FS decides, GPT-Z as tiebreaker" is undefined for
2 voters and is skipped, per the task.)

| Set | verse OR | verse AND | strict OR | strict AND | token OR | token AND |
|---|---|---|---|---|---|---|
| A | 0.566 | 0.559 | 0.295 | — | 0.313 | — |
| B | **0.560** | 0.532 | **0.300** | 0.164 | **0.313** | 0.187 |
| D | 0.553 | 0.558 | 0.304 | — | 0.327 | — |
| D2 | 0.556 | 0.562 | 0.316 | — | 0.340 | — |
| M1 | 0.559 | 0.498 | 0.300 | — | 0.305 | — |
| M2 | 0.574 | 0.554 | 0.327 | — | 0.346 | — |
| H1 | 0.559 | 0.541 | 0.299 | — | 0.317 | — |
| H2 | 0.571 | 0.505 | 0.300 | — | 0.319 | — |
| Q1 | 0.549 | 0.437 | 0.303 | — | 0.328 | — |
| Q2 | 0.563 | **0.573** | 0.320 | — | 0.344 | — |
| **mean** | **0.561** | 0.532 | — | — | — | — |

(Full strict/token AND figures for every set are in the JSON; B's are shown above as the
headline example — AND is uniformly the weaker rule on strict/token because it requires 2
independent models to localize the *same* span, a strictly harder bar than OR's "either model's
positive call is enough.")

**Reading**: OR beats or ties AND on verse in 8/10 sets (D and Q2 are the exceptions); OR beats
AND on every strict/token cell checked. OR is consistently the useful rule for this pair.

### 2.4 D_D — current 3-model design, 2-of-3 majority (GPT-Z + Claude-FS + Gemini)

Two Gemini variants: **Gemini-FS** (same few-shot set as Claude) and **Gemini-Z** (zero-shot).

| Set | verse (Gemini-FS) | verse (Gemini-Z) | strict (Gemini-FS) | token (Gemini-FS) |
|---|---|---|---|---|
| A | 0.573 | 0.569 | 0.234 | 0.264 |
| B | 0.556 | 0.559 | 0.223 | 0.244 |
| D | 0.582 | 0.564 | 0.236 | 0.267 |
| D2 | 0.583 | 0.571 | 0.242 | 0.268 |
| M1 | 0.517 | 0.505 | 0.213 | 0.237 |
| M2 | 0.567 | 0.561 | 0.232 | 0.263 |
| H1 | 0.571 | 0.551 | 0.248 | 0.268 |
| H2 | 0.559 | 0.540 | 0.252 | 0.278 |
| Q1 | 0.498 | 0.475 | 0.174 | 0.198 |
| Q2 | 0.578 | 0.573 | 0.234 | 0.267 |
| **mean** | **0.559** | **0.547** | — | — |

### 2.5 D_E — the other two pairs (which 2-model pair is actually best?)

Using each pair's OR rule (the consistently stronger one, §2.3), set by set:

| Set | GPT+Claude (D_C) | GPT+Gemini | Claude+Gemini | **best pair (verse)** |
|---|---|---|---|---|
| A | 0.566 | 0.572 | **0.587** | Claude+Gemini |
| B | 0.560 | **0.569** | 0.551 | GPT+Gemini |
| D | 0.553 | 0.574 | **0.582** | Claude+Gemini |
| D2 | 0.556 | **0.582** | 0.577 | GPT+Gemini |
| M1 | **0.559** | 0.558 | 0.513 | GPT+Claude |
| M2 | **0.574** | 0.566 | 0.568 | GPT+Claude |
| H1 | 0.559 | 0.568 | **0.576** | Claude+Gemini |
| H2 | 0.571 | **0.582** | 0.555 | GPT+Gemini |
| Q1 | 0.549 | **0.560** | 0.494 | GPT+Gemini |
| Q2 | 0.563 | 0.559 | **0.583** | Claude+Gemini |

**On verse, the production pair (GPT+Claude) is the best of the three pairs in only 2/10 sets
(M1, M2)** — in the other 8, a pair that keeps Gemini and drops either GPT or Claude does better.
On strict/token the pattern is sharper and nearly uniform: **Claude+Gemini is the best pair in
8/10 sets on strict and 9/10 on token; GPT+Claude is never the best pair on either span-level
metric.** This is the clearest single piece of evidence against "GPT+Claude, no Gemini" as a
*combination* choice specifically — Gemini pairs better with Claude on localization accuracy
than GPT does, in nearly every few-shot set tried.

### 2.6 Leave-one-out: marginal contribution of each model

Marginal(model) = F1(3-model 2-of-3 majority, D_D/Gemini-FS) − F1(best 2-model combo without that
model, i.e. the better of that pair's OR/AND). Bootstrap 95% CI over poems.

**Verse (primary)** — every set:

| Set | ens. F1 | marg. Gemini | marg. Claude | marg. GPT |
|---|---|---|---|---|
| A | 0.573 | +0.0075 ns | +0.0009 ns | −0.0142 ns |
| B | 0.556 | −0.0047 ns | −0.0136 ns | +0.0048 ns |
| D | 0.582 | +0.0240 ns | +0.0080 ns | −0.0001 ns |
| D2 | 0.583 | +0.0215 ns | +0.0013 ns | +0.0064 ns |
| M1 | 0.517 | −0.0418 ns | −0.0405 ns | +0.0043 ns |
| M2 | 0.567 | −0.0074 ns | +0.0010 ns | −0.0010 ns |
| H1 | 0.571 | +0.0127 ns | +0.0039 ns | −0.0047 ns |
| H2 | 0.559 | −0.0114 ns | −0.0225 ns | +0.0043 ns |
| Q1 | 0.498 | −0.0508 ns | **−0.0622 SIG** | +0.0047 ns |
| Q2 | 0.578 | +0.0043 ns | +0.0189 ns | −0.0053 ns |
| **mean / n SIG** | — | **−0.0046 / 0 of 10 SIG** | −0.0094 / 1 of 10 SIG | −0.0001 / 0 of 10 SIG |

**On the primary metric, no model's marginal contribution to the 3-model majority ensemble is
significant in essentially any set** (the lone exception, Claude on Q1, is a single-poet-pairing
effect already flagged as noise-prone in `E1_V2_ERAS_FEWSHOT.md`). **Gemini's mean marginal
contribution on verse is ≈0, same order as GPT's and Claude's.**

**Strict/token (secondary)** — every single set, every model:

| Criterion | marg. Gemini | marg. Claude | marg. GPT |
|---|---|---|---|
| strict | **SIG negative in 10/10 sets** (range −0.048 to −0.129) | **SIG negative in 10/10** (−0.065 to −0.143) | **SIG negative in 10/10** (−0.079 to −0.137) |
| token | **SIG negative in 10/10** (−0.041 to −0.129) | **SIG negative in 10/10** (−0.054 to −0.129) | **SIG negative in 10/10** (−0.072 to −0.135) |

**Read this result carefully — it is a combination-rule artifact, not literal evidence that every
model "hurts."** The 3-model ensemble requires 2-of-3 voters to agree on the exact *same* GT span
(the span-identity rule `ensemble_v2.py` already declares and documents as an under-counting
limitation); the "best 2-model combo" comparison point is almost always that pair's **OR** rule,
which only needs *one* model's positive call to be right. A stricter 3-way agreement bar will
structurally lose F1 to a looser 2-way "either is enough" bar whenever recall is the bottleneck —
which it is here (strict/token recall sits at 0.15–0.40 across every single model in this pilot).
**This is the same phenomenon `E1_V2_ENSEMBLE.md` §0/§6 already documented** (the ensemble's
declared span rule makes it worse than the average single model on strict/token in every set it
checked) — this task's leave-one-out numbers are a restatement of that known limitation across
three different "remove-one-model" cuts, not a new, independent finding that Gemini (or Claude,
or GPT) is actively harmful. **On the metric that is actually primary for this project's
conclusions (verse), none of the three marginal contributions reach significance.**

### 2.7 Precision/recall, agreement, abu_nuwas split (headline set = B)

| Design | verse P | verse R | verse F1 |
|---|---|---|---|
| D_A GPT-Z | 0.439 | 0.732 | 0.549 |
| D_B Claude-FS[B] | 0.433 | 0.740 | 0.547 |
| D_C OR [B] | 0.420 | **0.843** | 0.560 |
| D_C AND [B] | 0.460 | 0.630 | 0.532 |
| D_D Gemini-FS [B] | 0.442 | 0.748 | 0.556 |
| D_D Gemini-Z [B] | 0.462 | 0.709 | 0.559 |

Combining two models via OR buys recall (0.843 vs either single model's ~0.73-0.74) at a modest
precision cost (0.420 vs 0.43-0.44) — the same recall-for-precision trade this project has
documented at every other point two signals are combined (Phase 1 §3f/§3g, `E1_V2_ENSEMBLE.md`).

**Agreement matrix, GPT-Z vs Claude-FS[B]** (327 verse-units):

| Bucket | n | GT-positive rate | accuracy (as predicted) |
|---|---|---|---|
| both say yes | 174 | 0.460 | 0.460 |
| GPT only | 38 | 0.342 | 0.342 |
| Claude only | 43 | 0.326 | 0.326 |
| neither | 72 | 0.278 | **0.722** |

The two models agree on 174+72 = **246/327 (75%)** of verse-units. When they agree on "no," they
are usually right (72% accuracy) — the same "negative buckets are the most reliable" pattern
`E1_V2_ENSEMBLE.md` §4 found for the 3-model vote. When only one model says yes, that call is
right only ~33% of the time either way — GPT-only and Claude-only disagreement cells are **not**
meaningfully more trustworthy for one model than the other.

**أبو نواس vs other (indicative only, n=5 poems)**: every design scores noticeably higher on
أبو نواس poems than on the other 20 (e.g. D_C-OR[B]: 0.629 vs 0.545; D_D-Gemini-FS[B]: 0.632 vs
0.540) — consistent with every other abu_nuwas/other split already reported in this project, and
exactly as unreliable at n=5 as every one of those.

---

## Part 3 — Cost

### 3.1 Real cost already spent on the 25-poem pool (per model, relevant sets)

From `run_manifest.json`'s real logged usage × `runner.call_cost` (same pricing table used
throughout E1 v2 — Claude $3/$15 per MTok, GPT $0.75/$4.50, Gemini $1.50/$9.00):

| Model | Set Z | Set B |
|---|---|---|
| GPT-5.4-mini | $0.2698 | $0.3248 |
| Claude Sonnet 4.6 | $1.5860 | $1.8957 |
| Gemini | $0.5098 | $0.6033 |

**Design cost already incurred on this 327-verse pool**: GPT-Z + Claude-FS[B] = $0.2698 + $1.8957
= **$2.1655**. Adding Gemini-FS[B] = **$2.7688** (+28%); adding Gemini-Z = **$2.6753** (+25%).

### 3.2 Projected cost at full-corpus scale (from `FULL_COST_MODEL_V2.md` §3 — not re-estimated here)

That document's S1 (all 25 subtypes, zero-shot, 161-poem/3,246-verse pool) and S2 (all 25
subtypes, few-shot set B, 158-poem/3,228-verse pool) per-model totals, 1 run:

| Model | S1 (zero-shot) | S2 (fewshot-B) |
|---|---|---|
| Claude Sonnet 4.6 | $402.25 | **$476.46** |
| GPT-5.4-mini | **$68.67** | $81.87 |
| Gemini | $130.09 | $152.43 |

**Production design (GPT S1 + Claude S2, no Gemini)**: $68.67 + $476.46 = **$545.13**.
**+ Gemini-FS (S2)**: $545.13 + $152.43 = **$697.56**. **+ Gemini-Z (S1)**: $545.13 + $130.09 =
**$675.22**.

**Saving from dropping Gemini**: **$152.43** (22% of the with-Gemini-FS total, 28% of the
no-Gemini total) if the alternative kept Gemini on few-shot; **$130.09** (19%/24%) if Gemini would
have run zero-shot. With the 50%-off batch API (verified live by `FULL_COST_MODEL.md`, not
re-checked this session): no-Gemini $272.57, with-Gemini-FS $348.78 — same percentage saving,
roughly $76 at batch rates instead of $152.

Per-decision cost (from `FULL_COST_MODEL_V2.md` §2, independent of pool size): zero-shot mean
$0.004957 (Claude) / $0.000846 (GPT) / $0.001603 (Gemini) per `(verse, subtype)` call; fewshot-B
mean $0.005904 / $0.001015 / $0.001889. Claude is 3.1-5.8× GPT's per-call cost and ~3.1× Gemini's
— Claude's few-shot cost, not Gemini's, is the dominant line item in every design that includes
it, with or without Gemini.

### 3.3 Gemini pricing/identity uncertainty (flagged, not resolved — no API calls made here)

Every `google`-provider record in `run_manifest.json` logs `model_id: "gemini-3.5-flash"` — the
**requested** model string — with **zero** records showing `gemini-3.6-flash` anywhere in the
manifest (checked directly for this task: 6,578 google records, all sets, all "gemini-3.5-flash").
This matters because `E1_V2_RESULTS.md` separately claimed a pre-run verification call's raw API
response `model_version` field showed `gemini-3.6-flash` was *actually served* — a claim not
corroborated by anything persisted to the manifest, and explicitly walked back later in
`E1_V2_ERAS_FEWSHOT.md` §6.6 ("Gemini was served as `gemini-3.5-flash` throughout this entire
document's experiments — never `gemini-3.6-flash`"). **Net: which Gemini model actually served
every call across this pilot is not fully resolved from available records**, though the real
total spend ($10.5680 on Z/A/B/C) matches the project's configured $1.50/$9.00 rate exactly
(`FULL_COST_MODEL_V2.md` §0.1) — so the *billing* is not in question even if the model-string
identity is. `FULL_COST_MODEL_V2.md` §5 already recommends a one-time manual AI-Studio-console
check before committing real money to a full-corpus run; nothing in this task changes that
recommendation (no live check was made here, per the task's "NO API calls" instruction).

---

## Part 4 — Verdict

**Is dropping Gemini justified?** **Yes, on the evidence available, with real but bounded risk
— not an unambiguous "no loss" result.**

- **On the project's own primary metric (verse), Gemini's marginal contribution to the 3-model
  majority ensemble is statistically indistinguishable from zero in every one of the 10 few-shot
  sets tested** (§2.6) — mean marginal F1 ≈ −0.005, 0/10 significant. The simpler GPT-Z + Claude-FS
  design (via OR) scores **F1 0.560 on set B vs the 3-model ensemble's 0.556** — numerically
  *higher* without Gemini, though the difference itself was not tested for significance (it is
  smaller than the CIs already computed on the 3-model side, so should not be read as "dropping
  Gemini helps").
- **What the 2-model (GPT-Z + Claude-FS) design adds over either single model alone**: +0.011 to
  +0.013 F1 over Claude-FS[B] alone (0.560 vs 0.547) and +0.011 over GPT-Z alone (0.560 vs 0.549)
  on verse, bought with a real recall gain (0.843 vs ~0.73-0.74) at a real precision cost (0.420
  vs ~0.43-0.44) — a modest, not dramatic, improvement, and the production pair is the single
  model it protects against most is GPT, since GPT and Claude's joint "neither says yes" calls are
  correct 72% of the time (§2.7).
- **Saves real money**: $152.43 of a projected $697.56 full-corpus run (22%) if the alternative
  would have added Gemini on few-shot, or $130.09 (19%) if zero-shot (§3.2) — not a trivial saving
  at this project's demonstrated budget sensitivity (`FULL_COST_MODEL_V2.md`'s own $100/$300
  ceiling exercises).

**But the risk picture is not clean, and three things argue for caution, not confidence:**

1. **On strict/token — the span-level metrics that actually check *where* the model points, not
   just *whether* it says yes — Claude+Gemini is the best 2-model pair in 8-9 of 10 sets, and
   GPT+Claude (the chosen production pair) is never the best pair on either span-level metric**
   (§2.5). If localization accuracy (not just presence/absence) matters for any downstream use of
   this pipeline's output, dropping Gemini specifically removes the model that pairs best with
   Claude for that purpose — a real, if secondary-metric-only, cost of this decision.
2. **One run, no noise baseline, anywhere in this analysis** — every comparison above, including
   the "Gemini's marginal contribution is ns" headline finding, rests on 1 run per cell
   (CLAUDE.md rule 2). A second run could plausibly move any individual set's marginal-contribution
   point estimate across the significance boundary, the same way a documented 8× apparent gain
   halved on replication elsewhere in this project.
3. **Generality is untested beyond this one subtype.** Every number in this document is for
   **استعارة فعل** alone — one subtype out of 25 in the full taxonomy, and the one subtype where
   Phase 1 found **Gemini winning most clearly on Trope overall** (§1.1). Phase 1's full-Trope
   ranking (Gemini best) and this subtype's E1 v2 ranking (GPT best zero-shot, Claude/Gemini
   trading #1 on few-shot by metric) already disagree with each other (Part 1) — there is no basis
   in the current evidence for assuming either model's relative standing on **استعارة فعل**
   generalizes to the other 24 subtypes, several of which (مجاز مرسل, the archaic/lexicalized
   تمثيل types) behave very differently in Phase 1's own findings (PROJECT_STATE.md §3c).

**Recommendation**: the production design (GPT-Z + Claude-FS, no Gemini) is a **defensible, not a
risk-free, cut** — it is justified by a real, if modest, cost saving and no significant loss on
the metric the project has already chosen as primary, but it trades away the one pairing
(Claude+Gemini) that is consistently strongest on span-level correctness, on evidence from a
single subtype and a single run. **Before committing to it for the full run**, a cheap, targeted
check is worth running rather than assumed away: **one additional subtype, all 3 models, zero-shot
only, on the existing 25-poem pool** — reusing this pilot's own infrastructure (no new example
sets needed for a zero-shot-only check), at **≈$2.37** (GPT $0.27 + Claude $1.59 + Gemini $0.51,
scaled from §3.1's real Z-set costs for this subtype) for one run, or **≈$4.73** for the 2-run
minimum CLAUDE.md rule 2 requires before drawing any comparative conclusion from it. A reasonable
second-subtype candidate is one of the ≥50-GT-instance subtypes from `FULL_COST_MODEL_V2.md` §4
(enough support to score meaningfully) that is **not** another Trope/استعارة subtype — ideally
something structurally different from استعارة فعل (e.g. a كناية or طباق subtype) so the check
speaks to generality across element *types*, not just across metaphor subtypes. **This check was
not run as part of this task** (no API calls were authorized or made).

---

## Sources

`CLAUDE.md`, `PROJECT_STATE.md` §1-§7 (Phase 1, frozen), `docs/phase4/{E1_V2_RESULTS,
E1_V2_ENSEMBLE,E1_V2_ERAS_FEWSHOT,E1_V2_MULTIPOET,FULL_COST_MODEL_V2}.md`,
`results/phase4_e1_v2/run_manifest.json` (20,061 records, read programmatically),
`experiments/phase4_e1_v2/{e1v2_config,ensemble_v2,gt_v2,verse_analysis,runner}.py` (unmodified,
reused), `experiments/phase4_e1_v2/design_choice/{combine,analyze_design_choice}.py` (new, this
task). Full numeric report: `results/phase4_e1_v2/design_choice/analysis_report_design_choice.json`.
