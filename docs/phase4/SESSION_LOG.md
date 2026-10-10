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

---

**2026-10-10T01:00** — New task: gather facts for planning a few-shot example-sensitivity experiment. No API calls, no new analysis beyond a difficulty ranking. Output: `docs/phase4/INFO_REPORT.md`.
- Read `PROJECT_STATE.md` (full, both pages — Phase 1 §1-§7 and Phase 2 §0-§7) and `NEW_SESSION_HANDOFF.md` for current frozen numbers and open items.

**2026-10-10T01:10** — Per-element/subtype performance (report §1).
- Pulled frozen TEST table (§3a), Trope subtype table (§3c), and Phase 2 §3i Config A/B/C DEV numbers directly from `PROJECT_STATE.md` (no re-derivation, no new scoring run).
- Read `results/phase3_subelements/MEETING_SUMMARY.md` and `results/phase3_crossmodel/summary.md` for subtype-level recall (Gemini vs GPT-5.4-mini, span-level strict/token) — noted explicitly that Phase 3's design makes precision/F1 mathematically undefined (recall-only), not just unmeasured.
- Ranked the 4 elements by v4_combined mean strict F1 (Simile easiest ≈0.70, Trope ≈0.29, Antonymy ≈0.165, Kenning hardest ≈0.109) and picked 3 mid-difficulty subtype candidates (مجاز عقلي, كناية عن صفة, استعارة فعل) reasoned from n-size, cross-model/cross-criterion consistency, and distance from floor/ceiling; explicitly excluded طباق إيجاب (criterion-sensitive) and استعارة تمثيلية (documented sample-instability) from the "mid" recommendation.

**2026-10-10T01:20** — Example injection + leakage map (report §2).
- Read `experiments/pilot_3models/prompts.py` (`build_system_message`), `data/elements/Trope.txt`, `data/elements/Kenning.txt` directly to confirm the per-file template (header fields + N bare example verses, no span/subtype labels).
- Read `results/phase2_chatlike/example_gap_analysis.md` in full for the byte-verified leakage table (19 examples, one per poem in fixed order, 3-of-5 drawn from TEST poems) and cross-checked its claim against `experiments/phase2_chatlike/PROPOSAL_fewshot.md`'s contradicted premise.

**2026-10-10T01:30** — Ground-truth format + scoring entry points (report §3).
- Read `experiments/pilot_3models/ground_truth.py` (xlsx columns, SUBSTRING_MAP, dedup logic, output shape) and `span_matching.py` (normalize/strict_overlap/token_overlap_ratio/token_match/best_match) directly, source code only.
- Read `experiments/pilot_3models/span_scoring.py` (`majority_exists_and_appearance`, `score_span_level`) and grepped `analyze.py` function signatures (`prf1`, `load_all_runs*`, `run_consistency`, etc.) rather than reading the whole file, since PROJECT_STATE's file index already names their purpose — confirmed signatures only.

**2026-10-10T01:40** — Token usage and cost (report §4).
- Ran a local, read-only Python one-liner (via Bash tool) over `results/pilot_3models/test_final/**/run_manifest.json` and `results/pilot_3models/dev_variants/v4_combined/**/run_manifest.json` to compute per-poem, per-provider average input/output tokens and derived cost (using `config.py`'s pricing table) — no network calls, no API calls, pure arithmetic over already-stored JSON.
- Repeated the same read-only computation over `results/phase2_chatlike/{config_a,config_b,config_c}/**/run_manifest.json` for Fable 5 / Config B / Config C; read `results/phase2_chatlike/config_c/Imru2/run_manifest.json` directly (not just via script) to confirm the two-stage usage schema (`stage1_input_tokens` etc.) before computing its cost.
- Read `experiments/phase2_chatlike/phase2_config.py` for Fable 5's pricing ($10/$50 per MTok) and `experiments/pilot_3models/providers.py` to confirm no prompt-caching exists anywhere in the call wrappers.

**2026-10-10T01:50** — Poets/poems (report §5) and batching/resume logic (report §6).
- Read `experiments/pilot_3models/config.py`'s `POEMS` dict directly for poet names, titles, and verse counts per poem — no new computation needed, values transcribed as-is.
- Read `experiments/pilot_3models/run_pilot.py` and `run_per_verse.py` in full for the resume/retry mechanisms (`run_indices` override + manifest-extend in `run_pilot.py`; `--providers` filter + replace-not-append + the `error`-vs-`verse_errors` convention in `run_per_verse.py`) — confirmed no provider-side batch API and no poem-level batching loop exists in the repo today.

**2026-10-10T02:00** — Wrote `docs/phase4/INFO_REPORT.md` (all 6 sections + a "sources consulted" list). No API calls at any point in this task. Committing and pushing next.

**2026-10-10T02:05** — Committed `82c1fb0` (`docs/phase4/{SESSION_LOG.md,INFO_REPORT.md}`). `git push origin main` rejected again by GitHub's pre-receive hook — same pre-existing large-file-in-history issue first hit at 2026-10-10T00:45 (the 3 `dataset_with_embeddings.csv` files from commit `3d91e28`, up to 186.92MB, unrelated to this session's changes). Did not attempt a history rewrite/force-push (destructive, not instructed). `82c1fb0` exists locally on `main`, on top of the already-unpushed commits from earlier this session — still waiting on the user's decision from the earlier flag (git-lfs migrate / strip from history / leave local-only).

---

**2026-10-10T02:10** — New task: download all of Dr. Ali Hussein's manually analysed poems from `https://arabic-rhetoric.haifa.ac.il/manual-analysis/poems`. No LLM API calls (pure web scraping). Relates directly to blocker #1 in `writing/paper_plan/TOP_5_BLOCKERS.md` (undocumented licensing status of this corpus) — this task's README will flag that explicitly rather than resolve it.
- Read `CLAUDE.md`, `NEW_SESSION_HANDOFF.md`, and re-confirmed `TOP_5_BLOCKERS.md` item 1 for context before starting.
- Phase A (recon only): check robots.txt + terms/licensing notices, inspect page structure (pagination, static/JS/API), estimate poem count/size, propose scraper approach. Will stop and report before any download (Phase B gated on user approval).

**2026-10-10T02:15–02:45** — Phase A recon, via built-in browser (no download, no writes outside this log).
- `https://arabic-rhetoric.haifa.ac.il/robots.txt` and every other non-`/api` path (`/terms`, `/license`, `/privacy`, `/copyright`, `/about-us/terms`) all return HTTP 200 serving the same Angular SPA shell (client-side catch-all router defaulting to `/welcome`) — confirmed via raw `fetch()` with `redirect:'manual'`. **No real robots.txt exists, and no terms/license/privacy/copyright page exists anywhere on the site.** Only `/api/*` paths give real 404s ("Route not found") for unknown endpoints, confirming the SPA-shell-for-everything behavior is real, not a probing artifact.
- `/welcome` and `/about-us/research-team` (real content pages) carry no licensing/rights/reuse statement — just a mission description and team contact list (Prof. Ali Hussein, Prof. Tsvi Kuflik, developer Fawzi Abu Elhija, 4 research assistants). © 2022 notice only, no license text.
- `/manual-analysis/poems` is client-route-guarded: direct navigation bounces to `/welcome`, but in-app nav works. Login page (`/login`) offers **"Visitor Access (No user and password needed)"** — a guest button, not an account creation flow — which unlocks the full nav (manual/automatic analysis, search engine, comparisons). Confirmed via network-request inspection that clicking Visitor Access makes **zero backend calls** (no `/login`, no `/visitor`, no token exchange) — it's pure client-side UI state. Directly `fetch()`-ing `/api/*` endpoints from a fresh browser context (no visitor click, no cookies) returns full data — **the entire `/api/*` backend is unauthenticated and publicly reachable**, confirmed by hitting `/api/poets`, `/api/searchRetoricalsByPoemsPoets`, `/api/poem/{id}` directly.
- Site architecture: Angular SPA + a REST JSON API at `/api/*`. Key endpoints found: `/api/poets` (1,042 poets — the full catalogue, not just annotated ones), `/api/periods`, `/api/places`, `/api/themas`, `/api/retoricals` (157 rhetorical-element/subtype labels — close to but larger than our project's "53-taxonomy", taxonomy appears to have grown or includes non-poetry entries), `/api/rhymes`, `/api/poemsByPoet?poetIds=<id>[,<id>...]` (full per-poet diwan listing — **includes unanalyzed poems**, not just manually-analyzed ones), `/api/poem/{id}` (bibliographic metadata only: id, poet_id, name, source citation — **no full verse text**), and the actual data endpoint **`/api/searchRetoricalsByPoemsPoets?selectedPeriod=0&selectedPlace=0&selectedPoet=<id(s)>&selectedPoemsPoet=0&selectedRetorical=0&selectedThema=0`** (accepts comma-separated multi-poet IDs; `selectedPoemsPoet=0` returns all analyzed poems for the given poet(s); a poem with zero manual annotations returns `"لا توجد نتائج!"` / an empty `data` array — confirmed empirically, e.g. امرؤ القيس قصيدة 10 has no analysis while قصيدة 8 and 1 do).
- Each annotation record: `{description, key, wordName/word (the exact annotated Arabic span), colomn (comma list of verse-line indices the span touches), poemId, poemName, poetId, poetName, retoricalId, retoricalName (element, e.g. تشبيه/استعارة/كناية/تجريد), subRetoricalName (finer subtype), themaId, themaName (poem topic/theme), retoricalInRowPercent}`. **No verse ID or full verse text field** — only the annotated span text itself and a verse-position index (`colomn`). This is annotation-span data layered onto poems whose full texts live elsewhere (the cited published dīwān editions) — matches how our project's own `data/ground_truth/ali_ana/original/*.xlsx` already works (separate from `archive/Forth_Step/Data/*/poetry.txt` poem texts).
- **Full corpus census** (paginated by 1,042 poet IDs in 11 batches of ≤100, polite ~0 extra delay needed since each batch already took the server 1–26s to answer; total ≈11 GET requests, not thousands): **167 unique manually-analyzed poems across 52 unique poets, 10,430 total rhetorical-annotation records**. Raw annotation JSON for the entire corpus ≈ **5.7 MB** (well under any size concern — no large binary/audio/image assets are part of this data; poem metadata adds a trivial ~50 KB more via 167 `/api/poem/{id}` calls). This 167/52 figure is far larger than the 5 poems (2 poets: امرؤ القيس×2, النابغة الذبياني, جرير, أبو تمّام) our project currently uses — confirms this task's premise that there's a much bigger annotated corpus to recover.
- Confirmed our 5 existing project poems are present and queryable: امرؤ القيس (poet id 58) has poems incl. `قصيدة رقم 8` (poem id 2196, our "Imru2") and `قصيدة رقم 1` (poem id 3205, our "Imru1") both with real annotation data; أبو تمّام is poet id 33.
- **Licensing conclusion for `TOP_5_BLOCKERS.md` item 1**: no robots.txt disallow rules exist (there's no robots.txt at all), and no terms/license page exists anywhere on the site — so nothing *technical* blocks scraping and nothing *textual* on the site states a license either way. This is **not** a resolution of blocker #1 (still needs an explicit answer from Dr. Hussein/the supervisor on what can be shared/republished) — downloading the data does not establish its reuse rights, and the planned `data/ali_poems/README.md` will say so explicitly.

**Proposed Phase B scraper approach** (pending user approval):
- Hit `/api/poets` once, then `/api/searchRetoricalsByPoemsPoets` in batches of ~50–100 comma-joined poet IDs (empirically safe; 100 IDs took up to 26s server-side) — far more polite than one request per poem (which would be 1,000+ probing requests just to find the 167 that have data). Still add a 1–2s delay between batches, retry-with-backoff on failure, and log every request/response.
- Group the flat annotation-record list by `poemId`; for each of the 167 poems, also fetch `/api/poem/{id}` for bibliographic metadata (name, source citation, poet), 1–2s delay between calls, resumable (skip IDs already saved).
- Save **raw, unchanged** JSON: one file per poem under `data/ali_poems/raw/` (annotation records + metadata as returned, no reshaping) — satisfies "raw files unchanged."
- Build `data/ali_poems/manifest.csv` (id, poet, title/name, URL/API endpoint used, file path, sha256, download time; "verse count if parseable" will be the number of distinct `colomn` verse-indices referenced by that poem's annotation records, since full verse text isn't available from this API — noted as a caveat in the README).
- Validate: total poem count == 167 (cross-check against a fresh `/api/poets`+batched-search count at the end of the run, not just the recon count), no empty files, UTF-8/Arabic encoding check, duplicate detection (by poemId), and explicit flagging of the 5 poems already used in `experiments/pilot_3models/config.py` (Imru1=poem 3205/poet 58, Imru2=poem 2196/poet 58, Nabigha=poet 1070, Jarir=poet id TBD at scrape time, Abu_Tammam=poet 33).
- `data/ali_poems/README.md`: source URL, date, and the licensing-status caveat tying back to blocker #1.

---

**2026-10-10T03:00** — New task: build a Tuesday decision document, `docs/phase4/COST_PLAN.md`, for an
example-sensitivity pilot (E1) plus a cost projection for the supervisors' full 10-fold-CV request. No API
calls — planning and arithmetic only, per explicit instruction.
- Read `CLAUDE.md` (already in context), `NEW_SESSION_HANDOFF.md`, `docs/phase4/INFO_REPORT.md` in full,
  and attempted to read `data/ali_poems/manifest.csv`.

**2026-10-10T03:05** — Found: `data/ali_poems/manifest.csv` does not exist (`Glob` on `data/ali_poems/**`
returned no files). Per the session log's own 2026-10-10T02:10–02:45 entries, the Ali-corpus scrape got
only as far as Phase A recon (167 poems / 52 poets found via the public API); Phase B (the actual download
that would have produced `manifest.csv`) was proposed but never approved/run. Grepped `PROJECT_STATE.md`
for any other mention of this corpus — none found, confirming it's new-this-session and the manifest gap is
real, not a stale read. Decision: proceed with the planning document anyway (per Auto Mode bias — this
blocks concrete poem-pool numbers, not the arithmetic/decision-framework itself), flag the gap prominently
in `COST_PLAN.md` §0 and as decision point #1, and base all per-poem cost figures on Phase 1's real
per-poem averages (`INFO_REPORT.md` §4) with the length/pool-size mismatch risk stated explicitly.

**2026-10-10T03:10** — Confirmed pricing basis directly from source: read
`experiments/pilot_3models/config.py:74-81`'s `MODELS` dict (Claude Sonnet 4.6 $3/$15, GPT-5.4-mini
$0.75/$4.50, Gemini 3.5 Flash $1.50/$9.00 per MTok) rather than trusting the already-computed figures in
`INFO_REPORT.md` §4 blindly — matches.

**2026-10-10T03:15** — Worked E1 design (COST_PLAN §1):
- Element recommendation: مجاز (Trope) — 2nd-hardest at element level (~0.293 mean F1, not ceiling like
  Simile, not floor/resistant like Periphrasis), and matches 2 of `INFO_REPORT.md` §1e's 3 subtype-level
  mid-difficulty picks (مجاز عقلي, استعارة فعل are both Trope subtypes).
- Poet recommendation: could not be finalized — the manifest gap (§0) means poet-level poem counts in the
  Ali corpus are unknown, and the recon's aggregate (167 poems / 52 poets ≈ 3.2/poet) makes a single poet
  having 100 annotated poems implausible on average. Wrote this as an explicit open design question with
  two fallback options (relax "one poet" to cross-poet pool, or accept a smaller pool for whichever poet
  turns out largest) rather than guessing a poet name.
- Worked through the paired-comparison metrics list and the bootstrap-CI / run-noise-vs-set-difference
  framing requested, tying the run-noise check back to the already-documented Kenning/Periphrasis 8x→1/2
  incident (CLAUDE.md rule 2) as the concrete failure mode it's meant to catch.
- Answered "2 vs 3 example sets": 2 sets gives one pairwise difference (no way to tell typical variation
  from an outlier pair); 3 sets gives 3 pairwise differences and a crude between-set-vs-within-set variance
  comparison — recommended 3 if budget allows, 2 as an explicitly underpowered fallback.

**2026-10-10T03:25** — Built E1 cost table (COST_PLAN §2):
- Computed per-call cost per model from `INFO_REPORT.md` §4's pooled cross-poem averages (one call = one
  whole poem, one model, one run, all 4 elements, since the system message is frozen/shared across
  elements and there's no validated cheaper Trope-only prompt variant): Anthropic $0.0865/call, OpenAI
  $0.0161/call, Google $0.0402/call (arithmetic: in_tokens/1e6 × price_in + out_tokens/1e6 × price_out).
- Built the 50-vs-100-poem × 1-model-vs-2-models table (10 rows, 2 sets × 2 runs each), spanning
  ≈$3.22 (50 poems, cheapest single model) to ≈$50.68 (100 poems, 2 premium models) — stated the 3rd-set
  marginal-cost multiplier (×1.5) separately rather than a full second table.
- Flagged explicitly that these per-call costs inherit Phase 1's poem-length distribution (23-81 verses,
  mean ≈45), which may not match the real Ali-corpus pool once the manifest exists.

**2026-10-10T03:35** — Built the full-CV projection (COST_PLAN §3):
- Read the supervisors' request literally first (a 30×30 per-poet-prompt × per-eval-poet cross grid before
  any CV multiplication), established that 10-fold CV's inference cost is `n_poems × n_runs` once (each
  poem sits in exactly one held-out fold — CV doesn't multiply the per-poem cost by 10) and that the
  expensive part is the cross-poet grid, not the CV mechanism itself.
- Built Low/Mid/High scenarios on explicit poems/poet assumptions (3/5/8, capped at the corpus total of
  167 across 52 poets, flagged as placeholders pending the manifest), arriving at ≈$22 (Low) / ≈$84 (Mid) /
  ≈$1,140 (High = literal full grid) — the ~13-50x jump from Mid to High is driven almost entirely by
  switching from a shared cross-poet benchmark set to a full O(n²) grid, not by the CV or pool-size
  assumptions, which is the point of the "cheaper alternative" ask.
- Wrote the cheaper-alternative design (single shared 20-30-poem cross-poet benchmark reused across all 30
  prompts instead of a full grid) and noted it also makes the 30 prompts' cross-poet scores directly
  comparable to each other (same eval set) — a side benefit beyond cost.

**2026-10-10T03:45** — Wrote the one-page Tuesday recommendation (COST_PLAN §4) as an ordered list of 5
decision points (manifest gap → poet choice → 2-vs-3 sets → model scope → full-grid-vs-alternative), each
tied back to the section that costs it, and flagged that the full-CV decision should wait on E1's result
since a null example-sensitivity finding would undercut the per-poet-prompt premise.

**2026-10-10T03:50** — Wrote `docs/phase4/COST_PLAN.md` in full (sections 0-4). No API calls at any point
in this task. Committing and pushing next; final chat output will be the options table only, per
instruction.

**2026-10-10T03:55** — Committed `98c5384` (`docs/phase4/{COST_PLAN.md,SESSION_LOG.md}`). `git push origin
main` rejected again by the same pre-existing GitHub pre-receive hook (3 oversized CSVs baked into history
at commit `3d91e28`, up to 186.92MB — first hit 2026-10-10T00:45, unrelated to this task). Did not attempt
a history rewrite/force-push. `98c5384` exists locally on `main`, stacked on the already-unpushed commits
from earlier this session, still waiting on the user's decision (LFS-migrate / strip from history / stay
local for now).
