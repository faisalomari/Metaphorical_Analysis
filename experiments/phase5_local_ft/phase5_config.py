"""Phase 5 constants: models, tokenization, training hyperparameters."""
import os
from pathlib import Path

PHASE5_DIR = Path(__file__).resolve().parent
os.environ.setdefault("HF_HOME", str(PHASE5_DIR / "hf_cache"))  # local cache, gitignored, no HF token used

MODELS = {
    "camelbert_ca": "CAMeL-Lab/bert-base-arabic-camelbert-ca",
    "arabert_v2": "aubmindlab/bert-base-arabertv2",
    "marbert": "UBC-NLP/MARBERT",
}

# 99th percentile verse token length across all 3 tokenizers (corpus-wide, see SESSION_LOG):
# camelbert_ca p99=20, arabert_v2 p99=21, marbert p99=23. 32 covers all 3 with margin.
MAX_LEN = 32

BATCH_SIZE = 64
GRAD_ACCUM = 1
LR = 2e-5
WEIGHT_DECAY = 0.01
MAX_EPOCHS = 15
EARLY_STOP_PATIENCE = 3  # epochs with no val-F1 improvement before stopping
THRESHOLD_GRID = [round(0.05 + 0.01 * i, 2) for i in range(91)]  # 0.05..0.95 step 0.01
SEEDS = [0, 1, 2]

SPLITS_DIR = PHASE5_DIR / "splits"
CONFIG_DIR = PHASE5_DIR / "config"
RESULTS_DIR = PHASE5_DIR.parents[1] / "results" / "phase5_local_ft"
RAW_RESULTS_DIR = RESULTS_DIR / "raw"
RAW_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
