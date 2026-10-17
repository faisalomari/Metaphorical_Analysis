"""Promotes results/phase6_stronger_ft/selected_configs.json's top-2 configs
per target to the full S2 x3-seed grid (seed0 reused from the sweep, seed1/2
newly run), plus S3 x3 seeds for استعارة فعل (medium)'s top-2 configs. Uses
analysis_common.load_cell first so a selected config that resolves to Phase
5's own baseline data is never retrained."""
import json
import time
import traceback

import torch

import phase6_config as config
import runners
from analysis_common import load_cell


def ensure_seed(target_level: str, model_key: str, config_name: str, split_name: str, seed: int):
    existing = load_cell(target_level, model_key, config_name, split_name, seed)
    if existing is not None and existing.get("complete"):
        print(f"[reuse] {target_level}/{model_key}/{config_name}/{split_name}/seed{seed} already exists")
        return existing
    for attempt in (1, 2):
        try:
            return runners.run_cell(target_level, model_key, config_name, split_name, seed)
        except Exception as e:
            traceback.print_exc()
            torch.cuda.empty_cache()
            if attempt == 2:
                print(f"[final grid] GIVING UP on {target_level}/{model_key}/{config_name}/{split_name}/"
                      f"seed{seed} after 2 attempts: {e}")
                return None
            print(f"[final grid] attempt {attempt} failed, retrying once: {e}")


def main():
    selected = json.loads((config.RESULTS_DIR / "selected_configs.json").read_text(encoding="utf-8"))
    t0 = time.time()

    for target_level, cands in selected.items():
        for cand in cands:
            for seed in config.SEEDS:
                ensure_seed(target_level, cand["model_key"], cand["config_name"], "S2", seed)
            if target_level == "medium":
                for seed in config.SEEDS:
                    ensure_seed(target_level, cand["model_key"], cand["config_name"], "S3", seed)
        print(f"[final grid] {target_level} done, elapsed={((time.time()-t0)/60):.1f}min")

    print(f"\n[final grid] ALL DONE in {(time.time()-t0)/60:.1f} minutes.")


if __name__ == "__main__":
    main()
