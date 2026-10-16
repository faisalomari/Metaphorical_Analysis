"""Full training grid, resumable: S1 + S2 x 3 models x 5 targets x 3 seeds,
plus S3 (استعارة فعل only) x 3 models x 3 seeds. Smoke-tested timing (see
SESSION_LOG): ~4s/epoch, ~15-30s per full run on this corpus size -- the
whole grid is expected to take well under an hour on the RTX 3060 Ti, so
(unlike the task's "best model only" fallback for a slower setup) every
model x target x split x seed cell is run, not just the best model per
target. diacritics_check=True on every run (negligible extra cost: one more
val forward pass, no retraining)."""
import time

import phase5_config as config
import train
from run_baselines import run_one as run_baseline

TARGET_LEVELS = ["very_easy", "easy", "medium", "hard", "very_hard"]


def main():
    t0 = time.time()
    n_done = 0
    n_total = len(TARGET_LEVELS) * len(config.MODELS) * len(config.SEEDS) * 2 + len(config.MODELS) * len(config.SEEDS)

    for split_name in ["S1", "S2"]:
        for target_level in TARGET_LEVELS:
            for seed in config.SEEDS:
                run_baseline(target_level, split_name, seed)
            for model_key in config.MODELS:
                for seed in config.SEEDS:
                    train.run(target_level, model_key, split_name, seed, diacritics_check=True)
                    n_done += 1
                    elapsed = time.time() - t0
                    print(f"[grid] {n_done}/{n_total} done, elapsed={elapsed/60:.1f}min, "
                          f"avg={elapsed/n_done:.1f}s/run, ETA={((n_total-n_done)*elapsed/n_done)/60:.1f}min")

    for seed in config.SEEDS:
        run_baseline("medium", "S3", seed)
    for model_key in config.MODELS:
        for seed in config.SEEDS:
            train.run("medium", model_key, "S3", seed, diacritics_check=True)
            n_done += 1
            elapsed = time.time() - t0
            print(f"[grid] {n_done}/{n_total} done, elapsed={elapsed/60:.1f}min")

    print(f"\n[grid] ALL DONE in {(time.time()-t0)/60:.1f} minutes.")


if __name__ == "__main__":
    main()
