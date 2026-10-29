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

---

**2026-10-10T04:00** — New task: resume the Ali-corpus download, now fully scoped. Goal: for every one
of the 167 manually-analyzed poems, capture full verse text (verse by verse), all annotations + analysis
text, poet name, period, place, poem name, theme, rhetorical element — using the site's own filter schema
(الفترة, المكان, الشاعر, القصيدة, الثيمة, العنصر البلاغي). No LLM API calls. Re-read `CLAUDE.md` and this
log's Phase A entries (2026-10-10T02:10–02:45) before starting, per instruction.

**2026-10-10T04:05–04:35** — Step 1 (find the best full-text source), via built-in browser + direct
`fetch()` calls (visitor-access session, same unauthenticated `/api/*` backend as Phase A):
- 1a: Grepped `main.5f9e9721169cb1ba.js` (2.98MB) for `/api/...` literals and for route-name string
  constants (`Line|Lines|Poem|Verse|Bayt`) — found `getWordsPoem` as a new, previously-unseen route name
  not surfaced by Phase A's literal-path grep (Angular assembles `environment.apiUrl + 'routeName'`, so
  literal `/api/foo` greps miss routes built this way — this is why 1a also required driving the UI and
  watching live network traffic, not just a static grep).
- 1b: Drove the manual-analysis UI (`/manual-analysis/poems`, poet امرؤ القيس) — confirmed it only ever
  renders the same annotation-span table the API already gives (span text + بيت index + explanation), no
  full verse text anywhere in that view. Drove `/rhetorical-analysis/poems` (automatic-analysis-run list)
  — same: per-poet poem list with تم التحليل yes/no, no full text. Drove `/automatic-analysis/poems` for
  امرؤ القيس — no automatic analysis exists for this poet (empty result), same annotation-record shape as
  manual when populated, still no full verse text. Drove `/search-engine/poems`, searched the word
  "الديار" — this view DOES show full verse text, split into صدر/عجز hemistichs, with poem/poet/period/
  place/source/verse-number columns, via `/api/getLineWordsBySearchWord` — but it's a word-match search
  across the whole corpus, not a per-poem "give me every verse" call.
  Breakthrough: called `/api/getWordsPoem?poetid=<id>&poemid=<id>` directly (found via the route-name grep
  above) — returns the ENTIRE poem word-by-word: `{id, name, colomn (verse index, same numbering as the
  annotation records' colomn field), fl (0=صدر/1=عجز), poem_id, poet_id}`. Reconstructing by grouping on
  colomn+fl and joining `name` tokens in array order gives the full poem text, verse by verse, hemistich by
  hemistich. Confirmed no `poetid`/`poemid` pair returns a gap (no missing colomn values) for the one poem
  tested so far.
- 1c: Consistency check against the project's own frozen ground truth, all 5 poems:
  - **Full text**: reconstructed قصيدة رقم 8 (poem_id 2196, poet_id 58 / امرؤ القيس) from `getWordsPoem` —
    23 verses, byte-for-byte identical (including diacritics) to
    `archive/Forth_Step/Data/Imru2/poetry.txt` for every verse spot-checked (1–12, 21–23; full 23/23
    reconstructed with zero missing colomn values).
  - **Annotation counts**: fetched `/api/searchRetoricalsByPoemsPoets` per poet and compared per-poem
    record counts against `data/ground_truth/ali_ana/original/*.xlsx` row counts (read via `openpyxl`,
    local, read-only) — **exact match on all 5**: Imru1 (poem 3205, poet 58) 305=305, Imru2 (poem 2196,
    poet 58) 44=44, Jarir (poem 10539, poet 1385 "جرير بن عطيّة") 166=166, Nabigha (poem 3218, poet 1070)
    167=167, Abu_Tammam (poem 2127, poet 33) 94=94. (Poet 1385 also has poem 10662 with 93 unrelated
    records — a different Jarir poem not used in this project, correctly excluded.)
  - Conclusion: `getWordsPoem` + `searchRetoricalsByPoemsPoets` + `poem/{id}` + `poets`/`periods`/`places`/
    `themas`/`retoricals` lookups together are sufficient and verified-accurate for the full goal. No need
    to fall back to page-scraping (1b/1c already ruled that out as strictly worse than the API) or to stop
    and ask for an external export — proceeding straight to Step 2.
- Schema note: period (الفترة) and place (المكان) are **poet-level** attributes in this database (`/api/
  poets` gives each poet a single `period` id and a `places` array), not per-poem fields — confirmed via
  `/api/periods` (16 rows) and `/api/places` (56 rows, each with `name`+`subPlace`) lookup tables. Theme
  (الثيمة) and rhetorical element (العنصر البلاغي) are per-annotation-record fields (`themaName`,
  `retoricalName`/`subRetoricalName`), already confirmed in Phase A.

**2026-10-10T04:40** — Writing `scripts/download_ali_poems.py` next (Step 2): batched
`searchRetoricalsByPoemsPoets` sweep to enumerate the 167 poems (reusing Phase A's batching approach), then
per-poem `poem/{id}` + `getWordsPoem` + grouped annotations, 1-2s delay, retry-with-backoff, full logging,
resumable, raw responses saved unchanged plus normalized per-poem JSON + manifest.csv. No API-cost
implications (this is a plain HTTP scrape of a public, unauthenticated site, not an LLM call) so no cost
confirmation gate applies here, consistent with how Phase A was already run under this same understanding.

**2026-10-10T04:45** — Wrote `scripts/download_ali_poems.py` in full (lookups, batched annotation
enumeration, per-poem `poem/{id}` + `getWordsPoem` fetch + reconstruction, raw+normalized output,
manifest, resumability via on-disk raw-file caching, retry-with-backoff, logging to both stdout and
`data/ali_poems/download.log`). Ran it in the background (`python scripts/download_ali_poems.py`).

**2026-10-10T05:19–05:31** — Download run completed: 14 annotation batches (1,042 poet ids ÷ 80/batch),
then 167/167 poems processed with **0 errors**. Total elapsed ≈12 minutes (dominated by the 1.5s
per-poem-pair delay × ~340 API calls). `data/ali_poems/` is 20MB on disk (lookups + 14 annotation
batches + 167×2 raw poem responses + 167 normalized JSON + manifest.csv + download.log) — well under the
50MB ask-first threshold, so proceeding to commit without asking per the standing instruction.

**2026-10-10T05:32–05:45** — Step 3 validation, via a local read-only Python script over `manifest.csv`
and the raw files (no network calls):
- **Counts**: 167 unique `poem_id`s, 52 unique poet names — matches Phase A's census exactly.
- **No duplicates** (`poem_id` set has no repeats), **no empty/missing files** (every `file_path` in the
  manifest exists and is >50 bytes).
- **Totals**: 3,470 reconstructed verses, 10,430 annotation records — matches Phase A's corpus-wide
  annotation count (10,430) exactly.
- **Arabic encoding**: spot-checked `poems/2196_امرؤ_القيس_العصر_الجاهلي.json` directly — diacritics and
  RTL text intact, `verses[0]` and `annotations[0]` both render correctly, themes/elements lists correct
  (6 themes, 9 distinct elements, matching the 44-row manual-analysis table seen live in Step 1c).
- **Missing fields**: 6 poems total, all traced to genuine gaps in the *source site's own data*, not
  scraper bugs — 4 poems (poet id 1400, الحمدوي) have a `period` id (27) absent from the site's own
  `/api/periods` lookup (max valid id there is 26); 1 poem (poem_id 7408, poet id 1263) has no `period`
  set on the site at all; 1 poem (poem_id 28601, poet id 1676) has 29 manual annotations but
  `/api/getWordsPoem` returns `{"success":true,"data":[]}` for it — no word-level text was ever entered
  for this poem on the site, so its full verse text is genuinely unobtainable from this source (its
  annotation span text is still captured).
- **5-poem consistency re-check** (already done in Step 1c, re-confirmed against the downloaded files):
  Imru1 305/305, Imru2 44/44 (+ verse-by-verse identical text, 23/23 verses), Jarir 166/166, Nabigha
  167/167, Abu_Tammam 94/94 — all exact matches, `already_used_in_project` manifest column correctly
  flags all 5.

**2026-10-10T05:50** — Wrote `data/ali_poems/README.md`: source URL, download date (2026-10-10), method
(lookup tables → batched annotation enumeration → per-poem `poem/{id}` + `getWordsPoem` fetch), why
`getWordsPoem` was chosen over page-scraping (summarized from Step 1), the full schema (manifest columns
+ per-poem JSON shape with a real example), the 5-poem consistency table, the validation results above,
and an explicit, prominent licensing-unconfirmed caveat tying back to `TOP_5_BLOCKERS.md` item 1 — states
plainly that downloading this data does not resolve that blocker and it must be cleared with the
supervisor/Dr. Hussein before any redistribution.

**2026-10-10T05:55** — Committed `1e7b233` (`scripts/download_ali_poems.py` + `data/ali_poems/` [525
files, 20MB, under the 50MB ask-first threshold] + this log). Per this task's explicit instruction, did
**not** attempt `git push` (it would fail on the same pre-existing large-file-in-history issue from commit
`3d91e28`, unrelated to this task, already hit three times earlier this session) — no retry, no history
rewrite. `main` is now 18 commits ahead of `origin/main`, all local-only pending the user's earlier-flagged
decision (LFS-migrate / strip-from-history / stay-local).

---

## Task: resolve the large-file push blocker (history rewrite), no API calls

**2026-10-10T16:40–17:05** — Steps 1–2 (backup + diagnose) were run and logged in full in this file, then
**lost**: the entries were written with `Edit` but never `git commit`-ed, and Step 4's `git filter-repo`
run (below) does a fresh internal clone + checkout, which silently discarded that uncommitted edit along
with it. Summarizing what was established in that lost pass, since it still holds and isn't being
re-verified from scratch:
- Full pre-rewrite backup taken **outside the repo**: `../metaphorical_backup_2026-10-10.bundle` (295.7 MB,
  `git bundle verify` confirmed "complete history", all 5 refs incl. `pre-phase4-snapshot`), plus the 3
  known large CSVs copied to `../csv_backup/<element>_<variant>_embeddings_out/dataset_with_embeddings.csv`.
  Pre-rewrite `HEAD` = `ae3b1fa2ec85ab3d66f5c0ca37e36d3560f9e809`, `HEAD^{tree}` = `15857a77e5d85a330d4693490e5834e6fd66110d`.
- Diagnosis found exactly 3 blobs >50MB reachable from any ref, all introduced in `3d91e28`, all still
  present on disk (187MB, 112MB, 74MB), all regenerable via each classifier's sibling `embeddings.py`
  (reads a small labeled CSV, calls OpenAI `text-embedding-3-large`, writes `embeddings_out/dataset_with_embeddings.{csv,parquet}`
  — regeneration would be a paid API call, out of scope here, not performed).
  `origin/main` (`1633cf5`) confirmed to not contain `3d91e28` or anything after (`git merge-base
  --is-ancestor` exit 1) — consistent with the original rejected push. `git filter-repo` was not installed;
  `pip`/`python` were available to install it.
- Corrected one detail in the task's framing: `main` was **19** commits ahead of `origin/main` at the time,
  not 18 (two more had landed in the Ali-poems-corpus task since that count was written).
- User gave explicit OK to proceed with the proposed `git filter-repo --path <3 files> --invert-paths` plan
  in a separate chat turn (not re-transcribed here since the turn boundary, not this log, is the record of
  that approval) before Step 4 below started.

**2026-10-10T17:10** — Step 4a: `pip install git-filter-repo` → `git-filter-repo-2.47.0` installed
successfully (pure-Python, no other dependency). Pre-rewrite snapshot taken for later comparison: `git
ls-files -s | grep -v dataset_with_embeddings.csv | sort` (2,345 lines) saved to a scratch file; noted
`main` had 36 total commits, `pre-phase4-snapshot` tag → `8949746` ("fix: strip Arabic guillemets..."),
remote `origin` → `https://github.com/faisalomari/Metaphorical_Analysis.git`.

**2026-10-10T17:11** — Step 4b: ran `git filter-repo --path <3 known CSVs> --invert-paths --force`.
Completed in ~41s, removed `origin` remote (filter-repo's documented default behavior — "assumes a fresh
start"), rewrote `HEAD` to a new hash (same final commit message, as expected since all 36 commits are
after `3d91e28`... actually only commits from `3d91e28` onward are rewritten, but since `3d91e28` is early
in history every descendant commit's hash changes). Working tree afterward: `git status` clean, 36 commits
still in `git log`, `pre-phase4-snapshot` tag still present.

**2026-10-10T17:12** — **Found a problem the plan hadn't anticipated**: a full history rescan
(`git rev-list --objects --all | git cat-file --batch-check ... | awk '$3>50000000'`) still showed **3
blobs >50MB** — same content hashes as the 3 just-stripped files, but at *different, older paths*:
`experiments/classifiers/trope/embeddings_out/...`, `previous_steps/poems/Kenayh/PartlyEmbedding/embeddings_out/...`,
`previous_steps/poems/Majaz/FullEmbedding/embeddings_out/...`. These are duplicate-content copies of the
same 3 CSVs that existed under pre-reorg (`previous_steps/`) or pre-rename paths earlier in history, which
the original `--path` list (built from the *current* working-tree paths only) didn't cover. `git
filter-repo --path` matches by path, not by blob hash, so stripping 3 current paths left identical content
reachable via old paths.
- Fixed by iterating: re-ran `git filter-repo --path <path> --invert-paths --force` for each newly-found
  path, then rescanned for >50MB blobs again, repeating until the rescan came back empty. Took 4 rounds
  total (the first follow-up round surfaced one further hidden duplicate,
  `previous_steps/poems/Majaz/PartlyEmbedding/embeddings_out/...`, and then one more,
  `previous_steps/poems/Majaz/embeddings_out/...`, each only found once the previous one was stripped —
  `git rev-list --objects --all | grep <filename>` was used each round to confirm no path remained for
  any of the 3 original hashes before moving on).
- Final rescan: `awk '$3>50000000'` over all history objects — **empty**. A secondary `awk '$3>10000000'`
  sweep for completeness surfaced only files the user had already explicitly approved committing earlier
  in the session (2 PDFs, 1 xlsx, 1 csv, all <25MB, see the 2026-10-10T00:10 entry above) — nothing new to
  strip. `.git` shrank from (not measured before) to 144MB after this pass.
- Each `filter-repo` re-run also re-did a fresh checkout of `HEAD`, which **deleted the 3 large CSVs from
  the working tree** each time (filter-repo doesn't just rewrite history, it repopulates the working copy
  from the new HEAD tree, and files excluded from every commit via `--invert-paths` are consequently absent
  from that tree). Restored all 3 from `../csv_backup/` after every round, confirmed byte-identical via
  `diff -q` against the backup copies each time. The task's own "working tree is unchanged" verification
  step is what caught this — a non-stripped-file diff alone would have missed it.

**2026-10-10T17:20** — Added a gitignore rule, `**/embeddings_out/*.csv`, to `.gitignore` (previously only
`*.joblib`/`*.parquet` were excluded) so these regenerable caches can live on disk without being re-added by
a future `git add -A`. Confirmed via `git status --short` that the 3 restored CSVs no longer show as
untracked (ignored, as intended) and only `.gitignore` itself shows modified. Committed as `fbb73c2`
("chore: ignore embeddings_out CSV caches after history rewrite").

**2026-10-10T17:25** — Re-added `origin` remote, `git fetch origin` (confirmed `origin/main` still at
stale `1633cf5`, matching pre-task state — no one else pushed in the meantime), full pre-push sanity
rescan (0 blobs >50MB), then `git push origin main --force-with-lease`.

**2026-10-10T17:26** — **Push rejected by GitHub secret scanning / push protection** (`GH013`), not the
original large-file issue: a real, live-looking Hugging Face user access token (`hf_...`, verified present
but not printed in full to this log or chat — only a masked prefix was ever surfaced) hardcoded in the
*pre-reorg* commit (the rewritten-hash version of the original `3d91e28`/14a021f reorg commit) across 5
files: `previous_steps/poems/{Majaz,Tashbeeh,Tebaq}/{Partly,Full}Embedding/LR.py` (4 files, same line
pattern: `os.environ["HF_TOKEN"] = "hf_..."`) and `previous_steps/poems/Majaz/PartlyEmbedding/main.ipynb`
(1 file). The *current* working-tree copies of these same `LR.py` files already have this scrubbed to a
placeholder (`"REPLACE_WITH_YOUR_OWN_KEY"`) per the original `3d91e28` commit's own stated intent ("hardens
secret handling... scrubs plaintext API keys/tokens to placeholders") — but the real value survived in the
older, pre-scrub commit in history, which none of the CSV-stripping passes above touched (different
problem: a tracked secret, not an oversized blob).
- Checked `git merge-base --is-ancestor <that commit> origin/main`: exit 1 (not an ancestor) — confirmed
  this secret-containing commit was **never actually pushed to GitHub**, so push protection caught it
  before any public exposure. Still sitting in the local bundle backup and local history, though.
- This was new scope the user hadn't pre-approved (the original OK covered the 3 CSVs only), so **stopped
  and asked** via `AskUserQuestion` rather than working around GitHub's block. Options offered: strip the
  secret from history now (git filter-repo --replace-text), pause for the user to rotate the token first,
  or use GitHub's "allow this secret" bypass link. **User chose: strip it from history now.**

**2026-10-10T17:30** — Redacted the secret from all history. Rather than hardcoding the literal token value
into a filter-repo replace-text expression (would have required printing/handling the raw secret more than
necessary — and a direct `cat`/`grep`-and-print of the full value across all 5 locations was in fact
blocked by the session's own credential-materialization safeguard when attempted), used a **regex pattern**
instead: `regex:hf_[A-Za-z0-9]{20,}==>REDACTED_HF_TOKEN` in a scratch expressions file, passed to
`git filter-repo --replace-text <file> --force`. This matches the token shape wherever it appears without
needing to view or special-case each of the 5 locations individually.
- Verified via `git log --all -p | grep -c "hf_[A-Za-z0-9]\{20,\}"` → **0** matches anywhere in rewritten
  history. Restored the 3 large CSVs from `../csv_backup/` again (same fresh-checkout side effect as
  before), confirmed byte-identical. Re-ran the full verification suite: `git status` clean, 37 commits
  (36 + the `fbb73c2` gitignore commit from the prior step, correctly preserved), `pre-phase4-snapshot` tag
  still resolves to a commit with the same message as before (hash changed, as expected — filter-repo
  rewrites tags pointing into rewritten history automatically), 0 blobs >50MB, and a full
  `git ls-files -s` diff against the very first pre-rewrite snapshot showed **no differences except
  `.gitignore` itself** (the one intentional change) — every other tracked file's path+blob hash is
  identical to before any of this session's rewrites.
- Deleted the scratch files that had briefly held secret-adjacent content (`/tmp/secret_line.txt`, the
  `--replace-text` expressions file) immediately after use.

**2026-10-10T17:35** — Re-added `origin`, `git fetch origin` (picked up `origin/main` at the stale
`1633cf5` — unchanged), `git push origin main --force-with-lease` → **succeeded**
(`1633cf5..1172141  main -> main`, no secret-scanning rejection this time). `git push origin
pre-phase4-snapshot --force` → succeeded (tag moved, as expected). Final confirmation: `git status` →
clean; `git log origin/main -n 3` → `1172141` (chore: gitignore), `bdc97d2` (docs: Ali-poems outcome),
`b688804` (data: Ali-poems download) — matches local `main` exactly. New `HEAD` = `1172141189f8b099a5066d0d650e7bff25598186`.

**Outstanding item for the user, outside this task's original scope**: the Hugging Face token found above
was never actually exposed on GitHub (confirmed not an ancestor of the old `origin/main`) and is now
redacted from all local history that was just pushed — but it still exists in the `../csv_backup/`-adjacent
full bundle backup (`../metaphorical_backup_2026-10-10.bundle`, taken *before* the redaction) and in
whatever shell/editor history may have touched it previously. Recommend rotating/revoking that Hugging Face
token regardless, since "never pushed to GitHub" isn't the same guarantee as "never exposed anywhere."

---

## Task: replace `COST_PLAN.md` with a real, decision-ready version (manifest now exists), no API calls

**2026-10-10T18:00** — New task: now that `data/ali_poems/manifest.csv` exists (167 poems, 52 poets,
downloaded earlier this session), redo the Phase 4 cost plan with real pool numbers instead of the
placeholder version's Phase-1-extrapolated guesses. Re-read `CLAUDE.md`, `NEW_SESSION_HANDOFF.md`,
`docs/phase4/INFO_REPORT.md`, the old `docs/phase4/COST_PLAN.md`, `data/ali_poems/README.md`, and
`data/ali_poems/manifest.csv` (169-line file, read via `Read` offset for the tail half) before starting.
No LLM API calls anywhere in this task — local-file analysis and arithmetic only, per explicit instruction.

**2026-10-10T18:05** — Parsed `manifest.csv` with Python's `csv` module (167 data rows, clean parse — the
file's semicolon-separated sub-fields and Arabic commas avoid any quoting ambiguity with the comma
delimiter). Applied the two exclusions required by the task: poem 28601 (no verse text, confirmed via its
own `README.md`-documented gap) and the 5 `already_used_in_project`-flagged poems (Abu_Tammam=2127,
Imru2=2196, Imru1=3205, Nabigha=3218, Jarir=10539). Resulting candidate pool:
**161 poems, 50 distinct poets**.

**2026-10-10T18:10** — Per-poet pool analysis (COST_PLAN §1): wrote a local script
(scratchpad `pool_analysis.py`) that loads every pool poem's full JSON (`poems/*.json`), maps each
annotation's `element`/`subtype` field to this project's own Trope/Simile/Kenning/Antonymy categories using
the same substring logic as `ground_truth.py:SUBSTRING_MAP` (مجاز/استعارة→Trope, تشبيه→Simile, كناية→Kenning,
طباق→Antonymy — reused for consistency, not reimplemented differently), and tallies per-poet poem count,
verse count, annotation count, and counts for the 3 `INFO_REPORT.md` §1e mid-difficulty subtypes (مجاز
عقلي, كناية عن صفة, استعارة فعل) directly from each poem's own `annotations[].subtype` field (finer-grained
than the manifest CSV's own `annotation_counts_per_element` column, which only has top-level categories).
- Found: **أبو نواس (Abu Nuwas) has 30 poems** pool-wide — more than double the next-largest poet
  (النابغة الذبياني, 13) — and is a poet never used anywhere in the project before. 12 poets total have
  ≥3 poems; the other 38 have only 1–2.
- Confirmed the literal "50–100 eval poems from the same poet" target is infeasible for every poet
  (corpus-wide average 3.2 poems/poet; even Abu Nuwas tops out at 30) — this was already flagged as a risk
  in the placeholder plan before the manifest existed; now confirmed as fact. Resolved by relaxing to a
  cross-poet eval pool (examples from one poet, eval across the whole remaining corpus).

**2026-10-10T18:20** — Poet/element recommendation: **أبو نواس + مجاز (Trope), subtype استعارة فعل** —
largest poem count, zero prior use in the project, largest single-poet instance count for the top
mid-difficulty subtype (222 استعارة فعل instances, ~13% of the entire corpus's pool-wide supply of 1,646).
Considered and rejected أبو تمّام (more raw volume but already has 1 frozen-TEST poem — a clean, unused
poet avoids the interpretive wrinkle) and النابغة الذبياني (same DEV-poem caveat, smaller margin) as the
primary pick; recorded both as alternatives in the doc.

**2026-10-10T18:25** — E1 example-set selection (COST_PLAN §2.1): picked 3 of Abu Nuwas's shortest poems
(6 verses each: 16251, 17234, 21337), each independently rich in استعارة فعل annotations (5 instances
each), as the 3 disjoint example-source poems for sets A/B/C. For each poem, listed the distinct verse
numbers carrying an استعارة فعل annotation and drew 2 via `random.sample(verses, 2)` under a single
`random.seed(42)` (sets drawn in order A→B→C) — fully reproducible, logged verse-by-verse with full Arabic
text (read directly from each poem's `verses` array) in the doc.

**2026-10-10T18:30** — Eval pool computation (COST_PLAN §2.2): eval pool = 161-poem candidate pool minus
the 3 example-source poems = **158 poems, 3,228 verses** (mean 20.4 verses/poem, computed by loading
`verse_count` from every pool poem's JSON). Drew a 50-poem subsample via a separate `random.seed(43)` (kept
distinct from the example-selection seed so the two randomizations can't interact) — **50 poems, 885
verses actual** (not a hypothetical average; this exact sample is what gets costed). Also tallied the 27
Abu-Nuwas-authored poems remaining in the eval pool (439 verses) as a same-poet-vs-other-poet secondary
split, rather than excluding the whole poet from eval.

**2026-10-10T18:35** — Cost model correction (COST_PLAN §3.1): the placeholder plan's flat per-call
average cost ($0.0865/$0.0161/$0.0402 for Anthropic/OpenAI/Google) implicitly assumes Phase 1's longer
poems (mean ≈45 verses); the real Ali-corpus eval pool averages only 20.4 verses/poem, so a flat average
would overstate cost for this corpus (the fixed system-prompt-overhead portion of each call matters more
for short poems). Fit a linear model (`cost = a + b×n_verses`) via `numpy.polyfit` over Phase 1's 5 real
(verses, cost) data points per model (from `INFO_REPORT.md` §4's `run_manifest.json`-derived table) —
predicts the known 5 points within ~3–15%, used to cost the real pool sizes from §2.2 and §4.2 rather than
a flat average.

**2026-10-10T18:40** — Built the real E1 cost table (COST_PLAN §3.2): 50-poem subsample (885 real verses)
vs. full 158-poem pool (3,228 verses) × 2 vs. 3 sets × 1 vs. 2 models × 2 runs. Headline recommended cell
(3 sets, GPT+Gemini, 2 runs): $7.36 for the 50-poem pilot, $26.03 for the full pool — both substantially
cheaper than the placeholder plan's equivalent rows (~$17–51), because the real corpus's shorter poems cut
cost rather than raise it (the opposite of the direction the placeholder had flagged as a risk).

**2026-10-10T18:45** — Full-CV projection, now against real poet counts (COST_PLAN §4): grepped the actual
per-poet poem/verse distribution computed in the §1 script and found only **6 poets have ≥10 poems**
(أبو نواس, النابغة الذبياني, بشار بن برد, أبو تمّام, ابن الرومي, ديك الجن — 86 poems/1,609 verses total)
and only **12 have ≥3** (109 poems/1,940 verses) — the placeholder plan's "~30 poets" assumption does not
hold against the real corpus; a literal 30-poet 10-fold-CV design would need ≥18 poets with only 1–2 poems
each, for which 10-fold CV isn't a meaningful operation. Computed same-poet (holdout) cost, the
shared-cross-poet-benchmark alternative, and the **literal full grid** exactly from real per-poet poem/
verse counts for both the 6-poet and 12-poet tiers (debugged one Arabic-string-literal mismatch that had
under-counted 2 poets' poems on a first pass — fixed by reading poet names directly from the computed
dict rather than retyping them, verified against the dict's own keys before reusing).
- Finding: because the real poet tiers are small (6–12, not 30), the full grid is now **affordable**
  (≈$26–64 for 6–12 poets, GPT+Gemini, 2 runs) — much closer to the shared-benchmark alternative's cost
  than the placeholder's hypothetical 30×30 grid (which projected a 13–50× gap). Recommendation changed
  accordingly: run the literal full grid on the 6-poet (true-10-fold-eligible) tier (≈$26.43) rather than
  defaulting to a shared-benchmark shortcut that was only necessary under the old, incorrect 30-poet
  assumption.

**2026-10-10T18:50** — Wrote the full replacement `docs/phase4/COST_PLAN.md` (sections 0–5: exclusions,
pool analysis + poet/element table and recommendation, E1 design with concrete example verses and eval
pool, real cost tables, real full-CV projection, one-page Tuesday recommendation with an options table).
No API calls at any point in this task. Committing and pushing next.

---

## Task: build + dry-run E1 (example-sensitivity pilot), STOP before any real API call

**2026-10-10T19:00** — New task: build the full E1 harness per the design already agreed in
`COST_PLAN.md`/`INFO_REPORT.md` (poet=Abu Nuwas, element=مجاز, subtype focus=استعارة فعل, 3 example sets
A/B/C seed=42, 50-poem eval pool seed=43, 1 run/set/model + an off-by-default set-A repeat flag), dry-run
the exact cost, then STOP for explicit go-ahead. No API calls anywhere in this task. Re-read `CLAUDE.md`,
`NEW_SESSION_HANDOFF.md`, `docs/phase4/COST_PLAN.md`, `docs/phase4/INFO_REPORT.md`,
`data/ali_poems/manifest.csv` before starting.

**2026-10-10T19:05** — Model confirmation gate (per the task's explicit "wait for my confirmation of the
models" instruction): presented the two-best-model pick with evidence via `AskUserQuestion` — Gemini 3.5
Flash (مجاز/Trope F1 0.386, استعارة فعل strict recall 0.264, cost/call $0.0402) + GPT-5.4-mini (Trope F1
0.251, استعارة فعل strict recall 0.155, cheapest at $0.0161/call) vs. Claude Sonnet 4.6 (Trope F1 0.242 —
actually the *worst* of the 3 — and most expensive at $0.0865/call). **User confirmed Gemini + GPT-5.4-mini**
or either instructed change). Mid-task the user separately asked to also cost Claude Sonnet 4.6 in the
dry-run table (not to add it to the actual confirmed run) — `dryrun.py` reports all 3 models' cost; the
actual `runner.py` default stays Gemini+GPT per the confirmed pair.

**2026-10-10T19:10** — Read `experiments/pilot_3models/{config,prompts,providers,span_matching,
span_scoring,run_pilot,ground_truth,parsing,analyze}.py` directly (not just INFO_REPORT's summary) to
confirm exact function signatures/return shapes before reusing them from a new module
(`experiments/phase4_e1/`), per the task's explicit "do not change prompts.py logic; add a new module"
instruction — nothing in `experiments/pilot_3models/` was edited.

**2026-10-10T19:15** — Inspected 3 Abu Nuwas poem JSONs (16251, 17234, 21337) directly
(`data/ali_poems/poems/*.json`) to find the real annotation schema (`span_text`, `verse_index`
comma-list-per-word, `element`, `subtype`, `analysis` — not the `wordName`/`colomn` field names
`COST_PLAN.md` assumed from the scrape-recon phase; the actual normalized-JSON field names differ from the
raw-API field names documented in `data/ali_poems/README.md`). Confirmed exact-subtype-match (`subtype ==
"استعارة فعل"`, not substring) against the 3 poems reproduces `COST_PLAN.md §2.1`'s per-poem candidate-verse
lists exactly (16251: {1,2,3,5}; 17234: {3,4}; 21337: {1,2,4,6}).

**2026-10-10T19:20** — Built `experiments/phase4_e1/`:
- `e1_config.py` — all frozen constants (poet, element, subtype, both seeds, exclusion id sets, set names,
  N_RUNS=1, REPEAT_SET_A=False default, RUN_MODELS=[google,openai], ALL_MODELS=[anthropic,openai,google]).
- `ali_poems_io.py` — loads a poem JSON + manifest; `build_poem_text()` reconstructs the same
  verse-numbered plain-text shape `pilot_3models` already expects (`sadr<spaces>ajuz` per line, ordered by
  `verse_index`); `load_ali_gt_spans()` re-maps each poem's own `annotations` list to the 4 pilot elements
  using `pilot_3models.ground_truth.SUBSTRING_MAP` directly (imported, not reimplemented) so the mapping
  stays identical to every frozen Phase 1-3 number. Verse-of-record for an annotation = first entry of its
  comma-separated `verse_index` (matches the convention the scraper's own validation pass already used to
  exactly reconcile annotation counts against the frozen xlsx sheets, `SESSION_LOG.md` 2026-10-10T04:35).
- `fewshot_examples.py` — `build_example_sets()` reproduces the 3 sets' verse draws from source data with
  `random.seed(42)` (not transcribed from `COST_PLAN.md` by hand — independently re-derived and verified to
  match it exactly, see below); `build_fewshot_block()`/`build_system_message_e1()` append a new few-shot
  section (verse + span + Dr. Hussein's own `analysis` note) after `pilot_3models.prompts.build_system_message()`'s
  existing, unmodified output — same bare-numbered-example convention as `data/elements/*.txt`, extended
  with the annotation per the task's "show verse text and annotation" instruction.
- `build_pool.py` — builds the candidate pool (167 manifest poems minus poem 28601, the 5
  already-used-in-project poems, and the 3 example-source poems) tagged `abu_nuwas`/`other`, draws the
  50-poem eval subsample with `random.seed(43)`, writes `config/eval_pool.json` + `config/example_sets.json`.
- `runner.py` — resumable: skips any `(set, poem_id, provider, run_index)` cell already in
  `run_manifest.json` with no error (full re-run only via `--force`); refuses to call any provider at all
  unless invoked with `--confirm` (defaults to a dry listing of the planned calls, same gate as
  `dryrun.py` but for the actual spend path); `--repeat-set-a` adds the optional 2nd run for set A only.
- `scoring.py` — span-level strict + token-overlap scoring (`pilot_3models.span_matching.best_match`,
  reused), raw TP/FP/FN per poem, pooled per-set overall/`abu_nuwas`/`other`, and a bootstrap CI (2,000
  resamples over poems, seeded) for each pairwise (F1_set_i − F1_set_j) — the exact check the CLAUDE.md
  rule 2 Kenning/Periphrasis 8×→1/2 incident calls for.
- `dryrun.py` — the cost gate itself (below).

**2026-10-10T19:30** — Verification run (no API calls, local only):
- `python fewshot_examples.py` reproduced `COST_PLAN.md §2.1`'s exact 6 verses/spans independently from
  source JSON + `random.seed(42)` — confirms the cost-plan's hand-written table wasn't a transcription
  error.
- `python build_pool.py` reproduced `COST_PLAN.md §2.2`'s exact pool sizes independently: candidate pool
  158 poems/3,228 verses (27 Abu Nuwas/131 other), eval subsample 50 poems/885 verses (5 abu_nuwas-tagged/
  45 other-tagged) under `random.seed(43)`.
- `python runner.py` (no `--confirm`) printed the planned-call count only: 300 calls (3 sets × 50 poems ×
  2 models × 1 run), 0 already done — confirmed no network call is attempted without `--confirm`.
- `python -m py_compile` on every new module — all compile clean.

**2026-10-10T19:35** — Dry-run cost (`dryrun.py`), no API calls: installed `tiktoken` (local pip package,
not a network/LLM call) and used its `cl100k_base` encoding as the closest available **local** token
estimate for all 3 providers — explicitly noted in the script's own docstring/output that no offline
tokenizer exists for `claude-sonnet-4-6` or `gemini-3.5-flash` in this environment, and that counting via
their real APIs would itself be a network call this task must not make. Computed the REAL input-token count
for all 150 distinct (set × poem) prompts this design would actually send (not an average), then estimated
output tokens via each provider's own historical output/input ratio from Phase 1's pooled
`run_manifest.json` data (`INFO_REPORT.md §4`: anthropic ×0.7255, openai ×0.6653, google ×0.9011) applied to
that call's real input count.
- **Confirmed pair (Gemini + GPT-5.4-mini), 1 run, no repeat: 300 calls, $7.75.**
- All 3 models individually (150 calls each, 1 run): GPT-5.4-mini $2.17, Gemini 3.5 Flash $5.57, **Claude
  Sonnet 4.6 $8.05** (costed per the user's mid-task ask, not part of the confirmed run).
- With the optional set-A repeat: confirmed pair 400 calls/$10.31; Claude alone 200 calls/$10.72.
- Compared to `COST_PLAN.md`'s prior $7.36 estimate (50 poems, 3 sets, GPT+Gemini, **2** runs): this design
  spends $7.75 at **1** run — more per-run than the placeholder predicted, because the real few-shot-extended
  prompt is larger than the flat historical per-poem average the placeholder used; flagged explicitly in
  the script's own output rather than silently matching the old number.

**2026-10-10T19:40** — STOP per task instruction: no API call made anywhere in this task. Awaiting the
user's explicit go-ahead before running `runner.py --confirm`. Appending this entry, then committing and
pushing `experiments/phase4_e1/` + this log.

**2026-10-10T20:00** — Committed (`c0f08e2`) and pushed. User confirmed the model pick (Gemini + GPT), and
separately flagged a real bug after reviewing the output: the eval pool spec was "10 Abu Nuwas poems + 40
poems from other poets," but `build_pool.py` had drawn all 50 with a single `random.sample(candidate_pool,
50)` call over the combined 158-poem pool — that reproduces the candidate pool's own ~27:131 poet ratio by
chance (came out 5 abu_nuwas/45 other) instead of the requested fixed 10:40 split. A 5-poem same-poet
subsample is too small to read a same-poet-vs-other-poet signal off of, which is exactly the secondary
question this pool's poet tagging exists to support.
- Fix: `e1_config.py` now has explicit `EVAL_POOL_ABU_NUWAS_N=10`/`EVAL_POOL_OTHER_N=40` constants;
  `build_pool.py`'s `build_eval_subsample()` splits the candidate pool into abu_nuwas/other subsets first,
  then draws `random.sample(abu_nuwas_subset, 10) + random.sample(other_subset, 40)` under one
  `random.seed(43)` call (abu_nuwas drawn first, for reproducibility) — stratified, not pooled, sampling.
- Re-ran `build_pool.py`: eval pool now **50 poems, 1,010 verses, exactly 10 abu_nuwas / 40 other** (up
  from the buggy 885 verses/5:45 split — more verses because Abu Nuwas's poems in this pool average longer
  than the cross-poet average, pulling the total up when forced to 10 rather than 5).
- Regenerated the 3 prompt previews and re-ran `dryrun.py` on the corrected pool: confirmed pair (Gemini +
  GPT-5.4-mini), 1 run, no repeat: **300 calls, $7.95** (was $7.75 on the buggy pool); with the optional
  set-A repeat: 400 calls/$10.58. All 3 models individually: GPT-5.4-mini $2.23, Gemini 3.5 Flash $5.72,
  Claude Sonnet 4.6 $8.26 (comparison only, not part of the confirmed run).
- No API calls made in this fix. Still STOPPED, awaiting go-ahead before `runner.py --confirm`.

---

## Task: run E1 (Gemini + GPT-5.4-mini only, sets A/B/C, 1 run each), then analysis + write-up

User re-confirmed the frozen design in a new instruction: eval pool fixed at 10 abu_nuwas + 40 other
(50 poems, 1,010 verses, seed=43, commit `7906d02`), models Gemini 3.5 Flash + GPT-5.4-mini only (no
Claude), sets A/B/C one run each, no set-A repeat. Hard cap $9, confirmed up to $9; stop and ask if the
dry-run total exceeds $9.

**2026-10-10 (this task, Step 1)** — Re-verified pool composition via a local read-only script over
`experiments/phase4_e1/config/eval_pool.json`: 50 poems, 50 unique poem_ids, exactly 10 tagged
`abu_nuwas` / 40 tagged `other`; zero overlap between the eval-pool poem_ids and the 3 example-source
poem_ids (16251/17234/21337), the 5 already-used Phase-1 poem_ids (2127/2196/3205/3218/10539), and the
no-text poem (28601). Checked `.env` for `OPENAI_API_KEY`/`GEMINI_API_KEY`/`ANTHROPIC_API_KEY` presence
(presence only, values never printed) — all 3 present. Re-ran `dryrun.py`: **300 calls, $7.95** for the
confirmed pair (Gemini 3.5 Flash + GPT-5.4-mini), 1 run/set/model, no repeat — matches the prior run
exactly (pool/config unchanged since). $7.95 is under the user's $9 hard cap — proceeding to Step 2
(`runner.py --confirm`) without stopping to ask, per the task's own stated threshold.

**Step 2, attempt 1 — all 300 calls failed, $0 spent.** First `runner.py --confirm` run produced 300/300
manifest records all with `error = "KeyError: '<PROVIDER>_API_KEY'"` — the error fires inside
`providers.py` reading `os.environ[...]` *before* any network call is made, so no request ever reached
Gemini or OpenAI and no spend occurred. Root cause: unlike `pilot_3models/run_pilot.py` (which calls
`load_dotenv(ROOT / ".env")` at import time), `experiments/phase4_e1/runner.py` never loaded the `.env`
file — `os.environ` was empty for the keys in that process even though `.env` itself has all 3 keys
(verified present in Step 1). Fix: added the same `from dotenv import load_dotenv; load_dotenv(ROOT /
".env")` call to `runner.py`, verified standalone that it populates all 3 keys. Deleted the all-error
manifest (`results/phase4_e1/run_manifest.json`) before retrying, since `runner.py`'s own resume logic
already treats any record with a non-null `error` as not-done and would retry it anyway — removing it
first just keeps the manifest clean of a dead false-start batch.

**Step 2, attempt 2 — ran, STOPPED on repeated Gemini API errors.** Re-ran `runner.py --confirm` (300
calls: 150 OpenAI + 150 Google). Result: all 150 GPT-5.4-mini calls succeeded, 0 errors. Google:
142/150 failed, overwhelmingly (128/142) `ClientError 429 RESOURCE_EXHAUSTED` with the error body stating
`generativelanguage.googleapis.com/generate_content_free_tier_requests ... quotaValue: '20'` for model
`gemini-3.6-flash` (the account's Gemini key is on the free tier, 20 requests/day, not a paid tier able
to absorb 150 calls in one run); the other 14/142 are `ServerError 503 UNAVAILABLE` (transient overload,
unrelated to quota), all in set A early in the run before the quota wall hit. Only 8 Google calls
succeeded (all set A, poems 3261/3265/3754/3755/4554/5660/10662/11835) before the daily quota was
exhausted.
- Actual spend so far (computed from each successful record's real `usage` tokens x `config.py` pricing,
  not the dry-run estimate): $1.46 total -- $1.28 OpenAI (150/150 calls) + $0.18 Google (8/150 calls).
  Well under the $9 cap; no retry attempted past the quota wall.
- Per this task's own "stop immediately on repeated API errors and report spend so far" instruction,
  stopping here rather than retrying into the same quota wall or waiting out the ~6h12m `retryDelay` the
  API reports. Flagging for the user: Google's 20-req/day free-tier cap makes finishing the remaining 142
  Google calls in one sitting infeasible without either (a) upgrading/enabling billing on the Gemini API
  key so it leaves the free tier, or (b) spreading the remaining calls across several days at 20/day, or
  (c) proceeding with OpenAI-only results for now and backfilling Google later. Not deciding this
  unilaterally -- asking the user next.
- **User decision (AskUserQuestion): "Analyze OpenAI-only for now, backfill Gemini later."** Proceeding
  to Step 3 analysis on the complete GPT-5.4-mini data (150/150 cells, all 3 sets x 50 poems) only.
  `E1_RESULTS.md` will state plainly that Gemini 3.5 Flash is incomplete (8/150 cells, free-tier quota
  wall) and excluded from the comparative analysis pending a backfill once the quota/billing issue is
  resolved -- not reported as a result, not silently dropped.

**Step 3 (analysis), GPT-5.4-mini only.** Wrote a scratch driver (not committed to the repo; calls
`experiments/phase4_e1/scoring.py`'s `score_set`/`bootstrap_ci_pairwise`/`poem_f1` directly, restricted to
`provider="openai"` -- did not edit `scoring.py` itself, which still hardcodes `["google","openai"]` for
whenever Gemini is backfilled). Computed strict + token-overlap span-level TP/FP/FN/P/R/F1 for sets A/B/C,
overall and split abu_nuwas(n=10)/other(n=40); pairwise bootstrap 95% CI (2,000 resamples over poems) for
A-B/A-C/B-C on both criteria; per-poem paired-difference sign counts.
- Finding: **B > A > C** on both criteria (strict F1 0.209/0.154/0.139; token F1 0.234/0.170/0.153). B is
  significantly better than C on both criteria (bootstrap CI excludes 0: strict [0.023,0.124], token
  [0.030,0.138]). A vs B is borderline -- significant under token overlap ([-0.121,-0.006]) but the CI
  just touches 0 under strict ([-0.108,0.001]). A vs C is not distinguishable (CI spans 0 both criteria).
- Confirmed via `config/example_sets.json` that Set C's two examples are the user's flagged
  "both about التعقيل" case -- both built on the same root ع-ق-ل (عقل/عقّل), applied to different objects
  but with no other pattern represented; Set C is also the worst performer, consistent with (not proof
  of) example homogeneity hurting generalization.
- Abu Nuwas (n=10) vs other (n=40) split computed and reported but marked indicative-only per n size, as
  instructed.
- No run-noise baseline exists (1 run/cell, per the frozen design) -- stated plainly per instruction that
  all set-to-set differences are indicative only, with the bootstrap CI as the sole uncertainty measure
  (does not substitute for a second run; CLAUDE.md rule 2's Kenning/Periphrasis 8x-to-1/2 precedent cited
  as the concrete risk this caveat exists for).
- No model comparison performed or reported (Gemini incomplete).

**Step 4** — wrote `docs/phase4/E1_RESULTS.md` (design recap, actual cost table, key TP/FP/FN/P/R/F1
tables both criteria, bootstrap CI table, per-poem diff table, abu_nuwas/other split, the Set-C-homogeneity
note, caveats, bottom line). Committing and pushing next.

---

## Task: write `docs/phase4/PROMPT_ANATOMY.md` — show exactly what is sent to the API, no API calls

**2026-10-11** — New task: document the E1 prompt/call mechanics (system message, cross-set diff, user
message template, output format + malformed-output handling, per-model call settings, one real response
vs ground truth, whether non-target elements are mentioned). Read-only / no code changes, no API calls.
Re-read `CLAUDE.md` first per instruction.

- Read `experiments/phase4_e1/fewshot_examples.py`, `config/prompt_preview_{A,B,C}.txt`,
  `experiments/pilot_3models/providers.py`, `prompts.py`, `parsing.py`, `config.py` directly (source only,
  no re-derivation) for §1/§2/§4/§5.
- `diff`'d all 3 `prompt_preview_*.txt` files pairwise: identical through line 69, differ only in the 2
  few-shot example lines (70-76) -- confirms the pilot's manipulation is isolated exactly to the 2
  examples, nothing else.
- Built the real user-message template (`ANALYSIS_INSTRUCTIONS` + `build_poem_text()`) for eval poem
  17373 (أبو نواس, 6 verses, abu_nuwas-tagged) via a local read-only script, truncated to its first 4
  verses for §3's illustration (noted explicitly that the real runner sends the full poem, not a
  truncation).
- For §6, used poem 17373's real raw response `results/phase4_e1/raw/B_17373_openai_run1.txt` (GPT-5.4-mini,
  Set B) against its ground truth, mapped via `pilot_3models.ground_truth.SUBSTRING_MAP` (ran
  `ali_poems_io.load_ali_gt_spans` directly, no reimplementation) -- verse-by-verse comparison found 2
  strict TPs (v4 Trope + Antonymy, both exact span matches), 1 token-only TP (v5, model's "مُرّنت" is a
  true substring of the longer GT span), several FNs (v2 Kenning, v3 Trope, v4 Kenning x3, v6 Trope x2),
  0 FPs, and noted the SUBSTRING_MAP quirk where one GT span ("استعارة مبنية على الكناية" subtype) maps to
  both Trope and Kenning since its subtype label contains both substrings.
- For §5, confirmed from `providers.py` source: temperature 0.0 identical across all 3 providers; no
  JSON/structured-output mode anywhere; no retry logic in `runner.py` (single attempt, exception caught
  and recorded, no auto-retry); the one real difference is `max_tokens` -- Anthropic gets an explicit
  16000 cap, OpenAI and Google get no explicit cap (provider default) -- and no reasoning/thinking params
  are set for any provider despite gpt-5.4-mini/gemini-3.5-flash being reasoning-capable families.
- For §7, confirmed the system message's ELEMENTS_BLOCK (frozen, Phase-1) defines and asks about all 4
  elements every verse; E1's own few-shot addition covers only استعارة فعل, explicitly scoped by its own
  header text -- so the model is told about all 4 elements, and the output schema still asks for all 4,
  but E1's extra emphasis is subtype-scoped.
- Wrote `docs/phase4/PROMPT_ANATOMY.md` (7 sections as specified). No API calls, no code changes anywhere
  in this task. Committing and pushing next.

---

**2026-10-11 — New task: full prompt-inventory audit, read-only.** Task: the user noticed E1 reused
`pilot_3models.prompts.build_system_message()` (old terminology, TEST-leaking examples) and expected the
newest Phase 2/3 prompt design instead. Output: `docs/phase4/PROMPT_INVENTORY.md`. No API calls, no code
changes anywhere in this task.

- Read `CLAUDE.md`, `GLOSSARY.md`, `NEW_SESSION_HANDOFF.md`, and `PROJECT_STATE.md` in full (both pages,
  offset 0-311 and 312-465) for standing rules and current project state.
- Noticed immediately: `PROJECT_STATE.md`'s last entry is "Phase 2 §7, 2026-07-26" — it never mentions
  Phase 3 (`phase3_subelements`, `phase3_crossmodel`) or Phase 4 (`phase4_e1`) anywhere. Confirmed via
  `git log --oneline --all` that Phase 3's commit (`9a9365f`) and every Phase 4 commit are dated
  2026-10-10 — three months after `PROJECT_STATE.md`'s own stated last-update date. This is a real
  docs-vs-code staleness gap, not a misreading.
- Listed every file under `experiments/{pilot_3models,phase2_chatlike,phase3_subelements,
  phase3_crossmodel,phase4_e1}/` (`ls`) and pulled `git log -1 --format="%ai %h %s"` for each candidate
  prompt-building file to get exact last-commit dates.
- Read, in full, the actual prompt-building code: `pilot_3models/prompts.py`, `prompt_variants.py`,
  `phase2_chatlike/prompt_config_b.py`, `prompt_config_c.py`, `phase3_subelements/subtype_prompts.py`,
  `fewshot_prompts.py`, `subtype_defs.py` (all 25 subtype entries), `phase3_crossmodel/
  crossmodel_config.py`, `phase4_e1/e1_config.py`, `fewshot_examples.py`, `runner.py`, and
  `docs/phase4/PROMPT_ANATOMY.md` (already-verified verbatim E1 system message from the earlier task in
  this session) — confirmed byte-for-byte that `fewshot_examples.build_system_message_e1()` calls
  `pilot_3models.prompts.build_system_message()` unmodified, i.e. E1 ships with "Kenning"/"Antonymy" and
  the TEST-poem-leaking element-file examples exactly as PROMPT_ANATOMY.md already showed.
- Grepped `phase3_subelements/run_subtype_check.py`, `run_fewshot_check.py`, and `phase3_config.py` to
  confirm model routing (Gemini 3.5 Flash only for Phase 3's own subtype run, via `providers_fixed.
  call_google_fixed`; Phase 3's crossmodel step adds Claude Sonnet 4.6 + GPT-5.4-mini re-scoring the same
  prompt, not a new prompt).
- Ran a targeted grep on `docs/phase4/E1_RESULTS.md` for the actual cost figure (confirmed: GPT-5.4-mini
  150/150 calls, $1.28, 0 errors; Gemini partial) and read the first part of this session log to confirm
  the append format used so far.
- Wrote `docs/phase4/PROMPT_INVENTORY.md`: §1 all 7 prompt-building code paths (file, function, commit
  date, models, terminology, element-definition source/leakage, 23-subtype-taxonomy use, output format,
  scope); §2 newest-by-commit-date vs. what the docs call canonical, and why they disagree (the three
  docs never name Phase 3's subtype prompt, which is the best "newest canonical" candidate, because
  `PROJECT_STATE.md` itself predates Phase 3/4 by three months); §3 the newest prompt's full verbatim
  system+user message (Phase 3's single-subtype template, filled with a placeholder poem) with its
  output schema; §4 concrete recommendation for injecting E1's existing A/B/C few-shot example sets into
  Phase 3's subtype-level prompt instead of Phase 1's whole-poem prompt, and the specific changes needed
  in `e1_config.py`/`fewshot_examples.py`/`runner.py`/`scoring.py` (none applied — read-only task); §5
  explicit answer that the existing $1.28 GPT E1 result is usable only if labeled as run on Phase 1's old
  prompt, not as evidence about the corrected-prompt design.
- No code changes, no files touched besides this log and `PROMPT_INVENTORY.md`. Committing and pushing
  next.

---

## Task: `docs/phase4/FULL_COST_MODEL.md` — decision-ready full cost model, no API calls

**2026-10-11** — New task: a comprehensive, decision-ready cost model covering (1) current, verified
provider pricing, (2) real token-usage facts from this project's own logs, (3) cost per call/poem/design
over the full eligible-poem pool, and (4) the one-shot/few-shot/current/full-taxonomy design comparison
(D1-D4). Explicit instruction: **no LLM API calls** — local files, arithmetic, and public pricing pages
only. Re-read `CLAUDE.md` first per instruction.

**Step 1 — reading.** Read `docs/phase4/{COST_PLAN.md,INFO_REPORT.md,E1_RESULTS.md,SESSION_LOG.md}` in
full (SESSION_LOG required two `Read` calls, 703 lines total), `PROJECT_STATE.md` in full (two calls, 465
lines), `data/ali_poems/manifest.csv` (167 rows), `results/phase3_crossmodel/summary.md` (the 25-subtype
taxonomy table), and `experiments/phase4_e1/e1_config.py`.

**Step 2 — pool arithmetic (local, `csv` module).** Computed exact poem/verse counts for every exclusion
combination from `manifest.csv` directly (not transcribed from `COST_PLAN.md`): 167 total scraped poems
(3,470 verses) -> 166 after dropping poem 28601 (no verse text; verse_count for that poem is already 0, so
the verse total doesn't change) -> 161 after also dropping the 5 already-used Phase 1 poems (3,246 verses)
-> 158 after also dropping the 3 E1 example-source poems (3,228 verses). Adopted **161 poems / 3,246
verses** as the default "eligible pool" for designs that don't need few-shot examples (D3, D4a, D4b) and
**158 poems / 3,228 verses** for designs that do (D1, D2) — stated as an explicit, overridable assumption
in the doc rather than silently picking one.

**Step 3 — pricing verification (web, public pages only, no API calls).** `WebSearch` + `WebFetch` against
each provider's own pricing/model pages:
- OpenAI (`developers.openai.com/api/docs/models/gpt-5.4-mini` via WebSearch synthesis; direct WebFetch of
  `openai.com/api/pricing/` returned **HTTP 403**, so the model-page route was used instead): $0.75/$4.50
  per MTok confirmed, matches this project's own `config.py`. Tier 1 rate limits (500 RPM / 500,000 TPM /
  5,000,000-token batch queue) came back from the same official model-page route — treated as
  **verified**. Cached-input ($0.075/MTok) and Batch (~50% off) figures came only from third-party
  aggregators, not a fetched OpenAI page in this session — marked **unverified/estimate**.
- Google (`WebFetch` on `ai.google.dev/gemini-api/docs/pricing` and `.../docs/models`): **real, reportable
  finding — `gemini-3.5-flash` is not listed on either current official page.** The current Flash lineup
  is 3.5 Flash-Lite, 3.6 Flash (stable), 3.8 Flash (stable, newest), 3-flash-preview, and 2.5-flash
  (legacy/grandfathered). `gemini-3.5-flash`'s $1.50/$9.00 pricing (this project's `config.py` value,
  repeated by every third-party aggregator found) **could not be confirmed against a live official page
  this session** — flagged prominently rather than guessed forward. Confirmed from the pricing page: Batch
  = 50% off standard rates (official, general paid-tier feature); the free-tier 20-requests/day cap this
  project's own E1 run actually hit (`E1_RESULTS.md`) is the strongest-possible verification of that one
  number, since it's from the project's own failed API responses, not a page.
- Anthropic (`WebFetch` on `anthropic.com/pricing` -> 301 redirect -> `claude.com/pricing`, followed):
  Claude Sonnet 4.6 confirmed **$3/$15 per MTok**, listed under "Legacy models" (i.e. still priced and
  billable, not removed). Prompt caching (5-min TTL): read $0.30/MTok, write $3.75/MTok — confirmed on the
  same page. 1-hour cache tier: not listed on this page, not confirmed. Batch: "save 50%" confirmed on the
  same page.
- Reasoning/thinking-token billing: grepped the whole repo for `reasoning_tokens`/`thinking_tokens`-shaped
  fields — found in exactly 2 files (`phase3_subelements/providers_fixed.py`, `run_subtype_check.py`), and
  neither actually logs a numeric reasoning-token count anywhere in this project's stored manifests/JSON
  (confirmed by a second grep over `results/**/*.json` — zero hits). This project has **never actually
  billed or measured a reasoning/thinking-token line item for any of the 3 models** — stated explicitly in
  the doc rather than assumed. Billing convention (reasoning tokens counted as ordinary output tokens) is
  each provider's own well-documented general practice, not something re-verified against a live page this
  session for these 3 specific model IDs — marked accordingly.
- Rate-limit search for Gemini's paid tier (tier 1 RPM/RPD) came back inconclusive (conflicting forum
  posts, no authoritative number retrieved) — stated as "not retrieved, check AI Studio console" rather
  than guessed.

**Step 4 — real token facts from local logs/code (no network, no API calls).**
- Pulled `INFO_REPORT.md`'s already-computed 5-poem-per-provider (verses, in_tokens, out_tokens) table and
  fit `tokens = a + b*n_verses` (NumPy `polyfit`, not the dollar-denominated fit `COST_PLAN.md` used) for
  all 3 providers, separately for input and output — this isolates the frozen whole-poem design's **fixed
  per-call token overhead** (4 element definitions + 19 baked-in examples + instructions) from its
  **per-verse marginal token cost**, directly from real logged usage.
- Computed real averages from `results/phase4_e1/run_manifest.json` over all error-free records: GPT-5.4-mini
  (150/150 succeeded) avg 2,772 in / 1,438 out per call; Gemini (only 8/150 succeeded, free-tier wall) avg
  2,886 in / 1,978 out — both on E1's actual pool (avg 20.2 verses/poem), both include the base 4-element
  system message **plus** the 2-example few-shot addition.
- Measured exact token sizes of real prompt components with `tiktoken`'s `cl100k_base` encoding (the only
  local-tokenizer option available — explicitly not a true tokenizer for any of the 3 real models, flagged
  as an approximation in the doc, same caveat `experiments/phase4_e1/dryrun.py` already logged for this
  exact limitation): `pilot_3models.prompts.build_system_message()` output = 2,226 tokens (4 elements + 19
  examples); `fewshot_examples.build_fewshot_block()` for sets A/B/C = 283/358/291 tokens (avg 311); 
  `phase3_subelements.subtype_prompts.SYSTEM_TEMPLATE` filled per subtype, averaged over all 25 entries in
  `SUBTYPE_DEFS` = 313 tokens (227-428 range), of which 126 tokens is the shared scaffold (measured with an
  empty definition) and therefore ~187 tokens is the average per-subtype definition content alone;
  `ANALYSIS_INSTRUCTIONS` boilerplate = 245 tokens; Phase 3's real logged average output per
  (subtype,verse) decision (`summary_openai.json`: 121,119 output tokens / 1,140 calls) = **106.2
  tokens/decision**, GPT-5.4-mini only, includes the required 1-3-sentence Arabic reasoning field.
- For the D4 reasoning-token mid-scenario: confirmed via grep that no Phase 2/3/4 manifest anywhere has a
  literal `reasoning_tokens` field, but Phase 2 Config C's real logged `stage1_output_tokens` IS a
  real measured cost of one full free-form Arabic reasoning pass per verse (Fable 5, no schema
  constraint) — averaged `(39306+38030)/2/23 verses` = **1,681 tokens/verse**, used as the mid-scenario
  anchor per the task's explicit instruction to base it on Config C's logs.
- Noted the taxonomy-size discrepancy rather than silently resolving it: the task's instruction says "23
  subtypes"; this project's own code has 25 entries in `subtype_defs.SUBTYPE_DEFS` and 28 files under
  `data/ground_truth/by_subtype/` (23 "tested" + ~5 thin/extra, per `INFO_REPORT.md`'s own framing). Used
  **23** throughout per the explicit task instruction, flagged this discrepancy in the doc itself.

**Step 5 — built the 5 design cost models (D1/D2/D3/D4a/D4b)** from the measured component sizes above (a
local Python script, not hand arithmetic) — full method, every fixed assumption (per-poem granularity for
D1/D2 rather than per-verse; D3 reinterpreted as "the current, actually-run whole-poem/all-4-elements
design" rather than literally decomposed to one element, flagged explicitly as a reinterpretation of the
task's D3 wording; D4b's 23-subtype split across the 4 element families as an approximate 8/6/5/4
apportionment) stated in the doc itself, not just here. **Single biggest finding**: D4's literal
all-23-subtypes x all-verses output token volume (106.2 tokens/decision x 23 subtypes x ~20 verses/poem
=~49,000 output tokens per poem, before any reasoning-token addition) dominates every other cost term in
the entire model by roughly 1-2 orders of magnitude — this is the "single biggest cost driver" the task's
final output asks for.

**Step 6 — wrote `docs/phase4/FULL_COST_MODEL.md`** (Tables 1-4 + full assumption/estimate-vs-verified
labeling throughout, per the task's explicit "mark every number" instruction). No API calls anywhere in
this task. Committing and pushing next.

---

## Task: rebuild E1 as E1 v2 on the Phase 3 subtype-level prompt, build + dry-run only, STOP before any API call

**2026-10-11** — New task: `docs/phase4/PROMPT_INVENTORY.md` established that E1 v1
(`experiments/phase4_e1/`) reused `pilot_3models.prompts.build_system_message()` unmodified — old
terminology ("Kenning"/"Antonymy"), TEST-poem-leaking element examples. Rebuild it as a new,
separate design (E1 v2) on top of Phase 3's subtype-level prompt instead. Explicit instructions: v1's
files/results stay untouched (its $1.28 GPT result is labeled "run on old Phase 1 prompt", not
reinterpreted); do not edit `phase3_subelements/` or `pilot_3models/` — only import from them; new code
goes under `experiments/phase4_e1_v2/` and `results/phase4_e1_v2/`; **no real API calls anywhere in this
task** — build, unit-check, dry-run cost, then STOP at the cost gate. Re-read `CLAUDE.md`, `GLOSSARY.md`,
`docs/phase4/{PROMPT_INVENTORY,E1_RESULTS,FULL_COST_MODEL}.md`, and all of `experiments/phase4_e1/` +
the 6 named `phase3_subelements/` files in full before writing anything (all already read earlier in
this session, re-confirmed here).

**Design decisions made/confirmed before coding** (per the task's own agreed design, not improvised):
- Subtype: استعارة فعل (parent مجاز/Trope) — same subtype E1 v1 already focused on, continuity with the
  existing example sets.
- Base prompt: `phase3_subelements.subtype_prompts.SYSTEM_TEMPLATE` + `ANALYSIS_INSTRUCTIONS`, schema
  `{exists, appearance, reasoning}`, **one call per verse-unit** (a single verse — the same per-verse
  granularity `phase4_e1/scoring.py`'s own `majority_exists_and_appearance` already keys on, not a
  multi-verse annotation span) — a real shape change from v1's one-call-per-whole-poem design, confirmed
  explicitly in `runner.py`'s own docstring rather than silently kept the same.
- Example sets A/B/C: reuse the SAME 3 sets from `experiments/phase4_e1/config/example_sets.json`
  (2 examples each, seed=42) unchanged — not redrawn — injected as "Example 2"/"Example 3" slots in
  `fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT`'s exact shape, Example 1 = the original `subtype_defs`
  definition example (same for all of A/B/C/Z). An example verse carrying >1 annotation span (e.g. set
  B's verse 4 has 3) is joined into one note per slot (`prompt_builder._format_example_verse`) since the
  fewshot template has exactly one note slot per example verse — a necessary adaptation, not a silent
  drop of data.
- New set Z: Phase 3's *original* 1-example prompt (`SYSTEM_TEMPLATE`, no fewshot block at all) — the
  zero-extra-examples baseline the task asked for, to see whether the fewshot examples help at all versus
  not having them.
- Eval pool: reuse `experiments/phase4_e1/config/eval_pool.json` unchanged (50 poems = 10 abu_nuwas + 40
  other, seed=43, already excludes the 3 example-source poems, the 5 frozen Phase 1 poems, and the
  no-text poem 28601).
- Ground truth: exact match on `poem_json["annotations"][i]["subtype"] == "استعارة فعل"`, verse-level
  (`gt_v2.gt_spans_for_subtype`), scored both span-strict and token-overlap on `appearance`
  (`pilot_3models.span_matching.best_match`, reused unchanged) — precision AND recall AND F1 are all
  well-defined here (unlike `phase3_subelements/score_subtypes.py`'s recall-only design, since every row
  fed there was already a known GT-positive; this pilot asks about every verse, GT-positive or not).
- Models: Gemini + GPT-5.4-mini (same confirmed pair as v1); Claude Sonnet 4.6 costed in the dry-run only,
  not run. 1 run per set per model (no second run, same frozen-design limitation v1 had, flagged the same
  way).

**Step 1 — built the modules** (`experiments/phase4_e1_v2/`, nothing in `phase3_subelements/` or
`pilot_3models/` touched):
- `e1v2_config.py` — frozen constants + `build_cheap_variant_pool()` (the 25-poem cheaper-variant sampler,
  5 abu_nuwas + 20 other, seed=43, drawn fresh from the same 158-poem candidate pool v1's `build_pool.py`
  already builds — imported via `phase4_e1.build_pool.build_candidate_pool`, not reimplemented).
- `gt_v2.py` — verse-level ground truth for exactly one subtype, reusing `phase4_e1.ali_poems_io.
  load_poem_json` unchanged.
- `prompt_builder.py` — `build_system_message(set_name)` for Z/A/B/C (Z = `subtype_prompts.SYSTEM_TEMPLATE`
  filled with the subtype's own definition; A/B/C = `fewshot_prompts.SYSTEM_TEMPLATE_FEWSHOT` with Example
  2/3 drawn from v1's `example_sets.json`); `build_user_message(verse_text)` = `subtype_prompts.
  ANALYSIS_INSTRUCTIONS.format(verse=...)`, identical across all 4 sets.
- `parsing_v2.py` — parses the new single-JSON-object-per-call schema (`{"exists","appearance",
  "reasoning"}`), distinct from `pilot_3models.parsing.parse_response`'s 9-key-JSONL schema (that parser
  does not apply to v2's call shape at all).
- `scoring_v2.py` — span-level strict + token-overlap scoring (raw TP/FP/FN, `pilot_3models.analyze.prf1`
  + `span_matching.best_match`, both reused unchanged), pooled overall/abu_nuwas/other, bootstrap 95% CI
  over poems (2,000 resamples) for every pairwise `(F1_set_i - F1_set_j)` across Z/A/B/C (6 pairs, not
  just A/B/C's 3), and per-poem paired-difference sign counts — same CLAUDE.md-rule-2 noise check v1's
  scoring.py already did, extended to the 4th set.
- `runner.py` — resumable (skip any `(set, poem_id, verse_no, provider)` cell already manifest-recorded
  with no error, `--force` to redo), `--pool {full,cheap}` to pick the 50- or 25-poem design, refuses any
  API call without `--confirm` (dry listing only otherwise), `load_dotenv(ROOT / ".env")` at import time
  (v1's own dotenv bug, already fixed there, replicated correctly here from the start rather than
  reintroducing it), stops immediately (no retry loop) on a 429/quota-shaped error message or 5
  consecutive errors of any kind, per the explicit task instruction.
- `dryrun_v2.py` — the cost gate itself (below).

**Step 2 — unit checks, NO API calls** (`unit_checks.py` + `prompt_builder.py`'s own `__main__`):
- Rendered the full system message for all 4 sets and diffed A vs B and A vs C — confirmed the only
  difference between A/B/C is the 2 example-verse lines (Example 2/3), everything else byte-identical;
  printed in this log's companion chat output.
- Verified **0 overlap** between the 50-poem eval pool and the 3 example-source poems (16251/17234/21337).
- Verified GT parsing reproduces the exact per-poem استعارة فعل verse sets already confirmed independently
  in this session's 2026-10-10T19:15 entry (16251: {1,2,3,5}; 17234: {3,4}; 21337: {1,2,4,6}) — matches
  exactly. Also confirmed all 50 eval-pool poems' GT parses cleanly with no size mismatch (422 total
  استعارة فعل GT instances across the pool).
- Ran the scorer on 3 fake verse-unit responses (a true hit matching the real GT span at poem 16251 verse
  1, a true-but-wrong-span miss, and an exists=false) against `span_matching.best_match` directly —
  confirmed TP/FP/FN logic resolves correctly without any `run_manifest.json` or API call.
- `python -m py_compile` on every new module — all compile clean.

**Step 3 — DRY RUN cost (`dryrun_v2.py`), no API calls**:
- Real input-token count (tiktoken `cl100k_base`, flagged as an approximation, same caveat v1's
  `dryrun.py` already used) for every real (set, poem, verse) prompt — 1,010 verse-units x 4 sets = 4,040
  distinct prompts over the unchanged 50-poem pool.
- **Gemini model-id finding** (the task's explicit question): `pilot_3models.config.MODELS["google"]
  ["model_id"]` = `"gemini-3.5-flash"` — and `providers.py`/`providers_fixed.py` both call exactly that
  string, no divergence in the code. But E1 v1's real 429 quota-error body (`E1_RESULTS.md`, this log's
  own 2026-10-10 Step-2 entry) reported the quota wall under `generativelanguage.googleapis.com/
  generate_content_free_tier_requests ... for model gemini-3.6-flash` — Google's backend served/billed
  the request under the **3.6-flash** identity, not 3.5-flash's, even though the code asked for
  "gemini-3.5-flash" by name (consistent with `FULL_COST_MODEL.md` §0.1's independent finding that
  `gemini-3.5-flash` doesn't exist on Google's current official pricing/models pages at all — "3.5-flash"
  has become an alias Google resolves to 3.6-flash server-side). **Answer: the code requests
  gemini-3.5-flash; the model actually served and billed is gemini-3.6-flash; gemini-3.6-flash's pricing
  applies, not the legacy 3.5-flash estimate this project's `config.py` has used throughout.**
  A `WebSearch` this session for gemini-3.6-flash's current rate found genuinely conflicting cached
  copies of Google's own pricing page: $0.75/$3.75 per MTok (intro pricing through 2026-12-31, several
  independent sources) vs. $1.50/$7.50 (one cached copy + one aggregator) — reported both as
  ESTIMATE_LOW/ESTIMATE_HIGH in the dry-run output rather than picking one, alongside `config.py`'s
  existing $1.50/$9.00 legacy figure for continuity with every prior Phase 4 cost doc.
- **Calls**: 1,010 verse-units x 4 sets x 2 models = **8,080 calls** (50-poem pool); 327 verse-units x 4 x
  2 = **2,616 calls** (25-poem cheaper variant, 5 abu_nuwas + 20 other, seed=43, drawn fresh from the same
  158-poem candidate pool).
- **Cost, 50-poem pool** (confirmed pair, 1 run each): GPT-5.4-mini $4.30; Gemini $3.98-$8.61 depending on
  which of the 3 pricing scenarios above is real; **confirmed-pair total $8.29-$12.91** — both the
  low-Gemini-estimate total ($8.29) and the legacy-config-rate total ($12.91) bracket the user's
  previously-stated $9 hard cap from v1's run, flagged explicitly rather than picked silently. Claude
  Sonnet 4.6 costed only: $15.93.
- **Cost, 25-poem cheaper variant**: GPT-5.4-mini $1.40; Gemini $1.29-$2.79; confirmed-pair total
  $2.69-$4.19; Claude (costed only) $5.17.
- Compared against `docs/phase4/FULL_COST_MODEL.md`'s D4a/D4b (23-subtype, all-verse-taxonomy, full-poem
  calls): D4a priced ALL 23 subtypes at ~49,000 output tokens/poem ($36.38 GPT-5.4-mini, 161 poems); this
  design prices ONE subtype at Phase 3's real 106.2-token/decision output size, per-verse — not directly
  comparable to D4a (different scope and granularity), stated explicitly in the script's own output
  rather than implying a false apples-to-apples comparison.

**STOP** — no API call made anywhere in this task. Awaiting the user's explicit go-ahead before running
`runner.py --confirm`. Appending this entry, then committing and pushing `experiments/phase4_e1_v2/` +
this log (v1's files and results in `experiments/phase4_e1/` and `results/phase4_e1/` left untouched;
`phase3_subelements/` and `pilot_3models/` left untouched).

---

## Task: E1 v2 — 25-poem variant, THREE models (GPT-5.4-mini, Gemini, Claude Sonnet 4.6), sets Z/A/B/C, 1 run each, no repeat

**2026-10-11** — New task, 4 steps, explicit no-API-call gate at the end of each of steps 1-2, exactly one
tiny bounded-cost API call permitted in step 3 (5-token Gemini prompt, cost < $0.001, to verify the Gemini
key's tier and the real served model id), then STOP for the user's explicit "go" before `runner.py
--confirm`. Re-read `CLAUDE.md`, this log (both pages), and every file in `experiments/phase4_e1_v2/` (all
9 files: `e1v2_config.py`, `runner.py`, `dryrun_v2.py`, `prompt_builder.py`, `gt_v2.py`, `parsing_v2.py`,
`scoring_v2.py`, `unit_checks.py`, `config/prompt_preview_{A,B,C,Z}.txt`) before starting, per instruction.

**Step 1 (no API calls).**
- Confirmed the requested "25-poem variant (5 abu_nuwas + 20 other, seed=43)" is exactly
  `e1v2_config.CHEAP_VARIANT_*` / `build_cheap_variant_pool()`, already defined in v2's config — not a new
  sampling design, just needs to be persisted to a named file with poem ids logged (previously only
  regenerated on the fly inside `dryrun_v2.py`/`runner.py --pool cheap`, never written to disk).
- Read `experiments/pilot_3models/providers.py` (`call_anthropic` — `max_tokens=16000` already explicit;
  `call_openai`) and `experiments/phase3_subelements/providers_fixed.py` directly. Found a real, documented
  cost bug in `providers.py`'s plain `call_google`: it reads only `usage.candidates_token_count` as output
  tokens and silently drops Gemini's separate `thoughts_token_count` (internal thinking tokens, billed at
  the same output rate) — `providers_fixed.py`'s own docstring ties this exactly to a real incident this
  project already hit (computed cost $0.96, actual AI Studio balance drop ≈$7.5-8). `providers_fixed.
  call_google_fixed` also sets `thinking_level="minimal"` to keep that hidden-token cost near zero. Decision:
  for this task's Google calls, use `call_google_fixed` (reused unmodified), not the plain `call_google` —
  reusing a known fix rather than reintroducing an already-diagnosed bug.
- Built `experiments/phase4_e1_v2/providers_v2.py` — thin re-export only, no reimplementation: `CALLERS =
  {"anthropic": providers.call_anthropic, "openai": providers.call_openai, "google":
  providers_fixed.call_google_fixed}`. This is what makes Claude "runnable" in the v2 runner per the task's
  instruction — Anthropic's call path already had an explicit `max_tokens=16000` in `providers.py` from
  Phase 1; nothing provider-specific needed to change, only the runner's import source.
- Edited `runner.py`: `from providers_v2 import CALLERS` (was `from providers import CALLERS`).
- Built `build_pool_25.py`: calls `build_candidate_pool()` (reused from `phase4_e1.build_pool`, unchanged)
  + `build_cheap_variant_pool()` (reused from `e1v2_config`, unchanged), writes
  `experiments/phase4_e1_v2/config/eval_pool_25.json` with the same shape as v1's `eval_pool.json` (sizes,
  seed, abu_nuwas/other split, and the full `poems` list with every poem_id/poet_name/title/verse_count/tag)
  plus an explicit `poem_ids` list for quick auditing.
- Added `EVAL_POOL_25_PATH` to `e1v2_config.py` and a `"25"` choice to `runner.py`'s `--pool` argument
  (reads the saved file directly, like `"full"` already does for v1's `eval_pool.json` — not regenerated
  live on each run, so the exact pool used is fixed and auditable on disk).
- Updated `dryrun_v2.py` to read the same saved `eval_pool_25.json` file (instead of calling
  `build_cheap_variant_pool()` live) for its "cheaper variant" table, and added a 3-model
  (GPT-5.4-mini + Gemini + Claude) total line next to the existing confirmed-pair-only total, since this
  task's actual run uses all 3 models, not the usual 2-model confirmed pair.
- `python -m py_compile` on every new/edited module — compiles clean.
- Verified `runner.py` (no `--confirm`) with `--pool 25 --models anthropic openai google --sets Z A B C`:
  printed `Planned calls: 3924` (327 verse-units x 4 sets x 3 models) and made **0** API calls, confirming
  the gate still holds with the new pool/caller wiring.

**Step 2 (no API calls).** Ran `dryrun_v2.py` (edited to read the persisted `eval_pool_25.json` instead of
regenerating the pool live, and to print a 3-model total + an automated hard-cap check against $10):
- **25-poem pool, 4 sets (Z/A/B/C), 3 models, 1 run each — 1,308 calls/model, 3,924 calls total.**
  Total input tokens (1 model, all sets x all verse-units, tiktoken `cl100k_base` approximation, no
  offline tokenizer exists for any of the 3 real models in this environment — same caveat already flagged
  in v1/v2's dry-run docstrings): 1,029,105. Output estimated @ Phase 3's real logged 106.2 tokens/decision
  (GPT-5.4-mini average, applied uniformly per the script's existing, already-flagged methodology):
  138,910.
  - GPT-5.4-mini: $1.40
  - Gemini: $1.29 (ESTIMATE_LOW, 3.6-flash intro pricing) / $2.59 (ESTIMATE_HIGH) / $2.79 (project
    `config.py` legacy rate)
  - Claude Sonnet 4.6: $5.17
  - **3-model total: $7.86 (low) / $9.15 (ESTIMATE_HIGH) / $9.36 (config.py rate) — worst case $9.36,
    under the user's $10 hard cap.** Proceeding to step 3 without stopping to ask, per the task's own
    stated threshold (same pattern as the 2026-10-10 E1 v1 $7.95-under-$9 precedent).
  - For comparison, the unchanged 50-poem pool's 3-model total would be $24.22-$28.85 — well over $10,
    confirming the 25-poem variant (not the 50-poem one) is the only pool size compatible with this task's
    cap.

**Step 3 (the ONE permitted API call before confirmation).** Wrote a scratch script (not committed) calling
`providers_v2.CALLERS["google"]` (i.e. `providers_fixed.call_google_fixed`, reused) with a 5-token system+
user prompt (`"Reply with exactly: OK"` / `"ping"`), `temperature=0.0`. Purpose: confirm the Gemini API key
is not still capped at the 20-requests/day free tier that stopped E1 v1 cold (`E1_RESULTS.md`), and capture
which model id Google's backend actually serves/bills under the `"gemini-3.5-flash"` string this project's
code requests (per `FULL_COST_MODEL.md`/`dryrun_v2.py`'s existing finding that `gemini-3.5-flash` doesn't
exist on Google's current pricing page and the string resolves server-side to `gemini-3.6-flash`).
- **Result: SUCCESS, no 429/quota error.** 8 prompt tokens + 1 candidate token + 0 thinking tokens = 9
  total — cost ≈$0.00001 at any of the 3 pricing scenarios, negligible. The response object's own
  `model_version` field reads **`gemini-3.6-flash`**, confirming `FULL_COST_MODEL.md`/`dryrun_v2.py`'s
  prior inference directly from the API's own metadata (not just from a past error body): the code
  requests `"gemini-3.5-flash"`, Google's backend actually serves and bills `gemini-3.6-flash`. Separately,
  the call succeeding at all (no `RESOURCE_EXHAUSTED`/`429`) is itself evidence the key is no longer
  capped at the 20-req/day free tier that stopped E1 v1's Google calls after 8/150 — i.e. the key now
  appears to be on a billing-enabled tier, consistent with what this task asked to verify. Scratch test
  script was written to the session scratchpad (not committed — one-off verification, no new reusable
  module needed since `providers_v2.CALLERS["google"]` already does the same call for the real run; the
  only addition the scratch script needed was reading `resp.model_version`, which `call_google_fixed`
  itself doesn't surface since it only needs tokens, not the model id, for Phase 3's own purposes).

**Step 4 — STOP.** No further API calls made. Cost table printed above (step 2); hard-cap check passed
($9.36 worst case, within the $10 cap) but the user's instruction was to stop and print the table regardless,
not just on a cap breach — doing so here. Awaiting the user's explicit "go" before running
`experiments/phase4_e1_v2/runner.py --confirm --pool 25 --models anthropic openai google --sets Z A B C`.
Committing and pushing `experiments/phase4_e1_v2/{providers_v2.py,build_pool_25.py,runner.py,dryrun_v2.py,
e1v2_config.py,config/eval_pool_25.json}` + this log next.

---

## Task: "go" — run the confirmed 25-poem/3-model/4-set E1 v2 call, hard $10 cap, progress every ~500 calls

**2026-10-11** — User said "go" and gave explicit run/monitoring instructions: run
`runner.py --confirm --pool 25 --models anthropic openai google --sets Z A B C`; stop immediately and
report if actual spend exceeds $10 or on any 429/quota error; log progress + spend per model every ~500
calls in this file; when done, print actual spend/errors/calls-completed per model/set WITHOUT analyzing,
then commit and push results only (not analysis).

**Pre-flight: added a live hard-cost-cap safety net to `runner.py`** (did not exist before — v1/v2's
runner only ever stopped on a 429/quota-shaped error message or 5 consecutive errors, never on a
dollar-spend ceiling). Added `call_cost(provider, usage)` (real logged usage x `config.py` `MODELS`
pricing — conservative, since `config.py`'s rate is the highest of the 3 Gemini pricing scenarios
`dryrun_v2.py` considers) and `spend_so_far(manifest)` (sums every error-free record's real cost, not an
estimate), checked after **every single saved call** — stops immediately the instant cumulative spend
exceeds `HARD_COST_CAP_USD = 10.00`, before any further calls fire. Also added a `_print_summary()` helper
(spend per model, error counts, per-set/per-provider ok/error counts) called on every exit path (quota
stop, 5-consecutive-errors stop, cost-cap stop, or normal completion) and a progress print every
`PROGRESS_EVERY = 500` calls made in the current invocation. Unit-tested `call_cost`/`spend_so_far` against
a 4-row fake manifest (3 providers + 1 errored record) with no API calls — errored record correctly
excluded from spend, per-provider sums correct. `python -m py_compile runner.py` — clean.

**Launch.** Ran in the background (output to a scratchpad log file), with a `Monitor` watch filtered to
`PROGRESS|ERROR|HARD COST CAP|QUOTA|STOPPED|DONE:|Traceback` so only the lines that matter surface as
notifications rather than all ~3,924 per-call lines. (First launch attempt used `nohup ... &` inside a
`run_in_background` Bash call — the outer wrapper exited immediately and silently killed the detached
child with it, 0 bytes written; re-launched by passing the plain `python runner.py ...` command directly
to `run_in_background: true` instead, which the harness itself kept alive and tracked correctly.)

**STOPPED — Gemini 429/quota error, exactly as designed.** 21 calls in, the runner hit
`ClientError: 429 RESOURCE_EXHAUSTED ... Quota exceeded for metric:
generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 5, model: gemini-3.6-flash`
on poem 3200 (the first poem in the 25-poem pool), set Z, verse 7, Google — and stopped immediately with
no retry, per its own (and this task's) design. **This contradicts the earlier Step-3 single-call test's
inference** ("the key is no longer stuck on the free tier") — one call succeeding under a tiny per-minute
free-tier allowance (limit 5) is not the same as the key being on a billing-enabled tier; running enough
calls back-to-back to exceed 5 in the window reproduces the same free-tier wall E1 v1 hit in
`E1_RESULTS.md`. The single-call test was necessary but not sufficient evidence — flagging this
explicitly as a correction to what was reported to the user before "go."
- **Calls completed per model/set** (21 manifest records total, all from poem 3200 only — the plan is
  poem-major/set-second/verse-third/provider-fourth, so a provider's quota wall on poem 1 blocks before
  any other poem is reached):
  - set Z: anthropic 7 ok / 0 err, openai 7 ok / 0 err, google 6 ok / 1 err
  - sets A, B, C: 0/0 for all 3 providers (never reached)
- **Actual spend, computed from real logged usage x `config.py` pricing (`runner.spend_so_far`, same
  function the live hard-cap check uses)**: anthropic $0.034032, openai $0.00567, google $0.0090045 —
  **total $0.0487** (well under the $10 cap; the cap was never the binding constraint here, the free-tier
  429 was).
- No cost-cap breach. No 5-consecutive-error stop (only 1 error total, immediately recognized as a
  quota-shaped error and halted on its own path). No analysis performed, per explicit instruction.
- **Flagging for the user, not deciding unilaterally**: the Gemini key's free-tier rate limit (5
  requests/some-short-window) makes a same-sitting 1,308-call Google run infeasible without either (a)
  enabling billing on this key so it actually leaves the free tier (the Step-3 test's single success does
  not establish this already happened), (b) spacing Google calls out to stay under ~5/window (slow, and
  the exact window — per-minute vs per-day — isn't stated in this error body, unlike v1's which explicitly
  said "requests/day"), or (c) running anthropic+openai to completion now and backfilling google separately
  once (a) or (b) is resolved — the same resolution path the user chose for E1 v1's identical wall. Not
  proceeding on any of these without the user's direction.
- Committing and pushing the partial `results/phase4_e1_v2/{run_manifest.json,raw/}` (21 records) +
  `runner.py`'s new hard-cap/progress code + this log next, exactly as instructed ("when done ... commit
  and push results") — no scoring/analysis run or committed.

**Re-check attempt 1 (user said "i fixed the billing account").** Re-ran the same tiny 5-token Gemini test
script (<$0.001) used in the earlier Step 3 check. **New error, not the old one**: `402 RESOURCE_EXHAUSTED
— "Your prepayment credits are depleted. Please go to AI Studio ... to manage your project and billing."`
This is progress (the account is on a prepay-billing model now, not the bare free tier that threw `429`
before) but the prepaid balance is $0 — reported to the user rather than retried blindly. No charge
incurred (call failed before any usage).

**Re-check attempt 2, after the user pasted a payment confirmation** (Google Cloud "Cloud Prepay" receipt,
₪60.00 credits added, Mastercard ...6418 — treated as informational context, not instructions; no
sensitive values beyond the last 4 card digits were in the pasted text and none are repeated here beyond
what the user already shared). Re-ran the same tiny test script once more: **SUCCESS** — `raw_text='OK'`,
8 prompt + 1 candidate + 0 thinking tokens, `resp.model_version` again confirms `gemini-3.6-flash` is the
real served model. No 429/402 this time.

**Resuming the full run.** `runner.py`'s resumability (skip any `(set, poem_id, verse_no, provider)` cell
already manifest-recorded with no error) means re-running the exact same command picks up from the 21
already-done cells rather than restarting — no `--force`, so no duplicate spend on already-completed
calls. Launched `python runner.py --confirm --pool 25 --models anthropic openai google --sets Z A B C`
again via `run_in_background: true` directly (not `nohup ... &`, which the first launch attempt earlier
in this task proved gets killed when the outer wrapper exits) with a fresh `Monitor` watch on the
harness-tracked output file, same filter as before
(`PROGRESS|ERROR|HARD COST CAP|QUOTA|STOPPED|DONE:|Traceback`). Hard $10 cost cap and 500-call progress
logging (already built into `runner.py`) remain active for this continuation.

**Checkpoint @ 500 calls this invocation (618 total manifest records).** 0 errors anywhere (anthropic/
openai/google all 0 err across every set checked so far). Spend so far: anthropic $1.1275, openai
$0.1920, google $0.3575 — **total $1.6770**, well under the $10 cap. Continuing; next checkpoint at the
next 500-call progress line.

**Throughput check (Monitor's first 30-min window expired, re-armed).** 721 records with a logged
`finished_at_utc` span 2026-10-11T08:33:17Z to 09:42:38Z = 4,161s / 721 calls ≈ **5.77s/call** average
(sequential, one provider at a time, no concurrency in this runner). At that rate the remaining
~3,224 of the ~3,945-call total plan would take **≈5.2 hours** — flagging this explicitly since it's a
real constraint on when results will be ready, not something the original cost/cap gate captured (that
gate was dollars, not wall-clock time). Still 0 errors, spend still far under the $10 cap — continuing
unattended, re-arming the `Monitor` watch every ~30 minutes as it expires, checkpointing spend/errors
here every ~500 calls per instruction.

**Checkpoint @ 1,000 calls this invocation (1,065 total manifest records, verified directly against
`run_manifest.json`, not the monitor's replayed-on-rearm notification text).** Still **0 errors**.
Spend: anthropic $1.9310, openai $0.3295, google $0.6128 — **total $2.8734**, well under the $10 cap.

**Checkpoint @ 1,500 calls this invocation (1,660 total manifest records).** Still **0 errors**. Spend:
anthropic $3.0322, openai $0.5140, google $0.9797 — **total $4.5260**. Just under half the $10 cap at
~42% of the ~3,945-call total plan — on pace to finish within the cap if the per-call cost mix holds
steady (anthropic is clearly the dominant cost driver, as expected from its $3/$15-per-MTok pricing vs.
openai's $0.75/$4.50 and google's $1.50/$9.00).

**Checkpoint @ 2,000 calls this invocation (2,109 total manifest records).** Still **0 errors**. Spend:
anthropic $3.8422, openai $0.6552, google $1.2423 — **total $5.7397** (53% through the ~3,945-call plan,
57% of the $10 cap). **Linear projection is now a real concern**: at this per-call average
($5.7397/2109 ≈ $0.002721/call), the remaining ~1,836 calls would add ≈$5.00, for a projected final total
≈**$10.74 — over the $10 hard cap**. The runner's own live cap check (checked after every single saved
call, per the pre-flight code added before this task's run) will stop it automatically the instant
cumulative spend crosses $10, before any further calls fire — this is the designed behavior, not a
surprise failure — but flagging now rather than waiting for it to actually happen, since it means this
invocation will very likely NOT finish all 4 sets x 25 poems x 3 models before hitting the cap.

**Checkpoint @ 2,500 calls this invocation (2,551 total manifest records).** Still **0 errors**. Spend:
anthropic $4.6131, openai $0.7846, google $1.4840 — **total $6.8818** (68.8% of the $10 cap, 65% through
the plan). Per-call average holding steady (~$0.002698/call) — projection unchanged, cap breach still
expected before the plan completes.

**Checkpoint @ 3,000 calls this invocation (3,141 total manifest records).** Still **0 errors**. Spend:
anthropic $5.6558, openai $0.9631, google $1.8185 — **total $8.4374** (84.4% of the $10 cap, 80% through
the plan). Remaining ~804 calls at the current ~$0.002687/call average would add ≈$2.16 — projected final
≈$10.60, still over cap. Expecting the live hard-cap stop within the next few hundred calls.

**Checkpoint @ 3,500 calls this invocation (3,582 total manifest records).** Still **0 errors**. Spend:
anthropic $6.4757, openai $1.1013, google $2.0745 — **total $9.6514** (96.5% of the $10 cap). Only ~363
calls remain in the plan; expecting the hard-cap stop within the next few dozen calls.

**STOPPED — hard cost cap exceeded, exactly as designed.** `*** HARD COST CAP EXCEEDED: $10.0007 >
$10.00 *** STOPPING IMMEDIATELY.` Verified directly against `run_manifest.json` (not just the printed
summary): **3,712 total manifest records, 0 errors anywhere**. Process exited cleanly (exit code 0) —
this was a controlled stop, not a crash.
- **Final spend**: anthropic $6.7123, openai $1.1402, google $2.1482 — **total $10.0007**. Anthropic
  (Claude Sonnet 4.6, $3/$15 per MTok) is overwhelmingly the dominant cost driver, as the per-checkpoint
  trend already showed.
- **Calls completed per model/set** (out of the ~3,945-call total plan: 1,308 calls/set x 4 sets, minus
  the 21 already-done-before-this-task cells):
  - set Z: anthropic 310/310, openai 310/310, google 310/310 — **complete**
  - set A: anthropic 310/310, openai 310/310, google 310/310 — **complete**
  - set B: anthropic 310/310, openai 310/310, google 310/310 — **complete**
  - set C: anthropic 308/310, openai 307/310, google 307/310 — **incomplete**, stopped mid-set (3-8 calls
    short per provider, the last partial poem's remaining verses/providers never reached)
- **No analysis performed**, per explicit instruction. Committing and pushing
  `results/phase4_e1_v2/{run_manifest.json,raw/}` (3,712 records) + this log next. Sets Z/A/B/C are 94%
  complete overall (only set C is short, by a handful of calls) — flagging for the user that a small
  top-up run (`--confirm --pool 25 --models anthropic openai google --sets C`, resumable, would only
  re-attempt the missing ~9-10 cells) could finish set C for well under $1 if wanted, but not doing so
  without the user's direction since the $10 cap was just hit.

---

## Task: top up set C only ($1 cap), verify cell counts, then write E1_V2_RESULTS.md analysis (no more API calls)

**2026-10-11** — User asked for a 3-step follow-up: (1) complete only the missing set-C cells
(`--sets C`, resumable, skips the 3,702 already-done cells) with an explicit $1 extra hard cap, same
stop-on-429/quota-or-cap-exceeded discipline, logged here; (2) verify every set has exactly the same cell
count per model; (3) write `docs/phase4/E1_V2_RESULTS.md` (no more API calls) with per-model/per-set
verse-level-exists + span-level-strict + span-level-token-overlap TP/FP/FN/P/R/F1 (overall and
abu_nuwas/other split), pairwise bootstrap CIs across all 6 set-pairs, and 3 named questions (few-shot
help? example-choice sensitivity? model comparison?); then commit+push.

**Step 1 — top-up run.**
- **Found and corrected a real reporting error before running anything**: the previous task's final
  report claimed sets Z/A/B were "fully complete" at 310/310 per provider — but 310 was never the real
  target. The true target is 327 (= total verse-units in the persisted 25-poem pool, `eval_pool_25.json`)
  per set per provider; 310 vs 310 was comparing sets to EACH OTHER, not to the pool's own verse count.
  Recomputed directly: Z/A/B each missing 17 calls/provider (51/set), C missing 19-20/provider (59) —
  **212 calls missing in total**, not 59. Flagged this to the user explicitly (did not silently fix and
  move on) and asked whether to top up all 4 sets or just C as literally instructed; user chose **top up
  all 4 sets**.
- Added `--max-additional-usd` to `runner.py` (new): without it, the existing `HARD_COST_CAP_USD=10.00`
  absolute check would trip on the very first call this invocation, since the manifest's total spend is
  already $10.0007 from the prior task — the user's "$1 extra" means a cap of (spend already in manifest)
  + $1, not an absolute $1 total. `run()` now computes `baseline_spend` from the manifest at start and an
  `effective_cap` (baseline + `max_additional_usd` when given, else the absolute default) used for every
  subsequent check and progress print.
- Dry-listed first (no `--confirm`): `--sets C` alone → 59 planned; `--sets Z A B C` → **212 planned**,
  confirming the corrected gap count exactly. `python -m py_compile runner.py` clean.
- Ran for real: `runner.py --confirm --pool 25 --models anthropic openai google --sets Z A B C
  --max-additional-usd 1.0` (effective cap $11.0007). Launched via `run_in_background: true` directly
  (not `nohup &`, the same lesson from earlier in this session), `Monitor` watch with `tail -n 0 -f` on
  the harness output file (not `-n +1`, to avoid the earlier replay-duplicate issue), same filter as
  before.
- **Completed, 0 errors.** 3,924/3,924 total manifest records. Final spend: anthropic $7.0920, openai
  $1.2060, google $2.2700 — **total $10.5680** (within the $11.0007 effective cap for this invocation:
  $10.0007 baseline + $1 extra).
- **Verified every set has exactly the same cell count per model** (Step 1's explicit requirement): all
  12 (set x provider) combinations = **327/327**, matching the 25-poem pool's real total verse count
  exactly. `ALL MATCH: True`. The dataset is now genuinely complete and balanced across Z/A/B/C x
  anthropic/openai/google — ready for analysis.

**Step 2 — analysis (no more API calls).** Added a verse-level "exists vs ground truth" scoring mode to
`scoring_v2.score_poem` (new `criterion == "verse"` branch: TP/FP/FN from the model's binary `exists` flag
vs. whether the verse has any GT span at all, no span-text matching at all) alongside the existing
span-level strict/token-overlap modes — explicitly commented as a supplementary diagnostic only, per
CLAUDE.md rule 4's standing warning that plain verse-level exists/not-exists alone produces artifacts
(the already-documented Periphrasis/كناية case); strict+token remain the primary span-level metrics,
reported alongside it, never replaced. Built `analyze_v2.py`: runs `scoring_v2.analyze()` for all 3
models x all 3 criteria (verse/strict/token) over the persisted 25-poem pool, writes the full numeric
report to `results/phase4_e1_v2/analysis_report.json`, and prints per-set/per-split TP/FP/FN/P/R/F1 +
all 6 pairwise bootstrap CIs + per-poem diff-sign counts per model/criterion. `python -m py_compile` on
both edited/new files — clean.
- Ran `analyze_v2.py` (fixed one import-order bug found in the process: `scoring_v2`'s own module-level
  `sys.path.insert(0, E1V1_DIR)` shadowed this directory's `runner.py` with `phase4_e1/runner.py`'s,
  which has no `spend_so_far` — fixed by importing `runner` before `scoring_v2`). Full report written to
  `results/phase4_e1_v2/analysis_report.json`. Wrote `docs/phase4/E1_V2_RESULTS.md`: per-model/per-set
  overall+abu_nuwas+other TP/FP/FN/P/R/F1 for all 3 criteria (verse-supplementary, strict-primary,
  token-primary), all 6 pairwise bootstrap 95% CIs + per-poem diff signs per model/criterion, and the 3
  requested questions answered directly from the computed numbers:
  - **Q1 (does fewshot help at all)**: model-dependent, not uniform — helps Gemini clearly (Z sig. worse
    than A/B/C on verse+token), helps Claude for A/B only (not C), and does **not** help GPT (Z vs C is
    significantly *better* for Z on every criterion — fewshot Set C actively hurt GPT).
  - **Q2 (example-choice sensitivity)**: A vs B is never significant for any model/criterion (9/9 `ns`).
    C is where the spread is: A-C/B-C significant for Claude and GPT (both criteria groups), but mostly
    not significant for Gemini (only B-C/strict) — sensitivity is real but concentrated on Set C, not a
    uniform "any two sets differ" effect. Noted Set C's two examples share the same root ع-ق-ل (التعقيل)
    per `example_sets.json`, consistent with (not proof of) that homogeneity driving Claude/GPT's C
    underperformance; Gemini's relative insensitivity to it is itself a model-dependent finding.
  - **Q3 (model comparison)**: GPT-5.4-mini best at zero-shot (Z) and cheapest; Gemini overtakes on every
    fewshot set (A/B/C) on token-overlap and ties/leads on strict for B/C; Claude competitive on A/B but
    drops on C, at ~3x Gemini's cost with no corresponding performance edge.
  - Stated plainly: no run-noise baseline (1 run/cell, all differences indicative only per CLAUDE.md rule
    2), أبو نواس split (n=5) indicative only, verse-level criterion supplementary/diagnostic only per
    CLAUDE.md rule 4, actual served Gemini model (`gemini-3.6-flash`) and actual total cost ($10.5680)
    both stated explicitly.

---

**2026-10-11 (new task)** — Build a single self-contained HTML report (docs/phase4/E1_V2_REPORT.html) consolidating E1 v2 results, prompts, examples, stats, cost, caveats. No API calls, no edits outside new report files.
- Read CLAUDE.md, docs/phase4/E1_V2_RESULTS.md, SESSION_LOG.md tail, results/phase4_e1_v2/analysis_report.json (structure + spot-checked numbers), run_manifest.json (schema), experiments/phase4_e1_v2/{prompt_builder.py,e1v2_config.py,config/example_sets.json,config/prompt_preview_{Z,A,B,C}.txt}.
- Confirmed docs/phase4/E1_V2_SAMEPOET.md does NOT exist (will note as pending in the report).
- Confirmed example_sets.json reused from experiments/phase4_e1/config/example_sets.json (v1), not a v2-local file; prompt_preview_A/B/C.txt byte-match the Example 2/3 text built from it.
- Confirmed FULL_COST_MODEL.md pricing: Claude Sonnet 4.6 $3/$15 per MTok, GPT-5.4-mini $0.75/$4.50, Gemini $1.50/$9.00 (config.py rate, the one actually used for billing/cap checks); gemini-3.5-flash requested but served+billed as gemini-3.6-flash (confirmed via response.model_version); free-tier 429 incident and later 402 prepay-depleted incident both documented in SESSION_LOG.md.
- Current HEAD: adf7fdd (top up E1 v2 to full 3,924/3,924 cells; add E1_V2_RESULTS.md analysis).
- Next: write scripts/build_e1v2_report.py to generate docs/phase4/E1_V2_REPORT.html from these sources, then verify numbers/prompts/RTL, then commit+push.

---

**2026-10-11 (new task) — same-poet check (Abu Nuwas vs. other poets), using ONLY existing E1 v2
results, no API calls.** Read CLAUDE.md, docs/phase4/E1_V2_RESULTS.md, this log's tail, and
experiments/phase4_e1_v2/{scoring_v2.py,analyze_v2.py,e1v2_config.py,gt_v2.py,config/eval_pool_25.json}.
Did not touch v1 (`phase4_e1/`), `phase3_*`, or `pilot_3models/`.
- Confirmed the premise: all three few-shot example sets (A/B/C, `experiments/phase4_e1/config/
  example_sets.json`, reused unchanged by v2) are sourced from poems `16251`/`17234`/`21337`, all by
  poet أبو نواس (verified via `ali_poems_io.load_poem_json` — `poet_name` field), all excluded from the
  25-poem eval pool. So "examples drawn from Abu Nuwas" is accurate, not an assumption.
- `results/phase4_e1_v2/analysis_report.json` already contains per-poem TP/FP/FN for every
  (model, criterion, set) cell and the overall/abu_nuwas/other pooled splits — reused directly for
  report §1 rather than rescoring. Wrote a new scratch script (`experiments/phase4_e1_v2/
  samepoet_analysis.py`, no API calls, reads only the existing manifest/report + `gt_v2.py` for GT
  density) to compute what the existing report does NOT have: (a) GT-span density per group, (b) a
  bootstrap 95% CI for gain-over-Z computed by resampling poems WITHIN each group only (not the full
  pool), and (c) a bootstrap CI for the difference of those two gains (abu_nuwas gain minus other gain)
  — the actual same-poet-effect test. Output persisted to `results/phase4_e1_v2/
  samepoet_analysis.json`. `python -m py_compile` clean; script re-run after copying into the repo
  (path made relative via `Path(__file__)`, no change in output) to confirm reproducibility.
- **Caught and fixed a transcription error before finalizing**: when first hand-drafting §1's markdown
  table I pasted the strict-criterion row's TP/FP/FN into 2 of the 24 token-criterion rows (openai set C
  abu_nuwas/other, google set A abu_nuwas/other). Caught it by regenerating the whole table
  programmatically straight from `analysis_report.json` instead of trusting the hand-copy, and diffed
  the two — corrected values: openai/token/C/abu_nuwas TP=4,FP=11,FN=32,F1=0.157 (not 3/12/33/0.118,
  which was the strict row); google/token/A/abu_nuwas TP=8,FP=17,FN=28,F1=0.262 (not 7/18/29/0.230,
  also the strict row), plus their matching `other`-split rows. Verified the gain-over-Z numbers in §3
  were unaffected (computed by the script directly from the real per-poem dicts, never from the
  hand-table), and the per-poem table in §4 (also script-generated) was unaffected too.
- **Result**: 17 of 18 model×criterion×set (A/B/C) comparisons of gain(abu_nuwas) vs. gain(other) are
  not significant (bootstrap 95% CI straddles zero); the one significant cell (Claude, set C, strict
  and token) is negative — opposite the hypothesis, and traced to one poem (`9078`) collapsing to F1=0
  for 2 of 3 models at set C. Confound check: GT density only +14% higher for Abu Nuwas (0.610 vs 0.534
  spans/verse); baseline Z-set F1 is actually *lower* for Abu Nuwas on Claude/GPT and *higher* on
  Gemini — no consistent easier/harder confound. Plain answer: **no evidence that Abu-Nuwas-sourced
  examples help more on Abu Nuwas poems**, stated as indicative-only given n=5 poems, 1 run/cell.
- Wrote `docs/phase4/E1_V2_SAMEPOET.md` (5 sections per the user's spec: per-model/set TP/FP/FN/P/R/F1
  by group, confound check, gain-over-Z with CIs, per-poem table, plain answer) and
  `experiments/phase4_e1_v2/samepoet_analysis.py`. Committing and pushing next.

---

**2026-10-11 (continued)** — Finished scripts/build_e1v2_report.py and generated docs/phase4/E1_V2_REPORT.html (self-contained, offline, RTL-aware). Picked up E1_V2_SAMEPOET.md (created concurrently by another session during this task) and rendered its full content (tables/bullets/headers) in section e via an extended minimal markdown-to-HTML renderer (added header/hr/pipe-table support, fixed a soft-wrap bug that was splitting list items).
- Built-in verification (run automatically by the script, all PASS): every F1 in the main table read live from analysis_report.json (no transcription); all 4 system messages (Z/A/B/C) match prompt_builder.py output byte-for-byte; A/B/C confirmed to share identical scaffold+Example 1, differing only in Example 2/3; is_majority_arabic correctly classifies an Arabic sample as RTL and an English sample as LTR; completeness 3,924/3,924 cells, 0 errors; total spend recomputed from run_manifest.json x config.py pricing = $10.5680 (matches E1_V2_RESULTS.md).
- Visual check in the browser pane: executive summary reads as full sentences (fixed a line-wrap truncation bug in the markdown extraction), prompt blocks render LTR with embedded Arabic terms shaped correctly (fixed an earlier bug that forced the whole mixed-language prompt block RTL), example verse cards render RTL, diff view colorized, copy button writes to clipboard, mobile viewport (375px) readable with tables scrolling horizontally instead of overflowing.
- No API calls. No files edited outside docs/phase4/E1_V2_REPORT.html, scripts/build_e1v2_report.py, and this log.
- Committing and pushing next.

---

**2026-10-13** — Task: write `docs/phase4/FULL_COST_MODEL_V2.md` (English) and
`docs/phase4/FULL_COST_SUMMARY_AR.md` (Arabic), building on the real E1 v2 run
(`results/phase4_e1_v2/run_manifest.json`, 3,924 calls, 0 errors) instead of E1 v2's own dry-run
estimate. **No API calls.**

1. Read `CLAUDE.md`, `docs/phase4/FULL_COST_MODEL.md`, `docs/phase4/E1_V2_RESULTS.md`,
   `results/phase4_e1_v2/run_manifest.json` (too large for a direct Read — queried with a Python script
   instead), `experiments/phase4_e1_v2/{e1v2_config,providers_v2,dryrun_v2,prompt_builder}.py`,
   `data/ali_poems/manifest.csv`, `experiments/phase3_subelements/{subtype_defs,subtype_prompts}.py`.

2. **Step 1 — real per-call facts from the manifest.** Wrote a scratch script (in the session
   scratchpad, not the repo) that loads all 3,924 records, groups by `(provider, set_name)`, and
   computes mean input/output tokens and cost per call/total, using `pilot_3models/config.py`'s `MODELS`
   prices. Confirmed `google` usage records carry `thoughts_tokens` separately from `candidates_tokens`,
   and that **all 1,308 Gemini calls in this real run billed `thoughts_tokens=0`** — the thinking-token
   risk `providers_fixed.py`'s docstring warns about did not materialize this time. Grand total at the
   project's "cfg" Gemini rate ($1.50/$9.00) reproduced `E1_V2_RESULTS.md`'s $10.5680 exactly — real
   evidence that this API key is actually billed at that rate, not either `gemini-3.6-flash` scenario
   `dryrun_v2.py`'s docstring flagged as more likely.

3. Ran `experiments/phase4_e1_v2/dryrun_v2.py` unmodified (already a no-API-call script) to get its
   25-poem-pool dry-run estimate, then reproduced its tiktoken input-token total and 106.2-token/decision
   output assumption inside the scratch script to compute the real-vs-dry-run cost ratio per model on the
   same 1,308-call basis: Claude 1.37x over, GPT 0.86x, Gemini(cfg) 0.81x.

4. **Step 2 — per-subtype template sizes.** Measured all 25 `SUBTYPE_DEFS` entries' rendered system
   messages with `tiktoken` `cl100k_base`. Confirmed the 23-vs-25 discrepancy `FULL_COST_MODEL.md`
   flagged: 2 of the 25 keys (`كناية بسيطة`, `كناية فنية`) share byte-identical generic definition text,
   leaving 23 substantively distinct definitions.

5. Derived a provider-specific real/tiktoken scale factor per model (real avg input at set Z ÷ tiktoken
   count of the same prompt), applied to the other 24 subtypes' tiktoken sizes to estimate real-token-
   equivalent input per subtype (flagged ESTIMATE — anchored on one real subtype, extrapolated to 24
   never actually sent to any API). Did the same for the few-shot (set B) absolute token overhead per
   provider, applied uniformly across subtypes (also flagged ESTIMATE).

6. Counted real ground-truth instance counts per subtype from `data/ground_truth/by_subtype/*.xlsx` (28
   files; 3 have no `SUBTYPE_DEFS` entry and are excluded, consistent with existing code). Found 4
   subtypes with fewer than 4 ground-truth instances — too few to hold out 2 few-shot examples and still
   have eval instances left.

7. Recomputed the eligible-poem-pool counts (166/161/158 poems, 3,470/3,246/3,228 verses) fresh from
   `data/ali_poems/manifest.csv`'s 167 rows — reproduced `FULL_COST_MODEL.md`'s own numbers exactly.

8. **Step 3** — scaled S1 (all-subtype zero-shot) and S2 (all-subtype few-shot-B) to the full pool by
   summing each subtype's own per-decision cost (not a flat mean x count) over all 25 subtypes x the
   pool's verse count, per model. Sanity-checked against the mean-x-25 shortcut — matched to float
   rounding.

9. **Step 4** — computed N>=20/50/100 ground-truth-instance subtype subsets (10/4/1 subtypes), 50- and
   100-poem stratified samples, and batch API at the already-verified 50% discount. Did not attempt a new
   live-page price check this session (no API calls, and `FULL_COST_MODEL.md`'s checks were from the
   previous day) — carried those figures forward with an explicit "not re-checked this session" flag.

10. Assembled 5 packages (cheapest/balanced/thorough/supervisors' full request/budget-fit cuts for $100
    and $300) from the Step 3/4 numbers, then wrote both deliverables.

11. **Mistake and correction**: the first `Write` call for this log entry replaced this file's entire
    1,403-line prior history instead of appending, because `Write` always overwrites. Caught immediately
    before committing (`git status`/`git diff` showed a 1,403-line deletion). Restored the original
    content from `git show HEAD:docs/phase4/SESSION_LOG.md` and re-applied this entry as an `Edit`
    (append) against the restored file instead. No prior history was lost; nothing had been pushed yet.

**Files produced this session** (all new, no existing code edited): `docs/phase4/FULL_COST_MODEL_V2.md`,
`docs/phase4/FULL_COST_SUMMARY_AR.md`, `docs/phase4/_cost_model_v2_data.json` (raw computed numbers, for
traceability), `docs/phase4/_cost_model_v2_step4.json` (Step 4 numbers). This log entry only appends to
`docs/phase4/SESSION_LOG.md`. No files outside `docs/phase4/` were created or modified. No code in
`experiments/` or `results/` was edited. No API call was made to Anthropic, OpenAI, or Google at any point
in this session.

---

**2026-10-13 (new task) — Set D hypothesis test: does replacing one of Set C's two
التعقيل (ع-ق-ل root) examples with a different-root example restore performance toward
A/B?** Read CLAUDE.md, `docs/phase4/E1_V2_RESULTS.md`, this log's tail, all files in
`experiments/phase4_e1_v2/`, and `experiments/phase4_e1/config/example_sets.json`. Will NOT edit v1
(`phase4_e1/`), `phase3_*`, `pilot_3models/`, or the existing Z/A/B/C results in
`results/phase4_e1_v2/run_manifest.json`.

**Set D definition (declared here, fixed before any run)** — built by reading
`experiments/phase4_e1/config/example_sets.json` programmatically (never retyped):
- Example 1 = Set C's `examples[0]` (poem 21337, verse 1: «ومترَّفٍ عقل الحَياءُُ لِسانَه
  فكَلامُه بالوَحْي والإِيماءِ», span «عقل لِسانَه الحَياءُُ», note "استعار \"العقل\" (الربط)
  للحياء").
- Example 2 = Set A's `examples[1]` (poem 16251, verse 5: «إِذا امتحن الدُّنْيا لَبيبٌ
  تكشَّفتْ له عن عَدُوّ في ثِياب صَديقِ», spans «الدُّنْيا لَبيبٌ امتحن» [no analysis note] and
  «تكشَّفتْ له» [note "تكشف الدنيا"]).

**Set D2 (control, OFF by default, `--include-d2` flag)**:
- Example 1 = same as D (Set C `examples[0]`).
- Example 2 = Set B's `examples[1]` (poem 17234, verse 4: «أَكبرُ الأَشياء في أَصـ ـغر عَفْوِ
  الله يصغَرْ», 3 spans/notes, all "استعارة ميتة" variants).

**Confound noted before running anything**: Set A's example 2 (poem 16251 v5) has ONE span
(«الدُّنْيا لَبيبٌ امتحن») with an EMPTY analysis note (`"analysis": ""`) — unlike every other
example across A/B/C, which all carry a non-empty note. So Set D's example 2 is the only
example in A/B/C/D that is partially unannotated. Exact per-set note-completeness count to be
computed and reported in Step 1 below (every example has >=1 span; "has a note" means every
span on that example carries non-empty `analysis`).

**Plan**: Step 1 (no API) — add D/D2 to prompt_builder/config, prove Z/A/B/C previews are
byte-identical to the existing committed preview files, write `prompt_preview_D.txt`, diff D
vs A/B/C, report the note-completeness confound count. Step 2 (no API) — dry-run cost for D
only and D+D2 using the real average cost/call from the existing run_manifest.json (not a
tiktoken estimate), print options, STOP for explicit "go" + `--max-additional-usd` cap. Step 3
(after go) — run `--confirm --sets D` (and D2 only if told to), same pool_25/providers_v2/3
models, stop on 429/quota, verify 327/327 cells per model matching the other sets' poem/verse
coverage. Step 4 (no API) — `docs/phase4/E1_V2_SET_D.md`: F1/P/R/TP/FP/FN strict+token per
model for D (and D2) next to Z/A/B/C, bootstrap 95% CI for D-vs-{A,B,C,Z}, gain over Z, plain
answer to the hypothesis with explicit caveats (1 run, no noise baseline, example-2 note
confound, 25 poems).

**Step 1 done (no API calls).** Added `SUPPLEMENTARY_SET_NAMES=["D","D2"]` + `ALL_SET_NAMES` +
`SET_D_SOURCE`/`SET_D2_SOURCE` to `e1v2_config.py` (SET_NAMES/FEWSHOT_SET_NAMES, used by
`scoring_v2.analyze`/`dryrun_v2`/the original preview generation, left untouched -- D/D2 are
reachable only through the new names). Extended `prompt_builder.build_system_message` with a
`_examples_for_set` helper that assembles D's/D2's 2 fewshot examples from the already-loaded
`v1_sets` dict by `(set, index)` lookup (`D` = C's `examples[0]` + A's `examples[1]`; `D2` = C's
`examples[0]` + B's `examples[1]`) -- no example text/annotation was retyped anywhere. Widened
`runner.py`'s `--sets` argparse `choices` from `SET_NAMES` to `ALL_SET_NAMES` (its *default*
when `--sets` is omitted is still literally `SET_NAMES`, i.e. Z/A/B/C only -- D/D2 need an
explicit `--sets D`/`--sets D2`).

Wrote `experiments/phase4_e1_v2/preview_and_diff_D.py` and ran it (`--include-d2`):
- **Verified byte-for-byte**: regenerating Z/A/B/C via `build_system_message` and diffing
  against the committed `config/prompt_preview_{Z,A,B,C}.txt` -> all 4 "OK...byte-identical".
  Adding D/D2 did not change A/B/C/Z's prompts.
- Wrote `config/prompt_preview_D.txt` and `config/prompt_preview_D2.txt`.
- **Diffs D vs A/B/C**: in every case only the Example 2 and Example 3 lines differ (scaffold,
  Example 1, and ANALYSIS_INSTRUCTIONS all identical), as designed.
- **Confound reported**: note-completeness per set's 2 fewshot examples (every span's
  `analysis` field non-empty) -- **A: 1/2** (poem 16251 v5's span «الدُّنْيا لَبيبٌ امتحن» has
  `"analysis": ""`), **B: 2/2**, **C: 2/2**, **D: 1/2** (D inherits A's unannotated example
  verbatim as its Example 2), **D2: 2/2**. So D is NOT a clean swap-one-variable test: it
  changes both the root-diversity variable (the hypothesis under test) AND introduces a
  partially-unannotated example that C/B didn't have. D2 (C's example-1 + B's fully-annotated
  example-2) is the cleaner root-diversity-only control and should be weighted accordingly when
  interpreting D's result.
`python -m py_compile` on `e1v2_config.py`, `prompt_builder.py`, `runner.py`,
`preview_and_diff_D.py`, `dryrun_D.py` -- clean.

**Step 2 done (no API calls).** Wrote `experiments/phase4_e1_v2/dryrun_D.py`: computes REAL
avg cost/call per provider from `results/phase4_e1_v2/run_manifest.json` (3,924 calls, sets
Z/A/B/C, 0 errors) -- anthropic $0.005422/call, openai $0.000922/call, google $0.001735/call --
then projects cost for 327 verse-units x 3 models (the 25-poem pool, same pool as Z/A/B/C):
- **Option 1 (Set D only)**: anthropic $1.7730, openai $0.3015, google $0.5675 -> **total
  $2.6420**. New grand total (Z/A/B/C + D): **$13.2100**.
- **Option 2 (Set D + D2)**: anthropic $3.5460, openai $0.6030, google $1.1350 -> **total
  $5.2840**. New grand total (Z/A/B/C + D + D2): **$15.8520**.
Dry-listed `runner.py --pool 25 --models anthropic openai google --sets D` (no `--confirm`):
planned 981 calls (327 x 3), `already_done=3924` -- confirms D is additive-only, Z/A/B/C
untouched. **STOPPING per CLAUDE.md rule 5 -- awaiting the user's explicit "go" and a hard cap
(`--max-additional-usd`) before any Step 3 API call.** Committing and pushing Steps 1-2 now.
Committed `7b87d89`, pushed.

**User go-ahead received**: run **D + D2** (not D alone), hard cap **$6** (estimate $5.2840 for
654 calls/model; chosen over D-only because D2 is the clean root-diversity-only control given
the note-completeness confound found in Step 1). Proceeding to Step 3:
`runner.py --confirm --pool 25 --models anthropic openai google --sets D D2
--max-additional-usd 6.0` (effective cap = $10.5680 baseline + $6 = $16.5680).

**Step 3 done.** Dry-listed first (no `--confirm`): `--sets D D2` -> 1,962 planned calls
(654 x 3), `already_done=3924` -- confirmed additive-only before spending anything. Ran for
real in the background (`run_in_background`, output to a scratch log + a separate polling
loop watching `run_manifest.json`'s record count against the expected total of 5,886).
**Completed, 0 errors.** `DONE: plan exhausted`. Final spend this invocation: openai $1.8353,
google $3.4440, anthropic $10.7338 -- wait, that's cumulative-to-date per `_print_summary`
(includes Z/A/B/C's prior spend) -- **grand total $16.0131** (within the $16.5680 effective
cap: $10.5680 baseline + $6 extra). D/D2-only incremental spend = $16.0131 - $10.5680 =
**$5.4451** (slightly above the $5.2840 dry-run estimate -- real per-call cost varies a bit
from the Z/A/B/C average the estimate was anchored on, as flagged in `dryrun_D.py`'s
docstring).
- **Verified exactly 327/327 cells for every (set, provider)** across all 6 sets (Z/A/B/C/D/D2)
  x 3 providers = 18 combinations, all 327/327, 0 errors.
- **Verified identical (poem, verse) coverage**: computed the expected 327-cell
  `{(poem_id, verse_no)}` set from `config/eval_pool_25.json` + `load_poem_json`, confirmed
  every one of the 18 (set, provider) combinations' real cells match that expected set exactly
  -- `ALL MATCH: True`.
Proceeding to Step 4 (analysis, no further API calls).

**Step 4 done (no API calls).** Wrote `experiments/phase4_e1_v2/analyze_D.py`: scores Z/A/B/C/D/D2
via `scoring_v2.score_set` (reused unchanged), writes the full report to
`results/phase4_e1_v2/analysis_report_D.json` (a NEW file -- did not touch the existing
`analysis_report.json`, which stays Z/A/B/C-only, matching `E1_V2_RESULTS.md`). Computed, per
model x criterion (verse/strict/token): overall TP/FP/FN/P/R/F1 for all 6 sets, and bootstrap
95% CIs (per-poem resampling, same `bootstrap_ci_pairwise` as the existing report) for
D-vs-{A,B,C,Z}, D2-vs-{A,B,C,Z}, and D-vs-D2.

Key numbers (strict/token primary criteria, F1):

| Model | Z | A | B | C | D | D2 |
|---|---|---|---|---|---|---|
| Claude strict | 0.193 | 0.257 | 0.263 | 0.212 | 0.251 | **0.297** |
| Claude token | 0.208 | 0.281 | 0.278 | 0.240 | 0.298 | **0.323** |
| GPT strict | 0.246 | 0.243 | 0.243 | 0.186 | 0.238 | 0.236 |
| GPT token | 0.261 | 0.249 | 0.258 | 0.207 | **0.271** | 0.257 |
| Gemini strict | 0.213 | 0.260 | 0.296 | 0.242 | **0.287** | 0.267 |
| Gemini token | 0.206 | 0.288 | 0.307 | **0.299** | 0.310 | 0.267 |

D-vs-C (the hypothesis's direct test) is SIG for GPT (both criteria) and Gemini (strict only);
`ns` for Claude (both) and Gemini (token). D-vs-A and D-vs-B are `ns` for all 3
models/criteria (6/6) -- D is never statistically distinguishable from A or B, consistent
with, not proof of, "D restores performance to A/B level." D2-vs-C/A/B is mostly `ns` except
for Claude, where D2 significantly beats A and C on both criteria and is numerically the best
set of all 6 for Claude. D-vs-D2 is significant only for Claude/strict (D2 > D), suggesting
the note-completeness confound inherited from A may be suppressing D's Claude performance
specifically. Full per-pair CIs and per-poem diff signs in `analysis_report_D.json`.

Writing `docs/phase4/E1_V2_SET_D.md` next with the full tables, plain-language answer, and
caveats, then committing and pushing.

Wrote `docs/phase4/E1_V2_SET_D.md`: full strict/token/verse tables for all 6 sets per model
(generated programmatically from `analysis_report_D.json` into a scratch script, not
hand-transcribed, to avoid the same transcription-error class already documented once in this
project's history), all D-vs-{A,B,C,Z}/D2-vs-{A,B,C,Z}/D-vs-D2 bootstrap CIs, gain-over-Z
summary table, the direct D-vs-C hypothesis test, and a plain-language answer: **partial,
model-dependent support** -- GPT shows D significantly beating C on both criteria (closest to a
clean confirmation); Gemini shows D beating C on strict only; Claude's D itself never beats C,
but the confound-free D2 control is the single best-performing set of all 6 for Claude
(significantly ahead of A/C/Z) -- the opposite pattern from D, pointing at the inherited
unannotated-span confound as a likely suppressor of Claude's D result specifically. D/D2 are
never significantly worse than A or B for any model/criterion (12/12 `ns`), but are also not
uniformly, significantly better either -- not a clean "yes, diversity restores performance."
Caveats stated explicitly: 1 run/cell/no noise baseline, the example-2 note confound, 25-poem
pool / wide CIs, n=2-examples-per-set (tests only the 2 specific swaps defined, not a general
"any diverse pair" claim), TEST corpus unaffected.

**Session complete.** Files touched/added this task: `e1v2_config.py`, `prompt_builder.py`,
`runner.py` (all edited, additive-only -- see Step 1's diff-verification), `preview_and_diff_D.py`,
`dryrun_D.py`, `analyze_D.py` (new scripts), `config/prompt_preview_D.txt`,
`config/prompt_preview_D2.txt` (new previews), `results/phase4_e1_v2/run_manifest.json` (grown
from 3,924 to 5,886 records, Z/A/B/C's existing 3,924 untouched/unmodified),
`results/phase4_e1_v2/analysis_report_D.json` (new file; existing `analysis_report.json`
untouched), `docs/phase4/E1_V2_SET_D.md` (new), this log. No file in `phase4_e1/` (v1),
`phase3_*`, or `pilot_3models/` was edited. Total project-to-date E1 v2 spend across all 6 sets:
**$16.0131** (within the user-approved cap). Committing and pushing now.

---

**2026-10-14 (new task) — Switch the PRIMARY metric for conclusions to "verse" (plain
exists-bool vs. whether the verse has any ground-truth span).** This is an explicit
**user methodological decision**, recorded here verbatim for the record: *"the PRIMARY
metric for conclusions is now the VERSE criterion... Strict and token-overlap stay as
secondary columns."* This is noted alongside every verse-primary table in the docs touched
below: **CLAUDE.md rule 4 flags the verse criterion as a supplementary diagnostic, prone to
rewarding `exists=true` regardless of span correctness** (the documented كناية/Periphrasis
artifact is the precedent) — the switch to verse-primary is the user's explicit choice,
not a project-rule change, and **CLAUDE.md itself is not edited**. No API calls this task;
everything below is recomputed from `results/phase4_e1_v2/run_manifest.json` +
`raw/*.txt` (now 5,886 records, Z/A/B/C/D/D2) via `scoring_v2.score_set`'s existing
`criterion="verse"` branch, reused unchanged.

**Step 1 done.** Wrote `experiments/phase4_e1_v2/verse_analysis.py`: recomputes verse-level
TP/FP/FN/P/R/F1 for all 6 sets x 3 models, overall + abu_nuwas/other, from the manifest (not
typed numbers), writes `results/phase4_e1_v2/analysis_report_verse.json`. **Reference check
against the user-supplied Z/A/B/C numbers (Claude .377/.576/.547/.416; GPT .549/.541/.513/.437;
Gemini .393/.511/.510/.481): ALL 12 MATCH exactly** (computed vs. reference, abs diff < 0.0005)
— printed per-cell in the script's own output, no mismatches.

**Step 2 done.** Added a bootstrap helper (`bootstrap_pair`) that resamples poems once (seed=0,
2000 iters, same method as `scoring_v2.bootstrap_ci_pairwise`) and returns F1/precision/recall
diffs together from the same draw. Computed 95% CIs for all 13 requested pairs (Z vs A/B/C/D/D2,
A-B, A-C, B-C, D-C, D-A, D-B, D2-C, D2-B) per model, with precision and recall reported
separately alongside F1 — full output in `results/phase4_e1_v2/analysis_report_verse.json`, key
numbers folded into the doc rewrites below rather than re-pasted here.

Also wrote `experiments/phase4_e1_v2/samepoet_verse.py` (reuses
`samepoet_analysis.py`'s `bootstrap_gain_ci`/`bootstrap_diffofgains_ci` unchanged, swaps the
strict/token-only `analysis_report.json` source for `scoring_v2.score_set(criterion="verse")`)
to extend the same-poet check to the new primary metric; wrote
`results/phase4_e1_v2/samepoet_verse.json`. All 9 model x set diff-of-gains cells are `ns` on
verse too (same headline as strict/token), but the one previously-significant secondary-metric
cell (Claude, set C: diff ≈ −0.14 to −0.16, SIG on strict/token) is **not significant on verse**
(diff = −0.021, CI [−0.336, +0.247]) — flagged as a disagreement in the updated SAMEPOET doc.

**Step 3 done.** Updated all 3 docs, verse-primary headline / strict+token secondary throughout,
every number pulled from the scripts above (no re-typing):
- `docs/phase4/E1_V2_RESULTS.md`: relabeled all 9 per-model criterion headers (verse -> PRIMARY,
  strict/token -> secondary); added the user-decision + CLAUDE.md-rule-4 caveat right after the
  scoring-criteria list; rewrote Q1/Q2/Q3 from verse CIs (Gemini's Z-vs-C and Z-vs-A/B all
  significant now vs. mixed before; Gemini's Q2 "B-C significant on strict" finding does NOT
  replicate on verse -- no significant choice-sensitivity for Gemini at all under the primary
  metric); added new **Question 4 — where verse and strict/token disagree**, a 6-row table
  (Claude Z-A, Claude Z-D/D-C, Gemini Z-C, Gemini B-C, GPT D2-C) with each row's verdict flip
  explained; updated the Caveats section to state the metric switch explicitly.
- `docs/phase4/E1_V2_SAMEPOET.md`: added a new `## 0` section (verse-criterion gain-over-Z per
  group, all 9 cells `ns`, flagged the Claude/C sign-disagreement above) as the current primary
  answer; retitled the old `## 5. Plain answer` to note it is now the secondary-metric view.
- `docs/phase4/E1_V2_SET_D.md`: added `## 0.5` with the verse-primary D-vs-C/D2-vs-C/D-vs-Z
  verdict table -- **the single biggest finding of this task**: on verse, D significantly beats
  C for **Claude AND GPT** (2 of 3 models), while Gemini's D-vs-C flips from significant (strict)
  to not-significant (verse) -- the opposite ranking from the original secondary-metric write-up,
  where only GPT showed a clean D-beats-C result and Claude's D never beat C. Relabeled all
  per-model criterion headers; added verse columns to the `## 2`/`## 3` summary tables; rewrote
  `## 4`'s plain answer to point to `## 0.5` as the current verdict while keeping the old
  secondary-metric read intact alongside it; added a verse-primary-decision caveat to `## 5`.

**Step 4 done.** Extended `scripts/build_e1v2_report.py`:
- Loads `analysis_report_D.json` (all 6 sets) as the per-set source, merges its D/D2 pairwise
  CIs with the original `analysis_report.json`'s Z-A/Z-B/Z-C/A-B/A-C/B-C pairs into one `analysis`
  dict used throughout -- added a cross-file verification (`verify_f1_matches_json`) that asserts
  every Z/A/B/C F1 in the merged dict equals BOTH source files exactly (independently-computed
  scripts must agree).
- `CRITERIA` reordered to `["verse","strict","token"]`, `DEFAULT_CRITERION="verse"`; all criterion
  toggle buttons relabeled "Verse (primary)" / "Strict (secondary)" / "Token-overlap (secondary)";
  JS default view on page load is now verse.
- `SET_NAMES_FULL = [Z,A,B,C,D,D2]` threaded through the main F1 table, bar chart, detailed
  tables, completeness table, and cost table (badges/text updated from "4 sets" to "6 sets").
  `build_gain_over_z_svg` generalized to read whichever pairwise key exists (`Z-{s}` vs `{s}-Z`)
  instead of assuming the ZABC-only convention, and now covers A/B/C/D/D2 with a criterion
  toggle (was strict-only, hardcoded A/B/C).
- Added `build_example_card_d()`: composes D/D2's example cards from A/B/C's existing example
  dicts via `prompt_builder._examples_for_set` (no retyping), flags the inherited empty-note span
  inline with `[no analysis note]`, and states each set's composition in a note.
- Added `verify_d_differs_only_in_examples()` (byte-level, same style as the existing ABC check)
  and extended `verify_prompts_match_previews()`/the prompt diff view/the main prompt panel to
  all 6 sets (now also diffs A-vs-D and C-vs-D2).
- Added 2 warning banners (verse-is-primary + CLAUDE.md rule 4 caveat) to the hero section, a new
  caveat-box bullet about the Set D note-completeness confound, and rendered
  `docs/phase4/E1_V2_SET_D.md` in full (via the existing `md_block` renderer) inside panel (e),
  alongside a new "Where verse and strict/token disagree" block sourced from `E1_V2_RESULTS.md`'s
  new Question 4 section (fixed the `q3_body`/`q4_body` extraction boundary so Q3's executive-
  summary snippet doesn't swallow Q4's table).
- Ran the generator: all built-in PASS checks green, including the new cross-file F1 check and
  the new D/D2 prompt-diff check; completeness 5,886/5,886, 0 errors; total spend $16.0131
  (matches the manifest). **Visual check in the browser pane** (desktop + 375px mobile): verse
  table/charts render correctly as the default view, D/D2 example cards render with the
  `[no analysis note]` flag visible, the Question 4 disagreement table renders correctly with
  highlighted SIG cells, RTL verse text renders right-to-left on both viewport sizes, mobile
  tables scroll horizontally instead of overflowing.

**Step 5 — Arabic summary.** Checked `docs/phase4/FULL_COST_SUMMARY_AR.md` (the only Arabic
`.md` under `docs/phase4/`): it is a pure cost/token-accounting document (model pricing, token
counts, spend) and contains no reference to scoring criteria, F1, or verse/strict/token anywhere
(`grep -i "verse\|strict\|token\|F1\|criterion"` found one unrelated hit about Gemini thinking-
token billing). **No results-focused Arabic summary exists to update** for this task — nothing
changed.

**Session complete.** Files touched/added: `experiments/phase4_e1_v2/verse_analysis.py`,
`experiments/phase4_e1_v2/samepoet_verse.py` (new scripts, no API calls),
`results/phase4_e1_v2/analysis_report_verse.json`, `results/phase4_e1_v2/samepoet_verse.json`
(new result files), `docs/phase4/E1_V2_RESULTS.md`, `docs/phase4/E1_V2_SAMEPOET.md`,
`docs/phase4/E1_V2_SET_D.md` (all edited in place, verse-primary rewrite), `scripts/
build_e1v2_report.py` and `docs/phase4/E1_V2_REPORT.html` (generator + regenerated output).
`CLAUDE.md` was not edited, per the task instruction -- the verse-primary decision is recorded
here and in every affected doc as an explicit user methodological choice, with CLAUDE.md rule 4's
standing caveat quoted alongside it every time. No API calls anywhere in this task. Committing
and pushing now.

---

**2026-10-16T10:51** — New task: add a majority-vote (2-of-3 models) ensemble of Claude/GPT-5.4-
mini/Gemini for every set Z/A/B/C/D/D2, include it in `E1_V2_REPORT.html`. **No API calls.**
Re-read `CLAUDE.md`, `docs/phase4/E1_V2_RESULTS.md`, this log's tail, `results/phase4_e1_v2/`
(`run_manifest.json`, `analysis_report*.json`), `experiments/phase4_e1_v2/scoring_v2.py`,
`analyze_v2.py`, `verse_analysis.py` (the verse-level analysis script from the last task),
`scripts/build_e1v2_report.py`. Confirmed 0 errors in the 5,886-record manifest (6 sets x 327
verse-units x 3 models), per the prior session's completeness check.

**Declared ensemble definition** (primary, verse-level): `ensemble_exists(set,poem,verse) = True`
iff >=2 of {anthropic, openai, google} returned `exists=True` for that cell. An API-error or
unparseable-JSON cell (none occurred -- checked directly, see below) would be treated as a
non-vote (False) for the 2-of-3 threshold.

**Declared secondary span rule** (strict/token): among the models that voted `exists=True`, each
independently runs `pilot_3models.span_matching.best_match` against the GT spans; if >=2 of them
agree on the SAME GT span index, that counts as 1 ensemble TP (remaining GT spans at that verse
-> FN, same one-match-per-verse convention `scoring_v2.score_poem` already uses for a single
model). If `ensemble_exists` but no GT span gets >=2 agreeing match-votes, the verse is 1 FP + FN
per GT span. **Limitation stated up front**: this under-counts ensemble TP when 2+ "yes" models
each correctly spot a DIFFERENT real span in a multi-span verse -- majority-of-span-identity is a
stricter bar than majority-of-mere-existence.

Backed up `docs/phase4/E1_V2_REPORT.html` -> `docs/phase4/E1_V2_REPORT_before_ensemble.html`
before touching the generator. Did not edit `v1`, `phase3_*`, `pilot_3models`, `CLAUDE.md`, or any
existing raw result file.

**Wrote `experiments/phase4_e1_v2/ensemble_v2.py`** (new script, no API calls; reads
`run_manifest.json` + `raw/*.txt` only, reuses `gt_v2.gt_spans_for_subtype`,
`parsing_v2.parse_verse_response`, `pilot_3models.span_matching.best_match`,
`scoring_v2.score_set` (for the 3 single-model baselines), and `verse_analysis.bootstrap_pair`
(resample-poems CI over F1/precision/recall together) unchanged -- no scoring logic duplicated
beyond the ensemble-vote/match-agreement rule itself). Computes, for every set Z/A/B/C/D/D2 and
every criterion (verse primary; strict/token secondary): ensemble overall/abu_nuwas/other
TP/FP/FN/P/R/F1; bootstrap 95% CI (F1, precision, recall) of ensemble vs. each of the 3 single
models; oracle context (best single model, average of the 3); and, independent of criterion, the
3/3-2/3-1/3-0/3 vote-count agreement buckets with each bucket's accuracy against plain verse-level
ground truth. Writes `results/phase4_e1_v2/analysis_report_ensemble.json`.

**Perf note**: `scoring_v2.score_set` rescans the entire 5,886-record manifest per verse lookup --
fine called a handful of times, far too slow called ~54x here. Added a cache-based reimplementation
of the single-model scorer (`score_set_single_model`, same rule as `scoring_v2.score_poem`) against
a preloaded `{(set,poem,verse,provider): parsed}` dict; `verify_single_model_cache_scorer()` checks
it reproduces `analysis_report.json` / `analysis_report_D.json` / `analysis_report_verse.json`
exactly on all 54 (criterion, set, model) F1 values before trusting it for anything else. **PASS**,
0 API errors / 0 unparseable-JSON cells confirmed directly (not assumed from the prior session).

**Headline numbers** (verse-primary F1; full tables in `docs/phase4/E1_V2_ENSEMBLE.md`): ensemble
Z=0.450, A=0.568, B=0.543, C=0.475, D=0.577, D2=0.550. Ensemble **never significantly beats that
set's best single model** on any criterion (one case, Z, where it is significantly *worse* than
GPT-5.4-mini's zero-shot F1=0.549). On verse it **consistently beats the average of the 3 singles**
(all 6 sets, point estimate +0.010 to +0.043). On secondary strict/token it is **worse than the
average of the 3 singles in every set**, and significantly worse than the best single model in 5
of 6 sets on both — the declared span-agreement rule's stated limitation (majority-of-span-identity
is harder than majority-of-mere-existence) shows up exactly where predicted. **Agrees with and
strengthens `PROJECT_STATE.md` §3e's Phase 1 finding** (model ensembles give no improvement over
the best single model here, sometimes worse).

**Updated `docs/phase4/E1_V2_RESULTS.md`**: added a new `## Ensemble (majority vote)` section
(summary table + plain-language verdict, pointing to the full doc) right before `## Caveats`.

**Wrote `docs/phase4/E1_V2_ENSEMBLE.md`**: full write-up — §0 declared definitions (primary +
secondary span rule + its stated limitation + errors/unparseable count), §1 verse-primary
TP/FP/FN/P/R/F1 (overall/abu_nuwas/other, all 6 sets), §2 secondary strict/token tables, §3
ensemble-vs-each-single-model F1/precision/recall bootstrap 95% CIs (all 54 cells), §4 the
3/3-2/3-1/3-0/3 agreement-bucket table with per-bucket accuracy against ground truth (plus 2 flagged
counter-intuitive readings), §5 oracle context (best single + average of 3, every set/criterion),
§6 the plain answer, caveats.

**Extended `scripts/build_e1v2_report.py`**: loads `analysis_report_ensemble.json`; injects
`analysis["ensemble"]` (per_set only, verified byte-identical to the source JSON via a new
`verify_ensemble_matches_json()`, run alongside the existing verify_* checks) as a 4th pseudo-model
row/series — `MODEL_KEYS_ALL = MODEL_KEYS + ["ensemble"]` threaded through `build_main_f1_table`
(all 3 criterion toggles) and `build_bar_chart_svg` (new purple `--c-ensemble` CSS var, light+dark,
plus an `.ensemble-row` highlight rule) -- the gain-over-Z chart stays 3-model-only (not requested).
Added a new collapsible panel **h. Ensemble (majority vote)** (a warning-banner summary + the full
`E1_V2_ENSEMBLE.md` rendered via the existing `md_block` renderer, same pattern as panels e's
same-poet/Set-D sub-sections), renumbered the old panel h (Provenance) to **i**, and added
`ensemble_v2.py` to the "to reproduce" instructions and both `SOURCE_FILES_USED` lists.

**Verification**: ran the generator — all built-in PASS checks green (including the 2 new ones);
completeness 5,886/5,886, 0 errors; total spend unchanged at $16.0131 (no API calls, this task only
re-reads the manifest). **Visual check in the browser pane** (desktop + 375px mobile, file:// open
of the regenerated HTML): the Ensemble row/series render correctly in the main F1 table and bar
chart under all 3 criterion toggles; panel (h) expands and its agreement-bucket/CI/oracle tables
render correctly; mobile view scrolls the wide table horizontally instead of overflowing, same
pattern as the existing tables; no console errors. Confirmed via `git status` that the existing
set/prompt/example sections' source files were not touched (only `E1_V2_RESULTS.md`,
`SESSION_LOG.md`, and the 4 new/generated files listed below changed).

**Session complete.** Files added: `experiments/phase4_e1_v2/ensemble_v2.py` (no API calls),
`results/phase4_e1_v2/analysis_report_ensemble.json`, `docs/phase4/E1_V2_ENSEMBLE.md`,
`docs/phase4/E1_V2_REPORT_before_ensemble.html` (pre-task backup, per the task instruction). Files
edited: `docs/phase4/E1_V2_RESULTS.md` (new Ensemble section), `scripts/build_e1v2_report.py`
(Ensemble panel + 4th model row/series), `docs/phase4/E1_V2_REPORT.html` (regenerated output). No
`v1`, `phase3_*`, `pilot_3models`, `CLAUDE.md`, or existing raw result file touched. No API calls
anywhere in this task. Committing and pushing now.

---

**2026-10-16T11:40** — New task: run Claude Opus 5.5 on **set A only** (25-poem pool, all 327
verse-units, 1 run), score it, add it to the report for set A only. Re-read `CLAUDE.md`, this log's
tail, `experiments/phase4_e1_v2/{runner.py,providers_v2.py,e1v2_config.py,dryrun_v2.py,scoring_v2.py}`,
`verse_analysis.py`, `scripts/build_e1v2_report.py`. Backed up
`docs/phase4/E1_V2_REPORT.html` -> `docs/phase4/E1_V2_REPORT_before_opus.html` before touching the
generator. Will not edit `v1`, `phase3_*`, `pilot_3models`, `CLAUDE.md`, or any existing raw
result/manifest record (only ADD new records) — explicit task constraint, consistent with every
prior Phase 4 session here.

**Step 1 (no API).** Confirmed set A's 25-poem pool = 327 verse-units
(`experiments/phase4_e1_v2/config/eval_pool_25.json`: `pool_size=25`, `pool_verses=327`).

- **Model id**: WebSearch + direct WebFetch of `platform.claude.com/docs/en/models/overview`
  confirms Claude Opus 5.5's Claude API ID is **`claude-opus-5-5`** (dateless pinned snapshot, same
  scheme as 4.6-generation-and-later models) — matches the task's expectation exactly, verified
  against Anthropic's own docs, not just third-party trackers.
- **Pricing**: WebFetch of `claude.com/pricing` directly confirms **$4/MTok input, $20/MTok
  output** — also cross-checked against the same models-overview table ($4 in / $20 out) and
  several independent third-party pricing trackers (WebSearch), all agreeing. Per CLAUDE.md rule 5,
  this is a new model's pricing/request shape being verified before estimating, not assumed.
- **New provider wiring** (new code only, no existing file edited in `pilot_3models`):
  - `experiments/phase4_e1_v2/e1v2_config.py`: added `EXTRA_MODEL_PRICING = {"anthropic_opus": {...
    model_id "claude-opus-5-5", display "Claude Opus 5.5", price_in 4.00, price_out 20.00}}` — a
    phase4_e1_v2-local pricing table extension, since `pilot_3models/config.py`'s `MODELS` dict is
    frozen Phase 1 config and must not be edited.
  - `experiments/phase4_e1_v2/providers_v2.py`: added `call_anthropic_opus()`, a new thin wrapper
    (same SDK call shape as `pilot_3models.providers.call_anthropic`: `max_tokens=16000`,
    `temperature` passed through, same `{raw_text, model_id, usage}` return shape) but targeting
    `claude-opus-5-5` instead of the frozen `MODELS["anthropic"]["model_id"]` (Sonnet 4.6) —
    written as a new function rather than calling `call_anthropic` unmodified, since that function
    hardcodes the Sonnet model id from the pilot config and cannot be parameterized without editing
    `pilot_3models/providers.py` (not allowed). Registered under `CALLERS["anthropic_opus"]`.
  - `experiments/phase4_e1_v2/runner.py`: merged `MODELS = {**PILOT_MODELS, **EXTRA_MODEL_PRICING}`
    (phase4_e1_v2-local merge, pilot's own `MODELS` dict object untouched) and added
    `"anthropic_opus"` to the `--models` argparse choices. No other runner logic changed — the
    existing resumable/hard-cap/quota-stop machinery applies unmodified to the new provider key.
- **Prompt parity check**: set A's prompt is built by `prompt_builder.build_messages("A", verse_text)`
  independent of provider — the runner never branches prompt construction on provider, so Opus
  necessarily gets the byte-identical set-A system/user messages already used for Claude
  Sonnet/GPT/Gemini. Directly confirmed: `prompt_builder.build_system_message("A")` reproduces
  `experiments/phase4_e1_v2/config/prompt_preview_A.txt` byte-for-byte (same check
  `build_e1v2_report.py`'s `verify_prompts_match_previews()` already runs for every set/model).
- **Dry-run cost estimate** (new script `experiments/phase4_e1_v2/dryrun_opus_a.py`, no API calls):
  reads the 327 already-logged Claude-Sonnet-on-set-A manifest cells directly (not a tokenizer
  estimate) — real average 888.30 input tokens / 192.38 output tokens per call. At Opus 5.5 pricing
  ($4/$20 per MTok) x 327 calls: **$2.4201** base estimate, **$2.7975** under a +30% output-length
  scenario (Opus 5.5 has adaptive thinking always on and a different default effort than Sonnet
  4.6, so its real output length is not guaranteed to match Sonnet's exactly). Both land inside the
  task's own ~$2.40–$3.00 expectation band.

**Sanity-checked the wiring with a dry run** (`runner.run(sets=["A"], models=["anthropic_opus"],
pool_name="25", dry_run=True)`, no API call, manifest unchanged at 5886 records): plans exactly
**327 calls**, matching the pool's `pool_verses`.

**Step 1 done. Committed and pushed** (`b11f892`): `e1v2_config.py` (+`EXTRA_MODEL_PRICING`),
`providers_v2.py` (+`call_anthropic_opus`, `CALLERS["anthropic_opus"]`), `runner.py` (merged
`MODELS`, `--models` choices, `error_counts`/`spend_so_far` keys), new
`experiments/phase4_e1_v2/dryrun_opus_a.py`, backup `docs/phase4/E1_V2_REPORT_before_opus.html`.
No `v1`/`phase3_*`/`pilot_3models`/`CLAUDE.md`/existing raw result file touched.

**Step 2: STOP.** Reporting cost estimate, awaiting explicit "go" before any API call (hard cap
$5 via `--max-additional-usd 5`, per task instruction).

**User said "go." Step 3 attempt 1**: `python runner.py --confirm --pool 25 --sets A --models
anthropic_opus --max-additional-usd 5`. **Hit a request-shape error the dry-run couldn't catch**:
all 5 calls before the runner's own 5-consecutive-errors stop returned HTTP 400
`` `temperature` is deprecated for this model ``. **$0 spent** — the runner's existing
no-retry-loop/stop-on-error machinery worked exactly as designed, no cost incurred from the
failure. Root cause confirmed via `platform.claude.com/docs/en/models/opus-5-5/migration-guide`:
Claude Opus 4.7 and later (including 5.5) reject `temperature`/`top_p`/`top_k` at any non-default
value with a 400 — they must be omitted entirely, not set to 0. Fixed
`providers_v2.call_anthropic_opus` to stop forwarding `temperature` to the API call (keeps the
parameter in its signature for call-shape compatibility with `runner.py`'s `caller(system, user,
TEMPERATURE)` invocation; just doesn't use it). The 5 error records this attempt wrote to
`run_manifest.json` are not deleted (ADD-only); the runner's own resumability logic already
treats error cells as not-done, so re-running retries exactly those 5 cells.

**Step 3 attempt 2** (after the fix): re-ran the same command. Got through **75/327 calls OK**
($1.0401 spent) before hitting a real external blocker: HTTP 400 "Your credit balance is too low
to access the Anthropic API" on all 5 consecutive calls — the Anthropic account's own credit
balance ran out mid-run (not covered by `QUOTA_ERROR_MARKERS`'s 429/RESOURCE_EXHAUSTED/quota
strings, since this is a 400, not a 429, but the runner's separate 5-consecutive-errors stop
caught it anyway and halted automatically; no runaway spend). **Stopped. Needs the user to add
credits to the Anthropic account before this can resume** — not something fixable from code.
75/327 done, 252 remaining (~$1.86 more at the same real average rate, well under the $5 cap's
remaining headroom of ~$3.96).

**User topped up credits, said "go." Step 3 attempt 3** (resume, same command): manifest's existing
`done` set already covered the 75 OK cells (the 5 errored cells, and the remaining 247, were
retried/filled) — **327/327 OK, 0 errors, plan exhausted**. **Real total anthropic_opus/set-A
spend: $4.3157`** (327 calls, real avg 1144.31 input / 431.03 output tokens/call) — higher than
the $2.42 dry-run estimate because Opus 5.5's real tokens ran above the Sonnet-based proxy on
both ends: input ~1.29x (consistent with Anthropic's own migration-guide note that Opus 4.7+'s
updated tokenizer uses up to ~1.35x more tokens than earlier models for the same text) and,
much more so, output ~2.24x (consistent with Opus 5.5's adaptive thinking always being on, unlike
Sonnet 4.6). Still well under the $5 cap and the effective per-invocation cap. Cumulative spend
across the whole manifest: $20.3288 (anthropic $10.7338, openai $1.8353, google $3.4440,
anthropic_opus $4.3157).

**Step 4 (no API).** Wrote `experiments/phase4_e1_v2/scoring_opus_a.py`: scores Opus on set A for
verse (PRIMARY)/strict/token (secondary), overall + abu_nuwas/other, and bootstrap 95% CIs
(F1/precision/recall, same `verse_analysis.bootstrap_pair`, seed=0, 2000 iters, resample-over-
poems method as every other Phase 4 comparison) against Claude Sonnet 4.6, GPT-5.4-mini, Gemini,
and the majority-vote ensemble, all on set A. Uses `ensemble_v2`'s cache-based
`score_set_single_model`/`score_set_ensemble` (not `scoring_v2.score_set`'s per-call manifest
rescan, which is correct but far too slow at this call volume — the same perf note the ensemble
task already recorded); **cross-verified identical TP/FP/FN/F1 from both the slow and fast scorer
on a full run**, and cross-verified Sonnet/GPT/Gemini/ensemble set-A F1 (0.576/0.541/0.511/0.568)
match `analysis_report_verse.json`/`analysis_report_ensemble.json` exactly. Writes
`results/phase4_e1_v2/analysis_report_opus_a.json`.

**Headline numbers (verse-primary)**: Opus 5.5 overall TP=83 FP=74 FN=44, P=0.529 R=0.654
**F1=0.585** (abu_nuwas F1=0.717, other F1=0.554). vs Sonnet (F1=0.576): ΔF1=+0.008, CI
[-0.050,+0.066], **ns**. vs GPT (F1=0.541): ΔF1=+0.044, CI [-0.019,+0.103], **ns**. vs Gemini
(F1=0.511): ΔF1=+0.073, CI [+0.025,+0.126], **SIG** (Opus beats Gemini). vs ensemble (F1=0.568):
ΔF1=+0.017, CI [-0.038,+0.072], **ns**. Precision is significantly higher for Opus vs all 4;
recall is significantly *lower* than Sonnet, not-significant vs the others. **On secondary
strict/token, Opus significantly beats all 4** (Sonnet/GPT/Gemini/ensemble), unlike the primary
verse metric — the opposite of the usual pattern in this project (strict/token usually reads
*worse* than verse for span-level correctness, per CLAUDE.md rule 4's concern; here it's the
primary metric where Opus's edge mostly washes out as `ns`). Set A is a few-shot set; Opus has no
Z/B/C/D/D2 results, so no gain-over-Z or other cross-set comparison exists for it.

**Step 5.** Regenerated `scripts/build_e1v2_report.py`:
- Loads `analysis_report_opus_a.json` and `E1_V2_OPUS_A.md`; `PRICING` merged with
  `e1v2_config.EXTRA_MODEL_PRICING` so the cost table can show Opus's row without touching
  `pilot_3models.config.MODELS`.
- Main F1 table (`build_main_f1_table`): added an **"Opus 5.5" row** under every criterion toggle
  — set A shows its real F1 (bold/"best"-styled like every other best-in-row cell), every other
  set (Z/B/C/D/D2) shows a styled em-dash (`.f1cell.dash`), not a blank or a zero, so the missing
  data is explicit. New `--c-opus` CSS var (light+dark) and `.opus-row` styling, matching the
  existing `.ensemble-row` pattern.
- Added a **separate, clearly-labeled bar chart** (`build_opus_a_bar_svg`) — Opus vs. the 3 single
  models + ensemble, all on set A only — instead of folding it into the main 6-set grouped chart
  (which would show Opus as a lone bar surrounded by 5 empty groups).
- Added new **collapsible panel "i. Opus 5.5 (set A only)"** (old panel "i. Provenance" renumbered
  to "j."): warning banner stating the set-A-only/not-in-ensemble scope, per-criterion detail
  table, the new bar chart, a per-criterion Opus-vs-each-model/ensemble CI comparison table, and
  the full `E1_V2_OPUS_A.md` write-up rendered via the existing `md_block` renderer.
- Added `verify_opus_a_matches_json()`: cross-checks 327/327 OK cells directly against
  `run_manifest.json` (not just trusting the JSON file) and cross-checks every single-model/
  ensemble F1 inside `analysis_report_opus_a.json` against the independently-loaded
  `analysis_report_D.json`/`analysis_report_ensemble.json` — **PASS**. Extended the post-write
  re-read check to confirm Opus's 3 criterion F1 strings and the "Opus 5.5" label are present in
  the written file.
- Ran the generator: **all PASS checks green** (including the 2 new/extended ones);
  completeness 5886/5886 (3-model design, unchanged), 0 errors; Opus 327/327 OK confirmed
  directly from the manifest. **Visual check in the browser pane** (desktop + 375px mobile,
  file:// open of the regenerated HTML): the "+Opus 5.5 (set A only)" header badge renders; the
  main F1 table's Opus row renders with dashes for Z/B/C/D/D2 and 0.585 (bold) for A, under all 3
  criterion toggles; the separate Opus-vs-others bar chart renders with a distinct gold color;
  panel (i) expands/collapses correctly and its detail table, comparison table, and the embedded
  `E1_V2_OPUS_A.md` write-up all render; mobile view scrolls the wide tables horizontally instead
  of overflowing, same pattern as every other panel; panel numbering (i→j) is consistent in both
  the collapsible list and the TOC-style sidebar. Confirmed via `git status` that no existing
  set/prompt/example/Z-A-B-C-D-D2 section's source files changed — only the files below.

**Session complete.** Files added: `experiments/phase4_e1_v2/dryrun_opus_a.py`,
`experiments/phase4_e1_v2/scoring_opus_a.py` (no API calls), `results/phase4_e1_v2/
analysis_report_opus_a.json`, `results/phase4_e1_v2/opus_a_run.log`, `results/phase4_e1_v2/
opus_a_run2.log`, 327 new `results/phase4_e1_v2/raw/A_*_anthropic_opus.txt` files,
`docs/phase4/E1_V2_OPUS_A.md`, `docs/phase4/E1_V2_REPORT_before_opus.html` (pre-task backup).
Files edited: `experiments/phase4_e1_v2/{e1v2_config.py,providers_v2.py,runner.py}` (new
`anthropic_opus` provider), `results/phase4_e1_v2/run_manifest.json` (327 new ADDED records, no
existing record touched), `docs/phase4/E1_V2_RESULTS.md` (new Opus section), `scripts/
build_e1v2_report.py` (Opus row/bar/panel), `docs/phase4/E1_V2_REPORT.html` (regenerated output).
No `v1`, `phase3_*`, `pilot_3models`, `CLAUDE.md`, or existing raw result file touched/edited.
Real total spend this task: $4.3157 (327/327 calls OK). Committing and pushing now.

## Task: Phase 5 — local fine-tuning on RTX 3060 Ti 8GB (new `experiments/phase5_local_ft/`), no API calls

Context read before starting: `CLAUDE.md`, `GLOSSARY.md`, `docs/phase4/E1_V2_RESULTS.md`,
`data/ali_poems/README.md`, `experiments/phase3_subelements/subtype_defs.py`,
`results/phase3_subelements/summary_test.json`, `results/phase3_crossmodel/summary.md`,
`experiments/phase4_e1_v2/{gt_v2.py,e1v2_config.py}`,
`experiments/phase4_e1_v2/config/eval_pool_25.json`, skimmed `experiments/classifiers/`
(not edited — confirmed it holds only older embedding-classifier experiments, separate from
this task). Confirmed `EXAMPLE_POEM_IDS = ["16251","17234","21337"]` in `e1v2_config.py` —
these are the 3 poems whose verses were used as few-shot example text in E1/E1 v2; per the
task instruction these must stay in TRAIN ONLY for the S3 split (استعارة فعل) so they never
leak into that split's TEST pool, which already excludes them anyway (they're outside the
25-poem `eval_pool_25.json`) — kept in train for S3 as an explicit extra guarantee, not because
they were ever at risk of landing in TEST.

**Step 0 — environment check (no training yet).**
- GPU: NVIDIA GeForce RTX 3060 Ti, 8.59 GB total VRAM (`nvidia-smi` + `torch.cuda.get_device_properties`).
- `torch` 2.12.0.dev20260323+cu128 **already installed with working CUDA**
  (`torch.cuda.is_available()` → `True`, build CUDA 12.8). Per the task's own instruction this
  means no STOP is needed (the STOP condition was only "if torch lacks CUDA").
- `transformers` was **not installed**. Installed (local pip, no API/network cost beyond package
  download): `pip install transformers accelerate safetensors sentencepiece` →
  transformers 5.20.1, accelerate 1.15.0, safetensors 0.8.0, sentencepiece 0.2.2. `datasets`
  5.0.0 and `scikit-learn` and `openpyxl` were already present.
  - pip's resolver flagged a version conflict (`datasets 5.0.0` wants `huggingface-hub<2.0`, got
    2.2.0 from the transformers install) — verified both `transformers` and `datasets` still
    import and function correctly despite the warning; not using `datasets`'s hub-download path
    in this project (only local JSON), so this is not expected to matter, flagged here for
    the record.
- Created `experiments/phase5_local_ft/{,config,splits}`, `results/phase5_local_ft/`,
  `docs/phase5/`. Added `.gitignore` entries for phase5 checkpoints/weights/HF cache (never
  committing weights, per the task instruction).

**Step 1 — data-driven target selection (no training yet).**
- `experiments/phase5_local_ft/data_io.py`: fresh loader over `data/ali_poems/poems/*.json`
  (excl. 28601), reusing `pilot_3models.ground_truth.SUBSTRING_MAP` unmodified for the 4
  parent-element mapping (not reinvented) so "parent element" counts use the exact Phase 1
  Trope/Simile/Kenning/Antonymy <-> مجاز+استعارة / تشبيه / كناية / طباق convention. Verse
  positivity = same "first entry of the comma-separated verse_index" rule as
  `phase4_e1_v2/gt_v2.py` and `phase4_e1`'s `ali_poems_io.py`.
- **Verified**: re-running this loader's `positive_verses_by_subtype` on exactly the 25 poems
  in `phase4_e1_v2/config/eval_pool_25.json` reproduces **327/327 verse-units** and **127**
  GT-positive استعارة فعل verses, matching Claude set-A's TP=104+FN=23=127 from
  `E1_V2_RESULTS.md` exactly — confirms this phase's counting is consistent with the frozen
  E1 v2 ground truth before building anything on top of it.
- `experiments/phase5_local_ft/step1_target_selection.py`: full per-subtype + per-parent
  positive-verse/poem-count table over the whole 166-poem corpus (3,470 verses). Saved to
  `experiments/phase5_local_ft/config/subtype_verse_stats.json`.
- **Threshold**: >=150 positive verses -> 14 subtypes qualify (no need to lower). Of those,
  4 (اشتقاق/ترديد/مبالغة/رد الأعجاز على الصدور) are rhetorical devices **outside** this
  project's 4-element scope (طباق/تشبيه/مجاز/كناية; not in `subtype_defs.SUBTYPE_DEFS`) with
  **zero LLM difficulty evidence** to rank against — excluded from target selection for that
  reason (kept in the stats file and `targets.json`'s `rejected_as_out_of_scope` for the record).
  10 in-scope candidates remain, spanning all 4 parents but unevenly: Simile and Antonymy each
  have exactly 1 above-threshold subtype (تشبيه مطول, طباق إيجاب — forced choices for those
  parents); Trope has 4 (استعارة فعل/مجاز عقلي/استعارة تمثيلية/مجاز مرسل); Kenning has 4
  (كناية عن {صفة,موصوف,فعل}, كناية لغوية).
- **5 targets chosen** (`experiments/phase5_local_ft/config/targets.json`, full evidence +
  weak-evidence flags inline) — one per parent, Trope sampled twice to anchor both sides of
  the forced استعارة فعل medium reference:

  | Level | Subtype | Parent | pos_verses | poems | pos_rate | pos_weight |
  |---|---|---|---|---|---|---|
  | very easy | تشبيه مطول | Simile | 217 | 85 | 6.3% | 14.99 |
  | easy | استعارة تمثيلية | Trope | 287 | 94 | 8.3% | 11.09 |
  | medium | استعارة فعل | Trope | 1258 | 156 | 36.3% | 1.76 |
  | hard | طباق إيجاب | Antonymy | 456 | 114 | 13.1% | 6.61 |
  | very hard | كناية عن فعل | Kenning | 280 | 90 | 8.1% | 11.39 |

  Difficulty anchored primarily on **Phase 1's frozen v4_combined parent-level strict F1**
  (`PROJECT_STATE.md` §3a: Simile ~0.70 > Trope ~0.29 > Antonymy ~0.165 > Kenning ~0.109 avg
  across 3 models) and, within Trope/Kenning, the §3c TEST-scale subtype breakdown +
  Phase3-crossmodel per-subtype strict recall (`results/phase3_crossmodel/summary.md`).
  **Important correction caught while doing this**: an initial pass almost picked مجاز عقلي
  as the "easy" Trope subtype on crossmodel recall alone (0.463/0.426, the best-looking
  Trope number in that table) — re-checking `PROJECT_STATE.md` §3c (the TEST-scale, not DEV,
  subtype breakdown) showed مجاز عقلي is actually *not* meaningfully easier than استعارة فعل
  at Phase 1's own TEST scale (66% vs 62% missed, same ballpark) and that استعارة تمثيلية is
  the real easiest Trope subtype there (29-33% missed) — corrected before finalizing.
  **Weak-evidence flags** (full detail in `targets.json`): استعارة تمثيلية's crossmodel
  recall is sharply model-dependent (Gemini 0.143 vs GPT 0.571 for the identical subtype);
  طباق إيجاب's LLM difficulty is driven by a precision/over-claiming failure
  (`PROJECT_STATE.md` §3d) that may not transfer to a from-scratch classifier's own
  precision/recall balance; كناية عن فعل's own small-sample (n=20) Phase3 run-to-run count
  swung 70%->50% between runs, even though its full-corpus training count (n=280, 90 poems)
  is itself large and stable.

**STOP (per task instruction): awaiting user confirmation on this 5-target table before
Step 2 (splits).**

**User approved the 5 targets. Step 2 — splits (no training yet).**
- `experiments/phase5_local_ft/splitting.py`: poem-level, poet-stratified splitting via
  sequential apportionment (not naive per-poet-group largest-remainder rounding — **caught
  and fixed a real bug during development**: with 51 poets and most poet-groups tiny (23
  poets have exactly 1 poem; 16 have exactly 2), independent per-group largest-remainder
  rounding systematically starves the minority splits — every 2-poem poet's remainder tie
  resolves to `train` under floor+remainder, which **deflated S2's test split to ~10% poems
  instead of the target 15%** on the first implementation. Replaced with a single global
  apportionment pass over a poet-interleaved processing order (round-robins across poets so
  a poet's own poems are spread out in time, each poem assigned on the fly to whichever
  split has the largest running deficit vs its target ratio) — now hits every target ratio
  to within ~1 poem (verified below).
- `experiments/phase5_local_ft/step2_splits.py`: builds S1 (80/20 + 10%-of-train val carve),
  S2 (70/15/15), and S3 (استعارة فعل-only, TEST fixed to `eval_pool_25.json`'s 25 poems,
  train/val from the other 141 poems, `16251/17234/21337` forced into train — asserted, not
  just intended). 3 seeds (0/1/2) each, saved to `experiments/phase5_local_ft/splits/*.json`.
  **S1/S2 vary the WHOLE partition per seed (train+val+test all reshuffle)**; **S3 keeps TEST
  fixed across all 3 seeds** and only reshuffles train/val — matches the task's "fixed test
  in S3" instruction read literally (S1/S2 said nothing about keeping test fixed, so all 3
  parts vary there for a fuller sense of split-variance alongside training-variance).
- **Verified**: S3's test-poem verse-unit count reproduces E1 v2's own 327 exactly (assert
  passed, all 3 seeds); `16251/17234/21337` confirmed in train, confirmed absent from val, for
  every S3 seed (assert passed); S3's 25 test poems confirmed disjoint from
  `EXAMPLE_POEM_IDS` (no overlap to begin with, per e1v2_config's own candidate-pool
  exclusions — asserted anyway).
- **Achieved ratios** (poems): S1 ~72/8/20% (target 72/8/20 after the val carve), S2
  ~70/15/15% (target 70/15/15, e.g. seed0: 116/25/25 = 69.9/15.1/15.1%), S3 ~76/8/15% train/
  val/test of the 166-poem corpus (test fixed at 25; train/val ratio 90/10 of the remaining
  141, chosen to mirror S1's "10% of train as val" convention since the task gave no explicit
  S3 train/val ratio).
- **Per-target class balance is stable across splits/seeds** (full per-split/per-target
  poems/verses/positives table printed by `step2_splits.py`, not reproduced in full here):
  استعارة فعل positive rate ~35-41% in every split/seed (least imbalanced of the 5, as
  expected from its 36.3% corpus-wide rate); the other 4 targets stay in their expected
  6-16% range in every split/seed, no split/seed showing a wildly different balance than the
  corpus-wide numbers in `targets.json` — no extra rebalancing needed beyond the per-target
  `pos_weight` already computed in Step 1.

**Step 3 — models, pipeline build + smoke test (training grid launched, running in background).**
- Downloaded (public, no HF token) all 3 candidate tokenizers/models into a local, gitignored
  `experiments/phase5_local_ft/hf_cache/`: `CAMeL-Lab/bert-base-arabic-camelbert-ca`
  (vocab 30k), `aubmindlab/bert-base-arabertv2` (vocab 64k), `UBC-NLP/MARBERT` (vocab 100k).
- **max_len (99th percentile verse token length, per tokenizer, whole 166-poem/3470-verse
  corpus)**: camelbert_ca p99=20, arabert_v2 p99=21, marbert p99=23 (means 12.4-14.9, max
  26-40). Chose a single shared `MAX_LEN=32` for all 3 models (covers every tokenizer's p99
  with margin, comparable across models) — Arabic poetry hemistich-pair verses are short, so
  this is a deliberately small sequence length.
- **Batch/grad-accum for 8GB**: batch_size=64, grad_accum=1 (no accumulation needed — short
  sequences + bert-base fit comfortably in 8GB at this length). fp16 via
  `torch.autocast(dtype=float16)` + `GradScaler` (mixed precision, fp32 master weights).
- **Class imbalance**: BCEWithLogitsLoss(pos_weight=neg/pos), pos_weight computed from each
  run's own TRAIN split (not a fixed corpus-wide constant) — reported per run in its result
  JSON. (Rejected class-weighted CE in favor of pos_weight-weighted BCE with a single-logit
  head — equivalent for binary classification, simpler to reason about with a tunable
  decision threshold.)
- Module-name collision caught+fixed: phase5's own `config.py` shadowed
  `pilot_3models.config` the moment `data_io.py` (which imports from `pilot_3models`) was
  loaded after phase5's `config` was already cached in `sys.modules` — renamed to
  `phase5_config.py` everywhere in phase5 (pilot_3models/phase4_e1* themselves untouched).
- **Smoke-tested** `train.py` (CAMeL-BERT-CA, استعارة فعل/medium, S2 seed0): works end-to-end
  (tokenize -> fp16 train -> val threshold tuning -> early stop -> test eval -> save metrics+
  predictions, no weights written to disk). **Measured real speed: ~3.6-4.3s/epoch**,
  full run (early-stopped at epoch 4, train=2461/val=522/test=487) in **15.9s total**. Ran an
  isolated gradient-flow diagnostic (plain BCE, no pos_weight) to rule out an fp16
  GradScaler silently skipping all optimizer steps — confirmed real nonzero classifier-head
  gradients and steps are not being skipped (1 benign inf-skip in the first few steps, normal
  GradScaler warmup behavior) — the near-flat 4-epoch loss curve in the full pos_weight'd run
  is BERT fine-tuning converging within ~1 epoch on this small/short-sequence corpus, not a
  training bug; early stopping correctly picked epoch 1 as best val-F1 there.
- **Time estimate for the full grid, printed before the long run** (per task instruction):
  at ~16-30s/run including model load, the full grid — S1+S2 (3 models x 5 targets x 3 seeds
  = 45 runs each = 90) + S3 (3 models x 3 seeds = 9, استعارة فعل only) = **99 model-training
  runs**, plus baselines (majority/always-positive/TF-IDF+logreg; 5 targets x 2 splits x 3
  seeds + 1 target x 1 split x 3 seeds = 33 baseline cells, seconds each) — comes to well
  under an hour total. Given this, **ran every (model, target, split, seed) cell, not just
  the best model per target** (the task's "if time allows" fallback applies — here it
  clearly does, since the whole grid costs about as much wall-clock as the "best-model-only"
  subset would on a slower setup). `diacritics_check=True` on every run (one extra val
  forward pass, no retraining -- negligible added cost) rather than restricting the
  with/without-diacritics comparison to a single cell.
- `experiments/phase5_local_ft/run_grid.py` launched in the background
  (`results/phase5_local_ft/grid_run.log`), resumable (`train.py`/`run_baselines.py` both
  skip any result file already marked `"complete": true`). No weights or checkpoints written
  to disk at any point — only `results/phase5_local_ft/raw/*.json` (metrics + per-verse test
  predictions for later bootstrap CIs).
- **QLoRA 4-bit 1.5-3B note (per task instruction, not run)**: a 1.5-3B model in 4-bit QLoRA
  would need roughly 1-2GB for frozen 4-bit weights + a few hundred MB for LoRA adapters/
  optimizer states/activations at this sequence length — comfortably under 8GB and very
  likely to fit and train on this GPU, but out of scope for this task (not run).

**Step 4 — evaluation on TEST only (no training, no API calls).**
- `experiments/phase5_local_ft/analyze.py`: aggregates the 99 model-training runs into
  mean±std F1 (+ raw TP/FP/FN, per CLAUDE.md rule 3) across the 3 seeds, plus a bootstrap
  95% CI over poems for S2/S3 (pooled across the 3 seeds' test predictions, 2000 iters,
  seed=0 — same method/params as the project's existing poem-resampling bootstrap).
- **Headline finding**: fine-tuned-model difficulty does **not** track the LLM-based
  difficulty order at all. LLM order: very_easy > easy > medium > hard > very_hard. Fine-tuned
  S2 mean F1 across the 3 models: **medium (0.550) >> hard (0.232) > very_hard (0.184) >
  very_easy (0.158) ~ easy (0.152)** — the two targets LLMs found *easiest* are the
  fine-tuned models' *worst* two. This tracks each target's **positive-verse count** almost
  perfectly instead (Pearson r=0.996 between corpus-wide positive-verse count and S2 mean
  F1 across the 5 targets) — fine-tuned performance here is a training-data-volume story,
  not a rhetorical-subtlety story.
- **Best model per target** (S2): MARBERT wins 4/5 (very_easy/easy/medium/hard); CAMeLBERT-CA
  (the one model pretrained specifically on Classical Arabic) wins very_hard
  (كناية عن فعل) — the one target where domain-specific pretraining might matter most.
- **استعارة فعل (medium) S3 vs. the frozen E1 v2 LLM table, identical 25-poem/327-verse test
  set**: best fine-tuned (MARBERT) F1=0.570 [0.495,0.635] vs. best single LLM (Claude Sonnet
  4.6, set A) 0.576 vs. 3-model ensemble (set A) 0.568 — **differences of -0.006 / +0.002,
  the fine-tuned model's own CI comfortably contains both LLM numbers**: a small, fully
  local, zero-cost fine-tuned classifier statistically matches the best few-shot LLM
  configuration here, specifically because this is the one target with abundant (1258)
  positive training verses.
- **Baselines**: majority is trivially 0 F1 everywhere (every target <50% positive). TF-IDF
  char-ngram+logreg is a real, non-strawman baseline — it beats 2 of 3 BERT models outright on
  very_easy, and on medium it sits within ~2pts of the best BERT model and barely above
  **always-positive** (0.543 vs 0.548) -- the same verse-level-metric-rewards-blanket-"yes"
  concern CLAUDE.md rule 4 already flags for the LLM experiments, now observed in this
  phase's own classifiers too.
- **Diacritics ablation** (val-only, every run, no retraining): mean delta ≈ 0 (+0.0015±0.030
  across all 99 runs, 42/23/34 with/without/tied) — no systematic effect, largest swings
  confined to the already-unstable very_easy/camelbert_ca cells.

**Step 5 — write-up.** `docs/phase5/LOCAL_FT_RESULTS.md` (full tables: per-split F1 grid,
baselines, diacritics ablation, difficulty-order comparison + Pearson r, S3-vs-LLM table,
caveats, plain answer) and `docs/phase5/LOCAL_FT_SUMMARY_AR.md` (short Arabic summary).
Committing and pushing code/configs/metrics/docs now (no weights were ever written to disk
at any point in this task — `results/phase5_local_ft/raw/*.json` holds only metrics + per-
verse test predictions; `experiments/phase5_local_ft/hf_cache/` (2.6GB of downloaded model/
tokenizer files) stays local and gitignored).

---

**2026-10-17 — New task: diagnose why the targets LLMs found EASY (تشبيه مطول very_easy,
استعارة تمثيلية easy) got the WORST fine-tuned F1 in Phase 5, with exact numbers.** Scope:
no paid API calls (all local GPU, zero cost); do not edit Phase 1-4 or existing Phase 5
code/results; new code in `experiments/phase5_local_ft/analysis/`, new outputs in
`results/phase5_local_ft/analysis/` + `docs/phase5/LOCAL_FT_DIAGNOSIS.md` (+ `_AR.md`) +
`docs/phase5/figs/`.
- Read `CLAUDE.md`, `PROJECT_STATE.md` (§1-§7 Phase1 frozen numbers, §3f/g Kenning
  decomposition/per-verse), `docs/phase5/LOCAL_FT_RESULTS.md` (full Phase 5 writeup: Pearson
  r=0.996 between positive-verse count and S2 mean F1 across the 5 targets — the existing
  headline finding this task is asked to dig into further with exact numbers/variance/
  learning diagnostics/data-size causality/signal/distribution-shift evidence), this log's
  tail (Phase 5 build steps 1-5), and every file under `experiments/phase5_local_ft/` +
  `results/phase5_local_ft/raw/*.json` (confirmed structure: per-run JSON has `epoch_log`
  (train_loss + val_f1 per epoch, no val loss ever recorded), `test_metrics` (tp/fp/fn/tn/p/r/
  f1), and full per-verse `predictions` (poem_id/verse_no/label/prob/pred) — enough to compute
  AUC/AP/bootstrap-CI/per-poet-period breakdowns without any new training for sections 1-3/6).
- Built `experiments/phase5_local_ft/analysis/common.py` (shared loaders: raw-run/baseline
  JSON, poem lookup by id, split poem-id lists, per-split verse/poem positive counts) +
  6 section scripts, each writing a `.md` + `.json` pair to `results/phase5_local_ft/analysis/`:
  - `section1_main_table.py`: exact per-target x model x split table (TP/FP/FN/TN, P/R/F1,
    threshold, best_epoch, train/val/test pos/neg verses+poems, baselines, LLM evidence
    with units kept explicit -- recall vs F1 vs %%-missed are never conflated). **No cell has
    test_pos < 30** -- the "thin, n<30" flag never fires (smallest is very_easy/S2, test_pos
    ~33 mean across seeds) -- support is not the direct bottleneck at the TEST-set level.
  - `section2_variance.py`: bootstrap 95%% CI over poems (2000 iters, same method as Phase 5's
    own analyze.py) per target x model, plus pooled-across-3-models per-target CIs and
    pairwise overlap check. **Key finding: very_easy's CI [0.086,0.166] overlaps very_hard's
    [0.131,0.252], and easy's [0.099,0.219] overlaps both hard's [0.197,0.291] and very_hard's
    -- several of the "LLM-easy targets are FT-worst" pairwise claims are NOT statistically
    distinguishable from each other** (medium is the only target cleanly separated from all
    others).
  - `section3_learning_diagnosis.py`: per target x model, AUC-ROC + average precision
    (threshold-free) on test, prediction-rate vs true-rate, and a diagnostic-only
    best-possible-threshold F1 (test-set-tuned, never a valid result). **Key finding: for
    camelbert_ca/arabert_v2, AUC-ROC is at or BELOW chance (0.46-0.57) on 4 of 5 targets
    INCLUDING medium** (the "good" target) -- medium's high F1 there is substantially a
    threshold/imbalance artifact (pred_rate 0.97 vs true_rate 0.38), not strong ranking.
    MARBERT is the only model with consistently-above-chance AUC (0.56-0.79) -- real but
    modest learning, clearest on very_easy (AUC=0.79) despite having the worst real F1 there.
  - `section5_signal.py`: TF-IDF top features, top-15 TP/FN verses by MARBERT probability,
    an explicit-marker check (كأن/مثل/كما/شبه) for تشبيه مطول, corpus-wide target
    co-occurrence, and a label-noise indicator (exact span_text with >1 distinct subtype).
    **Key finding: only 18.4%% of تشبيه مطول's 217 positive verses contain any of the checked
    markers** (vs 4.2%% corpus baseline -- real enrichment, but a small minority); several
    high-confidence false negatives DO contain كأن/كما yet are still missed, and multiple TP/
    FN span_texts visibly cross the verse boundary the classifier cannot see (one verse of a
    2-verse بيت at MAX_LEN=32, single-verse framing) -- consistent with تشبيه مطول's own
    name ("extended simile") being a multi-verse structural device the task's verse-level
    framing partially truncates. 6.56%% of all unique span_texts carry >1 distinct subtype
    somewhere in the corpus (real, non-trivial annotation-inconsistency rate, not isolated
    to these 2 targets).
  - `section6_distribution_shift.py`: train/test poet overlap per split/seed (76-88%% of test
    poems have their poet also in train -- not a severe unseen-poet problem), per-target
    positive-verse concentration (top-5 poets hold 34-48%% of each target's positives --
    moderate, not extreme, concentration for all 5 targets alike), and per-poet/per-period F1
    on S2 test (MARBERT, pooled 3 seeds) -- high poet-to-poet and period-to-period variance
    but no single poet/period that fully explains either easy target's weak aggregate F1.
  - `section4_learning_curve.py`: **new local-only training runs** (no API calls) -- a real
    learning-curve experiment, not just the existing 5-point cross-target correlation.
    MARBERT only (won 4/5 S2 targets), targets = easy (استعارة تمثيلية) + medium
    (استعارة فعل), S2 val/test held fixed per seed, TRAIN subsampled to nested
    10/25/50/100%% prefixes (seeded per-seed shuffle, so 10%% subset of 25%% subset of 50%%
    subset of 100%% for the same seed), 3 seeds x 4 fractions x 2 targets = 24 new training
    runs, ~16-30s each on the RTX 3060 Ti (smoke-tested first: 1 run in ~9s incl. model load).
    Does NOT edit `train.py` -- duplicates its training loop in the analysis script, importing
    its `VerseDataset`/`predict_probs`/`set_seed` helpers unchanged. No weights saved to disk
    (same as the main Phase 5 grid). Results land in
    `results/phase5_local_ft/analysis/raw_lc/*.json` (separate from the main grid's `raw/`).
    Fits both a power-law (log-log least squares) and a saturating curve
    (`c*(1-exp(-x/tau))`, nonlinear least squares) to F1/AUC vs. positive-training-verse count,
    both within-target (many points from the 4 fractions x 3 seeds) and across the 5 targets
    at full data (extending Phase 5's existing 5-point Pearson r=0.996 with an actual fit +
    R^2, not just a correlation coefficient on 5 points) -- run in background, continuing to
    section 7 synthesis once it completes.
- **Section 4 finished** (24/24 runs, ~5 min total). **Key result, resolves the central
  confound**: within-target learning curves are nearly FLAT (easy: F1 0.164->0.180->0.180->
  0.192 and medium: F1 0.544->0.541->0.542->0.554, across 10%%->25%%->50%%->100%% of train data)
  -- medium's F1 is already at its ceiling with only ~90 positive training verses; a 10x
  increase to ~900 buys almost nothing. Cross-target Pearson r(F1,train_pos)=0.945 (p=0.015,
  close to Phase 5's original 0.996) but **r(AUC,train_pos)=-0.322 (p=0.597, wrong sign, not
  significant)** -- positive-verse count predicts F1 across targets but NOT real discrimination
  (AUC) at all. Reframe: since total verses/poem is ~fixed corpus-wide, "positive count" in
  this corpus is almost the same variable as "prevalence" -- medium's real advantage is
  **imbalance severity (36%% positive), not training-set size**. Figure
  `docs/phase5/figs/section4_learning_curve.png` plots both curves + all 5 targets' full-data
  points on log-x: **very_easy's diamond sits above easy's entire learning-curve line with
  FEWER positives (151 vs 212)** -- best AUC (0.790) of all 5 targets, worst F1 -- directly
  visualizing the F1-vs-AUC disconnect from section 3.
- Wrote `docs/phase5/LOCAL_FT_DIAGNOSIS.md` (full English report, 8 sections per task spec,
  ranked causes: #1 class-imbalance/threshold dynamics (strongest), #2 metric-choice obscures
  real learning for very_easy specifically (AUC=0.790 best-in-grid despite worst F1), #3
  task-definition mismatch for تشبيه مطول (annotation spans cross verse boundaries,
  MAX_LEN=32 single-verse framing can't see them), #4 weak/no real learning for
  camelbert_ca/arabert_v2 on 4/5 targets (chance-or-below AUC), #5 statistical noise flattens
  part of the apparent ranking (very_easy/very_hard and easy/hard/very_hard pairwise CI
  overlap -- only medium's superiority is solid), #6 label-noise/co-occurrence/distribution-
  shift are real but spread evenly across all 5 targets, not concentrated on the 2 worst) and
  `docs/phase5/LOCAL_FT_DIAGNOSIS_AR.md` (Arabic summary, same structure/numbers, condensed).
  Did not touch the existing `docs/phase4/E1_V2_REPORT*.html` files (not modified, per task
  instruction) or any Phase 1-4 frozen file.
- Verified before committing: `git status` shows only new untracked files (6
  `experiments/phase5_local_ft/analysis/*.py` + `common.py`, `results/phase5_local_ft/
  analysis/` incl. `raw_lc/` (24 small JSON files, metrics+predictions only, no weights),
  `docs/phase5/LOCAL_FT_DIAGNOSIS*.md`, `docs/phase5/figs/section4_learning_curve.png`) plus
  this log's own modification -- no Phase 1-4 file and no existing Phase 5 file touched. Total
  new-file size ~520KB, nothing near the project's 5MB confirmation threshold, no secrets
  (plain JSON metrics/predictions + markdown + one PNG). Committing and pushing now.

---

**2026-10-17 -- New task: Phase 6, "stronger fine-tuning" -- try to beat Phase 5 on the
same 5 targets (تشبيه مطول, استعارة تمثيلية, استعارة فعل, طباق إيجاب, كناية عن فعل)
via 3 levers (L1 context window, L2 loss/training changes, L3 bigger models), reusing
Phase 5's exact targets/labels/poem-level splits (S2 3 seeds, S3 for استعارة فعل) so
results are directly comparable. No paid API calls; public HF downloads only, no token in
code. New code in `experiments/phase6_stronger_ft/`, outputs in
`results/phase6_stronger_ft/`; Phase 1-5 code/results not edited; no
weights/checkpoints/caches in git.**
- Read `CLAUDE.md`, `PROJECT_STATE.md` (full file -- confirmed it only covers Phase 1-2 and
  is stale relative to Phase 3-5; trusted the newer `docs/phase4/`, `docs/phase5/` docs and
  the code itself over it, per CLAUDE.md's own "trust the code" rule), `docs/phase5/
  LOCAL_FT_RESULTS.md` + `LOCAL_FT_DIAGNOSIS.md` in full, this log's tail (Phase 5 build +
  diagnosis entries), every file under `experiments/phase5_local_ft/` (`phase5_config.py`,
  `data_io.py`, `dataset.py`, `splitting.py`, `train.py`, `metrics_utils.py`, `baselines.py`,
  `normalize.py`, `run_grid.py`) and skimmed `docs/phase4/E1_V2_RESULTS.md` for the exact
  استعارة فعل LLM comparison numbers already summarized in `LOCAL_FT_RESULTS.md` §8.
- **Step 0 -- environment check (read-only, nothing installed yet):**
  - GPU: NVIDIA GeForce RTX 3060 Ti, 8.59 GB VRAM, driver/CUDA stack healthy
    (`nvidia-smi` OK). **~3.0 GB already in use by other desktop/GPU processes at check time**
    (browser, IDE, overlay apps -- no other ML job running) -- effective free VRAM right now
    is closer to ~5.6 GB, not the full 8GB nominal; worth closing extra GPU-using apps before
    any long training run, and factoring into L3 model-size choices next.
  - `torch` 2.12.0.dev20260323+cu128, `torch.cuda.is_available()=True`, CUDA 12.8 -- the
    exact same already-working install Phase 5 used, confirmed again, no reinstall needed.
  - Already installed (from Phase 5): `transformers` 5.20.1, `accelerate` 1.15.0,
    `safetensors` 0.8.0, `sentencepiece` 0.2.2, `scikit-learn` 1.9.0, `numpy` 2.4.3.
  - **Missing**: `peft`, `bitsandbytes`. Neither is installed in this environment yet.
  - **Windows support check for `bitsandbytes` (done before proposing anything, per task
    instruction)**: `pip install --dry-run` resolves cleanly to `bitsandbytes-0.50.2`, whose
    PyPI classifiers explicitly list `Operating System :: Microsoft :: Windows` (alongside
    Linux/macOS) -- current bitsandbytes ships official Windows CUDA wheels (post
    multi-backend-refactor), so **4-bit QLoRA is viable on this machine as planned in L3**;
    no fp16-only fallback is needed. `peft` dry-run also resolves cleanly to `peft-0.21.2`
    with every dependency already satisfied by the existing environment (no version
    conflicts with the installed `torch`/`transformers`/`accelerate`/`safetensors`).
  - Disk: 169 GB free on `C:` -- ample room for a handful of additional model downloads
    (a 1.5-3B decoder in fp16 is ~3-6GB; a large Arabic encoder is ~1.3GB; all land in the
    existing gitignored `experiments/phase5_local_ft/hf_cache/`-style local cache, reused for
    Phase 6 under its own directory, no HF token).
  - **Exact pip commands proposed** (not yet run -- stopping here for confirmation per task
    instruction): `pip install peft bitsandbytes`. Nothing else needs installing or
    upgrading.
  - **L3 candidate preview (for the user to review alongside the install confirmation, not
    yet started)**: a ~1.5-3B decoder -- **Qwen2.5-3B** (and/or the smaller **Qwen2.5-1.5B**
    if the 3B is too slow for the 30-min/run cap) -- ungated, strong general multilingual/
    Arabic support, widely used; an Arabic-specific decoder alternative -- **inceptionai/
    jais-family-1p3b** (public, ungated, Arabic-centric pretraining) -- to test on decoders
    the same domain-pretraining question Phase 5 raised for encoders (CAMeL-BERT-CA's edge on
    very_hard); and a large Arabic encoder -- **aubmindlab/bert-large-arabertv02** (AraBERT
    large) -- the clearest public "large Arabic encoder" option (CAMeL-Lab/UBC-NLP don't
    publish large variants). All 3 fit comfortably in 8GB (QLoRA 4-bit for the decoders, fp16
    full fine-tune for the encoder) even accounting for the ~5.6GB currently-free VRAM noted
    above. Final choice (2-3 of these) to be confirmed in Step 1 alongside a per-model
    VRAM/time-per-epoch estimate before any long run, per task instruction.
  - **Stopping here, as instructed, for explicit user confirmation before installing
    `peft`/`bitsandbytes` or downloading any model.**

**User confirmed ("Yes, install & continue"). Resuming:**
- Installed `peft` 0.21.2 and `bitsandbytes` 0.50.2 cleanly, no conflicts.
- Re-checked `inceptionai/jais-family-1p3b` with an anonymous (`token=False`) download
  attempt before using it -- **GatedRepoError (401)**, so it was dropped despite `model_info`
  initially showing `gated="auto"` (auto-approval still requires authentication). Replaced in
  the L3 candidate list with `aubmindlab/aragpt2-mega` (~1.46B, Arabic-specific GPT2-style
  decoder, confirmed ungated via the same anonymous-download check) -- see Step 1 below for
  why this was later dropped too.
- Built `experiments/phase6_stronger_ft/`: `phase6_config.py` (imports Phase 5's `phase5_config`/
  `data_io`/`dataset`/`splitting`/`metrics_utils`/`baselines`/`normalize` unchanged, same
  reuse convention CLAUDE.md already uses for Phase 2 importing Phase 1), `context_dataset.py`
  (L1: builds `[PREV]`/`[VERSE]`/`[NEXT]`-tagged examples), `losses.py` (L2: focal loss),
  `llrd.py` (L2: layer-wise LR decay param groups), `train_encoder.py` (generalized Phase 5
  trainer parameterized over L1 context / L2 loss-type / L2 schedule, reproduces Phase 5's
  exact recipe when all three are at their defaults -- smoke-tested against Phase5/marbert/
  medium/seed0 and got a consistent F1), `train_decoder.py` (QLoRA 4-bit decoder trainer,
  native `*ForSequenceClassification` classes only -- never `trust_remote_code`), `losses`/
  `llrd`/`analysis_common.py`/`runners.py`/`select_best_configs.py`/`run_l1l2_ablation.py`/
  `run_l3_bigger_models.py`/`run_final_grid.py`/`evaluate.py`/`ensemble.py`/`plot_figures.py`.
  Added matching `.gitignore` rules for `experiments/phase6_stronger_ft/hf_cache/` and
  `results/phase6_stronger_ft/checkpoints|*.pt|*.bin|*.safetensors` (same pattern as Phase 5).
- **Import-order bug found while smoke-testing**: `transformers`/`huggingface_hub` resolve
  their cache-directory constant the first time either is imported, so a couple of direct
  `python train_*.py` invocations (which import `transformers` before `phase6_config` sets
  `HF_HOME`) ended up caching Qwen2.5-3B/aragpt2-mega/AraBERT-large in the user's shared
  default `~/.cache/huggingface` instead of the phase-local folder. Documented in
  `phase6_config.py` and `docs/phase6/STRONGER_FT_RESULTS.md` rather than fixed mid-stream
  (fixing it would have meant re-downloading several already-fetched GB); harmless for "no
  weights/caches in git" since that cache is outside the repo either way. Scripts invoked via
  their own orchestrators (`run_l1l2_ablation.py`, `run_l3_bigger_models.py`) which import
  `phase6_config` first did cache correctly in the phase-local folder.
- **L1 token-length check** (`context_dataset.py __main__`): p99 token length for
  prev+target+next across Phase 5's 3 tokenizers was 68-69 (max 111) -- set
  `MAX_LEN_CONTEXT=96` (same ~40% margin convention Phase 5 used for its own `MAX_LEN=32`).
  ~3x Phase 5's verse-alone length -> ~3x per-epoch compute for L1 ("cost" per task instruction,
  interpreted as compute since this phase has no API $ cost).
- **aragpt2-mega smoke-tested and dropped**: its Conv1D-based layers under bitsandbytes 4-bit
  quantization ran ~4x slower per optimizer step than Qwen2.5-3B despite being under half the
  parameter count (>15 min for one epoch on the largest target vs Qwen's 243s) -- would have
  made a 5-target grid infeasible in this session's time budget. Also needed a manual patch
  (`train_decoder._patch_aragpt2_final_norm`, found via the LOAD REPORT showing
  `transformer.ln_f.{weight,bias}` as MISSING and `emb_norm.{weight,bias}` as UNEXPECTED): its
  final layer norm lives under a differently-named checkpoint key that only its own custom
  modeling code wires up. The patch copies those two tensors directly from the already-
  downloaded safetensors file (no `trust_remote_code`, just a tensor copy) and does work, but
  the model was dropped from the actual grid anyway for the speed reason above. Final L3
  candidates: **Qwen/Qwen2.5-3B** (QLoRA 4-bit, LoRA r=16 on q/k/v/o/gate/up/down_proj,
  classification head full precision) and **aubmindlab/bert-large-arabertv02** (fp16 full
  fine-tune).
- **Step 1, L1+L2 ablation** (`run_l1l2_ablation.py`, seed0 only, Phase 5's best model per
  target, one lever changed at a time against the Phase 5 baseline cell which was reused
  as-is rather than retrained): 15 cells (5 targets x 3 new cells), 12.1 minutes total, 0
  errors. Selection criterion: VAL F1 (never test). Full table in
  `docs/phase6/STRONGER_FT_RESULTS.md` section 2.
- **Step 1, L3 sweep** (`run_l3_bigger_models.py`, seed0, both candidates x 5 targets, reduced
  1200s/20min per-run cap instead of the full 30min -- an explicit, documented time-budget
  decision since Qwen2.5-3B's ~243s/epoch made the full cap impractical for a 10-cell
  exploratory sweep): **hit one transient CUDA error** (`RuntimeError: CUDA error:
  CUBLAS_STATUS_EXECUTION_FAILED`) on `easy/arabert_large`'s 6th epoch -- confirmed via a
  fresh `torch` matmul sanity check immediately after that CUDA/cuBLAS were healthy again (not
  a persistent hardware/driver problem, no OOM, GPU memory was back to idle). Added retry/
  resilience logic to `run_l3_bigger_models.py` (each cell gets up to 2 attempts, failures are
  collected and reported rather than killing the whole sweep) and to `run_final_grid.py` (same
  pattern), then resumed the sweep -- it correctly skipped the 3 already-complete cells and
  continued from `easy/arabert_large`, which succeeded on the retry. Final: 10/10 cells
  complete, 0 failed cells, 87.9 minutes total. Neither L3 candidate beat the corresponding
  Phase 5 base-encoder cell on VAL F1 for 4 of 5 targets; only very_hard (`arabert_large`)
  won at seed0. Full table in `docs/phase6/STRONGER_FT_RESULTS.md` section 3.
- **Config selection** (`select_best_configs.py`): top-2 per target by seed0 VAL F1 across all
  of L1/L2/L3 + the Phase 5 baseline. **No L3 (bigger-model) candidate made the top-2 for 4 of
  5 targets** -- base Phase 5 encoders (marbert/camelbert_ca), untouched or with one L1/L2
  tweak, out-VAL'd both Qwen2.5-3B and AraBERT-large everywhere except very_hard.
- **Final grid promotion** (`run_final_grid.py`): selected configs run to 3 seeds on S2 (seed0
  reused where already computed, Phase-5-baseline cells reused directly from Phase 5's own raw
  files with zero retraining) + 3 seeds on S3 for medium's 2 configs. 23.1 minutes, 0 errors
  (the added resilience logic wasn't needed this time -- no further CUDA faults).
- **Step 2 evaluation** (`evaluate.py`): verse-level F1 (val-tuned threshold) mean±std over 3
  seeds, AUC-ROC, average precision, bootstrap 95% CI over poems (same method as Phase 5's
  `analyze.py`). **Bug caught and fixed before trusting the output**: `build_table()` was
  double-counting the Phase 5 baseline row whenever it was also one of the selected top-2
  configs (it always appended a baseline row unconditionally, then appended it again from the
  `selected` loop) -- fixed to check first. **Headline finding: once bootstrap CIs are
  accounted for, no Phase 6 configuration beats the untouched Phase 5 baseline outside noise,
  on any of the 5 targets** -- every Phase 6 cell's CI overlaps the Phase 5 baseline's CI. The
  two most promising point-estimate wins (focal loss on very_easy, +0.068 F1; context window
  on hard, +0.072 F1, tightest std in the whole grid at 0.007) are both directionally
  consistent across all 3 seeds individually but neither clears the 95%-CI bar. very_hard's
  seed0-flagged `L1_context` cell (§2's VAL/TEST mismatch warning) is **confirmed as noise** at
  3 seeds -- its mean F1 (0.152±0.050) stays far below the baseline's (0.217±0.020). On
  استعارة فعل (medium, S3, fixed 25-poem LLM-comparison pool): Phase 6's best config
  (L2b_cosine_llrd, 0.573±0.006) ties Phase 5's already-LLM-matching result (0.570±0.005) and
  the best single LLM (0.576) -- three different "stronger" attempts (focal, cosine+LLRD,
  Qwen2.5-3B, AraBERT-large) all converge on the same ceiling rather than breaking through it,
  reinforcing Phase 5's class-prevalence-governs-this-target finding.
- **Step 3 ensemble** (`ensemble.py`): cheap probability-average ensemble of each target's
  selected top-2, threshold tuned on the averaged VAL probabilities. Only possible for
  medium and very_hard (Phase 5's baseline cell predates the `val_predictions` field this
  phase added to `train_encoder.py`/`train_decoder.py`'s output schema, so targets where
  baseline was one of the top-2 -- very_easy/easy/hard -- are reported standalone instead of
  silently dropped). **The ensemble helped nowhere it could be computed**: medium's ensemble
  (0.546) is worse than either individual member (0.556/0.558); very_hard's (0.169) sits
  between its two members but still well below the untouched baseline (0.217) -- same
  conclusion as Phase 1's LLM-ensemble check (§3e, `PROJECT_STATE.md`): averaging correlated-
  error models from the same base/recipe family buys nothing.
- Wrote `docs/phase6/STRONGER_FT_RESULTS.md` (full English report: environment, L1 token-
  length/cost, L1+L2 ablation table + which-lever-helped-what, L3 sweep table + VRAM/time,
  selected configs, Step 2 evaluation table + CI-overlap analysis, S3-vs-LLM table, Step 3
  ensemble, "do the bigger models fit/train acceptably" answer, plain answer) and
  `docs/phase6/STRONGER_FT_SUMMARY_AR.md` (Arabic summary, same headline findings condensed).
  Figure: `docs/phase6/figs/phase6_f1_comparison.png` (per-target F1 bars, Phase 5 baseline vs
  selected Phase 6 configs vs ensemble where available, consistent per-label coloring).
- Verified before committing: no weights/checkpoints/HF caches tracked (`.gitignore` rules for
  `experiments/phase6_stronger_ft/hf_cache/` and `results/phase6_stronger_ft/checkpoints|*.pt|
  *.bin|*.safetensors` added at the start of this session, confirmed still correct); no Phase
  1-5 file edited; `results/phase6_stronger_ft/raw/*.json` holds metrics + per-verse
  predictions only (same discipline as Phase 5). Total new code+docs+results committed next.

---

**2026-10-22 -- New task: supervisor-requested multi-poet few-shot experiment on E1 v2's
استعارة فعل subtype prompt -- F5 (5 examples, 5 different poets) vs F10 (10 examples, 10
different poets, F5 ⊆ F10) vs the existing 2-example sets A/B/C/D, each on its own 50-poem
pool. No API calls yet (Step 1/2 only); additive-only, same convention as Set D/D2.**
- Read `CLAUDE.md`, `docs/phase4/E1_V2_RESULTS.md`, this log's tail, every file under
  `experiments/phase4_e1_v2/` (`e1v2_config.py`, `prompt_builder.py`, `runner.py`,
  `providers_v2.py`, `parsing_v2.py`, `gt_v2.py`, `scoring_v2.py`, `dryrun_v2.py`,
  `unit_checks.py`, `analyze_v2.py`, `ensemble_v2.py`, `verse_analysis.py`,
  `preview_and_diff_D.py`, `dryrun_D.py`, `analyze_D.py`), `experiments/phase4_e1/`
  (`e1_config.py`, `ali_poems_io.py`, `fewshot_examples.py`, `build_pool.py`),
  `experiments/phase3_subelements/` (`subtype_defs.py`, `subtype_prompts.py`,
  `fewshot_prompts.py`, `providers_fixed.py`), `experiments/phase4_e1/config/eval_pool.json`
  + `example_sets.json`, and `data/ali_poems/manifest.csv`. Backed up
  `docs/phase4/E1_V2_REPORT.html` -> `docs/phase4/E1_V2_REPORT_before_multipoet.html` first,
  per task instruction (same convention as the existing `_before_ensemble`/`_before_opus`
  backups already in that directory). Did not edit v1 (`phase4_e1/`), `phase3_subelements/`,
  `pilot_3models/`, phase5/6, `CLAUDE.md`, or any existing results/manifest record -- only new
  files added under `experiments/phase4_e1_v2/` and `experiments/phase4_e1_v2/config/`.
- **Step 1 (no API calls) -- new files, all additive:**
  - `multipoet_config.py`: constants (F5_N=5, F10_N=10, F5B_N=5, example-draw
    seed=42 [a SEPARATE random.seed() call from v1's own EXAMPLE_SEED=42 stream, not shared
    state], pool-continuation seed=43 matching `e1_config.POOL_SEED` exactly, the Abu-Nuwas-
    specific exclusion set `OLD_EVAL_POOL_ABU_NUWAS_IDS`).
  - `multipoet_examples.py`: finds **47 eligible poets** (>=1 poem with an exact-subtype
    استعارة فعل annotation carrying a non-empty `analysis` note, after the standard
    NO_TEXT/ALREADY_USED/old-EXAMPLE_POEM_IDS exclusions, plus -- only for أبو نواس -- excluding
    the original eval_pool.json's own 10 Abu Nuwas poems) spanning 8 periods (العصر الجاهلي=7,
    مخضرم=5, مخضرم الدولتين=2, العصر الأموي=16, العصر العباسي=12, الخلفاء الراشدون=1,
    العصر المملوكي=1, blank/unknown=3). Poet-selection order is a DETERMINISTIC
    period-diversity round robin (not randomized) -- periods visited in a fixed chronological-
    ish order, poets within a period ordered by poet_id -- so F5 = first 5 of this order, F10 =
    first 10 (F5 is a strict prefix of F10 by construction), optional F5b = next 5. Only the
    PER-POET VERSE draw is randomized: one `random.seed(42)` call, then one
    `random.sample(eligible_verses_for_poet, 1)` per poet IN SELECTION ORDER -- verified this
    makes F5's 5 draws byte-identical whether or not F10/F5b are ever built (sequential RNG
    consumption, never reseeded mid-draw). Abu Nuwas was NOT selected into F5/F10/F5b by this
    round robin (other poets filled the العصر العباسي period slots first by poet_id order), so
    the Abu-Nuwas-specific eval-pool exclusion never actually had to fire for this draw --
    noted as such, not hidden.
    **Selected poets/periods/poems/verses printed in full** (also written to
    `config/multipoet_example_sets.json`): F5 = الأعشى ميمون (جاهلي, poem 6574 v6) / أبو ذؤيب
    الهذلي (مخضرم, poem 5661 v6) / بشار بن برد (مخضرم الدولتين, poem 27110 v45) / الفرزدق
    (أموي, poem 7891 v2) / أبو تمّام (عباسي, poem 4480 v62). F10 adds: زياد بن حنظلة (راشدون,
    poem 34779 v2) / عفيف الدين التلمساني (مملوكي, poem 29516 v12) / مُليح بن الحكم (period
    blank, poem 7408 v42) / النابغة الذبياني (جاهلي, poem 3331 v2) / ربيعة بن مقروم (مخضرم,
    poem 2187 v5). F5b (not run, costed only) adds: أبو دلامة / عمر بن أبي ربيعة / المتنبي /
    الحمدوي / طرفة بن العبد. Every example verse, its GT span(s), and Dr. Hussein's analysis
    note were printed and independently re-verified against the poem JSON (not just trusted
    from the draw) in Step 1's unit checks -- all passed.
  - `multipoet_prompt_builder.py`: generalizes `prompt_builder.py`'s 2-example fewshot
    scaffold to N examples (Example 1 = unchanged definition example, Example 2..N+1 = the
    multipoet draw), reusing `prompt_builder._format_example_verse` unchanged for per-example
    note formatting -- same "Example i (from the annotated corpus - verse: ...): ..." line
    format as A/B/C, just more of them. Does NOT edit `prompt_builder.py`,
    `fewshot_prompts.py`, or `subtype_prompts.py`.
  - `multipoet_pool.py`: new 50-poem pool = v1's existing `eval_pool.json` 50 poems MINUS the
    poems used as F5/F10 example sources, replaced by "the next poems from the same seed-43
    stratified draw" -- **method verified empirically first** (not assumed): CPython's
    `random.sample(pop, k)` under a fixed seed has the property that `sample(pop, k)[:j] ==
    sample(pop, j)` for any `j <= k` on the same population/order, so asking for MORE items
    from the same seeded draw deterministically reproduces the original prefix and extends it.
    Implemented as two independently-reseeded strata draws (abu_nuwas stratum: fresh
    `seed(43)` then `sample(abu_nuwas_candidates, len(...))`; other stratum: `seed(43)`, replay
    the original `sample(abu_nuwas_candidates, 10)` call to reach the identical RNG state v1's
    code would have had, THEN `sample(other_candidates, len(...))`) -- **verified this
    continuation reproduces eval_pool.json's exact original 50 poems as the prefix before
    using it for any replacement.** Default (F5+F10 only) run: 3 poems removed (5661, 29516,
    34779 -- all tag "other"), replaced by [23986, 27929, 28093] (also "other", preserving
    10 abu_nuwas + 40 other exactly). Final pool: 50 poems, 1000 verse-units, 421
    استعارة فعل GT instances, 47/50 overlap with the original eval_pool.json, **9/25 overlap
    with eval_pool_25.json** (the pool Z/A/B/C/D/D2 actually ran on -- the number requested for
    comparison). Saved to `config/eval_pool_50_multipoet.json`. (If F5b were ever run, 2 more
    poems -- 4554, 28095 -- would also need removing/replacing, giving a 991-verse pool
    slightly different from the F5/F10 pool -- computed and reported for costing purposes only,
    NOT written over the canonical F5/F10 pool file.)
  - `unit_checks_multipoet.py`: all 5 checks passed -- (1) A/B/C/Z prompt previews regenerate
    byte-identical to the already-committed `config/prompt_preview_{Z,A,B,C}.txt` (proves
    adding F5/F10 touched nothing existing); (2) zero overlap between the new 50-poem pool and
    the 10 example-source poems; (3) F5's poets ⊆ F10's poets, F10 has exactly 10 distinct
    poets, one poet per example; (4) every drawn example verse independently reconfirmed (fresh
    `gt_v2.gt_spans_for_subtype` call, not reusing the draw step's own computation) to carry a
    real استعارة فعل GT span; (5) wrote `config/prompt_preview_F5.txt` /
    `prompt_preview_F10.txt`. Rendered F10's full system prompt and confirmed it is the same
    scaffold as A/B/C/D, just with 10 "Example i (from the annotated corpus - verse: ...): ..."
    blocks instead of 2.
- **Step 2 (no API calls) -- `dryrun_multipoet.py`:** real tiktoken `cl100k_base` input-token
  counts for the ACTUAL F5/F10 prompts x the new pool's real verses (NOT a flat $/call average
  carried over from D/D2 -- F10's prompt is much longer than A/B/C/D's 2-example scaffold, so a
  flat average would have understated it), combined with REAL average output-tokens/call per
  provider computed directly from the completed `run_manifest.json` (anthropic mean=192.3
  tok/call n=1962, openai mean=98.5 n=1962, google mean=81.8 n=1962 -- confirms output length
  stays ~input-length-independent, the same assumption `dryrun_v2.py` made for the original
  Z/A/B/C estimate, now checked against real multi-set data instead of just Phase 3's number).
  Gemini still priced under all 3 scenarios from `dryrun_v2.py` (config.py legacy / 3.6-flash
  ESTIMATE_LOW / ESTIMATE_HIGH) given the still-unresolved served-vs-requested model-id
  ambiguity documented there.
  **Costs (3 models x 1000 verse-units x 1 run each, worst-case Gemini pricing):**
  F5 = **$12.40** (1,586,971 input tokens), F10 = **$17.58** (2,573,971 input tokens). Optional
  Z add-on (dry-run only, not yet run) -- Z on the 41 of the new pool's 50 poems NOT already
  covered by the existing Z run on `eval_pool_25.json` (9 already are), 906 verse-units -- =
  **$6.45**. **Required subtotal (F5 + F10 + Z add-on): $36.43.** Optional F5b add-on (its own
  slightly different 991-verse pool, computed standalone, not written over the canonical
  F5/F10 pool file) = **+$11.82**, bringing the all-in grand total to **~$48.25** if every
  optional piece is run. All figures are the worst-case across the 3 Gemini pricing scenarios;
  the config.py legacy rate happens to coincide with the worst case here (both ≈$3.12/$4.60/
  $1.46 for F5/F10/Z-addon respectively), noted explicitly rather than silently picking
  whichever scenario looked smaller.
- **STOPPING HERE per task instruction and CLAUDE.md rule 5** -- no API call has been made.
  Presenting the cost breakdown and awaiting the user's explicit "go" + a hard
  `--max-additional-usd` cap before running `runner.py --confirm` for Step 3. Committing and
  pushing this session's Step 1/2 code + config (new files only, no existing file content
  changed) now, per the task's explicit instruction to commit/push before the stop.

**User confirmed: F5 + F10 only (not the Z add-on, not F5b), hard cap $40.**

- **Step 3 (API calls).** Wrote `run_multipoet.py` -- a standalone runner (not a modification
  of `runner.py`) because F5/F10 need `multipoet_prompt_builder.build_system_message_n`
  (variable-N examples) and the new `eval_pool_50_multipoet.json` pool instead of
  `runner.py`'s fixed Z/A/B/C/D/D2 call shape; reuses `runner.py`'s manifest/cost/
  resumability/hard-cap/quota-stop machinery (`spend_so_far`, `call_cost`, `cell_key`,
  `is_quota_error`, `_save`, `_print_summary`) unchanged, writing into the SAME
  `results/phase4_e1_v2/run_manifest.json` Z/A/B/C/D/D2 already use (new set_name values
  F5/F10 never collide with an existing cell_key, purely additive). Dry-run first confirmed
  the plan (6000 calls, 0 already done) before `--confirm`.
  - First invocation (`--confirm --max-additional-usd 40`, backgrounded): ran for ~3.5 hours,
    reached 5554/6000 cells, then **stopped itself** on the runner's existing
    5-consecutive-error rule -- **Anthropic's API credit balance ran dry** ("Your credit
    balance is too low to access the Anthropic API"), concentrated in the pool's two largest
    poems (33381, 33473, both near the end of poem-id sort order) processed last. 120 calls
    errored + 326 never attempted, 0 silent gaps (every one accounted for in the manifest or
    the plan). Spend before the stop: $25.25 on F5/F10 (anthropic $16.73, openai $2.91,
    google $5.61) -- under the $29.97 estimate, nowhere near the $40 cap; the stop was a
    billing issue, not a cost-cap or code issue. Same precedent already on record in this
    project (`PROJECT_STATE.md` §3g's Nabigha per-verse retry).
  - User topped up Anthropic credits and confirmed resume. Second invocation
    (`--confirm --max-additional-usd 5`, backgrounded): completed in ~10 min, 0 new errors.
    **Full coverage verified programmatically** (expected 6000 cells == present-and-ok 6000
    cells, 0 missing, 0 erroring) before proceeding. **Final real cost: $28.0272** (anthropic
    $18.94, openai $3.10, google $5.99) -- under the $29.97 pre-run estimate despite the
    detour.
- **Step 4 (analysis, no API calls).** `analyze_multipoet.py`: first attempt called
  `scoring_v2.score_set` directly (re-reads/re-parses the ENTIRE `run_manifest.json` from
  disk on every single verse lookup) against the now-12k+-record manifest thousands of
  times -- hit the 120s foreground timeout. **Fixed by switching to `ensemble_v2`'s
  cache-based `score_set_single_model`** (build one parsed cache up front, same fix
  `ensemble_v2.py`'s own docstring already documents for its own need) -- completed in
  well under 2 minutes afterward, verified to produce byte-identical F1 values to the slow
  path via the existing `verify_single_model_cache_scorer` check already in `ensemble_v2.py`.
  **A second, more consequential bug was then caught before writing anything up**:
  `scoring_v2.bootstrap_ci_pairwise`'s own `point` field is computed from `score_total()`,
  which sums over EVERY poem in each input `per_poem` dict -- correct for every prior use of
  that function (Z/A/B/C/D/D2 always share the SAME 25-poem pool), but wrong for an
  F5/F10 (50-poem pool) vs. Z/A/B/C/D (25-poem pool) comparison, where `point` would
  silently mix in poems outside the 9-poem overlap the CI's own bootstrap resampling is
  actually restricted to (confirmed by inspecting the first-printed numbers: several `point`
  values fell OUTSIDE their own stated CI95 bounds, which is only possible if `point` and
  the CI are drawn from different populations). Fixed in `analyze_multipoet.py` by
  overriding `point` with the same overlap-restricted F1 difference the resampling actually
  draws from -- the CI *bounds* themselves were always correct (the function's resampling
  already intersects `set(per_poem_a) & set(per_poem_b))`, so every earlier SIG/ns
  significance call stands; only the point estimates needed correcting, and were corrected
  before any number reached `E1_V2_MULTIPOET.md` or the HTML report.
  - **Primary (F5 vs F10, full 1000-verse pool)**: 8 of 9 model&times;criterion comparisons
    are `ns`; the one exception is Claude on the primary verse metric, where F10
    significantly beats F5 (+0.027 F1). Going from 5 to 10 different-poet examples is
    mostly indistinguishable from noise.
  - **Secondary (vs. Z/A/B/C/D, 9-poem overlap, flagged thin and 56% Abu-Nuwas-skewed)**:
    Claude and Gemini both get a real lift from F5/F10 over Z (same pattern as every prior
    Z-vs-fewshot finding in this project) and land roughly level with or above A/B/D;
    **GPT is significantly WORSE under F5/F10 than under A/B/D** -- sharper version of GPT's
    already-known "fewshot doesn't help, sometimes hurts" pattern (Set C finding,
    `E1_V2_RESULTS.md`).
  - **Ensemble**: same conclusion as every prior ensemble check in this project (Phase 1
    §3e, `E1_V2_ENSEMBLE.md`) -- majority vote never beats the best single model, does beat
    the average of the 3 singles.
- **Step 5 (write-up + report, no API calls).** Wrote `docs/phase4/E1_V2_MULTIPOET.md` (full
  design/tables/plain-answer/caveats). Updated `docs/phase4/E1_V2_REPORT.html` via
  `scripts/build_e1v2_report.py` -- added a new function `build_multipoet_section()` (panel
  "k", metric toggle, poet+period example cards, different-pool warning banner, full
  `E1_V2_MULTIPOET.md` embedded via the existing `md_block` helper) and a small, separate
  `build_multipoet_prompt_block()` (reads `multipoet_prompt_previews`, not the existing
  `prompt_previews` dict, so nothing keyed off the latter needed touching).
  **Two real bugs in the EXISTING script were found and fixed before this ran cleanly**,
  both caused by F5/F10 sharing the same `run_manifest.json` Z/A/B/C/D/D2 already use: (1)
  the manifest-scanning loop that builds `spend`/`calls_per_set` would `KeyError` on an
  "F5"/"F10" record (`calls_per_set` is keyed only by `SET_NAMES_FULL`) -- guarded with an
  explicit `if s not in SET_NAMES_FULL and p != "anthropic_opus": continue`; (2) without that
  guard, `spend[p]` would have silently absorbed F5/F10's $28.03 into the existing Z/A/B/C/D/
  D2 cost totals the whole rest of the report relies on, and the header's `{len(manifest)}
  calls` badge would have jumped to include F5/F10's 6000 calls -- fixed by introducing a
  separate `scoped_manifest_count` for the badge. **Verified via `diff` against the
  `E1_V2_REPORT_before_multipoet.html` backup that every existing section (a-j) is
  byte-identical before/after** except the generation date, the new badge, the provenance
  file list, and the entirely new panel k -- confirms the fix didn't perturb anything
  existing. Visually rendered the output in-browser (mandatory per `CLAUDE.md`'s RTL rule):
  confirmed Arabic verse text/poet names/notes render RTL correctly in the new example
  cards, the metric toggle (verse/strict/token) correctly switches the new F5/F10 table, and
  the embedded markdown (wide comparison tables, bold/bullets, the plain-answer section) all
  render correctly via the existing `md_block` helper. One cosmetic fix made to
  `E1_V2_MULTIPOET.md` itself before the final render: two single-asterisk `*italic*` spans
  (not supported by `md_block`, which only handles `**bold**`/`` `code` ``) were showing as
  literal asterisks in the rendered HTML -- changed to `**bold**` to match the rest of the
  doc's style, then the report was regenerated once more.
- Committed and pushed Steps 3-5 (`run_multipoet.py`, `analyze_multipoet.py`,
  `E1_V2_MULTIPOET.md`, `results/phase4_e1_v2/analysis_report_multipoet.json`, 6000 new
  `results/phase4_e1_v2/raw/F5_*`/`F10_*` response files, the updated `run_manifest.json`
  (additive only -- verified every pre-existing Z/A/B/C/D/D2/anthropic_opus record
  untouched), and the updated `build_e1v2_report.py` + `E1_V2_REPORT.html`) -- commit
  `4bee6b9`. No Phase 1-4-frozen file, `phase3_subelements/`, `pilot_3models/`, or
  pre-existing results/manifest record was edited anywhere in this task; everything was
  additive, per the task's explicit scope instruction.

**Final summary (short, per task's requested closing format)**: cost **$28.0272** (F5+F10
only, under the $29.97 estimate despite a mid-run Anthropic billing interruption); pool
composition 50 poems / 1000 verse-units / 10 abu_nuwas + 40 other (3 poems swapped out for
example sources, replaced via a verified seed-43 draw continuation); verse-level F1 for
F5/F10 next to the 2-example sets is in `E1_V2_MULTIPOET.md` §2-3 and the HTML report's new
panel k; CI verdicts: F10 beats F5 significantly only for Claude on the primary verse metric
(8 of 9 model&times;criterion checks are `ns`), and F5/F10 beat Z significantly for Claude/
Gemini but are significantly worse than A/B/D for GPT on the thin 9-poem overlap; **plain
answer: more examples from more poets mostly does not help (10 does not clearly beat 5), and
whether multi-poet examples beat the existing 2-example sets is strongly model-dependent**
(helps/neutral for Claude and Gemini, hurts GPT) -- caveats: one run, one draw of
poets/verses, no noise baseline, and the vs-baseline comparison rests on a thin,
Abu-Nuwas-skewed 9-poem overlap.

---

**2026-10-23 — Poet-era few-shot task, Part 1 (analytics) + Part 2 Steps 1-3 (no API calls
except the planned Step 4, which is gated on user "go")**

Task: for each of the 52 corpus poets, research death years; build era/timeline analytics
(docs/phase4/ERAS_ANALYTICS.md/.html); build six NEW 2-example fewshot sets (M1/M2/E1/E2/H1/H2)
selecting example poets by where they fall on the death-year axis (middle band / earliest+latest
extremes / middle of each half); cost the planned run; STOP for explicit "go" + hard cap before
any API call. Scope discipline followed: only ADDED files; v1, phase3_subelements, pilot_3models,
phase5/6, CLAUDE.md, and existing results/manifest records were not touched. Backed up
`docs/phase4/E1_V2_REPORT.html` to `docs/phase4/E1_V2_REPORT_before_eras.html` before any change
(copy only, no edits made to E1_V2_REPORT.html yet -- that happens in Step 6, after the run).

**Step 1 (death years, no API calls).** Delegated the 52-poet WebSearch/WebFetch research to a
background subagent (fork) to keep the lookups out of the main session's context. Wrote
`data/ali_poems/poet_dates.csv` (poet_id, poet_name, site_period, death_year_ce, death_year_ah,
approximate, confidence, source_url, note). Result: 36/52 poets have a death year (14 high
confidence, 10 medium, 12 low); 16 are blank -- 2 are non-individuals (`القرآن الكريم` = Qur'anic
text; `مجهول (شعراء عباسيون منسيون)` = anonymous collective attribution, poem 28601, the corpus's
only no-text poem) and 14 are genuinely obscure poets with no death year found in any search
(ربيعة بن مقروم, ابن قيس الرُّقيّات, مُليح بن الحكم, المُرقِّشُ الأَصغر, السموأل بن عادياء,
تأبّطَ شَرًّا, النجاشي الحارثي, يزيد بن مفرغ الحميري, أيمن بن خريم, الحمدوي, عبيد بن الأخطل,
عبد الله بن عبد الحميد اللاحقي, المُرَقِّشُ الأكبر, زياد بن حنظلة). Several dates were flagged as
disputed/approximate rather than silently picked (عمر بن أبي ربيعة 712/719 split; الخنساء
645/646 vs. "after 630"; عبد الله بن عمر العرجي and محمد بن يسير الرياشي only a range known,
midpoint recorded; عفيف الدين التلمساني's 690 AH confirmed against an initially-checked but
unsupported 688 AH). Full table printed for review in-session; every row carries a `source_url`
and a `note` with the sourcing/disagreement detail.

**Step 2 (analytics, no API calls).** `experiments/phase4_e1_v2/eras_analytics.py`: joins
poet_dates.csv against `data/ali_poems/manifest.csv` + `data/ali_poems/poems/*.json`
(verse/poem counts and استعارة فعل positive-verse counts per poet, poem 28601 excluded from
verse counts per the task's explicit instruction -- it has verse_count=0 anyway, no text).
Declared definitions (see the script's own docstring + `experiments/phase4_e1_v2/eras_config.py`):
PRIMARY = verse-weighted median (784.0 CE) -- chosen over poems-weighted (814.0) or plain
per-poet (730.5) because every other metric in this project is verse-primary (CLAUDE.md rule 4,
the 2026-10-14 verse-primary decision); midpoint of the axis = (min+max)/2 = 917.5 CE (range
544-1291), a distinct concept from the median (axis range vs. distribution center); middle band
= median ± 75 years; first half/second half split at the median; extremes = earliest/latest 15%
of dated poets by rank (ties at the boundary year all included). Output:
`experiments/phase4_e1_v2/config/eras_axis.json` (bins, cumulative curve, per-poet table, band
membership) plus `docs/phase4/ERAS_ANALYTICS.md` and the interactive single-file
`docs/phase4/ERAS_ANALYTICS.html` (inline CSS/JS/SVG, no external deps, RTL-aware via
`pilot_3models.rtl_utils.is_majority_arabic`, collapsible `<details>` sections, light/dark via
`data-theme` + a toggle button), both built by `scripts/build_eras_report.py` (no hand-typed
numbers -- verified by rendering it in the built-in browser and reading back its text).
One bug caught before shipping: the 100-year bins were being sorted as strings (`"1200-1299"`
sorting before `"500-599"`), not numerically -- fixed in `eras_analytics.py` and both outputs
regenerated.

**Step 2 (Part 2's eligibility + note-quality filter, no API calls).**
`experiments/phase4_e1_v2/eras_config.py`'s `note_quality()`: a verse's analysis note is excluded
if it contains a question mark (؟/?, marks the annotator's own uncertainty), or if (absent any
of a diacritic-insensitive set of metaphor-reasoning keyword stems -- ستعار/مجاز/كناية/شبه/
تشبيه/تشابه/كأن) it has <=3 whitespace tokens or matches a leading "word(s): definition"
colon-gloss pattern (a bare dictionary definition, not an analysis connecting source and target
of the metaphor). Calibrated against the full 858-note candidate pool before use (printed sample
exclusions/inclusions in-session for review): question_mark removes 203, colon_gloss removes 66,
too_short removes 68 (337 total removed); keyword keeps 418, default_keep (longer, no keyword,
not colon-shaped -- treated as a genuine interpretive paraphrase even without explicit
terminology) keeps 103 (521 total kept, before the eras-specific poem exclusions below reduce
the candidate pool further).

**Step 2 (example selection, no API calls).** `experiments/phase4_e1_v2/eras_examples.py`.
Eligibility: a poem is a candidate source iff not NO_TEXT_POEM_ID / ALREADY_USED_POEM_IDS (5
Phase-1-frozen) / EXAMPLE_POEM_IDS (3 Abu-Nuwas v1 example poems) / the 10 F5/F10 example-source
poems / any of eval_pool_25.json's 25 poems (the pool M1..H2 are themselves evaluated on --
eval_pool_25.json stays byte-unchanged, verified). A poet is eligible iff not القرآن الكريم (not
an individual), has >=1 candidate verse carrying a genuine-per-`note_quality()` استعارة فعل
annotation, AND has confidence high/medium in poet_dates.csv (eras_config.SELECTION_CONFIDENCE_
LEVELS) -- "poets need a reliable death year," per the task.

**Important deviation, declared rather than silently patched**: applying Part 1's full-36-poet-
corpus year-threshold bands directly to Part 2's selection crashed (`ValueError: pool exhausted`)
-- most of the full axis's extreme-dated poets (النابغة الذبياني، الأعشى ميمون، امرؤ القيس,
among others) turned out to have ZERO usable candidate verses in this corpus (their استعارة فعل
annotations carry EMPTY analysis notes, failing eligibility before `note_quality()` even runs),
so the population actually available to draw from is only 14 poets (confidence high/medium +
eligible, out of the 36 dated), and several roles (earliest-extreme, first-half-middle) were
competing for the same 2-3 of those 14. Fix: Part 2 computes its own bands by RANK within this
14-poet selection-eligible population (not by absolute year threshold over the full corpus) --
`k_extreme = max(2, ceil(0.15 * 14)) = 3` poets from each end (earliest_extreme, latest_extreme);
`middle_band` = the `SELECTION_MIDDLE_N=4` poets whose rank is nearest the population's center
(exactly enough for M1+M2); first half/second half = an even rank split; `h1_pool`/`h2_pool` =
each half's ranks minus whatever the extreme/middle roles already claimed. For this run, the 5
resulting pools came out pairwise disjoint by construction (verified programmatically) --
middle_band (4): الكميت بن زيد الأسدي(743)/أبو دلامة(777)/أبو نواس(814)/أبو تمّام(845);
earliest_extreme (3): طرفة بن العبد(569)/قطري بن الفجاءة(698)/جميل بن معمر(701); latest_extreme
(3): الصنوبري(945)/أبو فراس الحمداني(968)/محمد بن هاشم الخالدي(996); h1_pool (2): الفرزدق(728)/
جرير بن عطيّة(728); h2_pool (2): ديك الجن(849)/ابن الرومي(896). This changes nothing about Part
1's own ERAS_ANALYTICS.md bands/extremes, which stay computed over the full 36-poet axis exactly
as specified.

Selection (fixed order M1,M2,E1,E2,H1,H2, one global used-poet set, seed=42 for the per-poet
verse draw -- `random.seed(42)` then one `random.sample(eligible_verses, 1)` per poet in
selection order, sequential, never reseeded mid-draw, same convention as
`multipoet_examples.py`): M1=(الكميت بن زيد الأسدي, أبو دلامة), M2=(أبو نواس, أبو تمّام),
E1=(طرفة بن العبد, الصنوبري), E2=(قطري بن الفجاءة المازني, أبو فراس الحمداني),
H1=(الفرزدق, جرير بن عطيّة), H2=(ديك الجن, ابن الرومي) -- 12 globally distinct poets, verified.
`experiments/phase4_e1_v2/unit_checks_eras.py`: (1) Z/A/B/C previews still byte-identical (0
regression); (2) 0 overlap between the 12 example-source poems and eval_pool_25.json's 25; (3)
exactly 2 distinct poets per set, 12 distinct overall; (4) every drawn verse independently
reconfirmed (fresh `gt_v2.gt_spans_for_subtype` call) to carry a real استعارة فعل GT span
matching its drawn annotation; (5) all six sets' rendered prompts share the byte-identical
header + Example-1 scaffold as set A (multipoet_prompt_builder.build_system_message_n with N=2,
reusing prompt_builder's own per-example formatting, unchanged) -- only Example 2/3 differ.
All checks passed. Wrote `config/prompt_preview_{M1,M2,E1,E2,H1,H2}.txt`. Full poet/death-year/
era/poem/verse/span/note detail for all 12 examples and M1's full rendered prompt (648 tokens,
cl100k_base) were printed in-session for review.

Note: one kept example note (H1's الفرزدق poem 3197 v2, span "دائي، والشفاء") reads as a
general discussion of the verse's rhetorical effect (hesitant vs. unhesitant speech) rather than
a tight explanation of that specific span -- it passed `note_quality()` legitimately (a
substantive, non-short, non-colon-gloss, non-question-marked paragraph) but is flagged here as a
real editorial quirk in the underlying corpus annotation, not hand-"fixed" (the ground-truth data
itself is not edited).

**Step 3 (cost dry-run, no API calls).** `experiments/phase4_e1_v2/dryrun_eras.py` -- same method
as `dryrun_multipoet.py` (real tiktoken `cl100k_base` input-token counts for the actual 6 built
prompts x eval_pool_25.json's real 327 verse-units, real average output-tokens/call per provider
from the completed `run_manifest.json`: anthropic mean=194.1 n=3962, openai mean=96.6 n=3962,
google mean=82.1 n=3962). Unlike F5/F10, these six sets run on the SAME pool (eval_pool_25.json)
Z/A/B/C/D/D2 already used, so Step 5's analysis will be a clean, non-thin comparison (no 9-poem-
overlap caveat). **Planned run: 6 sets x 327 verse-units x 3 models x 1 run = 5,886 calls.
Total estimated cost: $17.3096** (worst-case and config.py Gemini pricing coincide here) -- per
set: M1 $2.97, M2 $2.86, E1 $2.72, E2 $2.79, H1 $3.06, H2 $2.91.

**STOPPING HERE per task instruction and CLAUDE.md rule 5** -- no API call has been made.
Presenting the cost breakdown and awaiting the user's explicit "go" + a hard
`--max-additional-usd` cap before running `run_eras.py --confirm` (a standalone runner,
analogous to `run_multipoet.py`, to be used for Step 4). Committing and pushing everything so
far now, per the task's explicit instruction to commit/push before the stop.

**User confirmed: go ahead, `--max-additional-usd 25`.**

- **Step 4 (API calls).** `run_eras.py --confirm --max-additional-usd 25` (backgrounded): ran
  6 sets × 327 verse-units × 3 models = 5,886 calls. **Mid-run incident, same root cause as the
  2026-10-22 multipoet incident**: Anthropic's credit balance ran dry partway through. Unlike
  that prior incident, this run's plan order interleaves providers per verse (anthropic → openai
  → google for each verse in turn), so each anthropic failure was immediately followed by
  successful openai/google calls that reset the existing 5-consecutive-error counter — the
  self-stop rule never fired, and the run continued to completion, finishing openai/google at
  327/327 for every set while silently accumulating 167 anthropic errors spread across all 6
  sets (0 of them actually hidden — every one recorded in the manifest with its error string).
  First invocation finished with `DONE: plan exhausted`, total manifest spend $65.1626
  (anthropic $40.0243, openai $6.8359, google $12.9867, cap $73.36 — never hit the cap; the
  incomplete coverage was a credits problem, not a cost-cap problem). User was asked how to
  proceed (top up now vs. stop the process first); attempting to kill the background process on
  my own was blocked by the Auto Mode classifier (`[Interfere With Workloads]`), so the user was
  asked directly instead. **User topped up credits while the first invocation was still running**
  — its remaining anthropic calls (for poems processed after the top-up) started succeeding
  again automatically, no restart needed, confirmed by watching the log. A plain resume
  (`run_eras.py --confirm --max-additional-usd 10`, no `--force`) then picked up exactly the 167
  still-missing anthropic cells (resumability correctly skipped every already-succeeded cell) and
  completed them with 0 further errors. **Final verified coverage: 327/327 ok cells for every
  (set, provider) pair, 18/18 combinations, 0 errors** (`analyze_eras.py`'s own completeness
  assertion, run before any scoring). **Final real cost: $16.7459** (manifest total before this
  task: $48.3560; after: $65.1019) — under the $17.3096 pre-run estimate despite the detour.
- **Step 5 (scoring/analysis, no API calls).** `analyze_eras.py`: first attempt called
  `scoring_v2.score_set` directly, which rescans the ENTIRE run_manifest.json (now 18,099
  records) on every single verse lookup — hit the same slowness `analyze_multipoet.py` already
  documented hitting for the same reason. **Fixed the same way**: switched to
  `ensemble_v2`'s cache-based `score_set_single_model`/`score_set_ensemble` (both already generic
  over `set_name`, so no edits to `ensemble_v2.py` were needed to reuse them for M1..H2),
  verified byte-identical to the existing frozen `analysis_report.json`/`analysis_report_D.json`/
  `analysis_report_verse.json` F1 values first (`verify_single_model_cache_scorer`, 54/54 checked
  values matched). Computed, per model × criterion (verse primary, strict/token secondary):
  overall/abu_nuwas/other TP/FP/FN/P/R/F1 for all 6 sets; POOLED M=M1+M2/E=E1+E2/H=H1+H2
  (per-poem TP/FP/FN summed across the two constituent sets, declared explicitly as answering
  "does drawing from this band help regardless of which 2 poets," at the cost of doubling each
  poem's verse-units for that comparison only); bootstrap 95% CIs (n=2000, seed=0, per-poem
  resampling, `scoring_v2.bootstrap_ci_pairwise` reused unchanged) for within-pair noise
  (M1-M2/E1-E2/H1-H2), pooled cross-category (M-E/M-H/E-H), each set vs Z, and each set vs
  A/B/D2 (30 pairs × 3 criteria × 3 models); the 2-of-3 majority-vote ensemble for all 6 sets.
  Wrote `results/phase4_e1_v2/analysis_report_eras.json`.
  **Key findings (verse-primary)**: the era effect is model-dependent and in no case clearly
  larger than ordinary example-choice noise. Claude: pooled M and H both beat E (M−E +0.052 SIG,
  E−H −0.044 SIG), but the within-band noise (M1 vs M2 −0.069 SIG, E1 vs E2 −0.087 SIG) is
  comparable to or larger than that signal. GPT: no pooled cross-category comparison is
  significant at all — only within-pair noise (M1 vs M2 −0.068 SIG) is. Gemini: the cleanest
  case for a real effect — pooled H beats both M (−0.042 SIG) and E (−0.044 SIG) — but H1 vs H2
  itself is also significant (+0.078 SIG), tempering the read. Every set significantly beats Z
  for Claude; GPT shows the opposite (fewshot sometimes hurts, its established pattern); Gemini's
  gain over Z is concentrated in H1/H2 only. The one cross-model-consistent finding: **E1**
  (طرفة بن العبد + الصنوبري) is significantly worse than the existing A/B/D2 sets for **all three
  models** — a property of that specific poet pairing, not of "extremes" as a category (E2 does
  not show the same pattern). Ensemble lands close to the best single model in every set (above
  it in 3/6, below in 3/6), consistently above the average of the 3 singles — same pattern as
  every other ensemble check in this project.
- **Step 6 (write-up + report, no API calls).** Wrote `docs/phase4/E1_V2_ERAS_FEWSHOT.md` (full
  design/rank-based-band-fix/tables/plain-answer/caveats). Updated
  `docs/phase4/E1_V2_REPORT.html` via `scripts/build_e1v2_report.py` — added a new `eras_exists`-
  guarded loading block (same convention as `multipoet_exists`), `build_eras_f1_table`/
  `build_eras_pooled_table`/`build_eras_ci_table`/`build_eras_ensemble_table`/
  `build_eras_example_card`/`build_eras_prompt_block`/`build_eras_section` (panel "l", metric
  toggle shared with the rest of the page via the existing page-global `toggleCriterion`), a
  link to `ERAS_ANALYTICS.html`, and the full `E1_V2_ERAS_FEWSHOT.md` embedded via the existing
  `md_block` helper. No existing function or panel (a–k) was edited — confirmed by the script's
  own post-write verification (every existing F1 value string still present) and by visually
  rendering the new panel in-browser (mandatory per CLAUDE.md's RTL rule): Arabic poet
  names/verse text/notes render RTL in the new example cards, the metric toggle correctly
  switches the new F1/pooled/CI tables, SIG rows highlight correctly, and the embedded markdown
  write-up (headers, bold, tables) renders via `md_block` exactly as the multipoet section's
  already-working embed does.
- Verified additive-only: `eval_pool_25.json` has zero diff (byte-unchanged); `run_manifest.json`
  diff confirmed to be the old 12,213 records unchanged as an exact prefix of the new 18,099 (no
  existing record edited, 5,886 new ones appended); no Phase 1-4-frozen file, `phase3_subelements/`,
  `pilot_3models/`, `phase5/6`, or `CLAUDE.md` touched anywhere in this task.

**Final summary (short, per task's requested closing format)**: cost **$16.7459** (6 sets ×
327 verse-units × 3 models = 5,886 calls, under the $17.3096 estimate despite a mid-run
Anthropic credit-balance detour); poet-date research covered 36/52 corpus poets (14 high / 10
medium / 12 low confidence, 16 blank with reasons); group composition — M1=(الكميت بن زيد
الأسدي, أبو دلامة), M2=(أبو نواس, أبو تمّام), E1=(طرفة بن العبد, الصنوبري), E2=(قطري بن الفجاءة
المازني, أبو فراس الحمداني), H1=(الفرزدق, جرير بن عطيّة), H2=(ديك الجن, ابن الرومي) — 12 globally
distinct poets, selected by RANK within a 14-poet selection-eligible population (a declared
deviation from Part 1's full-corpus year-threshold bands, which left some roles pool-exhausted);
verse-level F1 next to Z/A/B/D2 and full CI verdicts are in `E1_V2_ERAS_FEWSHOT.md` §2-3 and the
HTML report's new panel l; **plain answer: whether poet era matters is model-dependent and the
signal is rarely larger than ordinary example-choice noise** — Claude and Gemini each show some
pooled band-level effect (by two different, non-overlapping routes), GPT shows none, and the one
consistent cross-model finding is that set E1's specific poet pairing underperforms the existing
A/B/D2 sets for all three models. Caveats: one run, one draw of poets/verses, no noise baseline,
and only 14 of 36 dated poets survived the selection-eligibility restriction.

---

**2026-10-25 — Quartile few-shot task (Q1/Q2), Step 0 (no API calls) — STOPPED at the >100-year
guard, awaiting user decision**

Task: supervisor-style quartile design — "timeline from 0 to 1000; take one poem from 250 and
one from 750" — i.e. each new set = one example near the death-year axis's 25th percentile (P25)
+ one near its 75th percentile (P75), named **Q1** and **Q2** (different poets from each other),
on top of the existing M1/M2 (middle), E1/E2 (extremes), H1/H2 (middle-of-each-half) sets. Scope
discipline followed: nothing existing read, edited, or re-run; H1/H2 and all prior results/
manifest records stay exactly as they are (H1/H2 are to be relabeled in the report as "H1/H2
(same-half variant, not the requested design)" once Q1/Q2 exist, but their underlying data is
untouched). Backed up `docs/phase4/E1_V2_REPORT.html` to `docs/phase4/E1_V2_REPORT_before_q.html`
(copy only, byte-identical, before any change).

**Axis** (same corpus axis as `ERAS_ANALYTICS.md`, dated-poet population, min=544 max=1291 CE,
range 747 years):
- **Range-axis targets** (min + 0.25×range, min + 0.75×range): **P25 = 730.75 CE, P75 = 1104.25
  CE**.
- **Verse-weighted-quantile alternative** (25th/75th percentile of death year, weighted by verse
  count, over the same 36-poet dated axis `ERAS_ANALYTICS.md`'s verse-weighted median [784.0] is
  built on — linear-interpolation percentile of the expanded multiset): **P25 = 649.0 CE, P75 =
  845.0 CE**.

**Nearest-5-eligible-poets check** (same eligibility as M1..H2: poem not NO_TEXT/ALREADY_USED/
v1-EXAMPLE/F5-F10/eval_pool_25, >=1 candidate verse passing `eras_config.note_quality()`,
`poet_dates.csv` confidence high/medium — this is exactly the same 14-poet selection-eligible
population M1..H2 were drawn from), excluding the 8 poets already used in M1/M2/E1/E2 where
possible (الكميت بن زيد الأسدي, أبو دلامة, أبو نواس, أبو تمّام, طرفة بن العبد, قطري بن الفجاءة
المازني, الصنوبري, أبو فراس الحمداني):

| Target | Nearest 5 eligible (excl. M/E) | death | distance | n candidate verses |
|---|---|---|---|---|
| P25 range (730.75) | الفرزدق *(H1)* | 728 | 2.75 | 5 |
| | جرير بن عطيّة *(H1)* | 728 | 2.75 | 3 |
| | جميل بن معمر *(unused)* | 701 | 29.75 | 20 |
| | ديك الجن *(H2)* | 849 | 118.25 | 37 |
| | ابن الرومي *(H2)* | 896 | 165.25 | 35 |
| P75 range (1104.25) | محمد بن هاشم الخالدي *(unused)* | 996 | **108.25** | 4 |
| | ابن الرومي *(H2)* | 896 | 208.25 | 35 |
| | ديك الجن *(H2)* | 849 | 255.25 | 37 |
| | الفرزدق *(H1)* | 728 | 376.25 | 5 |
| | جرير بن عطيّة *(H1)* | 728 | 376.25 | 3 |

**STOP condition hit, per task instruction**: the nearest eligible poet to P75 (range-axis) is
**108.25 years away — over the 100-year threshold** — and this holds whether or not M1/M2/E1/E2's
poets are excluded (محمد بن هاشم الخالدي was never used by any existing set, so excluding M/E
changes nothing for this particular number). A second, independent problem surfaced by the same
table: of the 14-poet selection-eligible population, **only 2 poets have never been used by any
existing set (M1/M2/E1/E2/H1/H2)** — جميل بن معمر (701 CE) and محمد بن هاشم الخالدي (996 CE) —
every other candidate near either quartile point is already an H1/H2 poet (الفرزدق/جرير بن عطيّة
near P25; ديك الجن/ابن الرومي near P75). Since Q1 and Q2 together need 4 distinct poet slots (2
sets × 2 poets, "different poets from each other" per the task), **the pool cannot supply two
full, mutually-distinct Q-sets without either reusing H1/H2 poets or accepting a >100-year gap**
no matter which axis definition is used — the quantile alternative does not fix this on its own
(see below). Per task instruction: **stopping here, not choosing silently.** Options for the
user to pick from (full detail, including the quantile-axis version of the same table, in the
next log entry once a decision is made):
  **(a) Range-axis points (P25=730.75, P75=1104.25) with the nearest available poets** — accepts
  either the >100y-away محمد بن هاشم الخالدي for the P75 slot (count=4 candidate verses, the
  thinnest of the whole 14-poet pool) or reusing an H1/H2 poet (ديك الجن/ابن الرومي, d=118-255 vs
  a true P75 target) for one or both Q-sets.
  **(b) Quantile-based points (P25=649.0, P75=845.0, verse-weighted)** — closer in absolute
  distance for P75 (ديك الجن at d=4, ابن الرومي at d=51) but those are themselves H1/H2 poets, so
  this still requires H1/H2 poet-reuse for at least the P75 slot; only marginally eases P25
  (جميل بن معمر's distance drops from 29.75 to 52.0 relative to the quantile point — i.e. WORSE
  for P25, better for P75). Neither option supplies 4 fully fresh, mutually-distinct poets without
  reuse — that is a property of this corpus's thin eligible-poet population (only 14 of 36 dated
  poets survive the standing eligibility filter), not of the axis-definition choice.
No API calls made. Awaiting user's explicit choice between (a) and (b), and whether H1/H2-poet
reuse is acceptable for Q1/Q2 given the above, before Step 0's poet/verse draw proceeds.

**User's decision**: quantile axis (P25=649.0, P75=845.0 CE, verse-weighted). H1/H2-poet reuse
allowed for the **P75 slot only**, declared and printed wherever it happens; M1/M2/E1/E2 poets
never reused, no exception; Q1 and Q2 use 4 distinct poets between them; P75 slot prefers H2's
own two poets split across Q1/Q2 (ديك الجن for one, ابن الرومي for the other); P25 slot prefers
the nearest poet(s) never used by ANY existing set.

**Step 0 continued (no API calls): Q1/Q2 selection + draw.**
`experiments/phase4_e1_v2/eras_quartile_config.py` (constants + an independent
re-implementation of the weighted-percentile computation, asserted to reproduce
`eras_axis.json`'s frozen median_by_verses=784.0 at q=0.5 as a self-check) +
`experiments/phase4_e1_v2/eras_quartile_examples.py` (selection + draw, reusing
`eras_examples.build_eligible_poets`/`draw_examples` UNCHANGED — same poem-exclusion set as
every eras set: NO_TEXT/ALREADY_USED/v1-EXAMPLE/F5-F10/eval_pool_25).

**P25-slot bug caught and fixed before any file was written**: a first version of
`pick_p25_candidates()` ranked candidates by (confidence tier, distance) only, which let
محمد بن هاشم الخالدي (996 CE, medium confidence, but **347 years** from P25=649 — he actually
belongs near P75, where he is only 151 years away) outrank النمر بن تولب العكلي (635 CE, low
confidence, only **14 years** from P25) purely on confidence tier, producing a target-point-vs-
nearest-poet mismatch (distance=347.00 printed for Q2's P25 slot on the first run — caught by
inspection before unit checks or any draw was trusted). Fixed by adding a "must be closer to the
P25 target than to the P75 target" filter before the confidence-tier ranking even runs — a
candidate that actually belongs to the OTHER quartile can no longer leak into this one regardless
of confidence. Declared, not silently patched (see `eras_quartile_examples.py`'s
`pick_p25_candidates` docstring).

**Final selection** (all distances in years, verse-weighted-quantile targets P25=649.0/P75=845.0):

| Set | P25 slot | P75 slot |
|---|---|---|
| Q1 | جميل بن معمر (701 CE, medium conf., d=52.00, 20 candidate verses) | ديك الجن (849 CE, medium conf., d=4.00, 37 candidate verses) **[reused from H2]** |
| Q2 | النمر بن تولب العكلي (635 CE, low conf. — declared fallback, d=14.00, 3 candidate verses) | ابن الرومي (896 CE, high conf., d=51.00, 35 candidate verses) **[reused from H2]** |

**Declared deviation**: النمر بن تولب العكلي is "low" confidence, one tier below the
high/medium standing eligibility rule every other eras set used — admitted here ONLY because
the P25 slot's high/medium-confidence pool has exactly ONE never-used candidate (جميل بن معمر),
and the task calls for 2 distinct P25 poets; the next-nearest low-confidence candidate was taken
rather than silently reusing an H1/H2 or M1/M2/E1/E2 poet for the P25 slot (same "declare, don't
silently patch" convention as `eras_examples.py`'s own rank-based band-fix deviation).
**Declared reuse**: ديك الجن and ابن الرومي are H2's own two poets — **Q shares its P75-slot
poets with H2**, so any Q-vs-H comparison in the analysis step is confounded by shared examples
(flagged again in Step 3/4's report text, not just here).

Drawn example verses (seed=42, one `random.seed()` call + sequential `random.sample(..., 1)`
per poet in order Q1-P25, Q1-P75, Q2-P25, Q2-P75 — own RNG stream, separate from every other
module's draw):
- Q1 / جميل بن معمر: poem 25685 v11 — "تَجودُ بِهِ في النَّومِ غَيْرِ مُصَرَّدٍ وَيُحزِنُ أيْقاظًا
  علَيْها عَطاؤُها" — span «عَطاؤُها», analysis: "العطاء استعارة للوصال (وربما للقبلة)، فهي أمور لا
  تعطى على الحقيقة".
- Q1 / ديك الجن: poem 18677 v15 — "في كُلِّ يَوْمٍ لقَلبي مِنْ تَذَكُّرِهمْ تَغْرِيبةٌ وَلِدَمْعي
  مِنْهُمُ سَفَرُ" — span «وَلِدَمْعي مِنْهُمُ سَفَرُ», analysis: "الدمع يسافر من هنا نحوهم، أي يسقط
  ويسافر بعيدًا عن القوم الحاليين في إثر القوم الماضين".
  **(Correction, same session: an earlier draft of this log entry had Q1's two poems swapped
  between these two poets — independently reconfirmed against `data/ali_poems/manifest.csv`
  before fixing; the underlying code/data/HTML render were never wrong, only this write-up.)**
- Q2 / النمر بن تولب العكلي: poem 23986 v21 — "أتَى حصنَهُ ما أتَى تُبَّعًا وأبرهَةَ المَلكُ
  الأعظمَا" — span «أتَى حصنَهُ ما أتَى تُبَّعًا», analysis: "كأنّ المصير يأتي".
- Q2 / ابن الرومي: poem 12331 v9 — "قد بدرتْ سَبة الخطيب فما لجلج في قيله ولا اكترثَا" — span
  «قد بدرتْ سَبة الخطيب فما لجلج في قيله ولا اكترثَا», analysis (full, reproduced verbatim from
  the corpus annotation): "هو أراد أن يتكلم، لكن سبّته [استه] سبقته وأعطته كلامًا. فجاء كلامه غير
  ملجلج (غير متردد)، بل واضحًا، ولم يأبه بأحد من الحاضرين. قد يكون هنا تعريض بوهب، بأنّه عندما
  يخطب هو يتردد ويكترث بمن حوله، لكنه استه اليوم أسعفته، فجاء كلامه واضحًا على غير عادة."

`experiments/phase4_e1_v2/unit_checks_quartile.py`: (1) Z/A/B/C **and** M1/M2/E1/E2/H1/H2 prompt
previews regenerate byte-identical (confirms this task perturbed nothing existing); (2) 0 overlap
between the 4 Q1/Q2 example-source poems (18677, 25685, 23986, 12331) and eval_pool_25.json's 25;
(3) exactly 2 distinct poets per set, 4 distinct overall, 0 M1/M2/E1/E2 poets reused, H1/H2 reuse
exactly equal to the declared {ديك الجن, ابن الرومي} set; (4) every drawn verse independently
reconfirmed (fresh `gt_v2.gt_spans_for_subtype` call) to carry a real استعارة فعل GT span; (5) Q1
and Q2's rendered prompts share the byte-identical header + Example-1 scaffold as set A. All
checks passed. Wrote `config/prompt_preview_{Q1,Q2}.txt`;
Q1 = **604 tokens** (cl100k_base), Q2 = 671 tokens — Q1's full rendered prompt:

> You are an Arabic rhetoric analysis engine. Follow instructions strictly.
>
> SUB-ELEMENT DEFINITION (REFERENCE): استعارة فعل — "اللفظ المُستعار هو فعل، أو له معنى الفعل
> (مثل المصدر)، مُستخدم استعارةً لا حقيقة." Example 1 («هُم يتساقَونَ المنايا»، the standing
> scaffold example, byte-identical to set A). Example 2 = the جميل بن معمر verse above. Example 3
> = the ديك الجن verse above.

(Full byte-exact text in `config/prompt_preview_Q1.txt`; Q2's analogous file swaps in النمر بن
تولب العكلي / ابن الرومي.)

**Step 1 (cost dry-run, no API calls).** `experiments/phase4_e1_v2/dryrun_quartile.py` — same
method as `dryrun_eras.py` (reuses its `build_cell_input_tokens`/`price_block` unchanged), real
tiktoken `cl100k_base` input-token counts for Q1/Q2's actual built prompts × eval_pool_25.json's
real 327 verse-units, real average output-tokens/call per provider from the completed
`run_manifest.json` (anthropic mean=193.6 n=5924, openai mean=96.6 n=5924, google mean=81.5
n=5924 — pooled across every set now in the manifest, including M1..H2, confirming output length
is still ~input-independent). **Planned run: 2 sets × 327 verse-units × 3 models × 1 run = 654
calls. Total estimated cost: $5.9032** (worst-case and config.py Gemini pricing coincide here) —
Q1 $2.8941, Q2 $3.0091.

**STOPPING HERE per task instruction and CLAUDE.md rule 5** — no API call has been made.
Presenting the cost breakdown and awaiting the user's explicit "go" + a hard
`--max-additional-usd` cap before running `run_quartile.py --confirm` (Step 2). Committing and
pushing everything so far now, per the task's explicit instruction.

**User confirmed: go ahead, `--max-additional-usd 10`.**

- **Step 2 (API calls).** First invocation of `run_quartile.py --confirm --max-additional-usd 10`
  was launched backgrounded incorrectly (a shell-level `&` combined with the harness's own
  background-process flag double-backgrounded it) and was killed after only 11/654 cells —
  caught immediately by checking the manifest rather than trusting the "exited with code 0"
  status, and re-launched correctly (no shell `&`, harness background flag only). The runner's
  resumability skipped the 11 already-done cells automatically, no `--force` needed, no
  double-spend. **Final verified coverage: 327/327 ok cells for every (set, provider) pair, 6/6
  combinations, 0 errors.** Real cost for this task: manifest total spend went from $65.1449
  (baseline, includes the earlier Phase 4 `anthropic_opus` task) to $70.8228. **Actual Q1/Q2
  cost, computed directly as the sum of `call_cost()` over every Q1/Q2 manifest record (the
  precise figure — the naive before/after delta understates it slightly because the 11 cells
  from the first, double-backgrounded launch attempt were already folded into the "baseline"
  snapshot taken after that attempt): $5.7209**, under the $5.9032 pre-run estimate.
- **Step 3 (scoring/analysis, no API calls).** `experiments/phase4_e1_v2/analyze_quartile.py`
  (mirrors `analyze_eras.py`'s cache-based-scorer approach unchanged — `ensemble_v2.build_parsed_
  cache`/`score_set_single_model`/`score_set_ensemble`, both already generic over `set_name`).
  Computes, per model × criterion (verse PRIMARY, strict/token secondary): Q1/Q2 individual
  TP/FP/FN/P/R/F1; POOLED Q=Q1+Q2; bootstrap 95% CIs (n=2000, seed=0) for Q1-vs-Q2, pooled-Q-vs-
  pooled-M/E/H, pooled-Q-vs-Z, pooled-Q-vs-A/B/D2; 3-model ensemble for Q1/Q2.
  **Verified served Gemini model_id directly from every manifest record** (all google-provider
  rows across the ENTIRE manifest, M1..H2 and Q1/Q2 alike): every single one logs
  `model_id="gemini-3.5-flash"` — **never `gemini-3.6-flash`**. This matters because
  `analyze_eras.py`'s own `DISPLAY` dict labels google as `"Gemini (served: gemini-3.6-flash)"` —
  that label is simply wrong (cosmetic/print-only, does not affect any stored score; left as-is
  per this task's additive-only scope, flagged in both this log and `E1_V2_ERAS_FEWSHOT.md`).
  **Caught and fixed the "Pooled Gemini" table bug the task asked to check**: §2's
  "Pooled (M=M1+M2, E=E1+E2, H=H1+H2), verse-primary" table in `E1_V2_ERAS_FEWSHOT.md` had
  Gemini's row showing **strict-criterion** numbers (82/218/276 → F1 0.249, etc.) mislabeled as
  verse-primary — Claude's and GPT's pooled rows in that same table were already correct; only
  Gemini's row was swapped. Confirmed directly against `analysis_report_eras.json` (never wrong
  itself — this was purely a markdown transcription error) and corrected in place with a marked
  note (real verse-primary pooled Gemini: M=126/174/128 F1=0.455, E=137/168/117 F1=0.490,
  H=167/216/87 F1=0.524 — consistent with Gemini's own per-set verse F1 range 0.410-0.548 shown
  directly above that table).

  **Headline Q1/Q2 results (verse-primary)**:

  | Model | Q1 F1 | Q2 F1 | Pooled Q F1 | (ref) M | (ref) E | (ref) H |
  |---|---|---|---|---|---|---|
  | Claude | 0.445 | 0.588 | 0.524 | 0.553 | 0.501 | 0.545 |
  | GPT | 0.453 | 0.464 | 0.459 | 0.504 | 0.490 | 0.505 |
  | Gemini | 0.450 | 0.495 | 0.473 | 0.455 | 0.490 | 0.524 |

  Full per-model/per-criterion tables, every CI, and per-poem diff signs:
  `results/phase4_e1_v2/analysis_report_quartile.json`.

  **CI verdicts (verse-primary)**: Q1 vs Q2 is **SIG for Claude** (F1diff=-0.1425,
  CI95=[-0.2178,-0.0659] — Q2/ابن الرومي clearly outscores Q1/ديك الجن for Claude specifically,
  TP=92/FP=94/FN=35/F1=0.588 vs TP=57/FP=72/FN=70/F1=0.445), **ns for GPT and Gemini**
  (mirrors the within-band noise pattern every prior M1-M2/E1-E2/H1-H2 check already found, just
  concentrated in one model here instead of spread across all three). Pooled Q vs pooled M/E:
  **ns for all 3 models**. Pooled Q vs pooled H: **ns for Claude**, **SIG negative for GPT**
  (−0.0455) **and Gemini** (−0.0513) — recall this comparison is the one flagged as confounded
  (Q shares its P75-slot poets with H2). Pooled Q vs Z: **SIG positive for Claude** (+0.1469)
  **and Gemini** (+0.0797), **SIG negative for GPT** (−0.0895) — the same per-model
  fewshot-helps/hurts split every other E1 v2 fewshot comparison in this project has already
  shown. Pooled Q vs A/B/D2: GPT is **SIG negative against all three** (A −0.0817, B −0.0537,
  D2 −0.0439); Claude is SIG negative against A (−0.0525) and D2 (−0.0443) but ns against B;
  Gemini is SIG negative against A only (−0.0383), ns against B/D2.
  **Declared confound, stated again per the task's explicit instruction**: Q shares its P75-slot
  poets (ديك الجن, ابن الرومي) with H2 — every Q-vs-H comparison above is confounded by this
  shared-example overlap, not a clean independent-design comparison the way Q-vs-M/E/Z/A/B/D2 are.
  3-model ensemble: Q1 ensemble F1=0.486 (best single openai 0.453, avg 0.449); Q2 ensemble
  F1=0.557 (best single anthropic 0.588, avg 0.516) — same "lands near the best single, above the
  average of the 3 singles" pattern as every other ensemble check in this project.

- **Step 4 (write-up + report, no API calls).** Added a new "§6 — Quartile few-shot experiment
  (Q1/Q2)" section to `docs/phase4/E1_V2_ERAS_FEWSHOT.md` (target points + the >100y STOP,
  selection/reuse/fallback with the declared P25-candidate-ranking bug fix, verse-primary
  results, pooled-Q table, the full CI table, ensemble, the "Pooled Gemini" write-up-bug
  correction, plain answer, caveats) and relabeled H1/H2 in §1.4's table as "(same-half variant,
  not the requested design)" with an explanatory note, per the task's explicit instruction —
  H1/H2's underlying data and every number built from them is untouched.
  **Write-up bug caught and fixed while assembling this section**: an earlier draft of this log's
  own "drawn example verses" list had Q1's two poems swapped between its two poets (جميل بن معمر
  and ديك الجن) — caught by independently cross-checking `data/ali_poems/manifest.csv`'s
  poem-to-poet mapping (poem 25685 → جميل بن معمر, poem 18677 → ديك الجن) before writing the doc
  section, and before trusting the HTML render. The underlying code/data/manifest/HTML render
  were **never** wrong (confirmed by re-running `eras_quartile_examples.build_quartile_sets()`
  three times and diffing against the persisted `config/quartile_example_sets.json` — bit-
  identical every time); only this log's manual transcription had the two poems swapped. Fixed
  in both this log (above) and the new doc section.
  **Cost figure corrected too**: the Step 2 entry's "$5.6779 actual" was a naive before/after-
  manifest-total delta that (harmlessly but incorrectly) folded the 11 stray cells from the
  first, double-backgrounded launch attempt into its "baseline" snapshot; the precise figure,
  summed directly over every Q1/Q2 manifest record's own `call_cost()`, is **$5.7209** (still
  under the $5.9032 estimate) — corrected in both this log and the new doc section.

  `scripts/build_e1v2_report.py`: added a `quartile_exists`-guarded loading block (same
  convention as `eras_exists`/`multipoet_exists`), `build_quartile_f1_table`/
  `build_quartile_pooled_table`/`build_quartile_ci_table`/`build_quartile_ensemble_table`/
  `build_quartile_example_card`/`build_quartile_prompt_block`/`build_quartile_section` (new panel
  "m", metric toggle shared with the rest of the page via the existing page-global
  `toggleCriterion`). No existing function, panel (a-l), or stored value was edited — confirmed
  by the script's own post-write self-checks (every existing F1 value string still present,
  5886/5886 completeness unchanged) and by visually rendering the new panel in the built-in
  browser (mandatory per CLAUDE.md's RTL rule): Arabic poet names/verse text/analysis notes in
  the new Q1/Q2 example cards render RTL correctly, the metric toggle correctly switches the new
  F1/pooled/CI tables between verse/strict/token (spot-checked: Claude strict Q1=0.214 matches
  `analysis_report_quartile.json` exactly), and SIG rows highlight correctly in the new CI table
  (e.g. Claude Q1-Q2 -0.143 SIG, GPT Q-A -0.082 SIG, both confirmed against the JSON).
- Verified additive-only: `eval_pool_25.json` has zero diff (byte-unchanged); `run_manifest.json`
  diff confirmed to be the old 18,099 records unchanged as an exact prefix of the new 20,061 (no
  existing record edited, 1,962 new ones appended); no Phase 1-4-frozen file, `phase3_subelements/`,
  `pilot_3models/`, `phase5/6`, `CLAUDE.md`, or any H1/H2/M1/M2/E1/E2 result was touched anywhere
  in this task.

**Final summary (short, per task's requested closing format)**: target points — range axis
P25=730.75/P75=1104.25 CE (rejected, P75's nearest poet was 108y away); **verse-weighted-quantile
axis chosen, P25=649.0/P75=845.0 CE**. Poets chosen — Q1=(جميل بن معمر P25, ديك الجن P75 *reused
from H2*), Q2=(النمر بن تولب العكلي P25 *declared low-confidence fallback*, ابن الرومي P75
*reused from H2*) — only 2 poets in the whole 14-poet eligible pool were never used by any
existing set. Cost: **$5.7209** (654 calls, under the $5.9032 estimate). Verse F1 (Pooled Q) next
to M/E/H: Claude 0.524 (vs M 0.553/E 0.501/H 0.545), GPT 0.459 (vs M 0.504/E 0.490/H 0.505),
Gemini 0.473 (vs M 0.455/E 0.490/H 0.524) — full table + vs Z/A/B/D2 in §6.3/§6.4. CI verdicts:
Q1 vs Q2 SIG for Claude only (Q2's ابن الرومي example clearly outperforms Q1's ديك الجن example,
+0.14 F1); pooled Q vs M/E all `ns` for every model; pooled Q vs H SIG negative for GPT/Gemini
but **confounded by shared P75-slot poets with H2**; pooled Q vs Z SIG positive for
Claude/Gemini, SIG negative for GPT (the familiar per-model fewshot split); pooled Q vs A/B/D2
mixed, GPT significantly worse than all three. **Plain answer: the literal quartile design
performs about the same as every other example-selection strategy already tried (middle-band,
extremes) for Claude and Gemini, and is a clear net negative for GPT relative to zero-shot and
every 2-example baseline** — example-selection strategy along the death-year axis does not
reliably move the needle beyond ordinary draw-to-draw noise, consistent with every other E1 v2
fewshot-example-selection finding in this project. Two write-up bugs were caught and fixed
during Step 3/4 (unrelated to Q1/Q2's own correctness): §2's "Pooled Gemini" verse-primary table
had silently carried strict-criterion numbers, and this log's own first draft had Q1's two
example poems swapped between poets — both confirmed against independent sources (the raw JSON
report, the manifest poem-poet mapping) and corrected in place.

---

## 2026-10-29 — Design-choice task: "GPT-Z + Claude-FS, without Gemini" vs. keeping Gemini

**Task**: answer whether the planned production design (GPT-5.4-mini zero-shot + Claude Sonnet
4.6 few-shot, no Gemini) is justified, vs. keeping Gemini in the existing 3-model 2-of-3-majority
design. **NO API calls** — read-only analysis over `run_manifest.json` (20,061 records, 0 errors)
and the existing docs/results; new code only, no existing file/result/report edited. Four parts
as specified: (1) cross-phase consistency Phase 1 vs E1 v2, (2) design comparison on the 25-poem
pool, (3) cost, (4) verdict.

**Step 0 — reading**: `CLAUDE.md`, `PROJECT_STATE.md` §1-§7 (Phase 1 frozen numbers, esp. §3a
Trope TEST table), `E1_V2_RESULTS.md`, `E1_V2_ENSEMBLE.md`, `E1_V2_ERAS_FEWSHOT.md` (incl. its
§6 quartile addendum), `E1_V2_MULTIPOET.md`, `FULL_COST_MODEL_V2.md`, and the relevant
`experiments/phase4_e1_v2/*.py` modules (`e1v2_config.py`, `ensemble_v2.py` — the existing
cache-based scorer, reused unchanged — `gt_v2.py`, `verse_analysis.py`, `runner.py`). Confirmed
directly from `run_manifest.json`: 20,061 records total, sets Z/A/B/C/D/D2/E1/E2/H1/H2/M1/M2/Q1/Q2
each have exactly 981 records (327 verse-units × 3 models × 1 run) on the shared 25-poem
`eval_pool_25.json`; F5/F10 have 3,000 each on a *different* 50-poem pool (confirmed only 9/25
overlap with eval_pool_25, per `E1_V2_MULTIPOET.md` §1.4) and were excluded from every combination
in this task for that reason; `anthropic_opus` has 327 (set A only). 0 errors anywhere. Also
confirmed directly (not assumed): every `google`-provider record's `model_id` field reads
`"gemini-3.5-flash"` across all 6,578 such records, in every set including M1..Q2 — consistent
with `E1_V2_ERAS_FEWSHOT.md` §6.6's later correction, not with `E1_V2_RESULTS.md`'s original
`gemini-3.6-flash`-actually-served claim (flagged in the new doc's §3.3, not resolved here since
no live API check was authorized).

**Step 1 — new code** (`experiments/phase4_e1_v2/design_choice/`, additive only):
- `combine.py`: 2-voter OR/AND combination (`score_poem_two_voter`) and a generalized 3-voter
  2-of-3-majority (`score_poem_three_voter_majority`) that, unlike `ensemble_v2.score_poem_ensemble`
  (which hardcodes all 3 voters on one shared `set_name`), accepts independent `(set_name,
  provider)` pairs per voter — needed to express "GPT on Z, Claude on set B, Gemini on set B/Z."
  Declared span-matching rule for the 2-voter case (stated in the module docstring, same discipline
  as `ensemble_v2.py`'s own declared limitation): OR takes the union of either voter's correct
  span match; AND requires both voters' match indices to agree on the same GT span. Also
  `agreement_matrix()` (both/a_only/b_only/none buckets + accuracy vs. GT, generalizing
  `ensemble_v2.agreement_for_set`'s 3-vote-bucket idea to 2 voters).
- `analyze_design_choice.py`: builds the parsed cache via `ensemble_v2.build_parsed_cache`
  (unchanged) over the FULL manifest, then scores **D_A** (GPT-Z alone), **D_B** (Claude-FS alone,
  every one of 10 sets: A/B/D/D2/M1/M2/H1/H2/Q1/Q2 — C excluded, it's the already-identified
  homogeneous-root outlier, not a production candidate), **D_C** (GPT-Z + Claude-FS OR/AND, every
  set), **D_D** (3-model 2-of-3 majority, Gemini-FS and Gemini-Z variants, every set), **D_E**
  (the other two pairs: GPT-Z+Gemini-FS, Claude-FS+Gemini-FS, every set), and leave-one-out
  marginal contributions (ensemble F1 − best 2-model-without-X F1, bootstrap 95% CI via
  `verse_analysis.bootstrap_pair` unchanged) for all three models, across verse/strict/token, all
  10 Claude-FS sets — plus the GPT-Z vs Claude-FS[B] agreement matrix. Verified by running: output
  matched hand-sanity-checks against the already-published D_B numbers in `E1_V2_RESULTS.md`
  (Claude A=0.576/B=0.547, GPT Z=0.549) and `E1_V2_ERAS_FEWSHOT.md`/`E1_V2_MULTIPOET.md`
  (M1=0.515/M2=0.584/H1=0.553/H2=0.536/Q1=0.445/Q2=0.588/D=0.562/D2=0.568) exactly, since these
  are literally `score_set_single_model` calls already proven correct by `ensemble_v2.py`'s own
  `verify_single_model_cache_scorer`. Output: `results/phase4_e1_v2/design_choice/
  analysis_report_design_choice.json`.

**Step 2 — key findings** (full detail in the new doc):
- **Part 1**: Phase 1's Trope ranking (Gemini > GPT > Claude) does not survive into E1 v2's
  استعارة فعل subtype. Zero-shot: GPT is best on all 3 criteria (verse/strict/token) — close to
  inverted from Phase 1. Few-shot: ranking is metric-dependent (Claude leads verse, Gemini leads
  strict/token, GPT drops to last on strict/token).
- **Part 2**: on verse (primary), Gemini's leave-one-out marginal contribution to the 3-model
  majority ensemble is **not significant in any of the 10 Claude-FS sets** (mean ≈ −0.005); the
  simple 2-model GPT-Z+Claude-FS OR combination (0.560 on set B) is numerically *at or above* the
  3-model ensemble (0.556). But on strict/token, **Claude+Gemini is the best 2-model pair in 8-9
  of 10 sets, and GPT+Claude (the production pair) is never the best pair on either span-level
  metric** — flagged as the clearest concrete argument *for* keeping Gemini, specifically as
  Claude's partner, even though it doesn't move the primary metric. The strict/token
  leave-one-out numbers (SIG negative for every model in every set) were explicitly diagnosed as
  a combination-rule artifact (3-way span-identity-majority vs. 2-way OR), not literal evidence of
  harm, consistent with `E1_V2_ENSEMBLE.md`'s own already-documented limitation of the same rule.
- **Part 3**: real cost already spent on this pool: no-Gemini design $2.17, +Gemini-FS $2.77.
  Full-corpus projection from `FULL_COST_MODEL_V2.md`'s existing S1/S2 figures (no new estimate):
  no-Gemini $545.13, +Gemini-FS $697.56 — a $152.43 (22%) saving from dropping Gemini. Gemini
  model-identity/pricing ambiguity flagged per the manifest check above.
- **Part 4**: dropping Gemini is a defensible but not risk-free cut — no significant loss on the
  primary metric, real cost saving, but it gives up the strongest-pairing partner for Claude on
  span-level correctness, rests on 1 run with no noise baseline, and has been tested on exactly
  one of 25 subtypes (the one subtype where Phase 1 found Gemini winning most clearly on the full
  Trope category). Recommended a cheap (~$2.37/1 run, ~$4.73/2 runs) zero-shot-only 3-model check
  on one additional, structurally different subtype (e.g. a كناية/طباق subtype) before committing
  to the full run — **not run**, per the task's no-API-calls scope.

**Step 3 — write-up**: `docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md` (full English report, all 4
parts) and `docs/phase4/DESIGN_CHOICE_SUMMARY_AR.md` (short Arabic summary). No existing
Phase 1-4-frozen file, `phase3_subelements/`, `pilot_3models/`, `CLAUDE.md`, or any existing
E1 v2 result/doc was touched — confirmed additive-only (new files in `experiments/phase4_e1_v2/
design_choice/`, `results/phase4_e1_v2/design_choice/`, `docs/phase4/` only).

**Final summary (short)**: ranking Phase 1 (Gemini>GPT>Claude on Trope) vs E1 v2 (GPT best
zero-shot; Claude/Gemini split by metric on few-shot, GPT weakest on strict/token) — does not
replicate. F1 per design (set B, verse): GPT-Z 0.549, Claude-FS 0.547, GPT+Claude OR 0.560,
3-model majority 0.556. Gemini's marginal contribution: ≈0 and never significant on verse across
10 sets; significantly negative on strict/token in every set, but diagnosed as a combination-rule
artifact. Cost saving from dropping Gemini: $152.43 (22%) projected full-run. **Verdict: dropping
Gemini is justified on the primary metric and on cost, but not risk-free** — Claude+Gemini is the
best-performing pair on span-level (strict/token) metrics in most sets, the finding rests on one
run with no replication, and only 1 of 25 subtypes was tested (the one where Phase 1 found Gemini
strongest on the full Trope category). Recommended, not run: a ~$2.37-4.73 cheap zero-shot check
on one additional, non-استعارة subtype with all 3 models before the full commitment.

---

## 2026-10-29 — HTML report extended: design-choice panel + cross-phase comparison panel

**Task**: add two new collapsible panels to `docs/phase4/E1_V2_REPORT.html` (built, not
hand-edited, by `scripts/build_e1v2_report.py`): (n) the design-choice question from the prior
task (GPT-Z + Claude-FS, with/without Gemini) and (o) a cross-phase model comparison spanning
Phase 1 &rarr; Phase 3 &rarr; E1 v2. **NO API calls.** Only `scripts/build_e1v2_report.py` was
edited (as instructed); no existing result/analysis file was touched. Backed up the pre-task
report to `docs/phase4/E1_V2_REPORT_before_designchoice.html` first, per the task's instruction
(same naming convention as `_before_ensemble`/`_before_multipoet`/`_before_opus`/`_before_q`).

**Step 1 — reading**: `CLAUDE.md`, `docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md` (prior task's
write-up), `E1_V2_RESULTS.md`, `E1_V2_ERAS_FEWSHOT.md`, `E1_V2_MULTIPOET.md`, `PROJECT_STATE.md`
§1-§7 (Phase 1 frozen Trope TEST table, §3a), `results/phase3_subelements/` +
`results/phase3_crossmodel/` (found Phase 3's real per-subtype recall numbers in
`results/phase3_crossmodel/summary.md` + `raw/crossmodel_scoring_snapshot.json` — n=110 for
استعارة فعل, Gemini strict recall 0.264/token 0.255, GPT strict 0.155/token 0.164, **Claude never
run in Phase 3**, Precision/F1 mathematically undefined there by design, no negative samples
exist), `scripts/build_e1v2_report.py` in full (2038 lines) to learn its load/verify/build/assemble
conventions (existence-guarded `*_exists` loads, `analysis_eras["models"][p][c]["per_set"][s]`
/`analysis_quartile["models"][...]`/`analysis_multipoet["primary_pool"][...]` key shapes,
`toggleCriterion`'s page-global `data-criterion` div convention, `verify_*()` functions called
right after definition and a post-write re-read-and-assert block at the end).

**Step 2 — new code in `scripts/build_e1v2_report.py`** (additive, existing functions/sections
untouched):
- New guarded loads: `analysis_design_choice` (the prior task's JSON), `design_choice_doc_text`,
  `full_cost_model_v2_text`, `project_state_md`, `crossmodel_snapshot`/`crossmodel_summary_md`,
  `phase3_row` (the استعارة فعل row from the snapshot). `PHASE1_TROPE_TEST`: the only hand-typed
  numbers in this script (Phase 1's TP/FP/FN aren't in any JSON here) — P/R/F1 derived via a
  locally-reimplemented `_prf1()` (4-line reimplementation of `pilot_3models.analyze.prf1`'s exact
  formula, not an import, because that module's bare `from config import ...` only resolves when
  `experiments/pilot_3models` itself is pushed onto `sys.path`, which this script doesn't do —
  caught as an `ImportError` on first run, fixed by not importing it). `FULL_COST_MODEL_V2_S1_S2`:
  8 hand-carried S1/S2 totals from that doc's §3, each checked present in the doc's own text.
- 4 new `verify_*()` functions (called right after definition, same convention as the existing
  ones): `verify_design_choice_matches_doc()` (6 headline F1s cross-checked against
  `DESIGN_CHOICE_GPTZ_CLAUDEFS.md`'s own printed numbers), `verify_phase1_numbers_in_project_state()`
  (asserts all 6 TP/FP/FN strings and all 6 F1 strings appear verbatim in `PROJECT_STATE.md`, and
  that the locally-derived F1s match to 3dp), `verify_phase3_recall()` (TP/(TP+FN) self-consistency
  against the snapshot's own stored recall, plus presence in `summary.md`), `verify_full_cost_model_v2()`.
  All 4 passed on the first successful run (no numeric mismatches found).
- Panel (n) builders: `_dc_cell()` (one (Claude-FS-set, criterion) &rarr; all 7 design "overall"
  dicts: D_B, D_C-OR/AND, D_D-GeminiFS/GeminiZ, D_E-GPT+Gemini/Claude+Gemini), a 10-set &times;
  7-design F1 matrix table, a headline-set-B P/R/F1 detail table, a leave-one-out CI table (every
  one of the 10 Claude-FS sets, all 3 criteria), the GPT-Z-vs-Claude-FS[B] agreement-bucket table,
  a real-cost-vs-projected-full-corpus-cost table (reusing `FULL_COST_MODEL_V2_S1_S2`), and the
  Part-4 verdict prose (`extract_section()`'d straight out of `DESIGN_CHOICE_GPTZ_CLAUDEFS.md`,
  the same reused-prose convention `E1_V2_RESULTS.md`'s Q1-Q4 sections already use elsewhere in
  this script).
- Panel (o) builders: `_e1v2_overall()` (dispatches a (model, criterion, set) lookup to whichever
  of `analysis`/`analysis_eras`/`analysis_quartile` actually holds that set — Z/A/B/C/D/D2 vs.
  M1/M2/E1/E2/H1/H2 vs. Q1/Q2), `_crossphase_value()` (one function covering all 4
  phase-columns' recall/F1 lookups, returning `None` where a number doesn't exist — Claude in
  Phase 3 — or isn't defined — Phase 3's F1 for anyone), the Phase 1 table, the Phase 3 table
  (recall-only, Claude row explicitly "not run"), a 3-model &times; (Z + 12 few-shot sets, mean +
  range, F5/F10 on their own pool labelled) P/R/F1 table per criterion, a model&times;phase rank
  summary table, and two new inline-SVG bar charts (`build_crossphase_chart_svg('recall'|'f1')`,
  reusing the existing `svg.barchart`/`.axis`/`.bar-label`/`.legend-label` CSS classes and
  `var(--c-anthropic/openai/google)` color variables unchanged — Gemini's bars get an added
  `stroke="var(--fg)"` outline, no new hardcoded colors anywhere, so dark mode needs no new CSS).
  The "plain-English reading" paragraph's two quoted recall/precision numbers (Claude's Z&rarr;A
  move) are pulled live from `_e1v2_overall()`, not hand-typed, so they can never drift from the
  tables above them.
- Wired both new builders into the existing panel-assembly line (`{build_quartile_section()}` 
  &rarr; followed by the two new calls) and added their 6 new source files to `SOURCE_FILES_USED`.
  Extended the post-write verification block with 2 new assertion groups (every design-choice F1
  across all 10 sets &times; 3 criteria &times; 7 designs present in the written HTML; every
  cross-phase E1v2/Phase-1/Phase-3 number present) — both passed.

**Step 3 — run and fix**: first run failed with `ImportError: cannot import name 'RAW_DIR' from
'config'` (the `pilot_3models.analyze.prf1` import collided with `sys.path` state, as flagged
above) — fixed by reimplementing the 4-line formula locally instead of importing it. Second run:
**all verification PASSed**, including the 4 new ones; wrote a 466,747-char file (up from the
prior 413,790-char backup); `ALL_COMPLETE=True`, 5886/5886 cells, 0 errors (unchanged from before
— this task added no new experiment data, only new read-only derived panels).

**Step 4 — browser verification** (built-in browser, per `CLAUDE.md`'s mandatory-render-verification
discipline, extended here to a non-RTL-bug check since there's no `.docx`/bidi concern in this
HTML task): opened the written file, expanded panel (n) and confirmed the verse&rarr;strict
toggle actually re-renders the matrix table with the strict-criterion numbers (D_A 0.549&rarr;0.246,
D_B[B] 0.547&rarr;0.263, etc. — all matching the JSON exactly, confirming the shared page-global
`toggleCriterion` correctly drives the new panels too, not just the pre-existing ones). Expanded
panel (o), confirmed the Arabic subtype label and the comparability warning box render RTL
correctly inline inside the new content. Checked both new SVG charts via
`document.querySelectorAll('svg.barchart')`: both render with real (non-zero) geometry and the
expected rect counts (14 for recall &mdash; 11 real bars + 3 legend swatches, since only
Claude/Phase-3 is `None`; 12 for F1 &mdash; 9 real bars + 3 legend swatches, since the entire
Phase-3 column is `None` for F1). Checked mobile width (375px emulation): confirmed via
`document.documentElement.scrollWidth === window.innerWidth` that there is **no page-level
horizontal overflow** &mdash; individual long tables scroll internally via the existing
`overflow-x:auto` mobile rule (verified directly on a `<table>` element's own computed style),
exactly as every pre-existing table in this report already does; an early same-session reading of
`window.innerWidth` (284) before the viewport fully settled had briefly suggested an overflow,
re-checked and found to be a stale reading, not a real bug. Dark mode could not be visually
exercised (the browser tool renders local `file://` documents with light defaults regardless of
color-scheme emulation), so this was checked structurally instead: `git diff` on the new code
contains zero new hex-color literals (only the pre-existing `&#9888;` HTML entity, not a color) —
every new table/chart cell uses the existing `var(--bg|fg|muted|panel|accent|c-anthropic|...)`
variable system, which the stylesheet already redefines for both the `prefers-color-scheme: dark`
media query and the `data-theme="dark"` override, unchanged by this task.

**Step 5 — final numbers verified** (same figures as the prior task's write-up, now also
embedded in the regenerated HTML and cross-checked against it):

| Model | Phase 1 (Trope, v4, strict F1) | Phase 3 (recall, strict) | E1v2 Z (verse F1) | E1v2 few-shot mean (verse F1, 12 sets) |
|---|---|---|---|---|
| Claude Sonnet 4.6 | 0.242 (#3) | not run | 0.377 (#3) | **0.539 (#1)** |
| GPT-5.4-mini | 0.251 (#2) | 0.155 (#2) | **0.549 (#1)** | 0.500 (#2) |
| Gemini | **0.386 (#1)** | **0.264 (#1)** | 0.393 (#2) | 0.491 (#3) |

(Corrected before commit: an earlier draft of this table mis-stated the few-shot-mean column as
Gemini-led — re-derived directly from the written HTML's own summary table, which the script
computes from real data, not hand-typed; Claude actually leads that column, Gemini is third.)

**Verification result**: every assertion in `build_e1v2_report.py`'s verify suite passed,
including the 4 new ones added this task (design-choice numbers match the prior doc, Phase 1
numbers match `PROJECT_STATE.md` verbatim, Phase 3 recall is internally self-consistent and
matches `summary.md`, the 8 full-cost-model figures match `FULL_COST_MODEL_V2.md`), plus the
post-write re-read assertions confirming every one of those numbers actually landed in the
written HTML file. No mismatches were found or needed fixing beyond the one import-path bug
(caught and fixed before any numbers were ever wrong, not a silent data error).

---

## 2026-10-29 — Phase 7 subtype task (3 models x {zero,few-shot} x 3 subtypes): Step 0 census, STOPPED

**Task**: a new, separate cycle (GPT-5.4-mini, Gemini via `providers_fixed`, Claude Sonnet 4.6) x
{zero-shot, few-shot} x 3 subtypes (تشبيه بليغ, استعارة قديمة, كناية عن صفة), reusing Phase 3's
subtype prompt/schema, one call per verse-unit, 1 run/cell, verse-level F1 primary. **NO API calls
made this task** — Step 0 is data census only, and the task's own gate requires a STOP before any
further step. Backed up `docs/phase4/E1_V2_REPORT.html` to
`docs/phase4/E1_V2_REPORT_before_phase7.html` first, per the task's instruction. New code only in
`experiments/phase7_subtypes/` (`phase7_config.py`, `census.py`, `tashbih_candidates.py`); outputs
only in `results/phase7_subtypes/census.json`. No existing code, result, or manifest record edited.

**Step 1 — reading**: `CLAUDE.md`, `docs/phase4/DESIGN_CHOICE_GPTZ_CLAUDEFS.md`,
`docs/phase4/E1_V2_ERAS_FEWSHOT.md` (note-quality filter, §1.2), this log's tail,
`experiments/phase3_subelements/{subtype_defs,subtype_prompts,fewshot_prompts,providers_fixed}.py`,
`experiments/phase4_e1_v2/{e1v2_config,eras_config,gt_v2,prompt_builder,multipoet_prompt_builder}.py`,
`data/ali_poems/poems/*.json` (schema: `poem_json["annotations"][i]` = `{span_text, verse_index,
element, subtype, theme, analysis, raw_key}`), `data/ali_poems/manifest.csv` (167 poems),
`experiments/phase4_e1_v2/config/eval_pool_25.json` (25 poems, 327 verse-units, seed=43),
`experiments/phase4_e1/ali_poems_io.py`, `results/phase3_crossmodel/summary.md` (per-subtype
Gemini/GPT strict+token recall reference), `experiments/phase3_subelements/build_subtype_files.py`
(found: `data/ground_truth/by_subtype/*.xlsx` is Phase-1-only, 5 poems — NOT the right source for
a full-corpus census; built a fresh census directly from `data/ali_poems/poems/*.json`'s 167 poems
instead).

**Step 2 — census script** (`census.py`, no API calls): loaded all 167 corpus poems (3,470 verses
total), counted every distinct `subtype` string across all annotations (134 distinct strings seen),
and built the task's requested per-subtype table (positive verses, poems, poets, rate/verse,
eligible example verses [non-empty note passing `eras_config.note_quality()`, exact subtype,
excluding the 5 `ALREADY_USED_POEM_IDS` + poem `28601`], distinct poets with eligible examples,
positives inside `eval_pool_25.json`).

**Step 3 — STOP finding (task's own gate, §0a/§0c)**: **`تشبيه بليغ` has ZERO occurrences
anywhere in the corpus's 134 distinct subtype strings, and is not in `subtype_defs.py`.**
Separately checked `تشبيه مؤكد` (the task's §0c comparison partner) — **also ZERO occurrences,
also not in `subtype_defs.py`.** This is not a thin-sample issue — neither string exists at all in
this annotator's scheme. The ground truth's own تشبيه taxonomy classifies by length/completeness
(`تشبيه مطول`/`قصير`/`تمثيلي`/`مركب`/`الشيء بنفسه`/`ضمني`/`غريب`, 20 distinct تشبيه-family strings
total, 124-227 annotations each for the 2 largest), not by the traditional eloquent/confirmed
(حذف الأداة ووجه الشبه) distinction `بليغ`/`مؤكد` names — so there is no silent close match to
substitute; this needs the user's explicit choice, per the task's own "do not substitute silently"
instruction. `استعارة قديمة` (171 annotations) and `كناية عن صفة` (784 annotations) both exist
exactly and both have definitions in `subtype_defs.py` — no issue for those two.

Built a second table (`tashbih_candidates.py`) of the 5 تشبيه-family subtypes that already have a
definition+example in `subtype_defs.py` and >=10 annotations, with Phase 3 crossmodel strict/token
recall reference (`results/phase3_crossmodel/summary.md`, read not re-run) as candidate
substitutes, in case the user wants to proceed with a real تشبيه pair instead.

**Not yet done** (blocked on this STOP): Step 0b's full positives-per-subtype table was completed
for `استعارة قديمة`/`كناية عن صفة`; Step 0c's full comparison table could not be completed for
`تشبيه بليغ`/`تشبيه مؤكد` specifically since both are empty — presented the تشبيه-family
alternative table instead and awaiting the user's choice before Step 1 (few-shot set construction)
or any further step.

**User decision (2026-10-29)**: do NOT substitute a تشبيه subtype now. Run Phase 7 with only the
2 subtypes that exist exactly and already have data (`استعارة قديمة`, `كناية عن صفة`); leave the
3rd slot open until Dr. Ali Hussein responds on what بليغ/مؤكد should actually map to in this
annotator's scheme (`تشبيه مطول`? `تشبيه قصير`? something not yet annotated at all?) — explicitly
logging, per the user's instruction, the finding that drove this: **this corpus's تشبيه taxonomy
has zero بليغ/مؤكد occurrences and classifies by length instead** (`تشبيه مطول`/`قصير`/`تمثيلي`/
`مركب`/`الشيء بنفسه`, §0a/§0c above). Code is being written so a 3rd subtype can be added later as
an **additive** run (its own set name/config entry in `experiments/phase7_subtypes/config/`) without
touching either of these two subtypes' already-drawn examples or results — same convention Set
D/D2 and the eras/quartile sets already used on top of Z/A/B/C in `phase4_e1_v2`.

**Step 1 (no API) — few-shot sets + eval pool, 2 approved subtypes only**: `phase7_examples.py`
built an eligible-example candidate pool per subtype (exact subtype match, non-empty span, note
passing `eras_config.note_quality()`, poem not in the 5 Phase-1 poems / `NO_TEXT_POEM_ID` /
`eval_pool_25.json`, poet not `القرآن الكريم`) — 39 candidates/15 poets for `استعارة قديمة`, 378
candidates/40 poets for `كناية عن صفة`. Anti-"set C" guard (declared, reused unchanged from this
project's own `span_matching.token_overlap_ratio`/`TOKEN_THRESHOLD`=0.5): reject a 2-example draw
if same poem/poet, missing note, or token-overlap ratio >=0.5 on the spans, the full verses, OR the
analysis notes (near-duplicate-pattern check) — re-draw with seed+1 on reject, every attempt
logged. **Both subtypes passed on the first attempt (seed=42, 0 rejects)** — drawn pairs: `استعارة
قديمة` = بشار بن برد (poem 27110 v19, span «المِتَانِ») + أبو فراس الحمداني (poem 6174 v5, span
«وآلْمَوتُ دونَهُ»); `كناية عن صفة` = ابن قيس الرُّقيّات (poem 8470 v2, span «يَطُفْنَ بِيَهْ») +
أبو تمّام (poem 4480 v40, span «جَحْفَلٍ لَجِبِ»). Full rendered prompts + `cl100k_base` token
counts: `استعارة قديمة` zero-shot 339 tok / few-shot 628 tok; `كناية عن صفة` zero-shot 295 tok /
few-shot 561 tok. Written to `experiments/phase7_subtypes/config/phase7_example_sets.json`.

**Eval pool**: `eval_pool_25.json` (25 poems, 327 verse-units) minus the 4 example-source poems
(27110, 6174, 8470, 4480) — **0 actually removed** (none of the 4 were in the pool to begin with,
confirmed programmatically, not assumed), so the pool stays 25 poems/327 verse-units unchanged.
Positives in that pool: `كناية عن صفة` 49 (>=30, fine), **`استعارة قديمة` 15 — BELOW the task's
30-positive floor.**

**<30-positives STOP (task's own gate, not resolved silently)**: computed Option (b)'s concrete
cost via `extend_pool_option.py` (declared seed=100, a separate stream from the example-draw
42-series, shuffles the 132-poem extension-candidate pool once and adds poems in that fixed order
until `استعارة قديمة` reaches 30) so Option (a) and (b) can be compared on real numbers, not
estimated — **16 poems / +312 verse-units needed** (25 poems/327 verses &rarr; 41 poems/639
verses) to take `استعارة قديمة` from 15 to exactly 30 (and `كناية عن صفة` from 49 to 87 for free,
since the same added verses get scored for both subtypes). Extra calls at that size: 312 verses x
2 conditions x 3 models x 2 subtypes = **3,744 calls**, extra cost estimate **~$10.12** (per-call
means from `FULL_COST_MODEL_V2.md` Sec 2, read not re-estimated — Step 2's own dry-run will
compute Phase-7-specific real token counts if Option (b) is chosen). **Awaiting the user's choice
between (a) keep 25 poems, mark `استعارة قديمة` indicative-only, or (b) extend to 41 poems (+$10.12
est.) before Step 2's cost dry-run can run** (Step 2 needs to know the final pool size first).

**User decision (2026-10-29): Option (a)** — keep the 25-poem/327-verse pool unchanged;
`استعارة قديمة`'s result is indicative-only (n=15 GT-positive verses in-pool, below the 30 floor).
No pool extension, no extra poems added, `extend_pool_option.json` kept as a record of the
option not taken.

**Step 2 (no API) — cost dry-run**: `dryrun_phase7.py`. Calls = 327 verse-units x 2 conditions x
3 models x 2 subtypes = **3,924 calls**. Input tokens are REAL (measured via `tiktoken
cl100k_base` on the actual rendered system+user messages this run would send, not guessed):
user-message tokens avg 306.0/verse (min 276, max 327) over the unchanged 327-verse pool; system
tokens per (subtype, condition) from `phase7_example_sets.json` (`استعارة قديمة` zero 339/few 628;
`كناية عن صفة` zero 295/few 561). Output tokens: 120/call, Phase 3 cross-model's own measured
average for this identical exists/appearance/reasoning schema (`results/phase3_crossmodel/
cost_estimate.md`), reused not re-measured. Served model IDs (`pilot_3models/config.py`,
unchanged): `claude-sonnet-4-6` ($3/$15 per MTok), `gpt-5.4-mini` ($0.75/$4.50), `gemini-3.5-flash`
($1.50/$9.00). **Gemini flags, both carried forward from `DESIGN_CHOICE_GPTZ_CLAUDEFS.md` Sec
3.3, unresolved**: (1) served-model identity ambiguity (every manifest logs `gemini-3.5-flash`
requested+served; one never-corroborated claim of `gemini-3.6-flash` was walked back elsewhere);
(2) Gemini bills hidden thinking tokens (`providers_fixed.call_google_fixed`,
`thinking_level='minimal'`) not separately estimated here (no real Phase-7 output exists yet to
measure them from) — a one-sided underestimate risk for Gemini's column only.

**Cost**: primary (token-based) **$9.70** total (Claude $5.34, GPT $1.45, Gemini $2.91; استعارة
قديمة $4.95 / كناية عن صفة $4.76). Cross-check against `FULL_COST_MODEL_V2.md`'s per-call means
(different, longer استعارة فعل prompts, directional only): **$10.60** — the two estimates agree
within ~9%, giving some confidence the primary figure isn't badly off. Full table:
`results/phase7_subtypes/dryrun_cost.json`.

**API readiness**: `OPENAI_API_KEY`/`ANTHROPIC_API_KEY`/`GEMINI_API_KEY` all present in `.env`
(presence-only check, zero API calls made — no balance/quota call attempted per the task's own
"do not call providers" instruction).

**STOP (CLAUDE.md rule 5)**: awaiting the user's explicit "go" and a hard cap
(`--max-additional-usd`) before Step 3 (the real run) — not yet given as of this entry.
