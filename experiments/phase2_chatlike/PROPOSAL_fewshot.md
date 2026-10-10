# Proposal (designed, not run) — Few-shot demonstration variant

**Status**: design only, written 2026-07-23. No code, no API calls. Logged as an open item in `PROJECT_STATE.md`.

## Motivation

This session's three configurations showed three different effects:
- **Model** (Config A): free recall gain, no precision cost, cheap (whole-poem batching).
- **Terminology** (Config B): small, element-specific gain, cheap.
- **Format** (Config C): the largest Kenning/مجاز مرسل recall gain of anything tried, but expensive (per-verse batching, ~4-8× Phase 1's known cost tax) and — per the probe in `report_3i.md` §8-§9 — **not reliably reproducible run-to-run** (2-run majority collapses most of the any-of-2-runs signal).

Config C's gain comes from letting the model reason freely before answering. That reasoning is expensive to elicit at inference time on every verse. The open question: **can some of that same gain be taught via a handful of worked few-shot demonstrations embedded in the system prompt, rather than elicited fresh per verse?** If so, it would recover part of Config C's benefit at Config A/B's cost (whole-poem batching, no per-verse overhead, no second free-form-reasoning stage).

## Design

**Base**: Config B's system message (terminology-corrected v4_combined) — chosen as the base rather than raw v4_combined so the demonstration effect is isolated from the terminology effect already measured.

**Demonstrations added**: 2-3 worked examples, each showing a verse → brief worked reasoning (2-3 Arabic sentences, in the style of Config C's Stage 1 but compressed) → the correct strict-JSONL line. Critically, **demonstrations must be drawn from outside DEV and TEST** to avoid any leakage into the eventual evaluation:
- Reuse `data/elements/{Kenning,Trope}.txt`'s own existing canonical example couplets (already shipped with the element definitions, never drawn from the 5 annotated poems) — these currently illustrate definitions only; this proposal adds worked reasoning to 1-2 of them.
- For مجاز مرسل specifically (the subtype with no worked example anywhere in Phase 1's prompts): use the two canonical examples already established in `GLOSSARY.md`/Config B's system message (السماء تمطر / أراني أعصر خمراً), extended into full demonstrations (verse → reasoning → JSONL line) rather than the current brief in-line note.

**Output format unchanged**: the real poem is still analyzed in the existing strict, no-explanation JSONL format — only the *system prompt* gains demonstrations, not the *per-verse task*. This keeps the call shape (and cost) identical to Config A/B: one call per poem per run, no second stage.

**Models**: Sonnet 4.6 (isolates the few-shot effect from the already-measured model effect) and, if the first result is promising, Fable 5 (tests whether the two effects stack).

**Scope**: DEV only (Imru2 + Nabigha), 2 runs, per standing discipline. TEST untouched.

**Question this answers**: does teaching the reasoning pattern via demonstration recover part of Config C's Kenning/مجاز مرسل gain without Config C's per-verse cost and — this is the part actually worth testing given §9's finding — **without Config C's run-to-run non-determinism**, since the model isn't doing fresh open-ended reasoning per verse, just pattern-matching against worked examples inside an otherwise-closed-form task.

## Cost estimate (not yet run — would need fresh confirmation before executing)

Same call shape as Config A/B (whole-poem, 2 poems, 2 runs = 4 calls per model tested), with a system prompt a few hundred tokens longer than Config B's. Rough order: **~$0.35-0.55 on Sonnet 4.6 alone**, similar order to Config B's measured $0.27; roughly double if also run on Fable 5. Would need real `count_tokens` figures and explicit confirmation before any API call, same as every other configuration this cycle.
