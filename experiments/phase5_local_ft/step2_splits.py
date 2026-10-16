"""Step 2: poem-level splits (S1 80/20, S2 70/15/15, S3 استعارة فعل-only vs
eval_pool_25), always by poem, stratified by poet where possible (splitting.py),
3 seeds each. Reports poems/verses/positives per split, per target. No training.
"""
import json
from pathlib import Path

from data_io import list_poem_files, load_poem, positive_verses_by_subtype
from splitting import carve_val_from_train, stratified_poet_split

SPLITS_DIR = Path("splits")
SEEDS = [0, 1, 2]
EXAMPLE_POEM_IDS = {"16251", "17234", "21337"}  # phase4_e1_v2.e1v2_config.EXAMPLE_POEM_IDS -- forced train-only in S3

with open("config/targets.json", encoding="utf-8") as f:
    TARGETS = json.load(f)["targets"]
TARGET_VALUES = [t["value"] for t in TARGETS]  # the 5 subtypes


def load_corpus():
    poems = {}
    poem_meta = []
    for f in list_poem_files():
        poem = load_poem(f)
        pid = str(poem["poem_id"])
        poems[pid] = poem
        poem_meta.append({"poem_id": pid, "poet_name": poem["poet_name"], "verse_count": poem["verse_count"]})
    return poems, poem_meta


def split_stats(poems: dict, poem_ids: list, target_values: list) -> dict:
    n_poems = len(poem_ids)
    n_verses = sum(poems[pid]["verse_count"] for pid in poem_ids)
    per_target = {}
    for target in target_values:
        pos_verses = 0
        poems_with = 0
        for pid in poem_ids:
            pv = positive_verses_by_subtype(poems[pid]).get(target, set())
            if pv:
                pos_verses += len(pv)
                poems_with += 1
        per_target[target] = {"pos_verses": pos_verses, "poems_with": poems_with,
                               "pos_rate": round(pos_verses / n_verses, 4) if n_verses else 0.0}
    return {"n_poems": n_poems, "n_verses": n_verses, "targets": per_target}


def report_split(name: str, seed: int, split: dict, poems: dict, target_values: list):
    print(f"\n--- {name} seed={seed} ---")
    for part, ids in split.items():
        stats = split_stats(poems, ids, target_values)
        print(f"  {part:<6} poems={stats['n_poems']:<4} verses={stats['n_verses']:<5}", end="")
        for t, s in stats["targets"].items():
            print(f" | {t}: pos={s['pos_verses']}({s['pos_rate']*100:.1f}%) poems_w={s['poems_with']}", end="")
        print()


def save_split(name: str, seed: int, split: dict):
    path = SPLITS_DIR / f"{name}_seed{seed}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(split, f, ensure_ascii=False, indent=2)


def build_s1(poems, poem_meta, seed):
    outer = stratified_poet_split(poem_meta, ["train", "test"], [0.8, 0.2], seed=seed)
    poems_by_id = {p["poem_id"]: p for p in poem_meta}
    inner = carve_val_from_train(outer["train"], poems_by_id, val_frac=0.10, seed=seed + 100)
    return {"train": inner["train"], "val": inner["val"], "test": outer["test"]}


def build_s2(poems, poem_meta, seed):
    return stratified_poet_split(poem_meta, ["train", "val", "test"], [0.70, 0.15, 0.15], seed=seed)


def build_s3(poems, poem_meta, test_ids, seed):
    test_set = set(test_ids)
    remaining = [p for p in poem_meta if p["poem_id"] not in test_set]
    forced_train = [p["poem_id"] for p in remaining if p["poem_id"] in EXAMPLE_POEM_IDS]
    to_split = [p for p in remaining if p["poem_id"] not in EXAMPLE_POEM_IDS]
    inner = stratified_poet_split(to_split, ["train", "val"], [0.90, 0.10], seed=seed)
    return {"train": inner["train"] + forced_train, "val": inner["val"], "test": list(test_ids)}


if __name__ == "__main__":
    SPLITS_DIR.mkdir(exist_ok=True)
    poems, poem_meta = load_corpus()
    print(f"Loaded {len(poem_meta)} poems, {sum(p['verse_count'] for p in poem_meta)} verses "
          f"(excl. 28601), {len(set(p['poet_name'] for p in poem_meta))} distinct poets.")

    print("\n================ S1 (80/20 train/test, 10% of train carved as val) ================")
    for seed in SEEDS:
        split = build_s1(poems, poem_meta, seed)
        save_split("S1", seed, split)
        report_split("S1", seed, split, poems, TARGET_VALUES)

    print("\n================ S2 (70/15/15 train/val/test) ================")
    for seed in SEEDS:
        split = build_s2(poems, poem_meta, seed)
        save_split("S2", seed, split)
        report_split("S2", seed, split, poems, TARGET_VALUES)

    print("\n================ S3 (استعارة فعل only -- TEST fixed to eval_pool_25) ================")
    with open("../phase4_e1_v2/config/eval_pool_25.json", encoding="utf-8") as f:
        pool25 = json.load(f)
    test_ids = pool25["poem_ids"]
    overlap = set(test_ids) & EXAMPLE_POEM_IDS
    assert not overlap, f"eval_pool_25 unexpectedly overlaps EXAMPLE_POEM_IDS: {overlap}"
    for seed in SEEDS:
        split = build_s3(poems, poem_meta, test_ids, seed)
        assert set(EXAMPLE_POEM_IDS) <= set(split["train"]), "example poems leaked out of train in S3"
        assert not (set(split["val"]) & EXAMPLE_POEM_IDS), "example poems leaked into S3 val"
        save_split("S3", seed, split)
        report_split("S3", seed, split, poems, ["استعارة فعل"])
    # sanity: S3 test verse-unit count must reproduce E1 v2's own 327
    n_test_verses = sum(poems[pid]["verse_count"] for pid in test_ids)
    print(f"\nS3 test verse-unit count: {n_test_verses} (expected 327, E1 v2's own eval_pool_25 count)")
    assert n_test_verses == pool25["pool_verses"]
