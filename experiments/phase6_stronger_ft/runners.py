"""Dispatches a (model_key, config_name) cell to train_encoder.run or
train_decoder.run, parsing config_name back into its (use_context, loss_type,
schedule) parts. config_name format: "ctx{0|1}_{loss_type}_{schedule}", where
loss_type in {bce_pos_weight, focal} and schedule in {constant, cosine_llrd,
qlora}. Shared by run_final_grid.py and the ensemble/evaluation scripts."""
import re

import phase6_config as config
import train_decoder
import train_encoder

_PATTERN = re.compile(r"^ctx(?P<ctx>[01])_(?P<loss>bce_pos_weight|focal)_(?P<schedule>constant|cosine_llrd|qlora)$")


def parse_config_name(config_name: str) -> dict:
    m = _PATTERN.match(config_name)
    if not m:
        raise ValueError(f"unparseable config_name: {config_name}")
    return {"use_context": m.group("ctx") == "1", "loss_type": m.group("loss"), "schedule": m.group("schedule")}


def run_cell(target_level: str, model_key: str, config_name: str, split_name: str, seed: int, force: bool = False):
    parsed = parse_config_name(config_name)
    if model_key in config.BIG_MODELS and config.BIG_MODELS[model_key]["kind"] != "encoder":
        return train_decoder.run(target_level, model_key, split_name, seed,
                                  use_context=parsed["use_context"], loss_type=parsed["loss_type"],
                                  force=force, tag=config_name)
    model_name = config.ENCODER_MODELS.get(model_key) or config.BIG_MODELS.get(model_key, {}).get("id")
    if model_name is None:
        raise ValueError(f"unknown model_key: {model_key}")
    return train_encoder.run(target_level, model_key, model_name, split_name, seed,
                              use_context=parsed["use_context"], loss_type=parsed["loss_type"],
                              schedule=parsed["schedule"], force=force, tag=config_name)
