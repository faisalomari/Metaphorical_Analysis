# Multi-Model Poetry Voting

This folder contains a clean script-based pipeline for analyzing one Arabic rhetorical element at a time on one poem CSV, using multiple providers:

- OpenAI GPT
- Anthropic Claude
- Google Gemini
- Cohere Command A
- Cohere Aya Expanse
- Alibaba Qwen

The pipeline:

1. Loads a poem CSV.
2. Combines `Sadr` + `Ajuz` into one verse string.
3. Sends each verse to each selected model for one rhetorical element only.
4. Saves raw and normalized per-model outputs.
5. Performs voting on the label.
6. Chooses the highest-confidence model among those supporting the final label.
7. Calls only that selected model again to produce the final Arabic explanation.
8. Saves the merged final CSV plus logs.

## Folder Layout

```text
multi_model_poetry_voting/
  README.md
  requirements.txt
  config.py
  run_analysis.py
  prompts/
    system_labeling.txt
    system_explanation.txt
  elements/
    Trope.txt
    Similie.txt
    Kenning.txt
    Antonymy.txt
  keys/
    openai_key.txt
    claude_key.txt
    gemini_key.txt
    cohere_key.txt
    qwen_key.txt
  src/
    __init__.py
    io_utils.py
    prompt_builder.py
    parsing.py
    voting.py
    explanation.py
    pipeline.py
    schemas.py
    logging_utils.py
    models/
      __init__.py
      base_model.py
      openai_model.py
      claude_model.py
      gemini_model.py
  outputs/
    raw/
    normalized/
    final/
    logs/
```

## Required Files

Place API keys as UTF-8 text files inside:

- `keys/openai_key.txt`
- `keys/claude_key.txt`
- `keys/gemini_key.txt`
- `keys/cohere_key.txt`
- `keys/qwen_key.txt`

The code strips whitespace safely and never hardcodes secrets.

Notes:

- `command_a` and `aya` both use the same Cohere API key file: `keys/cohere_key.txt`
- `qwen` uses `keys/qwen_key.txt`
- Qwen defaults to the international OpenAI-compatible endpoint:
  `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- If you need a different Qwen endpoint, set the `QWEN_BASE_URL` environment variable before running.

## Input CSV Expectations

The input poem CSV is expected to include at least:

- `Poet`
- `Poem Title`
- `Sadr`
- `Ajuz`

`Sadr` and `Ajuz` are combined into `combined_verse` for analysis. All original columns are preserved in outputs.

If your file has extra columns, they are kept.

## Supported Elements

Use exactly one of:

- `Trope`
- `Similie`
- `Kenning`
- `Antonymy`

Important: `Similie` remains spelled exactly this way for compatibility with your existing project.

## Install

```bash
pip install -r requirements.txt
```

## Run

From inside `multi_model_poetry_voting/`:

```bash
python run_analysis.py --input_csv ..\Imru_Al_Qais_Poem_8.csv --element Trope
```

Example with options:

```bash
python run_analysis.py ^
  --input_csv ..\abu_tammam_Poem_2.csv ^
  --element Kenning ^
  --models gpt claude gemini command_a aya qwen ^
  --temperature 0 ^
  --max_retries 2 ^
  --limit 10
```

Optional arguments:

- `--output_dir`
- `--temperature`
- `--max_retries`
- `--models`
- `--limit`

Default behavior:

- If you do not pass `--models`, the script runs the original default set:
  `gpt claude gemini`
- To include the three added models, pass them explicitly:
  `--models gpt claude gemini command_a aya qwen`

## Output Files

Outputs are written under `outputs/` by default:

- `outputs/raw/`
  Raw JSONL per provider, one record per verse attempt.
- `outputs/normalized/`
  Parsed and normalized CSV containing one row per verse and per-model fields.
- `outputs/final/`
  Final merged CSV with voting, selected model, final span, and final Arabic explanation.
- `outputs/logs/`
  Run log file with API failures, parsing failures, retries, and skips.

## Labeling Schema

Each provider is normalized into this shape:

```json
{
  "label": "yes",
  "span": "النص المستخرج",
  "confidence": 0.87,
  "reasoning": "short explanation",
  "raw_response": "...",
  "model_name": "...",
  "provider": "...",
  "status": "ok"
}
```

Normalization rules:

- `label` is normalized to `yes` or `no`.
- `confidence` is clamped to `0.0`-`1.0`.
- If a model returns `0`/`1`, `true`/`false`, percent-like values, or alternate strings, they are normalized in code.
- If `label` is `no`, `span` is forced to an empty string.
- Failures are stored with `status="error"` and the pipeline continues.

## Voting Logic

Voting is done per verse:

1. Majority vote across all selected models on the normalized label.
2. If all three disagree or there is otherwise no majority, the label from the highest-confidence model wins.
3. The selected model for explanation is the highest-confidence model among those that support the final chosen label.
4. The final span is taken from that selected model.
5. Only that same selected model is called again to generate the final Arabic explanation.

## Explanation Logic

The explanation prompt includes:

- the full verse
- the selected rhetorical element
- the element definition text from `elements/<Element>.txt`
- the voted label
- the selected span

The explanation response is plain Arabic text only, intended to be concise and academically useful.

## Notes / Assumptions

- UTF-8 is used throughout.
- The pipeline reuses the old prompt style conceptually: element definition file, explicit verse, strict JSON request, short reasoning, and extracted span.
- Cost tracking is not fully implemented for all providers, but logging is structured so cost tracking can be added later.
- The pipeline saves partial progress after each verse so a single failure does not lose the run.
- Gemini, Qwen, Command A, and Aya use banded confidence prompts internally and are normalized back into numeric scores in the final CSV.
