# Phase 4 Session Log — repo snapshot before new work

Append-only. Each entry: timestamp, what, why, commands, outcome.

---

**2026-10-10T00:00 (session start)** — Task: snapshot the repo before starting Phase 4 work. No API calls, no experiments.
- Read `CLAUDE.md` and `NEW_SESSION_HANDOFF.md` for standing rules and current project state (already done earlier in this session — DEV/TEST discipline, 2-run majority, span-level scoring, cost-confirmation-before-API-calls, RTL rules for .docx).
- Created this log file (`docs/phase4/SESSION_LOG.md`).

**2026-10-10T00:05** — Secret scan.
- Why: step 3 requires scanning all untracked/modified files for leaked credentials before staging anything.
- Commands: `git status --porcelain=v1 -uall` (full untracked+modified list, 368 lines, saved to scratchpad); `Grep` for API-key-shaped patterns (`sk-...`, `sk-ant-...`, `AIza...`, `hf_...`, `Bearer ...`, PEM private-key headers) across the repo; targeted grep for hardcoded `OPENAI_API_KEY =` / `ANTHROPIC_API_KEY =` / `GEMINI_API_KEY =` assignments in `experiments/`.
- Outcome: no matches. No stray `.env`/`key.txt`/`token.txt`/`keys/` files among the untracked set (already covered by `.gitignore` if they existed). Nothing to redact.

**2026-10-10T00:10** — Large-file check.
- Why: step 4 requires asking before committing anything >5MB.
- Commands: sized every changed/untracked path against a 5MB threshold.
- Found: 2 root-level docs (`arabic rhetoric.pptx` 7.4MB, `Statistical Development...(1).pdf` 8.1MB) + 3 literature PDFs (`2022_Kim_SyuzhetLimits.pdf` 10.2MB, `2025_Fuchs_EmbeddingGenreHebrew.pdf` 7.8MB, `2026_Glass_AutomatedTaggingWilliamBlakeArchive.pdf` 24.4MB).
- Asked the user via AskUserQuestion. Answer: commit them as-is.

**2026-10-10T00:15–00:30** — Committed in logical groups (as instructed), each after re-verifying no secrets/oversized surprises in the diff:
1. `31ebc74` — docs: `CLAUDE.md`, `GLOSSARY.md`, `NEW_SESSION_HANDOFF.md` (new) + `PROJECT_STATE.md` (modified, Phase 2 updates).
2. `91a3ab5` — `experiments/phase2_chatlike/` + `results/phase2_chatlike/` (Config A/B/C disentanglement experiment, 41 files).
3. `28cccb6` — `experiments/phase3_crossmodel/`, `experiments/phase3_subelements/`, `results/phase3_crossmodel/`, `results/phase3_subelements/`, `data/ground_truth/by_subtype/` (23-subtype taxonomy + cross-model check, 214 files).
4. `0613739` — `writing/` + `literature/` + `deep-research-report.md` + the 2 root-level large reference docs (paper draft, paper plan, DHQ/non-DHQ literature review, 108 files).
5. `8949746` — `experiments/pilot_3models/span_matching.py` alone, diff summarized in the message (guillemet-stripping fix, verified no-op on frozen Phase 1 numbers).
- `git status` after all 5 commits: clean except `docs/` itself (this log, intentionally held until the final step).

**2026-10-10T00:35** — Tagged `pre-phase4-snapshot` (annotated tag on the commit after all 5 groups). Confirmed with user before pushing (push is a shared/remote action).

**2026-10-10T00:40** — Push attempt #1: `git push origin main` then `git push origin pre-phase4-snapshot`.
- Result: HTTP 408 timeout mid-push (`RPC failed`, `unexpected disconnect while reading sideband packet`). Tag was not pushed (main push must succeed first). `git ls-remote` confirmed `origin/main` was untouched, still at `1633cf5` — far behind local `main` (12 unpushed commits, not just this session's 5 — the previous session's Phase 1-closure commits `13a85e5`/`a68e1b2`/`db23ccb`/`e80415a`/`9b7fff8`/`d8079eb` were apparently never pushed either).

**2026-10-10T00:45** — Push attempt #2: raised `http.postBuffer` to 500MB and disabled low-speed timeouts, retried `git push origin main`.
- Result: **rejected by GitHub's pre-receive hook**, not a network issue. Three files in the repo's history exceed GitHub's size limits:
  - `experiments/classifiers/trope/PartlyEmbedding/embeddings_out/dataset_with_embeddings.csv` — 73.56 MB (over the 50MB *warning* threshold, still pushable alone)
  - `experiments/classifiers/trope/FullEmbedding/embeddings_out/dataset_with_embeddings.csv` — 111.56 MB (**over GitHub's hard 100MB limit**)
  - `experiments/classifiers/kenning/PartlyEmbedding/embeddings_out/dataset_with_embeddings.csv` — 186.92 MB (**over GitHub's hard 100MB limit**)
  - Traced to commit `3d91e28` ("Reorganize project into data/experiments/results/writing/literature/archive") — a pre-existing commit from well before this session, already sitting in local history, unrelated to anything done in this task.
- **Push could not complete.** All 5 new commits + the tag exist locally (safe, nothing lost) but are **not yet on `origin/main`**. Fixing this requires rewriting history (e.g. `git filter-repo`/BFG to strip those 3 CSVs from the commit that introduced them, or moving them to Git LFS) followed by a force-push — a destructive/disruptive operation this session did not take without explicit instruction, consistent with how the same large-file problem was previously handled in `PROJECT_STATE.md` §7 (history rewrite "explicitly declined as too destructive/disruptive for this session").
- Flagging for the user to decide: (a) git-lfs migrate the 3 CSVs + force-push, (b) strip them from history entirely (they're regeneratable embedding caches, not source data) + force-push, or (c) leave `origin/main` behind and keep working locally for now.
