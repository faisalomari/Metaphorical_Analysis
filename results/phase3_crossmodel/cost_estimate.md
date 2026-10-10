# Phase 3 cross-model — cost estimate (pre-spend)

Written before any new API call, per CLAUDE.md's standing discipline (#5) and
the task's own step 3. **No paid calls have been made yet** — this is the
estimate gate.

## What would be run

The existing Phase 3 sub-element recall task
(`experiments/phase3_subelements/run_subtype_check.py`'s design, data, and
prompts — unchanged), on the **570 ground-truth rows** across 25 subtypes
that Gemini 3.5 Flash was already run on
(`results/phase3_subelements/final_summary.xlsx`), **2 runs per row**
(`N_RUNS=2`, the project's 2-run minimum), temperature 0.0, for each of:

| Model key | Model ID | Source config | price_in $/MTok | price_out $/MTok |
|---|---|---|---|---|
| `anthropic` | `claude-sonnet-4-6` | `pilot_3models/config.py` | 3.00 | 15.00 |
| `openai` | `gpt-5.4-mini` | `pilot_3models/config.py` | 0.75 | 4.50 |

→ 570 rows × 2 runs = **1,140 calls per model = 2,280 calls total.**

**Not included: `anthropic_fable5` (`claude-fable-5`, $10.00/$50.00 per
MTok, from `phase2_chatlike/phase2_config.py`).** At this volume Fable 5
alone is estimated at **~$15-18**, which both exceeds the $10 auto-proceed
gate by itself and repeats the exact reasoning the original Phase 3 session
already used to exclude it (`results/phase3_subelements/MEETING_SUMMARY.md`
§5: "explicitly ruled out for cost, $10/$50 per MTok vs Gemini's $1.50/$9.00
... roughly half Claude Sonnet 4.6's price"). Excluded here for the same
reason; would need its own separate cost estimate and approval if ever
wanted.

## Token estimate

No per-call token log survived for Gemini's authoritative full run (the
`summary_*.json` files were overwritten by later partial runs — only the
aggregate cost, **$1.9991 for ~1,140 calls, ≈$0.00175/call**, survives in
`MEETING_SUMMARY.md` §7). Built an independent, deliberately conservative
(higher than that empirical number) estimate from the actual prompt/response
text on disk instead:

- **Input**: a real `subtype_prompts.build_messages()` system+user pair
  measured at ~2,150 characters for a typical row (short definition block +
  one verse). Used **850 tokens/call** (Arabic-heavy text tokenizes closer
  to 2-3 chars/token than English's ~4).
- **Output**: the actual `exists`+`appearance`+`reasoning` JSON across all
  1,140 rows in every `*_all.jsonl` (the authoritative, reasoning-enabled
  data) averages **246 characters** (max 486). Used **120 tokens/call**.
- Cross-check: at these assumptions, Gemini's own price table
  (1.50/9.00) gives ~$0.0024/call — **~35% above** the real $0.00175/call
  logged in `MEETING_SUMMARY.md`, i.e. the estimate below already has a
  safety margin built in, not an optimistic one.

| Model | $/call | 1,140 calls |
|---|---|---|
| Claude Sonnet 4.6 | 850×3.00e-6 + 120×15.00e-6 = $0.00435 | **$4.96** |
| GPT-5.4-mini | 850×0.75e-6 + 120×4.50e-6 = $0.00118 | **$1.34** |

**Total: ~$6.30**, +~15% buffer for parse-error retries/malformed-JSON
re-asks (the project's own history shows this happens occasionally, e.g.
Phase 1 §6.3's 2/40 malformed-JSON case) → **~$7.25, still under $10.**

## Gate

Per the task's step 3 (and the fact that **total < $10**), this estimate
authorizes proceeding automatically — but see note below.

**Note on CLAUDE.md's stricter standing rule**: CLAUDE.md §"Standing
experiment discipline" item 5 says cost estimate + **explicit user
confirmation** before any paid API call, "every time, no exceptions" — a
stricter bar than this task's "$10 auto-proceed" instruction. Following the
project's own stricter, more conservative standing rule: **real API spending
will wait for an explicit go-ahead in chat**, even though the estimate is
under $10.

**User response (2026-10-07): the ~$6.30 full 2-model/2-run run was judged
too expensive. Cheaper options requested below; still no paid calls made.**

## Cheaper options (same $/call rates as above: Claude $0.00435/call, GPT-5.4-mini $0.00118/call)

The 10-subtype stratified sample below (option C/D's "sample") was chosen to
span all 4 parent elements and both high- and low-recall subtypes from
Gemini's existing results, every one with n≥10 (consistent with this
project's own `MIN_RELIABLE_N` cutoff — see `score_crossmodel.py`), so a
sample-based comparison isn't resting on single-digit denominators:

| Subtype | Parent | n (rows) | Gemini naive recall | Gemini strict recall |
|---|---|---|---|---|
| استعارة فعل | مجاز (Trope) | 110 | 0.627 | 0.264 |
| كناية عن صفة | كناية (Periphrasis) | 74 | 0.676 | 0.446 |
| كناية عن موصوف | كناية (Periphrasis) | 61 | 0.590 | 0.262 |
| مجاز عقلي | مجاز (Trope) | 54 | 0.704 | 0.463 |
| طباق إيجاب | طباق (Antithesis) | 38 | 0.605 | 0.237 |
| كناية لغوية | كناية (Periphrasis) | 32 | 0.938 | 0.719 |
| تشبيه مطول | تشبيه (Simile) | 30 | 0.967 | 0.833 |
| استعارة تمثيلية | مجاز (Trope) | 28 | 0.143 | 0.143 |
| كناية عن فعل | كناية (Periphrasis) | 27 | 0.778 | 0.333 |
| مجاز مرسل | مجاز (Trope) | 24 | 0.583 | 0.292 |
| **Sample total** | | **478** | | |

| Option | What runs | Calls | GPT-5.4-mini cost | Claude cost | **Total** |
|---|---|---|---|---|---|
| **A** | GPT-5.4-mini only, full 570 rows, 2 runs | 1,140 | $1.342 | — | **$1.34** |
| **B** | GPT-5.4-mini only, full 570 rows, 1 run | 570 | $0.671 | — | **$0.67** |
| **C** | Both models, 478-row sample, 1 run each | 478+478=956 | $0.563 | $2.079 | **$2.64** |
| **D** | GPT-5.4-mini full 570 rows (1 run) + Claude on 478-row sample (1 run) | 570+478=1,048 | $0.671 | $2.079 | **$2.75** |
| *(for reference)* C at 2 runs | Both models, 478-row sample, 2 runs each | 478×2×2=1,912 | $1.126 | $4.159 | **$5.28** |

**Claude is indeed the dominant cost in every option that includes it** — at
these rates it's ~3.7x GPT-5.4-mini's per-call price, matching the ratio
already visible in `pilot_3models/config.py`'s pricing table.

**Recommendation — option C (both models, 478-row stratified sample, 1 run
each, ~$2.64) is the cheapest option that still gives a usable cross-model
recall comparison** against Gemini's existing data: it's the only one of A-D
that puts both new models on the *same* rows Gemini was scored on, across
all 4 parent elements and both easy and hard subtypes, rather than
comparing GPT alone (A/B) or two different row sets for GPT vs Claude (D).

**One caveat worth flagging before you pick:** CLAUDE.md's standing
discipline (#2) treats a single run as unreliable for any comparative
conclusion — a real past incident in this project (Phase 1's Kenning
F1 doubling on one run, halving on the second — `PROJECT_STATE.md` §6.1) is
exactly why the 2-run-minimum rule exists. **Options B, C, and D's "1 run"
variants, and even A if you only count GPT's own numbers against Gemini's
already-2-run data, carry that same single-run noise risk** — a cross-model
delta built on 1 run per new model could be partly noise, not a real model
difference. The 2-run version of the sample (last row, **$5.28**) is the
cheapest option that doesn't trade away the project's own reliability rule.
No calls made; awaiting your choice.
