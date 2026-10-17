"""L3 lever: QLoRA 4-bit fine-tuning of a decoder (causal LM) for verse-level
binary classification, via each model's native *ForSequenceClassification
class (last-non-pad-token pooling + a linear head) -- never trust_remote_code
(aragpt2-mega ships a custom modeling_aragpt2.py; this loads it as a plain
GPT2Config/GPT2ForSequenceClassification instead, since its config.json uses
GPT2's own field names). Base weights are frozen+4bit; only LoRA adapters +
the classification head train.

aragpt2-mega caveat (found via the LOAD REPORT during smoke-testing, not
assumed): its final layer norm is a differently-named module in the
checkpoint (`emb_norm.weight`/`.bias`) that only the custom modeling code
wires up as `transformer.ln_f` -- loading through the native GPT2 class
leaves `transformer.ln_f` at nn.LayerNorm's default init (weight=1, bias=0)
instead. `_patch_aragpt2_final_norm()` below copies those two tensors
straight from the already-downloaded safetensors file (no custom code
executed, just a tensor copy) so the pretrained final norm is actually used.

Same per-run JSON schema as train_encoder.py (so analysis code doesn't care
whether a cell came from an encoder or a decoder run); no weights/checkpoints
ever written to disk; hard time cap per run (task instruction)."""
import argparse
import json
import random
import time

import numpy as np
import torch
from huggingface_hub import hf_hub_download
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from safetensors import safe_open
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig,
                           GPT2Config, GPT2ForSequenceClassification, GPT2TokenizerFast)

import phase6_config as config
from context_dataset import build_examples, load_split
from losses import build_loss
from metrics_utils import best_threshold, prf

DECODER_BATCH_SIZE = 8
DECODER_GRAD_ACCUM = 4
DECODER_LR = 2e-4  # standard LoRA lr, ~10x the full-fine-tune encoder lr
DECODER_MAX_EPOCHS = 10
DECODER_PATIENCE = 3

# Registry: how to build the tokenizer/model/LoRA-target-modules for each L3 decoder id.
DECODER_SPECS = {
    "qwen2p5_3b": {
        "hf_id": "Qwen/Qwen2.5-3B",
        "loader": "auto",
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    },
    "aragpt2_mega": {
        "hf_id": "aubmindlab/aragpt2-mega",
        "loader": "gpt2config",  # avoids trust_remote_code -- see module docstring
        "target_modules": ["c_attn", "c_proj", "c_fc"],
    },
}


class VerseDataset(Dataset):
    def __init__(self, examples, tokenizer, max_len):
        texts = [e["text"] for e in examples]
        enc = tokenizer(texts, max_length=max_len, padding="max_length", truncation=True, return_tensors="pt")
        self.input_ids = enc["input_ids"]
        self.attention_mask = enc["attention_mask"]
        self.labels = torch.tensor([e["label"] for e in examples], dtype=torch.float32)
        self.meta = [(e["poem_id"], e["verse_no"]) for e in examples]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        return self.input_ids[i], self.attention_mask[i], self.labels[i]


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def _patch_aragpt2_final_norm(model, hf_id: str) -> bool:
    """Copies emb_norm.{weight,bias} from the checkpoint's own safetensors file
    into model.transformer.ln_f (see module docstring). Returns True if the
    patch was applied, False if the checkpoint doesn't have that key (so a
    caller can tell whether this was needed/possible)."""
    path = hf_hub_download(hf_id, "model.safetensors", token=False)
    with safe_open(path, framework="pt") as f:
        keys = f.keys()
        if "emb_norm.weight" not in keys or "emb_norm.bias" not in keys:
            return False
        w = f.get_tensor("emb_norm.weight")
        b = f.get_tensor("emb_norm.bias")
    with torch.no_grad():
        model.transformer.ln_f.weight.data.copy_(w.to(model.transformer.ln_f.weight.dtype))
        model.transformer.ln_f.bias.data.copy_(b.to(model.transformer.ln_f.bias.dtype))
    return True


def _load_tokenizer_and_model(spec: dict, device):
    hf_id = spec["hf_id"]
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
    )
    if spec["loader"] == "auto":
        tokenizer = AutoTokenizer.from_pretrained(hf_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model = AutoModelForSequenceClassification.from_pretrained(
            hf_id, num_labels=1, quantization_config=bnb_config, device_map={"": 0})
    elif spec["loader"] == "gpt2config":
        tokenizer = GPT2TokenizerFast.from_pretrained(hf_id)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        gpt2_config = GPT2Config.from_pretrained(hf_id, num_labels=1)
        model = GPT2ForSequenceClassification.from_pretrained(
            hf_id, config=gpt2_config, quantization_config=bnb_config, device_map={"": 0})
        patched = _patch_aragpt2_final_norm(model, hf_id)
        print(f"  [aragpt2 final-norm patch] applied={patched}")
    else:
        raise ValueError(f"unknown loader: {spec['loader']}")
    model.config.pad_token_id = tokenizer.pad_token_id
    return tokenizer, model


@torch.no_grad()
def predict_probs(model, loader, device):
    model.eval()
    probs = []
    for input_ids, attention_mask, _ in loader:
        input_ids, attention_mask = input_ids.to(device), attention_mask.to(device)
        logits = model(input_ids=input_ids, attention_mask=attention_mask).logits.squeeze(-1)
        probs.extend(torch.sigmoid(logits.float()).cpu().tolist())
    return probs


def run(target_level: str, model_key: str, split_name: str, seed: int,
        use_context: bool = False, loss_type: str = "bce_pos_weight",
        force: bool = False, max_runtime_seconds: int = None, tag: str = None) -> dict:
    spec = DECODER_SPECS[model_key]
    target = config.TARGETS_BY_LEVEL[target_level]
    target_value = target["value"]
    max_runtime_seconds = max_runtime_seconds or config.RUN_TIME_CAP_SECONDS

    config_name = tag or f"ctx{int(use_context)}_{loss_type}_qlora"
    out_path = config.RAW_RESULTS_DIR / f"{target_level}__{model_key}__{config_name}__{split_name}__seed{seed}.json"
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing.get("complete"):
            print(f"[skip] {out_path.name} already complete")
            return existing

    set_seed(seed)
    device = torch.device("cuda")

    split = load_split(config.SPLITS_DIR / f"{split_name}_seed{seed}.json")
    train_ex = build_examples(split["train"], target_value, use_context)
    val_ex = build_examples(split["val"], target_value, use_context)
    test_ex = build_examples(split["test"], target_value, use_context)

    train_pos = sum(e["label"] for e in train_ex)
    train_neg = len(train_ex) - train_pos
    pos_weight_value = (train_neg / train_pos) if train_pos else 1.0
    max_len = config.MAX_LEN_CONTEXT if use_context else config.MAX_LEN_BASE

    t_load = time.time()
    tokenizer, model = _load_tokenizer_and_model(spec, device)
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS, r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=spec["target_modules"], modules_to_save=["score"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    load_seconds = time.time() - t_load

    vram_gb = torch.cuda.memory_allocated() / 1e9
    vram_reserved_gb = torch.cuda.memory_reserved() / 1e9
    print(f"[{out_path.stem}] train={len(train_ex)}(pos={train_pos}) val={len(val_ex)} test={len(test_ex)} "
          f"pos_weight={pos_weight_value:.3f} max_len={max_len} "
          f"model_load={load_seconds:.1f}s vram_allocated={vram_gb:.2f}GB vram_reserved={vram_reserved_gb:.2f}GB")

    train_ds = VerseDataset(train_ex, tokenizer, max_len)
    val_ds = VerseDataset(val_ex, tokenizer, max_len)
    test_ds = VerseDataset(test_ex, tokenizer, max_len)

    train_loader = DataLoader(train_ds, batch_size=DECODER_BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=DECODER_BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=DECODER_BATCH_SIZE, shuffle=False, num_workers=0)

    loss_fn = build_loss(loss_type, pos_weight_value, device)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=DECODER_LR)

    val_labels = [e["label"] for e in val_ex]
    test_labels = [e["label"] for e in test_ex]

    best_val_f1 = -1.0
    best_state = None
    best_epoch = -1
    epochs_no_improve = 0
    epoch_log = []
    t_start = time.time()
    hit_time_cap = False
    first_epoch_seconds = None

    for epoch in range(1, DECODER_MAX_EPOCHS + 1):
        if time.time() - t_start > max_runtime_seconds:
            print(f"  [time cap] stopping at epoch {epoch-1} after {max_runtime_seconds}s")
            hit_time_cap = True
            break
        model.train()
        t_ep = time.time()
        running_loss = 0.0
        optimizer.zero_grad()
        for step, (input_ids, attention_mask, labels) in enumerate(train_loader):
            input_ids, attention_mask, labels = input_ids.to(device), attention_mask.to(device), labels.to(device)
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits.squeeze(-1)
            loss = loss_fn(logits.float(), labels) / DECODER_GRAD_ACCUM
            loss.backward()
            if (step + 1) % DECODER_GRAD_ACCUM == 0:
                optimizer.step()
                optimizer.zero_grad()
            running_loss += loss.item() * DECODER_GRAD_ACCUM * len(labels)
        epoch_time = time.time() - t_ep
        if first_epoch_seconds is None:
            first_epoch_seconds = epoch_time
            est_total = first_epoch_seconds * DECODER_MAX_EPOCHS
            print(f"  [estimate] first epoch took {first_epoch_seconds:.1f}s -> "
                  f"~{est_total/60:.1f}min for all {DECODER_MAX_EPOCHS} epochs if no early stop "
                  f"(run time-capped at {max_runtime_seconds/60:.0f}min)")

        val_probs = predict_probs(model, val_loader, device)
        val_best = best_threshold(val_labels, val_probs, config.THRESHOLD_GRID)
        epoch_log.append({"epoch": epoch, "train_loss": running_loss / len(train_ex),
                           "val_f1": val_best["f1"], "val_threshold": val_best["threshold"],
                           "epoch_seconds": round(epoch_time, 2)})
        print(f"  epoch {epoch}: loss={running_loss/len(train_ex):.4f} val_f1={val_best['f1']:.4f} "
              f"({epoch_time:.1f}s)")

        if val_best["f1"] > best_val_f1:
            best_val_f1 = val_best["f1"]
            best_epoch = epoch
            best_state = {k: v.detach().clone().cpu() for k, v in model.state_dict().items() if "lora" in k or "score" in k or "modules_to_save" in k}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= DECODER_PATIENCE:
                print(f"  early stop at epoch {epoch} (best={best_epoch}, val_f1={best_val_f1:.4f})")
                break

    total_train_seconds = time.time() - t_start
    if best_state is not None:
        model.load_state_dict(best_state, strict=False)

    val_probs = predict_probs(model, val_loader, device)
    val_best = best_threshold(val_labels, val_probs, config.THRESHOLD_GRID)
    threshold = val_best["threshold"]

    test_probs = predict_probs(model, test_loader, device)
    test_pred = [1 if p >= threshold else 0 for p in test_probs]
    test_metrics = prf(test_labels, test_pred)

    predictions = [{"poem_id": pid, "verse_no": vno, "label": lab, "prob": prob, "pred": pred}
                   for (pid, vno), lab, prob, pred in zip(test_ds.meta, test_labels, test_probs, test_pred)]
    val_pred_bin = [1 if p >= threshold else 0 for p in val_probs]
    val_predictions = [{"poem_id": pid, "verse_no": vno, "label": lab, "prob": prob, "pred": pred}
                        for (pid, vno), lab, prob, pred in zip(val_ds.meta, val_labels, val_probs, val_pred_bin)]

    result = {
        "target_level": target_level, "target_value": target_value, "model_key": model_key,
        "model_name": spec["hf_id"], "split": split_name, "seed": seed,
        "config_name": config_name, "use_context": use_context, "loss_type": loss_type,
        "schedule": "qlora", "max_len": max_len,
        "batch_size": DECODER_BATCH_SIZE * DECODER_GRAD_ACCUM, "base_lr": DECODER_LR,
        "max_epochs": DECODER_MAX_EPOCHS, "early_stop_patience": DECODER_PATIENCE,
        "pos_weight": pos_weight_value,
        "train_size": len(train_ex), "train_pos": train_pos,
        "val_size": len(val_ex), "val_pos": sum(val_labels),
        "test_size": len(test_ex), "test_pos": sum(test_labels),
        "best_epoch": best_epoch, "best_val_f1": best_val_f1, "threshold": threshold,
        "total_train_seconds": round(total_train_seconds, 1),
        "hit_time_cap": hit_time_cap,
        "model_load_seconds": round(load_seconds, 1),
        "vram_allocated_gb": round(vram_gb, 2), "vram_reserved_gb": round(vram_reserved_gb, 2),
        "first_epoch_seconds": round(first_epoch_seconds, 1) if first_epoch_seconds else None,
        "epoch_log": epoch_log,
        "test_metrics": test_metrics,
        "predictions": predictions,
        "val_predictions": val_predictions,
        "complete": True,
    }

    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] {out_path.name} test_f1={test_metrics['f1']:.4f} "
          f"(tp={test_metrics['tp']} fp={test_metrics['fp']} fn={test_metrics['fn']}) "
          f"total={total_train_seconds:.1f}s")

    del model, best_state
    torch.cuda.empty_cache()
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-level", required=True, choices=list(config.TARGETS_BY_LEVEL))
    ap.add_argument("--model-key", required=True, choices=list(DECODER_SPECS))
    ap.add_argument("--split", required=True, choices=["S1", "S2", "S3"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--use-context", action="store_true")
    ap.add_argument("--loss-type", default="bce_pos_weight", choices=["bce_pos_weight", "focal"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--max-runtime-seconds", type=int, default=None)
    args = ap.parse_args()
    run(args.target_level, args.model_key, args.split, args.seed,
        use_context=args.use_context, loss_type=args.loss_type,
        force=args.force, tag=args.tag, max_runtime_seconds=args.max_runtime_seconds)
