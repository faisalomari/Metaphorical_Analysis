# Gap statement draft (DHQ paper)

Drafted 2026-10-07, after the task-2 re-assessment of the novelty claim against Attia et al. 2026 (Kinayat) and the two Kühn et al. rhetorical-figures papers (see `novelty_gap.md`, "Update (2026-10-07)" section). Every claim below is backed by a verified source in `RELATED_WORK_INDEX.md` / `DHQ_LITERATURE_INDEX.md`, scoped to the search terms and venues documented in `novelty_gap.md` §"Exact search scope." Word count target: ~150 words.

## Draft gap statement (~150 words)

Automatic identification of rhetorical elements in classical Arabic poetry has so far relied on rule-based systems, which Abd Alhadi, Hussein and Kuflik (2023) show can reach high precision and recall overall — but only by explicitly excluding metaphor and periphrasis (kinaya) as too semantically demanding for rule-based matching. Large language models are a natural candidate for exactly this gap, and two adjacent literatures already show the ingredients exist separately: rigorous multi-model LLM benchmarking of named rhetorical figures beyond metaphor and irony (Kühn, Mitrović and Granitzer 2024), and a 22-model, quantified benchmark of LLMs on Arabic figurative language (Attia et al. 2026) — but for modern colloquial idioms and proverbs, not classical poetry or named balagha categories. No existing study evaluates multiple LLMs on the identification of named classical Arabic rhetorical elements, including the semantically demanding cases rule-based systems cannot handle, against expert-annotated ground truth with a span-level, difficulty-stratified evaluation.

## Research questions

**RQ1.** How accurately can current large language models identify named classical Arabic rhetorical elements (antithesis/طباق, periphrasis/كناية, metaphor/استعارة, metonymy/مجاز مرسل) in classical Arabic poetry, measured at the span level against expert-annotated ground truth?

**RQ2.** Does LLM identification accuracy vary systematically by rhetorical-element type, and in particular, do the elements that Abd Alhadi et al. (2023) excluded as "too semantic" for rule-based detection (metaphor, periphrasis) show a different accuracy and error profile than the more surface-marked elements (antithesis) their rule-based system already handles well?

**RQ3.** Does evaluating multiple LLMs (rather than a single model, as in Al Kaabi et al. 2024) reveal consistent cross-model difficulty patterns by element, or does difficulty vary idiosyncratically by model — and how do any such patterns compare to the general difficulty findings reported for non-Arabic, non-classical rhetorical-figure detection (Kühn, Mitrović & Granitzer 2024) and for Arabic figurative language more broadly (Attia et al. 2026)?

## Notes on scope and wording discipline

- "No existing study" is scoped to the search described in `novelty_gap.md` (DHQ full-text search; ACL Anthology, arXiv, CHR, JLCL, DSH, and targeted Arabic-rhetoric web search terms, through 2026-10-07) — not a claim of exhaustive coverage of every NLP/DH venue.
- The gap statement deliberately does **not** claim novelty for "LLMs on Arabic figurative language" in general (Attia et al. 2026 already does this well) or for "multi-model rhetorical-figure benchmarking" in general (Kühn et al. 2024's survey shows this methodology exists, just not for Arabic) — only for the specific intersection of classical Arabic poetry + named balagha elements + span-level, difficulty-stratified, multi-model LLM evaluation.
- RQ2 and RQ3 are phrased as empirical questions (not yet asserted answers) since Phase 2 TEST results were not reviewed as part of this session's literature task — do not state a finding here that the experiments haven't confirmed.
