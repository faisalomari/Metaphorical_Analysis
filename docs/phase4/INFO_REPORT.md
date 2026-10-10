# Phase 4 Info Report — facts for planning a few-shot example-sensitivity experiment

**Status**: fact-gathering only. Zero API calls, zero new experiments, no analysis beyond the
ranking requested in §1. Everything below is reconstructed from already-committed files (`PROJECT_STATE.md`,
`NEW_SESSION_HANDOFF.md`, `GLOSSARY.md`, frozen Phase 1/2/3 results, and source code) plus small
read-only scripts run against existing `run_manifest.json` files to compute token/cost averages
(no files were modified, no API calls were made). Terminology: new-term (antithesis/periphrasis)
used going forward per `GLOSSARY.md`; Phase 1 frozen material is quoted with its original terms
(antonymy/kenning) where that's what the source document says, per standing discipline.

---

## 1. Per-element / per-subtype performance — frozen TEST + Phase 2/3

### 1a. Frozen TEST (`PROJECT_STATE.md` §3a) — 2-run majority, strict criterion, pooled across Imru1+Jarir+Abu_Tammam

GT support (deduped): Trope(مجاز)=179, Simile(تشبيه)=52, Kenning/periphrasis(كناية)=147, Antonymy/antithesis(طباق)=43.

| Element | Model | Baseline TP/FP/FN | Baseline F1 | v4_combined TP/FP/FN | v4 F1 |
|---|---|---|---|---|---|
| مجاز (Trope) | Claude Sonnet 4.6 | 17/3/162 | 0.171 | 25/3/154 | 0.242 |
| مجاز (Trope) | GPT-5.4-mini | 6/1/173 | 0.065 | 28/16/151 | 0.251 |
| مجاز (Trope) | Gemini 3.5 Flash | 34/4/145 | 0.313 | 45/9/134 | 0.386 |
| كناية (Periphrasis) | Claude Sonnet 4.6 | 8/2/139 | 0.102 | 8/6/139 | 0.099 |
| كناية (Periphrasis) | GPT-5.4-mini | 1/4/146 | 0.013 | 4/7/143 | 0.051 |
| كناية (Periphrasis) | Gemini 3.5 Flash | 9/4/138 | 0.113 | 15/8/132 | 0.176 |
| تشبيه (Simile) | Claude Sonnet 4.6 | 28/6/24 | 0.651 | 28/6/24 | 0.651 |
| تشبيه (Simile) | GPT-5.4-mini | 30/4/22 | 0.698 | 31/3/21 | 0.721 |
| تشبيه (Simile) | Gemini 3.5 Flash | 32/7/20 | 0.703 | 32/4/20 | 0.727 |
| طباق (Antithesis) | Claude Sonnet 4.6 | 5/14/38 | 0.161 | 6/12/37 | 0.197 |
| طباق (Antithesis) | GPT-5.4-mini | 4/11/39 | 0.138 | 5/17/38 | 0.154 |
| طباق (Antithesis) | Gemini 3.5 Flash | 4/19/39 | 0.121 | 5/21/38 | 0.145 |

**Ranking by difficulty (easiest → hardest), v4_combined strict F1, mean across 3 models**:
1. تشبيه (Simile) — mean F1 ≈ 0.700 (ceiling; precision/recall both high)
2. مجاز (Trope) — mean F1 ≈ 0.293
3. طباق (Antithesis) — mean F1 ≈ 0.165
4. كناية (Periphrasis) — mean F1 ≈ 0.109 (hardest; resistant to every Phase 1/2 intervention except Config C and per-verse Mode A)

### 1b. Trope subtype breakdown, TEST scale (`PROJECT_STATE.md` §3c, pooled 3 models)

| Subtype | n | Baseline missed | v4 missed |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | 62% |
| مجاز عقلي (rational trope) | 41 | 83% | 66% |
| استعارة تمثيلية (unmarked whole-clause allegory) | 24 | 33% | 29% |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% |
| مجاز مرسل (metonymy, single lexicalized word) | 13 | 85% | 85% (flat) |
| استعارة حديثة | 4 | 75% | 75% (flat) |

### 1c. Phase 2 §3i (DEV: Imru2 [+ Nabigha probe for مجاز مرسل]) — Config A/B/C vs. existing v4_combined, pooled DEV strict F1

| Element | Existing (Sonnet4.6, v4) | Config A (Fable5, same prompt) | Config B (terminology-corrected) | Config C (two-stage, per-verse, Imru2 only) |
|---|---|---|---|---|
| مجاز (Trope) | 0.059 | 0.200 | 0.090 | — |
| كناية (Periphrasis) | 0.130 | 0.198 | 0.123 (flat/worse) | 0.316 (token 0.421) on Imru2; targeted probe on Nabigha's مجاز مرسل found only 1/10 strict (0/10 token) survives 2-run majority despite 4/10 (any-of-2-runs) |

### 1d. Phase 3 subtype recall (recall-only — no FP/TN/precision/F1 is computable by this design; every row is a known positive for its own subtype). Span-level, strict/token, reliable subtypes n≥10, Gemini 3.5 Flash vs GPT-5.4-mini (`results/phase3_crossmodel/summary.md`):

| Subtype | Parent | n | Gemini strict | GPT strict | Gemini token | GPT token |
|---|---|---|---|---|---|---|
| استعارة فعل | مجاز (Trope) | 110 | 0.264 | 0.155 | 0.255 | 0.164 |
| كناية عن صفة | كناية (Periphrasis) | 74 | 0.446 | 0.351 | 0.486 | 0.378 |
| كناية عن موصوف | كناية (Periphrasis) | 61 | 0.262 | 0.328 | 0.279 | 0.344 |
| مجاز عقلي | مجاز (Trope) | 54 | 0.463 | 0.426 | 0.463 | 0.481 |
| طباق إيجاب | طباق (Antithesis) | 38 | 0.237 | 0.053 | 0.579 | 0.263 |
| كناية لغوية | كناية (Periphrasis) | 32 | 0.719 | 0.031 | 0.656 | 0.031 |
| تشبيه مطول | تشبيه (Simile) | 30 | 0.833 | 0.667 | 0.933 | 0.767 |
| استعارة تمثيلية | مجاز (Trope) | 28 | 0.143 | 0.571 | 0.143 | 0.571 |
| كناية عن فعل | كناية (Periphrasis) | 27 | 0.333 | 0.148 | 0.481 | 0.185 |
| مجاز مرسل | مجاز (Trope) | 24 | 0.292 | 0.000 | 0.250 | 0.042 |
| استعارة قديمة | مجاز (Trope) | 17 | 0.412 | 0.176 | 0.412 | 0.235 |
| تشبيه قصير | تشبيه (Simile) | 13 | 0.615 | 0.769 | 0.769 | 0.846 |
| كناية فنية | كناية (Periphrasis) | 10 | 0.300 | 0.200 | 0.300 | 0.200 |

12 more subtypes exist with n<10 (flagged, not reliable) — see `results/phase3_crossmodel/summary.md` for the full list (e.g. طباق في المعنى n=8 at 0.000/0.000, كناية بسيطة n=9 at 0.667/0.333).

### 1e. Ranking + recommended mid-difficulty candidates for a few-shot example-sensitivity experiment

**Floor** (near-zero, likely abstention/structural-cap failure, not sensitive to ordinary example tweaks): مجاز مرسل (GPT strict 0.000, Gemini 0.292, flat 85%-missed since Phase 1 v4), كناية لغوية for GPT specifically (0.031 vs Gemini 0.719 — looks like a GPT-specific near-total failure mode, not example-sensitivity), طباق في المعنى (0.000/0.000, n=8).

**Ceiling** (already near-saturated, little room for a few-shot manipulation to show movement): تشبيه مطول (0.667–0.933), تشبيه قصير (0.615–0.846), استعارة تمثيلية for GPT (0.571, though Gemini is floor here — a split case, see caveat below).

**Recommended mid-difficulty candidates (reasoning)**:
1. **مجاز عقلي (rational trope)** — n=54 (Phase 3) / n=41 (Phase 1 TEST), recall 0.426–0.481 across both models and both scoring criteria — the most *cross-model-consistent* mid-range subtype in the whole table (narrow 0.43–0.48 band), large enough sample to trust a delta, and already flagged in Phase 1 §3c as "genuinely hard but tractable" (not flat/resistant like مجاز مرسل).
2. **كناية عن صفة (periphrasis of quality)** — largest periphrasis subtype (n=74), recall 0.351–0.486 across models/criteria, comfortably mid-range and not criterion-sensitive (strict/token stay close, unlike طباق إيجاب below), so an example-sensitivity signal here would be legible rather than swamped by strict-vs-token noise.
3. **استعارة فعل (verbal metaphor)** — largest single subtype overall (n=110), recall 0.155–0.264, mid-low but not floor, and both models' strict and token numbers sit close together (low criterion-sensitivity) — the sample size alone makes it attractive for detecting small effects.

**Explicitly not recommended as "mid"**: طباق إيجاب (criterion-dependent swing 0.237→0.579 strict→token for Gemini, 0.053→0.263 for GPT — too noisy/ambiguous a case to isolate an example-sensitivity effect from a scoring-criterion effect) and استعارة تمثيلية (known DEV→TEST and small-sample reversal pattern, flagged twice already — §3c and Phase 3 `MEETING_SUMMARY.md` §6 — a genuinely unstable subtype across samples, not a stable "mid" baseline).

---

## 2. How examples are injected into prompts today

**Exact file/mechanism**: `experiments/pilot_3models/prompts.py:build_system_message()` concatenates, in `ELEMENT_ORDER` (`Trope, Simile, Kenning, Antonymy`), the full text of `data/elements/{Trope,Simile,Kenning,Antonymy}.txt` into one system message, under a fixed `SYSTEM_HEADER` ("Learn them deeply using ONLY the definitions and examples provided here. Do NOT use outside knowledge.") — see `prompts.py:3-16, 56-61`. This system message is **frozen and byte-identical since Phase 1** (`GLOSSARY.md`: "Phase 1 reproducibility depends on these files staying byte-identical") and is reused, unmodified, by every prompt variant in this project (baseline, v1–v4_combined, decomposed, per-verse Mode A/B, Config A, Config B's terminology-only edit is layered on top of this same base).

**Template per element file** (e.g. `data/elements/Trope.txt`, `Kenning.txt`): `ELEMENT_N:` header, `Arabic name:`, `English name:`, `Arabic explanation:` (one paragraph), `English explanation:` (one paragraph), then `Examples:` followed by **4 or 5 numbered bare verse lines, no span highlighting, no subtype label, no worked reasoning** — confirmed by direct read of `Trope.txt` (4 examples) and `Kenning.txt` (5 examples); `results/phase2_chatlike/example_gap_analysis.md` confirms Simile.txt and Antonymy.txt also carry 5 examples each (19 total across the 4 files).

**Leakage map** (`results/phase2_chatlike/example_gap_analysis.md` §0, verified byte-for-byte): every one of the 19 examples is a real annotated verse from this project's own 5-poem corpus, one per poem in the fixed order **Imru1 → Imru2 → Nabigha → Jarir → Abu_Tammam**:

| # | Trope.txt | Simile.txt | Kenning.txt | Antonymy.txt |
|---|---|---|---|---|
| 1 | Imru1 v22 (**TEST**) | Imru1 v25 (**TEST**) | Imru1 v23 (**TEST**) | Imru1 v38 (**TEST**) |
| 2 | Imru2 v15 (DEV) | Imru2 v6 (DEV) | Imru2 v20 (DEV) | Imru2 v20 (DEV) |
| 3 | Nabigha v7 (DEV) | Nabigha v14 (DEV) | Nabigha v8 (DEV) | Nabigha v20 (DEV) |
| 4 | Jarir v12 (**TEST**) | Jarir v9 (**TEST**) | Jarir v11 (**TEST**) | Jarir v26 (**TEST**) |
| 5 | — | Abu_Tammam v6 (**TEST**) | Abu_Tammam v7 (**TEST**) | Abu_Tammam v8 (**TEST**) |

**Consequence**: 3 of every file's 4–5 examples (60–75%) are literal TEST-poem verses, present in the system message of every frozen TEST call since Phase 1. `PROPOSAL_fewshot.md`'s premise that these examples were "never drawn from the 5 annotated poems" is factually wrong per this table — flagged there already, not re-litigated here. Any new few-shot experiment that reuses `data/elements/*.txt`'s existing examples as its demonstration source would repeat this same leakage; it needs new, externally-sourced example material instead.

---

## 3. Ground-truth format + scoring entry points

**Source files**: `data/ground_truth/ali_ana/original/*.xlsx`, one file per poem (`امرؤ القيس 1.xlsx` = Imru1, `امرؤ القيس 8.xlsx` = Imru2, `النابغة الذبياني.xlsx` = Nabigha, `جرير.xlsx` = Jarir, `ابو تمام.xlsx` = Abu_Tammam) — Dr. Ali Hussein's manual annotations, a 53-label classical taxonomy.

**Fields read** (`experiments/pilot_3models/ground_truth.py:load_ground_truth_spans`, columns from the xlsx):
- `البيت` — verse number (int, 1-indexed, range-checked against the poem's declared `n_verses`; out-of-range/malformed refs skipped)
- `العنصر البلاغي المستعمل` — primary rhetorical-element label (free Arabic text from the 53-label taxonomy)
- `العنصر البلاغي الثانوي` — secondary label (same taxonomy; some rows are double-tagged)
- `التعبير البلاغي` — the span text itself (the literal substring/phrase)

**Mapping to the 4 pilot elements** (`ground_truth.py:SUBSTRING_MAP`, substring match against `primary + " " + secondary`): `مجاز` or `استعارة` → Trope; `تشبيه` → Simile; `كناية` → Kenning; `طباق` → Antonymy. Exact-duplicate `(verse, element, span)` rows are deduplicated (`seen` set). A verse absent from the sheet is treated as containing none of the 4 elements (not "no ground truth"). Output shape: `{verse_no: {element: [{"span": str, "primary": str, "secondary": str}, ...]}}`.

**Subtype-level ground truth** (Phase 3): `data/ground_truth/by_subtype/<subtype>.xlsx`, 28 files, each a slice of the same source xlsx filtered to one of 23 tested (+5 extra) subtypes, tagged with DEV/TEST split and source poem.

**Scoring entry points**:
- `experiments/pilot_3models/span_matching.py` — `normalize()` (strips tashkeel, tatweel, quote-like wrapping incl. `«»`), `strict_overlap(pred, gt)` (substring either direction after normalize), `token_overlap_ratio(pred, gt)` / `token_match(pred, gt, threshold=0.5)` (token-set overlap coefficient with و/ف clitic-prefix variants), `best_match(pred, gt_spans, criterion, threshold)` (returns index of best unused GT span, or `None`).
- `experiments/pilot_3models/span_scoring.py` — `majority_exists_and_appearance(runs, element, verse_no)` (2-run majority vote + first matching run's predicted span), `score_span_level(by_provider, gt_spans, n_verses, criterion, threshold=0.5)` — **the real scoring function**: TP/FP/FN/TN per provider per element, span-aware, multi-instance-aware (unmatched extra GT instances in a multi-figure verse count as additional FN). `score_verse_level()` is kept only for the old-vs-new comparison, not used for any frozen number.
- `experiments/pilot_3models/analyze.py` — `prf1(tp, fp, fn)` (precision/recall/F1), `load_all_runs()` / `load_all_runs_single_element()` (manifest+raw-text loaders; discard a run if its manifest `error` field is truthy), `run_consistency()`, `cross_model_agreement()`, `build_comparison_table()` (all take an explicit `n_verses` parameter — see `PROJECT_STATE.md` §6.4 pitfall about a historical hardcoded-constant bug, now fixed).
- `experiments/pilot_3models/test_report.py` — reproduces the frozen TEST table exactly (`print_main_report`).
- `experiments/phase3_crossmodel/score_crossmodel.py` — reuses `span_matching.best_match` to re-score Phase 3's subtype data at span level (strict + token) instead of the original verse-level check.

---

## 4. Actual token usage and cost per call / per poem, by model (from past run manifests)

**Phase 1 (frozen TEST + the 2-run v4_combined DEV dirs)** — averages computed from `run_manifest.json` files under `results/pilot_3models/test_final/**` and `results/pilot_3models/dev_variants/v4_combined/**` (one API call = one full poem, all 4 elements, all verses):

| Poem (n_verses) | Provider | avg input tokens/call | avg output tokens/call | cost/call | cost/verse |
|---|---|---|---|---|---|
| Imru1 (81) | anthropic (Claude Sonnet 4.6, $3/$15 per MTok) | 9,494 | 7,910 | $0.1471 | $0.00182 |
| Imru1 (81) | openai (GPT-5.4-mini, $0.75/$4.50) | 6,525 | 5,108 | $0.0279 | $0.00034 |
| Imru1 (81) | google (Gemini 3.5 Flash, $1.50/$9.00) | 6,176 | 6,314 | $0.0661 | $0.00082 |
| Jarir (40) | anthropic | 5,090 | 3,541 | $0.0684 | $0.00171 |
| Jarir (40) | openai | 3,514 | 2,542 | $0.0141 | $0.00035 |
| Jarir (40) | google | 3,499 | 3,283 | $0.0348 | $0.00087 |
| Abu_Tammam (30) | anthropic | 4,941 | 3,287 | $0.0641 | $0.00214 |
| Abu_Tammam (30) | openai | 3,413 | 1,859 | $0.0109 | $0.00036 |
| Abu_Tammam (30) | google | 3,360 | 2,612 | $0.0285 | $0.00095 |
| Imru2 (23) | anthropic | 4,900 | 2,175 | $0.0473 | $0.00206 |
| Imru2 (23) | openai | 3,460 | 1,486 | $0.0093 | $0.00040 |
| Imru2 (23) | google | 3,380 | 1,803 | $0.0213 | $0.00093 |
| Nabigha (50) | anthropic | 5,868 | 4,498 | $0.0851 | $0.00170 |
| Nabigha (50) | openai | 3,962 | 2,333 | $0.0135 | $0.00027 |
| Nabigha (50) | google | 4,030 | 3,946 | $0.0416 | $0.00083 |

Across all 5 poems (pooled): anthropic avg ≈6,227 in / 4,518 out per call; openai avg ≈4,290 in / 2,854 out; google avg ≈4,185 in / 3,771 out. Pricing (`experiments/pilot_3models/config.py:MODELS`): Claude Sonnet 4.6 $3.00/$15.00, GPT-5.4-mini $0.75/$4.50, Gemini 3.5 Flash $1.50/$9.00 per MTok.

**Phase 2 — Fable 5 (Claude Fable 5, $10/$50 per MTok, from `experiments/phase2_chatlike/phase2_config.py`)**, from `results/phase2_chatlike/config_a/{Imru2,Nabigha}/run_manifest.json`:

| Poem | avg input tokens/call | avg output tokens/call | cost/call |
|---|---|---|---|
| Imru2 (23 verses, whole-poem) | 5,532 | 4,970 | $0.3038 |
| Nabigha (50 verses, whole-poem) | 6,550 | 11,694 | $0.6502 |

**Phase 2 — Config B (Sonnet 4.6, terminology-corrected prompt)**, `results/phase2_chatlike/config_b/{Imru2,Nabigha}/run_manifest.json`:

| Poem | avg input tokens/call | avg output tokens/call | cost/call |
|---|---|---|---|
| Imru2 | 5,272 | 2,193 | $0.0487 |
| Nabigha | 6,240 | 4,470 | $0.0858 |

**Phase 2 — Config C (two-stage: Fable 5 free-form reasoning per verse + GPT-5.4-mini strict-JSON extraction per verse)**, `results/phase2_chatlike/config_c/Imru2/run_manifest.json` — aggregated per-run (23 verses × 2 stages = 46 calls per run):

| Run | stage1 (Fable5) in/out | stage2 (GPT-5.4-mini) in/out | run cost (computed) |
|---|---|---|---|
| run1 | 56,325 / 39,306 | 25,942 / 2,461 | ≈$2.56 |
| run2 | 56,325 / 38,030 | 25,409 / 2,374 | ≈$2.50 |

Matches the project's own cited total: "$5.05" for Config C on Imru2 (`PROJECT_STATE.md` Phase 2 §3i). Per-verse cost on this design ≈$0.111/verse for one run (23 verses) — roughly 50-100× Phase 1's whole-poem-call per-verse cost, because the system prompt (and, in Config C, a full free-form reasoning stage) is resent on every single verse rather than once per poem.

**No prompt-caching is implemented anywhere** in `providers.py` or `providers_v2.py` — every call resends the full system message (element definitions + all examples) from scratch. This is the direct cause of per-verse/per-call-granularity experiments (Config C, §3g's per-verse Mode A/B) costing 4–100× more per unit of accuracy than whole-poem batching (`PROJECT_STATE.md` §3g item 4's F1-per-dollar table).

---

## 5. Poets and poems in the 5-poem corpus

From `experiments/pilot_3models/config.py:POEMS`:

| Poem key | Poet | Title | Verses | Split |
|---|---|---|---|---|
| Imru1 | امرؤ القيس (Imru' al-Qais) | قصيدة رقم 1 (the Mu'allaqa) | 81 | TEST |
| Imru2 | امرؤ القيس (Imru' al-Qais) | قصيدة رقم 8 | 23 | DEV |
| Nabigha | النابغة الذبياني (Al-Nabigha Al-Dhubyani) | — | 50 | DEV |
| Jarir | جرير (Jarir) | — | 40 | TEST |
| Abu_Tammam | أبو تمام (Abu Tammam) | — | 30 | TEST |

**4 distinct poets, 5 poems**: Imru' al-Qais contributes 2 poems (Imru1, Imru2 — split across TEST and DEV respectively), each of the other 3 poets (Al-Nabigha, Jarir, Abu Tammam) contributes exactly 1 poem. Total 224 verses across the corpus. (Phase 2 §6 already examined whether same-poet pairing predicts performance — "no clear poet-consistency effect," confounded with the DEV/TEST split since Imru2 is DEV and Imru1 is TEST.)

---

## 6. Existing support for running on many poems (batching, caching, resume logic)

- **"Batching" in this project means whole-poem-per-call, not an API batch endpoint** — `run_pilot.run(poem_key, n_runs, ...)` (`experiments/pilot_3models/run_pilot.py`) sends one API call per (provider, run) covering every verse of one poem in a single system+user message; there is no literal provider-side batch API usage anywhere in the codebase.
- **No cross-call caching** (no prompt caching, no response memoization) — confirmed by reading `providers.py`/`providers_v2.py`: every call reconstructs and resends the full system message.
- **Resume/retry logic exists at the manifest level**, in two places:
  - `run_pilot.run(..., run_indices=None)` — pass e.g. `run_indices=[2]` to add a single new run to a directory that already has run1 data, without re-running or overwriting it; the manifest is *extended*, not replaced, when it already exists (`run_pilot.py:28-44`).
  - `run_per_verse.py`'s `_run_one_cell()` supports a `providers` filter (`--providers` CLI flag) to retry just one provider's cell without re-spending on providers that already succeeded, and retrying an already-attempted `(provider, run_index)` cell **replaces** its existing manifest record rather than appending a duplicate (`run_per_verse.py:56-62, 132-136`) — this convention was specifically added to support the Anthropic-credit-balance retry described in `PROJECT_STATE.md` §3g.
  - `run_per_verse.py` also deliberately keeps a per-cell manifest `error` field at `None` even when some individual verses within that cell failed (logging those failures separately in a `verse_errors` list) — a fix for a real bug where a partial per-verse failure used to zero out an entire run's good data in the shared `analyze.py` loaders (documented at length in `PROJECT_STATE.md` §3g and §6.8).
  - `run_decompose.py` and `run_test.py` are one-off scripts built the same way (call `run_pilot.run()` per experiment batch) — not designed for repeated/parametrized re-use beyond their original one-time run.
- **No poem-batching loop exists today** (e.g. "run this prompt over N poems in one command") — every runner takes a single `poem_key` (or, for Config C, is Imru2-specific) and is invoked once per poem; extending to "many poems" would currently mean calling the existing single-poem entry points in a loop, which the manifest-append/replace semantics above would support cleanly, but no such wrapper currently exists in the repo.

---

## Sources consulted

`CLAUDE.md`, `PROJECT_STATE.md`, `NEW_SESSION_HANDOFF.md`, `GLOSSARY.md`, `docs/phase4/SESSION_LOG.md`,
`experiments/pilot_3models/{config,prompts,ground_truth,span_matching,span_scoring,analyze,providers,run_pilot,run_per_verse}.py`,
`experiments/phase2_chatlike/{phase2_config,providers_v2}.py`, `experiments/phase2_chatlike/PROPOSAL_fewshot.md`,
`data/elements/{Trope,Kenning}.txt`, `results/phase2_chatlike/example_gap_analysis.md`,
`results/phase3_subelements/MEETING_SUMMARY.md`, `results/phase3_crossmodel/summary.md`,
`results/pilot_3models/test_final/**/run_manifest.json`, `results/pilot_3models/dev_variants/v4_combined/**/run_manifest.json`,
`results/phase2_chatlike/{config_a,config_b,config_c}/**/run_manifest.json` (token/cost tables computed by a local read-only script, no API calls).
