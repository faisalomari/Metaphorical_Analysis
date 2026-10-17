"""Phase 6 constants. Imports Phase 5 modules unchanged (same convention CLAUDE.md
already uses for Phase 2 importing Phase 1 modules) rather than duplicating them --
Phase 5's targets.json, splits/*.json, data_io.py, dataset.py, splitting.py,
metrics_utils.py, baselines.py, normalize.py, train.py are all reused as-is."""
import os
import sys
from pathlib import Path

PHASE6_DIR = Path(__file__).resolve().parent
PHASE5_DIR = PHASE6_DIR.parents[0] / "phase5_local_ft"
if str(PHASE5_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE5_DIR))

os.environ.setdefault("HF_HOME", str(PHASE6_DIR / "hf_cache"))
# NOTE: huggingface_hub resolves its cache-directory constant the first time any of its
# submodules is imported, so this setdefault only takes effect in a process where nothing
# has imported transformers/huggingface_hub yet. In practice several Step-0/Step-1 smoke
# tests imported transformers before phase6_config (direct `python train_*.py` invocations),
# so Qwen2.5-3B/aragpt2-mega/bert-large-arabertv02 ended up in the user's shared default
# cache (~/.cache/huggingface) instead of here -- outside the repo either way, so "no
# weights/caches in git" still holds; documented rather than fixed mid-stream to avoid a
# second multi-GB re-download of models already fetched. No HF token is used either way.

import json

import phase5_config as p5  # noqa: E402  (Phase 5 module, path-inserted above)

# ---- Phase 5 targets/splits/best-model-per-target, reused unchanged for comparability ----
with open(p5.CONFIG_DIR / "targets.json", encoding="utf-8") as _f:
    TARGETS_BY_LEVEL = {t["level"]: t for t in json.load(_f)["targets"]}
SPLITS_DIR = p5.SPLITS_DIR
SEEDS = p5.SEEDS
THRESHOLD_GRID = p5.THRESHOLD_GRID
MAX_LEN_BASE = p5.MAX_LEN  # 32, Phase 5's verse-alone max_len
# L1 context-window max_len: p99 token length (prev+target+next, 3 Phase5 tokenizers) was
# 68-69 (max 111, one outlier) -- see results/phase6_stronger_ft/l1_context_token_lengths.json.
# 96 covers p99 with the same ~40% margin convention Phase5 used for MAX_LEN=32 over its own
# p99 of 20-23. ~3x Phase5's verse-alone length -> ~3x the per-epoch compute ("cost") for L1.
MAX_LEN_CONTEXT = 96

# L2 "stronger training recipe" hyperparameters (cosine schedule + layer-wise LR decay +
# longer training) -- early stopping on val still applies, this just raises the epoch ceiling
# and patience so cosine annealing has room to actually anneal.
L2_COSINE_MAX_EPOCHS = 30
L2_COSINE_PATIENCE = 6
L2_LLRD_DECAY = 0.95  # per-layer multiplier, deeper layers get higher lr (standard BERT LLRD)
L2_WARMUP_RATIO = 0.06

TARGET_LEVELS = ["very_easy", "easy", "medium", "hard", "very_hard"]

# Phase 5's best model per target (docs/phase5/LOCAL_FT_RESULTS.md S2 table) --
# L1/L2 ablation (Step 1) is run against THIS model per target, per task instruction
# ("change one thing at a time against the Phase 5 best model per target").
PHASE5_BEST_MODEL = {
    "very_easy": "marbert",
    "easy": "marbert",
    "medium": "marbert",
    "hard": "marbert",
    "very_hard": "camelbert_ca",
}
PHASE5_BEST_F1_S2 = {  # mean F1 across 3 seeds, docs/phase5/LOCAL_FT_RESULTS.md S2 table
    "very_easy": 0.282, "easy": 0.189, "medium": 0.562, "hard": 0.275, "very_hard": 0.217,
}

ENCODER_MODELS = dict(p5.MODELS)  # camelbert_ca, arabert_v2, marbert -- unchanged ids

# L3 "bigger model" candidates (chosen + verified ungated in Step 0/Step 1, see
# docs/phase6/STRONGER_FT_RESULTS.md for the availability/quality check):
#  - qwen2p5_3b: general multilingual decoder, strong Arabic coverage, ungated. QLoRA 4-bit.
#  - arabert_large: large Arabic encoder (aubmindlab's only public "large" BERT), fp16 full
#    fine-tune, same recipe family as Phase 5's base encoders.
# aragpt2_mega (aubmindlab/aragpt2-mega, ~1.46B, Arabic-specific GPT2-architecture decoder)
# was smoke-tested and DROPPED: its Conv1D-based layers under bitsandbytes 4-bit quantization
# ran ~4x slower per optimizer step than Qwen2.5-3B despite being less than half the
# parameter count (>15 min for one epoch on the "medium" target vs Qwen's 243s), making a
# 5-target grid infeasible within this session's time budget. It also needed a manual patch
# (train_decoder.py's _patch_aragpt2_final_norm) to work around its final-layer-norm being
# stored under a checkpoint key (emb_norm.*) the native GPT2 classes don't wire up -- kept in
# the code (still correct, still avoids trust_remote_code) in case a future session has more
# time budget to retry it, but it is not part of the grid this phase actually ran.
BIG_MODELS = {
    "qwen2p5_3b": {"id": "Qwen/Qwen2.5-3B", "kind": "decoder", "quant": "4bit"},
    "arabert_large": {"id": "aubmindlab/bert-large-arabertv02", "kind": "encoder", "quant": "fp16"},
}

RUN_TIME_CAP_SECONDS = 30 * 60  # hard cap per training run, per task instruction

RESULTS_DIR = PHASE6_DIR.parents[1] / "results" / "phase6_stronger_ft"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"
RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR = PHASE6_DIR.parents[1] / "docs" / "phase6"
FIGS_DIR = DOCS_DIR / "figs"
FIGS_DIR.mkdir(parents=True, exist_ok=True)
