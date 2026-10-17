"""Step 1, L1+L2: controlled one-lever-at-a-time ablation against the Phase 5
best model per target, seed0 only (cheap sweep to see which lever helps which
target before committing to 3-seed runs). Baseline cell (ctx0_bce_pos_weight_
constant) is NOT retrained here -- it is Phase 5's own raw/*.json for that
(target, model, S2, seed0), reused as-is (verified in smoke-testing that this
generalized trainer reproduces it almost exactly). Three new cells per target:
  - L1 alone:  use_context=True,  loss=bce_pos_weight, schedule=constant
  - L2a alone: use_context=False, loss=focal,          schedule=constant
  - L2b alone: use_context=False, loss=bce_pos_weight, schedule=cosine_llrd
"""
import time

import phase6_config as config
import train_encoder

CELLS = [
    {"use_context": True, "loss_type": "bce_pos_weight", "schedule": "constant", "label": "L1_context"},
    {"use_context": False, "loss_type": "focal", "schedule": "constant", "label": "L2a_focal"},
    {"use_context": False, "loss_type": "bce_pos_weight", "schedule": "cosine_llrd", "label": "L2b_cosine_llrd"},
]


def main():
    t0 = time.time()
    n_total = len(config.TARGET_LEVELS) * len(CELLS)
    n_done = 0
    for target_level in config.TARGET_LEVELS:
        model_key = config.PHASE5_BEST_MODEL[target_level]
        model_name = config.ENCODER_MODELS[model_key]
        for cell in CELLS:
            train_encoder.run(
                target_level, model_key, model_name, "S2", seed=0,
                use_context=cell["use_context"], loss_type=cell["loss_type"], schedule=cell["schedule"],
            )
            n_done += 1
            elapsed = time.time() - t0
            print(f"[l1l2 ablation] {n_done}/{n_total} done, elapsed={elapsed/60:.1f}min "
                  f"({target_level}/{model_key}/{cell['label']})")
    print(f"\n[l1l2 ablation] ALL DONE in {(time.time()-t0)/60:.1f} minutes.")


if __name__ == "__main__":
    main()
