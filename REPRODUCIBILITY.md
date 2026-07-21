# Reproducibility Guide — 3-Model Pilot Cycle

Exact steps to re-run any part of the `experiments/pilot_3models/` pilot cycle from scratch, including the frozen TEST evaluation. See [`PROJECT_STATE.md`](PROJECT_STATE.md) for what each experiment found; this file only covers *how to reproduce the runs*, not the results themselves.

---

## 1. Environment setup

**Python**: 3.13 (developed and run on 3.13.12; nothing here is Python-version-sensitive beyond a standard modern 3.x install).

**Install dependencies** (no `requirements.txt` exists yet for this folder specifically — this is a known open item; the exact versions used throughout this pilot cycle were):

```bash
pip install anthropic==0.117.0 openai==2.44.0 google-genai==2.12.1 python-dotenv==1.2.1 pandas==3.0.3 python-docx==1.2.0 matplotlib==3.11.0
```

**API keys**: copy `.env.example` to `.env` at the repo root and fill in real keys:

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

(`COHERE_API_KEY`, `QWEN_API_KEY`, `HUGGINGFACE_TOKEN` in `.env.example` belong to the unrelated `previous_steps/` line of work, not this pilot — not needed to reproduce anything in `experiments/pilot_3models/`.)

`.env` is loaded automatically via `python-dotenv` by every runner script (`run_pilot.py`, `run_per_verse.py`) — no manual `export` needed. **Never commit `.env`** — it's already covered by `.gitignore`.

All scripts assume being run with `experiments/pilot_3models/` as the working directory (each script does `sys.path.insert(0, str(Path(__file__).resolve().parent))`, so run them as `python <script>.py` from inside that directory, not as a package from elsewhere).

---

## 2. Model IDs and pricing

Defined in `experiments/pilot_3models/config.py` (`MODELS` dict). Verified against provider docs at the time of the pilot:

| Provider | Model ID | Input $/1M tok | Output $/1M tok |
|---|---|---|---|
| Anthropic | `claude-sonnet-4-6` | $3.00 | $15.00 |
| OpenAI | `gpt-5.4-mini` | $0.75 | $4.50 |
| Google | `gemini-3.5-flash` | $1.50 | $9.00 |

Temperature = 0.0 everywhere (`config.TEMPERATURE`). `anthropic` calls use `max_tokens=16000` (see `providers.py`) — this was raised from a 4096 default that silently truncated a 50-verse poem's response; re-check this ceiling if a poem larger than 81 verses (Imru1, the current largest) is ever added.

If prices change, update `MODELS` in `config.py` — every cost calculation in every report script reads from this dict, nothing is hardcoded elsewhere.

---

## 3. Data and ground truth

- Poem texts: `archive/Forth_Step/Data/{Imru1,Imru2,Althobyane,Jareer,Abu_tammam}/poetry.txt` (folder-name mapping: `Imru2` = Imru' al-Qais's poem 8, not a second poet; `Althobyane` = Al-Nabigha Al-Dhubyani; `Jareer` = Jarir). Registered in `config.POEMS`.
- Ground truth: Prof. Ali Hussein's manual annotations, `data/ground_truth/ali_ana/original/*.xlsx`, one file per poem. Loaded and mapped from the 53-element taxonomy down to the 4 thesis elements by `ground_truth.load_ground_truth_spans(poem_key)` — this is the only ground-truth entry point; don't re-derive counts by hand.
- Element definitions: `data/elements/{Trope,Simile,Kenning,Antonymy}.txt` — the canonical definitions every prompt variant builds from.
- **DEV/TEST split is fixed in `config.py`** (`DEV_POEMS = ["Imru2", "Nabigha"]`, `TEST_POEMS = ["Imru1", "Jarir", "Abu_Tammam"]`). This is a frozen decision (see `PROJECT_STATE.md` §2) — do not evaluate or tune anything new against `TEST_POEMS`.

---

## 4. Reproducing the frozen TEST run (the thesis's primary numbers)

This is the one command a stranger with API keys needs to regenerate the exact TEST data behind `PROJECT_STATE.md` §3a-§3d:

```bash
cd experiments/pilot_3models
python run_test.py
```

This runs baseline and v4_combined, 2 runs each, on all 3 TEST poems, for all 3 models — **36 API calls**, landing in `results/pilot_3models/test_final/{baseline,v4_combined}/{Imru1,Jarir,Abu_Tammam}/` (each with `raw/*.txt` responses + `run_manifest.json` usage/cost/error records).

Then reproduce the report:

```bash
python test_report.py
```

This prints the §3a (main P/R/F1 table, both criteria), §3b (run-consistency), and §3c (Trope subtype breakdown) numbers exactly, by calling `test_report.pooled_counts()` / `trope_subtype_breakdown()`, which internally use `analyze.load_all_runs()` + `span_scoring.score_span_level()` — the actual scoring harness (see §6 below).

**Do not re-run `run_test.py` casually** — TEST is spent. It exists here only so the frozen numbers are independently verifiable; running it again would not change `PROJECT_STATE.md`'s reported numbers (which are the ones actually used) and risks the temptation to "just check one more thing" against poems that must stay untouched.

---

## 5. Reproducing DEV-side work (prompt tuning, supplementary experiments)

All of these are safe to re-run freely since DEV is not frozen — re-running will not match the exact stored numbers 1:1 (LLMs are not perfectly deterministic even at temperature 0) but will be close, consistent with the 2-run-majority protocol's tolerance for run-to-run noise (§7 below).

| Step | Command | Produces |
|---|---|---|
| Prompt-variant sweep (v1-v4, ablations) | `python run_variants.py` | `results/pilot_3models/dev_variants/{variant_key}/{Imru2,Nabigha}/` |
| Per-element decomposition (§3f) | `python run_decompose.py` | `results/pilot_3models/dev_variants/decomposed_{element}/{Imru2,Nabigha}/` + a 2nd v4_combined DEV run |
| Per-verse granularity grid (§3g) | `python run_per_verse.py --mode a` and `python run_per_verse.py --mode b` | `results/pilot_3models/per_verse/{mode_a,mode_b_<element>}/<poem>/` |
| Explanation-augmented sample (illustrative, not scored) | see inline example in `explanation_prompt.py`'s docstring | `results/pilot_3models/explanations_sample/Imru2/` |

Corresponding report generators: `decompose_report.py`, `per_verse_report.py`. Both re-slice/re-score directly from the raw manifests — never hand-transcribe a number from a previous run.

`run_per_verse.py` supports two flags useful for partial re-runs without re-spending on providers that already succeeded:
- `--providers anthropic google` — restrict to specific providers (e.g. retrying one provider's failed calls; retrying a `(provider, run_index)` cell **replaces** its manifest record rather than duplicating it).
- `--elements Kenning Trope` (mode `b` only) — restrict to specific elements.

---

## 6. The scoring harness

Never write a new one — every report in this project scores through the same three-layer stack:

1. **`parsing.py`** — turns raw JSONL model output into `{verse_no: {element: {exists, appearance}}}`. Malformed lines are flagged in `parse_errors`, never repaired. `parse_response()` is for the standard 4-element schema; `parse_response_single_element()` is for decomposed single-element runs.
2. **`analyze.load_all_runs(out_dir)`** (or `load_all_runs_single_element(out_dir, element)`) — reads a directory's `run_manifest.json` + raw files, returns `{provider: [{run_index, verses, parse_errors, meta}, ...]}`. **A manifest record's `error` field must stay `None` unless the entire call's raw output is unusable** — see `run_per_verse.py`'s docstring for why this matters when aggregating multiple API calls into one manifest record (a real bug, once hit and fixed, is documented there).
3. **`span_scoring.score_span_level(by_provider, gt_spans, n_verses, criterion)`** — the actual scorer. `criterion` is `"strict"` (literal span overlap) or `"token"` (word-level overlap ≥0.5, with a partial Arabic-clitic fix). Always compute both; they diverge meaningfully for Antonymy specifically (Arabic morphological variation).

For a decomposed/single-element directory, don't call `score_span_level` directly (it assumes the standard 4-key schema) — instead reuse `span_scoring.majority_exists_and_appearance()` + `span_matching.best_match()` directly, exactly as `decompose_report.py` and `per_verse_report.py` do.

**2-run majority is always the primary metric.** `analyze.run_consistency()` / `per_verse_report`'s per-element helpers compute run-to-run agreement — always report this alongside F1, and always report raw TP/FP/FN alongside precision/recall/F1 (small denominators are easy to misread as a big effect otherwise — see `PROJECT_STATE.md` §6 for two real incidents this caught).

---

## 7. Known pitfalls to check for on any new run

See `PROJECT_STATE.md` §6 for the full list with worked examples; the two most likely to bite a fresh reproduction attempt:

- **Never trust a single run.** Always compare 2 runs before drawing any comparative conclusion — a single lucky/unlucky run can double or halve an apparent F1.
- **A new poem larger than 81 verses may need a higher Claude `max_tokens`** (currently 16000) — verify `n_verses_parsed` in the parsed output matches the poem's actual verse count rather than assuming a 200 response means a complete one.

---

## 8. Where everything lands

```
results/pilot_3models/
  raw/, run_manifest.json          — original single-poem pilot (historical)
  dev_nabigha_baseline/             — baseline on Nabigha
  dev_variants/{variant}/{poem}/    — DEV prompt-tuning sweep
  dev_variants/decomposed_{el}/{poem}/  — §3f decomposition experiment
  test_final/{prompt}/{poem}/       — FROZEN TEST DATA
  per_verse/mode_a/{poem}/          — §3g Mode A (per-verse, all-4-elements)
  per_verse/mode_b_{el}/{poem}/     — §3g Mode B (per-verse, single-element)
  explanations_sample/Imru2/        — illustrative, not scored
  *.md, *.docx                      — generated reports (never hand-edited; regenerate via the corresponding build_*.py / *_report.py)
```

Every directory has a `run_manifest.json` (poem, provider, run_index, usage, error, raw_text_file path) and a `raw/` subdirectory with the actual model responses — these two together are sufficient to re-derive every number in every report.
