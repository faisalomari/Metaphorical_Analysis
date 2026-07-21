"""Per-element decomposition experiment, DEV only (PROJECT_STATE.md item 5a).

Runs:
  1. The 4 decomposed single-element prompts, 2 poems x 3 models x 2 runs
     = 48 calls, into results/pilot_3models/dev_variants/decomposed_{element}/{poem}/.
  2. A 2nd run of v4_combined on DEV (6 calls), appended to the existing
     results/pilot_3models/dev_variants/v4_combined/{poem}/ directories (which
     only had run1), so the comparison is 2-run majority vs 2-run majority.

Total: 54 calls. Never touches TEST.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DEV_POEMS, ELEMENT_ORDER, RESULTS_DIR
from prompts import build_user_message
from prompt_variants import build_system_message_variant
from decompose_prompts import build_system_message_decomposed, build_user_message_decomposed
from run_pilot import run

VARIANTS_DIR = RESULTS_DIR / "dev_variants"


def run_decomposed():
    for element in ELEMENT_ORDER:
        sm = build_system_message_decomposed(element)
        for poem_key in DEV_POEMS:
            um = build_user_message_decomposed(element, poem_key)
            out_dir = VARIANTS_DIR / f"decomposed_{element}" / poem_key
            run(poem_key=poem_key, n_runs=2, out_dir=out_dir, system_message=sm, user_message=um)


def run_v4_combined_run2():
    sm = build_system_message_variant("v4_combined")
    for poem_key in DEV_POEMS:
        um = build_user_message(poem_key)
        out_dir = VARIANTS_DIR / "v4_combined" / poem_key
        run(poem_key=poem_key, out_dir=out_dir, system_message=sm, user_message=um, run_indices=[2])


if __name__ == "__main__":
    run_v4_combined_run2()
    run_decomposed()
