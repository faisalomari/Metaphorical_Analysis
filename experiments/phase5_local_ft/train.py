"""Fine-tunes one HF model on one target, for one split+seed. fp16, early
stopping on val F1, decision threshold tuned on VAL only. Saves ONLY metrics
+ predictions (results/phase5_local_ft/raw/*.json) -- no weights/checkpoints
ever written to disk (kept in memory only, for the duration of one run)."""
import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import phase5_config as config
from dataset import build_examples, load_split
from metrics_utils import best_threshold, prf
from normalize import strip_diacritics

with open(config.CONFIG_DIR / "targets.json", encoding="utf-8") as f:
    TARGETS_BY_LEVEL = {t["level"]: t for t in json.load(f)["targets"]}


class VerseDataset(Dataset):
    def __init__(self, examples, tokenizer, max_len, diacritics=True):
        texts = [e["text"] if diacritics else strip_diacritics(e["text"]) for e in examples]
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


def run(target_level: str, model_key: str, split_name: str, seed: int,
        diacritics_check: bool = False, force: bool = False, max_epochs: int = None) -> dict:
    target = TARGETS_BY_LEVEL[target_level]
    target_value = target["value"]
    model_name = config.MODELS[model_key]
    max_epochs = max_epochs or config.MAX_EPOCHS

    out_path = config.RAW_RESULTS_DIR / f"{target_level}__{model_key}__{split_name}__seed{seed}.json"
    if out_path.exists() and not force:
        existing = json.loads(out_path.read_text(encoding="utf-8"))
        if existing.get("complete"):
            print(f"[skip] {out_path.name} already complete")
            return existing

    set_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    split = load_split(config.SPLITS_DIR / f"{split_name}_seed{seed}.json")
    train_ex = build_examples(split["train"], target_value)
    val_ex = build_examples(split["val"], target_value)
    test_ex = build_examples(split["test"], target_value)

    train_pos = sum(e["label"] for e in train_ex)
    train_neg = len(train_ex) - train_pos
    pos_weight_value = (train_neg / train_pos) if train_pos else 1.0
    print(f"[{out_path.stem}] train={len(train_ex)}(pos={train_pos}) val={len(val_ex)} test={len(test_ex)} "
          f"pos_weight={pos_weight_value:.3f}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_ds = VerseDataset(train_ex, tokenizer, config.MAX_LEN)
    val_ds = VerseDataset(val_ex, tokenizer, config.MAX_LEN)
    test_ds = VerseDataset(test_ex, tokenizer, config.MAX_LEN)

    train_loader = DataLoader(train_ds, batch_size=config.BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=0)

    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.LR, weight_decay=config.WEIGHT_DECAY)
    scaler = torch.amp.GradScaler("cuda")
    pos_weight_t = torch.tensor([pos_weight_value], device=device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight_t)

    val_labels = [e["label"] for e in val_ex]
    test_labels = [e["label"] for e in test_ex]

    best_val_f1 = -1.0
    best_state = None
    best_epoch = -1
    epochs_no_improve = 0
    epoch_log = []
    t_start = time.time()

    for epoch in range(1, max_epochs + 1):
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
            if epochs_no_improve >= config.EARLY_STOP_PATIENCE:
                print(f"  early stop at epoch {epoch} (best={best_epoch}, val_f1={best_val_f1:.4f})")
                break

    total_train_seconds = time.time() - t_start
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

    result = {
        "target_level": target_level, "target_value": target_value, "model_key": model_key,
        "model_name": model_name, "split": split_name, "seed": seed, "max_len": config.MAX_LEN,
        "batch_size": config.BATCH_SIZE, "lr": config.LR, "max_epochs": max_epochs,
        "early_stop_patience": config.EARLY_STOP_PATIENCE,
        "loss": "BCEWithLogitsLoss(pos_weight) -- computed from this run's TRAIN split "
                "(neg/pos), not a fixed corpus-wide value",
        "pos_weight": pos_weight_value,
        "train_size": len(train_ex), "train_pos": train_pos,
        "val_size": len(val_ex), "val_pos": sum(val_labels),
        "test_size": len(test_ex), "test_pos": sum(test_labels),
        "best_epoch": best_epoch, "best_val_f1": best_val_f1, "threshold": threshold,
        "total_train_seconds": round(total_train_seconds, 1),
        "epoch_log": epoch_log,
        "test_metrics": test_metrics,
        "predictions": predictions,
        "complete": True,
    }

    if diacritics_check:
        val_ds_nodia = VerseDataset(val_ex, tokenizer, config.MAX_LEN, diacritics=False)
        val_loader_nodia = DataLoader(val_ds_nodia, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=0)
        val_probs_nodia = predict_probs(model, val_loader_nodia, device)
        val_best_nodia = best_threshold(val_labels, val_probs_nodia, config.THRESHOLD_GRID)
        result["diacritics_ablation"] = {
            "val_f1_with_diacritics": val_best["f1"],
            "val_f1_without_diacritics": val_best_nodia["f1"],
            "val_threshold_with_diacritics": val_best["threshold"],
            "val_threshold_without_diacritics": val_best_nodia["threshold"],
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
    ap.add_argument("--target-level", required=True, choices=list(TARGETS_BY_LEVEL))
    ap.add_argument("--model", required=True, choices=list(config.MODELS))
    ap.add_argument("--split", required=True, choices=["S1", "S2", "S3"])
    ap.add_argument("--seed", type=int, required=True, choices=config.SEEDS)
    ap.add_argument("--diacritics-check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--max-epochs", type=int, default=None)
    args = ap.parse_args()
    run(args.target_level, args.model, args.split, args.seed,
        diacritics_check=args.diacritics_check, force=args.force, max_epochs=args.max_epochs)
