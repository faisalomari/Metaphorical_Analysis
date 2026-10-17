"""Phase 6 generalized encoder trainer: same fp16/early-stopping/val-tuned-
threshold discipline as Phase 5's train.py, but parameterized over the L1
(context window) and L2 (loss type, LR schedule + LLRD) levers, so it can
reproduce Phase 5's exact recipe (use_context=False, loss_type=bce_pos_weight,
schedule=constant) as a sanity check, or vary exactly one lever at a time
against the Phase 5 best model per target, per task instruction. Also used
for the L3 large-encoder candidate (aubmindlab/bert-large-arabertv02) --
same code path, just a different model_name. No weights ever written to disk."""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_cosine_schedule_with_warmup

import phase6_config as config
from context_dataset import build_examples, load_split
from losses import build_loss
from llrd import llrd_param_groups
from metrics_utils import best_threshold, prf


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


@torch.no_grad()
def predict_probs(model, loader, device):
    model.eval()
    probs = []
    for input_ids, attention_mask, _ in loader:
        input_ids, attention_mask = input_ids.to(device), attention_mask.to(device)
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            logits = model(input_ids=input_ids, attention_mask=attention_mask).logits.squeeze(-1)
        probs.extend(torch.sigmoid(logits.float()).cpu().tolist())
    return probs


def run(target_level: str, model_key: str, model_name: str, split_name: str, seed: int,
        use_context: bool = False, loss_type: str = "bce_pos_weight", schedule: str = "constant",
        force: bool = False, max_runtime_seconds: int = None, tag: str = None) -> dict:
    target = config.TARGETS_BY_LEVEL[target_level]
    target_value = target["value"]
    max_runtime_seconds = max_runtime_seconds or config.RUN_TIME_CAP_SECONDS

    config_name = tag or f"ctx{int(use_context)}_{loss_type}_{schedule}"
    out_path = config.RAW_RESULTS_DIR / f"{target_level}__{model_key}__{config_name}__{split_name}__seed{seed}.json"
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing.get("complete"):
            print(f"[skip] {out_path.name} already complete")
            return existing

    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    split = load_split(config.SPLITS_DIR / f"{split_name}_seed{seed}.json")
    train_ex = build_examples(split["train"], target_value, use_context)
    val_ex = build_examples(split["val"], target_value, use_context)
    test_ex = build_examples(split["test"], target_value, use_context)

    train_pos = sum(e["label"] for e in train_ex)
    train_neg = len(train_ex) - train_pos
    pos_weight_value = (train_neg / train_pos) if train_pos else 1.0
    max_len = config.MAX_LEN_CONTEXT if use_context else config.MAX_LEN_BASE
    print(f"[{out_path.stem}] train={len(train_ex)}(pos={train_pos}) val={len(val_ex)} test={len(test_ex)} "
          f"pos_weight={pos_weight_value:.3f} max_len={max_len}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_ds = VerseDataset(train_ex, tokenizer, max_len)
    val_ds = VerseDataset(val_ex, tokenizer, max_len)
    test_ds = VerseDataset(test_ex, tokenizer, max_len)

    train_loader = DataLoader(train_ds, batch_size=config.p5.BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=config.p5.BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=config.p5.BATCH_SIZE, shuffle=False, num_workers=0)

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1).to(device)
    loss_fn = build_loss(loss_type, pos_weight_value, device)

    if schedule == "constant":
        max_epochs, patience = config.p5.MAX_EPOCHS, config.p5.EARLY_STOP_PATIENCE
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.p5.LR, weight_decay=config.p5.WEIGHT_DECAY)
        lr_scheduler = None
    elif schedule == "cosine_llrd":
        max_epochs, patience = config.L2_COSINE_MAX_EPOCHS, config.L2_COSINE_PATIENCE
        groups = llrd_param_groups(model, config.p5.LR, config.L2_LLRD_DECAY, config.p5.WEIGHT_DECAY)
        optimizer = torch.optim.AdamW(groups)
        total_steps = max_epochs * max(1, len(train_loader))
        lr_scheduler = get_cosine_schedule_with_warmup(
            optimizer, num_warmup_steps=int(config.L2_WARMUP_RATIO * total_steps), num_training_steps=total_steps)
    else:
        raise ValueError(f"unknown schedule: {schedule}")

    scaler = torch.amp.GradScaler("cuda")
    val_labels = [e["label"] for e in val_ex]
    test_labels = [e["label"] for e in test_ex]

    best_val_f1 = -1.0
    best_state = None
    best_epoch = -1
    epochs_no_improve = 0
    epoch_log = []
    t_start = time.time()
    hit_time_cap = False

    for epoch in range(1, max_epochs + 1):
        if time.time() - t_start > max_runtime_seconds:
            print(f"  [time cap] stopping at epoch {epoch-1} after {max_runtime_seconds}s")
            hit_time_cap = True
            break
        model.train()
        t_ep = time.time()
        running_loss = 0.0
        for input_ids, attention_mask, labels in train_loader:
            input_ids, attention_mask, labels = input_ids.to(device), attention_mask.to(device), labels.to(device)
            optimizer.zero_grad()
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                logits = model(input_ids=input_ids, attention_mask=attention_mask).logits.squeeze(-1)
                loss = loss_fn(logits.float(), labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            if lr_scheduler is not None:
                lr_scheduler.step()
            running_loss += loss.item() * len(labels)
        epoch_time = time.time() - t_ep

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
            best_state = {k: v.detach().clone().cpu() for k, v in model.state_dict().items()}
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"  early stop at epoch {epoch} (best={best_epoch}, val_f1={best_val_f1:.4f})")
                break

    total_train_seconds = time.time() - t_start
    if best_state is not None:
        model.load_state_dict(best_state)
    model.to(device)

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
        "model_name": model_name, "split": split_name, "seed": seed,
        "config_name": config_name, "use_context": use_context, "loss_type": loss_type,
        "schedule": schedule, "max_len": max_len,
        "batch_size": config.p5.BATCH_SIZE, "base_lr": config.p5.LR,
        "max_epochs": max_epochs, "early_stop_patience": patience,
        "pos_weight": pos_weight_value,
        "train_size": len(train_ex), "train_pos": train_pos,
        "val_size": len(val_ex), "val_pos": sum(val_labels),
        "test_size": len(test_ex), "test_pos": sum(test_labels),
        "best_epoch": best_epoch, "best_val_f1": best_val_f1, "threshold": threshold,
        "total_train_seconds": round(total_train_seconds, 1),
        "hit_time_cap": hit_time_cap,
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
    ap.add_argument("--model-key", required=True)
    ap.add_argument("--model-name", default=None, help="defaults to phase6_config.ENCODER_MODELS[model_key]")
    ap.add_argument("--split", required=True, choices=["S1", "S2", "S3"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--use-context", action="store_true")
    ap.add_argument("--loss-type", default="bce_pos_weight", choices=["bce_pos_weight", "focal"])
    ap.add_argument("--schedule", default="constant", choices=["constant", "cosine_llrd"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    model_name = args.model_name or config.ENCODER_MODELS.get(args.model_key)
    if model_name is None:
        raise SystemExit(f"no known model for --model-key {args.model_key}; pass --model-name explicitly")
    run(args.target_level, args.model_key, model_name, args.split, args.seed,
        use_context=args.use_context, loss_type=args.loss_type, schedule=args.schedule,
        force=args.force, tag=args.tag)
