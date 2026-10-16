"""Runs the 3 non-neural baselines (majority, always-positive, TF-IDF char
n-gram + logistic regression) for every (target, split, seed) combination.
No GPU needed; fast. Resumable (skips files that already exist)."""
import json

import phase5_config as config
from baselines import always_positive_baseline, majority_baseline, tfidf_logreg_baseline
from dataset import build_examples, load_split

with open(config.CONFIG_DIR / "targets.json", encoding="utf-8") as f:
    TARGETS_BY_LEVEL = {t["level"]: t for t in json.load(f)["targets"]}


def run_one(target_level: str, split_name: str, seed: int, force: bool = False) -> dict:
    out_path = config.RAW_RESULTS_DIR / f"baselines__{target_level}__{split_name}__seed{seed}.json"
    if out_path.exists() and not force:
        return json.loads(out_path.read_text(encoding="utf-8"))

    target_value = TARGETS_BY_LEVEL[target_level]["value"]
    split = load_split(config.SPLITS_DIR / f"{split_name}_seed{seed}.json")
    train_ex = build_examples(split["train"], target_value)
    val_ex = build_examples(split["val"], target_value)
    test_ex = build_examples(split["test"], target_value)

    train_labels = [e["label"] for e in train_ex]
    val_labels = [e["label"] for e in val_ex]
    test_labels = [e["label"] for e in test_ex]
    train_texts = [e["text"] for e in train_ex]
    val_texts = [e["text"] for e in val_ex]
    test_texts = [e["text"] for e in test_ex]

    result = {
        "target_level": target_level, "target_value": target_value, "split": split_name, "seed": seed,
        "train_size": len(train_ex), "val_size": len(val_ex), "test_size": len(test_ex),
        "majority": majority_baseline(train_labels, test_labels),
        "always_positive": always_positive_baseline(test_labels),
        "tfidf_logreg": tfidf_logreg_baseline(train_texts, train_labels, val_texts, val_labels, test_texts, test_labels),
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[baselines] {target_level}/{split_name}/seed{seed}: "
          f"majority_f1={result['majority']['f1']:.3f} "
          f"always_pos_f1={result['always_positive']['f1']:.3f} "
          f"tfidf_logreg_f1={result['tfidf_logreg']['test']['f1']:.3f}")
    return result


if __name__ == "__main__":
    for target_level in TARGETS_BY_LEVEL:
        for seed in config.SEEDS:
            run_one(target_level, "S1", seed)
            run_one(target_level, "S2", seed)
    for seed in config.SEEDS:
        run_one("medium", "S3", seed)
    print("All baselines done.")
