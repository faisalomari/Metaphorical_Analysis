# Phase 5 — Local Fine-Tuning Results (RTX 3060 Ti, 8GB VRAM)

**Scope**: fine-tune 3 public Arabic BERT-base models, fully local, no API calls, on 5
verse-level binary classification targets chosen from `data/ali_poems/` (166 poems, 3,470
verses, excl. poem 28601 — no word-level text on the source site). Code:
`experiments/phase5_local_ft/`. Raw metrics + per-verse test predictions (no weights, ever):
`results/phase5_local_ft/raw/*.json` (132 files: 99 model-training runs + 33 baseline cells).

Terminology note (per `GLOSSARY.md`): طباق=antithesis, كناية=periphrasis, مجاز (incl.
استعارة)=trope/metaphor — used throughout below.

---

## 1. Environment

- GPU: NVIDIA GeForce RTX 3060 Ti, 8.59 GB VRAM. `torch` 2.12.0.dev20260323+cu128 already had
  working CUDA — no install-confirmation needed (the task's STOP condition was "if torch
  lacks CUDA" only). Installed `transformers` 5.20.1, `accelerate`, `safetensors`,
  `sentencepiece` (none were present).
- Models downloaded (public, no HF token): `CAMeL-Lab/bert-base-arabic-camelbert-ca`,
  `aubmindlab/bert-base-arabertv2`, `UBC-NLP/MARBERT`.

## 2. The 5 targets (chosen from data, not by guess)

Counted positive verses + poems-containing for every subtype and the 4 parent elements
across all 166 poems. Threshold: **>=150 positive verses** (14 subtypes qualified — no need
to lower it). Of those 14, 4 (اشتقاق/ترديد/مبالغة/رد الأعجاز على الصدور) are rhetorical
devices **outside** this project's 4-element scope (not in
`experiments/phase3_subelements/subtype_defs.py`) with zero LLM difficulty evidence to rank
against, and were excluded. From the remaining 10 in-scope candidates (spanning all 4
parents, but Simile/Antonymy each had only 1 above-threshold subtype), picked 5 — one per
difficulty level, Trope sampled twice to anchor both sides of the forced استعارة فعل medium
reference (full evidence + weak-evidence flags: `experiments/phase5_local_ft/config/targets.json`):

| Level | Subtype | Parent | pos_verses | poems_with | pos_rate | pos_weight (corpus-wide) |
|---|---|---|---|---|---|---|
| very easy | تشبيه مطول | Simile | 217 | 85 | 6.3% | 14.99 |
| easy | استعارة تمثيلية | Trope | 287 | 94 | 8.3% | 11.09 |
| medium | استعارة فعل | Trope | 1258 | 156 | 36.3% | 1.76 |
| hard | طباق إيجاب | Antonymy | 456 | 114 | 13.1% | 6.61 |
| very hard | كناية عن فعل | Kenning | 280 | 90 | 8.1% | 11.39 |

Difficulty was anchored on Phase 1's frozen v4_combined parent-level strict F1 (`PROJECT_STATE.md`
§3a: Simile ~0.70 > Trope ~0.29 > Antonymy ~0.165 > Kenning ~0.109, avg across 3 LLMs), plus,
within Trope/Kenning, the §3c TEST-scale subtype breakdown and Phase3-crossmodel per-subtype
recall. **Weak-evidence flags** (kept from Step 1, relevant below): استعارة تمثيلية's LLM
difficulty is sharply model-dependent (Gemini recall 0.143 vs GPT 0.571 on the same subtype);
طباق إيجاب's LLM difficulty is driven by a precision/over-claiming failure specific to
generative models, not necessarily transferable to a from-scratch classifier; كناية عن فعل's
own small-sample Phase3 run-to-run recall swung 70%→50% between runs. The user reviewed and
approved this table before any training.

**Ground-truth verification**: re-counting استعارة فعل positives on exactly E1 v2's 25-poem/
327-verse pool reproduced **127 GT-positives**, matching Claude-Sonnet-set-A's TP=104+FN=23=127
from `docs/phase4/E1_V2_RESULTS.md` exactly.

## 3. Splits (poem-level, poet-stratified, 3 seeds each)

Stratification bug caught+fixed during development: naive per-poet-group largest-remainder
rounding starved minority splits (most of the 51 poets have only 1-2 poems, so every 2-poem
poet's rounding tie went to `train`, deflating S2's test split to ~10% instead of 15%).
Replaced with sequential apportionment over a poet-interleaved processing order
(`experiments/phase5_local_ft/splitting.py`) — now hits every target ratio to within ~1 poem.

- **S1** (80/20 train/test, then 10% of train carved off as val): ~72/8/20% of poems.
- **S2** (70/15/15 train/val/test): ~70/15/15% of poems (e.g. seed0: 116/25/25 poems =
  69.9/15.1/15.1%).
- **S3** (استعارة فعل only): **TEST fixed to E1 v2's exact 25-poem/327-verse pool across all
  3 seeds** (asserted); train/val from the other 141 poems, split 90/10 (mirrors S1's "10% of
  train as val" convention — the task gave no explicit S3 train/val ratio); poems
  16251/17234/21337 (E1/E1v2's few-shot example source poems) forced into train, never val
  (asserted every seed — they were already outside the 25-poem test pool by construction, so
  this is an extra guarantee, not a fix for an actual leak).
- **S1/S2 reshuffle the WHOLE partition per seed** (train+val+test all vary); **S3 keeps TEST
  fixed** across all 3 seeds and only reshuffles train/val, per the task's explicit "fixed
  test in S3" instruction.

Per-target class balance is stable across splits/seeds (full table:
`experiments/phase5_local_ft/step2_splits.py` output) — no split/seed shows a wildly
different positive rate than the corpus-wide numbers in the table above.

## 4. Models and training

| | |
|---|---|
| max_len | **32** (99th-pct verse token length: camelbert_ca 20, arabert_v2 21, marbert 23 — one shared value, covers all 3 with margin; Arabic poetry hemistichs are short, mean ~12-15 tokens) |
| batch size / grad-accum | 64 / 1 (short sequences + bert-base fit 8GB comfortably at this length — no accumulation needed) |
| precision | fp16 (`torch.autocast` + `GradScaler`, fp32 master weights) |
| optimizer | AdamW, lr=2e-5, weight_decay=0.01 |
| class imbalance | **BCEWithLogitsLoss(pos_weight=neg/pos)**, computed from each run's own TRAIN split (not a fixed corpus constant) — reported per run |
| early stopping | on val F1 (best-threshold search, 0.05-0.95 step 0.01), patience=3 epochs, max 15 epochs |
| decision threshold | tuned on VAL only, applied unchanged to TEST |
| checkpoints | kept in memory only during a run (best-val-F1 epoch); **never written to disk** |

**Smoke test** (CAMeL-BERT-CA, استعارة فعل, S2 seed0): ~3.6-4.3s/epoch, full early-stopped run
in 15.9s. A gradient-flow diagnostic (plain BCE, no pos_weight) confirmed the fp16
`GradScaler` was not silently skipping optimizer steps — the near-flat 4-epoch loss curve in
the full run is BERT converging within ~1 epoch on this small/short-sequence corpus, not a bug.

**Full-grid time estimate (printed before the long run, per task instruction)**: ~16-30s/run
→ 99 model-training runs (S1+S2: 3 models × 5 targets × 3 seeds = 90; S3: 3 models × 3 seeds =
9, استعارة فعل only) + 33 baseline cells, well under an hour. **Actual: 44.8 minutes, 99/99
runs OK.** Given this cost, every (model, target, split, seed) cell was run — not just the
best model per target (the task's "if time allows" fallback explicitly applies here).

**Baselines** (per target × split × seed, no GPU): majority class, always-positive, TF-IDF
char-(2,4)-gram + logistic regression (`class_weight="balanced"`, threshold tuned on val).

**Diacritics (val-only, every run — negligible extra cost, no retraining)**: mean (with −
without) val-F1 delta across all 99 runs = **+0.0015 ± 0.030** (42 runs favor with, 23 favor
without, 34 ≈tied) — **no systematic effect either direction**; the largest individual swings
(±0.10-0.13) are concentrated in the already-unstable very_easy/camelbert_ca cells, not a real
diacritics signal.

**QLoRA 4-bit 1.5-3B note (per task instruction — not run)**: at this sequence length (32
tokens), a 1.5-3B model in 4-bit would need roughly 1-2GB for frozen weights plus a few
hundred MB for LoRA adapters/optimizer states/activations — comfortably under 8GB and very
likely to fit and train on this GPU. Out of scope here.

## 5. Results — F1 by target × model × split (TEST only)

Primary metric: verse-level F1 (raw TP/FP/FN always alongside, per CLAUDE.md rule 3). Mean±std
across 3 seeds; bootstrap 95% CI over poems (pooled across the 3 seeds' test predictions,
2000 iters, seed=0 — same method/params as the project's existing poem-resampling bootstrap)
for S2/S3.

### S2 (70/15/15) — primary split

| Level | Model | F1 mean±std | P | R | TP/FP/FN | bootstrap 95% CI |
|---|---|---|---|---|---|---|
| very easy | camelbert_ca | 0.096±0.049 | 0.073 | 0.418 | 32/421/66 | [0.076,0.155] |
| very easy | arabert_v2 | 0.097±0.026 | 0.056 | 0.397 | 34/594/64 | [0.054,0.131] |
| very easy | **marbert** | **0.282±0.090** | 0.296 | 0.285 | 27/67/71 | [0.177,0.371] |
| easy | camelbert_ca | 0.120±0.038 | 0.075 | 0.354 | 42/476/85 | [0.065,0.220] |
| easy | arabert_v2 | 0.148±0.034 | 0.087 | 0.570 | 75/752/52 | [0.100,0.218] |
| easy | **marbert** | **0.189±0.023** | 0.139 | 0.401 | 54/400/73 | [0.119,0.253] |
| medium | camelbert_ca | 0.546±0.006 | 0.380 | 0.969 | 561/915/16 | [0.493,0.592] |
| medium | arabert_v2 | 0.542±0.006 | 0.376 | 0.968 | 560/927/17 | [0.487,0.592] |
| medium | **marbert** | **0.562±0.008** | 0.405 | 0.919 | 532/787/45 | [0.508,0.606] |
| hard | camelbert_ca | 0.175±0.072 | 0.119 | 0.584 | 108/732/117 | [0.152,0.252] |
| hard | arabert_v2 | 0.246±0.027 | 0.143 | 0.911 | 207/1212/18 | [0.197,0.306] |
| hard | **marbert** | **0.275±0.053** | 0.246 | 0.351 | 88/272/137 | [0.229,0.358] |
| very hard | **camelbert_ca** | **0.217±0.020** | 0.131 | 0.661 | 107/698/55 | [0.148,0.300] |
| very hard | arabert_v2 | 0.172±0.015 | 0.108 | 0.422 | 67/549/95 | [0.096,0.248] |
| very hard | marbert | 0.164±0.007 | 0.149 | 0.272 | 45/333/117 | [0.121,0.213] |

**Best model per target** (bold above): MARBERT wins 4 of 5 (very_easy, easy, medium, hard);
CAMeLBERT-CA wins very_hard (كناية عن فعل) — plausibly because it is the one model
pretrained specifically on Classical Arabic, mattering most on the hardest/most semantically
subtle target.

### S1 (80/20) — full grid also run (time allowed)

| Level | Model | F1 mean±std | P | R | TP/FP/FN |
|---|---|---|---|---|---|
| very easy | camelbert_ca | 0.115±0.046 | 0.100 | 0.137 | 18/166/115 |
| very easy | arabert_v2 | 0.099±0.083 | 0.070 | 0.171 | 23/213/110 |
| very easy | marbert | 0.359±0.059 | 0.311 | 0.437 | 58/140/75 |
| easy | camelbert_ca | 0.092±0.065 | 0.050 | 0.574 | 93/1165/85 |
| easy | arabert_v2 | 0.103±0.048 | 0.065 | 0.559 | 91/1150/87 |
| easy | marbert | 0.225±0.041 | 0.162 | 0.449 | 78/455/100 |
| medium | camelbert_ca | 0.535±0.029 | 0.371 | 0.960 | 748/1272/31 |
| medium | arabert_v2 | 0.538±0.027 | 0.376 | 0.947 | 737/1232/42 |
| medium | marbert | 0.549±0.034 | 0.421 | 0.800 | 623/859/156 |
| hard | camelbert_ca | 0.200±0.031 | 0.127 | 0.541 | 153/1019/117 |
| hard | arabert_v2 | 0.222±0.019 | 0.130 | 0.798 | 221/1455/49 |
| hard | marbert | 0.254±0.103 | 0.248 | 0.326 | 84/242/186 |
| very hard | camelbert_ca | 0.125±0.017 | 0.070 | 0.691 | 101/1379/47 |
| very hard | arabert_v2 | 0.146±0.014 | 0.082 | 0.739 | 110/1257/38 |
| very hard | marbert | 0.110±0.001 | 0.108 | 0.114 | 17/145/131 |

Same qualitative pattern as S2 (medium far ahead of the rest; MARBERT generally strongest on
the low-prevalence targets, with far fewer false positives than the other two models).

### S3 (استعارة فعل only, TEST fixed to E1 v2's 25-poem/327-verse pool)

| Model | F1 mean±std | P | R | TP/FP/FN | bootstrap 95% CI |
|---|---|---|---|---|---|
| camelbert_ca | 0.564±0.003 | 0.394 | 0.995 | 379/584/2 | [0.485,0.634] |
| arabert_v2 | 0.568±0.012 | 0.400 | 0.984 | 375/564/6 | [0.487,0.639] |
| **marbert** | **0.570±0.005** | 0.427 | 0.887 | 338/467/43 | [0.495,0.635] |

## 6. Baselines (mean across 3 seeds)

| Level | Split | majority F1 | always-positive F1 | TF-IDF+logreg F1 mean±std |
|---|---|---|---|---|
| very easy | S1 | 0.000 | 0.119 | 0.296±0.032 |
| very easy | S2 | 0.000 | 0.118 | 0.268±0.020 |
| easy | S1 | 0.000 | 0.156 | 0.184±0.028 |
| easy | S2 | 0.000 | 0.155 | 0.166±0.018 |
| medium | S1 | 0.000 | 0.540 | 0.541±0.026 |
| medium | S2 | 0.000 | 0.548 | 0.543±0.011 |
| medium | S3 | 0.000 | 0.559 | 0.553±0.004 |
| hard | S1 | 0.000 | 0.226 | 0.235±0.015 |
| hard | S2 | 0.000 | 0.252 | 0.227±0.033 |
| very hard | S1 | 0.000 | 0.132 | 0.145±0.021 |
| very hard | S2 | 0.000 | 0.193 | 0.158±0.024 |

`majority` is always 0 F1 (negative is the majority class for all 5 targets; a target with
<50% positive rate always makes this baseline trivially fail on recall). More informative:
**TF-IDF+logreg is a genuinely competitive baseline, not a strawman** — it beats 2 of 3 BERT
models outright on very_easy (0.268-0.296 vs camelbert_ca 0.096 / arabert_v2 0.097), and on
medium it is within ~2 points of the best BERT model (0.543 vs 0.562) and barely above
**always-positive** (0.548) — a textbook case of CLAUDE.md rule 4's standing warning that a
verse-level metric on a high-prevalence target rewards blanket-positive predictions almost as
much as real discrimination. BERT's real, clear lift over TF-IDF only shows up on hard/very
hard/easy (lower-prevalence, more semantically subtle targets).

## 7. Does fine-tuned-model difficulty follow the LLMs' difficulty order?

**No — not even close, and the reason is informative.** LLM-based difficulty order (Phase1
frozen F1 + Phase3 recall): **very_easy > easy > medium > hard > very_hard**. Fine-tuned S2
F1, averaged across the 3 models: **medium (0.550) >> hard (0.232) > very_hard (0.184) >
very_easy (0.158) ≈ easy (0.152)** — medium dominates, and the two targets the LLMs found
*easiest* (very_easy, easy) are the fine-tuned models' *worst* two.

**This tracks positive-verse count almost perfectly, not rhetorical difficulty**: Pearson
r = **0.996** between each target's corpus-wide positive-verse count (217/287/1258/456/280)
and its S2 mean F1 (0.158/0.152/0.550/0.232/0.184) across the 5 targets. The fine-tuned
classifiers' performance here is dominated by **how much positive training signal exists**,
not by how semantically subtle the rhetorical device is to a reader (or to a zero/few-shot
LLM). This makes sense mechanically — LLM difficulty reflects world-knowledge/reasoning
transfer from pretraining with *zero* task-specific positive examples, while a from-scratch
fine-tuned classifier's only signal is however many labeled positives it was shown — but it
means the two difficulty rankings answer genuinely different questions and should not be
conflated in the thesis.

## 8. استعارة فعل (medium), S3 — direct comparison with the LLM experiments

Same exact 25-poem/327-verse TEST pool, same verse-level primary criterion
(`docs/phase4/E1_V2_RESULTS.md`'s "verse" criterion — gt_v2.py's definition, reproduced
exactly here, see §2):

| | F1 | 95% CI |
|---|---|---|
| **Best fine-tuned (MARBERT, S3)** | **0.570** | **[0.495, 0.635]** (bootstrap, over poems) |
| Best single LLM (Claude Sonnet 4.6, set A) | 0.576 | not available (no run-noise baseline for the LLM experiments — `E1_V2_RESULTS.md` caveat) |
| LLM 3-model ensemble (set A) | 0.568 | not available |
| LLM zero-shot range (set Z, 3 models) | 0.377–0.549 | — |

Difference: fine-tuned best − best-single-LLM = **−0.006**; fine-tuned best − ensemble =
**+0.002** — both differences are tiny, and the fine-tuned model's own 95% CI comfortably
contains both LLM numbers. **Plainly stated: on this one target, with enough positive
training data (36% prevalence, ~1,000+ positive training verses), a small, fully local,
zero-cost fine-tuned BERT-base model statistically matches the best few-shot LLM
configuration and the 3-model ensemble on the identical held-out test set** — while clearly
beating every LLM zero-shot (set Z) number.

## 9. Caveats

- **Small data, few positives for 4 of 5 targets.** Only استعارة فعل has enough positive
  verses (1258) for the classifier to really learn; the other 4 (217-456 positives) are
  working with a few hundred positive examples at most, and this shows directly in their
  far lower, noisier F1 (§7).
- **High-recall / low-precision operating points.** Several cells (e.g. medium/camelbert_ca:
  R=0.969, P=0.380; hard/arabert_v2: R=0.911, P=0.143) show the val-tuned threshold pushing
  hard toward "say yes often" to maximize F1 under class imbalance — the same verse-level
  gaming concern CLAUDE.md rule 4 flags for the LLM experiments applies here to the
  classifier's own chosen threshold, not just to the metric choice.
- **Poet/period shifts.** Splits are poet-stratified but far from poet-balanced (51 poets, 23
  with exactly 1 poem — §3); a held-out test poem's poet may be entirely unseen in training
  for many splits, and classical Arabic rhetorical usage can shift across poets/periods in
  ways this corpus's size can't fully separate from target difficulty.
- **Poems with several rhetorical types in one verse** are common in this corpus (the raw
  annotation schema allows multiple `element`/`subtype` tags on overlapping or adjacent
  spans within a verse) — a verse-level binary label collapses this, same simplification the
  LLM experiments' verse-primary metric already makes (and the same standing caveat CLAUDE.md
  rule 4 raises about it).
- **Run-to-run noise is real and sometimes large** (e.g. hard/marbert S1: F1 std=0.103 across
  3 seeds) — every comparative statement above is read with that in mind, same standing
  discipline as the rest of this project (CLAUDE.md rule 2).
- **No weights were ever saved to disk** (per task instruction) — every number above is
  reproducible from `results/phase5_local_ft/raw/*.json`'s predictions + the saved split
  files, but the trained models themselves do not persist past their own training run.

## 10. Plain answer

A small, locally fine-tuned Arabic BERT-base model (no API cost) **matches the best
few-shot-prompted LLM on استعارة فعل specifically** (the one target with abundant positive
training data) on the identical held-out test set — but **loses clearly on the other 4
targets**, where positive examples are scarce (a few hundred at most) and F1 stays in the
0.10-0.28 range regardless of which of the 3 pretrained models is used. The fine-tuned
models' own difficulty ordering is driven almost entirely by training-data volume (Pearson
r=0.996 with positive-verse count), not by the rhetorical subtlety that governs LLM
zero/few-shot difficulty — so "fine-tuning helps" is not a blanket statement here: it is a
data-volume statement, true only where the corpus happens to already have enough labeled
positives.
