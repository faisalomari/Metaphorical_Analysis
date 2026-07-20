from __future__ import annotations

import argparse
from pathlib import Path

from config import DEFAULT_OUTPUT_DIR, SUPPORTED_ELEMENTS, SUPPORTED_MODELS
from src.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze one rhetorical element on one poem CSV using multi-model voting."
    )
    parser.add_argument("--input_csv", required=True, help="Path to the input poem CSV.")
    parser.add_argument(
        "--element",
        required=True,
        choices=sorted(SUPPORTED_ELEMENTS),
        help="Rhetorical element to analyze.",
    )
    parser.add_argument(
        "--output_dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for raw, normalized, final, and log outputs.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max_retries", type=int, default=2)
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gpt", "claude", "gemini"],
        help="Subset of models to run. Supported: gpt claude gemini command_a aya qwen",
    )
    parser.add_argument("--limit", type=int, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    models = [name.strip().lower() for name in args.models]
    unknown = [name for name in models if name not in SUPPORTED_MODELS]
    if unknown:
        parser.error(f"Unsupported model(s): {', '.join(unknown)}")

    run_pipeline(
        input_csv=Path(args.input_csv).expanduser().resolve(),
        element=args.element,
        output_dir=Path(args.output_dir).expanduser().resolve(),
        temperature=args.temperature,
        max_retries=args.max_retries,
        selected_models=models,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
