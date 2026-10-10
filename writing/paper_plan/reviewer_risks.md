# Reviewer Risks — What a DHQ Peer Reviewer Would Flag

Each risk: description, evidence it's real (not hypothetical), 2–3 fix options ranked by cost, and which is the minimum for submission vs. nice-to-have.

---

## 1. Single annotator, no inter-annotator agreement (IAA)

**Evidence it's real**: `writing/chapters/limitations_future_work.md` §1 states plainly "no inter-annotator agreement figure exists anywhere in this project." All ground truth across all 5 poems is Dr. Ali Hussein's manual analysis alone (`PROJECT_STATE.md` §1, `experiments/pilot_3models/ground_truth.py`). This is explicitly on the supervisors' own radar — Tsvika's feedback log (`PROJECT_STATE.md` Phase 2 §5 Entry 1) does not raise IAA directly, but Phase 2 §4 item 5 lists "second annotator for inter-annotator agreement — supervisor's call" as a still-open, unresolved item. DHQ's own related-work precedents (Bender et al. 2023, Zirker & Göggelmann 2023 — both flagged as "Must-cite" in `related_work_outline.md` §2c) treat measured annotator agreement as standard practice for exactly this kind of ambiguous-category task, which raises reviewer expectations specifically for this venue.

**Fix options**:
- Cheap: explicitly frame every precision/recall number as "against one expert's reading" throughout the paper (already drafted this way in `limitations_future_work.md` §1) and cite the DHQ precedents (Bender, Zirker) as acknowledgment that the field treats this as a known, unresolved limitation rather than an oversight. No new annotation needed.
- Moderate: a second annotator re-labels a stratified sample (e.g. the 13-verse shortlist already prepared in `results/phase2_chatlike/ali_adjudication_shortlist.md`, or a slightly larger ~50-100 verse sample) and report Cohen's κ or Krippendorff's α (both already flagged as candidate statistics in `related_work_outline.md` §2g). This produces a real, reportable IAA figure without re-annotating all 5 poems.
- Expensive: full second-annotator pass on all 5 poems (or at minimum the 3 TEST poems), enabling a true adjudicated gold standard rather than a single-annotator one.
- **Minimum needed for submission**: the cheap option — explicit limitation framing with DHQ-precedent citations. This is already drafted.
- **Nice-to-have, materially strengthens the paper**: the moderate option (IAA on the adjudication shortlist) — the shortlist already exists and the supervisor meeting that would produce it is a listed-but-unscheduled open item (`PROJECT_STATE.md` Phase 2 §4 item 4).

---

## 2. Small corpus (5 poems; TEST = 3 poems)

**Evidence it's real**: `PROJECT_STATE.md` §2, `limitations_future_work.md` §2 — 5 poems total, 3 held out as TEST. Antonymy/Antithesis support is as low as 1 instance on one DEV poem (Imru2) and 43 on the full TEST set (`methodology.md` §2 table). The project's own internal history records *two* documented reversals that only became visible when scaling from 2-poem DEV to 3-poem TEST (§3c's subtype reversal; §3d's antithesis over-claiming pattern, invisible at DEV's n=5). This is not a hypothetical reviewer concern — it already happened twice inside the project's own data.

**Fix options**:
- Cheap: state the reversal-on-scaling findings explicitly as *evidence for*, not just an admission of, the small-corpus limitation — i.e., turn the limitation into a methodological finding the paper can claim credit for discovering (already drafted this way in `methodology.md` §7 and `limitations_future_work.md` §2).
- Moderate: add one additional poem's ground truth (Phase 1 §5.3's "fresh held-out poem" item, Phase 2 §4 item 3) — but this requires new expert annotation, not just more model calls, and is explicitly flagged in the source documents as "a scope/resourcing decision for the supervisor... not something this codebase can decide or start on its own."
- Expensive: a substantially larger corpus (tens of poems) — not discussed anywhere in the project's current planning documents as a near-term option.
- **Minimum needed for submission**: the cheap option (honest, evidence-backed framing). Already drafted.
- **Nice-to-have**: the moderate option (one more poem) — explicitly the single most "ready to request" extension, since the ground-truth annotation gap is well-defined and the harness already supports adding a poem (`config.py`'s `POEMS` registry).

---

## 3. Low absolute F1 for Kenning/Periphrasis (and modest numbers generally)

**Evidence it's real**: Table 1 in `results_for_paper.md` — Periphrasis strict F1 never exceeds 0.176 anywhere in the frozen TEST evaluation, against Simile's 0.65-0.73 ceiling. A reviewer could reasonably ask "is this paper reporting a negative result?"

**Fix options**:
- Cheap: reframe explicitly as a *diagnostic* contribution rather than a performance claim — the paper's value is in characterizing *where and why* LLMs fail (the marker-explicitness hypothesis in `discussion_draft.md`, the recall-decomposition analysis in `recall_decomposition.md`), not in reporting a high headline number. This is squarely what `deep-research-report.md`'s positioning advice recommends ("an evaluation study with a humanities research contribution," not "LLM did well").
- Moderate: include Phase 2's Config C finding (strict F1 0.111→0.316 on Imru2 via free-form reasoning) as evidence that periphrasis detection is *reachable*, just not by the strict-JSON zero-shot format Phase 1 used — this converts "the number is low" into "the number is low under one specific pipeline design, and we have evidence of why, and evidence that an alternative pipeline moves it substantially, with a clearly documented reliability cost."
- Expensive: pursue fine-tuning (already flagged as future work, `limitations_future_work.md` §7) to actually raise the ceiling before submission — a multi-week, nontrivial-cost undertaking, not realistic for this submission cycle.
- **Minimum needed for submission**: the cheap reframing, which is largely already present in the discussion draft.
- **Nice-to-have**: incorporating Config C's finding into the main narrative (currently sitting only in Phase 2 documents, not yet in any chapter draft) — see `paper_mapping.md` for exactly where this needs to be folded in.

---

## 4. Phase 3 findings are single-model (Gemini only) and recall-only

**Evidence it's real**: `results/phase3_subelements/MEETING_SUMMARY.md` §5 ("Model used and why" — Gemini 3.5 Flash chosen for cost, explicitly not cross-validated against Claude/GPT) and §4 ("this design only tests recall... FP/TN/Precision/F1 are not measurable from this run"). This is the single most exposed piece of evidence in the whole project if a reviewer zeroes in on subtype-level claims, since the entire 23-subtype breakdown rests on one model and no precision figure.

**Fix options**:
- Cheap: do not present Phase 3 numbers as comparable to Phase 1's 3-model F1 results; present them explicitly as a single-model, recall-only screening pass whose purpose was to generate hypotheses about which subtypes are hard, not to establish final subtype-level performance. State this limitation in the same sentence as every Phase 3 number, not in a separate footnote.
- Moderate: run the existing negative-sampling design that is "designed but not run" (`MEETING_SUMMARY.md` §4) for at least the subtypes with the most striking numbers (استعارة تمثيلية 7.1%, كناية نسبة 0%) to get a real precision/F1 figure for the subtypes the paper most wants to discuss.
- Expensive: replicate the full 23-subtype x negative-sampling design across all 3 models — the full Phase 1-grade treatment of the sub-taxonomy.
- **Minimum needed for submission**: the cheap framing. If Phase 3 numbers are used in the paper at all, they must be clearly scoped as single-model/recall-only in the same breath they're reported.
- **Nice-to-have**: the moderate negative-sampling follow-up on the 2-3 most interesting subtypes — cheap relative to a full redo and would materially upgrade the paper's strongest subtype-level claim (استعارة تمثيلية's dramatic small-sample-to-full-scale reversal) from "recall dropped" to "F1 dropped," which is the number reviewers will actually want.

---

## 5. Model version drift / reproducibility over time

**Evidence it's real**: every model in this project is a hosted commercial API (`claude-sonnet-4-6`, `gpt-5.4-mini`, `gemini-3.5-flash`, plus `claude-fable-5` in Phase 2), pinned only by model-ID string, with no guarantee the provider won't silently update weights behind that ID. `methodology.md` §5 documents the exact model IDs and pricing "at the time," language that itself signals the authors are aware this could change. `deep-research-report.md`'s literature synthesis explicitly flags this as a DHQ-relevant concern (Hua & Raley 2023's "model names and API calls should not be treated as interchangeable black boxes").

**Fix options**:
- Cheap: state exact model IDs, call dates, and temperature/sampling settings in the methods section (already done in `methodology.md` §5) and add an explicit sentence acknowledging that hosted-model reproducibility over time is a known limitation of this experimental design, citing Hua & Raley 2023 and/or Ziemińska 2026 (DSH, found explicit "absence of reproducibility" with Gemini-2.5-Pro on a comparable task per `novelty_gap.md`).
- Moderate: archive every raw model response (already done — `results/pilot_3models/*/raw/*.txt`, `run_manifest.json` per run) and state in the paper that raw outputs are preserved for exactly this reason, so a future re-run can be compared against this project's frozen snapshot even if it can't reproduce it exactly.
- Expensive: re-run the frozen TEST evaluation at paper-acceptance time to confirm numbers haven't drifted — directly forbidden by this project's own TEST-is-spent discipline (`PROJECT_STATE.md` §2) and therefore not a real option without violating the project's own methodology.
- **Minimum needed for submission**: the cheap option, largely already present.
- **Nice-to-have**: the moderate option (explicit "raw outputs archived" statement) — essentially free, since the archiving already happened; just needs a sentence in the methods/data-availability section.

---

## 6. No fixed temperature/seed control beyond temperature=0

**Evidence it's real**: `methodology.md` §5 states temperature=0 for all three models but does not mention any seed control, and none of the provider wrapper code reviewed in this session (`providers.py` references throughout `PROJECT_STATE.md`) is described as passing a seed parameter. Despite temperature=0, the project's own data shows real run-to-run non-determinism (`PROJECT_STATE.md` §6.1-§6.2: Gemini's Kenning behavior specifically, 77-89% agreement; the single-run artifact that motivated the entire 2-run-majority protocol). This is already well-documented as an empirical fact, just not framed as a "no seed control" methods gap explicitly.

**Fix options**:
- Cheap: add one sentence to the methods section noting that temperature=0 does not guarantee determinism for any of the three providers used, and that this motivated the 2-run-majority protocol — turning what could read as an oversight into a stated, evidence-backed design decision.
- Moderate: investigate whether any of the three providers expose a seed parameter and, if so, re-run a small DEV check with a fixed seed to quantify how much of the residual variance a seed removes — informative but not essential, and would need fresh cost confirmation per standing discipline.
- Expensive: not applicable — there is no way to force full determinism from a hosted commercial LLM API end-to-end; this is a structural limitation of the model class, not something more spend fixes.
- **Minimum needed for submission**: the cheap framing sentence.
- **Nice-to-have**: the moderate seed investigation, mainly for intellectual completeness, not because the current 2-run-majority protocol is inadequate without it.

---

## 7. Licensing / rights status of the ground-truth corpus

**Evidence it's real**: a repo-wide search for "license," "rights," "copyright," "IRB," "ethics," "consent" (case-insensitive) in this session found no file in `data/`, `PROJECT_STATE.md`, `GLOSSARY.md`, or any `writing/`/`literature/` document that states the licensing or usage-rights status of the Haifa/Dr. Ali Hussein ground-truth annotations (`data/ground_truth/ali_ana/original/*.xlsx`) or the underlying poem texts (`archive/Forth_Step/Data/*/poetry.txt`). **Not found** anywhere searched.

**Fix options**:
- Cheap: ask the supervisor/Dr. Hussein directly what the data-sharing terms are (internal project use vs. publishable-with-attribution vs. restricted) before any public release of the annotation files, and state the answer explicitly in a data-availability statement — DHQ's AI policy and the 2026 Tarkka precedent (`dhq_format_guide.md` part (b)) both suggest DHQ now expects this kind of statement.
- Moderate: if the annotations cannot be shared in full, prepare a redacted or aggregate-only release (e.g., span offsets + element labels without full poem text, if the poem texts themselves have separate rights status) suitable for a "data availability" section.
- Expensive: formal rights clearance/licensing agreement with Haifa University if the data is to be redistributed as a companion dataset to the paper — a process outside this codebase's control and likely outside the timeline of this submission cycle.
- **Minimum needed for submission**: the cheap option — explicitly ask and document the answer. **This is currently an open question, not yet resolved, and should be treated as a blocker for any data-availability claim in the paper** (see `TOP_5_BLOCKERS.md`).
- **Nice-to-have**: the moderate option, if the cheap option reveals restrictions that a redacted release could work around.

---

## 8. Other issues found while reading

### 8a. TEST-set leakage via `data/elements/*.txt`'s worked examples
**Evidence it's real**: `results/phase2_chatlike/example_gap_analysis.md` §0 — "3 of every element file's 4-5 examples (60-75%) are drawn from TEST poems... the frozen TEST run has, since Phase 1, shown the model [a] 'this verse contains element X' example drawn from the exact poem... it is later asked to score." This is a genuine methodology gap present in every frozen Phase 1 number, discovered in Phase 2, and explicitly **not yet reflected** in `limitations_future_work.md` (which predates this finding).

**Fix options**:
- Cheap: add this as an explicit new limitation in the paper (it is not yet in any chapter draft — see `paper_mapping.md`), quantified as "practical impact likely small but non-zero and unquantified" per the source document's own honest hedge.
- Moderate: quantify the impact directly — re-score TEST with the contaminating examples swapped for DEV-only or synthetic examples, on at least one model, to measure how much (if any) of the frozen F1 is attributable to this leakage. This would require fresh API calls and cost confirmation, and raises the question of whether such a re-score would count as "touching TEST" under the project's own frozen-TEST discipline (it would be evaluating a *different* configuration against TEST, not re-scoring the same one — this needs an explicit decision, not a default).
- Expensive: rebuild the entire example set from non-corpus sources (classical rhetoric textbooks, as partially sketched for the now-invalidated `PROPOSAL_fewshot.md`) and re-run the full TEST evaluation under the new prompt as a *new*, clearly-labeled configuration (not a retroactive edit of Phase 1's frozen numbers).
- **Minimum needed for submission**: the cheap option. **This is a must-fix before submission in the sense that it must be disclosed** — omitting it after it has already been discovered and documented internally would be a disclosure problem, not just a missed opportunity, if reviewers or the supervisor later notice `example_gap_analysis.md` already existed.
- **Nice-to-have**: the moderate quantification.

### 8b. Phase 1/Phase 2 code and data were uncommitted to git for an extended period
**Evidence it's real**: `PROJECT_STATE.md` §7's "Housekeeping note" (end of file) — at the start of the 2026-07-26 session, all of `CLAUDE.md`, `GLOSSARY.md`, `experiments/phase2_chatlike/`, `results/phase2_chatlike/`, and a `span_matching.py` fix were untracked/uncommitted, and the current git status (visible in this session's environment) still shows many of these as untracked (`?? experiments/phase2_chatlike/`, `?? results/phase2_chatlike/`, etc.) alongside Phase 3 and literature-review material.
**Fix options**: Cheap — commit everything before submission so the repository the paper's data-availability statement points to is actually complete and version-controlled. This is a housekeeping risk, not a scientific one, but a DHQ reviewer who follows a repo link to a state that doesn't match the paper would be a bad look. **Minimum needed for submission**: commit the work (not performed by this task per its own constraints — flagged for the user to do separately).

### 8c. Exposed API keys in git history
**Evidence it's real**: `PROJECT_STATE.md` §7 documents 48 files with live-looking credentials that were committed and pushed to the public GitHub remote, redacted in-place in commit `13a85e5` but **never removed from git history**, with an explicit note that "every one of these keys needs rotating at its provider... that action is on the user, not something this session could do." This is a security risk, not a peer-review risk per se, but worth flagging since a public DHQ-linked repo makes this history more visible, not less.
**Fix options**: Cheap — confirm all keys were already rotated (the note implies this may not have happened yet). Moderate — history rewrite (BFG/filter-branch + force-push), previously declined as too disruptive. **Minimum needed for submission**: confirm key rotation happened; do not necessarily need the history rewrite if rotation is confirmed.
