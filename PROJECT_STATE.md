# Project State — Handoff Document

**Purpose**: single source of truth for a fresh session to continue this work with zero prior context. If anything here conflicts with your memory of a past conversation, trust this file and the files it points to — not the conversation.

**STATUS: PHASE 1 EXPERIMENTAL PHASE CLOSED — 2026-07-21. PHASE 2 (v2) OPENED — 2026-07-23.** Everything in §1-§7 below is Phase 1: frozen, historical, and untouched — no further API calls, experiments, or changes to any Phase 1 number are planned, and Phase 1 documents/reports keep their original (now-superseded) terminology (see Phase 2 §0 below). Phase 2 is a new, distinct experimental cycle opened in response to a supervisor terminology correction and a chat-interface observation that Phase 1's pipeline missed a real كناية instance — see the **Phase 2** section after §7 for full rationale, terminology corrections, and the §3i (Phase 2) experiment. Thesis writing (`/writing/chapters/`) continues to draw from Phase 1's frozen numbers for everything Phase 1 covered; Phase 2 findings get their own subsections once results exist.

**Last updated**: 2026-07-26 (analysis-only session: supervisor notes logged in Phase 2 §5 Entry 2; four deliverables + one new methodology finding in Phase 2 §7).

---

## 1. Project status — what's done

This thesis ("Exploring the Potential of LLMs to Identify Challenging Rhetorical Elements") studies 4 rhetorical elements in classical Arabic poetry: **kenning (كناية), trope (مجاز), antonymy (طباق), simile (تشبيه)**. Prior phases (FirstStep–Forth_Step, `previous_steps/`) are documented in [`THESIS_KNOWLEDGE.md`](THESIS_KNOWLEDGE.md) (full project history/inventory) and [`ENHANCEMENT_PLAN.md`](ENHANCEMENT_PLAN.md) (prioritized roadmap) — read those first for anything predating this pilot cycle. This document covers only the **3-model pilot experiment cycle** built on top of that foundation.

| Milestone | Status | Key output |
|---|---|---|
| Repo reorganization (Phase 2) | Done | `/archive`, `/data`, `/experiments`, `/results`, `/writing`, `/literature`, root `README.md` |
| Single-poem 3-model pilot (Claude/GPT/Gemini, Imru2) | Done | [`results/pilot_3models/pilot_report.md`](results/pilot_3models/pilot_report.md) + `.docx` version |
| Ground-truth audit (all 5 annotated poems) | Done | `experiments/pilot_3models/audit_ground_truth.py` (run it to reproduce) |
| Ensemble-uselessness check | Done | `experiments/pilot_3models/ensemble_check.py` |
| Span-level scoring harness (fixes verse-level scoring artifacts) | Done | `experiments/pilot_3models/span_matching.py`, `span_scoring.py` |
| DEV/TEST split defined + confirmed | Done | `config.py`: `DEV_POEMS`, `TEST_POEMS` |
| DEV error analysis (Imru2 + Nabigha, subtype-level) | Done | reproducible via `test_report.py`-style subtype breakdown, was run ad hoc on DEV in-session |
| 4 prompt variants designed + run on DEV | Done | `experiments/pilot_3models/prompt_variants.py`, results in `results/pilot_3models/dev_variants/{v1_boundary,v2_marker_independence,v3_multi_figure,v4_combined}/` |
| 2 ablation variants (v1+v2, v1+v3) + v1 2nd-run consistency check | Done | `results/pilot_3models/dev_variants/{v1_v2,v1_v3}/`, `run_ablations.py` |
| **Frozen TEST run**: baseline vs v4_combined | **Done — TEST is spent** | `results/pilot_3models/test_final/{baseline,v4_combined}/{Imru1,Jarir,Abu_Tammam}/` |
| Final TEST report | Done | reproducible via `experiments/pilot_3models/test_report.py`; exact numbers also captured in §3 below |
| Per-element decomposition experiment (DEV only, supplementary) | Done — result is negative/mixed, see §3f | `experiments/pilot_3models/decompose_prompts.py`, `run_decompose.py`, `decompose_report.py`; data in `results/pilot_3models/dev_variants/decomposed_{Trope,Simile,Kenning,Antonymy}/` + a 2nd run added to `dev_variants/v4_combined/` |
| Per-verse granularity experiment (Imru2 only, supplementary) | Done — mixed/negative, see §3g | `experiments/pilot_3models/per_verse_prompts.py`, `run_per_verse.py`, `per_verse_report.py`; data in `results/pilot_3models/per_verse/{mode_a,mode_b_Trope,mode_b_Simile,mode_b_Kenning,mode_b_Antonymy}/Imru2/` |
| Nabigha Kenning-replication follow-up (Mode A only) | **Done — all 3 models**, see §3g addendum | `results/pilot_3models/per_verse/mode_a/Nabigha/` |
| Supervisor deliverable: verse-by-verse detailed results (5 poems) | Done, see §3i | `results/pilot_3models/detailed_results.docx` |
| Supervisor deliverable: explanation-augmented illustrative sample | Done, see §3i | `results/pilot_3models/explanations_sample.docx` |
| Repository closure: secret scan, duplicate-dir cleanup, commits, `REPRODUCIBILITY.md` | Done | see §7 |

**Total actual API spend across the whole pilot cycle: $8.29** across **1,134 individual API calls** (180 manifest records). Breakdown by stage: original single-poem pilot $0.15, DEV Nabigha baseline $0.14, DEV prompt-variant tuning (v1-v4 + ablations) $1.72, per-element decomposition (§3f) $0.67, frozen TEST run $1.85, per-verse granularity grid + Nabigha replication + Anthropic retry (§3g) $3.64, explanation-augmented sample (§3i) $0.13. Figures are computed programmatically from every `run_manifest.json` under `results/pilot_3models/` (`experiments/pilot_3models/build_final_report.py:build_cost_table`) — not hand-summed. All code and results are now committed to git (commits `13a85e5`, `a68e1b2`, `db23ccb` — see §7 for the full commit log and one labeling caveat).

**Per-experiment index** (one line each; see the linked subsection for detail):
- §3a — Frozen TEST: baseline vs v4_combined, 3 models, 3 poems. **v4_combined wins for Trope/Simile/Antonymy; Kenning barely moves.** These are the thesis's primary numbers.
- §3b — Run-consistency on TEST: 88-100% baseline, 89-100% v4_combined; Gemini's Kenning consistency is the one notable dip.
- §3c — Trope subtype breakdown: DEV had flagged the wrong subtype as hardest; TEST-scale data reversed that conclusion.
- §3d — Antonymy over-claiming: all 3 models' false positives exceed true positives at baseline; invisible on DEV's thin n=5.
- §3e — Ensemble check: majority-vote-across-models gives no improvement over the best single model; sometimes worse.
- §3f — Per-element decomposition (DEV, supplementary): negative/mixed — Kenning got worse for 2 of 3 models.
- §3g — Per-verse granularity grid + Nabigha replication (DEV, supplementary): mixed — real, cross-poem-replicated Kenning gain for 2 of 3 models, but small in absolute terms and 4-8x more expensive per unit of F1 than the adopted method.
- §3i — Supervisor deliverables (detailed verse-by-verse results; explanation-augmented sample): no new findings against frozen numbers, but the explanation-sample run surfaced a justification-seeking effect (every decision flip went absent→present, zero the other way).
- §3j — Original single-poem pilot: superseded, kept for history only.

---

## 2. Frozen decisions — MUST NOT be violated

1. **DEV = Imru2 + Nabigha. TEST = Imru1 + Jarir + Abu_Tammam.** Defined in `experiments/pilot_3models/config.py` (`DEV_POEMS`, `TEST_POEMS`). All prompt iteration happened on DEV only.
2. **TEST is SPENT.** The baseline-vs-v4_combined numbers in `results/pilot_3models/test_final/` (reproduced exactly in §3 below) **are the final thesis numbers**. Do not re-run, re-score with a new prompt variant, or "just check one more thing" against Imru1/Jarir/Abu_Tammam. If a new prompt idea comes up, it gets evaluated on DEV as a *supplementary* experiment (see §5a) — it does not get to touch TEST again, and it does not retroactively change the frozen numbers.
3. **v4_combined is the selected prompt, for all 3 models** (no per-model prompt — DEV evidence for splitting by model turned out to be noise, see §6). Defined in `experiments/pilot_3models/prompt_variants.py` as `VARIANTS["v4_combined"]` — the baseline system message plus all 3 added rule blocks (`RULE_1_BOUNDARY`, `RULE_2_MARKER_INDEPENDENCE`, `RULE_3_MULTI_FIGURE`).
4. **Scoring = span-level harness, both strict and token-overlap criteria, 2-run majority as the primary metric.** Never go back to pure verse-level exists/not-exists scoring (see §6 for why — it produces artifacts, especially for Kenning). Single-run numbers may be shown for transparency but are never the reported/primary number when 2 runs exist.

---

## 3. Key findings — actual numbers

### 3a. TEST results (frozen thesis numbers): baseline vs v4_combined, 2-run majority, strict criterion

Ground truth support on TEST (deduplicated instance counts, from `ground_truth.load_ground_truth_spans`): **Trope=179, Simile=52, Kenning=147, Antonymy=43** (pooled across Imru1+Jarir+Abu_Tammam). Note: earlier back-of-envelope estimates during planning cited "~181/55/150/47" — those were pre-deduplication; **179/52/147/43 are the real, deduped counts actually used for scoring.**

| Element | Model | Baseline TP/FP/FN | Baseline F1 | v4 TP/FP/FN | v4 F1 | Δ |
|---|---|---|---|---|---|---|
| **Trope** | Claude Sonnet 4.6 | 17/3/162 | 0.171 | 25/3/154 | 0.242 | +42% |
| Trope | GPT-5.4-mini | 6/1/173 | 0.065 | 28/16/151 | 0.251 | **+286%** |
| Trope | Gemini 3.5 Flash | 34/4/145 | 0.313 | 45/9/134 | 0.386 | +23% |
| **Kenning** | Claude Sonnet 4.6 | 8/2/139 | 0.102 | 8/6/139 | 0.099 | ~flat (tiny regression) |
| Kenning | GPT-5.4-mini | 1/4/146 | 0.013 | 4/7/143 | 0.051 | +0.038 (4x, still tiny) |
| Kenning | Gemini 3.5 Flash | 9/4/138 | 0.113 | 15/8/132 | 0.176 | +56% |
| **Simile** | Claude Sonnet 4.6 | 28/6/24 | 0.651 | 28/6/24 | 0.651 | flat |
| Simile | GPT-5.4-mini | 30/4/22 | 0.698 | 31/3/21 | 0.721 | +3% |
| Simile | Gemini 3.5 Flash | 32/7/20 | 0.703 | 32/4/20 | 0.727 | +3% |
| **Antonymy** | Claude Sonnet 4.6 | 5/14/38 | 0.161 | 6/12/37 | 0.197 | +22% |
| Antonymy | GPT-5.4-mini | 4/11/39 | 0.138 | 5/17/38 | 0.154 | +12% |
| Antonymy | Gemini 3.5 Flash | 4/19/39 | 0.121 | 5/21/38 | 0.145 | +20% |

**Token-overlap criterion** tells the same Trope/Simile/Kenning story but reveals a much bigger baseline-to-v4 gap for **Antonymy** (word-form variation matters a lot there): baseline token F1 = 0.419/0.345/0.545 (Claude/GPT/Gemini), v4 token F1 = 0.393/0.431/0.609. Full strict+token table, both prompts, all elements: reproduce with `python experiments/pilot_3models/test_report.py` (function `print_main_report`).

### 3b. Run-to-run consistency (decision-level agreement, pooled TEST, out of 151 verse-element checks per element unless noted)

| | Trope | Simile | Kenning | Antonymy |
|---|---|---|---|---|
| baseline: Claude / GPT / Gemini | 98% / 88% / **100%** | 99% / 96% / 100% | 99% / 95% / 100% | 99% / 93% / 100% |
| v4: Claude / GPT / Gemini | 95% / 89% / 97% | 100% / 98% / 99% | 91% / 98% / 89% | 95% / 95% / 96% |

Gemini's baseline was perfectly deterministic on TEST; v4's added rules cost some of that (down to 89-97%) — a reasonable trade for the recall gains above.

### 3c. Trope false-negative breakdown by ground-truth subtype (pooled across 3 models, TEST) — the DEV→TEST reversal

| Subtype | n | Baseline missed | v4 missed |
|---|---|---|---|
| استعارة فعل (verbal metaphor) | 76 | 83% | **62%** |
| مجاز عقلي (rational trope) | 41 | 83% | **66%** |
| **استعارة تمثيلية** (unmarked whole-clause allegory) | 24 | **33%** | **29%** |
| استعارة قديمة (archaic/lexicalized) | 15 | 80% | 60% |
| **مجاز مرسل** (metonymy, single lexicalized word) | 13 | 85% | **85% — unchanged** |
| استعارة حديثة | 4 | 75% | 75% — unchanged |

**Important, counterintuitive finding**: the 2-poem DEV analysis (Imru2+Nabigha) had flagged استعارة تمثيلية (unmarked whole-clause metaphor, no lexical marker) as the hardest/most concerning Trope subtype. **At TEST scale (3 poems, larger n), that hypothesis did not hold up** — استعارة تمثيلية turned out to be the *easiest* subtype both before and after v4 (33%→29% missed), while مجاز مرسل (single lexicalized/archaic-word metonymy, e.g. "nose"→redness) is the subtype v4 does **nothing** for (85%→85%, completely flat). v4's real, validated wins are استعارة فعل and مجاز عقلي — both were correctly predicted from the DEV Nabigha analysis. **Lesson**: small-sample DEV subtype analysis can point at the wrong culprit; always re-check subtype breakdown at TEST scale before trusting a DEV-derived narrative.

### 3d. Antonymy over-claiming (first real evaluation at n=43, was too thin on DEV to trust — n=5 there)

All 3 models systematically over-claim Antonymy — false positives exceed true positives at baseline for every model (e.g. Claude baseline: TP=5, FP=14 → precision only 0.263 strict). This is a new finding only visible once TEST gave enough Antonymy support to evaluate honestly.

### 3e. Ensemble (majority-vote-across-3-models) is useless here

Computed once, on the original Imru2 pilot data, no new API calls (`experiments/pilot_3models/ensemble_check.py`): Trope F1=0.222, Kenning F1=0.167 — **identical to the best single model**, because all 3 models miss the *same* instances (systematic gap, not independent noise ensembling could average out). Simile ensemble F1=0.667, actually *worse* than GPT-5.4-mini alone (0.769) since ensembling trades recall gain for precision loss. **Do not assume a multi-model panel improves recall on the hard elements — verified false for this task.**

### 3f. Per-element decomposition experiment (DEV only, supplementary — item 5a, now closed)

Tested whether splitting v4_combined into 4 single-element prompts (each call only sees 1 element's definition + only the v4 rule content specific to that element, rewritten one-directionally where it used to be comparative — see `decompose_prompts.py` docstring) improves detection, especially for Kenning. Both sides scored 2-run majority, pooled DEV (Imru2+Nabigha), strict criterion unless noted. GT support (pooled DEV): Trope n=60, Kenning n=69, Simile n=20, Antonymy n=5.

| Element | Model | v4_combined TP/FP/FN | v4 F1 | Decomposed TP/FP/FN | Dec. F1 | Run-agree (v4→dec.) |
|---|---|---|---|---|---|---|
| **Kenning** | Claude Sonnet 4.6 | 5/3/64 | 0.130 | 8/7/61 | 0.190 | 89%→95% |
| Kenning | GPT-5.4-mini | 7/8/62 | 0.167 | 4/0/65 | **0.110 (worse)** | 98%→**82% (worse)** |
| Kenning | Gemini 3.5 Flash | 10/3/59 | **0.244** | 7/5/62 | **0.173 (worse)** | 95%→96% |
| Trope | Claude Sonnet 4.6 | 2/6/58 | 0.059 | 4/6/56 | 0.114 | 93%→97% |
| Trope | GPT-5.4-mini | 6/9/54 | 0.160 | 6/14/54 | 0.150 (token: 0.175) | 77%→**93%** |
| Trope | Gemini 3.5 Flash | 5/5/55 | 0.143 | 7/6/53 | 0.192 | 82%→85% |
| Simile | Claude Sonnet 4.6 | 14/7/6 | 0.683 | 15/7/5 | 0.714 | 99%→99% |
| Simile | GPT-5.4-mini | 13/7/7 | 0.650 | 16/7/4 | 0.744 | 96%→99% |
| Simile | Gemini 3.5 Flash | 13/7/7 | 0.650 | 12/7/8 | 0.615 | 96%→93% |
| Antonymy (n=5, too thin — noise) | all 3 | — | — | — | — | — |

**Kenning (the motivating target): mixed, not a win.** Only Claude improved (F1 +0.06, but by trading precision for recall — P dropped 0.62→0.53 as R roughly doubled 0.07→0.12). GPT and Gemini both got *worse*: Gemini's F1 dropped from the best-in-class 0.244 to 0.173, and GPT's Kenning collapsed to near-total abstention (TP+FP went from 15 calls down to just 4, precision hit a hollow 1.00 while recall nearly halved) *and* became notably less run-to-run consistent (98%→82% agreement, the opposite of what isolation was supposed to buy). **This does not support the task-interference hypothesis for Kenning** — 2 of 3 models got worse, not better, when Kenning was the model's only job.

**Trope held up better than the "loses contrastive context" concern predicted.** 2 of 3 models improved (Claude nearly doubled its F1, Gemini +34%), GPT was roughly flat (strict F1 slightly down 0.160→0.150, token F1 slightly up 0.160→0.175 — precision cost, recall unchanged). The clearest decomposition effect turned out to be on **run-to-run consistency**, not accuracy: all 3 models' Trope agreement rate rose, GPT's dramatically (77%→93%). The one-directional adaptation of the boundary rule (no longer showing the model Kenning's contrasting definition) did not visibly cost Trope anything.

**Simile and Antonymy ("baseline alone, isolated") moved even though no new rule was added for them.** Simile: 2/3 models improved (GPT notably, 0.650→0.744; Claude slightly; Gemini slightly worse), on a small base (n=20) — plausibly an attention/focus effect from not sharing the call with 3 other elements, but the swings are only 1-3 instances so treat as suggestive, not conclusive. Antonymy (n=5) is too thin to read anything into either direction, consistent with the existing §3d caveat.

**Verdict: decomposition does not earn a place as a recommended thesis approach, at least not on this evidence.** The element it was designed to help (Kenning) got *worse* for 2 of 3 models, and none of the deltas anywhere are large relative to their small denominators (Kenning n=69, Simile n=20, Antonymy n=5) even after 2-run majority voting — several could still be run-to-run noise despite the majority vote. Combined with the ~1.75x API cost of 4 calls per poem instead of 1, decomposition is reportable as a **negative/mixed supplementary finding that argues against a simple task-interference story for Kenning**, not as a technique to adopt or to spend a fresh held-out poem validating. The one genuinely interesting side-finding — decomposition consistently raising run-to-run determinism for Trope, independent of whether accuracy moved — is worth a footnote/future-work mention but doesn't change the primary TEST numbers or the v4_combined recommendation in §2.3.

### 3g. Per-verse granularity experiment (Imru2 only, supplementary — NEW, completes the 2x2 grid)

Completes the granularity x decomposition grid: whole-poem x all-4 (v4_combined) and whole-poem x single-element (decomposed) were already done (§3f); this adds **per-verse x all-4** (Mode A: v4_combined content, one API call per verse, minimally adapted instructions) and **per-verse x single-element** (Mode B: §3f's decomposed prompts reused verbatim, one call per verse per element). Imru2 only (23 verses), not extended to Nabigha. All 4 cells scored 2-run majority, both strict and token criteria. **All existing v4_combined/decomposed numbers below are re-sliced to Imru2 ONLY** (not the pooled-DEV numbers in §3f) for a fair apples-to-apples comparison.

**Imru2-only ground-truth support (deduped, verified via `ground_truth.load_ground_truth_spans`): Trope=8, Simile=5, Kenning=17, Antonymy=1.** (Note: these are the real counts used for scoring — Simile and Kenning are 1 lower than the back-of-envelope 6/18 cited when this experiment was scoped.) **These are extremely small denominators — every finding below is suggestive, not conclusive, especially Antonymy (n=1) and Simile (n=5).**

One real API error occurred: Claude/Antonymy/run2/verse23 failed with "credit balance too low" (a billing-side issue, not a bug). Verse 23 has zero Antonymy ground truth, so it has no scoring impact — the majority vote for that one verse falls back to run1 alone. **Bug found and fixed during this run**: the per-verse runner initially wrote a non-null `error` string on the whole manifest record whenever *any* single verse-call failed, and the existing harness (`analyze.py`) treats a truthy `error` as "discard this run's data entirely" — which silently zeroed out 22 good verses' worth of real data for that one cell. Fixed in `run_per_verse.py` (manifest `error` now stays `None` for partial per-verse failures; failures are logged informationally in a new `verse_errors` field instead) and the one already-written manifest record was patched in place (no re-run needed, since the raw JSONL text itself was already correct).

**Full grid, strict criterion (TP/FP/FN, F1):**

| Element (n) | Model | Whole+All4 (v4) | Whole+Single (decomp.) | Verse+All4 (Mode A) | Verse+Single (Mode B) |
|---|---|---|---|---|---|
| **Trope (8)** | Claude | 2/0/6, .400 | 2/1/6, .364 | 2/2/6, .333 | **4/3/4, .533** |
| Trope | GPT | 1/0/7, .222 | 1/1/7, .200 | 3/9/5, .300 | 2/3/6, .308 |
| Trope | Gemini | 1/2/7, .182 | 1/2/7, .182 | **3/3/5, .429** | 1/4/7, .154 |
| **Simile (5)** | Claude | 5/5/0, .667 | 5/5/0, .667 | 5/5/0, .667 | 5/5/0, .667 |
| Simile | GPT | 4/5/1, .571 | 5/5/0, .667 | **5/4/0, .714** | 5/5/0, .667 |
| Simile | Gemini | 4/5/1, .571 | 4/5/1, .571 | 5/5/0, .667 | 4/6/1, .533 (token .667) |
| **Kenning (17)** | Claude | 1/0/16, .111 | 1/2/16, .100 (tok .200) | 3/4/14, .250 (tok .333) | 3/6/14, .231 (tok .308) |
| Kenning | GPT | 2/1/15, .200 | 2/0/15, .211 | 2/4/15, .174 (tok .261) | 2/6/15, .160 |
| Kenning | Gemini | 2/2/15, .190 | 1/3/16, .095 (tok .190) | **6/2/11, .480** | 4/4/13, .320 (tok .400) |
| Antonymy (1, noise) | Claude | 0/1/1, .000 (tok 1.0) | 0/2/1, .000 (tok .667) | 0/2/1, .000 (tok .667) | 0/2/1, .000 (tok .667) |
| Antonymy | GPT | 0/1/1, .000 (tok 1.0) | 0/1/1, .000 (tok 1.0) | 0/1/1, .000 (tok 0) | 0/1/1, .000 (tok 0) |
| Antonymy | Gemini | 1/0/0, 1.000 | 0/1/1, .000 (tok 1.0) | 0/3/1, .000 (tok .5) | 0/3/1, .000 (tok .5) |

Run-agreement (out of 22-23 checks; unaffected/near-ceiling cells omitted): Trope Claude 22/23→21/23→**23/23**→**23/23**; Trope GPT 17/22→21/23→21/23→21/23; Trope Gemini 23/23→23/23→21/23→20/23 (down); Kenning Gemini 23/23→23/23→21/23→21/23 (down); Simile/Antonymy mostly flat at or near ceiling throughout.

**Answers to the 4 analysis questions:**

1. **Verse isolation (losing poem context): net positive for Trope and Kenning, not just noise in one direction.** Whole→verse (v4→Mode A): Trope improves for 2/3 models (GPT +35%, Gemini +136%; Claude -17%); Kenning improves for all 3 models when also comparing decomposed→Mode B lines, and Mode A alone lifts Kenning for 2/3 models sharply (Gemini .190→.480, Claude .111→.250; GPT roughly flat/-13%). This argues against "losing context always hurts figurative/indirect readings" — if anything, fewer competing verses in-context seems to help the model focus on Kenning's subtle plausible-literal-reading test and Trope's non-literal-verb cases. The gain consistently comes with a recall-for-precision trade (FP counts rise alongside TP), the same pattern seen in §3f.

2. **Mode B vs Mode A does NOT cleanly mirror the whole-poem decomposition-vs-v4 pattern — granularity and element-isolation are largely independent, and don't stack.** At per-verse granularity, decomposing further (Mode A → Mode B) makes Kenning *worse* for all 3 models (Claude .250→.231, GPT .174→.160, Gemini .480→.320) — the same negative direction §3f found for whole-poem decomposition, so that part replicates. But Trope's Mode A→B move is mixed in a new way: Claude and GPT improve (as whole-poem decomposition also showed), while Gemini drops sharply (.429→.154) — the opposite of what whole-poem decomposition did to Gemini's Trope (flat, .182→.182). Gemini's big verse-isolation gain (Mode A) evaporates once the element is ALSO isolated, suggesting Gemini's gain was about general decluttering, not about Trope specifically — and stacking the two interventions can cancel out rather than compound.

3. **Per-verse calls are not more run-deterministic in general — it's model-dependent, and Gemini gets *less* deterministic.** Claude and GPT's agreement rates are flat-to-slightly-up moving to per-verse (e.g. Trope Claude 22/23→23/23, GPT 17/22→21/23). Gemini trends the other way on both Trope (23/23→21/23→20/23) and Kenning (23/23→21/23), consistent with the existing pitfall (§6.2) that Gemini specifically has unstable Kenning behavior — that instability now also shows up on Trope once verses are isolated. With 22-23 already-high-agreement checks per cell, there wasn't much room to move either way, and no model shows the "23 independent chances to flip" degradation pattern except Gemini.

4. **F1-per-dollar: whole-poem batching is ~4-8x more cost-efficient than per-verse calls, because the system prompt is re-sent on every call.** Using support-weighted (micro) F1 across all 12 element x model cells (accounts for Kenning's larger n=17 dominating vs Antonymy's n=1):

   | Cell | Micro F1 (strict) | Real cost (Imru2, 2 runs, 3 models) | F1 per dollar |
   |---|---|---|---|
   | Whole+All4 (v4_combined) | 0.333 | $0.156 | **2.14** |
   | Whole+Single (decomposed) | 0.308 | $0.243 | 1.27 |
   | Verse+All4 (Mode A) | **0.398 (best accuracy)** | $0.804 | 0.50 |
   | Verse+Single (Mode B) | 0.351 | $1.128 | 0.31 (worst value) |

   Verse+All4 (Mode A) is actually the highest-*accuracy* cell of the four (driven mostly by Kenning's TP roughly doubling), but at ~5x the whole-poem cell's price for a ~19% relative F1 gain — a bad trade in $/F1 terms. Mode B is worse than Mode A on both accuracy and cost, the worst cell on the whole grid.

**Verdict: the signal is not strong enough to justify spending on Nabigha for this grid.** The most interesting result — Kenning's accuracy roughly doubling under per-verse-all-4 calls (Mode A) — is real in direction across all 3 models, but built on a single poem's n=17 instances, doesn't survive being combined with element-isolation (Mode B), and costs 5x more per unit of accuracy than the already-adopted v4_combined whole-poem approach. Recommendation: **do not extend the full 2x2 per-verse grid to Nabigha.** The one narrow thread worth a cheap, targeted follow-up if there's appetite — not a full-grid ask — would be Kenning-only, Mode-A-only on Nabigha (~$0.05-0.10, similar order to a single decomposed-element run) to see if the per-verse recall gain for Kenning replicates on a second poem; everything else in this grid (Trope's mixed direction, Simile/Antonymy's near-total insensitivity to granularity, the cost multiplier) argues for keeping v4_combined whole-poem as the thesis's primary method and treating this experiment as a reportable negative/mixed supplementary finding, same as §3f.

**(Historical note: this verdict was written before the Nabigha follow-up below existed. The follow-up's actual result — direction replicates for 2/3 models, magnitude doesn't — is more nuanced than "negative/mixed"; read the follow-up section immediately below for the corrected picture, not this paragraph alone.)**

**Nabigha replication follow-up (2026-07-21, user-requested, corrects the cost estimate above):** the true cost of a faithful Mode A replication (all 4 elements per call, matching the mechanism that produced Imru2's gain, not the cheaper single-element decomposed prompt) was recalibrated at **~$1.75** for 300 calls (50 verses x 3 models x 2 runs), not the ~$0.05-0.10 quoted above — that earlier estimate wrongly compared against a single decomposed-element's Imru2 cost without accounting for Nabigha's 2.2x verse count or Mode A's 4-element-per-call scope. User approved the corrected $1.75 estimate and the run proceeded.

**Anthropic retry completed 2026-07-21** (credits confirmed live by the user; 100 calls, both runs 0 errors, ~$1.11 — `run_per_verse.py` was extended with a `--providers` filter and safe replace-not-append manifest semantics specifically to support a single-provider retry without re-spending on OpenAI/Gemini, which had already succeeded).

**Correction to an arithmetic error**: Gemini's Imru2 Kenning delta was mis-stated as "+136%" in the first version of this section (and in chat) — the correct figure, recomputed programmatically from the stored TP/FP/FN, is **+152%** (0.190→0.480). Fixed below and in `results/pilot_3models/final_report.docx`.

**Result with all 3 models present: the *direction* replicates for 2 of 3 models, but the *magnitude* does not — and the story is more nuanced than the GPT+Gemini-only preliminary read suggested.** Nabigha Kenning GT support: n=52. Whole-poem (v4_combined) -> per-verse (Mode A) Kenning F1, same poem, both poems shown for direct comparison:

| Model | Imru2: whole→verse F1 (Δ) | Nabigha: whole→verse F1 (Δ) |
|---|---|---|
| Claude Sonnet 4.6 | 0.111→0.250 (+125%) | 0.136→0.338 (**+149%**) |
| GPT-5.4-mini | 0.200→0.174 (-13%) | 0.156→0.143 (-9%) |
| Gemini 3.5 Flash | 0.190→0.480 (+152%) | 0.262→0.290 (+11%) |

Gemini's dramatic Imru2 gain (+152%) shrank to +11% on Nabigha — the single-poem-optimism this check was designed to catch. **But Claude's gain did the opposite of shrinking: +125% on Imru2, +149% on Nabigha — as large or larger the second time**, which was not visible in the GPT+Gemini-only preliminary version of this section (written while Claude's retry was still pending on the user's Anthropic billing issue) and changes the conclusion. GPT is the one model with a consistent story across both poems: flat-to-negative, never benefiting from per-verse calling.

**Revised verdict**: per-verse Mode A produces a real, cross-poem-replicated Kenning improvement for 2 of 3 models (Claude, Gemini) — this is a genuine positive finding, not purely an artifact of one lucky poem, and the earlier framing of this experiment as fully negative was premature (written before Claude's data existed). What does *not* replicate is the *size* of any one model's gain — no specific percentage from a single poem should be quoted as if it generalizes, which is exactly the lesson worth keeping (see §6.9, revised accordingly). What still argues against adopting per-verse Mode A as a technique: absolute Kenning F1 even at its best (Claude 0.338, Gemini 0.290 on Nabigha) remains far below Simile's ~0.65-0.7 ceiling, it costs 4-8x more per unit of F1 than whole-poem batching, and one of three models never benefits from it on either poem.

### 3i. Supervisor deliverables: verse-by-verse detailed results + explanation-augmented illustrative sample (2026-07-21)

Two documents built in response to the supervisor wanting to see, per model and per element, *why* a model decided an element exists — one from existing data, one from a small new run.

**`detailed_results.docx`** (`experiments/pilot_3models/build_detailed_results.py`) — built entirely from already-collected v4_combined 2-run-majority data, **zero new API calls**. Covers all 5 poems (TEST first: Imru1, Jarir, Abu_Tammam; then DEV: Imru2, Nabigha), grouped by poem then by element, one row per verse, with ground truth, each model's TP/FP/FN-colored verdict, and its predicted appearance span. Reuses the exact same scoring primitives (`span_scoring.majority_exists_and_appearance`, `span_matching.best_match`) that produce the frozen numbers — this is a per-verse presentation layer over the existing harness, not a new one. **Bug caught and fixed while building it**: Imru1's poem-text file uses doubled quote marks (`""..."" `) unlike the other 4 poems' single quotes, which left stray quote characters in the rendered verse-text column until the parsing regex was generalized to strip any number of quote characters.

**`explanations_sample.docx`** (`experiments/pilot_3models/explanation_prompt.py`, `build_explanations_sample.py`) — Imru2 only, 1 run per model (3 calls, **actual cost $0.13**), v4_combined system message completely unchanged, with a required one-sentence Arabic "reason" field added to the output schema for positive decisions only. Explicitly **not** part of the frozen evaluation (labeled as such prominently in the document) — reasons are reproduced verbatim, no cleanup. A dedicated one-off parser (not `parsing.py`) handles the extended schema, since this data is never scored/majority-voted into the main harness.

**Sanity-check finding, worth carrying into the thesis**: comparing this run's single-run decisions against the existing 2-run-majority v4_combined decision on the same poem (92 verse×element checks per model), decisions flipped for all 3 models (Claude 5/92, GPT 14/92, Gemini 2/92) — and **every single flip went absent→present; zero went the other way, for any model.** Requiring a stated reason never made a model retract an existing positive call; it only generated new ones. This reads as a justification-seeking generative effect rather than a self-correction effect, and is worth flagging as a reason not to assume that an "explain yourself" prompting strategy would improve precision — on this single-poem illustrative sample it only ever moved recall, and not necessarily toward correct positives. This was never run with 2+ runs or scored against ground truth for correctness of the *new* positive calls specifically (only their presence/absence was checked) — flagged as a future-work item in §5.

### 3j. Original single-poem pilot (Imru2 only) — superseded by the above, kept for history

`results/pilot_3models/pilot_report.md`/`.docx` — the very first 3-model comparison, before DEV/TEST existed. Its numbers (e.g. Trope mean F1 0.15) are **not** the frozen thesis numbers — §3a supersedes them. Old-vs-new (verse-level vs span-level) scoring comparison on this same data, reproducible via `experiments/pilot_3models/span_scoring.py`: confirms the fixed harness didn't change Trope's number on this one poem (0.222 both ways) but *worsened* Kenning's apparent score (0.154→0.105) once multi-instance verses were counted correctly — i.e., the harness fix mattered, and mattered differently per element.

---

## 4. Where everything lives

### Code — `experiments/pilot_3models/`
| File | Purpose |
|---|---|
| `config.py` | Poem registry (`POEMS`), `DEV_POEMS`/`TEST_POEMS`, `MODELS` (IDs + pricing), element definitions map |
| `prompts.py` | Baseline system/user message builders |
| `prompt_variants.py` | `VARIANTS` dict — baseline, v1_boundary, v2_marker_independence, v3_multi_figure, v1_v2, v1_v3, v4_combined |
| `providers.py` | Thin per-provider API wrappers (`call_anthropic`, `call_openai`, `call_google`) — instruction-only JSON, no structured-output mode |
| `run_pilot.py` | Core runner: `run(poem_key, n_runs, out_dir, system_message, user_message)` |
| `run_variants.py`, `run_ablations.py`, `run_test.py` | One-off scripts that called `run_pilot.run()` for each experiment batch — kept for reproducibility/reference, not meant to be re-run (would re-spend money and violate §2 if pointed at TEST) |
| `parsing.py` | JSONL response parser; flags malformed lines, never repairs |
| `ground_truth.py` | `load_ground_truth_spans(poem_key)` — loads Dr. Ali Hussein's annotations, maps 53-taxonomy → 4 elements, dedupes |
| `span_matching.py` | `strict_overlap`, `token_overlap_ratio`/`token_match` — the span-level matching primitives |
| `span_scoring.py` | `score_span_level()` — the real scoring function, span-aware, multi-instance-aware |
| `analyze.py` | `load_all_runs()`, `prf1()`, `run_consistency()`, legacy verse-level scoring (superseded, kept for the old-vs-new comparison) |
| `audit_ground_truth.py` | Per-poem/per-element ground-truth instance counts (crude, non-deduped — for a deduped audit use `ground_truth.load_ground_truth_spans` directly) |
| `ensemble_check.py` | Majority-vote-across-models check (§3e) |
| `compare_variants.py`, `final_comparison.py` | DEV-side variant comparison + v1_boundary robustness/consistency check |
| `test_report.py` | **The TEST report generator** — run this to reproduce §3a-3c exactly |
| `decompose_prompts.py` | Builds the 4 single-element decomposed prompts (`build_system_message_decomposed`, `build_user_message_decomposed`) — see its docstring for the RULE_1/2/3 adaptation logic |
| `run_decompose.py` | One-off script that ran the decomposition experiment (48 calls) + a 2nd v4_combined DEV run (6 calls) — kept for reference, not meant to be re-run |
| `decompose_report.py` | **The decomposition report generator** — run this to reproduce §3f's table exactly (uses `parse_response_single_element` in `parsing.py` and `load_all_runs_single_element` in `analyze.py`) |
| `per_verse_prompts.py` | Builds Mode A (v4_combined, single-verse-adapted instructions) and Mode B (§3f's decomposed prompts, unchanged, single verse) user messages; `get_verses()` splits a poem into verse lines |
| `run_per_verse.py` | Runner for the per-verse experiment — makes 1 API call per verse, aggregates each (provider, run) into one manifest record + one JSONL raw file (compatible with the existing `analyze.py` loaders unchanged); also writes a `per_call_log.json` per directory with per-verse usage/error detail |
| `per_verse_report.py` | **The per-verse grid report generator** — run this to reproduce §3g's table exactly (re-slices existing v4_combined/decomposed DEV dirs to Imru2 only + scores the new `per_verse/` dirs) |

### Results — `results/pilot_3models/`
| Path | Contents |
|---|---|
| `raw/`, `run_manifest.json`, `pilot_report.{md,docx}` | Original single-poem (Imru2) pilot — historical, superseded |
| `dev_nabigha_baseline/` | Baseline prompt run on Nabigha, 1 run each — DEV data |
| `dev_variants/{variant_key}/{Imru2,Nabigha}/` | All prompt-variant DEV runs. `v4_combined/` now has 2 runs (run2 added for the §3f comparison; originally 1) |
| `dev_variants/decomposed_{Trope,Simile,Kenning,Antonymy}/{Imru2,Nabigha}/` | The decomposition experiment (§3f), 2 runs each |
| `test_final/{baseline,v4_combined}/{Imru1,Jarir,Abu_Tammam}/` | **The frozen TEST data** — each has `raw/*.txt` (model responses) + `run_manifest.json` (usage/cost/errors) |
| `per_verse/mode_a/Imru2/` | Mode A (per-verse, all-4-elements), 2 runs, 3 models — §3g |
| `per_verse/mode_b_{Trope,Simile,Kenning,Antonymy}/Imru2/` | Mode B (per-verse, single-element), 2 runs, 3 models, per element — §3g. Each dir also has `per_call_log.json` (per-verse usage/error detail, not read by the scoring pipeline) |

### Ground truth & prompts
- `data/ground_truth/ali_ana/original/*.xlsx` — Dr. Ali Hussein's manual annotations, one file per poem (`امرؤ القيس 1.xlsx`, `امرؤ القيس 8.xlsx`, `النابغة الذبياني.xlsx`, `جرير.xlsx`, `ابو تمام.xlsx`)
- `data/elements/{Trope,Simile,Kenning,Antonymy}.txt` — canonical element definitions (unchanged since Phase 2 reorg, still the source both baseline and all variants build from)
- `archive/Forth_Step/Data/{Imru1,Imru2,Althobyane,Jareer,Abu_tammam}/poetry.txt` — the poem texts (note folder-name mapping: `Imru2`="poem 8", `Althobyane`=Nabigha, `Jareer`=Jarir)

### Environment
- `.env` (repo root, gitignored, **must exist** with `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) — copy from `.env.example` if missing. Loaded via `python-dotenv` in `run_pilot.py`.
- Python deps used: `anthropic` (0.117.0 at last check), `google-genai`, `openai`, `python-dotenv`, `pandas`, `python-docx`. No `requirements.txt` exists yet for this pilot folder specifically (open item).

### Model IDs and pricing actually used (verified against provider docs at the time, in `config.py`)
| Provider | Model ID | Input $/1M | Output $/1M |
|---|---|---|---|
| Anthropic | `claude-sonnet-4-6` | $3.00 | $15.00 |
| OpenAI | `gpt-5.4-mini` | $0.75 | $4.50 |
| Google | `gemini-3.5-flash` | $1.50 | $9.00 |

`anthropic` calls use `max_tokens=16000` (raised from an initial 4096 that truncated Nabigha's 50-verse response — see §6).

---

## 5. Open items — the experimental phase is closed; everything below is either waiting on someone else or is future work, not a next action for this codebase

### 5.1 Awaiting supervisor feedback

The supervisor email went out with 3 deliverables (`final_report.docx`, `detailed_results.docx`, `explanations_sample.docx`). Two specific questions are pending their response:

1. **Subtype-difficulty intuition**: §3c found that a DEV-derived hypothesis about which Trope subtype is hardest (استعارة تمثيلية) reversed at TEST scale, while مجاز مرسل (single-word lexicalized metonymy) is the one subtype v4_combined does nothing for at all, and Kenning broadly remains resistant to every intervention tried (§3f, §3g). These are patterns a rhetoric scholar may be able to explain in a way a purely computational analysis cannot (e.g. is مجاز مرسل's flatness because it's lexically closed/enumerable rather than compositional? does كناية's resistance track a real linguistic property of indirection that per-verse/per-element isolation can't touch?) — worth asking the supervisor directly rather than speculating further in code.
2. **Second annotator for inter-annotator agreement**: all ground truth in this project is single-annotator (Dr. Ali Hussein only); no IAA figure exists anywhere. Whether this is worth pursuing (and if so, on which poems) is the supervisor's call.

Nothing in the codebase should change in response to either question until the supervisor actually replies — see the thesis-writing note below for how the reply could reshape scope.

### 5.2 Thesis writing — in progress

`/writing/chapters/` now has `methodology.md`, `results.md`, `limitations_future_work.md`, `abstract_draft.md`, drafted from this document and the frozen reports only, with every number cited to its source file. `/writing/figures/` has the 4 supporting figures. These are drafts, not final chapters — they will need supervisor review and likely revision once §5.1's questions are answered (e.g. if the supervisor requests a second annotator, `limitations_future_work.md`'s "no IAA yet" framing may need to become a completed IAA section instead).

### 5.3 Possible future work (not started, not scheduled)

- **Fine-tuning**: everything in this pilot is zero-shot/prompt-only; a fine-tuned model (even a small open-weight one) on the existing ground truth has never been tried and could plausibly help Kenning specifically, where the failure mode looks more like "doesn't know the pattern" than "prompt friction."
- **Lexicon-augmented prompting for مجاز مرسل**: since this subtype is lexically closed (a finite set of conventionalized metonyms) rather than compositional, providing the model a lexicon/list of known مجاز مرسل expressions as additional context (rather than relying on the model to infer the pattern from a handful of examples) is untested and specifically targeted at the one subtype v4_combined does nothing for (§3c).
- **Fresh held-out poem for per-verse Kenning validation**: §3g's cross-poem replication (Imru2 → Nabigha) already checked this once and found the effect direction holds for 2 of 3 models but magnitude varies a lot — a third poem would tell us whether Nabigha's numbers are themselves reliable or still noisy at n=2 poems.
- **A proper (2-run, scored) test of the reasoning/explanation-augmented variant**: §3i's explanation-augmented sample was illustrative only — 1 run, and only decision *flips* were checked (absent→present for every flip, across all 3 models), never whether the new positive calls the reasoning requirement produced were actually *correct*. A properly scored version (2+ runs, judged against ground truth) would answer whether "explain yourself" is a net-positive or net-negative prompting strategy, rather than just an interesting behavioral observation.

---

## 6. Known pitfalls for the next session

1. **Small-sample noise is real and already burned us once.** The very first ablation run showed Gemini's Kenning F1 "jumping" 0.056→0.433 (8x) with v1_boundary on a single run. A second real run brought the honest (2-run-majority) number down to 0.225 — **half the apparent gain was noise from one lucky run.** Rule going forward: **never trust a single-run F1 number for a conclusion; always get ≥2 runs before drawing any comparative conclusion, and always report raw TP/FP/FN alongside F1** so small denominators are visible (an F1 of 0.43 built on 9 TP / 60 FN reads very differently once you see the counts).
2. **Gemini specifically has unstable run-to-run behavior on Kenning** — 77% agreement on DEV, 89% on TEST with v4 (vs. 91-100% for every other element/model combo, and vs. Gemini's own 100% baseline consistency on TEST). If Gemini's Kenning number looks unusually good or bad in a future run, check consistency before believing it.
3. **The one malformed-JSON case**: `results/pilot_3models/test_final/v4_combined/Jarir/raw/openai_run1.txt` has 2/40 verses with malformed JSON (stray trailing comma, truncated string — a real model glitch, not a parsing bug). `parsing.py` correctly flagged and excluded these rather than repairing them; run2 (clean) covered those verses in the 2-run majority. This is expected, rare behavior, not something to "fix" — but if you see a `parse_errors` count above near-zero in a future manifest, check it's this kind of thing and not a systematic issue.
4. **The hardcoded-`n_verses` bug class**: `analyze.py`'s `run_consistency()`, `score_vs_ground_truth()`, `cross_model_agreement()`, and `build_comparison_table()` originally defaulted to a module-level `N_VERSES` constant (=23, Imru2's count) regardless of which poem's data was actually being scored — silently truncating any other poem's consistency/scoring to only its first 23 verses. **Fixed** by adding an explicit `n_verses` parameter to all four functions (default kept at 23 for backward compatibility with old call sites that only ever touched Imru2). `span_scoring.py`'s `score_span_level()` was written correctly from the start (always took `n_verses` explicitly) and was never affected. **If you add a new scoring/consistency function, always take `n_verses` as an explicit parameter — never rely on a module-level poem-specific constant.**
5. **Claude requires an explicit, sufficiently large `max_tokens`.** The original 4096 default silently truncated Claude's response mid-verse-50 on the 50-verse Nabigha poem (Anthropic's API doesn't error on this, it just stops). Raised to 16000 in `providers.py`, which was enough headroom even for Imru1 (81 verses, ~7900 output tokens actually used). If a poem larger than Imru1 is ever added, re-check this ceiling before trusting a response is complete — always verify parsed verse count equals expected verse count (`parsing.py`'s `n_verses_parsed`) rather than assuming success from a 200-response alone.
6. **Strict vs. token span-matching criteria disagree meaningfully, especially for Antonymy** — Arabic morphological variation (e.g. النُّوّامِ vs نَوَّمُوا, different forms of the same root) makes strict substring matching fail even when the model clearly found the right instance. Token-overlap (word-level, with a partial fix for attached و/ف clitics) recovers some of this but not inflectional variation. Both criteria are reported for exactly this reason — don't pick just one and discard the other, and don't be surprised when they diverge a lot on Antonymy specifically.
7. **Isolating a task doesn't reliably help just because it removes distraction — GPT-5.4-mini can swing to near-total abstention.** In the decomposition experiment (§3f), giving GPT only Kenning to classify (no other 3 elements competing) made it *far* more conservative: positive calls (TP+FP) dropped from 15 to 4 and run-agreement fell from 98% to 82% — the opposite of the determinism gain every other element/model combo showed under decomposition. If a future single-element or narrowly-scoped prompt experiment shows a model's positive-call count collapsing alongside falling consistency, don't read that as "the model got more careful" — check whether it's actually an abstention failure mode before trusting the resulting precision number.
8. **When aggregating N per-verse API calls into one manifest record (as `run_per_verse.py` does for §3g), never let a partial per-verse failure set the record's `error` field to a truthy value.** `analyze.py`'s loaders (`load_all_runs`/`load_all_runs_single_element`) treat any truthy `error` as "discard this entire run's parsed data" — correct for the original one-call-per-run design (a truthy error there really does mean raw_text is empty/garbage), but wrong for an aggregated per-verse run where raw_text still has N-1 good verses. This bug actually happened once (§3g: a single Anthropic credit-balance error on the last verse of a 23-verse run zeroed out the other 22 verses' real data until caught and fixed) and was fixed by keeping `error: None` for partial failures and logging per-verse failures in a separate informational `verse_errors` field instead. If you write another aggregating runner, replicate that convention — don't let per-call granularity leak into the harness's per-run error semantics.
9. **Poem-level replication is a second, independent axis of noise, parallel to the run-level noise in pitfall #1 — but it attacks magnitude, not direction, and this entry was itself corrected once Claude's retry completed (worth noting as a caution about drawing conclusions from partial data).** Pitfall #1 established that a single *run's* apparent gain can be largely noise (Gemini's Kenning F1 "jumping" 0.056→0.433 on one run, corrected to 0.225 with a second). The Nabigha Kenning-replication follow-up to §3g found a related failure mode one level up, across *poems* — but only for Gemini: its per-verse Kenning gain on Imru2 (whole-poem F1 0.190 → per-verse F1 0.480, **+152%**, not the "+136%" this section originally stated — an arithmetic error, corrected here) shrank to +11% (0.262→0.290) on Nabigha. **Claude's gain did not shrink**: +125% on Imru2 (0.111→0.250), **+149% on Nabigha** (0.136→0.338) — as large or larger the second time. This section's first version was written while Claude's data was still blocked on an Anthropic credit-balance issue, using only GPT+Gemini, and concluded the effect was "not strong enough to justify adopting per-verse calling" in a way that read as a full negative — **that conclusion was premature; the corrected version (§3g) is a real, cross-poem-replicated positive finding for 2 of 3 models, just with a magnitude that varies too much per poem to quote a single percentage as generalizable.** Lesson, revised: never draw a comparative conclusion from a single sample unit's effect *size* (one run, or one poem) even when its *direction* looks robust — and separately, **don't write up a multi-model comparative finding as final while one model's data is still pending** (as this section briefly did) — flag it as preliminary/partial until all planned models are in, exactly as the report itself now does correctly. The frozen TEST numbers in §3a, pooled across 3 poems with 2-run majority throughout, remain the only numbers in this project that avoid both the run-level and poem-level version of this problem. **Net effect on the Kenning story**: whole-poem decomposition (§3f) doesn't help; per-verse calling (§3g Mode A) does help 2 of 3 models, replicated across 2 poems, but not enough in absolute terms (still far below Simile's ceiling) or cheaply enough (4-8x cost per unit of F1) to recommend adopting — Kenning remains the hardest element, but "nothing helps at all" is not the accurate summary once this correction is made.

---

## 7. Repository closure (2026-07-21)

**Secret scan finding, more extensive than previously known.** `THESIS_KNOWLEDGE.md` §7 had already flagged one exposed OpenAI key (`Forth_Step/GPT/key.txt`, committed at `1633cf5`). A full re-scan for this closure found **48 files total** with live-looking credentials still tracked in git and already pushed to the repo's public GitHub remote (`github.com/faisalomari/Metaphorical_Analysis`) — everything up to and including `1633cf5` was already on `origin/main`, so these were live regardless of any local fix:
- The same root-level `Forth_Step/GPT/key.txt` duplicate (the `archive/Forth_Step/` copy had been redacted during the Phase 2 reorg; the root duplicate was never removed).
- ~29 files under `previous_steps/poems/{Majaz,Tashbeeh,Kenayh,Tebaq}/**` (`key.txt`/`token.txt`/`LR.py`/`main.ipynb`) — one duplicated OpenAI key and one duplicated Hugging Face token, per the gap already noted in `THESIS_KNOWLEDGE.md`'s "Decisions Confirmed With User" §3 (the planned redaction never actually happened before these were committed).
- 5 files under `previous_steps/poems_analysis/multi_model_poetry_voting/keys/` — one each for OpenAI, Anthropic, Google, Cohere, and Qwen.
- 14 more files under `experiments/classifiers/` and `experiments/llm_pipelines/` — duplicates of the above created by the Phase 2 reorg copying `previous_steps/` content without re-scrubbing it.

**Remediation done**: all 48 files redacted in-place (same `REPLACE_WITH_YOUR_OWN_KEY` placeholder convention as the original fix), committed as `13a85e5`. This does **not** remove the keys from git history (already public) — **every one of these keys needs rotating at its provider** regardless of this fix; that action is on the user, not something this session could do. History rewriting (BFG/filter-branch + force-push) was explicitly declined as too destructive/disruptive for this session — noted here in case it's revisited later.

**Also removed**: root-level `FirstStep/`, `SecondStep/`, `ThirdStep/`, `Forth_Step/` — confirmed byte-identical duplicates of `archive/{FirstStep,SecondStep,ThirdStep,Forth_Step}/` (aside from stray `.DS_Store`/Office lock files), left over from the Phase 2 reorg never having removed the pre-move originals. Also removed a stray tracked root `.DS_Store` and two Word lock files under `הצעת תזה/`. `.gitignore` itself already covered all the relevant patterns (`.env`, `key.txt`, `token.txt`, `keys/`, `__pycache__/`, `.DS_Store`, `~$*`) — the problem was purely files tracked *before* those rules existed; no `.gitignore` changes were needed.

**Commit log for this closure** (chronological):
1. `13a85e5` — secret redaction. **Labeling caveat**: this commit's message only describes the secret redaction, but it also ended up containing the `FirstStep`/`SecondStep`/`ThirdStep`/`Forth_Step` + stray-junk removal, because `git rm` stages immediately and those removals were already sitting in the index from earlier in the session when this commit was made. The *content* is all correct and intended; only the commit boundary/message doesn't fully describe it. Noted here rather than silently left for a future reader to puzzle over.
2. `a68e1b2` — `experiments/pilot_3models/` harness and experiment code.
3. `db23ccb` — `results/pilot_3models/` results and reports.
4. (later, same closure pass) — `PROJECT_STATE.md` (this file, closed) + `REPRODUCIBILITY.md`.
5. (later, same closure pass) — `/writing/chapters/*.md` thesis drafts + `/writing/figures/*` result figures.

**`REPRODUCIBILITY.md`** (repo root) now documents exact environment setup, `.env` keys needed, model IDs/pricing, script execution order, where manifests/results land, and scoring-harness usage — a stranger with API keys can reproduce the frozen TEST run from that file alone (`python run_test.py` + `python test_report.py`).

---

# PHASE 2 (v2) — opened 2026-07-23

Everything above this line (§1-§7) is Phase 1: frozen, closed, historical. Nothing above is edited or re-scored by Phase 2. This section is additive.

## Phase 2 §0 — Rationale

Phase 2 exists because of two developments that came **after** Phase 1 closed on 2026-07-21:

1. **Supervisor correction on English element terminology.** Phase 1's English names for two of the four elements were wrong, and may have misled the models (all of whose prompts are in a mix of Arabic definitions + English element names) throughout Phase 1:
   - **طباق** — Phase 1 called this "antonymy" (a lexical relation between two words). The correct term is **antithesis** (a rhetorical figure: pairing opposites within one context for effect). Antonymy and antithesis are related but not the same thing, and the wrong name could plausibly bias a model toward a narrower, more lexical reading than the element actually requires.
   - **كناية** — Phase 1 called this "kenning". A kenning is a specific Old Norse/Old English poetic-compounding device ("whale-road" for sea) — a real but unrelated device from a different poetic tradition. The correct term is **periphrasis** (indirect expression conveying a meaning without stating it directly, while the literal reading stays possible) — this is not just "wrong terminology" but potentially *actively misleading*, since "kenning" points a model at the wrong structural pattern entirely.
   - **مجاز** is confirmed to be an umbrella term, not a single figure. It covers at minimum three subtypes: **استعارة** (metaphor), **تمثيل** (analogy/extended metaphor), and **مجاز مرسل** (metonymy/synecdoche — e.g. «السماء تمطر» "the sky is raining" where the actual rain-source is the cloud, a part-for-whole/cause-for-effect relation; or «أراني أعصر خمراً» "I see myself pressing wine" where what is literally pressed is grapes, not wine). Phase 1's `data/elements/Trope.txt` gives one unified definition and examples but never explicitly names or exemplifies the مجاز مرسل subtype — see §3c above, where مجاز مرسل is the one Trope subtype v4_combined does nothing for (85%→85% missed, completely flat). This is a candidate explanation worth testing, not yet confirmed.

2. **Chat-gap observation.** In a chat-interface session (not this pipeline), Fable 5, given free-form Arabic reasoning space (no strict JSON schema, no "don't explain" instruction), correctly identified a كناية in Imru' al-Qais's verse «فُوهَا كُلَّمَا نَبَّهْتُهَا... » that **every** Phase 1 pipeline configuration missed for that verse (baseline, v4_combined, decomposed, per-verse — across all 3 models, both runs). Hypothesis under test: Phase 1's strict no-explanation JSON output format, the wrong terminology, and the mid-tier models used, **jointly** suppressed detection — and §3i (Phase 2) below is designed to disentangle which of the three variables (if any) is doing the work, rather than assume it's all three.

**Important framing**: this is a hypothesis-generation and disentanglement experiment, not a re-litigation of Phase 1's frozen numbers. Phase 1's TEST results remain the thesis's primary numbers regardless of what Phase 2 finds — see §2 below for how Phase 2 findings get reported alongside them.

## Phase 2 §1 — Frozen decisions carried over unchanged from Phase 1, plus new ones

All of Phase 1 §2's rules still apply without exception: DEV = Imru2 + Nabigha, TEST = Imru1 + Jarir + Abu_Tammam, TEST remains spent and untouchable, 2 runs per configuration with 2-run majority as primary, span-level scoring (both strict and token-overlap criteria) — never verse-level. Phase 2 adds:

5. **Phase 2 experiments are DEV-only, same as Phase 1's supplementary experiments (§3f, §3g).** §3i (Phase 2) uses Imru2 + Nabigha exclusively. TEST is not touched by anything in this section.
6. **Terminology corrections apply to all NEW writing only.** Phase 1 documents/reports (`final_report.docx`, `detailed_results.docx`, `explanations_sample.docx`, `/writing/chapters/*.md` as already drafted, and every number/table in §1-§7 above) are **not** retroactively edited — they used "antonymy"/"kenning" throughout and stay that way as an accurate historical record of what was actually run. See `GLOSSARY.md` (repo root) for the full old-term → correct-term mapping and how to cite Phase 1 material going forward without silently correcting it in place.
7. **Cost estimate + explicit user confirmation BEFORE running any Phase 2 API call.** Same discipline as Phase 1 §5's Nabigha-replication follow-up — no exceptions, especially for Config C (unknown-priced flagship model, per-verse, two-stage, with thinking).

## Phase 2 §2 — Where Phase 2 lives

- Code: `experiments/phase2_chatlike/`
- Results: `results/phase2_chatlike/`
- Terminology: `GLOSSARY.md` (repo root)

## Phase 2 §3i — Three-configuration disentanglement experiment (DEV: Config A/B full DEV, Config C Imru2-only so far)

**Status as of 2026-07-23: Config A and B run on full DEV (Imru2+Nabigha, 2 runs); Config C run on Imru2 only (2 runs), Nabigha's Config C explicitly held pending confirmation.** Full tables, the verse-6 case study, and the four-question analysis are in [`results/phase2_chatlike/report_3i.md`](../results/phase2_chatlike/report_3i.md) — this subsection is a summary pointer, not a duplicate.

Three configurations isolate the model-effect, terminology-effect, and full-recipe variables from Phase 1's Sonnet 4.6 + v4_combined + strict-JSON baseline:

- **Config A (pure model effect)**: v4_combined unchanged, on Fable 5 (`claude-fable-5`, `effort=medium`). Compared against Sonnet 4.6's existing v4 DEV numbers.
- **Config B (pure terminology effect)**: v4_combined with only the English element names corrected (antonymy→antithesis, kenning→periphrasis) and the مجاز block annotated with its three subtypes and the two canonical examples above, on Sonnet 4.6. Everything else — model, schema, scoring — identical to v4.
- **Config C (full chat-like recipe)**: two-stage, per-verse (Mode A granularity, matching §3g's per-verse mechanism), Stage 1 on Fable 5 (free-form Arabic analysis, verbatim user-specified prompt, full poem context, one verse per call), Stage 2 on GPT-5.4-mini (extraction into the unmodified strict JSONL schema). **Imru2 only so far** — Nabigha not yet run.

**Headline results** (full detail + TP/FP/FN in `report_3i.md`):
1. **Model effect is real**: Fable 5 alone (Config A, same prompt/terminology as existing) moves both Trope (F1 0.059→0.200) and Kenning (F1 0.130→0.198) on pooled DEV, with *no* precision cost — the first intervention in this whole project (Phase 1 included) to gain recall without trading precision.
2. **Terminology effect is real but small, and element-specific**: Trope gets a modest genuine boost (F1 0.059→0.090); Kenning does not (F1 0.130→0.123, flat-to-worse) — correcting "kenning"→"periphrasis" alone did not unlock Kenning recall. **Reportable caveat for the thesis**: Phase 1's frozen Trope numbers carry a small terminology caveat; its Kenning numbers do not.
3. **Full recipe (Config C) moves Kenning recall substantially on Imru2** (strict F1 0.111→0.316, token F1 0.111→0.421; TP 1→6-8 out of GT n=16), at a real precision cost (more FP than TP) consistent with every other recall-boosting intervention tried in this project (§3f, §3g). **It catches the exact motivating verse** (Imru2 v6, «كُلَّمَا نَبَّهْتُهَا») that Existing/A/B all miss, in both runs, with a substantively correct rhetorical justification — replicating the original chat-gap observation inside the harness.
4. **مجاز مرسل question is inconclusive from Imru2 alone** — its ground truth has exactly 1 مجاز مرسل instance, too thin to read either way. Answering this properly requires Nabigha.

**A shared-infra bug found and fixed during scoring**: `span_matching.py`'s `normalize()` didn't strip Arabic guillemets (`«»`), which Config C's Stage-1-quoting style introduces but no Phase 1 model ever produced. Fixed (now strips `«»` alongside the existing `"'`) and **verified byte-identical against Phase 1's frozen TEST pooled counts before/after** — zero impact on any frozen number, real and substantial impact on Config C's own scores (Kenning token F1 0.263→0.421 once spans matched correctly).

**Cost actually spent**: A $1.91, B $0.27, C (Imru2 only) $5.05 — **$7.23 total**, within the approved ranges. Extending C to Nabigha *in full* is estimated at **≈$11.9** and remains **not run** — the user instead approved a cheaper, narrowly-scoped alternative to answer question 4 specifically (below), and the full-poem Nabigha run is still open for a future decision.

**Addendum, same day — Nabigha مجاز مرسل targeted recall probe** ($2.73 actual, 22 stage-pairs: 9 verses containing all of Nabigha's مجاز مرسل ground truth + 2 contrast verses, 2 runs each). **Labeled explicitly as a recall probe, not an evaluation** — known-positive verses only, no precision/F1 claim made. Result: 4 of 9 مجاز مرسل verses caught in ≥1 of 2 runs (v7, v14, v30, v47); pooled with Imru2's 1 verse, **4/10 verses caught strict, 3/10 token (any-of-2-runs)** — a directional improvement over Phase 1's flat ~15% recall, but inconsistent run-to-run (3 of the 4 hits came from only one of two runs — under the project's standard 2-run-majority convention this collapses to just **1/10 strict, 0/10 token**) and not methodologically comparable to Phase 1's pooled-3-model 2-run-majority figure. Both contrast verses (استعارة فعل, مجاز عقلي) were caught, matching §3c's finding that those subtypes are already tractable. Full detail, per-instance quotes, and the full-poem-Nabigha-still-open note: `report_3i.md` §8.

## Phase 2 §4 — Open items (2026-07-23)

1. **Nabigha full-poem Config C run — budget-held, not run.** The targeted مجاز مرسل probe (Phase 2 §3i addendum, above) answered question 4 cheaply ($2.73) without it. A full run would additionally produce real precision/F1 numbers for Config C on a second poem (the probe deliberately does not — see `report_3i.md` §8's known-positive-only framing) and would let §9's "reachable but not reliably decided" finding be checked against a second poem's data, the same way §3g's Kenning-per-verse finding was checked against Nabigha in Phase 1. Estimated cost ≈$11.9 (measured Imru2 per-call average carried forward — see Phase 2 §3i above). **Requires fresh confirmation before running**, per standing discipline.
2. **Few-shot demonstration experiment — designed, not run.** Full design in `experiments/phase2_chatlike/PROPOSAL_fewshot.md`: tests whether 2-3 worked reasoning demonstrations (drawn from `data/elements/*.txt`'s own existing example couplets plus the مجاز مرسل canonical examples already in `GLOSSARY.md` — zero DEV/TEST leakage) embedded in Config B's system message can recover part of Config C's Kenning/مجاز مرسل recall gain at Config A/B's whole-poem cost, and — the more interesting question given §3i §9's finding — without Config C's run-to-run non-determinism. Estimated cost ≈$0.35–0.55 (Sonnet 4.6 only) if run. Not started.
3. **Fresh-poem validation — needs supervisor.** Phase 1 §5.3 already flagged this for the per-verse Kenning finding specifically ("a third poem would tell us whether Nabigha's numbers are themselves reliable or still noisy at n=2 poems"); Phase 2's findings (Config A's model effect, Config C's Kenning/مجاز مرسل reachability, the determinism gap in §3i §9) sharpen the case for it but don't change the fact that no DEV/TEST poem can serve this purpose — a genuinely fresh, never-touched poem is needed, which means new ground-truth annotation. This is a scope/resourcing decision for the supervisor, not something this codebase can decide or start on its own.

## Phase 2 §5 — Supervisor feedback log

**Purpose**: this project has two supervisors and one ground-truth annotator, and feedback from them arrives outside this repo (chat, email, meetings) — logging it here verbatim is the only way a future session (or a future instance of this assistant) has access to it. Add to this log; don't summarize over previous entries.

**People**: **Tsvi Kuflik** ("Tsvika") — co-supervisor. **Ali Hussein** ("Ali") — the ground-truth annotator (his manual annotations are `data/ground_truth/ali_ana/*.xlsx`, referenced throughout this document).

**Entry 1 — 2026-07-23, Tsvika, responding to the Phase 1 report** (translated from Hebrew, relayed via chat, not in this repo until now):

> "The results are indeed not impressive. You have 2 poems by the same poet — you could check just for this poet (perhaps when it's the same poet, success will be better?). Regarding the errors, we need to start examining them and identifying characteristics. We should talk at the next meeting and you'll probably need to go over this with Ali."

**What this means, disambiguated** (the request that produced this log entry clarified the reading): the same-poet question is a **hypothesis about the models** — does performance improve when evaluated within one poet's poems (style consistency) versus across poets — not a question about DEV/TEST split validity per se. It happens to be confounded with the DEV/TEST split here, since the two Imru' al-Qais poems are Imru2 (DEV) and Imru1 (TEST) — that confound must be stated honestly whenever this question is answered (see Phase 2 §6 below), not glossed over. The "errors... identifying characteristics" request is answered by the error-characteristics summary (`results/phase2_chatlike/error_characteristics_summary.md`). The "go over this with Ali" request is the motivation for the shortlist prepared in Phase 2 §7 below.

## Phase 2 §6 — Per-poem breakdown and the same-poet question

Computed by `experiments/phase2_chatlike/per_poem_breakdown.py` — re-slices Phase 1's frozen TEST/DEV manifests (baseline and v4_combined, all 3 models, both criteria) by individual poem instead of §3a's pooled-across-poems view. No new API calls; no change to any frozen pooled number. Full per-element/per-model table is reproducible by running that script; this section reports the macro-average (mean F1 across all 3 models × 4 elements, strict criterion, v4_combined) per poem, which is what's needed to answer Tsvika's question, plus the full table's most relevant lines inline.

**One pre-existing asymmetry worth flagging before the numbers**: Nabigha's baseline has only **1 run** per model (not 2) — a Phase 1-era data gap (`PROJECT_STATE.md` §4), not something Phase 2 introduced. Nabigha's baseline column should be read with that in mind; its v4_combined column (2 runs, same as everywhere else) is unaffected.

### Macro-average F1 per poem (v4_combined, strict, mean across 3 models × 4 elements)

| Poem | Poet | Split | Macro-avg F1 |
|---|---|---|---|
| Abu_Tammam | Abu Tammam | TEST | **0.366** (highest of all 5) |
| Imru2 | Imru' al-Qais | DEV | 0.343 |
| Imru1 | Imru' al-Qais | TEST | 0.302 |
| Nabigha | Al-Nabigha | DEV | 0.284 |
| Jarir | Jarir | TEST | **0.256** (lowest of all 5) |

### Tsvika's question, answered

**Question** (Tsvika, §5): does model performance improve when evaluated on a single poet's poems, compared to across poets — is style consistency a factor?

**Short answer: the data doesn't show a clear same-poet effect.** Imru' al-Qais's two poems (Imru2 0.343, Imru1 0.302; poet mean 0.323) sit in the *middle* of the 5-poem range, not clustered at the top — Abu_Tammam, a different poet with only one poem in the corpus, scores highest (0.366), and Jarir, also a different poet with one poem, scores lowest (0.256). If "same poet" were a strong driver of success, Imru' al-Qais's two poems should cluster together and apart from the rest; instead, individual-poem variance (Abu_Tammam vs. Jarir: Δ=0.11) is larger than the gap between the two Imru' al-Qais poems and the group of other poets (poet-of-interest mean 0.323 vs. other-poets mean 0.302: Δ=0.02).

**The honest confound, stated as asked**: Imru2 was studied during DEV prompt-tuning (all 4 variants, ablations, decomposition, and per-verse experiments were iterated against it); Imru1 was TEST, seeing the frozen v4_combined prompt exactly once. If DEV-tuning gave Imru2 a "home-field" advantage independent of poet identity, we would expect Imru2 to outscore Imru1 by more than ordinary poem-to-poem noise — it does outscore it (0.343 vs 0.302, Δ=0.04), but that gap is *smaller* than the gap between Abu_Tammam and Jarir (Δ=0.11), two poems that never touched the DEV-tuning loop at all. So the DEV-tuning advantage, if it's doing anything here, isn't doing more than ordinary poem-to-poem noise already does.

**What can be concluded**: no dramatic, unambiguous poet-consistency effect is visible in this data.
**What cannot be concluded**: whether a real but modest poet-effect exists that 5 single-poem data points (2 for the poet in question, 1 each for 3 others) are too thin to resolve — this is the same "never trust a comparative conclusion from a small sample" caution already on record (`PROJECT_STATE.md` §6.1, §3d) applied to a new axis (poet identity, not run-to-run or element-support size). Properly separating "poet consistency" from "individual poem difficulty" from "DEV-tuning advantage" would need at least one more poem by an already-represented poet that never touched DEV tuning — structurally the same ask as Phase 2 §4 item 3 (fresh-poem validation), not a new, separate request.

**Entry 2 — 2026-07-23, supervisor meeting (relayed via chat, not in this repo until now)**:

> "Check line by line in chat and Claude Code, not using the API" — they want to see the chat-like per-verse reasoning output itself.
>
> "Check and analyze why the models are missing a lot — recall is too low."
>
> "What are the differences between the examples used in the few-shot prompt and the testing — why is it missing?"
>
> Working hypothesis to refine: "models are good at simpler rhetorical elements but not strong on more complex tasks."
>
> Terminology corrections (already implemented in GLOSSARY.md / Phase 2 Config B — verify, don't redo).

**Disambiguation / how this maps to work items**: the "check line by line in chat" request is answered by a new per-verse analyses document (assembling Config C's existing Fable 5 stage-1 Arabic reasoning, verbatim, verse text + ground truth alongside it — no new API calls, since Config C's Imru2 and Nabigha-probe outputs already exist from §3i). The "why is recall too low" and "few-shot example gap" requests are answered by two new analysis documents: a recall/FN decomposition over the frozen TEST results, and a gap analysis comparing `data/elements/*.txt`'s worked examples against the ground-truth instances (especially missed ones) — both from existing frozen data, zero new API calls. The "simple vs complex" hypothesis is being refined (not rebutted) into a marker-explicitness framing for the discussion chapter, cross-referencing §3c's subtype breakdown and §3i's Config C findings. The terminology-correction item is confirmed already done (`GLOSSARY.md`, Phase 2 Config B) — nothing to redo.

## Phase 2 §7 — Analysis-only session, 2026-07-26: four deliverables + one new methodology finding

**Status**: this entire session was analysis-only, zero new API calls, per standing user instruction. Everything below reconstructs or re-presents already-collected Phase 1/Phase 2 data.

**Deliverables**:
1. [`results/phase2_chatlike/verse_by_verse_reasoning.docx`](../results/phase2_chatlike/verse_by_verse_reasoning.docx) — Config C's Fable 5 Stage-1 Arabic analyses, verbatim, all 23 Imru2 verses (both runs) + the 11 Nabigha مجاز مرسل-probe verses (both runs), each with verse text and Dr. Hussein's ground truth alongside. Built with `experiments/phase2_chatlike/build_verse_by_verse_reasoning.py`. RTL-verified by rendering actual pages to PNG (Word→PDF→PyMuPDF) — not just source inspection — per CLAUDE.md's mandatory visual-render rule.
2. [`results/phase2_chatlike/recall_decomposition.md`](../results/phase2_chatlike/recall_decomposition.md) — every frozen-TEST FN (v4_combined, strict, 1,031 events) classified into schema-structural / subtype-knowledge / boundary-confusion (mechanical scan) / annotation-sensitive (shortlist) / model-capability / format-suppression-candidate / unclassified, per a priority order explicitly sanity-checked with the user before running. Reconstruction verified byte-exact against §3a's frozen TP/FP/FN table before any decomposition. Code: `experiments/phase2_chatlike/recall_decomposition.py`; raw per-instance data in `results/phase2_chatlike/recall_decomposition_events.json`. Also surfaced 8 new mechanical Trope↔Kenning boundary-confusion instances beyond the manual shortlist, and 5 candidate new entries for `ali_adjudication_shortlist.md` (shared-FP pattern, not auto-classified — flagged for Dr. Hussein).
3. [`results/phase2_chatlike/example_gap_analysis.md`](../results/phase2_chatlike/example_gap_analysis.md) — characterizes `data/elements/*.txt`'s worked examples against the ground-truth population (subtype coverage, marker explicitness, span length, multi-figure share). Code: `experiments/phase2_chatlike/example_gap_analysis.py`.
4. [`writing/chapters/discussion_draft.md`](../writing/chapters/discussion_draft.md) — draft discussion section refining "simple vs. complex" into a marker-explicitness/literal-reading-foreclosure hypothesis, cited against §3a/§3c/§3i's frozen numbers. Not yet reviewed.

**Important new finding, surfaced by deliverable 3 — needs attention before `PROPOSAL_fewshot.md` is ever run**: every one of the 19 worked examples across `data/elements/{Trope,Simile,Kenning,Antonymy}.txt` is a real, annotated verse from this project's own 5-poem corpus, one per poem in the fixed order Imru1→Imru2→Nabigha→Jarir→Abu_Tammam — verified byte-for-byte (e.g. Trope.txt's example #1 is Imru1 v22 verbatim, example #4 is Jarir v12 verbatim). Since `data/elements/*.txt` is loaded into every prompt variant's system message (frozen, byte-identical since Phase 1), **3 of every element file's 4-5 examples are literal TEST-poem verses** — meaning the frozen TEST evaluation has, since Phase 1, shown the model a "this verse contains element X" example drawn from the exact poem (and in a few cases the exact verse) it is later asked to score. This directly contradicts `PROPOSAL_fewshot.md`'s stated premise that its planned demonstration source ("`data/elements/{Kenning,Trope}.txt`'s own existing canonical example couplets") was "never drawn from the 5 annotated poems" — that proposal's demonstration-selection plan needs new source material before it is ever run. Full detail and the provenance table: `results/phase2_chatlike/example_gap_analysis.md` §0. Not re-litigated against any frozen TEST number here — TEST stays spent regardless (§2) — but flagged as a limitation for `limitations_future_work.md` to pick up.

**Housekeeping note**: `git status` at the start of this session showed `CLAUDE.md`, `GLOSSARY.md`, all of `experiments/phase2_chatlike/`, and all of `results/phase2_chatlike/` (i.e. everything from the 2026-07-23 Phase 2 session) as untracked/uncommitted, plus an uncommitted fix to `span_matching.py`'s `normalize()` (the «» guillemet-stripping fix already documented in Phase 2 §3i). None of this was touched or committed by this session — flagging only so a future session (or the user) is aware a large amount of Phase 2 work has never been committed to git.
