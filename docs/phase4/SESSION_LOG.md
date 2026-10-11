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
