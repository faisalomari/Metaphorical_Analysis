from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"multi_model_poetry_voting::{log_path}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
