"""Run all prompt variants across DEV poems, 3 models x 1 run each."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DEV_POEMS, RESULTS_DIR
from prompts import build_user_message
from prompt_variants import VARIANTS, build_system_message_variant
from run_pilot import run

VARIANTS_DIR = RESULTS_DIR / "dev_variants"


def main():
    total_cost_tokens = []
    for variant_key in VARIANTS:
        if variant_key == "baseline":
            continue  # already have this data: pilot_3models/raw (Imru2) + dev_nabigha_baseline (Nabigha)
        sm = build_system_message_variant(variant_key)
        for poem_key in DEV_POEMS:
            um = build_user_message(poem_key)
            out_dir = VARIANTS_DIR / variant_key / poem_key
            manifest = run(poem_key=poem_key, n_runs=1, out_dir=out_dir,
                            system_message=sm, user_message=um)
            total_cost_tokens.append((variant_key, poem_key, manifest))
    return total_cost_tokens


if __name__ == "__main__":
    main()
