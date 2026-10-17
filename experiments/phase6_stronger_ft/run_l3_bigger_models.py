"""Step 1, L3: bigger-model candidates, seed0 only first (cheap sweep), one
model x one recipe per target. `--recipe` lets the winning L1/L2 cell (picked
by select_best_configs.py after run_l1l2_ablation.py) be applied uniformly;
defaults to the Phase 5 baseline recipe (verse-alone, bce_pos_weight) if no
winner was picked yet. Each run is individually time-capped (task
instruction); this script prints the per-model VRAM/time estimate from the
first run before continuing to the rest."""
import argparse
import time
import traceback

import torch

import phase6_config as config
import train_decoder
import train_encoder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-context", action="store_true")
    ap.add_argument("--loss-type", default="bce_pos_weight", choices=["bce_pos_weight", "focal"])
    ap.add_argument("--targets", nargs="*", default=config.TARGET_LEVELS)
    ap.add_argument("--models", nargs="*", default=list(config.BIG_MODELS))
    ap.add_argument("--max-runtime-seconds", type=int, default=None,
                     help="defaults to config.RUN_TIME_CAP_SECONDS (30min); pass a smaller "
                          "value for a cheaper exploratory sweep before the final grid")
    args = ap.parse_args()

    t0 = time.time()
    n_total = len(args.targets) * len(args.models)
    n_done = 0
    failed = []
    for target_level in args.targets:
        for model_key in args.models:
            spec = config.BIG_MODELS[model_key]
            print(f"\n=== {target_level} / {model_key} ({spec['id']}, {spec['kind']}) ===")
            for attempt in (1, 2):
                try:
                    if spec["kind"] == "encoder":
                        train_encoder.run(
                            target_level, model_key, spec["id"], "S2", seed=0,
                            use_context=args.use_context, loss_type=args.loss_type, schedule="constant",
                            max_runtime_seconds=args.max_runtime_seconds,
                        )
                    else:
                        train_decoder.run(
                            target_level, model_key, "S2", seed=0,
                            use_context=args.use_context, loss_type=args.loss_type,
                            max_runtime_seconds=args.max_runtime_seconds,
                        )
                    break
                except Exception as e:
                    traceback.print_exc()
                    torch.cuda.empty_cache()
                    if attempt == 2:
                        print(f"[l3 sweep] GIVING UP on {target_level}/{model_key} after 2 attempts: {e}")
                        failed.append((target_level, model_key, str(e)))
                    else:
                        print(f"[l3 sweep] attempt {attempt} failed for {target_level}/{model_key}, retrying once: {e}")
            n_done += 1
            elapsed = time.time() - t0
            print(f"[l3 sweep] {n_done}/{n_total} done, elapsed={elapsed/60:.1f}min")
    print(f"\n[l3 sweep] ALL DONE in {(time.time()-t0)/60:.1f} minutes. Failed cells: {failed}")


if __name__ == "__main__":
    main()
