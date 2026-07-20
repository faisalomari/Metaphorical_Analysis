# Thesis Knowledge Base

**Thesis (as given):** "Exploring the Potential of LLMs to Identify Challenging Rhetorical Elements" — kenning, trope, antonymy, simile.

**Scope note (resolved):** the formally-approved v6 proposal (`הצעת תזה/Research Proposal_v6.docx`) was titled around implicit/hidden **simile** only. The thesis title and scope have since been changed — **confirmed by the user**: the four-element framework (kenning, trope, antonymy, simile) is the current, active thesis scope. `FirstStep`–`Forth_Step` are retained as historical/foundational work (to be archived in Phase 2), not superseded or invalidated.

Advisors: **Prof. Tsvi Kuflik** and **Prof. Ali Hussein** (University of Haifa, Dept. of Computer Science / Arabic Language). Ground-truth annotations throughout the repo ("Ali_ana", "تحليل د. علي") are Prof. Hussein's own manual analysis. The poem corpus and legacy rule-based system (REI) originate from Haifa's Arabic rhetoric database (`arabic-rhetoric.haifa.ac.il`), built in an earlier, related thesis by Heyam Abdalhade (`הצעת תזה/ex2.docx`) under the same two advisors.

---

## 1. Project Overview & Timeline

Git history (all dates confirmed via `git log`) plus file-internal timestamps give a reliable chronology:

| Date | Commit / artifact | Phase |
|---|---|---|
| 2024-12-23 → 2024-12-26 | `cb29056`, `2e41d5a` | Raw poem xlsx collection begins (`FirstStep/data/with|without`) |
| 2025-03-17 | `7fa1a5f` | Early cleanup |
| 2025-05-06 → 2025-05-15 | `c8f0ae7` … `07cc5ae` | **FirstStep**: AraBERT explicit-simile classifier trained |
| 2025-05-26 → 2025-06-10 | (untracked docs) | **Formal thesis proposal** written and approved (v0→v6, see §7) — overlaps directly with FirstStep training |
| 2025-08-12 | `77de412` | Progress (bridges FirstStep→SecondStep) |
| 2025-11-25 | `b144e0a`,`913f9ce`,`be2b462` | **SecondStep**: browser-automated ChatGPT rhetorical analysis (broad taxonomy) vs. Dr. Hussein ground truth |
| 2025-11-27 | `e02940b` "task3" | **ThirdStep** begins: manual 53-taxonomy ground truth (`Ali_ana`), reduced to 19 elements, ChatGPT web-UI "teach + classify" |
| 2025-12-03 → 2025-12-11 | `745b713`,`cfdd53b`,`b07c06d` | ThirdStep refinement |
| 2025-12-31 | `1633cf5` "forth step in progress" | **Forth_Step**: narrows to the exact 4 thesis elements (Trope/Simile/Kenning/Antonymy), moves from browser automation to the OpenAI API (`gpt-5.2`) |
| ~2026-01-19 onward (untracked, `previous_steps/`) | — | **Parallel/later exploratory branch**, never committed to git (`git status` shows it entirely untracked): per-element embedding classifiers (Kenayh/Majaz/Tashbeeh/Tebaq), GPT zero/few-shot experiments, and finally a multi-model voting ensemble (`multi_model_poetry_voting/`, dated 2026-04-01 — the latest work in the repo) |

**Narrative arc:** the project started as a narrow, rule-based/ML binary classifier for one element (simile/tashbeeh, matching the formally approved proposal), then broadened experimentally to a wide classical-rhetoric taxonomy (SecondStep, 27→15 elements), then narrowed back down to exactly the thesis's four target elements (Forth_Step onward), while a separate, untracked line of work (`previous_steps/`) re-ran the same four-element problem from scratch with three different methodological families (embeddings+classical ML, GPT zero/few-shot, and finally a 5-LLM voting ensemble) without ever connecting back to the earlier ThirdStep/Forth_Step ground truth.

---

## 2. Data Inventory

### 2.1 FirstStep — Simile (Tashbeeh) binary classification data
- `FirstStep/data/with/*.xlsx` (8 era-based files: abasy/amaoy/andalus/d_veterans/jahly/mamloky/unknown/veterans) — 29,264 positive (simile) verses total, schema `#, البيت, الشاعر, القصيدة, التعبير البلاغي, العنصر البلاغي المستعمل, العنصر البلاغي الثانوي`.
- `FirstStep/data/without/without1.xlsx` — 48,206 negative verses, same schema.
- `FirstStep/merged_poems_dataset_cleaned.csv` — final balanced training set, 58,528 rows (29,264/29,264), diacritics stripped. **Quality issue:** diacritic stripping raises duplicate count from 86 to 3,696 rows, and duplicates were never removed before the train/test split (leakage risk).
- Language: Classical/Modern Standard Arabic poetry, spanning Jahiliyya → Andalusian → Mamluk eras.

### 2.2 SecondStep — broad rhetorical taxonomy vs. expert ground truth
- Ground truth: **Dr. Ali Hussein's manual analysis**, 305 rows for Imru' al-Qais Poem 1 alone (`تحليل شعر امرؤ القيس/تحليل بلاغي.xlsx`, sheet "تحليل د. علي"), schema includes primary + secondary rhetorical element, theme, and an edit/delete review flag.
- 5 poets/poems covered: Imru' al-Qais (2 poems), Al-Nabigha Al-Dhubyani, Jarir, Abu Tammam.
- Taxonomy: 27 elements in `analysation1`, collapsed to 15 broader categories in `analysation2` (e.g. 5 jinās subtypes → 1 "الجناس").
- Automatic-vs-manual paired CSVs per poet (`csv_outputs/*_يدوي.csv` vs `*_آلي.csv`) — row counts vary substantially per poet (e.g. Imru' al-Qais 1: manual 305 vs automatic 119).

### 2.3 ThirdStep — 53→19 element ground truth
- `ThirdStep/elements1.csv` — 53-row master classical-rhetoric catalog (Arabic+English).
- `ThirdStep/elements2.csv` / `elemnts_from_poetries.csv` — reduced to 19 representative elements with per-poet worked examples.
- `ThirdStep/Ali_ana/original/*.xlsx` — richest ground truth in the repo: 5 poets (Abu Tammam 95, Nabigha 168, Imru1 306, Imru2 45, Jareer 167 rows), full 53-taxonomy labels + secondary element + theme.
- `ThirdStep/Ali_ana/*.xlsx` (top-level, same names) — **not a duplicate**: a lossy 2-column projection that silently drops verse-range/multi-verse annotation rows (e.g. `"37 - 38"`) that don't fit a single-verse schema.

### 2.4 Forth_Step — the exact 4 thesis elements
- `Forth_Step/Elements/{Trope,Simile,Kenning,Antonymy}.txt` — final element definitions (verbatim subset of ThirdStep's 19), each with Arabic/English name, definition, and 4-5 worked examples.
- `Forth_Step/Data/{Abu_tammam,Althobyane,Imru1,Imru2,Jareer}/` — per-poet `poetry.txt` (22-81 verses), `Analysation.jsonl` (GPT-5.2 output: `exists`/`appearance` per element per verse), plus a merged CSV.
- Note: `Imru2` = Imru' al-Qais's *poem 8* (not a second poet); `Althobyane` = Al-Nabigha Al-Dhubyani.
- Extra variants for consistency-checking: `Jareer/Analysation2.jsonl` (per-verse calls vs. batch), `Imru1/AnalysationPro.jsonl` (a second, more expensive model run).

### 2.5 previous_steps/poems — raw corpus + per-element datasets
- Raw scraped corpus (from `arabic-rhetoric.haifa.ac.il`, via browser-console scrapers in `previous_steps/poems/Scrappers/`): `all.csv` (5,065 labeled rows), `merged_poets_data.csv` (8,176 rows), `Analyzed_Poetry_Master.csv` (2,616 verse rows, no labels — the base corpus for later LLM pipelines).
- Per-element balanced datasets (all built as `{element}_only.csv` + `non_{element}_random_same_size.csv` pairs, embedded with OpenAI `text-embedding-3-large`, 3072-dim):

| Element | Positive rows | Notes |
|---|---|---|
| Kenayh (kenning) | 1,937 ("Full"), 1,415 ("Partly") | |
| Majaz (trope) | 557–842 across variants | Most duplicated dataset copies (4-6x, verified byte-identical) |
| Tashbeeh (simile) | 385–591 across variants | Most experimentally developed element |
| Tebaq (antonymy) | 387 ("Full"), 188 ("pos_only") | **Label leakage**: 5/387 (Full) and 6/188 (pos_only) "negative" rows are themselves tagged طباق |

### 2.6 previous_steps/poems_analysis — LLM ensemble outputs
- `GPT1/` — single-model experiments (gpt-4.1-mini → gpt-5.2 → gpt-5.2-pro) on a handful of individual poems.
- `multi_model_poetry_voting/outputs/` — the only pipeline run: **Imru' al-Qais Poem 8** (23 verses) × 4 elements × 5 models (GPT-5.2, Claude Sonnet, Gemini 2.5 Pro, Cohere Command-A, Cohere Aya). Raw/normalized/final CSVs + logs for every model/element combination.

---

## 3. Methods (chronological, by phase)

| Phase | Approach | Model(s) | Prompting |
|---|---|---|---|
| FirstStep | Fine-tuned transformer classifier | `aubmindlab/bert-base-arabertv2` (AraBERTv2) | N/A (supervised fine-tune, 5 epochs) |
| FirstStep (legacy) | Rule-based morphological analysis | AlKhalil2 analyzer (Java, ported to Python) | N/A — hand-coded simile-particle rules |
| SecondStep | LLM via **browser DOM automation** (not API) | ChatGPT (version unspecified) | One verse per message; later, batches of 3 elements per verse; F1 itself computed by *asking ChatGPT* to tally TP/FP/FN in a second conversation (`f_score_prompt.txt`) — not computed in code |
| ThirdStep | LLM via browser DOM automation | ChatGPT | "Teach" the model all 19 element definitions first (`portions_script.js`), then classify one verse × one element per message |
| Forth_Step | LLM via **official OpenAI API** | `gpt-5.2` (+ one `gpt-5.2-pro` comparison run) | System prompt = intro + 4 element definitions + strict JSON-per-verse schema; two variants tested: whole-poem-in-one-call (`code1.py`) vs. one-call-per-verse (`code2.py`) |
| previous_steps (embeddings) | Embedding + classical ML | OpenAI `text-embedding-3-large` → LogisticRegression / RandomForest / XGBoost / TabPFN, PCA swept at {16,32,64,128,512,None} | N/A |
| previous_steps (LLM zero/few-shot) | Direct LLM classification | gpt-4o, gpt-4.1, gpt-5-mini, gpt-5.2, gpt-5.2-pro, ArabianGPT-0.3B (fine-tuned), AraGPT2-base (fine-tuned), AraBERT-large (fine-tuned) | Zero-shot, few-shot (up to full-training-set-in-context), English-translation pipeline |
| previous_steps/poems_analysis | **5-model voting ensemble** | GPT-5.2, Claude Sonnet 4.6, Gemini 2.5 Pro, Cohere Command-A, Cohere Aya (Qwen3-max coded but broken — bad API key) | Per-element structured-JSON prompts with confidence (numeric or banded by provider); majority vote with confidence tiebreak; winning model re-queried for a clean Arabic explanation |

---

## 4. Results — every metric found

### 4.1 FirstStep (Simile, binary, held-out test n=54,490)
- **Accuracy 0.9571**, class-balanced P/R/F1 ≈ 0.955–0.957 both classes.
- Confusion matrix: TN 26,000 / FP 1,245 / FN 1,090 / TP 26,155.
- Caveat: only ~5% of data (2,926 rows) was used for training; the rest is test — an unusually train-starved split, and undetected duplicate leakage (see §2.1).

### 4.2 SecondStep (broad taxonomy, ChatGPT vs. Dr. Hussein, via `f_score_prompt.txt`)

| Poet/poem | Macro F1 | Micro F1 |
|---|---|---|
| Imru' al-Qais 1 | 0.281 | 0.549 |
| Al-Nabigha Al-Dhubyani | 0.281 | 0.620 |
| Jarir | 0.216 | 0.381 |
| Abu Tammam | 0.237 | 0.416 |

Per-element breakdown (Imru' al-Qais 1 example): Simile (تشبيه) F1 0.833 (best), Trope (مجاز) F1 0.628, Kenning (كناية) F1 0.532, several minor jinās/rhetorical categories at F1 0.0. **Caveat: these F1 numbers were computed by asking ChatGPT itself to tally TP/FP/FN — no code-based verification exists.**

### 4.3 ThirdStep/Forth_Step
**No computed evaluation metrics exist.** A comparison tool (`Forth_Step/Data/compare.py`) was built specifically to diff batch-vs-per-verse and model-vs-model JSONL outputs, but no output artifacts (`comparison_summary.json` etc.) were ever committed — spot-checks show real disagreements (e.g. Jarir verse 4, Imru1 verse 2) that were never quantified.

### 4.4 previous_steps per-element classifiers

**Only completed embedding+TabPFN result (any element):** Majaz (trope) — Accuracy 0.6746, F1 0.6727, ROC-AUC 0.7189. Kenayh, Tashbeeh, and Tebaq's identical TabPFN notebook cells all **stalled with zero output**. The full LogisticRegression/RandomForest/XGBoost × 6-PCA-dimension sweep (`LR.py`) was never logged to disk for **any** element — results were printed to a terminal that wasn't captured.

**Majaz (trope) — GPT zero/few-shot:**

| Model | Method | n | Accuracy |
|---|---|---|---|
| gpt-5-mini | zero-shot | 80 | 0.575 |
| gpt-4.1 | zero-shot + CoT | 160 | 0.506 |
| gpt-5.2 | few-shot (full train set in context) | 160 | 0.581 |
| gpt-5.2 | zero-shot, positive-only | 50 | 0.86 recall |
| gpt-5.2 | zero-shot, full dataset | 1,594 | 0.543 |
| gpt-4o (translated to English) | zero-shot | 80 | 0.575 |

CAMeL-Tools symbolic/hybrid features topped out at 0.553-0.555 accuracy; feature fusion never beat the single best feature group.

**Tashbeeh (simile) — GPT and fine-tuning (best-developed element):**

| Model | Method | n | Accuracy |
|---|---|---|---|
| **gpt-5.2-pro** | **zero-shot** | 55 | **0.8727 (best LLM result in the whole repo)** |
| gpt-5.2 | (provenance undocumented) | 218 | 0.7615 |
| gpt-4o-mini | few-shot (8 examples) | 218 | 0.7523 |
| ArabianGPT-0.3B | fine-tuned, 4 epochs | 218 | 0.7385 (best local fine-tune) |
| AraGPT2-base | fine-tuned, 20 epochs | 218 | 0.6972 |
| AraBERT-large | fine-tuned, 20 epochs | 178 | **0.50 — collapsed classifier (predicts positive for everything); not a real result** |

**Kenayh (kenning) and Tebaq (antonymy): zero recoverable quantitative results anywhere in the repo.** Tebaq additionally has no LLM experiment at all (no `api/` folder); its "FullEmbedding" pipeline never ran due to a copy-paste path bug (hardcoded Tashbeeh filenames).

### 4.5 previous_steps/poems_analysis (multi-model voting)
No ground-truth comparison exists — the ensemble only resolves disagreement *between* the 5 LLMs, never against Dr. Hussein's human labels (which do exist for this exact poem in `previous_steps/poems/all.csv`). Qualitative finding: the 5 models frequently disagree on span and even label; Claude wins the "selected/highest-confidence" role most often.

---

## 5. Code Inventory (by phase, one line each)

**FirstStep:** `clean.py` (diacritic stripping), `main1.py`/`main2.py` (rule-based/NER marker extraction), `merge_2csv.py` (balanced dataset builder), `model1.py`/`*.ipynb` (AraBERT fine-tune), `t.java`+Python port (legacy rule-based detector), `xlsx_csv.py`/`cols_rm.py` (format utilities).

**SecondStep:** `{poet}.js` (ChatGPT browser-automation senders, one per poet), `portions_script.js` (re-injects manual/automatic comparison data for F1 scoring), `tables_prompt.txt` (DOM table→CSV scraper bookmarklet), `main.py`/`main2.py` (xlsx→csv, then pairs manual/automatic files into portioned txt).

**ThirdStep:** `elements_training_txt.py` (builds the 19-element teaching text), `poem_script.js`/`portions_script.js` (browser automation), `xlsx2csv.py`.

**Forth_Step:** `code1.py` (whole-poem-per-call GPT-5.2), `code2.py` (per-verse-per-call, for consistency comparison), `jsonl2csv.py`, `numbering.py`, `compare.py` (unused diff tool).

**previous_steps/poems/{element}:** `embeddings.py` (OpenAI embedding fetch), `LR.py` (LogisticRegression/RandomForest/XGBoost × PCA-dim sweep, despite the filename), `main.ipynb` (TabPFN + classifier comparison), plus per-element `api/*.ipynb` (GPT zero/few-shot), `hybrid_features/main.ipynb` (CAMeL-Tools symbolic features), and (Tashbeeh only) `ArabianGPT/`, `FineTune/`, `all_models/` (local fine-tunes).

**previous_steps/poems_analysis/multi_model_poetry_voting:** full installable package — `src/models/{provider}_model.py` (one wrapper per LLM), `src/pipeline.py` (orchestration), `src/voting.py` (majority vote + confidence tiebreak), `src/parsing.py` (JSON/label normalization), `run_analysis.py` (CLI entrypoint).

**previous_steps/poems (data collection):** `Scrappers/*.js` (browser-console scrapers driving the Haifa Arabic-rhetoric web app), `Part1/*.py` (raw corpus merging).

**Duplicated/dead code:** the rule-based simile detector exists as `t.java`, a Python port (`main1.py`), and a docx that's just a copy of the Java source — three copies of the same logic. `Kenayh/FullEmbedding/embeddings.py` and `Tebaq/FullEmbedding/embeddings.py` are unedited copy-pastes of Tashbeeh's script (still reference `tashbeeh_dataset.csv`) and never successfully ran.

---

## 6. Writing — state of thesis drafts

- **`הצעת תזה/` (Hebrew: "Thesis Proposal")** — 9 sequential drafts (v0→v6) written May 26 – June 10, 2025, converging on a final approved title: *"Combining Classical Rhetorical Theory with State-of-the-Art AI Techniques for Discovering Hidden Tashbīh in Arabic Poetry as a Case Study."* Central RQ: can ML/NLP detect **implicit** (hidden) simile beyond what the legacy rule-based REI system catches. Planned methodology: manually transform explicit-simile verses into implicit form, build a 3-way dataset (explicit/implicit/none), fine-tune AraBERT, evaluate with accuracy/P/R/F1 + qualitative error analysis.
- **`אישור הצעת תזה.pdf`** — the "approval" document is actually a **blank, unsigned form template** (no filled fields, no recorded approval date) — this is a gap, not a completed record (see §7).
- **No formal thesis chapters/manuscript were found anywhere in the repo** — only the proposal documents. No draft introduction, literature review chapter, results chapter, etc.
- **`implicit simile - gpt5.pptx`** — a concrete pilot directly testing the proposal's planned methodology: 10 verses manually stripped of their simile particle, fed to GPT-5, asked to recover Tenor/Vehicle/Ground of the now-implicit simile.

---

## 7. Gaps, Inconsistencies, and Things to Flag

1. **Scope discrepancy — resolved.** The formally approved proposal (v6) was scoped to implicit **simile only**, with no amendment document in the repo; the user has confirmed the thesis title/scope changed since and the four-element (kenning/trope/antonymy/simile) framing is the current, active target. `FirstStep`–`Forth_Step` are to be archived as historical foundation, not discarded.
2. **~~Exposed API key~~ — already flagged separately and a background task was spawned for it**: `Forth_Step/GPT/key.txt` contains a live-looking OpenAI key, committed to git in `1633cf5`.
3. **Other API keys/tokens are NOT git-tracked** (confirmed via `git ls-files`) but exist in plaintext across `previous_steps/` (a Hugging Face token repeated in every `LR.py`, plus 5 provider keys under `multi_model_poetry_voting/keys/`). Since `previous_steps/` is currently untracked, these must be gitignored **before** Phase 2 reorganization commits anything, to avoid accidentally introducing them into history.
4. **No evaluation code exists for ThirdStep/Forth_Step** despite a purpose-built `compare.py` — real disagreements were spot-checked manually but never quantified.
5. **Kenayh and Tebaq have essentially zero usable results** — the weakest-covered elements by far, vs. Tashbeeh (most developed, best LLM result 87.3% with gpt-5.2-pro) and Majaz (second most developed).
6. **The three methodological lines never talk to each other**: (a) ThirdStep/Forth_Step's JSONL pipeline, (b) previous_steps' per-element embedding classifiers, and (c) previous_steps/poems_analysis' multi-model voting ensemble all attack the same 4-element problem independently, with no shared code, dataset format, or metrics convention — and none of them scores against the rich Dr. Hussein ground truth that exists for the exact same poems.
7. **The multi-model voting pipeline (architecturally the most mature code in the repo) was only ever run on one poem** (Imru' al-Qais Poem 8, 23 verses) and has no evaluation harness at all, despite matching ground truth existing right next to it.
8. **Data quality issues**: FirstStep duplicate leakage after diacritic stripping (§2.1); Tebaq negative-set label leakage (§2.5); `Ali_ana` top-level xlsx files silently drop multi-verse annotation rows (§2.3); several Majaz/Tashbeeh dataset copies are exact duplicates across 4-6 folders.
9. **`spam.cs`** at repo root is an unrelated stray file (hardcoded admin/1234 login check, C#) — not part of the thesis, likely safe to remove in Phase 2.
10. **`Arabic NLP overview.pptx`** lists a different supervisor (Dr. Adir Solomon) — it's coursework from an unrelated class, not a thesis artifact.

---

## Decisions Confirmed With User (2026-07-20)

1. **Scope**: Four-element framework (kenning, trope, antonymy, simile) is the current, active thesis scope. The title changed from the original v6 proposal to this. `FirstStep`–`Forth_Step` are kept, not discarded.
2. **previous_steps status**: To be treated as the active line of work; `FirstStep`–`Forth_Step` archived as historical/foundational.
3. **API keys**: All plaintext keys/tokens across `previous_steps/` will be replaced with `.env`-style placeholders as part of Phase 2, in addition to rotating the one already exposed in git history (`Forth_Step/GPT/key.txt`).

These will shape the Phase 2 folder-structure proposal and enhancement plan.
