"""Final, frozen TEST evaluation: baseline vs v4_combined, on Imru1 + Jarir +
Abu_Tammam, 2 runs per model per prompt. This is the one-shot TEST run --
no further prompt iteration is evaluated against these poems after this.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import TEST_POEMS, RESULTS_DIR
from prompts import build_system_message, build_user_message
from prompt_variants import build_system_message_variant
from run_pilot import run

TEST_DIR = RESULTS_DIR / "test_final"

PROMPTS = {
    "baseline": build_system_message,
    "v4_combined": lambda: build_system_message_variant("v4_combined"),
}


def main():
    for prompt_key, sm_builder in PROMPTS.items():
        sm = sm_builder()
        for poem_key in TEST_POEMS:
            um = build_user_message(poem_key)
            out_dir = TEST_DIR / prompt_key / poem_key
            run(poem_key=poem_key, n_runs=2, out_dir=out_dir, system_message=sm, user_message=um)


if __name__ == "__main__":
    main()
