from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from config import (
    CLAUDE_MODEL_FALLBACKS,
    DEFAULT_MODEL_NAMES,
    ELEMENTS_DIR,
    FINAL_DIRNAME,
    KEY_FILES,
    LOGS_DIRNAME,
    NORMALIZED_DIRNAME,
    PROMPTS_DIR,
    QWEN_BASE_URL,
    RAW_DIRNAME,
)
from src.io_utils import (
    append_jsonl,
    dataframe_to_verse_records,
    ensure_dir,
    load_api_key,
    load_poem_csv,
    save_csv,
)
from src.logging_utils import setup_logger
from src.models import (
    ClaudeModel,
    CohereAyaModel,
    CohereCommandModel,
    GeminiModel,
    OpenAIModel,
    QwenModel,
)
from src.parsing import build_error_result, parse_model_response
from src.prompt_builder import (
    build_explanation_user_prompt,
    build_labeling_user_prompt,
    load_element_definition,
    load_system_prompt,
)
from src.schemas import ModelResult
from src.voting import choose_vote


def _build_model_clients(selected_models: Iterable[str]) -> dict[str, object]:
    clients: dict[str, object] = {}
    for provider in selected_models:
        api_key = load_api_key(KEY_FILES[provider])
        model_name = DEFAULT_MODEL_NAMES[provider]
        if provider == "gpt":
            clients[provider] = OpenAIModel(model_name=model_name, api_key=api_key)
        elif provider == "claude":
            clients[provider] = ClaudeModel(
                model_name=model_name,
                api_key=api_key,
                fallback_model_names=CLAUDE_MODEL_FALLBACKS,
            )
        elif provider == "gemini":
            clients[provider] = GeminiModel(model_name=model_name, api_key=api_key)
        elif provider == "command_a":
            clients[provider] = CohereCommandModel(
                model_name=model_name,
                api_key=api_key,
            )
        elif provider == "aya":
            clients[provider] = CohereAyaModel(
                model_name=model_name,
                api_key=api_key,
            )
        elif provider == "qwen":
            clients[provider] = QwenModel(
                model_name=model_name,
                api_key=api_key,
                base_url=QWEN_BASE_URL,
            )
    return clients


def _safe_stem(path: Path) -> str:
    return path.stem.replace(" ", "_")


def _prepare_run_paths(
    base_run_name: str,
    selected_models: list[str],
    raw_dir: Path,
    normalized_dir: Path,
    final_dir: Path,
    logs_dir: Path,
) -> tuple[str, dict[str, Path], Path, Path, Path]:
    run_name = base_run_name
    while True:
        raw_paths = {
            provider: raw_dir / f"{run_name}__{provider}.jsonl"
            for provider in selected_models
        }
        normalized_path = normalized_dir / f"{run_name}__normalized.csv"
        final_path = final_dir / f"{run_name}__final.csv"
        log_path = logs_dir / f"{run_name}.log"

        try:
            for path in [*raw_paths.values(), normalized_path, final_path, log_path]:
                if path.exists():
                    path.unlink()
            return run_name, raw_paths, normalized_path, final_path, log_path
        except PermissionError:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            run_name = f"{base_run_name}__{timestamp}"


def _label_with_retries(
    client,
    provider: str,
    verse: str,
    element: str,
    definition: str,
    system_prompt: str,
    temperature: float,
    max_retries: int,
    logger,
) -> ModelResult:
    user_prompt = build_labeling_user_prompt(
        verse=verse,
        element=element,
        definition=definition,
        provider=provider,
    )
    raw_text = ""
    last_error = "unknown_error"
    for attempt in range(1, max_retries + 2):
        try:
            raw_text = client.label_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            return parse_model_response(
                raw_text=raw_text,
                provider=provider,
                model_name=client.model_name,
                attempt_count=attempt,
            )
        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "Labeling failure | provider=%s | attempt=%s | error=%s",
                provider,
                attempt,
                last_error,
            )

    return build_error_result(
        raw_text=raw_text,
        provider=provider,
        model_name=client.model_name,
        error_message=last_error,
        attempt_count=max_retries + 1,
    )


def _generate_final_explanation(
    client,
    verse: str,
    element: str,
    definition: str,
    voted_label: str,
    final_span: str,
    system_prompt: str,
    temperature: float,
    logger,
) -> str:
    user_prompt = build_explanation_user_prompt(
        verse=verse,
        element=element,
        definition=definition,
        selected_label=voted_label,
        selected_span=final_span,
    )
    try:
        return client.explain_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
    except Exception as exc:
        logger.warning(
            "Explanation failure | provider=%s | error=%s",
            client.provider,
            str(exc),
        )
        return ""


def run_pipeline(
    input_csv: Path,
    element: str,
    output_dir: Path,
    temperature: float,
    max_retries: int,
    selected_models: list[str],
    limit: int | None = None,
) -> None:
    output_dir = ensure_dir(output_dir)
    raw_dir = ensure_dir(output_dir / RAW_DIRNAME)
    normalized_dir = ensure_dir(output_dir / NORMALIZED_DIRNAME)
    final_dir = ensure_dir(output_dir / FINAL_DIRNAME)
    logs_dir = ensure_dir(output_dir / LOGS_DIRNAME)

    base_run_name = f"{_safe_stem(input_csv)}__{element}"
    run_name, raw_paths, normalized_path, final_path, log_path = _prepare_run_paths(
        base_run_name=base_run_name,
        selected_models=selected_models,
        raw_dir=raw_dir,
        normalized_dir=normalized_dir,
        final_dir=final_dir,
        logs_dir=logs_dir,
    )
    logger = setup_logger(log_path)

    definition = load_element_definition(element=element, elements_dir=ELEMENTS_DIR)
    labeling_system_prompt = load_system_prompt(PROMPTS_DIR / "system_labeling.txt")
    explanation_system_prompt = load_system_prompt(PROMPTS_DIR / "system_explanation.txt")

    logger.info("Starting run | input_csv=%s | element=%s", input_csv, element)

    df = load_poem_csv(path=input_csv, limit=limit)
    verse_records = dataframe_to_verse_records(df)
    clients = _build_model_clients(selected_models)
    normalized_rows: list[dict] = []
    final_rows: list[dict] = []

    for record in tqdm(verse_records, desc=f"{element} verses"):
        model_results: dict[str, ModelResult] = {}

        for provider in selected_models:
            result = _label_with_retries(
                client=clients[provider],
                provider=provider,
                verse=record.combined_verse,
                element=element,
                definition=definition,
                system_prompt=labeling_system_prompt,
                temperature=temperature,
                max_retries=max_retries,
                logger=logger,
            )
            model_results[provider] = result

            append_jsonl(
                raw_paths[provider],
                {
                    "verse_index": record.verse_index,
                    "combined_verse": record.combined_verse,
                    "rhetorical_element": element,
                    **result.to_dict(),
                },
            )

        vote = choose_vote(model_results)
        final_explanation = ""
        if vote.selected_provider:
            final_explanation = _generate_final_explanation(
                client=clients[vote.selected_provider],
                verse=record.combined_verse,
                element=element,
                definition=definition,
                voted_label=vote.voted_label,
                final_span=vote.final_span,
                system_prompt=explanation_system_prompt,
                temperature=temperature,
                logger=logger,
            )

        normalized_row = dict(record.original_row)
        normalized_row["rhetorical_element"] = element
        final_row = dict(record.original_row)
        final_row["rhetorical_element"] = element

        for provider in selected_models:
            result = model_results[provider]
            normalized_row[f"{provider}_label"] = result.label
            normalized_row[f"{provider}_span"] = result.span
            normalized_row[f"{provider}_confidence"] = result.confidence
            normalized_row[f"{provider}_reasoning"] = result.reasoning
            normalized_row[f"{provider}_status"] = result.status
            normalized_row[f"{provider}_model_name"] = result.model_name
            normalized_row[f"{provider}_error"] = result.error_message

            final_row[f"{provider}_label"] = result.label
            final_row[f"{provider}_span"] = result.span
            final_row[f"{provider}_confidence"] = result.confidence
            final_row[f"{provider}_reasoning"] = result.reasoning

        final_row["voted_label"] = vote.voted_label
        final_row["selected_model_for_explanation"] = vote.selected_provider
        final_row["selected_model_name"] = vote.selected_model_name
        final_row["selected_confidence"] = vote.selected_confidence
        final_row["final_span"] = vote.final_span
        final_row["vote_reason"] = vote.vote_reason
        final_row["final_explanation"] = final_explanation

        normalized_rows.append(normalized_row)
        final_rows.append(final_row)

        save_csv(normalized_path, normalized_rows)
        save_csv(final_path, final_rows)

    logger.info(
        "Completed run | verses=%s | normalized_path=%s | final_path=%s",
        len(normalized_rows),
        normalized_path,
        final_path,
    )
