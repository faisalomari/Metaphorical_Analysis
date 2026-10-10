# Experiment Priorities — Ranked, Not Exhaustive

Each item: what it is, why it matters most, estimated effort (time), estimated API cost with an explicit scaling basis from a real logged cost in `PROJECT_STATE.md`/`report_3i.md`, and what it would let the paper claim that it currently cannot.

---

## 1. IAA on the existing 13-verse adjudication shortlist (or a modestly larger stratified sample)

**Why top priority**: this is the single most reviewer-visible gap (`reviewer_risks.md` §1) and the cheapest to close, because the shortlist is already built (`results/phase2_chatlike/ali_adjudication_shortlist.md`) and the meeting with Dr. Hussein is already a listed-but-unscheduled open item (`PROJECT_STATE.md` Phase 2 §4 item 4). It requires zero new API calls — this is a human-annotation task, not a model-evaluation task.

**Effort**: 1 meeting/session with Dr. Ali Hussein (shortlist is pre-built with explicit discussion questions per group, A-D). If extended to a larger stratified sample (e.g. 50-100 verses instead of 13), likely 2-3 sessions or a take-home annotation task.

**API cost**: **$0** — no model calls involved, purely human annotation + agreement-statistic computation (Cohen's κ or Krippendorff's α, both already identified as candidate statistics in `related_work_outline.md` §2g).

**What it unlocks**: a real, citable IAA figure — directly closes the single limitation every DHQ-precedent paper in the related-work list (Bender et al., Zirker & Göggelmann) would lead a reviewer to expect.

---

## 2. Negative-sampling follow-up for Phase 3's 2-3 most striking subtypes (to get real precision/F1)

**Why second priority**: Phase 3's recall-only design (`MEETING_SUMMARY.md` §4) is explicitly flagged by the project's own documentation as insufficient to draw conclusions ("is recall-only sufficient for this round, or is real Precision/F1... needed before drawing conclusions?" — an open question in the source). The headline numbers the paper would most want to cite (استعارة تمثيلية's 7.1% recall collapse, كناية نسبة's 0%) are exactly the ones a reviewer would most want precision context for.

**Effort**: design is "designed but not run" per the source — a negative-sampling harness needs building (test each subtype's prompt against *other* subtypes' lines as negatives), but this reuses Phase 3's existing subtype-prompt infrastructure (`experiments/phase3_subelements/subtype_defs.py`) rather than starting from scratch. Estimate: 1-2 days of engineering + the run itself.

**API cost, with scaling basis shown**: Phase 3's full 551-line, 1-run-equivalent (23-subtype) run cost **$2.0071** for every ground-truth-positive line across 23 subtypes (`MEETING_SUMMARY.md` §7). Restricting to the 3 most interesting subtypes (استعارة تمثيلية n=28, كناية نسبة n=4, مجاز مرسل n=24 — 56 positive lines total, ~10% of the 551-line full set) and adding an equal number of negative lines (drawn from other subtypes' positives, reused — not newly generated) roughly doubles the per-subtype call count without re-touching the other 20 subtypes. **Scaling assumption**: cost scales roughly linearly with (number of API calls) × (per-call token cost), and per-call token cost is roughly constant across subtypes (same model, similar verse length) per the source's own flat ~$0.0036/call average ($1.9991 / 551 lines ≈ $0.00363/line, 2-run). For 56 positive + 56 negative lines × 2 runs = 224 calls at that same per-call rate: **≈$0.81**. Rounding up for the two-run-per-line-plus-retry overhead already seen in the source (actual was ~5% above naive estimate), estimate **≈$0.85-1.00**.

**What it unlocks**: converts the paper's strongest subtype-level finding from a recall-only observation into a reportable F1 with raw TP/FP/FN — directly satisfies the project's own standing experiment-discipline rule (`CLAUDE.md` rule 3) that recall-only results should not stand as a comparative conclusion.

---

## 3. One additional poem (fresh, never touched by DEV tuning) for per-verse Kenning/Periphrasis validation

**Why third priority**: this is explicitly named as the natural next step in two separate places — `limitations_future_work.md` §7 ("a fresh held-out poem for per-verse kenning validation... is a comparatively low-cost way to firm up a finding that is otherwise the single most encouraging result this pilot cycle produced for kenning specifically") and `PROJECT_STATE.md` Phase 2 §4 item 3. It directly addresses the two-poem-is-barely-enough problem already surfaced twice in this project's own history (§3g's Imru2→Nabigha magnitude swing; §6.9's "poem-level noise" lesson).

**Effort**: requires new ground-truth annotation (not something the codebase can generate) — this is the blocker already flagged ("needs supervisor... a genuinely fresh, never-touched poem is needed, which means new ground-truth annotation"). Once annotated, the harness itself (per-verse Mode A runner, `run_per_verse.py`) is already built and requires no new engineering. Effort is therefore dominated by annotation turnaround time (supervisor/Dr. Hussein's availability), not engineering — likely weeks, not days, and outside this codebase's control.

**API cost, with scaling basis shown**: the most directly comparable logged cost is the actual Nabigha per-verse replication: **$1.75 for 300 calls (50 verses × 3 models × 2 runs)**, i.e. ≈$0.00583/call (`PROJECT_STATE.md` §3g, "Nabigha replication follow-up" — note this is the *corrected* estimate, not the originally wrong $0.05-0.10 guess, which is exactly the kind of error this estimate must avoid repeating). **Scaling assumption**: a new poem's cost scales linearly with its verse count at this same $0.00583/call rate, scoped to the single most informative per-verse configuration (Mode A, all-4-elements, matching the mechanism that produced the original Kenning finding — not the full 2x2 grid). For a poem of similar length to Nabigha (~50 verses): **≈$1.75**. For a shorter poem (~25 verses, e.g. Imru2-length): **≈$0.88**. If also running the whole-poem v4_combined baseline on the same new poem for comparison (cheap, per Imru2's $0.156 whole-poem/2-run/3-model cost, `results.md` §9): add **≈$0.15-0.30**. **Total estimate: ≈$1.00-2.10 depending on poem length**, once annotation exists.

**What it unlocks**: a third data point on whether per-verse Kenning/Periphrasis improvement is a real, generalizable effect or an artifact of 2 poems — directly needed before the discussion draft's "direction replicates for 2 of 3 models" claim can be stated with more confidence than "2 poems checked."

---

## 4. Extend Phase 2's Config C (free-form reasoning) to a full Nabigha run

**Why fourth priority**: this is the one open item with the most detailed cost history already on record, and it would resolve two explicitly still-open questions: (a) the مجاز مرسل recall question, currently only answerable from a known-positive-only probe with no precision/F1, and (b) whether Config C's precision cost and run-to-run instability (found on Imru2 alone) hold on a second poem — the same "don't trust a single poem" lesson already applied twice elsewhere in this project (§3g, §6.9).

**Effort**: zero new engineering — the full Config C pipeline (Stage 1 Fable 5 free-form, Stage 2 GPT-5.4-mini extraction) already exists and ran successfully on Imru2 and the Nabigha probe subset.

**API cost, with scaling basis shown**: already estimated directly in the source, not re-derived here — **≈$11.9** (`report_3i.md` §6/§7: Stage 1 ≈$11.85 + Stage 2 ≈$0.07, based on Config C's measured Imru2 per-call average of ~2,447 input/~1,681 output tokens at effort=medium, scaled to Nabigha's 50 verses × 2 runs = 100 pairs using Nabigha's actual `count_tokens` input of ~3,443/call). This is the most carefully-derived estimate in the whole project (it already corrects an earlier, wrong $0.05-0.10 guess) and should be trusted as-is rather than re-estimated.

**What it unlocks**: real precision/F1 for Config C on a second poem (currently only Imru2 has full Config C numbers) and a direct answer to whether the مجاز مرسل recall gain (currently "4/10 known-positive verses, probe-only") generalizes with real negative-verse data included.

**Caveat already on record**: this is explicitly the most expensive single item here relative to what it buys (a config whose defining trait is already known to be a large precision cost — "extending it doesn't change that trade-off, only tests whether the trade-off's size replicates," `report_3i.md` §7). Ranked 4th, not 1st, for exactly this reason — it's well-estimated and ready to run, but not the most reviewer-critical gap.

---

## 5. Cross-model replication of the Phase 3 sub-taxonomy (at least for the 2-3 subtypes prioritized in item 2)

**Why fifth priority**: Phase 3's entire 23-subtype breakdown rests on Gemini 3.5 Flash alone (`MEETING_SUMMARY.md` §5) — a single-model result is the Phase-3 analogue of the single-poem problem this project has already learned to distrust twice over (poem-level: §3g/§6.9; now needed at the model level for subtypes). Ranked below items 1-4 because it compounds with item 2 (no point cross-model-validating a recall-only number) and is more expensive to do properly.

**Effort**: moderate — requires adapting the Phase 3 subtype-prompt harness to the other two models (Claude Sonnet 4.6, GPT-5.4-mini), which already have working provider wrappers from Phase 1 (`providers.py`), so this is mostly a matter of re-running existing prompt logic against two more APIs, not new engineering. 1-2 days.

**API cost, with scaling basis shown**: Phase 3's logged, corrected full run (1 model, 551 lines, 1 run-pass each but structured as 2 runs per the project convention) cost **$2.0071**. Running the same 551-line set on Claude Sonnet 4.6 and GPT-5.4-mini as well (2 more models) scales roughly by the ratio of each model's per-token price to Gemini 3.5 Flash's ($1.50/$9.00 per MTok). Claude Sonnet 4.6 ($3.00/$15.00) is roughly 2x Gemini's rate; GPT-5.4-mini ($0.75/$4.50) is roughly 0.5x. **Scaling assumption**: cost scales linearly with the model's price ratio at a fixed token volume (the task and prompt lengths are identical across models). Estimate: Claude ≈$2.0071 × 2 ≈ **$4.01**; GPT-5.4-mini ≈$2.0071 × 0.5 ≈ **$1.00**. **Combined for both additional models: ≈$5.00**, or **≈$0.65-0.90** if restricted to just the 2-3 priority subtypes from item 2 (same ~10% scope reduction applied as in item 2's estimate).

**What it unlocks**: tells the paper whether Phase 3's subtype-difficulty ordering (e.g. استعارة تمثيلية's collapse, كناية نسبة's zero recall) is a genuine task property or a Gemini-specific artifact — directly relevant to RQ3 (`gap_statement.md`) about cross-model consistency, and currently **not yet supported** per `claim_evidence_matrix.md` B3.

---

## Not prioritized here, but on record as open items (for completeness, not re-ranked)

- Few-shot demonstration experiment (`PROPOSAL_fewshot.md`) — currently **blocked**, not just low-priority: its demonstration-source premise is factually contradicted by `example_gap_analysis.md` and needs a redesign before it can run at all.
- Fine-tuning (`limitations_future_work.md` §7) — explicitly future work, outside a prompting-only pilot's scope and this paper's realistic submission timeline.
- Lexicon-augmented prompting for مجاز مرسل (`limitations_future_work.md` §7) — untested, plausible, but no cost estimate exists anywhere in the source documents to scale from, so it is not included above with a fabricated number.
