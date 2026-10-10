I'm continuing work on my MSc thesis project (Metaphorical_Analysis — LLMs identifying rhetorical elements in classical Arabic poetry). Read `PROJECT_STATE.md` first — it's the maintained single source of truth, kept current across sessions. Then `CLAUDE.md` for standing rules. This message is just fast orientation on top of those.

## Where things stand

**Phase 1** (closed, frozen, `PROJECT_STATE.md` §1-§7): baseline vs. v4_combined prompt, 3 models, TEST = Imru1+Jarir+Abu_Tammam, DEV = Imru2+Nabigha. v4_combined wins Trope/Simile/Antonymy, Kenning barely moves. Never re-run, never re-scored — TEST is spent.

**Phase 2** (open, `PROJECT_STATE.md` §0 onward) — triggered by a supervisor terminology correction (طباق=antithesis not antonymy, كناية=periphrasis not kenning, مجاز has 3 subtypes: استعارة/تمثيل/مجاز مرسل) plus a chat-interface observation that free-form reasoning caught a periphrasis every Phase 1 config missed. Two sessions so far:

**Session A (2026-07-23, §0-§6)** — three configs isolating *why*: Config A (Fable 5, same prompt) = clean recall gain, zero precision cost. Config B (terminology-only) = small Trope gain, no Kenning gain. Config C (free-form reasoning, per-verse, two-stage) = biggest Kenning/periphrasis gain, catches the motivating verse, but at real precision cost and — critically — **not reliably reproducible run-to-run** (a targeted probe found 4/10 known-positive verses caught in ≥1 of 2 runs, but only 1/10 survive 2-run majority). Also answered a supervisor same-poet question from a per-poem re-slice (no clear poet-consistency effect). Deliverables: `results/phase2_chatlike/report_3i.md`, `error_characteristics_summary.md`, `ali_adjudication_shortlist.md` (13 verses for an annotator review session), `meeting_brief.docx`, `PROPOSAL_fewshot.md` (a designed-not-run experiment).

**Session B (2026-07-26, §7)** — analysis-only, zero API calls, in response to a follow-up supervisor note (also logged verbatim, §5 Entry 2). Four deliverables: a verse-by-verse reasoning docx (Config C's actual Arabic reasoning, readable), a full recall/FN decomposition of frozen TEST (1,031 FN events bucketed by cause — schema cap, subtype-knowledge gap, boundary confusion, model-capability, format-suppression), an example-vs-test gap analysis, and a discussion-chapter draft refining "simple vs. complex" into a marker-explicitness hypothesis.

## The one thing you need to know before touching anything

Session B's example-gap analysis found that **`data/elements/*.txt`'s canonical worked examples are majority drawn from TEST poems themselves** (3 of every file's 4-5 examples, verified verbatim) — a real methodology gap present since Phase 1. This **directly contradicts a factual claim in `PROPOSAL_fewshot.md`** (which asserted these examples were "never drawn from the 5 annotated poems"). That proposal's demonstration-selection plan is currently wrong and needs new source material before it is ever run. Full detail: `results/phase2_chatlike/example_gap_analysis.md` §0.

## Open items (`PROJECT_STATE.md` Phase 2 §4, not yet done)

1. Nabigha full-poem Config C run — budget-held (~$11.9 estimated), would give real precision/F1 on a second poem.
2. Few-shot demonstration experiment — designed but **needs rework** per the contradiction above before running.
3. Fresh-poem validation — needs supervisor (new ground-truth annotation required).
4. Error-review session with Dr. Ali Hussein — shortlist ready, not yet scheduled.
5. Second annotator for inter-annotator agreement — supervisor's call.

## Standing discipline (also in `CLAUDE.md`)

DEV/TEST is a hard boundary, TEST stays spent. 2 runs minimum, 2-run majority is primary. Report raw TP/FP/FN always. Span-level scoring, both criteria. **Cost estimate + my explicit confirmation before any API call, every time, no exceptions.** New terminology (antithesis/periphrasis/مجاز subtypes) applies to new writing only — Phase 1 frozen docs keep original terms.
