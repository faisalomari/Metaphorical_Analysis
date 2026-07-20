# Metaphorical Analysis — Rhetorical Elements in Classical Arabic Poetry

Master's thesis project: exploring the potential of LLMs to identify four challenging rhetorical
elements in classical Arabic poetry — **kenning** (كناية), **trope** (مجاز), **antonymy** (طباق),
and **simile** (تشبيه).

See [THESIS_KNOWLEDGE.md](THESIS_KNOWLEDGE.md) for the full project history, data/methods/results
inventory, and known gaps. See [ENHANCEMENT_PLAN.md](ENHANCEMENT_PLAN.md) for the prioritized
roadmap of next steps.

## Setup

Copy `.env.example` to `.env` and fill in your own API keys (OpenAI, Anthropic, Gemini, Cohere,
Qwen, Hugging Face) before running anything under `experiments/`. Never commit `.env` or any
`key.txt`/`token.txt`/`keys/` file — they're gitignored.

## Layout

- **`data/`** — datasets, ground truth, and canonical element definitions.
  - `raw/haifa_corpus/` — the scraped poem + rhetorical-analysis corpus from the University of
    Haifa Arabic rhetoric database, and `raw/scrapers/` — the browser-console scripts that built it.
  - `ground_truth/ali_ana/` — Prof. Ali Hussein's manual expert annotations (53-element taxonomy),
    the richest ground truth in the project.
  - `elements/` — canonical definitions for the 4 target elements.
  - `processed/{kenning,trope,simile,antonymy}/` — balanced positive/negative datasets per element,
    ready for modeling.

- **`experiments/`** — active modeling work.
  - `classifiers/{kenning,trope,simile,antonymy}/` — embedding + classical ML (LogisticRegression/
    RandomForest/XGBoost/TabPFN) and LLM zero-/few-shot experiments, one folder per element.
  - `llm_pipelines/gpt1_single_model/` — early single-model GPT experiments.
  - `llm_pipelines/multi_model_voting/` — the 5-LLM ensemble voting pipeline (most architecturally
    mature code in the repo; currently only run on one poem, no ground-truth evaluation yet).

- **`results/multi_model_voting/`** — raw/normalized/final outputs from the voting pipeline.

- **`writing/`** — `proposal/` (the formal research proposal, drafts v0→v6) and `pilots/` (small
  exploratory decks, e.g. the implicit-simile GPT-5 pilot).

- **`literature/`** — `related_work/` (external papers) and `authored/` (papers by the thesis
  advisors, directly foundational to this work).

- **`archive/`** — the project's earlier phases (`FirstStep` → `Forth_Step`), kept intact as
  historical/foundational reference. `FirstStep` trained the original AraBERT simile classifier;
  `SecondStep`–`Forth_Step` progressively developed and narrowed the rhetorical-element taxonomy
  down to the current 4-element scope. Not superseded — the ground truth and definitions from
  this period are still in active use (copied into `data/`).

## Known gaps (see THESIS_KNOWLEDGE.md §7 for full detail)

- No pipeline in the repo currently scores its own output against the available human ground
  truth (Ali Hussein's annotations exist for poems the multi-model voting pipeline already ran on).
- Kenning and antonymy have far weaker experimental coverage than trope and simile.
- One OpenAI API key was found committed to git history (`Forth_Step/GPT/key.txt`) — rotate it if
  you haven't already.
